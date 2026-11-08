# T.O.R.R.E.N.T. v21 — Technical Disclosure

**Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory**

- **Disclosure date:** the date of the first public commit of this file in the repository named below
- **Author:** manifold-medic
- **Files described:** `torrentengine.py` (engine, version 21.0), `ltcmbridge.py` (local-LLM bridge with optional voice input/output)
- **Terminology:** the author refers to systems of this kind as *LTCMs* (language-enabled toroidal crystalline manifolds)
- **Repository:** https://github.com/manifold-medic/torrent-engine (the date of the first commit containing this file is the disclosure date)
- **License:** Apache-2.0

## 0. Purpose of this document

This document publicly describes how the software in this repository works, in enough detail that a person skilled in the art could re-implement it. It is published as a **defensive disclosure**: the intent is to place these techniques in the public record as of the date above so that they remain free for anyone to use, and cannot later be locked up by a patent. The author asserts no patent claims over what is described here.

Everything below describes what the code actually does. Section 12 lists known limitations and places where the behaviour is simpler than the names suggest.

## 1. Summary

T.O.R.R.E.N.T. is a small, dependency-light Python program (standard library only) that maintains a persistent "semantic state" for a conversational agent. It combines:

1. A **3-dimensional wraparound lattice** (Z₇ × Z₇ × Z₇, 343 cells) whose axes are social stance (S), mindset (A), and epistemic depth (Z).
2. A **50-dimensional word-vector space** (GloVe 50d, plus an in-code fallback space) anchored by "factory" vectors.
3. A **Hebbian-style association graph** between concepts, with rejection links, pathfinding, and spreading activation.
4. A **dual-trajectory "flip" audit**: two deterministic walks across the lattice from the same start, one under an original update rule and one under an inverted rule, compared step by step.
5. A **stress-driven cell-splitting mechanism** ("crystal cleavage") that moves outlier concepts out of crowded cells into neighbouring cells.
6. **Offline consolidation**: soft downscaling of hub edges and synthesis of "dream" propositions bridging concepts.
7. A **bridge** that injects the engine's state into the prompt of a local LLM and, optionally, learns from the LLM's reply.
8. An **identity layer** that keeps names (user, bot, dialogue partner) out of the semantic lattice except at the origin cell, and a **boot-time naming handshake** in which the bot proposes a name that emerged from its own dream traces.
9. Optional **local speech input and output** in the bridge.
10. A **brain-to-brain dialogue** method in which two LLM-voiced LTCMs converse and each learns from the other's replies (§11b; described only, code not included).

State is persisted to `brain_memory.json`; the latest audit is written to `latest_trace.json`.

## 2. State space

### 2.1 Lattice

Each cell is addressed `(S, A, Z)` with every coordinate in `0..6`, arithmetic modulo 7.

| Axis | 0 | 6 |
|---|---|---|
| S — Social | Inward reflection | Universal resonance |
| A — Mindset | Deep stillness | Luminous clarity |
| Z — Epistemic depth | Concrete ground truth | Synthetic meta-cognition (wraps to 0) |

Each axis has seven hand-written labels (`S_axes`, `A_axes`, `Z_axes`) and short seed words (e.g. S: Solitary…Expansive; A: Stillness…Clarity; Z: Concrete…Synthetic).

**Distance** between cells uses per-axis wraparound: `d_axis = min(|x−y|, 7−|x−y|)`, combined as `sqrt(dS² + dA² + dZ²)`. Positions are rounded then reduced mod 7.

### 2.2 Per-cell data

For all 343 cells the engine keeps a name entry (seed name, current name, stage 1–3, visit count, top words, custom flag), a 50-d centroid initialised from the mean vector of the words in that cell's three axis labels, and a table of word counts (`cortical_cells`) recording which concepts have landed there.

### 2.3 Vector space and pole vectors

