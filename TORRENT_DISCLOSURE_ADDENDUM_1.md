# T.O.R.R.E.N.T. — Technical Disclosure, Addendum 1 (v21.1 to v24.1.1)

- **Disclosure date:** the date of the first public commit of this file in the repository named below
- **Author:** manifold-medic
- **Files described:** `torrentengine.py` (engine, version 24.1.1) and `ltcmbridge.py` (bridge, version 24.1.1)
- **Repository:** https://github.com/manifold-medic/torrent-engine
- **License:** Apache-2.0
- **Relationship to the main disclosure:** `TORRENT_DISCLOSURE.md` describes engine v21.0. This addendum describes what
  was added or changed from v21.1 to v24.1.1, in enough detail to re-implement it. Where this addendum and the main
  disclosure differ, this addendum describes the current code. The dated changelog at the top of `torrentengine.py`
  and in `CHANGELOG.md` gives the version-by-version history.

## A0. Purpose

Like the main disclosure, this is published as a **defensive disclosure**: to place these techniques in the public
record as of the date above, so they remain free for anyone to use and cannot later be patented. The author asserts no
patent claims over what is described here. Everything below describes what the code does; numbers given are the
current defaults, which are first guesses unless a test is mentioned. Names such as "levels", "arousal", "valence",
"cerebellum", "amygdala" or "brainstem" are vocabulary for parts of this engine only; no medical, pharmacological or
neuroscientific claim is made.

## A1. Movement on the lattice

- **Wraparound damping (v21.3).** Each of the 10 trajectory steps moves the state 3/16 of a cell
  (`TRAJECTORY_DAMPING`), so a turn travels about 1-3 cells in the direction of its push instead of lapping the 7-cell
  ring. The flip audit, rules and torus are unchanged.
- **Divergence ratio (v21.2)** divides by 8 (steps 0 and 1 are always shared).

## A2. Keeping the lattice from saturating (v21.6 to v22.2)

- **Cell pruning and spread cap (v21.7).** Once per sleep, each word's count in each cell shrinks; a placement under
  0.5 leaves the cell. One word may occupy at most 10 cells (`MAX_CELLS_PER_WORD`), keeping its strongest placements.
  The origin cell's name is protected. Counts are stored as decimals.
- **Relative hub cut (v21.8).** A word counts as crystal material only if its link count is outside the top 10% of
  link counts (was a fixed 18 links).
- **Day-scaled fading (v21.9).** Cell counts fade by `1 - PRUNE_PER_PLACEMENT x placements added since the last sleep`,
  and every link by `1 - LINK_FADE_PER_STRENGTH x link strength added since the last sleep`, so a quiet day fades
  little and a brain nobody talks to fades nothing. Links under 0.15 are deleted unless used since the last sleep; a
  word with no links leaves the graph (its vectors and weights stay). Built-in starter links fade like any other.
- **Sleep pressure and sleep depth (v22.0).** Waking learning (link strength added while talking) builds a saved
  `sleep_pressure`; links made by sleep itself (cleave veins, dream links, self-correction) don't count. Pressure is
  drained at wake-up, where the time away is known: depth = hours away / 8, capped at 1 (a 2-hour nap drains a quarter
  and does a quarter of the scaling). One sleep releases at most max(2% of all links, links created since the last
  sleep), weakest first, times depth. The strongest 20% of links are spared from the nightly scaling.
- **Sleep record (v22.1-v22.2).** Each wake-up sleep writes `last_sleep`: when it woke, hours slept (capped at 8) and
  hours away, nap (< 4 h) / short night (4-8 h) / full night (8 h+), up to 6 of that sleep's dreams, links released.
  `sleep_pressure_report()` gives rested / building / high / very high, measured in busy days of waking learning (one
  busy day = 250 units of link strength, about 40 sentences).
- **Comfort bridge habituation (v21.6).** Sleep's self-correction bridge (the word that relinks a positive-negative
  pair toward calm) is chosen with a penalty for bridges used in recent sleeps, and only from words the brain has been
  told (`experienced_words`). Before, the same nearest-to-calm word won about 44% of the time and became a hub.

## A3. Words, names and teaching

