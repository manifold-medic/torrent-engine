# Changelog

All notable changes to T.O.R.R.E.N.T. Newest first. The engine (`torrentengine.py`) also keeps this history in the
comment block at the top of the file. Versions before v21.1 (v10 to v21.0) were not recorded in a changelog.

## v22.3 (2026-11-08)
- **Nightmare mode** (off by default, saved per brain). Turns off the engine's "lean up" rules so a brain can learn and
  dream about frightening things the way it learns anything else: negative words can become names, dream bridges,
  recall results and spreading-activation paths, and sleep's comfort bridge (Contrastive Self-Correction) is skipped.
- Turn it on or off with `/nightmare` (engine CLI or bridge). It is stored in the brain file as `nightmare_mode`, so a
  brain stays in the mode you left it in. `TORRENT_NIGHTMARE=1` (or `0`) sets it at start-up for test runs.
- The bridge shows `🌑 nightmare` in the status line and a banner line when it is on.

## v22.2 (2026-11-08)
- Sleep record fixes: all of a sleep's dreams are kept even when the dream journal is full (before, a brain away 87 hours
  dreamed 12 times but remembered 1); time asleep and time away are reported separately ("slept about 8 hours, away
  about 87"); a sleep is a nap (under 4 h), a short night (4-8 h) or a full night (8 h+).

## v22.1 (2026-11-08)

### Engine
- **The brain remembers its sleep.** Every wake-up sleep records when it woke, how long it slept, nap or full night,
  the dreams it had and how many links it released (`last_sleep` in the brain file).
- **Sleep pressure as a level:** rested / building / high / very high, measured in busy days of waking learning
  (one busy day, about 40 sentences, = 250). Learning itself is unchanged.

### Bridge (`ltcmbridge.py`)
- When you ask about sleep, dreams or being tired, the model is given the brain's real record of its last sleep, so
  it no longer invents one. A brain named after a sleep word (e.g. Dream) doesn't trigger this by being addressed.
- When sleep pressure is high, one plain line tells the model the brain is ready to rest (and not to dramatize it).
- The status line shows `Sleep: <level>`.

## v22.0 (2026-11-08): "sleep v2"

Sleep now works like a simple version of real sleep: what the brain learns while awake builds sleep pressure, and
sleep scales things back down in proportion to it.

### Engine
- **Sleep pressure.** Learning while awake (talking with the brain) builds pressure. It is saved in the brain file
  (`sleep_pressure`) and drained at wake-up, where the time away is known. Depth = hours away / 8, capped at 1: a
  2-hour nap drains a quarter of the pressure and does a quarter of the scaling; a full night drains it all; sleeping
  longer does nothing extra. Under 30 minutes away is still no sleep. `/exit` no longer fades anything (it still
  dreams, scales hub links and runs the self-correction).
- **Only waking learning counts.** Links made by sleep itself (cleave veins, dream links, self-correction) still form,
  but don't count as the day's learning.
- **No overnight cliff.** One sleep releases at most max(2% of all links, links created since the last sleep), weakest
  first. A saturated test brain used to release ~24,000 links in one night; now ~680 a night.
- **The strongest 20% of links are spared** from the nightly scaling, after de Vivo et al. 2017 (*Science*):
  synapses are ~18% smaller after sleep, proportional to size, mostly in the weaker ~80%.

### Bridge (`ltcmbridge.py`)
- What the brain learns from the LLM's reply now counts as waking learning (builds sleep pressure).
- Header shows v22.

## v21.9 (2026-11-08)
- Sleep scales cells and links down in proportion to how much the brain learned since its last sleep. A quiet day
  barely fades; a busy day fades more; a brain nobody talks to doesn't fade at all.
- Cells: the fixed x0.97 per sleep (v21.7) became 1 - 0.000347 x placements added. At 12 sentences a day, v21.8 had
  shrunk to 152 cells and 2 words per cell by day 40; v21.9 kept ~307 cells and ~6 words per cell.
- Links: every link scales by 1 - 0.000179 x link strength added; the 0.25 link floor is removed (it existed twice:
  in the hub scaling and in the load-time repair). Links under 0.15 that weren't used since the last sleep are deleted.
  A word with no links left leaves the link graph (its weights and vector stay).
- The built-in starter links (the semantic cluster lists) fade like any other link and are no longer reset on load:
  protecting them re-saturated a busy test brain.
- First version that can delete links.

## v21.8 (2026-11-08)
- Crystals no longer drift down over time. The "hub" test for crystal material was a fixed 18 links, but link counts
  only grow, so more and more words stopped counting. Now a hub is a word in the top 10% of link counts.

## v21.7 (2026-11-08)
- The torus no longer saturates. Before, every landing in a cell was permanent: a fresh brain fed Alice in Wonderland
  had all 343 cells crystallized by day 23 and cleaved ~800 times a day, and "said" sat in 217 cells.
  - Pruning: cell counts fade in sleep; placements under 0.5 leave the cell.
  - Spread cap: one word may live in at most 10 cells, keeping its strongest placements.
- Names at the origin cell (3,3,3) are protected. Links, weights and memories are untouched.
- `catchup_cells.py`: optional one-time cleanup for a brain that saturated before v21.7 (works on a copy).

## v21.6 (2026-11-08)
- Sleep's comfort bridge habituates: a bridge used in recent sleeps is less likely to win again, and only words the
  brain has actually been told can be bridges. Before, "quiet" won ~44% of the time and became one of the brain's
  strongest words ("the quiet problem"); now ~2%. New brain-file keys: `bridge_habituation`, `experienced_words`.

## v21.5 (2026-11-08)
- The annealing log is honest: a demotion is reported once, after the crystal's final rebuild (it was printed twice
  and then undone). Brain behaviour unchanged.

