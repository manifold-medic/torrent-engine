# T.O.R.R.E.N.T. — Technical Disclosure, Addendum 2 (v24.1.2 to v25.0.0)

- **Disclosure date:** the date of the first public commit of this file in the repository named below
- **Author:** manifold-medic
- **Files described:** `torrentengine.py` (engine, version 25.0.0) and `ltcmbridge.py` (bridge, version 25.0.0)
- **Repository:** https://github.com/manifold-medic/torrent-engine
- **License:** Apache-2.0
- **Relationship to earlier disclosures:** `TORRENT_DISCLOSURE.md` describes engine v21.0 and
  `TORRENT_DISCLOSURE_ADDENDUM_1.md` describes v21.1 to v24.1.1. This addendum describes what was added or changed from
  v24.1.2 to v25.0.0, in enough detail to re-implement it. Where they differ, this addendum describes the current code.
  `CHANGELOG.md` and the comment block at the top of `torrentengine.py` give the version-by-version history.

## B0. Purpose

Like the earlier documents, this is a **defensive disclosure**: it places these techniques in the public record as of
the date above, so they remain free for anyone to use and cannot later be patented. The author asserts no patent claims
over what is described here. Everything below describes what the code does; numbers are the current defaults, which
are first guesses unless a test is mentioned. Words such as "mood", "trust", "together", "arousal" or "overstimulation"
are vocabulary for parts of this engine only; no psychological, medical or neuroscientific claim is made.

Most features below are **per-brain switches, off by default**, saved in the brain file. Section B7 describes how a
"standard" setup turns the tested ones on together.

## B1. What the axes mean

The lattice has three axes (S, A, Z), each with 7 cells on a ring. A word's starting weight on each axis is its GloVe
vector projected on a direction built from seed words.

- **A, the Mood Ring (v24.4.2).** Checked against human word ratings (Warriner, Kuperman & Brysbaert 2013; NRC VAD
  lexicon), A's starting weights correlate with rated valence (+0.59 and +0.54) and weakly against arousal (about
  -0.3); A=0 holds fear and anger words, A=6 joy and trust words. Its labels became, from 0 to 6: Distressed, Tense,
  Uneasy, Neutral, At ease, Content, Joyful (the older labels described A=0 as stillness and A=6 as luminous clarity).
  The rating sets are used only to derive and check the labels; they are not shipped.
- **S, rebuilt (v24.4.1).** The old S direction tracked rated socialness only weakly (+0.24) and overlapped with mood
  (+0.37). With `/snew`, a word's starting S weight is its GloVe vector projected on a direction fitted by ridge
  regression to human socialness ratings (Diveica, Pexman & Binney 2023; 7,417 rated words found in GloVe): "about
  things" (0) to "about people" (6), correlating +0.71 with the ratings on held-out words and +0.07 with mood. Only the
  fitted direction (50 numbers, `FITTED_S`) is in the engine; it is centred so a typical word starts at 0 and scaled to
  the old S spread. Words a brain already has an S number for keep it. Labels (the People Ring): Material, Mechanical,
  Mixed, Factual, Shared, Personal, Social.
- **Label sets** (`/newlabels`): the axis names, each cell's starting description, the two-word starting cell names and
  the feeling words used for evolved cell names come from one table (`NEW_LABELS`). Cells a brain has used keep their
  learned meaning; names the user gave a cell are always kept. The evolved-name feeling list drops five stillness and
  light words and adds unpleasant and mixed feelings.

## B2. What happens at the ends of an axis

The lattice is a torus: each axis is a ring. Three switches decide what a turn does at an axis's ends.

- **S learns from its real position (v24.4.0, `/sfix`).** A word's S number learned from the landing cell, (S - 3)/3,
  and the landing cell wraps, so a turn pushed past one end taught its words the opposite end (about 1 turn in 4 in a
  replay). With the switch on it learns from the exact, unwrapped S position the trajectory already keeps, clipped to
  -1..+1 (the same fix the mood level received in v23.3).