- **Names vs words (v21.3).** A name that is also an ordinary word counts as a name only when used as one (address,
  capitalised mid-sentence, "your name is X"); otherwise it is the word. Grammar words are refused as names.
- **Filler tier (v21.3).** Words such as together, talk, people, hello, goodbye, morning, night move the state and land
  in cells but stay out of crystals, dreams and bridges. Dashes, slashes and ellipses split words; possessive 's is dropped.
- **Teaching only from clear forms (v21.4, v22.4).** A sentence is stored as a definition only for "X means Y",
  "X represents / stands for Y", "X is a kind / type / sort of Y", "X is short for Y", "X is another / a / the word for
  Y", or a quoted form. Ordinary "X is Y" sentences are learned as links only. `/facts forget <word>` removes one.
- **Seen-once rule (v22.4, v22.11).** A word typed in only one message gets faint links (0.25) and no cell, crystal,
  dream or idea; a second message establishes it. Words a brain already held count as established (one-time migration).
- **Weighted, fading rejections (v23.1).** A negated pairing adds a soft rejection (0.3) that weakens the existing link
  by 30% instead of deleting it; a correction of the brain's guess removes the link with strength 1.0. Rejections fade
  x0.8 per full night (x depth) and are released under 0.05; new learning on a rejected pair is scaled by (1 - strength).
- **Negation scope (v23.3.3).** "not" reaches only the next real word (skipping articles and intensifiers) plus words
  joined by or/nor; it stops at clause words (when, because, if, while, although, since, who, which, unless, until), at
  punctuation and at "but". A "don't go together" rejection (0.3, once) is recorded only for "X is not Y" sentences. A
  negated word pushes the calm axis the opposite way at half weight and is not linked or placed.
- **Relation-aware verbs (v23.3.3).** When the engine words a link between two words, opposed pairs (rejection >= 0.3)
  draw from an opposing-verb list, strongly linked pairs (>= 0.8) exclude it; within the family, the landing cell picks.

## A4. Lean-up and nightmare mode (v22.3, v22.7.1)

The engine leans up by design: frightening words are kept out of names, dream bridges, recall and spreading activation,
and sleep softens strongly positive-to-negative links toward a calm bridge. **Nightmare mode** (per brain, off by
default) turns these rules off, so negative material is learned and dreamed like anything else. Outside nightmare mode,
a word with a positive built-in calm score that learned a negative score is reset to the built-in score at load.

## A5. Expectation, surprise and calm learning

- **Expectation and surprise (v22.5; code name "cerebellum").** After each turn the engine stores what it expects next:
  words (this turn's concepts, their 5 strongest links, the pondered path) and a calm level. Next turn, surprise (0..1) =
  0.6 x share of the first 6 non-stop-words not expected + 0.4 x change of calm level, judged against the brain's own
  running average surprise (adapting at 0.05). Surprise sets a learning gain in 0.5..1.5 for that turn's wiring, cell
  placements and weight nudges (since v23.0 the gain comes from arousal, A7).
- **Efference check (v22.5).** The engine predicts which content words its LLM voice will use; the bridge reports the
  share predicted ("self-match"). Measurement only.
- **"What follows" learning (v22.11; code name "amygdala").** The words of the user's previous message move 2% (x the
  surprise gain) of the way toward the calm level of the next message. Skipped across gaps over 30 minutes; names and
  words repeated in both messages are left alone.
- **Calm numbers learn from company (v22.6.1, v22.10).** A word's calm number moves 2% toward the average calm number of
  the other words in its turn, instead of being nudged by where the turn landed. At each wake-up sleep, every calm number
  relaxes 3% (x depth) toward its home: its built-in value, else its reading from the word vectors; made-up words and
  names have no home.
- **Mood level (v22.6).** Before each turn the calm position relaxes halfway to the middle, and the turn's push is
  measured against the brain's own running "usual lean". A word moved by a crystal split can't be moved again for 80
  turns (split rest).

## A6. Source tags (v22.7)

Every link stores who made it, as shares of its strength: user (per person since v23.2), note, voice, sleep, dream,
engine, built-in, book, idle, legacy. Shares shrink together when the link fades. Trusted = user, note, book, legacy. A
word reachable only through untrusted links cannot be chosen as a bridge word or a step of the thought path, and the
bridge counts only trusted strength when judging whether a reply is grounded.

