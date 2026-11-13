# Changelog

All notable changes to T.O.R.R.E.N.T. Newest first. The engine (`torrentengine.py`) also keeps this history in the
comment block at the top of the file. Versions before v21.1 (v10 to v21.0) were not recorded in a changelog.

## v24.1.1 (2026-11-12): fixes from a second review
Fable 5.2 re-reviewed v24.1 (19 of its 32 findings fully fixed, the rest partly or with side effects) and found
three new medium problems, now fixed with the rest:
- **Model server started late:** the bridge now always re-checks for it on a turn while it isn't connected, which
  also picks the brain's saved model (before, a server on the default port with a model other than `gemma2` gave a
  404 every turn).
- **Naming offer:** hesitant answers no longer become names ("yeah I guess" named a brain "Guess"); a clear yes takes
  the proposed name, "not sure" or "let me think" leaves it unnamed, a naming form ("I like Echo better") names it.
- **Truth and lie words:** the built-in truth/lie rule no longer pushes these meanings apart at every start.
- Smaller: two forms of one word count as one (learned/learning, run/running) only when their meanings agree
  (part/party don't); the dream balance only counts dream/sleep links; "call me curious" no longer adds a person;
  `/voicechat` and `/listen` no longer stop the bridge when the microphone library can't load (Linux); Ctrl+C in voice
  chat can't leave the brain unlocked; "so ill be back" becomes "so I'll be back"; `/clear` deletes the erased brain's
  notes; summaries wait their turn for the model; the face page also checks the Host header; the notes line's label no
  longer counts as grounded; `TORRENT_NIGHTMARE` applies to loading learned weights; 1-2 letter names mid-chat aren't
  registered.
- From a Kintsu field run: "Do you know how long I was gone?" now gets the time facts (only "how long was I gone"
  was recognised), and '"thankfully" means fortunately, in the way I used it' stores the meaning (the part after the
  comma used to block it).

## v24.1 (2026-11-12): fixes from a full code review
A full review of the engine and bridge by Fable 5.2 found 32 issues; these are fixed (numbers are the review's):
- **Learning lasts across restarts [1].** Loading a brain used to pull every learned word meaning about halfway back
  to its original GloVe meaning, so a few restarts undid most of what words had learned. Meanings now load as saved
  (still within the usual limit on how far a meaning can drift).
- **No fading without learning [5].** The step that scales down busy words' links ran at every `/exit` and `/dream`,
  even when nothing was learned. It now runs only at a wake-up sleep, scaled by how much was learned that day.
- **Sleep doesn't pile up its own links (new).** Fixing [5] showed that dreams kept adding strength with nothing to
  balance it (a brain nobody talked to grew 25% in a week in a test). What sleep adds is now taken back at the next
  wake-up sleep from links that are mostly sleep-made; a real memory that a dream replays keeps its boost.
- **The voice:** facts the engine writes itself ("my creator and conversational anchor") are no longer shown to the
  voice as things you taught [2]; label words from the prompt ("memory", "familiar", "dream") no longer count as
  grounded, dream lines and sleep lines don't ground anything [6]; an idea made of invented reply words no longer
  leaves a full-strength link [4].
- **The bridge:** if it starts before the model server, it now finds the server later by itself [3]; a speak-up and
  your message can't use the model at the same time [7]; `/clear` stops live idle and keeps your bridge settings [9];
  the face page's chat only accepts messages from the page itself [11]; `/back` keeps settings changed since the
  message [26]; `/live on` restores speaking up [27]; `/voicechat` uses the same turn as typed messages and no longer
  freezes live idle [28]; Piper falls back to another voice when nothing can play its sound [29]; a bad `/connect`
  port no longer stops the bridge [14]; a retry keeps the turn's tone [13]; notes with apostrophes teach the whole
  definition [22]; small fixes to time labels and "I'll" [32].
- **The engine:** "call me later" no longer adds a person named Later [8]; one "X is not Y" only weakens the link
  instead of hiding Y from recall for days [10]; a doze cut short is recorded for the time it lasted [12]; the
  seen-once rule covers a new brain's first message [15]; made-up words have no calm "home" [16]; the
  `TORRENT_...` switches apply to the wake-up sleep too [17]; "I like Echo better" at the naming offer names it Echo
  [19]; speaking up about a barely known word skips taught words [21]; names need 3+ letters [23]; `/export` before
  any message no longer moves the brain [24]; words that only share their first 4 letters can now be linked
  ("computer" and "company") [25]; cleave veins don't add to sleep pressure [30].
- **Kept as is, on purpose:** the crystal rule's "2 visits" also counts sleep passes [20]. Counting only real visits
  cut crystals from 145 to 9 in a 20-day test, so it would be a design change, not a fix.
- Test (20 simulated days of reading, same seeds): words 1264 -> 1287, crystals 145 -> 143, total link strength +39%,
  learned meanings kept (average shift from the original meaning 0.013 -> 0.081).

## v24.0.1 (2026-11-12): review fixes
- From a code review by Fable 5.2: the fix for re-spent silences now works from every way a silence is closed; in felt
  time, an unfinished doze or rest no longer counts whole, a first silence always looks back equal to the clock, any
  new link counts as engaged, a thought back that starts a walk counts, and a usual of 0 is saved. Felt time is told to
  the voice only with the rhythm on and only for a recent time alone.

## v24.0 (2026-11-12): a sense of time, part 2 (experimental)
- **Daily rhythm** (`/rhythm on`, off by default, saved per brain). Using this computer's clock, the brain's idle
  choices follow a 24-hour cycle: at night sleep and dozing come easier and thinking and speaking up less; in the
  afternoon sleep comes harder. The pull is strongest at 3 am and 3 pm and zero at 9 am and 9 pm. `/rhythm +3` moves a
  brain's night three hours later (for someone on a night schedule); `/rhythm off` removes it. It only changes what the
  brain chooses while left alone; a message is learned the same way at any hour.
- **Felt time** (measured and reported only). Each silence records how long it seemed looking back (busy stretches
  seem longer, sleep shorter) and, with live idle, how long it felt while it passed (bored stretches drag). When you
  ask about the time or about a recent time alone, and the rhythm is on, the voice is told these numbers if they differ
  from the clock by more than a quarter. The `💭` status line shows them as `⏳ felt passing/looking-back min`.
- At night (with the rhythm on) the facts the voice gets when asked how it is include "By your own daily rhythm it's
  night now."
- Fix: closing a live silence early (`/live off`, `/sleep`, `/read`) left its start time in place, so the next message
  spent the same silence a second time.
- Reviewed by Fable 5.2 before release; its findings (all in the new felt-time code, plus the fix above) are fixed.
- Lab tests (fake clock, 20 runs each on copies of two brains): starting at 9 am, rested brains no longer fell asleep
  before 5 pm (without the rhythm, about half did); starting at 10 pm, most fell asleep within 3 hours; speak-ups
  between midnight and 6 am fell by more than half, because the brain was asleep. With the rhythm off, every choice
  and the saved brain are identical to v23.5.5.

## v23.5.5 (2026-11-12): bridge fixes
- The face shows what live idle is doing: eyes closed with a sleepy peek while dozing, lowered lids while resting,
  eyes up and to the side while thinking back, a quick glance on a leap, and more looking around.
- The thought-claim check counts a word in quote marks ('step') as the word itself.
- When live idle starts by itself, a second line says whether speaking up is on.
- "ill be / ill let / ill check ..." from voice-to-text becomes "I'll ..." before the brain sees it (brains were
  learning the word "ill"). "I feel ill" is left alone.

## v23.5.4 (2026-11-12): chat from the face page
- **Bridge only** (the engine changed only its version number). The face page (`/face`) has a chat box: a message
  typed there is handled exactly like one typed in the terminal (same brain, same voice, same learning), and the
  terminal still prints everything. The page shows the last 40 messages, including the brain's own speak-ups.
  Commands stay terminal-only. Chat from the page works only on the same device unless `TORRENT_FACE_PASSWORD` is set.
- The thought-claim check (v23.5.2) no longer flags words about how a quiet stretch went ("a calm space" after a calm
  idle walk).

## v23.5.3 (2026-11-12): speaking up (experimental, off by default)
- With live idle on, `/speak on` lets the brain send the person a message first. Speaking up is one more option in the
  idle race, with its own urge: something to say (a word the person used that the brain has seen only once, a new link
  made by a leap, a surprising moment thought back to, a walk that settled), missing the person (scaled by the brain's
  own mood after that person's messages), boredom, minus tiredness and minus each unanswered message in a row, plus a
  learned habit (answered within 30 minutes: up a little; unanswered for 2 hours: down a little).
- The brain decides what the message is about and hands the bridge a small "packet"; the voice only puts that into
  words and is told not to add other thoughts or events. Fixed limits: 20 minutes of silence first, 45 minutes between
  speak-ups, never while asleep or dozing. Optional phone notification on Termux (`TORRENT_NOTIFY=1`).

## v23.5.2 (2026-11-12): live idle for a whole day + bridge fixes
- Live only: the count of thought steps and the replay limit start again after a doze, so a long silence alternates
  thinking and dozing instead of thinking for ~36 minutes and then only resting. The all-at-once path is unchanged.
- Bridge: connects by itself to the last LLM server that worked (saved in `torrent_hosts.json`), then `TORRENT_HOSTS`,
  then the defaults. Asked what it thought about while alone, the voice gets the gist (where the thoughts started and
  ended, how it went) instead of a raw word list. A measure-only status flag (`💭?`) when the voice claims thoughts the
  idle record doesn't back.

## v23.5.1 (2026-11-12): a sense of time, part 1 (bridge only)
- Asked about the time ("what day is it?", "how long was I gone?"), the voice is told the date and time on this
  computer, how long ago the previous message was, the last long break, and the last sleep. Other turns don't get it.
- Recalled past moments carry a "when" label after their strength label ("last night", "yesterday", "3 days ago").

## v23.5 (2026-11-12): live idle (experimental, off by default)
- `/live on` (needs idle time and the levels on): a background clock lets the brain spend a silence while it happens,
  one choice at a time, instead of all at once when the next message arrives. The face shows what it is doing
  ("wandering · rain · 12 min on its own"). A lock keeps the clock and a message from touching the brain at once.
- Live-only differences: sleep lasts until something wakes it (the sleep pass runs at wake-up for the hours actually
  slept; woken within 30 minutes it counts as a doze), and a doze is never cut short.

## v23.4.3 (2026-11-12): one clock
- Every place the engine reads the time goes through one front door, `now()`. Nothing changes in normal use; tests can
  give a brain its own clock, so timed runs repeat exactly.

## v23.4.2 (2026-11-11): honest self-report (bridge only)
- Asked about its insides ("how are you?", "what were you thinking about while I was gone?", "did you sleep?"), the
  voice is given the brain's real facts (its levels in plain words, its last time alone, its last sleep, what it keeps
  about each person) and told to say it doesn't know anything not covered. Other turns are unchanged.

## v23.4.1 (2026-11-11): reading, tone sense, voice fixes
- `/read <file> [N]`: the brain reads a text file as a book, N sentences a night (default 40) with a sleep between,
  bookmarked per file. Book lines get no reply and aren't treated as someone talking.
- Tone sense (experimental, measured only): a rough warm/cold reading of each message, shown on the status line and
  the face; it changes nothing in the brain.
- The mood baseline the valence is measured against follows about the last 70 turns instead of 14.
- Voice fixes: Piper found without PATH setup, silence and Whisper "phantom" phrases ignored, `/voicechat N`, Ctrl+C
  goes back to text. `/whoami` alone goes back to the caretaker.

## v23.4 (2026-11-11): idle option menu
- During a silence (idle time and levels on) the brain chooses, one decision at a time, between wander, leap, replay
  (think back to a recent moment), doze and sleep. Each option's urge comes from the levels plus a learned habit, and
  the urges race to a line that is lower when the brain is wound up. Fixed safety rules sit underneath (very high
  sleep pressure forces sleep; replay limits; idle can't push arousal above 0.8). Every choice is logged with its
  reasons (`/idle why`).

## v23.3.4 (2026-11-11): face visualizer (bridge)
- `/face` opens a small local web page that draws the four levels as a face, with the numbers in bars beneath. It is a
  visualizer of the numbers, labelled as such.

## v23.3.3 (2026-11-11): negation fixes, verbs from the brain's own relations
- A "not" reaches only the word it is attached to; a "these don't go together" mark is recorded only for real "X is
  not Y" sentences, once. A negated word pushes mildly the opposite way. When the brain words a link, opposed pairs get
  opposing verbs.

## v23.3.1-v23.3.2 (2026-11-11): bridge
- `/voicestyle inward|outward` test switch; slant telemetry counts self-talk. Thinking models (gpt-oss, kimi...) get
  extra tokens and a lower reasoning effort, and an empty reply is retried once; their reasoning text is never learned.

## v23.3 (2026-11-11): levels, step 2
- Valence becomes its own level with soft edges (no more flips across the ring's edge). One clock lets time pass for
  every level. Sleep pressure gains a clock part (hours awake). New novelty level. The last 20 turns are kept for replay.

## v23.2 (2026-11-11): reading mode and people
- `read(text)` learns a book line without treating it as someone talking. "My name is X" from a second person adds a
  new person instead of renaming the caretaker; `/whoami`, `/people`; links remember which person taught them. Crystal
  events print as one summary line (`/tectonics` shows each).

## v23.1 (2026-11-10): rejections fade
- A negated sentence used to delete and ban links between its words forever. Rejections are now weighted, weaken
  links instead of deleting them, and fade in sleep.

## v23.0 (2026-11-10): levels, step 1 (on by default)
- Two levels with clock-time clearance: valence (mood) and arousal (wound up). Arousal sets how strongly a turn is
  learned and shortens and cools the voice's replies. The names are vocabulary for this engine only, not medical or
  neuroscience claims. `/levels` or `TORRENT_LEVELS=0` turns them off.

## v22.11 (2026-11-10): "what follows" learning + seen-once rule
- A word slowly takes on the calm or tension of what tends to follow it. A word typed in only one message gets faint
  links and no cell until it shows up again (typos like "I tam cold" no longer become hubs).

## v22.10 (2026-11-10): calm learning
- Words' calm numbers learn from the company they keep and relax a little toward their original meaning each sleep.
  Trace labels show the actual move. Bridge: `/timestamps`.

## v22.8-v22.9 (2026-11-09/10): idle time (experimental, off by default)
- `/idle`: the silence since the last message is spent wandering the brain's own links, faintly learned and tagged
  "idle". v22.9 fixed the review findings (faint links really faint, boredom leaps, a way out of tense loops).

## v22.7-v22.7.1 (2026-11-09): source tags + packaged word file
- Every link remembers who made it (user, voice, sleep, dream, built-in...). Words reached only through untrusted links
  can't become bridge words or thought-path steps.
- `torrent_wordspace_50k.gz` (~20 MB) ships the processed GloVe vectors, so a word file no longer has to be downloaded.
  Without it or a GloVe file, the engine warns that it is in test mode. `/flip` and cell names survive restarts.

## v22.5-v22.6.4 (2026-11-09): surprise-driven learning, mood level, fixes
- v22.5: after each turn the brain writes down what it expects next; the surprise on the next turn sets how strongly
  that turn is learned. The bridge reports "self-match" (how many of the reply's words the brain predicted).
- v22.6-v22.6.1: experimental mood level (`/moodlevel`), so where a turn lands follows what was said.
- v22.6.2-v22.6.4: slant telemetry (`/slant`), built-in sayings no longer shown as memories, fixes from a code review.

## v22.4 (2026-11-09)
- Definitions are learned only from clear forms ("X means Y", "X is a kind of Y", quoted). `/facts forget <word>`.
  Typo rule for words outside the dictionary.

## v22.3.1 (2026-11-09)
- Nightmare mode shows in purple (off with `NO_COLOR` or when output isn't a terminal).

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