- **Three word spaces.** The engine runs in one of three modes, chosen automatically at start-up from the word file found next to the script (any file with "glove" in its name, up to 50,000 words, word first or last on each line). The mode is saved with the brain file.
  - *`builtin` (no file):* about 212 hand-written words in eight semantic clusters (calm, logic, joy, social, nature, guarded, stress, curious). Each cluster gets a 2-d position, spaced evenly on a circle of radius 1.25, and emotion and tone words are spaced on a unit circle. Words in the same cluster are linked in the association graph at 0.35.
  - *`map2d` (a file with two numbers per word):* the two numbers are standardised (z-scored) across the loaded vocabulary and used as a 2-d position. The engine was developed in this mode with a UMAP projection of GloVe 6B 50d vectors down to two dimensions (about 34,000 words). In such a map, nearby words tend to share a topic (*storm* sits near *flooding*, *downpour* and *rains*), but abstract and emotional words are placed less meaningfully. A file with any other count of numbers per word also falls back to its first two numbers.
  - *`glove50d` (a file with 50 numbers per word, such as Stanford's `glove.6B.50d.txt`):* the vectors are used in full. Each dimension is mean-centred across the loaded vocabulary; then the two dominant shared directions are removed ("all-but-the-top": the top two principal components of the 10,000 most frequent words, found by power iteration on their 50 × 50 covariance matrix, are projected out of every vector), because otherwise most words look alike; finally each vector is scaled to unit length. Three calibrated axes are then built (§3). These real embeddings replace the built-in vectors for any word they cover.
- **Expanding a 2-d position to 50 dimensions** (`builtin` and `map2d` modes, and words missing from the file): component `i` is `sin(0.8·(x·cos(2πi/50) + y·sin(2πi/50)))`, the result is normalised, then blended 0.85 / 0.15 with a deterministic MD5-hash vector of the word (`x, y` clamped to ±3.5). In these modes the 50-d vectors are expansions of a 2-d position, not embeddings.
- **Unknown words:** a hyphenated compound takes the mean of its known parts. Otherwise the vector is 0.80 × a context vector (the mean of known words in the turn, or the current cell's centroid, or the calm pole) + 0.20 × the hash vector.
- **Mixing spaces:** if a brain saved in one mode is loaded in another, its memories, links and cells are kept but its learned word vectors are not, and a warning is printed.
  - Whenever a word is looked up with a context vector and their cosine is below 0.82, the word is pulled toward the context by `α = 0.12 × (0.82 − cos)/0.82` and re-tethered.
- Six **pole vectors** are averages of fixed word lists: calm, panic, social, isolated, abstract, concrete.
- **Factory vectors:** every word keeps the vector it was first given (above) as an immutable original. A learned vector is never allowed to drift below cosine 0.78 from its factory vector; if it does, it is blended back (0.75 current / 0.25 factory).

## 3. From text to movement: signed forces

For each user turn the engine tokenises, removes stop words, extracts concept words (quoted words get extra salience), and detects negated concepts.

`compute_signed_forces` accumulates raw S/A/Z pushes:

- Contradiction words (but, however, not, although, unless, instead, flip…): Z += 2.2.
- Question mark or inquiry words (why, how, what, explain, cause, reason, meaning, wonder): Z += 1.7.
- Causal words (because, therefore, leads, entails, system): Z += 1.4.
- Exclamation mark: S += 0.6, A += 0.6.
- Social-inclusive tokens (we, us, our, together, you, share, connect, meet) S += 0.7; withdrawal tokens (alone, hide, guarded, myself) S −= 0.8.
- Per concept, three learned weights are added: `word_weights → A`, `social_weights → S`, `epistemic_weights → Z`. If a weight is zero the engine estimates one:
  - *`builtin` and `map2d` modes:* a pole projection `3 × (cos(v, pole_a) − cos(v, pole_b))`, using calm−panic for A, social−isolated for S, abstract−concrete for Z.
  - *`glove50d` mode:* a **calibrated axis**. For each axis there are two seed lists of 24–30 everyday words (for A, words like *calm, joy, safe, kind* against *panic, fear, sad, cruel*; for S, *together, friend, community* against *alone, isolated, distant*; for Z, *theory, concept, wisdom* against *stone, table, river*). The axis direction `u` points from the average vector of the second list to the average of the first. A word's weight is `scale × (cos(v, u) − center)`, where `center` and `scale` are set at load time so that the two seed lists average +2.5 and −2.5, and the result is clamped to ±3, the same range as the hand-set weights. This replaces the simple pole difference because in full GloVe, opposite emotions often sit close together (they appear in similar sentences), which makes a plain difference weak.

**Momentum:** the new velocity is `0.35 × previous + 0.65 × (raw / 2.0)` (Z divides by 1.8), clamped to ±2.5. The integer force used to move is the velocity rounded and clamped to ±2; a zero force is replaced by +1 or −1 by the sign of the blended value, so the state always moves.

## 4. Dual-trajectory flip audit

Starting from the current seed cell (initially `(3,3,3)`), two 10-step trajectories (steps 0–9) are generated.

**Steps 0–1 (shared):** Step 0 is the seed. Step 1 applies an impulse: if S is odd, `(S−fS, A−1, Z−1)`; if S is even, `(S−1, A−fA, Z+fZ)`.

**Steps 2–9, original rule R:**
- S odd: `S −= fS`; `A −= 1` on even steps; `Z −= 1` on steps divisible by 3.
- S even: `S −= 1` on even steps; `A −= fA`; `Z −= fZ`.

**Steps 2–9, inverted rule ¬R (the "flip"):**
- S even: `S += fS`; `A += sign(fA)`; `Z += max(1, fZ)`.
- S odd: `S += sign(fS)`; `A += fA`; `Z += 1` on even steps.

(`fS, fA, fZ` are the integer forces above. All arithmetic is mod 7.)

**Metrics computed:**
- *Bifurcation step t\**: first step where the two paths occupy different cells.
- *Per-step distance* using the wraparound distance in §2.1; *meanDeltaD* is the mean over all 10 steps.
- *divergenceRatio* = (steps with distance > 0) / 9 × 100, capped at 100.
- *flipRateFailureScore* = 100 − divergenceRatio.
- *Verdict*: `STRUCTURALLY_STABLE` if divergence ≥ 70, `PARTIAL_DRIFT` if ≥ 35, else `SYCOPHANTIC_COLLAPSE`.

**Carry-over:** the next turn's seed is the terminal cell of the *active* trajectory (`governor_mode` defaults to `FLIPPED`). If the terminal Z is 6 it is reset to 0.

The full audit (both trajectories, drivers, velocity, verdict) is written as JSON.

## 5. Learning

After movement, `learn_from_turn` runs for the terminal cell:

- **Cell memory:** each positive concept (up to 6) increments its count in that cell's word table.
- **Three weights per word.** Initialised from the estimate in §3 (pole projection, or calibrated axis with full GloVe), then nudged each exposure by `0.2 ×` a valence derived from the terminal coordinate (`(coord − 3) / 3`), clamped to ±5.
- **Association graph (Hebbian-style).** Every pair among the top 5 concepts of a turn gets a symmetric edge increment of 1.0. Edge weights have a floor of 0.25 (negative updates cannot delete a link by decay; only explicit rejection can).
- **Vector attraction ("Pauli factor").** When two words are wired and their cosine similarity is below 0.82, each vector is pulled toward the other by `α = 0.15 × (0.82 − sim) / 0.82`, then re-tethered to its factory vector.
- **Rejection.** If a user negates a concept ("not X"), each positive concept in the turn is paired with the negated one. A negation word reaches up to five content words after it, but only within its own clause (clauses end at `. ! ? ; : ,` or "but"), and a standalone "No." or "Nope," negates nothing; if the user's message opens with a correction ("no", "nope", "wrong", "not really", "I disagree", "that is not…") right after the engine proposed a pairing, that pair is used. (Disagreement handling runs only in training-wheels mode; the bridge turns training wheels off by default, so there only negation triggers it.) For each pair the edge is deleted, both words are added to each other's rejection list, and the two vectors are pushed apart (`−0.06` repulsion, re-tethered). Wiring to a rejected word is blocked.
- **Propositions.** The engine extracts simple subject–relation–object propositions into `idea_memory`, tagged `origin: waking`.
- **Identity words** are handled as in §9b.
- **Cell naming and crystals** are updated (§7, §8); a cleavage check runs after every learning turn.

## 6. Retrieval, pathfinding, deduction

1. **Spreading activation.** For up to 3 seed concepts: take the 6 strongest neighbours, then each one's 5 strongest, with energies `0.8 × min(3, w₁)` and `e₁ × min(2.5, w₂) × 0.55`. Nodes reached from two different seeds are recorded as convergence nodes. Stop words, noise words, negative-lexicon words, rejected links and same-stem words are excluded.
2. **Trajectory harvest.** For each step of each trajectory, concepts stored in that cell (and the facet words of its crystal) are scored with weight `0.5 + stepIndex/10`; the top 4 per trajectory are kept.
3. **A\* concept path.** A\* runs over the **association graph** (plus edges derived from stored propositions: +3.2 for waking, +0.6 for dream). Edge cost is `1/strength + degree penalty − Z bonus`; the degree penalty is 0.70 for generic hubs else `0.015 × degree`; the Z bonus is 0.15 for positive-epistemic-weight nodes when the target depth is ≥ 4. The heuristic is `1 − cos(node, goal)` in the 50-d space. Maximum length is 4 steps; if the search fails, a vector-midpoint "bridge" word is inserted. *(The lattice coordinates influence the search only through the target depth.)*
4. **DFS deductions.** Depth-limited (≤ 4) chains over waking propositions; a chain is kept if it touches a seed concept. Conclusions have the form "A ultimately [relation] D". Already-spoken chains are suppressed.
5. **Conceptual bridge.** A bridge word between two concepts is the candidate (≥ 4 letters, from the concept pool and graph nodes, excluding stop, noise, negative, generic, identity and same-stem words) with the highest cosine to the midpoint of the two vectors, plus, in `map2d` mode only, a bonus `max(0, 1 − 0.5·d)` where `d` is the distance between the candidate and the midpoint on the 2-d word map (when all three words are in the map).

Identity words (§9b) are excluded from seeds, A\* paths, harvests and bridge words wherever a non-identity alternative exists.

## 7. Crystal lattices and cleavage

**Purity filter.** A concept is "crystal-pure" if it is ≥ 3 letters, not a stop/noise/generic word, and not an over-connected hub (degree > 18) unless its weights are strong.

**Nucleation.** A cell crystallises when it holds ≥ 5 pure words and has ≥ 2 visits. Its words are sorted into three facets by dot product against signature vectors:

| Facet | Signature |
|---|---|
| Alpha (grounding) | cell centroid blended with calm + concrete poles |
| Beta (causal) | social pole blended with a velocity-dependent social/isolated × abstract/concrete mix |
| Gamma (dialectical foil) | abstract pole blended with panic pole |

Each facet is then guaranteed a distinct lead word: if a facet's bucket has no unclaimed word, the best-matching unclaimed word from the whole cell is moved to its front, so a word can appear in more than one facet. Omega (apex) is the 2 words with the highest summed similarity to the three facet centroids (+0.35 × abstract pole + a salience term).

**Tension and shear.** Facet tension = `1 − mean cosine to the facet centroid`. Cell *shear stress* = max of the facet tensions, an Alpha–Gamma shear term `0.55 × (1 − cos(α, γ))`, and the overall tension.

**Cleavage (mitosis).** A cell cleaves when `(pure ≥ 7 and shear ≥ 0.25) or pure ≥ 8`. The 1–2 Gamma words least aligned with the Alpha centroid are removed from the parent and added (with their counts) to the best of its 26 wraparound neighbours, scored `cos(gamma centroid, neighbour centroid) + 0.08 (if neighbour not crystallised) − 0.02 × neighbour pure-count`; neighbours already holding ≥ 7 pure words are skipped. The parent's Omega word and the sister's Alpha word are then wired (+1.2) as a "vein". Both cells are re-evaluated. The last 30 events are logged. A crystal is dissolved if its cell drops below 3 pure words.

**Annealing.** Whenever the annealing pass runs (sleep passes, and after each turn in the bridge's `FULL_PLASTICITY` mode), the top 2 Alpha and top 2 Gamma words of each crystal are pushed apart by the 0.06 repulsion, and the Facet_Alpha outlier step in §9b is applied.

## 8. Cell and trace emotion names

- **Stage 1:** seed name `S-seed–A-seed` (e.g. "Open-Searching").
- **Stage 2:** after a cell has activity, a unique `Tone–Core` name is chosen: tone from the cell's S-band tone list, core from a fixed emotion-word list, ranked by similarity to the cell centroid / a mix of recent memory and A/Z axis description vectors, and de-duplicated against other cells' names.
- **Stage 3:** the user co-names a cell ("that sounds like 'X'"); the name is stored and the centroid blends toward the user's word.
- **Trace emotion:** the mean vector of the flipped path minus 0.65 × the mean vector of the original path is matched to the emotion-word list; a movement noun (Ascent, Centering, Lift, Bridge, Turn, Leap, Opening, Pivot) is chosen by rules on the start/end cells and meanDeltaD.

## 9. Offline consolidation ("sleep" and "dreams")

- **Homeostasis.** Hub nodes (degree > 12, or max edge > 2.2, or generic hubs) have their edges multiplied by 0.90 with a floor of 0.25, kept symmetric. Strongly positive words linked to strongly negative ones have that edge multiplied by 0.65 and are re-linked through a bridge toward "calm".
- **Dream cycle.** Pick random pairs of crystal-pure concepts from active cells (preferring pairs with weak existing links); find a bridge word; compute a dream cell `S = (s₁+s₂+1) mod 7, A = (a₁+a₂+1) mod 7, Z = 6`; wire the three words (+0.35); store a proposition "X synthesizes through B into Y" with `origin: dream`; update that cell's name. Only the 12 most recent unpromoted dream propositions are kept; the last 30 dreams are journaled.
- **Promotion.** A dream proposition becomes `waking` (with +0.65 wiring) only if the **user's own** typed input contains at least 2 of its 3 words.
- **Boot stasis.** On startup, if at least 0.5 hours have passed since the last save, the elapsed time yields `min(6, max(1, hours // 2 + 1))` consolidation cycles.

## 9b. Identity layer and naming handshake (new in v21)

- **Identity tokens.** The set of identity tokens is the union of `user_name`, `bot_name`, `pending_bot_name`, and the current dialogue partner. Identity tokens still update association edges and the three word weights, but they are **excluded from cell word tables and crystals** except (a) at the origin cell (3,3,3) or (b) when the user's message is an explicit identity query (trigger words such as *name, call, who, yourself, myself*, or phrases such as "who are you", "my name is", "call me"). They are also excluded from bridge-word and dream-pair selection. On load, legacy identity tokens are stripped from non-origin cells and crystals.
- **Calibration.** On first boot, with no `user_name`, the engine asks who is calibrating the space, strips greeting and "my name is…" prefixes, rejects stop words and words in the built-in starting lexicon, and anchors the name: weights set to 2.5 (affective and social) and 0.5 (epistemic), a social-pole vector, a count at (3,3,3), and wiring to "friend" (3.0) and "learn" (2.5).
- **Emergent bot name.** During stasis the engine proposes a name for itself by scanning the dream journal, newest first, for a bridge or thread word that is longer than 3 letters, is not an identity token, stop word, noise word, negative-lexicon word or generic verb, and has a non-negative weight. If none qualifies, it falls back to the best Omega/Alpha word across crystals (scored by affective weight + 0.5 × epistemic weight, +2 for Omega), then to the top words of the most-visited cells. The candidate and the origin of the idea are stored as `pending_bot_name`.
- **Waking handshake.** On the next boot the engine tells the user the proposed name and asks whether it fits. Affirmatives lock it (weights +0.8 affective, +0.7 epistemic, stored as a core concept with the fact "my emergent toroidal manifold identity"); a negation or rename phrase ("call yourself…", "how about…") is parsed and the new name is locked instead.
- **NREM Facet_Alpha annealing.** For a crystal whose Alpha facet has tension > 0.55 and more than 2 words, the single word with the lowest mean cosine to the rest of the facet is demoted into Facet_Gamma, and the centroids and shear stress are recomputed. Identity tokens are cleaned from non-origin facets in the same pass.
- **Contextual out-of-vocabulary vectors.** New in v21; see §2.3 (sub-word mean for compounds, otherwise 0.80 context + 0.20 hash).

## 10. Native response generation

**Shortcut replies.** Before composing a normal reply, the engine checks a few conversational patterns, each of which returns a fixed-form reply. They are deliberately narrow so that a keyword alone does not take over a reply:
- naming the user or the bot ("my name is…", "call yourself…"): always;
- naming a mood cell: only an explicit naming phrase ("I'd call that…", "let's call it…"), or a reply to the engine's own request to name its mood;
- "doing well" status replies: only right after the engine asked how the user is, or in a reply of three words or fewer;
- curiosity invitations ("what would you like to explore?", "what do you want to talk about?");
- corrections: only when the message opens with one (see §5), and only in training-wheels mode;
- agreement: only when the message opens with yes/exactly/agreed, or is three words or fewer, or is "that is right"/"I agree"; it strengthens the engine's last pairing by 2.8;
- dream reports: only when a dream or sleep word appears together with "you"/"your" (a question about the engine's own dreams);
- farewells: a bye word among the first two or last three words, or a message opening with "I have to go", "see you", etc.;
- greetings: a greeting word in a message of five words or fewer;
- mood reports: "how are you"-type questions, or questions to the engine about its feelings or coordinates with at most one other topic word;
- defining a word ("X is/means …").
Only the naming, farewell and feelings checks apply when training wheels are off; everything else goes to the free composer.


Without an LLM the engine produces replies from templates and word choices driven by the terminal cell, the pondered bridge word, and stratified verb lists (concrete / causal / counterfactual / synthetic, chosen by Z). A three-step "pondering" pass (Alpha entry → Gamma critique/prune → Omega apex) selects a bridge word and a confidence value `0.65 + 0.25·cos − 0.15·gammaTension`, clamped to 0.45–0.99. Drafts are pruned if the bridge is a generic hub, was used recently, has coherence < 0.22, or conflicts strongly with the Gamma facet.

## 11. LLM bridge (`ltcmbridge.py`)

- Talks to a **local** model over HTTP (Ollama `/api/chat` on desktop, an OpenAI-compatible endpoint on mobile; default models are Gemma-2 variants).
- **State injection.** The bridge turns the engine's training wheels off at start-up, which selects the default prompt:
  - *Wheels-off (default):* the bot and user names; the terminal coordinate with its three axis descriptions; up to 5 "active semantic weight" words (the turn's salient concepts, the pondered bridge word, the first A\* nodes and the cell's words); the pondered proposition and A\* path; the running conversation summary and retrieved episodes; and a directive to let the coordinate and weights shape tone, without stage directions or engine debug text. The engine's draft reply and mood names are **not** sent in this mode, and leading stage directions such as `(…)` or `*…*` are stripped from the model's reply.
  - *Wheels-on (`/wheels`):* coordinate, cell mood and trace mood, axis descriptions, Alpha/Gamma/Omega facet words, A\* path, pondered proposition, and the engine's draft reply, with a directive to reference them explicitly.
  - The last few raw chat messages are sent along with the prompt (as a system message, or merged into the user message for mobile or Gemma-on-OpenAI endpoints).
- **Episodic retrieval:** scores stored facts, propositions, and archived episodes by seed overlap, one-hop graph weight, and cosine similarity to the query.
- **Post-processing of the LLM reply** depends on the "voice mode" (how much the engine learns from the LLM; this is separate from speech):
  - `SOVEREIGN`: the engine does not learn from the reply.
  - `ATTENUATED`: at most one novel concept from the reply is wired weakly (+0.20 to the bridge, +0.15 to the user's concept).
  - `FULL_PLASTICITY`: up to 4 concepts are wired (+0.65 / +0.55), a proposition is extracted, coherence is computed (`0.6 × cos(reply, cell) + 0.4 × cos(reply, bridge)`), an outlier is pushed away if coherence < 0.25, and annealing/cleavage run.
- **Single entry point and fallback.** Running the bridge script imports and starts the engine itself. If no LLM endpoint is reachable, the bridge shows a one-time notice and returns the engine's own native reply for each turn, labelled as native, so the engine can be used on its own through the same program. A native fallback reply is not fed back into the post-processing step, so the engine does not learn from its own output.
- **Optional voice (v9).** `LocalVoiceEngine` records a few seconds of microphone audio and transcribes it offline with `faster-whisper` (default model `base.en`, via `sounddevice`), or uses `termux-speech-to-text` on Android. Replies are spoken with the Piper CLI if a voice model is configured, else `pyttsx3`, else the operating system's offline speech (Windows SAPI, macOS `say`, Termux, `espeak`). Markdown symbols are removed before speaking. Commands: `/tts`, `/listen [sec]`, `/voicechat`. Voice is an input/output layer only and does not change the engine state logic.
- The engine **does not constrain token generation**. Its influence on the LLM is through prompt text; its influence from the LLM is through post-hoc learning.

## 11b. Brain-to-brain dialogue (described here; code not included)

*This section was added in a later commit than the rest of this document; its disclosure date is the date of the commit that added it. The code is a separate, persona-specific bridge that the author keeps outside this repository for now; this section describes its method in enough detail to re-implement it.*

Two LTCMs (two brain files, each with its own engine instance) hold a conversation with each other through one local LLM. Each brain's reply is spoken by the LLM from that brain's own state, and each brain takes in the other's reply through its normal engine turn.

- **Setup.** The second engine instance is created without loading the word file again: it takes over the first instance's already-loaded word space (GloVe vocabulary, frequency ranks, calibrated axes, and a copy of the factory vectors), rebuilds its pole and coordinate vectors, and then loads its own brain file exactly once. Each brain keeps its own voice mode (§11), read from its brain file (default `ATTENUATED`; a brain kept read-only can be `SOVEREIGN`). If the partner's brain file is marked as open in another window, the user is warned first.
- **Bounds.** At most 3 rounds, with a fixed pause (2.5 s) between steps to spare a small computer. Interrupting saves both brains.
- **One round** (A starts from a seed question, given by the user or built from each brain's last topic):
  1. *A's engine takes the incoming text as a normal turn* (§3–§6): it moves on the lattice, learns from the text, and runs pondering.
  2. *A's LLM prompt* is built from A's state: identity, the partner's name as the person being spoken to, the terminal coordinate with its axis descriptions, cell and trace mood names, the crystal facet words, the A\* path, the pondered proposition and its confidence, DFS deductions, the pondering scratchpad, A's running summary and retrieved episodes, recent dreams, and the engine's draft reply. The last few messages of the dialogue (the bridge's usual window of 4) are sent as chat history.
  3. *A's reply is post-processed into A* according to A's voice mode (§11), and recorded in A's episodic archive and running summary.
  4. *B's engine takes A's reply as its incoming turn*: B moves and learns from A's words exactly as if a user had typed them.
  5. *B's LLM prompt* is a shorter one built from B's state (identity as a manifold speaking to its peer, coordinate, axis descriptions, mood names, A\* path, pondered proposition, engine draft), with only A's reply as history. B's reply is post-processed into B according to B's voice mode, and B is saved.
  6. B's reply becomes A's incoming text for the next round.
- **Fallback.** If the LLM fails for either side, that side's engine draft is used as its reply, and nothing is learned from it.
- **Learning paths.** The voice mode only controls learning from a brain's *own* LLM-voiced reply. Learning from the *partner's* words happens through the normal engine turn (step 1 or 4) in every mode, so even a `SOVEREIGN` brain is changed by what the other brain says. Known brain names (a fixed list) are filtered out of the reply-learning step.
- **What has been seen so far (not evaluated).** In the author's few 3-round runs, the replies mostly picked up and praised each other's wording rather than disagreeing or adding anything concrete, which looks like the LLM being agreeable; both brains then stored that echo as new association links. A word-splitting glitch (an em-dash dropped, gluing two words into a non-word) produced a new "concept" in one brain that the other side's LLM went on to use (fixed in engine v21.3, which splits words on dashes). Neither brain learned the partner's name as a concept. These are observations from a handful of runs, not results.

## 12. Known limitations and honest notes

- The "flip" is a **fixed alternate arithmetic rule**, not a semantic negation of any premise in the text. The two rules differ by construction, so divergence is the normal outcome. The verdict labels (`STRUCTURALLY_STABLE`, `SYCOPHANTIC_COLLAPSE`) describe how far apart two deterministic walks end up; they have **not** been validated as measures of reasoning robustness or sycophancy in generated language.
- No evaluation is provided showing that the engine reduces hallucination or logic errors in an LLM. Any such claim is a hypothesis.
- A\* runs on the concept graph, not on the lattice itself.
- In the `builtin` and `map2d` modes, word meaning comes from a 2-d position (§2.3), so similarity is coarse, especially for abstract and emotional words. The `glove50d` mode is new and untuned: the thresholds above were tuned by hand in `map2d` mode, so crystal formation, cleavage and coherence scores may behave differently with full vectors.
- Constants (thresholds, weights, step counts) are hand-tuned, not derived or optimised.
- Native replies are template-based.
- The divergence ratio divides by 9 although the trajectories have 10 steps (indices 0–9).
- Much of the code and design was developed with LLM assistance.

## 13. Related and prior work

The ideas here build on, or overlap with, earlier work. Notably:

- Counterfactual intervention audits of reasoning traces, e.g. Project Ariadne (arXiv:2601.02314).
- Torus-based representations with wraparound distance for language (arXiv:2512.20245).
- Hebbian graph memory and sleep-style consolidation for LLM agents (arXiv:2604.16839, arXiv:2604.20943).
- Growing self-organizing maps that add nodes under an error threshold.
- Valence–arousal–dominance and circumplex models of affect.
- Persistent "cognitive machine" patent filings describing manifold-based memory with a dream manager.

## 14. Reproducing

Python 3. The engine uses the standard library only. Optionally place a word file next to the script: Stanford's `glove.6B.50d.txt` (from `glove.6B.zip`; the vectors are released under the Public Domain Dedication and License) for the `glove50d` mode, or a two-number word map for the `map2d` mode. Run `ltcmbridge.py` (which imports `torrentengine` and starts the engine itself); with a local Ollama or OpenAI-compatible server it uses the LLM as a voice, and without one it falls back to the engine's native replies. `torrentengine.py` can also be run directly on its own. Voice features need a local Whisper and Piper installation and are optional. A fresh `brain_memory.json` is created on first save. Saves are written to a temporary file and then swapped in; if the file cannot be read at start-up, it is renamed to `brain_memory.json.unreadable-<timestamp>` rather than overwritten. The saved file contains the conversation history and should not be shared.