## A7. Levels (v23.0, v23.3)

Four numbers updated by each turn and by clock time, saved per brain:

- **Valence** (-1..+1): a turn moves it by 0.5 x how far the turn really travelled on the calm axis (3 cells = 1.0),
  with soft edges (tanh) instead of wrapping. It clears 30% of its distance from the middle per turn and halves every 30
  minutes of clock time. Shown relative to a slow running "usual" (about the last 70 turns since v23.4.1).
- **Arousal** (0..1): moves toward a target = surprise above this brain's usual level + how tense the turn's words are;
  rises fast (half the gap per turn), falls slowly (keeps 79% per turn; halves every 20 minutes). Learning gain =
  1 + (arousal - its usual level), within 0.5..1.5. The bridge lowers temperature by 0.15 x arousal and shortens replies.
- **Novelty** (0..1, rests at 0.5): a fully predicted turn (surprise < 0.15) aims it at 0; surprise that isn't tense, or
  real words the brain never linked, raise it; it drifts back to 0.5 with a 60-minute half-life.
- **Sleep pressure:** the waking-learning part (A2) plus a clock part (12 hours awake = one busy day of learning).
- **One clock.** `levels_advance(minutes)` lets time pass for every level; since v23.4.3 every read of the time goes
  through one front door, `now()`, which a test or a live clock can replace.
- The last 20 turns (words, speaker, valence, arousal, surprise) are kept as `recent_turns`.

## A8. Idle time and the option menu (v22.8, v22.9, v23.4)

When idle time is on, a silence (3 minutes or more since the end of the last turn) is spent on the brain's own
material. Since v23.4 it is a series of decisions, each consuming clock time and ticking the levels:

| Option | Time | What it does |
| --- | --- | --- |
| wander | 3 min | One step along the current word's links (habituated: weight x 0.45 per earlier idle visit). A step back onto a word already in the walk leaps instead. |
| leap | 3 min | Jump to a known word whose vector resembles the current one; a faint new link (0.05). |
| replay | 3 min | Return to a word of a recent turn and rehearse that moment's links faintly (0.08). |
| doze | 15 min | Nothing learned; arousal clears twice as fast. |
| sleep | rest of the silence | A real sleep pass for the hours remaining (needs 30+ minutes left). |
| rest | up to 15 min | Chosen when no urge crosses the line: ordinary clearance, nothing learned. |