- **The S edge (v24.4.4, `/sedge walls|overstim|wrap`).** `wrap` is the ring. `walls` stops S at 0 and 6. `overstim`
  is a wall at "about things", and at "about people" the turn wraps round to "about things" only while the brain's
  arousal is at least `OVERSTIM_AROUSAL` (0.5, from the turn before) and the step starts at S >= 5.0; otherwise a wall.
  Walls alone piled turns against one end, so with `walls` or `overstim` S also gets: the push as an average over a
  message's words (x1.5) instead of a sum; measured against this brain's usual S push (seeded from plain text, adapting
  30% a turn); a dead zone (`S_DEAD_ZONE` 0.5); no built-in tilt from the first step; soft edges (an outward step is
  multiplied by 1 - |u|^6, u = distance from the middle as a share of the half-range); and clearance (S relaxes 50%
  toward the middle before each turn, `S_CLEARANCE`).
- **The A edge (v24.4.7, `/aedge wrap|walls|level`).** The reply's Mood Ring cell wrapped, so a turn one step past
  Joyful landed on Distressed while the continuous mood level read near +0.8. `walls` clips each step's A cell to
  0..6. `level` sets the reply's A cell to the mood level's own cell: round(3 + 3 x valence). The mood level, arousal and
  the next turn's starting point are the same in all three modes; only the cell the voice is given changes. Replay on
  four brains: 1-10 wrong-end cells per brain with `wrap`, 0 with `walls` or `level`.
- **Z follows the push (v24.1.2, `/zpush`), with clearance (v24.4.6).** On the active path Z used to move at least one
  step every step and restart at 0 after 6, so it worked as a turn counter. With the switch on, Z steps by the message's
  own Z push (no step when |vZ| < 0.5), stops at 0 and 6, and relaxes 50% toward the middle before each turn
  (`Z_CLEARANCE`), which stopped turns piling up at Z=6.

## B3. Measuring the mood

- **Weak pushes (v24.3.4, `/moodfix`).** The mood push comes in whole steps with a minimum of one, so a slightly cool
  message moved the mood a full step. With the switch on, a scaled push weaker than `A_DEAD_ZONE` (0.5) is no push, and
  the shared first step no longer moves A, so up and down moves are the same size.
- **Mood zero (v24.3.0, `/moodzero blank|usual`).** `usual` measures the mood against a running average of the
  brain's own pushes, which learns the warmth of whoever talks most. `blank` measures it against the average push of 16
  fixed, feeling-free sentences (`BLANK_SENTENCES`) computed with this brain's own word numbers, re-measured at each
  wake-up sleep, and stretches each side of that zero to the full push range. Each person's own usual push is also kept,
  measured only, and each message's push compared with it ("vs their usual").
- **Names don't push (v24.4.6, default on).** A brain's or a person's name used as a name pushes nothing, isn't a
  question and isn't surprising; used as an ordinary word ("I wonder") it counts as before.

## B4. Two brains talking (v24.2.0, v24.2.1)

- `peer_respond(text, name, trusted=False)` answers another brain's line like a person's, but tags what it teaches as
  `peer:<name>` (untrusted). A peer line can't teach definitions, confirm a dream or rename the brain.
- An untrusted peer's line is learned faintly: links at `PEER_LEARN` (0.25) and new links start faint; calm, social
  and depth numbers move a quarter as much; no cell deposits, renaming or cleaving; its "X leads to Y" ideas aren't
  kept. A trusted peer is learned like a person. (Two brains repeating each other for about 80 rounds had made one word
  the top hub of both.)
- The bridge runs the dialogue (`/dialogue`): both brain files are copied to a `backups` folder first. A line
  "repeats" when 80% of its words were in the line it answers or in the speaker's own last line
  (`DIALOGUE_ECHO_LIMIT`); three repeating lines in a row end the dialogue (`DIALOGUE_ECHO_STRIKES`, `echostop=off` to
  watch a loop on copies).