## v21.4 (2026-11-08)
- Teaching definitions works with training wheels off and in natural sentences, one sentence at a time, including the
  quoted form `a 'TCM' is a 'Toroidal-Crystalline Manifold'` (also *means / stands for / represents*).
- "X means a b c" no longer also becomes a misleading one-word idea.

## v21.3 (2026-11-07)
- Names vs words: a name that is also a normal word (Hope, Drift) only counts as a name when used as one.
- Filler words with real meaning (together, talk, people, hello, goodbye, night...) now move the brain and land in
  cells, but stay out of crystals, dreams and bridges.
- Word splitting: dashes, slashes, ellipses and hyphens separate words; possessives drop their 's;
  "good night" becomes "goodnight".
- Wraparound damping: each trajectory step moves 3/16 of a cell, so a turn travels ~1-3 cells in the direction of its
  push instead of lapping the 7-cell ring.

## v21.2 (2026-11-07)
- Brain picker: brains live in a `brains` folder; menu at startup, `--brain NAME`, `--new`. `/clear` asks you to type ERASE.
- Divergence ratio divides by 8 (it was capped at 88.9%).
- GloVe startup cache (`*.torrentcache.json/.bin`): later starts load in seconds, identical numbers.
- The "X is Y" teaching trigger ignores vague subjects ("something is wrong"), names, and sentences about I/you/we.
- Self-naming: answering "no" / "not yet" leaves the brain unnamed instead of naming it "No".

## v21.1
- Learned negative weights are kept on load (an old reset turned them into +0.5); negative words can be dream threads.

## Bridge (`ltcmbridge.py`), 2026-11-07 / 08 (not versioned separately)
- "Corpus callosum" features: memory lines labelled by strength, careful learning (reply words not grounded in what
  the brain gave the model are learned only faintly), and a tone channel (the brain's state sets the model's sampling).
  Toggle with `/callosum`.
- Per-brain notes the user writes (`/note`, `/notes`), `/recall`, and `/back` to undo your last message.
- Chat history carries over within a session; summaries are cut at word boundaries (no more word fragments).
- `TORRENT_SEED` makes the model's randomness repeatable for tests.