- **Urges** = a base + terms from arousal, valence, boredom (average of 1 - novelty and the walk's own habituation),
  sleep pressure, the last talk's surprise, and "missing the person" q = 1 - e^(-hours since they spoke), + a learned
  habit. Examples: wander 0.5 + 0.3(1 - b) - 0.3p; sleep -0.4 + 1.2p - 0.5a.
- **The race.** Each option's tally grows by urge x 0.1 + noise (sd 0.3 x sqrt(0.1)) per tick from the brain's own random
  generator; the first over the line 1.0 - 0.4 x arousal wins; none within 60 ticks = rest.
- **Habits.** After each choice, outcome = 0.7 x discovery (freshness of the word reached) + 0.3 x relief; the option's
  bias moves 5% toward (outcome - the usual outcome), clipped to +-0.2, shrinking 10% per full night.
- **Fixed rules underneath ("brainstem").** Very high sleep pressure forces sleep (or doze); below valence -0.6 (outside
  nightmare mode) only calm or neutral moments are replayed and the walk escapes after 2 tense steps via the comfort
  bridge; replaying one moment twice, or 3 replays in a row, ends replay for that silence; idle cannot push arousal above
  0.8; at most 12 thought steps and 40 decisions per silence (all-at-once path).
- **Learning while idle is faint.** Idle links skip the 0.25 minimum, move word vectors about 1/20 as much as a user
  link, are tagged idle (untrusted) and don't count as "used today", so sleep can release them. The walk's mood dose =
  mean calm of the walked words / 2 (clipped), added to valence.
- Every choice is logged with its urges' top reasons; the record includes the path, leaps, replays, new links, counts,
  dozed and rested minutes, hours slept and the walk's mood (calm / settled / drifted / ruminated).

## A9. Real time: live idle and speaking up (v23.4.3 to v23.5.3)

- **Live idle (v23.5).** The option menu is split into begin a silence / make one choice / finish the silence, with the
  silence's state kept between calls. A background clock in the bridge calls `live_tick()` every 20 s; a choice is made
  when its time comes (a choice at time t once t + 3 minutes of silence have passed). A lock ensures a tick and a message
  never touch the brain at the same time (a tick during a turn is skipped). The next message, exit, a nap, a dream or
  reading closes the silence and makes the usual record. With the same rules, live and all-at-once give identical
  choices (tested with a controlled clock).
- **Live-only differences.** Sleep doesn't require 30 minutes left: the brain sleeps until woken and the sleep pass runs
  at wake-up for the hours actually slept; woken within 30 minutes, the time counts as a doze. A doze is never cut short.
  After a doze, the thought-step count and the replay limit start again, and the decision cap is a 600-choice safety rail.
- **Speaking up (v23.5.3).** A sixth live option whose urge is

  u = -0.3 + 0.6 s + 0.5 q (1 + 0.5 w) + 0.2 b - 0.6 p - 0.5 n + h

  where s is the strongest new thing to say (a word the person used that the brain has seen only once: 0.8; a new link
  made by a leap: 0.6; a replayed moment: 0.6 x its surprise; a walk that started tense and ended calm: 0.4; each usable
  once), q is missing the person, w the brain's average valence after that person's messages (-1..1), b boredom, p sleep
  pressure, n the number of its messages in a row not yet answered (max 3), h the speak habit. Limits: 20 minutes of
  silence first, 45 minutes between speak-ups, never while asleep or dozing. Answered within 30 minutes: habit outcome
  good; unanswered 2 hours: bad (same habit rule as A8).
- **Packets.** When speak wins, the engine hands the bridge a packet (kind, words, person, minutes away, levels, the last
  words of the walk). The bridge asks the LLM, outside the brain's lock and on its own thread, for one or two sentences
  about that packet only, with an instruction not to claim other thoughts, events or feelings; the line is checked
  (A11), shown in the terminal and on the face page, optionally spoken or sent as a phone notification, and stored in the
  chat history after a placeholder user turn so roles alternate.

## A9b. A sense of time (v23.5.1, v24.0, v24.0.1)

- **Clock facts (v23.5.1, bridge).** Only when the message asks about the time, the voice is told the local date and
  time, the time since the previous message, the last break of 15+ minutes and the last sleep; recalled moments carry a
  time label (A11).
- **Daily rhythm (v24.0, experimental, off by default, saved per brain).** With h the hour of this computer's local
  clock minus a per-brain offset (in half hours, within 12), r(h) = cos(2π(h - 3)/24): +1 at 3 am, 0 at 9 am and 9 pm,
  -1 at 3 pm. Added to the idle urges (A8) and the speak urge (A9): sleep +0.5 r, wander -0.2 r, leap -0.2 r,
  speak -0.3 r, doze +0.3 r only when r > 0. It acts only on idle choices (live or all at once), not on how a message
  is learned. The engine's sleep pressure plays the other process of the two-process model (A12). Design notes from
  testing: a first draft used c = 0.5 + 0.5 cos(...), which is never negative and so only ever added sleepiness; and
  lowering doze by day left live idle's thought count un-refreshed (only a doze refreshes it), so rested brains spent
  most of the day resting awake.
- **Felt time (v24.0, measured and told only).** Each closed silence of the option menu records two numbers next to
  the clock time. Looking back = awake minutes x clip(0.5 + 0.5 x R / max(1, U), 0.5, 2) + asleep minutes x 0.5,
  where R is the silence's events per awake hour (distinct words reached + new links + thoughts back + speak-ups) and U
  is the brain's usual R (awake time only; moves 10% toward each silence's R). The first silence sets U to its own R
  and looks back equal to the clock. While passing (live silences only) = the sum over its choices of minutes x
  clip(1 + 0.6 b - 0.5 e, 0.5, 2), where b is boredom at the choice and e engagement (a step: 1 if it made a new link,
  else how fresh the word reached was; thinking back or speaking up 0.5; rest or doze 0), and asleep minutes x 0.5; a
  doze or rest is counted when it starts, and the part not yet lived is taken back if the silence closes during it.
  Both numbers can disagree. With the rhythm on, when asked about the time or a recent time alone (within 6
  messages), the voice gets them if either differs from the clock by more than a quarter, and at night (c > 0.75)
  "by your own daily rhythm it's night now" joins the plain-words levels in the facts block.