## B5. What the voice is shown

These are bridge settings for testing how the language model (the "voice") is influenced by what it is given.

- **Link line (`/linkline asis|gated|hint|both`).** The brain's connection between two words is shown as written,
  only when its bridge word came up in the message or is linked to it (`gated`), as a background hint the voice is told
  not to state (`hint`), or both.
- **Coordinate words (`/labels plain|original`).** Which words describe the coordinate to the voice.
- **Sequestrant (`/sequestrant on|off`).** Words whose link strength came mostly (> 50%) from the voice or another
  brain are left out of what the voice is shown (words "on its mind", memory lines, the running summary), so a brain and
  its voice can't keep handing each other the same words. Learning is unchanged.
- **Outward or inward voice style (`/voicestyle`).** Outward asks the voice to look at the person and the topic and
  mention its own feelings only when asked; inward lets the coordinate shape tone and perspective.

## B6. Text clean-up (v24.4.8)

- The bridge restores apostrophes that voice-to-text drops: "ill" before words like be/do/let (not after feeling or
  being words: "I feel ill"), im, dont, cant, itll, thatll, and "id" as "I'd" only before words like like/rather/say
  and not after a/the/my/your/his/her/their/our.
- The engine splits contractions whose apostrophe-less form is a different real word: he'll, she'll, he'd, she'd
  ("hell", "shell", "shed" before), it'll, that'll, there'll, what'll, who'll, it'd, that'd, who'd.

## B7. Standard and research setups (v24.5.0)

- A per-brain setting, `standard` or `research`, is kept in the brain file. `standard` turns on every switch that has
  passed its tests (B1-B2's `/zpush`, `/moodfix`, `/sfix`, `/snew`, `/newlabels`, `/sedge walls`, `/aedge level` and the
  link line as a hint; a brain already on `overstim` or A `walls` keeps that choice) and shows only the everyday
  switches in the switch list and help. `research` shows every switch and changes none.
- New brains made by the bridge start on `standard`; brains made before this version count as `research` until
  switched, so nothing changes under an existing brain. The engine's own defaults are unchanged, so scripted lab runs
  that create brains without the bridge are unaffected.
- The daily rhythm (v24.4.9) reports four parts of the day by the brain's own clock: night (11 pm-7 am), morning,
  afternoon, evening.

## B8. Trust (v24.6.0, measured only)

Each person, and each other brain met in a dialogue, has a trust number. Nothing in the engine or the bridge reads it
to change learning, listening or movement; it is computed, saved and shown.