## A9c. Review fixes that change learning (v24.1, v24.1.1)

- **Learned meanings persist across restarts.** A saved learned vector is loaded as saved, subject only to the waking
  tether (a vector whose cosine to its original falls below 0.78 is blended 0.75/0.25 back toward it). Before v24.1,
  every load blended it 0.55/0.45 with the original.
- **Hub scaling follows learning.** Links of busy words (more than 12 links, one above 2.2, or a built-in common word) are multiplied by
  1 - 0.10 x min(1, L / 250) x depth at a wake-up sleep only, where L is the waking link strength added since the last
  sleep and depth the drained share of sleep pressure.
- **Sleep-made strength is balanced.** Link strength added while asleep (dreams, sleep's own links) is counted (S).
  At the next wake-up sleep, the links whose source shares are at least half dream/sleep are multiplied by
  max(0.5, 1 - S x depth / their total), and S is reduced by depth. A link strengthened only while asleep is not
  "used since the last sleep", so it can be released when weak.
- **Grounded ideas only.** A proposition found in a reply is linked only after the bridge confirms both of its words
  are grounded; otherwise at a quarter strength, faint.
- **Rejections.** A rejection of 0.5 or more hides a partner from recall, spreading activation and paths; a weaker one
  only scales new learning down.
- **Same word (v24.1.1).** Two words count as one (and are never linked) when one is the other plus a listed ending, or
  both reduce to the same rough stem (longest listed ending removed, a doubled final consonant undone), and their
  original vectors have cosine 0.5 or more.

## A10. Reading and people (v23.2, v23.4.1)

- `read(text)` learns a book line without a reply; links are tagged book; the line can't rename anyone, teach a
  definition, confirm a dream or count as idle time. `/read FILE [N]` reads N sentences a night (default 40), then a
  night (exit dreams + an 8-hour wake-up sleep), repeating; a bookmark per file name; a Project Gutenberg header and
  footer are skipped.
- **People.** "My name is X" from a second speaker adds a person instead of renaming the caretaker; `/whoami` switches
  the speaker; what a person teaches is tagged `user:<name>`; a new person's name starts calm and social.

## A11. Bridge between the engine and the LLM

- **Memory strength labels.** Recalled items are labelled for the LLM by strength: a note the user wrote (certain), a
  taught fact (strong), an often-recalled grounded episode (familiar, after 3 recalls with at least half its words
  grounded), a once-recalled episode (faint), a dream (dream, not a real event). Since v23.5.1 each episode also carries
  a time label from its timestamp (in the last hour, earlier today, this morning, last night, yesterday, N days ago,
  last week, weeks ago, months ago). When memory is weak and the message is a question, a line tells the LLM to say it
  doesn't remember rather than invent.
- **Careful learning from replies.** Reply words the brain neither predicted nor can ground in the user's words or
  trusted links are held back: linked at a quarter strength (or not at all, as a test switch).
- **Tone channel.** Temperature = 0.65 + 0.06 vZ - 0.08 max(0, -vA) - 0.15 (when unsure) - 0.15 arousal, within
  0.25..1.0; target length = round(4.5 x clip(1 + 0.12 vZ - 0.07 speed - 0.3 arousal, 0.5, 1.3)) sentences (2..8),
  where v is the turn's velocity on the three axes.
- **Notes file and undo.** A per-brain notes file written only by the user is added to prompts as certain memory;
  `/back` undoes the last message.
- **Honest self-report (v23.4.2).** When the message asks about the brain's state, its time alone, its sleep, a person,
  or (v23.5.1) the time, the prompt gets a facts block: the levels in plain words, the gist of the last idle record
  (where it started and ended, how it went, whether it went back over the recent conversation, up to 5 words; kept for
  6 messages), the last sleep, the per-person tone reading, the local date and time, the time since the previous message
  and the last break of 15+ minutes; plus a last-line rule to answer only from these facts and say it doesn't know
  otherwise. Other turns are unchanged.
- **Thought-claim check (v23.5.2).** Phrases like "I've been thinking about X" or "while you were gone I ..." in a
  reply are checked: X's content words (minus words about how a quiet stretch went) must appear in the recent idle
  records, their moods, or the speak-up packet; otherwise the status line flags the claim. Measurement only.
- **Outward voice style, thinking models, slant telemetry.** A test switch words the same brain material outward
  (feelings only when asked; engine words kept out). Reasoning models get a reasoning-effort setting and extra tokens;
  their reasoning text is never learned. Per-reply telemetry counts stock phrases, ungrounded key words and self-talk.
- **Tone sense (v23.4.1, experimental, measured only).** Each word is placed on a warm-cold line built from the original
  word vectors and hand-written example sentences; a message's tone is the average of its 3 most charged words.
- **Face page (v23.3.4, v23.5.4).** A local web page draws the four levels as a face (mood: mouth and colour; arousal:
  eyes and brows; sleep pressure: lids; novelty: pupils), shows what live idle is doing, and has a chat box whose
  messages go through the same turn function as the terminal. Chat from another device requires a password.
- **Auto-connect (v23.5.2).** The last LLM server that worked is saved and tried first at start-up, then a user list,
  then local defaults.

## A12. Related and prior work (additions)

As far as the author found; this list is not exhaustive.

- Borbély (1982), the two-process model of sleep regulation (sleep pressure plus a 24-hour process): reference for the
  daily rhythm (A9b); the engine's sleep pressure is the first process. Unlike that model, the rhythm here only shifts
  choices and does not wake a sleeping brain.
- de Vivo et al. (2017, Science): synapse sizes after sleep; reference for sparing the strongest 20% of links.
- Tononi and Cirelli's synaptic homeostasis hypothesis: the idea behind day-scaled fading.
- Rescorla and Wagner (1972): prediction-error conditioning; the "what follows" rule is in that style.
- Behrouz, Hashemi and Mirrokni, "Language Models Need Sleep" (arXiv 2606.03979, 2026): sleep-like consolidation and
  dreaming for LLMs; it inspired the author's sleep and dream cycles in an earlier side project, which led to the ones
  here. That work updates model weights; this engine's sleep acts on its own lattice and links.
- "Controlling Long-Horizon Behavior in Language Model Agents with Explicit State Dynamics" (arXiv 2601.16087): a
  valence-arousal-dominance state with position and velocity steering an LLM by prompt, without retraining. Closest
  found to this engine's level-and-velocity steering; that work has no lattice, learning or idle behaviour.
- Moshi (Kyutai, arXiv 2410.00037) and Sacks, Schegloff and Jefferson (1974) on turn-taking: references for the planned
  multi-brain real-time conversation.
- Generative Agents (Park et al., 2023): memory streams with reflection; related to idle time and memory labels.
- Letta, sleep-time compute (arXiv 2504.13171), and the Gubernaut Cognitive Controller (arXiv 2607.24339): related to
  offline processing and to a homeostatic controller setting an LLM's sampling.

## A13. Known limitations of the additions

- Most weights are first guesses; the tests that exist are short simulated runs on a few brains, plus the author's own
  conversations. Nothing here has been evaluated with outside raters.
- The honest self-report and the packet instruction depend on the LLM following its prompt; the claim check catches only
  one family of phrasings, and an LLM can still decorate (an observed reply claimed to "remember now" a word it had just
  asked about).
- The tone sense confuses topic with tone and was tuned after one failed attempt; it is shown, not used.
- Brains differ a lot under the same rules (in one simulated 8-hour day one brain made 72 thought steps, another 20);
  idle and speak-up behaviour should be judged per brain.
- Live idle and speaking up are experimental and off by default.
- The daily rhythm is a fixed cosine with its low point at 3 pm; it has no morning waking (a brain asleep stays asleep
  until a message arrives) and is not learned from when the person talks. Felt time is not used by anything yet; in lab
  runs busy hours felt about as long as the clock while passing rather than shorter, because boredom as measured rarely
  falls below about 0.4.