- **Counting.** Per name: `good` and `bad` experience totals. trust = (a0 + good) / (a0 + b0 + good + bad), as in the
  beta reputation system (Josang & Ismail 2002). The caretaker (the brain's main person) starts at a0:b0 = 3:2 (0.60);
  everyone else at 2:2 (0.50).
- **Fading.** Before each new experience, both totals are multiplied by 0.5^(days since the last update / 14).
- **Experiences**, grouped after Mayer, Davis & Schoorman's (1995) parts of trustworthiness:
  - Tone (benevolence): a message the tone reader calls warm adds 0.1 to `good`; cold adds 0.1 to `bad`; another brain's
    lines count a quarter of that.
  - Keeping your word (integrity): a message matching a promise to return ("I'll be back", "be right back", "brb",
    "talk to you later", "I will return"; "see you tomorrow"; "back in N minutes/hours") opens a promise with a deadline:
    24 hours, 36 hours for "tomorrow", or 3 x N for "back in N", at least 2 hours. The person writing again before the
    deadline adds 1.0 to `good`; the deadline passing first adds 1.0 to `bad`, dated at the deadline. One open promise
    per person; a new message resolves the old promise before opening a new one. Another brain's lines make no promises.
  - Answering the brain (integrity): when the brain speaks up first (live idle), the person answering within 30
    minutes adds 0.5 to `good`; no answer for 2 hours adds 0.5 to `bad` (the speak-up's own habit timings).
- **Right now.** trust_now = trust + 0.1 x the brain's current valence (-1..+1), clipped to 0..1: the brain's own
  side ("propensity to trust").
- Test (fresh brains, a fixed clock, real GloVe): replaying the same 29 messages with and without trust gave identical
  cells, mood and learned numbers; a kept promise lifted 0.60 to 0.645, a broken one dropped it to 0.508; 14 quiet days
  brought a raised value halfway back.

## B9. Connection: together and alone (v25.0.0, measured only)

Each word learns a number for whether the brain meets it with someone or alone. Nothing reads it to change the torus,
learning or the voice.

- **The number.** `together_weights[word]`, from -1 (met alone) to +1 (met with someone). Every word starts at 0: no
  human rating set measures felt togetherness, so each brain builds its own from what happens to it.
- **A moment's togetherness, m:**
  - a message from a person: m = trust_now in that person (0..1, B8), so a distrusted person feels less "with";
  - a line from another brain in a dialogue: the same m, learned at a quarter of the rate;
  - a word visited during idle time (wandering, leaping, thinking back while nobody is talking): m = -1;
  - a speak-up nobody answered for 2 hours: its words, m = -1 at 1.25 times the rate;
  - sleep and book reading: nothing.
- **Learning.** For each word the moment touches (a message's top six concepts, or the idle word), w += 0.05 x rate
  share x (m - w), clipped to -1..+1.
- **Pull back.** At each wake-up sleep every number is multiplied by 1 - 0.05 x sleep depth, so a single long stretch
  alone can't make every word "alone"; only words the brain actually met move at all.
- **Together level.** A brain-wide level from -1 to +1: a message moves it halfway toward that message's m; each idle
  step moves it 2% toward -1.
- Test (fresh brains, a fixed clock, real GloVe): with and without the feature, cells, mood, calm and social numbers
  were identical; after 29 messages, 78 words had a number, all on the together side; a speaker at trust 0.3 taught
  exactly half as much as one at 0.6; one night pulled every number back by 5%.

## B10. Considered and not taken

- **Changing the engine's own defaults for the tested fixes:** it would change every scripted replay and every existing
  brain, so the standard setup lives in the bridge (B7).
- **Building all three axes straight from rating sets:** a larger change, kept for later; only S was rebuilt.
- **Keeping S as "connected vs alone", made perpendicular to mood:** no rating set can check labels for connectedness,
  so S became "about things vs about people" (checkable) and togetherness became a separately learned number (B9).
- **Trust changing how much a brain learns from someone:** a brain could learn to distrust the one person who could help
  it; v1 only measures. Any future version that lets trust change listening is meant for a separate, backed-up copy,
  with a floor on listening.
- **Fading that depends on how the brain feels about the person:** it would feed trust back into its own memory and is
  left for a later version, to be compared against this baseline.
- **Starting togetherness from S or from a rating set:** that would mix "about people" back into "with people".
- **Counting the voice's own reply words as "together":** only the person's message counts; the voice wrote the reply.
- **Sleep counting as "alone":** sleep counts as neither; only awake time alone does.

## References

- Diveica, V., Pexman, P. M., & Binney, R. J. (2023). Quantifying social semantics: An inclusive definition of
  socialness and ratings for 8,388 English words. *Behavior Research Methods*, 55, 461-473.
- Jøsang, A., & Ismail, R. (2002). The beta reputation system. *Proceedings of the 15th Bled Electronic Commerce
  Conference*.
- Mayer, R. C., Davis, J. H., & Schoorman, F. D. (1995). An integrative model of organizational trust. *Academy of
  Management Review*, 20(3), 709-734.
- Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words.
  *Proceedings of ACL 2018* (NRC VAD lexicon).
- Warriner, A. B., Kuperman, V., & Brysbaert, M. (2013). Norms of valence, arousal, and dominance for 13,915 English
  lemmas. *Behavior Research Methods*, 45, 1191-1207.
