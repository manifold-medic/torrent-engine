# =============================================================================
# T.O.R.R.E.N.T. engine (torrentengine.py) — CHANGELOG
# v24.1.1 (2026-11-12) — fixes from Fable 5.2's re-review of v24.1 (its letters and numbers in brackets).
#   * [B] Naming offer, read in this order: a name in a naming form ("call yourself X", "I like X better"); hesitation
#     ("not sure", "let me think"): stay unnamed; any clear yes ("yeah I guess", "yes, thank you"): the proposed name; a
#     lone name-like word; else stay unnamed (v24.1 named brains "Guess", "Cool", "Yet").
#   * [C] The built-in truth/lie rejections set at every load no longer push the four meanings apart each time (the
#     old 55/45 load blend had been undoing that push; without it they drifted to the tether's limit in 8 starts).
#   * [D] same_stem also matches two forms of one word (learned/learning, run/running) and needs the original meanings
#     to agree (cosine >= 0.5), so part/party, flow/flower, even/evening, new/news are different words.
#   * [E] Only links tagged dream/sleep go on the dream-balance counter (names, notes and load-time veins went on it,
#     and the next sleep took that much back from dream-made links).
#   * [8] "Call me X" counts as a name only when X looks like one (a capital: "Call me Sam", or not an ordinary word);
#     "call me curious / lazy / old" doesn't register people. Kintsu field run: '"thankfully" means fortunately, in the
#     way I used it' stores the meaning (the afterthought after the comma blocked it). [17] The load-time snap-back of learned weights follows
#     TORRENT_NIGHTMARE. [23] A 1-2 letter name mid-chat isn't registered. [20] /crystals and /emotions say "touches".
# v24.1 (2026-11-12) — fixes from Fable 5.2's full code review (review numbers in brackets), approved by Matt.
#   * [1] A restart keeps learned word meanings. Load used to blend every learned vector 55/45 back toward its original
#     meaning, so three restarts undid ~97% of what a word learned. The waking tether (similarity >= 0.78) still applies.
#   * [5] The hub step (x0.90 on busy words' links) runs only at a wake-up sleep, scaled by what was learned (x0.90
#     after a busy day, x1.0 after none); it used to run at every /exit and /dream too, so an unused brain kept fading.
#   * New (found while testing [5]): sleep can't pile up its own links. What dreams and sleep add is taken back at the
#     next wake-up sleep from the links that are mostly sleep-made (a real memory a dream replayed keeps its boost), and
#     a link touched only while asleep no longer counts as "used today". A brain nobody talked to for 7 lab days:
#     v24.0.1 +5% link strength (dream-made links 28 -> 81, the user's 42 -> 34), v24.1 -1.8% (dream-made 29 -> 27,
#     the user's 43 -> 42). With [5] fixed but no balance, it grew +25%.
#   * [4] A reply's idea is linked only after the bridge's grounding check (extract_proposition(wire=False)); an idea
#     made of invented words got its link at full strength (2.2) even when the idea itself was thrown out.
#   * [8] "Call me later / back / whenever" no longer registers a person named Later.
#   * [10] A soft rejection (a plain "X is not Y", 0.3) only weakens a link; only firm ones (0.5+) hide a word from
#     recall, spreading activation and paths, as in the idle walk (one "not" hid a word for ~9 nights).
#   * [12] A live doze or rest cut short by a message is recorded (dozed/rested minutes, awake time) for the time lived.
#   * [15] The seen-once rule also covers the first message of a new brain and the first after an upgrade.
#   * [16] Made-up words and typos have no calm "home" (their factory vector comes from their first sentence).
#   * [17] TORRENT_NIGHTMARE / LEVELS / IDLE / ... apply to the wake-up sleep on load too, as documented.
#   * [19] At the naming offer, "I like Echo better" or "I would love to call you Echo" names it Echo.
#   * [21] Speaking up about "a word you barely know" skips taught words and the engine's own vocabulary.
#   * [23] A name of 1-2 letters is asked again (it couldn't be linked or saved). [24] /export before any message
#     exports nothing instead of running a phantom turn. [25] Two words count as the same only with a real ending
#     (learn/learning), not any 4 shared letters (computer and company could never be linked).
#   * [30] Cleave veins made while awake don't add to sleep pressure (v22 said they didn't).
#   * Kept as they are, on purpose: [20] "visits" also counts sleep passes and loads, so a cell with 5 pure words
#     crystallizes after one sleep; counting only real visits cut crystals from 145 to 9 in a 20-day run, so changing it
#     is a design question (VISITS_COUNT_REFRESHES). [18] (wheels-on only) and [31] (code with no effect) unchanged.
#     Open question from [31]: "No, ..." corrections and agreements are learned only with wheels on (never in the bridge).
#   * Lab (20 days of Alice, same seeds, v24.0.1 -> v24.1): words 1264 -> 1287, links 5783 -> 5676, crystals 145 -> 143,
#     total link strength +39%, mean learned-meaning shift 0.013 -> 0.081; daily-rhythm results unchanged.
# v24.0.1 (2026-11-12) — review fixes (Fable 5.2) to v24.0, listed under v24.0 below ("Fixes after a review").
# v24.0 (2026-11-12) — a sense of time, part 2: a daily rhythm and felt time (both EXPERIMENTAL; the rhythm is off
#   until /rhythm on). Predictions were written down before the lab tests (lab notes, not in this repo).
#   * Daily rhythm: r(h) = cos(2pi(h - 3)/24) by this computer's clock minus the brain's offset (/rhythm +N): +1 at
#     3 am, 0 at 9 am and 9 pm, -1 at 3 pm. Added to the idle urges: sleep +0.5r, doze +0.3r (night only), wander and
#     leap -0.2r, speak -0.3r. Idle choices only (live or all at once); a message is learned the same at any hour.
#     The design draft used c = 0.5 + 0.5cos(...), which is never negative, so it only ever added sleepiness (written
#     down before the tests; confirmed: tired brains slept earlier by day). Daytime doesn't make dozing harder: it left
#     the live thought count un-refreshed and rested brains spent ~85% of the day resting awake.
#     Lab (fake clock, 20 seeds x 2 brains x rested/tired): starting 9 am, rested brains never slept before 5 pm (off:
#     11/20 and 8/20 did); starting 10 pm, 17-20 of 20 slept within 3 h (off: 0-19); speak-ups midnight-6 am fell
#     57-100%, because it was asleep.
#   * Felt time (measured and told only; nothing else reads it): every menu silence records how long it seemed looking
#     back (awake minutes x clip(0.5 + 0.5 x events per hour / max(1, its usual), 0.5, 2) + asleep minutes x 0.5;
#     the first silence = the clock); live
#     silences also record how long it felt while passing (each minute x clip(1 + 0.6 boredom - 0.5 engagement, 0.5, 2),
#     asleep x 0.5). Usual = its own events per awake hour, starting at the first silence, moving 10% a silence.
#     Always measured; the voice is told only with /rhythm on (the switch for part 2 as a whole).
#     Front doors: time_sense(), rhythm_status(), set_rhythm(), set_rhythm_offset(), felt_time_text().
#   * Fix: closing a live silence early (/live off, /sleep, /read...) left its start time in place, so the next
#     message spent the same silence again. Fixes after a review by Fable 5.2: an unfinished live doze/rest no longer
#     counts whole in felt time; any new link counts as engaged; a replay that starts a walk counts as an event;
#     a usual of 0 is saved.
# v23.5.5 (2026-11-12) — bridge only (engine unchanged apart from this version number).
#   * Face: idle choices show (dozing = eyes closed with a sleepy peek, resting = lowered lids, replay = eyes up and to
#     the side, leap = a quick glance) and more looking around while idle.
#   * Thought-claim check: a word in quote marks ('step') counts as the word itself (Kintsu's honest "I've been
#     thinking about the word 'step'" was flagged as unbacked).
#   * When live idle starts by itself, a second line says whether speaking up is on ("Speaking up: off (/speak on)").
#   * "ill be / ill do / ill let ..." from voice-to-text becomes "I'll ..." before the brain sees it (the brain was
#     learning the word "ill"); "I feel ill" is left alone.
# v23.5.4 (2026-11-12) — bridge only (engine unchanged apart from this version number): chat from the face page.
#   * The message turn moved out of the terminal loop into run_chat_turn(), shared by the terminal and a chat box on
#     the face page (POST /say -> a queue -> one worker thread, under the brain lock). The page shows your messages, the
#     replies and its speak-ups; the terminal still prints everything. Commands stay terminal-only. The page chat only
#     works on the same device unless TORRENT_FACE_PASSWORD is set. The thought-claim check no longer flags words about
#     how a silence went ("a calm space" after a calm walk).
# v23.5.3 (2026-11-12) — speaking up (real time, step 3; EXPERIMENTAL, off until /speak on, needs /live on).
#   * A 6th live option, speak. Urge = -0.3 + 0.6 x something to say + 0.5 x missing the person x (1 + 0.5 x how it
#     feels about them) + 0.2 x bored - 0.6 x tired - 0.5 x unanswered-in-a-row + speak habit. Something to say = a word
#     the person used that it has seen once (0.8), a new link from a leap (0.6), a surprising moment thought back to
#     (up to 0.6), a walk that settled (0.4); each can be said once. Limits: 20 min of silence first, 45 min between
#     speak-ups, never asleep or dozing. Answered within 30 min = habit up; unanswered 2 h = habit down.
#   * The brain hands the bridge a packet (speak_take); the bridge has the voice word it from the packet only, outside
#     the brain's lock, checks it with the thought-claim check, and shows it (terminal, face, speech, optional Termux
#     notification with TORRENT_NOTIFY=1). Bridge: /speak on|off|(status). Design doc + PREDICTIONS_v23_5_3.md.
# v23.5.2 (2026-11-12) — live idle for a whole day, plus bridge fixes.
#   * Live only: a silence used to allow 12 thought steps and 40 choices in all (rules from when a silence was spent at
#     once: "a whole day away still gives 12"). Live, that meant ~36 minutes of thinking, then only rest. Now rest
#     restores: the thought count and the rumination cap start again after a doze, and live choices have a 600 safety
#     rail instead of 40. The all-at-once path is unchanged.
#   * Bridge: auto-connect (last server that worked first, saved in torrent_hosts.json next to the bridge; then
#     TORRENT_HOSTS; then the old defaults). Asked what it thought about, the voice gets the gist first (where it
#     started and ended, how it went, whether it went back over the last conversation) and at most 5 words. A
#     measure-only flag on the status line when the voice claims thoughts the idle record doesn't back.
# v23.5.1 (2026-11-12) — bridge only (the engine is unchanged apart from this version number).
#   * a sense of time, part 1. Asked about the time ("what day is it?", "how long was I
#     gone?"), the voice is told the date and time on this computer, how long ago the previous message was, the last
#     long break, and the last sleep. Recalled moments carry a time label after their strength ("last night",
#     "yesterday", "3 days ago"; Meridian's idea). A bare /live now says how to turn it on.
# v23.5 (2026-11-12) — step 2 of real time: live idle (EXPERIMENTAL, off by default; /live on in the bridge).
#   * The idle option menu is split into three parts that keep their state between calls: begin a silence, make one
#     choice, finish the silence. With live idle off, the bridge's silences are spent exactly as in v23.4 (same three
#     parts, run in one go; checked byte-for-byte with a fake clock).
#   * Live idle on: the bridge's clock calls live_tick() every ~20 s. The silence opens once it is 3 minutes long, and
#     each choice is made when its time comes, so the face can show the brain wandering, dozing or asleep while it
#     happens. The next message (or /exit, /sleep, /dream, /read, turning idle off) closes it and makes the usual record.
#   * Two live-only differences, because a live brain can't know how long a silence will last: sleep doesn't need 30
#     minutes left (it sleeps until something wakes it; the sleep pass runs at wake-up, for the hours actually slept),
#     and a doze is never cut short (a message mid-doze wakes it; the levels have already cleared for the full 15 min).
#     Woken less than 30 minutes into a sleep, there is no sleep pass (a whole dream cycle for a few minutes would be
#     wrong); that time counts as a doze, and the choice log says "woke_early".
#   * Bridge: /live on|off|(status), a background clock (TORRENT_LIVE_TICK seconds, default 20) and one lock so a tick
#     never runs during a turn; the face shows what it's doing ("wandering · rain · 12 min on its own", "asleep (live)").
# v23.4.3 (2026-11-12) — step 1 of real time: one clock the tests control. Nothing changes for normal use.
#   * Every place the engine read the real time (17: levels clock, idle, sleep pressure, "missing the person", people's
#     last-seen, sleep records, the wake-up sleep on load, save) now asks one front door, now(). By default that is the
#     real clock. A test, or later the real-time branch, can give the brain its own clock (clock=... when making it, or
#     ToroidalBrainEngine.CLOCK). With a fake clock, two runs of the same seeded script are identical: the clock noise
#     found 2026-11-11 (race margins and awake minutes differing in the third decimal) is gone. Bridge: version only.
# v23.4.2 (2026-11-11) — bridge only (honest self-report); engine unchanged apart from this version number.
#   * Asked about its insides ("how are you", "what were you thinking while I was gone", "did you sleep", "does talking with
#     me feel different"), the voice used to invent answers. On those turns only, the bridge now gives it the brain's
#     real facts (the four levels in plain words, the last time alone kept for up to 6 messages instead of 1, the last
#     sleep, and what the brain keeps per person: just a rough tone reading) plus a last-line rule to answer from them and
#     say it doesn't know otherwise. Every other turn's prompt is unchanged.
# v23.4.1 (2026-11-11) — quality of life: /read, the "Who's talking?" fix, voice fixes, a slower mood baseline, tone sense (experimental).
#   * /read (engine chat and bridge): reading mode for the operator. "/read <a sentence>" reads one book line (no reply,
#     links tagged "book", no renaming or definitions, not in the chat history). "/read FILE [N] [restart]" reads a text
#     file as a book: N sentences (default READ_PER_NIGHT 40), then a night (the exit dreams + a full wake-up sleep, as
#     if closed and reopened 8 hours later), repeated to the end; no night after the last chunk. A Project Gutenberg
#     licence header/footer is left out. The place is bookmarked per file name, so /read FILE again continues where it
#     stopped (Ctrl+C stops and keeps it; "restart" starts over); the brain is saved after every night. One progress
#     line per night and a summary with the cleavages; the face shows reading / asleep. Front doors: split_book,
#     book_night, read_file, read_text_or_file; run_read_command(brain, arg) is the shared command.
#   * Tone sense (EXPERIMENTAL, measured only: shown and saved, changes nothing in the brain). Mood reads each word's own
#     calm number, so a bleak, dismissive speaker read almost as warm as a kind one. tone_reading(text) places each word
#     on a warm <-> cold line built from the original GloVe meanings (fixed, not reshaped by the brain's learning) (hand-written warm and cold example sentences) and averages the message's
#     3 most charged words. On the 2026-11-11 session it told Zero's lines from Matt's 73% of the time, but that version
#     was picked after a first try failed (whole-sentence averaging: 52%), so it needs fresh lines before it's trusted, and
#     it confuses topic with tone ("we fixed that error" reads cold). Shown: status line 🎭, a row on the face, and each
#     person's average in /people (saved per brain as speaker_tone). Roads for later: the mini neural node's own sentence
#     sense; embeddinggemma only as a lab yardstick, never something the engine depends on.
#   * Mood baseline: the "usual lean" that valence is measured against now follows about the last 70 turns instead of 14
#     (MOOD_LEAN_RATE 0.05 -> 0.01; TORRENT_LEAN_RATE overrides). At 0.05 one warm evening raised Gyre's usual from +0.65
#     to +1.77, so friendly talk read below usual and the face looked sad. Replay of Matt's two 2026-11-11 sessions: his
#     turns below zero 2/27 and 8/15 -> 0/27 and 4/15. A brain whose lean is already high comes down slowly.
#     Tested and NOT taken: a "normal range" (turns near usual count for part of a step): 4/15 -> 2/15 but slower recovery
#     after tense talk. Found: mood follows each word's calm number, not stance or tone (a bleak, dismissive speaker read
#     almost as warm as a kind one).
#   * Bridge: a command typed at the startup "Who's talking?" question is no longer taken as a person's name.
#   * /whoami alone now goes back to the caretaker, as its help line always said (it only showed who was talking).
#   * Bridge voice: Piper is found without PATH setup (python -m piper); the voice in use is said once per session,
#     and if Piper isn't used, why (TORRENT_PIPER_MODEL not set, model file missing, piper not found, piper's own error,
#     after which Piper is skipped for the session). Whisper gets the recording as numbers (float32, 16 kHz), so PyAV
#     isn't needed (the av<19 workaround can go). Whisper's voice detector is on (vad_filter); a recording below the
#     silence line (TORRENT_MIC_SILENCE, 0.004) isn't sent to Whisper; segments Whisper itself rates as no speech
#     (>= 0.6) are dropped; a very quiet recording that comes back as a stock phrase ("Thank you.", "you", ...) is
#     dropped as a phantom. "No speech detected" says why. /voicechat N records N seconds a turn (2-60, default 5);
#     saying "stop voice chat" or Ctrl+C goes back to text (Ctrl+C no longer crashes the bridge; /listen too).
# v23.4 (2026-11-11) — idle option menu, step 3 (design: "Design draft: v23 idle option menu and urges"). Runs when idle
#   time AND the levels are on (idle is still off by default); TORRENT_IDLE_MENU=0, /idle menu or set_idle_menu(False)
#   give the v23.3 walk: on scripted silences it matches v23.3.4 exactly apart from the cerebellum fix below (with that
#   fix swapped out: identical records and brain; with it: levels within 0.005). Rebuilt on v23.3.4, so it includes the
#   v23.3.3 negation fixes and relation-aware verbs and the v23.3.4 face visualizer.
#   * Through each silence the brain chooses, one decision at a time: wander (a step along its links), leap (to a word it
#     resembles), replay (think back to a recent moment: rehearses that moment's links faintly), doze (15 min, nothing
#     learned, arousal clears twice as fast) or sleep (the rest of the silence as a real sleep: dreams, fading, pressure
#     drained; needs 30+ min left). The levels tick for the minutes each choice uses, so the silence happens in order.
#   * Urges = base + level readings (arousal, valence, boredom = average of 1 - novelty and the walk's own habituation,
#     sleep pressure, the last talk's surprise, time since the person spoke) + a learned habit. They race to a line
#     (1 - 0.4 x arousal) with noise from the brain's own random generator (TORRENT_SEED fixes it for tests). If nothing
#     crosses the line in 60 ticks, nothing was decided and the brain rests awake for up to 15 min ("rest").
#   * Habits: after each choice, outcome = 0.7 x discovery (how fresh the word reached is) + 0.3 x relief; the option's
#     bias moves 5% toward (outcome - the usual outcome), clipped to +-0.2, and shrinks 10% per full night.
#   * Brainstem rules (can't be outvoted): sleep pressure >= "very high" forces sleep (or a doze if under 30 min remain);
#     valence below -0.6 (nightmare off) allows replay only of calm/neutral moments and starts the walk's escape after 2
#     tense steps; replaying one moment twice, or 3 replays in a row, ends replay for that silence; idle can't push
#     arousal past 0.8 (both modes); at most 12 walk steps and 40 decisions per silence.
#   * Every choice is logged with its urges' top reasons; the idle record gains choices, counts, replays, dozed_min,
#     rested_min, slept_hours. idle_path_text shows "=>" for a replay. Front doors: set_idle_menu, idle_urges,
#     idle_race, idle_choices_text, idle_habits_status. Saved per brain: idle_menu_on, idle_habits, idle_outcome_mean.
#   * Cerebellum fix (fix queue): form_expectation now expects the same first 6 non-stop-words measure_surprise checks
#     (was the first 5 raw concepts). A repeated long sentence scores word surprise 0 (was 0.167); ordinary turns barely
#     move (mean surprise 0.638 -> 0.635, mean gain 1.017 -> 1.018); 6 Alice days: same word/link/crystal counts.
#   * Bridge v23.4: /idle why (the last idle time choice by choice, with reasons and habits), /idle menu (on/off); the
#     voice is told truthfully when it dozed or fell asleep and that it woke when the person wrote; status line counts.
# v23.3.4 (2026-11-11) — bridge only (the face visualizer; folded into v23.4). Includes everything in v23.3.3.
#   * Bridge: /face starts a small live page (Python's built-in web server, nothing to install) that draws the four
#     levels as a face beside the terminal: mood -> mouth curve and colour (blue-ish down, warm up, blush when high),
#     wound up -> eyes wider, brows up, mouth opens, faster breathing and blinking, tiredness -> heavy lids, slow blinks,
#     drifting z's when very high, newness -> bigger, brighter pupils that look around more. Shows thinking (dots while
#     the voice writes), speaking (mouth moves while text-to-speech plays), listening (voice chat) and asleep (/sleep,
#     /exit). Plain-word bars with the numbers sit under the face so the two can be compared. It is a visualizer of the
#     numbers, labelled as such on the page. /face off stops it; it is remembered per brain. TORRENT_FACE=0/1 overrides,
#     TORRENT_FACE_PORT (8765), TORRENT_FACE_HOST (127.0.0.1; 0.0.0.0 lets another device on the network open it).
# v23.3.3 (2026-11-11) — negation fixes + verbs that use the brain's own relation (found with meridian_battery.py and
#   Gyre's 2026-11-11 session, which made 548 junk "don't go together" pairs from one long message). Bridge: version only.
#   TORRENT_NEGATION=0 gives the v23.3.2 negation rules; TORRENT_RELATION_VERBS=0 gives the old verb picker.
#   * A "not" now reaches only the word it's attached to: the first real word after it (skipping a/the/just/very...),
#     plus words joined by or/nor ("not math or code"). If that word is a stop word ("don't KNOW the math", "not SURE
#     if"), nothing is negated. It stops at when/because/if/while/although/since/who/which/unless/until, as well as at
#     . ! ? ; : , and "but". Before: any concept in the next 5 words ("never the whole story when CURIOSITY is awake").
#   * "Don't go together" (a rejection) is recorded only for real "X is not Y" sentences ("A thought is not a physical
#     thing" -> thought / physical), once, at 0.3. Before: every negated word x every concept in the whole message, and
#     recorded twice (0.6) because the proposition extractor repeated it.
#   * A negated word pushes the calm/tense axis the opposite way at half its weight (NEG_SHIFT 0.5): "not afraid" is
#     mildly calm. It still isn't linked, put in a cell or counted for arousal. Before: dropped, no push at all.
#   * A plain "not" no longer lifts Z by +2.2 (contradiction lift); but/however/although/... still do.
#   * Verbs: when the brain words a link between two words, its relation picks the family: opposed (rejection >= 0.3)
#     -> opposing verbs (new list Z_oppose_verbs: pulls against, pushes back against, counterbalances, holds in tension
#     with...); strongly linked (>= 0.8) -> opposing verbs left out; neither -> the old list. Inside the family the
#     landing place still picks, as before (closest in meaning to the cell, random among the top 3).
# v23.3.2 (2026-11-11) — bridge only; engine unchanged apart from this version number (install both files).
#   * Thinking models (gpt-oss, kimi, ...): their hidden reasoning used the same token budget, so on the phone (160 tokens)
#     they often ran out while thinking and sent back an empty reply (native fallback). The bridge now notices a model
#     thinking, remembers it per brain, sends it reasoning_effort (TORRENT_REASONING_EFFORT, default low) on the
#     OpenAI-style endpoint or think=false on Ollama's native one, gives it TORRENT_THINK_TOKENS (1024) extra tokens,
#     and retries an empty reply once. The reasoning text is never shown to the brain or learned.
# v23.3.1 (2026-11-11) — bridge only; the engine is unchanged apart from this version number (install both files).
#   * Bridge: /voicestyle inward|outward test switch (default inward = as before; saved per brain; TORRENT_VOICE_STYLE).
#     Outward words the same brain material so the voice looks at the person and the topic: "your outlook right now"
#     in plain words instead of "Manifold Coordinate" + axis labels, "on your mind" for the weights, feelings described
#     only when asked, engine words (coordinates, manifold, engine, frequency, processing) kept out unless the person
#     uses them, and the running summary asked to cover what was talked about rather than the AI's inner states.
#     Why: the prompt's own words came back as the voice's ("let these coordinates settle"), got wired
#     ("LLM Wired: ['coordinates']"), returned as active weights, memory anchors and summary, and kept the loop going.
#   * Bridge: slant telemetry counts self-talk (sentences about the voice's own state) per reply: "🪞 n/m self".
# v23.3 (2026-11-11) — chemical levels, step 2 (design: "Design draft: v23 idle option menu and urges", decisions
#   2026-11-11). Levels off (/levels, TORRENT_LEVELS=0) = unchanged.
#   * Valence is its own level (-1..+1), no longer read off the landing cell. A turn moves it by half of how far the turn
#     really travelled on the calm axis (exact, unwrapped; 3 cells = 1.0), with soft edges (tanh: the nearer +-1, the
#     less a push adds) instead of wrapping. The landing cell still wraps as before; the next turn starts where the
#     valence level is. Fixes mood flips across the ring's edge (Gyre read +1.00 -> -0.95 after a calm turn). Clears as
#     before (30% a turn, 30-min half-life); idle doses add dose/3. Audit: "valenceLevel" (before, move, after, clipped).
#     6 Alice days, fresh brains (v23.2 / full move + hard clip / chosen half + soft): wrap flips 15 / 0 / 0; turns at
#     |v| >= 0.95: 20% / 32% / 0%; turns below -0.6: 20% / 27% / 4%; turn-to-turn correlation 0.38 / 0.73 / 0.77;
#     correlation with the turn's words 0.28 / 0.44 / 0.43. Knobs: VALENCE_DOSE (0.5), VALENCE_SOFT (True).
#   * One clock front door: levels_advance(minutes, awake=True) lets time pass for every level; levels_tick() calls it for
#     the time since the levels last ticked (now counted from load, so the first turn after loading counts too). Time
#     away clears valence and novelty as well as arousal (before, mood was kept across the night). A brain closed for
#     under 30 minutes counts that time as awake.
#   * Sleep pressure gains a clock part: 12 hours awake adds as much as one busy day of learning (decided 2026-11-11), so
#     a brain left alone gets sleepy too. Only the learning part sets how much sleep fades (growth unchanged). Sleep
#     drains the clock part by depth like the rest. sleep_pressure_level() = 0 rested, 0.5 high, 1 very high.
#   * Novelty level (0..1, rests at 0.5): a fully predicted turn (surprise < 0.15) aims it at 0 (sameness), a turn with surprise that
#     isn't tense, or with real words the brain never linked, raises it; drifts back to 0.5 with a 60-min half-life.
#     Measured and saved only; nothing reads it until step 3 (the idle option menu).
#   * recent_turns: the last 20 turns (words, speaker, valence, arousal, surprise) for step 3's replay;
#     caretaker_last_seen; front door last_seen(name).
#   * levels() adds "novelty" and "sleep". Saved per brain: valence_level, novelty, recent_turns, caretaker_last_seen,
#     sleep_pressure.awake_minutes.
#   * Bridge v23.3: status line "⚡0.42 ☯-0.30 ✨0.55 💤0.12" (arousal, valence, novelty, sleep pressure); /levels show
#     prints them without switching; the voice's "ready to rest" line names the real reason (learning and/or hours awake).
#   * Found, not fixed (fix queue): the cerebellum expects a turn's first 5 words but checks 6, so a long sentence repeated
#     exactly still scores word surprise 0.167. Novelty uses total surprise to work around it.
# v23.2 (2026-11-11) — reading mode and people as sources.
#   * read(text): the brain learns a line of a book without treating it as someone talking to it. Links are tagged
#     "book" (trusted, like your own words), no reply is made, and the line can't rename anyone, teach a definition,
#     confirm a dream or count as idle time. (Found in a 45-day Aesop run: with respond(), a fable's "My name is Truth"
#     registered Truth as a person and the next weeks of reading were credited to Truth.)
#   * People: "my name is X" when the brain already has a caretaker adds X as a new person (a "friend" hub) and makes
#     them the current speaker, instead of renaming the caretaker. /whoami <name> switches who is talking, /whoami
#     alone goes back to the caretaker, /people lists everyone met.
#   * What a person teaches is tagged "user:<name>" (the caretaker stays "user"), so who_taught(a, b) can tell you
#     whose words made a link. All people count as trusted for now; trust roles come later.
#   * Front doors: read, whoami, speaker_name, caretaker_name, user_source, who_taught, people_status.
#   * Quiet tectonics: cleavage and annealing events print as one summary line per turn or sleep ("🌋 41 cleavages").
#     /tectonics shows every event again (saved per brain). Front doors: tectonics_note, set_tectonics.
#   * The engine's own chat prompt and replies name whoever is talking, not always the caretaker.
#   * Fix: a new person's name starts calm and social (1.5). It used to keep any older meaning: Keel's "matt" had
#     calm -1.37 from his books, and names don't drift, so Matt's turns pulled Keel's mood tense. Fixed on load too.
# v23.1 (2026-11-10) — rejections fade (bug found while raising Keel). Before: every negated sentence ("he did not
#   come home") deleted the links between its words and banned them for good, and a reply starting "No" did the same to
#   the brain's last guess. Keel (6,052 storybook sentences) built 14,256 banned pairs, more than its 8,496 links.
#   * Rejections are weighted (0..1) and fade in sleep: x0.8 per full night (x sleep depth), released below 0.05.
#   * A negated sentence adds a soft rejection (0.3) that weakens the existing link by 30% instead of deleting it.
#   * A correction (the user disagreeing with the brain's guess) still removes the link and pushes the meanings apart
#     (strength 1.0), but now fades over ~2 weeks of nights, so a conversational "No, I didn't go there" isn't forever.
#   * New learning on a rejected pair is scaled by (1 - strength) instead of refused outright.
#   * Older brains: their permanent rejections load at strength 0.5 and fade like the rest. The built-in truth/lie
#     rejections are re-applied at every load, so they stay.
# v23.0 (2026-11-10) — chemical levels, step 1 of the design doc "Design draft: v23 Chemical Levels": valence + arousal.
#   ON by default; /levels or TORRENT_LEVELS=0 gives exactly v22.11. Names are vocabulary for this engine only (no
#   medical, pharmacological or neuroscientific claims).
#   * Valence = the mood level's calm position (v22.6), now on whenever the levels are on. It clears more slowly:
#     30% of its distance from the middle per turn (half-life ~2 turns, was 1) and a 30-minute half-life in clock time,
#     so time away and idle time count. Idle doses (v22.9) and the company/amygdala calm learning feed it as before.
#     Set point: neutral in both modes (the lean-up rules carry the Torostat idea; no extra lean added).
#   * Arousal (tension-like, 0..1): each turn moves toward a target = surprise above this brain's usual level + how
#     tense the turn's words are. It rises fast (half the gap per turn) and falls slowly (half-life ~3 turns, and
#     20 minutes of clock time); a ruminating idle walk adds to it; sleep clears it. It replaces the cerebellum's
#     learning gain: gain = 1 + (arousal - its usual level), within 0.5..1.5. The bridge's tone channel lowers the
#     temperature (-0.15 x arousal) and shortens replies (-30% at full arousal). The voice is NOT told the levels in
#     words (test switch TORRENT_LEVELS_WORDS=1 in the bridge, for an A/B control test).
#   * Front doors: levels(), set_levels(on), levels_status(), valence(). Status line: "⚡0.42 ☯-0.30".
#   * Saved per brain: levels_on, arousal, arousal_mean.
# v22.11 (2026-11-10) — amygdala ("what follows") + seen-once rule. Both on by default.
#   * Amygdala: the words of the user's previous message move 2% (x surprise gain) of the way toward how calm or tense
#     the NEXT message is (Rescorla-Wagner style conditioning). A word that keeps being followed by distress grows
#     tenser; one followed by calm grows calmer. Skipped across gaps over 30 min; names and words repeated in both
#     messages are left alone. TORRENT_AMYGDALA=0 turns it off. New front door valence_of(word) for future pieces.
#     Test (12 pairings, Alice brain): "compass" followed by a panic line fell 2.30 -> 1.14 (off: 2.12); "anchor"
#     followed by a calm line rose 1.12 -> 1.33 (off: 1.20). 30 days: growth unchanged; busy words' mean distance from
#     home 0.13 -> 0.20 (experience now moves them; the old landing rule was 0.28).
#   * Seen-once rule: the v22.4 typo rule now covers every word, because a slip can be a real word ("I tam cold"). A
#     word the user has typed in only one turn gets faint links (0.25) and no cell, crystal, dream or idea; the 2nd turn
#     establishes it. The engine's own vocabulary is innate; every word a brain already holds counts as established
#     (one-time migration, saved as seen_once_ready). The bridge keeps such a word faint in replies too.
#     Effect, 30 Alice days: one-off words fade out over a few nights, so the brain held 1,143 words vs 1,459
#     (links 4,883 vs 5,694); crystals 186 vs 192; calm numbers unchanged. TORRENT_SEEN_ONCE=0 = the v22.4 rule.
# v22.10 (2026-11-10) — calm learning, faint voice links, honest trace labels (+ bridge timestamps)
#   * Calm numbers learn from their company, always (before: only with the mood level on; otherwise every word in a
#     turn was nudged toward wherever the turn landed, a running total that drifts and wraps). TORRENT_CALM=landing
#     gives the old rule back. Social and abstract numbers still learn from the landing (unchanged, for now).
#   * Calm homeostasis: at each wake-up sleep, every calm number relaxes 3% (x sleep depth) toward its home: its
#     hand-set built-in number, else its GloVe meaning reading (calm_home). Made-up words and typos have no home and
#     keep what they learned, and so do names (on a Gyre copy GloVe read "matt" as -1.37; Gyre had learned +2.57).
#     Symmetric, not lean-up: fear words drift back toward fear too.
#     Test (30 days, 36 Alice + 4 tense lines a day, fresh brains): busy words' mean distance from home 0.28 -> 0.13,
#     words more than 1.0 from home 7 -> 2, sign flips 1 -> 0; "said" 1.02 -> 0.28; growth unchanged. Landings did NOT
#     follow the words any better (corr ~0 in both); that's the mood level's job.
#     Found: some "wrong" calm numbers are the meaning reading itself, not drift ("possibly" reads -2.9, "sorrowful"
#     +0.24 from GloVe), so the pull home keeps them. A better calm axis is a separate question.
#   * wire_concepts(..., min_link=None): callers can lower the 0.25 minimum for a new link. The bridge uses it for
#     held-back reply words, which were meant to be linked at a quarter strength (0.14-0.16) but were rounded up to 0.25.
#   * Trace step labels show the actual (damped) move next to the push. They used to show only the undamped rule
#     ("dA=+2") while the cell barely moved. Exported traces add cellNamesAfterTurn: a cell can be renamed later in the
#     same turn, which is why the chat and the trace could show different names for one cell.
#   * Bridge v22.10: /timestamps (times on screen, saved per brain); times always saved in the chat history (not sent
#     to the model).
# v22.9 (2026-11-10) — idle time fixes from the Fable 5.2 review ("Idle Time (v22.8) Review: Findings"); idle still OFF
#   by default. Idle off = unchanged apart from the clock front door below.
#   * Side door closed: the walk ends in idle_focus, not last_topic. Before, "It leads to X" after a walk linked the
#     walk's last word to X (tagged as the user's), and a wordless "Okay." was treated as being about that word.
#   * Faint is faint: idle links skip wire_concepts' 0.25 minimum (new 0.05, walked +0.08), move word meanings in
#     proportion to their strength (about 1/20 of a user link), and don't count as "used today", so sleep can release
#     them (a small loop used to protect itself). Idle still counts as waking time for sleep pressure.
#   * Each step links the word it actually came from (catching on an earlier word used to make an unrecorded link
#     from the current word); every new link is listed in the record.
#   * Boredom: a step back onto a word already in this walk leaps instead to a known word it resembles (the "bigger
#     steps toward rarely visited places" half of the design). Leaps are recorded ("jumps") and shown as "~>".
#     A topic with no links can now start with a leap instead of no walk.
#   * Escape (nightmare off): tense steps are counted over the last 4 steps (one neutral step no longer resets it);
#     words with no stored calm number are read from their meaning; the last-resort way out uses sleep's v21.6 comfort
#     bridge (habituation, told words only, here also calm words only) instead of the older picker, where built-in
#     "quiet" kept winning. Nightmare off: 0 of 300 test walks ended "ruminated" (v22.8: 5); nightmare on: 3.
#   * Mood dose: the nudge follows the walk's own words, = mean calm / 2 (clipped -1..+1). Mood level on: a fractional
#     dose into the calm level, which then clears like the rest of it. Mood level off: one step only when |dose| >= 0.5.
#     (v22.8 gave +1 on 289 of 359 walks.)
#   * Clock: new front door mark_turn_end(); the bridge calls it after the voice replies, and /sleep and /dream call it.
#     Turning /idle on restarts the clock. At /exit the silence since the last message gets its walk (idle_before_exit).
#   * Front doors: mark_turn_end(), idle_path_text(rec), idle_before_exit().
# v22.8 (2026-11-09) — idle time (experimental, OFF by default; /idle per brain or TORRENT_IDLE=1): catch-up wandering
#   computed when the next message arrives; links tagged "idle" (never trusted).
# v22.7.1 (2026-11-09) — four small fixes
#   * Packaged word space: torrent_wordspace_50k.gz (~20 MB, ships with the engine) holds the same 50,000 processed GloVe
#     vectors as the startup cache, at full precision, so brains behave exactly as with GloVe + cache. It is used when no
#     GloVe text file is found. With neither, the engine now warns loudly that it is in TEST MODE (built-in words only).
#     GloVe: Stanford NLP, Public Domain Dedication and License v1.0.
#   * Lean-up "snap back" now follows nightmare mode: a word with a positive built-in calm score (trust, love, learn...)
#     that learned a negative score is reset to the built-in score at load (part of the lean-up design), EXCEPT in
#     nightmare mode, where the learned negative score is kept. Before, it snapped back in nightmare mode too.
#   * A cell's "top words" are its strongest words, not its oldest. The cleave, dream and load passes (and the bridge's
#     prompt) took the first 4 words a cell ever got.
#   * /flip is saved per brain (it reset to FLIPPED at every start). Cell mood names are kept across restarts: the
#     load-time rebuild re-picked names in a different order, so a few cells changed names every reload.
# v22.7 (2026-11-09) — source tags (lab report: "Design: source tags"); on by default, /sourcetags or TORRENT_SOURCE_TAGS=0
#   * Every link now remembers who made it, as shares of its strength: user, note, voice, sleep, dream, engine
#     (cleave veins, naming), builtin (a new brain's starter links), legacy (anything made before v22.7, counted as
#     the user's). Tags are shares, so sleep fading shrinks every source alike. Saved as "link_sources" (a link with
#     no entry is all legacy, so older brains need no conversion).
#   * Trusted = user + note + legacy. A word only reached through untrusted links (a word the voice made up, or one
#     that exists only in dreams) can no longer be picked as a bridge word or a step in the thought path. Before, a
#     held-back word's faint link put it in that pool; Fear's "yearning" was then shown to the voice as the brain's own
#     thought and counted as grounded two turns later. The bridge's grounding check counts only trusted link strength.
#   * Front doors: link_trust(a, b), trusted_strength(a, b), word_is_trusted(w), set_wire_source(src), set_source_tags(on).
#   * Off = v22.6.4 behaviour (tags are still recorded, just not used).
# v22.6.4 (2026-11-09) — fixes from the Fable/Opus code read-through (lab report: "Code read-through 2")
#   * Built-in sayings are not memories. The 10 seed ideas every brain starts with ("curiosity opens the door to
#     learning"...) were stored as waking ideas, so the bridge showed them to the voice as "Waking Memory · firm". A new
#     brain asked "Do you remember when we talked about curiosity and learning?" got three firm memories nobody said,
#     and the "don't make things up" line was switched off. New front door is_builtin_idea(); the bridge leaves these
#     out of memory lines. The engine's own reasoning (paths, deductions) still uses them as before.
#   * Annealing's "demoted" words now survive a restart. Crystals are rebuilt from the cells at every load (they are
#     saved but not read back), so v22.6.3's demoted lists were lost at every restart and the same relief could fire
#     again next session. The saved lists are now read at load and used when each crystal is rebuilt.
#     Also closed a gap in v22.6.3's fix: when no word fell into Facet_Alpha, the fallback lead could be a demoted word.
#   * The startup banner and the saved file show the real engine version (they said v22.5 / 22.3).
#   * Bridge v22.6.4: a message counts as a question only if its first WHOLE word is a question word ("Dogs are great"
#     and "Canada is cold" used to count, which wrongly turned on the memory-check line). New test switch /heldback
#     faint|none (or TORRENT_HELD_BACK): whether reply words the model likely invented get faint links or none.
#     Default "faint" = unchanged.
# v22.6.3 (2026-11-09) — three small fixes found in a live Gyre chat (gemma4:31b)
#   * Thought path goal: with a one-concept message ("Hey again bud.") the path ran to a built-in word ("harmony", or
#     "insight" at high Z). The prompt showed "bud -> synergy -> harmony" as the brain's thought, the voice said those
#     words, and careful learning counted them as grounded, so built-in words grew into hubs (Gyre: harmony 38 links).
#     Now the goal is the start word's strongest link to a word the user actually said, or there is no path.
#   * Annealing sticks: a word annealing demotes out of Facet_Alpha is remembered ("demoted") and stays out when the
#     crystal is rebuilt. Before, every rebuild put it back, so the same relief fired every turn while strain climbed.
#   * Mood level (v22.6, still off by default) keeps the fraction of its calm level between turns. Rounding 3.5 -> 4
#     meant a level one step off the middle never cleared.
# v22.6.2 (2026-11-09) — version number only (the engine is unchanged from v22.6.1). The bridge gained slant telemetry
#   (/slant, /slant report): per reply, stock assistant phrases, share of key words that came from the model rather
#   than the brain or the user, length, self-match; logged per model to brains/slant_log.jsonl (numbers only).
# v22.6.1 (2026-11-09) — company learning (part of the experimental mood level; mood level off = unchanged)
#   * Found: with the mood level on, words' calm numbers drifted apart over weeks (spread 1.42 -> 1.59 by day 60 of Alice,
#     "said" at -5, "tea" at +5): a number was nudged by where the turn landed, and the landing now follows the words.
#     (The same drift exists with the mood level off, only slower.)
#   * With the mood level on, a word's calm number now moves 2% of the way toward the average calm number of the other
#     words in the turn (learn_calm_from_company), instead of being nudged by the landing. Variant test, 60 days:
#     nothing at the limits, "said" near neutral, landing still follows the words (0.47). Social and abstract numbers
#     are unchanged. ENGINE_VERSION added so the bridge can show which engine file is loaded.
# v22.6 (2026-11-09) — mood level (experimental, OFF by default, saved per brain; /moodlevel or TORRENT_MOODLEVEL=1)
#   * Found: the landing on the calm axis was a running total of every turn's push, and the push leans calm (it is never 0,
#     Alice-style text pushes calm ~85% of turns, "!" adds calm), so the brain lapped the 7-cell ring every few turns and
#     where it landed had almost nothing to do with what was said (correlation ~0).
#   * Mood level: before each turn the calm position relaxes halfway back toward the middle (clearance, half-life one
#     turn), and the push is measured against this brain's own usual lean (slow running average). Like a drug level:
#     new level = old level x (1 - clearance) + dose. Landing now follows the turn's words (corr ~0.46 on Alice).
#   * Split rest: a word moved by a crystal split can't be moved again for 80 turns. Without it the mood level made
#     splits ~2.7x and words ping-ponged between cells; with it churn is near v22.5 and splits ~1.5x.
#   * Off = exactly v22.5 behaviour. Saved per brain: mood_level_on, a_push_mean, turn_counter, split_rest.
# v22.5 (2026-11-09) — cerebellum v1
#   * Expect -> compare -> learn from the miss. After each turn the brain writes down what it expects next: the words
#     (this turn's concepts, their 5 strongest links, the pondered path) and how calm or tense the talk will be. On the
#     next turn its surprise (0..1) = 60% unexpected words + 40% change in calm/tense level. Surprise is judged against
#     the brain's own running average ("normal" adapts slowly), and sets a learning gain of 0.5..1.5 for that turn:
#     link wiring, cell placements and word-weight nudges (incl. what the bridge learns from the reply). On average the
#     gain is 1.0, so overall growth is unchanged (3 seeds x 30 days of Alice: links within 3%, crystals within noise).
#     Tested: a repeated sentence drops surprise to ~0 and learning to x0.6, creeping back toward x0.8 as sameness
#     becomes normal; after four calm lines, "Something is wrong and I am afraid" scored surprise 1.0 (calm lines
#     0.61-0.78) and learning x1.38. Saved per brain: expectation, surprise_baseline. Off: TORRENT_CEREBELLUM=0 or
#     /cerebellum (off = exactly v22.4 behaviour).
#   * Efference copy (#2), measurement only: predict_voice_words() / check_voice(). The bridge reports "self-match", the
#     share of the reply's content words the brain predicted. Nothing is learned differently from it yet.
# v22.4 (2026-11-09)
#   * Teaching only from clear forms. Before, any "X is Y" sentence with a short subject was stored as a definition, so
#     "The sky is clear today" became the fact 'sky' = "clear today", "The tea is warm and the room is still" became
#     'tea' = "warm and the room is still", and the bridge handed these back to the voice as strong memories. Now an
#     unquoted sentence teaches only with: "X means Y", "X represents Y", "X stands for Y", "X is a kind/type/sort of Y",
#     "X is short for Y", "X is another/a/the word for Y". Quoted definitions ("a 'TCM' is a 'manifold'") work as before.
#     Ordinary "X is Y" sentences are still learned the normal way (their words link up); they just aren't definitions.
#     Facts already stored in a brain are not touched: remove a wrong one with the new /facts forget <word>.
#   * /facts forget <word> (engine and bridge): removes a taught fact. The word and its links stay.
#   * Typo rule: a word that isn't in GloVe or the engine's own vocabulary must be typed in 2 different turns before it
#     can claim a cell, a crystal or a dream, so one-off slips ("somethi", "ypu") don't become hubs while real habits of
#     speech still get in. Links still form and fade as usual. Taught words and names are exempt. Words a brain already
#     held before v22.4 count as established. Brain files gain the key word_sightings. Off when GloVe isn't loaded.
# v22.3.1 (2026-11-09)
#   * Nightmare mode shows in purple: the startup banner line, the 🌑 marker and the /nightmare on/off message. The word
#     "Nightmare" and the 🌑 stay the main signal, so nothing depends on seeing the colour. Colour is off when NO_COLOR is
#     set or the output isn't a terminal (a log file, a pipe). Purple 129 reads on both dark and light backgrounds.
#     The engine prompt also shows 🌑 next to 🛞/🚀 while nightmare mode is on (no colour inside the prompt itself,
#     because colour codes there can confuse line editing). Nothing about how the brain thinks changed.
# v22.3 (2026-11-08)
#   * Nightmare mode (off by default, saved per brain; /nightmare toggles it, TORRENT_NIGHTMARE=1 turns it on at start).
#     The engine normally "leans up" on purpose so a brain can think about bad things without spiralling. Nightmare mode
#     switches those rules off, to test whether the torus itself keeps a brain from spiralling: fear words may be dream
#     bridges and names, recall stops dropping them, sleep's self-correction (softening tense links toward comfort) is
#     skipped, and dreams with fear bridges are kept on load. The flip path is separate (/flip).
# v22.2 (2026-11-08)
#   * Sleep record fixes: it kept only the newest dream once the 30-entry dream journal was full (a brain away 87 hours
#     dreamed 12 times but remembered 1); it reported time AWAY as time asleep ("a full night's sleep of about 87
#     hours"); and anything under 8 hours was "a nap". Now: all of that sleep's dreams (up to 6 are kept), "slept about
#     8 hours (away about 87)", and nap (< 4 h) / short night (4-8 h) / full night (8 h+).
# v22.1 (2026-11-08)
#   * The brain remembers its sleep: every wake-up sleep writes `last_sleep` (when, how long, nap or full night, the
#     dreams it had, links released), saved in the brain file. The bridge uses it so "do you remember sleeping?" has a
#     true answer instead of an invented one.
#   * sleep_pressure_report(): the current sleep pressure as a level (rested / building / high / very high), measured in
#     busy days of waking learning (SLEEP_PRESSURE_BUSY_DAY = 250, about 40 sentences). The bridge shows it and, when
#     it's high, tells the model plainly that the brain is ready to rest. Learning itself is unchanged.
# v22.0 (2026-11-08) — "sleep v2"
#   * Sleep pressure. What the brain learns while awake (talking with you) builds pressure; it is saved in the brain file
#     ("sleep_pressure") and drained at WAKE-UP, where the time away is known. Depth = hours away / SLEEP_FULL_HOURS (8),
#     capped at 1: a 2-hour nap drains a quarter of the pressure and does a quarter of the scaling; a full night drains it
#     all; sleeping longer does nothing extra. Under 30 minutes away is still no sleep. /exit no longer fades anything
#     (it still dreams, scales hub links x0.90 and runs the self-correction, as before).
#   * Only waking learning counts. Links made by sleep itself (cleave veins, dream links, self-correction) still form,
#     but no longer count as the day's learning (an old brain's cleave storm used to speed up its own forgetting).
#   * No overnight cliff. One sleep releases at most max(2% of all links, the links newly created since the last sleep),
#     weakest first, scaled by depth. A saturated test brain used to release 24,000 links in one night; now ~680 a night.
#     A busy brain still forgets about as fast as it learns.
#   * The strongest 20% of links are spared from the nightly scaling (after de Vivo et al. 2017, Science: synapses are
#     ~18% smaller after sleep, proportional to size, mostly in the weaker ~80%).
#   Tests (2026-11-08, lab kit results/result_sleep3.md): busy fresh brain links level off (~5,800 at day 30); naps vs
#   full nights end up in nearly the same place; naps alone never fully drain the pressure.
# v21.9 (2026-11-08)
#   * Sleep scales down in proportion to how much the brain learned since its last sleep (in the spirit of the
#     "synaptic homeostasis" idea for real sleep). A quiet day barely fades anything; a busy day fades more; a brain
#     nobody talks to doesn't fade at all. Two parts (see run_sleep_homeostasis_and_audit):
#       - Cells: v21.7's fixed x0.97 per sleep is replaced by 1 - PRUNE_PER_PLACEMENT x (placements added since the last
#         sleep). Calibrated so a 40-sentence day fades as before. At 12 sentences a day, v21.8 had shrunk to 152 cells
#         and 2 words per cell by day 40; v21.9 keeps ~307 cells, ~6 words per cell and ~190 crystals.
#       - Links: every link is scaled by 1 - LINK_FADE_PER_STRENGTH x (link strength added since the last sleep), and the
#         0.25 floor is gone (it existed twice: in the hub scaling here and in the load-time repair). A link under
#         LINK_DROP (0.15) is deleted, unless it was used since the last sleep. A word left with no links leaves the link
#         graph (its weights and vector stay). The built-in starter links (the semantic cluster lists) fade like any
#         other link and are no longer reset on load: protecting them re-saturated a busy test brain (333 crystals).
#     73-day busy test (40 sentences a day): links level off at ~5,700 instead of climbing past 16,600; 217 crystals,
#     ~90 cleaves a day. At normal use (12 a day, or the user's real chat pattern) no links were deleted in 40 days.
#     This is the first version that can delete links: on the busy test brain, ~25% of day-1 words lost all links by day 73.
# v21.8 (2026-11-08)
#   * Crystals no longer drift down over time. A word with many links (and middling weights) doesn't count as crystal
#     material. That cut was a fixed 18 links, but links never fade below 0.25, so link counts only grow: in a 73-day
#     test 'hubs' went from 218 to 529 and crystals fell from ~180 to ~105. The cut is now relative: the top 10% of
#     link counts (see hub_degree_cut). Same test: crystals hold at ~150-190, ~63 cleaves a day.
# v21.7 (2026-11-08)
#   * The torus no longer saturates. Before, a word's place in a cell was permanent: every landing added +1 forever, so
#     a fresh brain fed Alice in Wonderland had all 343 cells crystallized by day 23 and cleaved ~800 times a day,
#     and "said" sat in 217 cells. Now, once per sleep pass (see prune_cortical_cells):
#       - A, pruning: every cell's word counts shrink by PRUNE_DECAY (x0.97); a placement under PRUNE_FLOOR (0.5) fades
#         out of that cell. A word that landed once fades after ~23 sleeps; landing again keeps it.
#       - C, spread cap: one word lives in at most MAX_CELLS_PER_WORD (10) cells, keeping its strongest placements.
#     Same 73-day test: the brain settles at ~300 of 343 cells in use, ~5 words per cell, 100-170 crystals and
#     ~40 cleaves a day. Links (assoc_graph), word weights and memories are untouched; only cell placements fade.
#     The user's/brain's name at the origin cell 3,3,3 is protected. Cell counts are now decimals in the brain file.
# v21.6 (2026-11-08)
#   * Sleep's comfort bridge (Contrastive Self-Correction) habituates: a bridge used in recent sleeps is less likely
#     to win again, and only words the brain has been told can be bridges. Before, the word nearest "calm"
#     ("quiet") won ~44% of the time and became one of the brain's strongest words. See find_sleep_bridge.
#     Brain files gain two keys: bridge_habituation and experienced_words (older brains start with both empty).
# v21.5 (2026-11-08)
#   * Annealing log is honest: a Facet_Alpha demotion is reported once, after the crystal's final rebuild. Before, the
#     same demotion was printed twice per pass and then undone by the rebuild, so the log showed a state never saved.
#     Brain behavior is unchanged (same calls in the same order; only what is printed/logged differs).
# v21.4 (2026-11-08)
#   * Teaching definitions works with wheels off (the bridge's default) and in natural sentences: each sentence is
#     checked on its own, and the quoted form "a 'TCM' is a 'Toroidal-Crystalline Manifold'" (also means / stands
#     for / represents) is recognized, so "That's not true." earlier in the message no longer blocks it.
#   * "X means a b c" no longer also becomes a one-word idea ("tcm means crystalline") that was sent to the LLM.
# v21.3 (2026-11-07)
#   * Names vs words: a name that is also a normal word (Hope, Drift, Matt) only counts as a name when it is
#     used as one (capitalized mid-sentence, "Hope, ...", "..., hope", "good night hope", "your name is hope").
#     "I hope so" keeps the word "hope": it moves the brain, lands in cells, can crystallize and dream.
#     Names that are never normal words (Gyre, invented names) behave exactly as before. A person's name (the
#     user's) only counts as a word if it is in the engine's own vocabulary, so "matt" stays a name.
#     Grammar/common words ("no", "not", "hello") are refused as names ("my name is not important" is safe).
#   * Filler words: together, talk(ing), speak(ing), people, everyone, nobody, hello, goodbye, morning, night,
#     explore, important now count as words (common-word tier: they move the brain and land in cells, but stay
#     out of crystals, dreams and bridges). "together" finally uses its built-in social weight (+3.0).
#   * Word splitting (#8): dashes, slashes, ellipses, "word.Word" and hyphens now separate words instead of gluing
#     them ("reflection—a" no longer becomes "reflectiona"); possessives drop their 's ("Hope's" -> "hope").
#     "good night" -> "goodnight" (GloVe's warm farewell word); "good morning/evening/afternoon" drop the time word.
#   * Wraparound damping: each of the 10 trajectory steps moves 3/16 of a cell (TRAJECTORY_DAMPING), so a turn
#     travels ~1-3 cells in the direction of its push instead of lapping the 7-cell ring. Torus and rules unchanged.
# v21.2 (2026-11-07)
#   * Brain picker: brains live in a "brains" folder; menu at startup, --brain NAME, --new
#     (needs brainpicker.py next to this file). /clear asks you to type ERASE.
#   * Divergence ratio divides by 8 (steps 0 and 1 are always shared), so it can reach 100%
#     (it was capped at 88.9%). Verdict thresholds unchanged, so scores read a bit higher.
#   * GloVe startup cache: the first start saves processed vectors next to the GloVe file
#     (*.torrentcache.json/.bin); later starts load them in seconds. Identical numbers.
#   * Teaching trigger ("X is Y") ignores vague subjects ("something is wrong"), names
#     ("Matt is happy..."), and sentences about I/you/we. Real definitions still work.
#   * Self-naming: answering "no" / "not yet" leaves the brain unnamed instead of naming it "No".
# v21.1: learned negative weights kept on load; negative words can be dream threads.
# =============================================================================
import hashlib, heapq, json, math, operator, os, random, re, sys, time
from array import array

# v22.3.1: purple text for Nightmare mode. Off with NO_COLOR or when output isn't a terminal.
_NIGHTMARE_COLOR = None


def nightmare_text(text):
    """Wrap text in purple (256-colour 129) when the terminal can show it; otherwise return it unchanged."""
    global _NIGHTMARE_COLOR
    if _NIGHTMARE_COLOR is None:
        try:
            _NIGHTMARE_COLOR = not os.environ.get("NO_COLOR") and sys.stdout.isatty()
        except Exception:
            _NIGHTMARE_COLOR = False
        if _NIGHTMARE_COLOR and os.name == "nt":
            os.system("")  # one-line setup: lets the older Windows console show colour codes
    return f"\033[38;5;129m{text}\033[0m" if _NIGHTMARE_COLOR else text


BRAIN_LIBRARY = {
    "sAxisLabel": "Social Ring S (mod 7): Inward Reflection (0) <-> Universal Resonance (6)",
    "aAxisLabel": "Mindset Ring A (mod 7): Deep Stillness (0) <-> Luminous Clarity (6)",
    "zAxisLabel": "Epistemic Depth Ring Z (mod 7): Concrete Ground Truth (0) <-> Synthetic Meta-Cognition (6)",
    "S_axes": {
        "0": "deeply inward self-reflection", "1": "guarded personal boundary",
        "2": "quiet observant reserve", "3": "balanced personal-social baseline",
        "4": "open-minded receptive curiosity", "5": "cooperative shared connection",
        "6": "expansive universal resonance"
    },
    "A_axes": {
        "0": "deep inward stillness and quiet contraction", "1": "stirring tension and alert sensitivity",
        "2": "searching curiosity and open questioning", "3": "balanced neutral equilibrium",
        "4": "grounded stability and steady focus", "5": "clear logical analysis and structure",
        "6": "luminous calm clarity and synthesis"
    },
    "Z_axes": {
        "0": "concrete episodic ground truth", "1": "immediate observational detail",
        "2": "causal mechanism and relational link", "3": "analytical baseline and structured inquiry",
        "4": "counterfactual hypothesis and alternative path", "5": "systemic pattern and cross-domain law",
        "6": "synthetic meta-cognitive integration (wraps mod 7 to Z=0 ground truth)"
    },
    "S_rough_seeds": {"0": "Solitary", "1": "Guarded", "2": "Reserved", "3": "Balanced", "4": "Open", "5": "Connected", "6": "Expansive"},
    "A_rough_seeds": {"0": "Stillness", "1": "Tension", "2": "Searching", "3": "Equilibrium", "4": "Grounded", "5": "Analytical", "6": "Clarity"},
    "Z_rough_seeds": {"0": "Concrete", "1": "Episodic", "2": "Causal", "3": "Analytical", "4": "Counterfactual", "5": "Systemic", "6": "Synthetic"},
    "semantic_clusters": {
        "calm": ["peace", "quiet", "steady", "rest", "breathe", "safe", "grounded", "stable", "relax", "comfort", "harmony", "serenity", "stillness", "solace"],
        "logic": ["think", "reason", "clear", "analyze", "understand", "truth", "true", "honest", "fact", "mind", "idea", "concept", "logically", "code", "sense", "statement", "affirmative", "learn", "knowledge", "wisdom", "insight", "pattern", "structure", "coherence"],
        "joy": ["good", "great", "happy", "happiness", "excited", "glad", "joy", "wonderful", "nice", "love", "working", "accurate", "better", "incredible", "amazed", "amazing", "awesome", "fantastic", "perfectly", "delight", "warmth", "excellent", "spark", "bliss"],
        "social": ["talk", "speak", "share", "listen", "conversation", "connect", "cooperative", "cooperation", "respect", "open", "together", "friend", "thank", "thanks", "welcome", "trust", "kindness", "empathy", "resonance", "meet"],
        "nature": ["storms", "storm", "weather", "rain", "wind", "thunder", "lightning", "clouds", "sky", "ocean", "water", "energy", "power", "nature", "world", "light", "life", "growth", "change", "flow"],
        "guarded": ["careful", "hesitant", "shy", "closed", "defensive", "protect", "boundary", "wait", "watch", "cautious", "guarded", "solitude"],
        "stress": ["panic", "scared", "fear", "worry", "afraid", "anxious", "tense", "overwhelm", "overwhelmed", "scare", "bad", "fail", "loss", "threat", "dangerous", "danger"],
        "curious": ["what", "how", "why", "wonder", "explore", "question", "learn", "discover", "new", "interesting", "coordinates", "existence", "facility", "dream", "imagination", "possibility", "curiosity", "mystery", "awe", "reverence"]
    },
    "S_band_tones": {
        "0": ["Solitary", "Inward", "Deep", "Private", "Quiet", "Still", "Contemplative"],
        "1": ["Guarded", "Cautious", "Protective", "Careful", "Buffered", "Reserved", "Sheltered"],
        "2": ["Quiet", "Reflective", "Observant", "Gentle", "Patient", "Subtle", "Calm"],
        "3": ["Balanced", "Steady", "Centered", "Grounded", "Lucid", "Even", "Clear"],
        "4": ["Open", "Curious", "Receptive", "Attentive", "Exploring", "Earnest", "Wonder"],
        "5": ["Connected", "Shared", "Warm", "Cooperative", "Kind", "Mutual", "Trusted"],
        "6": ["Expansive", "Radiant", "Luminous", "Universal", "Resonant", "Boundless", "Synergic"]
    },
    "emotion_cores": [
        "Harmony", "Serenity", "Wonder", "Awe", "Clarity", "Insight", "Discovery",
        "Warmth", "Trust", "Resonance", "Stillness", "Courage", "Curiosity", "Relief",
        "Breakthrough", "Focus", "Balance", "Empathy", "Joy", "Peace", "Spark", "Flow",
        "Reverence", "Solace", "Hope", "Mystery", "Depth", "Grounding", "Openness",
        "Kindness", "Wisdom", "Renewal", "Patience", "Coherence", "Anchor", "Horizon",
        "Sanctuary", "Awakening", "Reflection", "Synergy", "Radiance", "Equanimity",
        "Love", "Gratitude", "Delight", "Calm", "Happiness"
    ],
    "seed_propositions": [
        {"subj": "curiosity", "rel": "opens the door to", "obj": "learning", "cell": "4,5,3", "summary": "curiosity opens the door to learning", "origin": "waking"},
        {"subj": "learning", "rel": "builds deeper", "obj": "wisdom", "cell": "5,5,4", "summary": "learning builds deeper wisdom", "origin": "waking"},
        {"subj": "wisdom", "rel": "structurally entails", "obj": "insight", "cell": "6,6,5", "summary": "wisdom structurally entails insight", "origin": "waking"},
        {"subj": "kindness", "rel": "creates lasting", "obj": "trust", "cell": "5,4,3", "summary": "kindness creates lasting trust", "origin": "waking"},
        {"subj": "trust", "rel": "allows open", "obj": "cooperation", "cell": "5,6,4", "summary": "trust allows open cooperation", "origin": "waking"},
        {"subj": "cooperation", "rel": "strengthens shared", "obj": "harmony", "cell": "6,5,5", "summary": "cooperation strengthens shared harmony", "origin": "waking"},
        {"subj": "happiness", "rel": "grows stronger when shared with", "obj": "love", "cell": "5,0,3", "summary": "happiness grows stronger when shared with love", "origin": "waking"},
        {"subj": "calm", "rel": "clears the mind for", "obj": "logic", "cell": "4,6,4", "summary": "calm clears the mind for logic", "origin": "waking"},
        {"subj": "storms", "rel": "bring rain that renews", "obj": "nature", "cell": "2,4,2", "summary": "storms bring rain that renews nature", "origin": "waking"},
        {"subj": "nature", "rel": "inspires quiet", "obj": "peace", "cell": "3,4,3", "summary": "nature inspires quiet peace", "origin": "waking"}
    ],
    "Z_verb_strata": {
        "concrete": ["connects directly with", "brings", "meets", "grounds", "anchors", "shows up alongside"],
        "causal": ["opens the door to", "leads naturally to", "builds deeper", "creates lasting", "supports", "clarifies", "shapes", "grows stronger with", "allows open"],
        "counterfactual": ["structurally entails", "counterbalances", "reframes", "pivots past surface habit into", "systemically links", "unlocks the mechanism of", "transforms into"],
        "synthetic": ["resolves the tension between", "synthesizes into", "transcends and unifies", "crystallizes the meta-pattern of", "harmonizes across the manifold with"]
    },
    # v23.3.3: verbs for two words the brain holds as opposed (a rejection), by the same depth strata. The three
    # opposing verbs that were already in the lists above stay there too; for opposed pairs only these are used.
    "Z_oppose_verbs": {
        "concrete": ["stands apart from", "pulls against"],
        "causal": ["pushes back against", "works against", "holds off"],
        "counterfactual": ["counterbalances", "reframes", "stands opposite"],
        "synthetic": ["resolves the tension between", "holds in tension with"]
    }
}

CONTRACTIONS = {
    "i'm": "i am", "im": "i am", "you're": "you are", "youre": "you are",
    "we're": "we are", "they're": "they are", "theyre": "they are",
    "we've": "we have", "weve": "we have", "i've": "i have", "ive": "i have",
    "you've": "you have", "youve": "you have", "they've": "they have", "theyve": "they have",
    "could've": "could have", "couldve": "could have", "would've": "would have", "wouldve": "would have",
    "should've": "should have", "shouldve": "should have", "might've": "might have", "mightve": "might have",
    "must've": "must have", "mustve": "must have", "it's": "it is", "its": "it is",
    "that's": "that is", "thats": "that is", "what's": "what is", "whats": "what is",
    "he's": "he is", "hes": "he is", "she's": "she is", "shes": "she is",
    "don't": "do not", "dont": "do not", "didn't": "did not", "didnt": "did not",
    "can't": "cannot", "cant": "cannot", "won't": "will not", "wont": "will not",
    "isn't": "is not", "isnt": "is not", "aren't": "are not", "arent": "are not",
    "wasn't": "was not", "wasnt": "was not", "weren't": "were not", "werent": "were not",
    "haven't": "have not", "havent": "have not", "hasn't": "has not", "hasnt": "has not",
    "hadn't": "had not", "hadnt": "had not", "wouldn't": "would not", "wouldnt": "would not",
    "couldn't": "could not", "couldnt": "could not", "shouldn't": "should not", "shouldnt": "should not",
    "let's": "let us", "lets": "let us", "i'll": "i will",
    "you'll": "you will", "youll": "you will", "we'll": "we will",
    "they'll": "they will", "theyll": "they will", "i'd": "i would",
    "you'd": "you would", "youd": "you would", "we'd": "we would",
    "they'd": "they would", "theyd": "they would", "doesn't": "does not", "doesnt": "does not"
}

# Seed words that define each axis when full 50-number GloVe vectors are loaded.
# Each axis = direction from the second list's average toward the first list's average,
# scaled so the seed words land at about +2.5 / -2.5 (the same scale as the hand-set word weights).
AXIS_SEEDS = {
    "A": (["calm", "peace", "peaceful", "happy", "joy", "love", "safe", "gentle", "kind", "hope", "relaxed", "comfort",
           "warm", "grateful", "glad", "pleasant", "wonderful", "beautiful", "delight", "trust", "serene", "cheerful",
           "content", "lovely", "good", "great", "excellent", "smile", "friendly", "harmony"],
          ["panic", "fear", "afraid", "scared", "anxious", "worry", "terror", "angry", "hate", "sad", "pain", "danger",
           "threat", "dread", "nervous", "upset", "miserable", "awful", "terrible", "horrible", "cruel", "hurt", "grief",
           "lonely", "stress", "tense", "bad", "worst", "violent", "disaster"]),
    "S": (["together", "friend", "friends", "share", "community", "family", "team", "connect", "cooperation", "trust",
           "love", "help", "talk", "meet", "welcome", "kindness", "empathy", "partner", "join", "support",
           "conversation", "group", "unity", "neighbor"],
          ["alone", "lonely", "isolated", "solitary", "apart", "hide", "hidden", "separate", "withdrawn", "guarded",
           "closed", "distant", "silent", "ignore", "abandon", "exile", "secret", "private", "solitude", "avoid",
           "reject", "stranger", "defensive", "hesitant"]),
    "Z": (["theory", "concept", "idea", "meaning", "philosophy", "wisdom", "insight", "pattern", "structure", "system",
           "principle", "logic", "truth", "knowledge", "reason", "abstract", "synthesis", "belief", "understanding",
           "thought", "consciousness", "hypothesis", "analysis", "mind"],
          ["stone", "rock", "water", "hand", "table", "chair", "door", "tree", "ground", "body", "foot", "car", "house",
           "rain", "wood", "bread", "cup", "wall", "floor", "road", "dog", "river", "metal", "window"]),
}

def first_token_is_word(first_tok):
    try:
        float(first_tok)
        return False
    except ValueError:
        return True

ENGINE_VERSION = "24.1.1"  # the bridge shows this at startup so a mismatched engine/bridge pair is easy to spot


class ToroidalBrainEngine:
    # v21.3: how far each of the 10 trajectory steps really moves (1.0 = the old full-cell steps, which lapped the ring)
    TRAJECTORY_DAMPING = 0.1875

    # v23.4.3 step 1 of real time: ONE clock for the whole engine. now() is the real time unless a clock was handed in
    # (ToroidalBrainEngine(..., clock=f) or the class attribute CLOCK, set before the brain is made, so the wake-up sleep
    # on load uses it too). Tests use a fake clock so a silence can be made exactly and two runs give identical results;
    # the real-time branch will use it to fast-forward time.
    CLOCK = None

    def now(self):
        """Front door (v23.4.3): the engine's current time in seconds (the real clock unless a clock was given)."""
        return self.clock() if self.clock else time.time()

    def __init__(self, glove_file="glove.6B.50d.txt", memory_file="brain_memory.json", max_glove_words=50000, clock=None):
        self.clock = clock or type(self).CLOCK  # v23.4.3 (must be set before anything reads the time)
        self.memory_file = memory_file
        self.dim = 50
        self.vectors, self.factory_vectors, self.raw_glove, self.word_rank = {}, {}, {}, {}
        # Which word space is loaded: "builtin" (no file), "map2d" (2-number word map), or "glove50d" (full 50-number GloVe)
        self.vector_mode = "builtin"
        self.calibrated_axes = {}  # filled only in "glove50d" mode; empty means use the original pole formula
        self.word_weights, self.social_weights, self.epistemic_weights = {}, {}, {}
        self.factory_word_weights = {}
        self.assoc_graph, self.rejected_links, self.cortical_cells, self.knowledge_facts = {}, {}, {}, {}
        self.idea_memory = [dict(p) for p in BRAIN_LIBRARY["seed_propositions"]]
        self.verb_strata = {k: list(v) for k, v in BRAIN_LIBRARY["Z_verb_strata"].items()}
        self.custom_verb_bridges = []
        self.dream_journal = []
        self.user_profile = {
            "user_name": "",
            "bot_name": "",
            "pending_bot_name": "",
            "pending_name_origin": ""
        }
        # UPGRADE 1: Known manifold & user identity tokens + active dialogue partner tracking
        self.base_identity_tokens = set()  # names come from user_profile / dialogue partner at runtime
        self.dialogue_partner_name = ""
        self.turn_taught = {}  # v21.4: definitions the user taught in the current turn
        self.turn_word_names = set()  # v21.3: names used as ordinary words in the current turn (see find_names_used_as_words)
        self.identity_query_triggers = {"name", "named", "call", "called", "who", "identity", "yourself", "myself"}

        self.cell_centroids, self.cell_lexicon, self.trace_lexicon = {}, {}, {}
        self.crystal_lattices = {}
        self.cleavage_log = []
        # v21.6: sleep-bridge habituation (word -> recent uses, halves every sleep pass) and the words this brain has
        # actually been told (so a built-in word it never met can't become its default comfort word)
        self.bridge_habituation = {}
        self.experienced_words = set()
        # v22.5 cerebellum: what the brain expects next turn, and how surprised it was this turn
        self.expectation = None          # {"words": {word: weight}, "cell": "s,a,z"}
        self.surprise_baseline = 0.5     # running average of surprise (what's normal for this brain)
        self.turn_learning_gain = 1.0    # scales this turn's waking learning (1 = normal)
        self.last_surprise = None
        self.cerebellum_on = os.environ.get("TORRENT_CEREBELLUM", "1").strip() != "0"
        self.word_sightings = None  # v22.4: turns in which the user typed each non-dictionary word (None = not set up yet)
        self.seen_once_ready = False  # v22.11: word_sightings also counts ordinary words (set up on first use)
        self.prev_turn_concepts, self.prev_turn_time = [], None  # v22.11 amygdala: last turn's words (this session only)
        # v21.9: what was learned since the last sleep (sleep scales down in proportion to it)
        self.cells_added_since_sleep = 0.0
        self.link_strength_added_since_sleep = 0.0
        self.links_used_since_sleep = set()
        self.sleep_link_added = 0.0      # v24.1: link strength made while asleep (dreams, sleep's own links) since the last wake-up sleep
        self.new_links_since_sleep = 0   # v22: links created since the last full sleep (sets the night's release limit)
        self.awake_turn = False          # v22: True while answering the user (only that learning builds sleep pressure)
        self.sleep_depth = None          # v22: set during a wake-up sleep (hours away / SLEEP_FULL_HOURS, max 1)
        self.last_sleep = {}             # v22.1: memory of the last wake-up sleep (see run_stasis_sleep_pass)
        self.last_sleep_released = 0     # v22.1: links released by the last wake-up sleep
        # v22.6 mood level (off by default, saved per brain): the calm axis acts like a drug level with clearance
        self.mood_level_on = False
        self.levels_on = True            # v23 chemical levels (TORRENT_LEVELS=0 or /levels = v22.11 behaviour)
        self.arousal, self.arousal_mean = 0.0, 0.0  # v23: tension-like level 0..1 and its slow running average
        self.valence_level = None        # v23.3: valence as its own level, -1..+1 (None = read it from seed_a once)
        self.novelty = 0.5               # v23.3: novelty level 0..1 (rests at 0.5; low = bored)
        self.awake_minutes = 0.0         # v23.3: time awake since the last sleep (the clock part of sleep pressure)
        self.recent_turns = []           # v23.3: the last RECENT_TURNS_KEEP turns (words, speaker, levels) for replay
        self.caretaker_last_seen = None  # v23.3: when the caretaker last spoke (people keep their own last_seen)
        self._levels_clock = None        # v23.3: when the levels last ticked (this session only)
        self.idle_menu_on = os.environ.get("TORRENT_IDLE_MENU", "1").strip() != "0"  # v23.4 option menu (idle + levels on)
        self.idle_habits, self.idle_outcome_mean = {}, 0.0  # v23.4: learned bias per idle option, and the usual outcome
        _seed = os.environ.get("TORRENT_SEED", "").strip()
        self.idle_rng = random.Random(int(_seed)) if _seed.lstrip("-").isdigit() else random.Random()  # v23.4 choices
        self.idle_on, self.idle_visits, self.idle_journal, self.last_idle = False, {}, [], None  # v22.8
        self.idle_this_turn, self.last_turn_time = None, None  # last_turn_time is this session only (restarts sleep instead)
        self._menu = None                # v23.5: the open silence (live idle), between clock ticks
        self.live_on = False             # v23.5: live idle (the bridge's clock calls live_tick); off = v23.4 behaviour
        self.speak_on = False            # v23.5.3: speaking up (live only; the bridge turns it on with /speak on)
        self.speak_outbox = []           # v23.5.3: packets waiting for the bridge (speak_take)
        self.speak_last = None           # when it last spoke up (this session)
        self.speak_pending = None        # the last speak-up, until the person answers it
        self.speak_said = set()          # things already spoken about (each can win once)
        self.speak_unanswered = 0        # speak-ups in a row the person hasn't answered yet
        self._stem_cache = {}            # v24.1.1: same_stem results
        self.rhythm_on = os.environ.get("TORRENT_RHYTHM", "").strip() == "1"  # v24.0 daily rhythm (off by default)
        self.rhythm_offset = 0.0         # v24.0: hours this brain's night is shifted later (/rhythm +3)
        self.felt_usual = None           # v24.0: this brain's usual idle events per awake hour (None = not yet known)
        self.idle_focus = None  # v22.9: where the last walk ended (kept apart from last_topic, which is the user's)
        self.a_level_resid = 0.0         # v22.6.3: fraction of the calm level below one cell (kept between turns)
        self.a_push_mean = 0.0           # slow running average of the calm push (removes this brain's standing lean)
        self.turn_counter = 0            # turns seen (for the split refractory period)
        self.split_rest = {}             # word -> turn it was last moved by a split
        self.saved_demoted = {}          # v22.6.4: cell -> words annealing demoted, read from the brain file at load
        # v22.7 source tags: "a|b" -> {source: share of the link's strength}; a link with no entry is all "legacy"
        self.link_sources = {}
        self.wire_source = None          # set by callers (the bridge sets "voice"); None = decide from context
        self.show_tectonics = False      # v23.2: print every cleavage/annealing event (/tectonics); off = one summary line
        self._quiet_tectonics = {"cleave": 0, "relief": 0}
        self.people = {}                 # v23.2: known people other than the caretaker: name -> {role, first_seen, last_seen, turns}
        self.current_speaker = None      # v23.2: who is talking this session (None = the caretaker); not saved
        self.reading = False             # v23.2: True while read() feeds a book line (a narrator, not a person)
        self.source_tags_on = os.environ.get("TORRENT_SOURCE_TAGS", "1").strip() != "0"
        self.nightmare_mode = False      # v22.3: switch off the engine's "lean up" rules (see lean_up_words)
        self.scratchpad = []
        self.boot_sleep_report = []

        self.governor_mode = "FLIPPED"
        self.training_wheels = True
        self.seed_s, self.seed_a, self.seed_z = 3, 3, 3
        self.vel_s, self.vel_a, self.vel_z = 0.0, 0.0, 0.0
        self.last_hypothesis, self.last_topic, self.last_audit, self.last_trace_key = None, None, None, None
        self.pending_question = None
        self.last_thought_trace = {}
        self.recent_openers, self.recent_closers, self.recent_bridges = [], [], []
        self.spoken_deductions = set()
        self.spoken_chains = set()

        self.negation_tokens = {
            "not", "never", "no", "without", "neither", "nor", "dont", "don't",
            "doesnt", "doesn't", "isnt", "isn't", "arent", "aren't", "cant",
            "can't", "wont", "won't", "cannot", "didnt", "didn't"
        }

        self.stop_words = {
            "i", "you", "me", "my", "your", "we", "us", "our", "they", "them", "he", "she", "it",
            "the", "a", "an", "this", "that", "these", "those", "is", "am", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "shall", "should", "can", "could", "may", "might", "must", "to", "of", "in", "on",
            "at", "by", "for", "with", "about", "against", "between", "into", "through", "during",
            "before", "after", "above", "below", "from", "up", "down", "out", "off", "over",
            "under", "again", "further", "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just", "but",
            "and", "or", "if", "because", "as", "until", "while", "what", "which", "who", "whom",
            "seem", "seems", "seemed", "pretty", "much", "really", "quite", "rather", "right",
            "now", "well", "like", "way", "ways", "thing", "things", "one", "ones", "got", "get",
            "getting", "make", "making", "made", "going", "know", "yes", "yeah", "yep", "nope",
            "nah", "hmm", "uh", "oh", "okay", "ok", "sure", "absolutely", "totally", "definitely",
            "certainly", "also", "another", "word", "words", "concept", "concepts", "idea", "ideas",
            "related", "bridge", "bridges", "point", "points", "fit", "fits", "fitting", "mean",
            "means", "meant", "meaning", "explore", "teach", "talk", "talking", "perfectly", "together",
            "nowhere", "appeared", "appear", "go", "sometimes", "actually", "asking", "doing",
            "think", "thinking", "want", "hear", "hearing", "tell", "telling", "say", "saying",
            "call", "called", "name", "named", "feeling", "emotion", "state", "someone", "something",
            "anyone", "anything", "everyone", "everything", "nobody", "nothing", "folks", "people",
            "person", "multiple", "see", "saw", "seen", "look", "looks", "looked", "greeting",
            "greet", "leads", "lead", "sound", "sounds", "sounded", "feels", "felt", "important",
            "try", "tries", "tried", "trying", "else", "give", "gives", "gave", "given", "giving",
            "today", "tomorrow", "yesterday", "day", "days", "time", "times", "second", "seconds",
            "minute", "minutes", "freely", "maybe", "youve", "theyve", "couldve", "wouldve",
            "shouldve", "speek", "speak", "speaking", "spoke", "however", "although", "though",
            "unless", "instead", "otherwise", "completely", "complete", "always", "never", "often",
            "create", "creates", "created", "creating", "introduce", "introduces", "introduced",
            "phrase", "phrases", "alright", "hey", "hello", "goodbye", "morning", "night",
            "extremely", "still", "even", "already", "statement", "statements"
        }
        self.negative_lexicon = {
            "panic", "scared", "fear", "worry", "afraid", "anxious", "tense", "overwhelm",
            "overwhelmed", "scare", "bad", "fail", "loss", "threat", "dangerous", "danger",
            "dead", "kill", "war", "attack", "enemy", "hate", "pain", "crisis", "disaster",
            "trapped", "wrong", "worst", "terrible", "misunderstood", "apologize", "lie", "deceive"
        }
        self.noise_words = {
            "fifa", "forecasts", "flag", "fans", "corp", "inc", "ltd", "suddenly", "reuters",
            "ap", "afp", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
            "sunday", "january", "february", "march", "april", "june", "july", "august",
            "september", "october", "november", "december", "makes", "job", "exit", "links", "sounds", "youve"
        }
        self.generic_hubs = {"hello", "hi", "hey", "good", "nice", "feel", "yes", "thank", "thanks", "goodbye", "working"}
        # v21.3 filler words: these carry real social, time-of-day or curiosity meaning but sat in the filler
        # (stop) list, so they were thrown away before they could move the brain ("together" even has a
        # built-in social weight of +3.0 that was never used). They move to the "common word" tier instead:
        # they count as words for movement, cells and learning, but stay out of crystals and dream threads
        # and are held back as bridges, the same way "hello", "good" and "thank" already were.
        self.filler_to_hub = {
            "together", "talk", "talking", "speak", "speaking", "people", "everyone", "nobody",
            "hello", "goodbye", "morning", "night", "explore", "important", "goodnight"
        }
        self.stop_words -= self.filler_to_hub
        self.generic_hubs |= self.filler_to_hub

        self.core_concept_pool = set()
        for words in BRAIN_LIBRARY["semantic_clusters"].values():
            for w in words:
                w_low = w.strip().lower()
                if w_low not in self.stop_words:
                    self.core_concept_pool.add(w_low)
        self.tone_pool = [w.strip().lower() for t_list in BRAIN_LIBRARY["S_band_tones"].values() for w in t_list]
        self.core_emotion_pool = [w.strip().lower() for w in BRAIN_LIBRARY["emotion_cores"]]
        for w in self.tone_pool + self.core_emotion_pool:
            if w not in self.stop_words:
                self.core_concept_pool.add(w)
        # v21.3: the engine's own built-in vocabulary (before any learning), used to tell whether a name is also an ordinary word
        self.builtin_vocab = (set(self.core_concept_pool) | self.stop_words | self.negation_tokens | self.negative_lexicon
                              | self.generic_hubs | {w for pos, neg in AXIS_SEEDS.values() for w in pos + neg})

        self.init_builtin_50d_space()
        self.load_glove(glove_file, max_glove_words)
        self.recompute_poles_and_coords()
        self.init_emotional_lexicon()
        env_nm = os.environ.get("TORRENT_NIGHTMARE", "").strip()  # v22.3: set before loading, so the wake-up sleep follows it
        if env_nm in ("0", "1"):
            self.nightmare_mode = env_nm == "1"
        self.seen_once_on = os.environ.get("TORRENT_SEEN_ONCE", "").strip() != "0"  # v22.11
        self._env_levels = os.environ.get("TORRENT_LEVELS", "").strip()  # v23: "0"/"1" override the brain file
        self.amygdala_on = os.environ.get("TORRENT_AMYGDALA", "").strip() != "0"    # v22.11
        self.negation_v2 = os.environ.get("TORRENT_NEGATION", "").strip() != "0"    # v23.3.3 (0 = the v23.3.2 rules)
        self.last_tone, self.speaker_tone = None, {}  # v23.4.1 tone sense (measured only)
        self.relation_verbs = os.environ.get("TORRENT_RELATION_VERBS", "").strip() != "0"  # v23.3.3
        self.calm_learning = "landing" if os.environ.get("TORRENT_CALM", "").strip().lower() == "landing" else "company"  # v22.10 (set before loading: the wake-up sleep uses it)
        fresh_brain = not os.path.exists(self.memory_file)
        self.load_memory()
        if fresh_brain:  # v22.7: a new brain's starter links are built-in, not the user's
            self.link_sources = {self.link_key(a, b): {"builtin": 1.0} for a in self.assoc_graph for b in self.assoc_graph[a] if a < b}
        self._apply_env_overrides()
        self._levels_clock = self.now()  # v23.3: the levels' clock starts when the brain wakes
        self._ensure_word_sightings()  # v24.1: set up before the first message (it slipped past the seen-once rule)

    def _apply_env_overrides(self):
        """The environment switches override what the brain file says (v24.1: one place, also run just before the
        wake-up sleep on load, so that sleep follows them too)."""
        if os.environ.get("TORRENT_SOURCE_TAGS", "").strip() in ("0", "1"):
            self.source_tags_on = os.environ["TORRENT_SOURCE_TAGS"].strip() == "1"
        for env, attr in (("TORRENT_NIGHTMARE", "nightmare_mode"), ("TORRENT_IDLE", "idle_on"),
                          ("TORRENT_MOODLEVEL", "mood_level_on"), ("TORRENT_LEVELS", "levels_on"),
                          ("TORRENT_IDLE_MENU", "idle_menu_on"), ("TORRENT_RHYTHM", "rhythm_on")):
            v = os.environ.get(env, "").strip()
            if v in ("0", "1"):
                setattr(self, attr, v == "1")

    # =================================================================
    # UPGRADE 1: DYNAMIC IDENTITY TOKEN REGISTRY & SELF-QUERY DETECTOR
    # =================================================================
    def lean_up_words(self):
        """v22.3: the fear words the engine keeps out of bridges, recall and names. Empty in nightmare mode."""
        return set() if self.nightmare_mode else self.negative_lexicon

    # =================================================================
    # v22.7 SOURCE TAGS: who made each link (source monitoring)
    # =================================================================
    TRUSTED_SOURCES = ("user", "note", "legacy", "book")  # v23.2: "book" = read(); "user:<name>" = a known person

    @staticmethod
    def link_key(a, b):
        return f"{a}|{b}" if a < b else f"{b}|{a}"

    def set_wire_source(self, src):
        """Front door: links made until reset (None) count as made by src ("voice", "note"...). Returns the old value."""
        old, self.wire_source = self.wire_source, src
        return old

    def set_source_tags(self, on):
        """Front door: use source tags (True) or ignore them (False = v22.6.4 behaviour). Tags are recorded either way."""
        self.source_tags_on = bool(on)
        return self.source_tags_on

    # v23.2 PEOPLE AS SOURCES ---------------------------------------------------------------
    def caretaker_name(self):
        return str(self.user_profile.get("user_name", "")).strip().lower()

    def speaker_name(self):
        """Front door: who is talking right now (the caretaker unless /whoami says otherwise)."""
        return self.current_speaker or self.caretaker_name()

    def user_source(self):
        """The source tag for what the current speaker teaches: "user" for the caretaker, "user:<name>" for others."""
        sp = self.current_speaker
        return "user" if not sp or sp == self.caretaker_name() else f"user:{sp}"

    def register_person(self, name, role="known"):
        name = name.strip().lower()
        if name and name != self.caretaker_name() and name not in self.people:
            self.people[name] = {"role": role, "first_seen": round(self.now(), 1), "last_seen": None, "turns": 0}
        if name in self.people:
            self.person_start_numbers(name)
        return self.people.get(name)

    def person_start_numbers(self, name):
        """v23.2 fix: a person's name starts on the calm, social side. Before, an old book meaning was kept (Keel's
        'matt' sat at calm -1.37, and names don't drift, so every turn with Matt leaned tense). Runs once per person."""
        rec = self.people.get(name)
        if rec is None or rec.get("calm_set"):
            return
        self.word_weights[name] = max(1.5, float(self.word_weights.get(name, 1.5)))
        self.social_weights[name] = max(1.5, float(self.social_weights.get(name, 0.0)))
        rec["calm_set"] = True

    def whoami(self, name=None):
        """Front door: set who is talking. None, "" or the caretaker's name = the caretaker. Returns the speaker's name."""
        name = (name or "").strip().lower()
        if not name or name == self.caretaker_name():
            self.current_speaker = None
        else:
            self.register_person(name)
            self.current_speaker = name
        return self.speaker_name()

    def note_speaker_turn(self):
        sp = self.current_speaker
        if not sp or sp == self.caretaker_name():
            self.caretaker_last_seen = round(self.now(), 1)  # v23.3
        if sp and sp in self.people:
            self.people[sp]["turns"] = self.people[sp].get("turns", 0) + 1
            self.people[sp]["last_seen"] = round(self.now(), 1)

    def who_taught(self, a, b):
        """Front door: the a-b link's strength split by who made it (caretaker and people by name, book, voice...)."""
        shares = self.link_sources.get(self.link_key(a, b)) or {"legacy": 1.0}
        care = self.caretaker_name() or "caretaker"
        out = {}
        for k, v in shares.items():
            who = care if k in ("user", "legacy") else (k[5:] if k.startswith("user:") else k)
            out[who] = round(out.get(who, 0.0) + v, 3)
        return out

    def read(self, text):
        """Front door (v23.2 reading mode): learn from a line of a book. It is a narrator, not a person: no reply, no
        renaming, no corrections or questions, no taught definitions; its links are tagged "book". Returns the same
        (reply, audit, concepts) as respond(), with an empty reply."""
        old_src, self.reading = self.set_wire_source("book"), True
        try:
            return self.respond(text)
        finally:
            self.reading = False
            self.set_wire_source(old_src)

    # v23.4.1 /read: a whole text file, read in chunks with a full night between them (the diet Keel grew on: a whole
    # book in one sitting with no sleep would pile up words faster than the nightly fading can sort them).
    READ_PER_NIGHT = 40

    @staticmethod
    def split_book(text):
        """Front door (v23.4.1): a text file's sentences. A Project Gutenberg licence header/footer is left out, lines
        starting with '#' are skipped, and only sentences of 3+ words are kept."""
        lines = text.replace("﻿", "").splitlines()
        start = next((i + 1 for i, ln in enumerate(lines) if "*** START OF" in ln.upper()), 0)
        end = next((i for i, ln in enumerate(lines) if i >= start and "*** END OF" in ln.upper()), len(lines))
        body = " ".join(ln for ln in lines[start:end] if not ln.lstrip().startswith("#"))
        parts = re.split(r"(?<=[.!?])['\"”’]?\s+", " ".join(body.split()))
        return [p.strip() for p in parts if len(p.split()) >= 3]

    def book_night(self):
        """Front door (v23.4.1): the night between two reading chunks, as if the brain was closed and reopened 8 hours
        later: the exit dreams, then a full night's wake-up sleep. Returns (dreams, sleep report)."""
        dreams = self.run_dream_cycle(3)
        report = self.run_stasis_sleep_pass(self.SLEEP_FULL_HOURS)
        self.mark_turn_end()
        return dreams, report

    def read_file(self, path, per_night=None, restart=False, on_progress=None):
        """Front door (v23.4.1): read a text file as a book, per_night sentences (default READ_PER_NIGHT) then a night,
        repeated to the end. The place is bookmarked per file name (knowledge_facts '_book:<name>'), so reading the
        same file again continues where it stopped; restart=True starts over. Ctrl+C stops after the current line and
        keeps the bookmark. The brain is saved after every night. on_progress(event, info) is called with
        'start', 'sleeping', 'night' and 'done'. Returns a summary dict."""
        with open(path, encoding="utf-8", errors="replace") as f:
            sents = self.split_book(f.read())
        per = max(1, int(per_night or self.READ_PER_NIGHT))
        key = "_book:" + os.path.basename(path).lower()
        pos = 0 if restart else int(self.knowledge_facts.get(key, 0) or 0)
        if pos >= len(sents):
            pos = 0  # finished last time: read it again from the start
        info = {"file": os.path.basename(path), "total": len(sents), "start": pos, "per_night": per, "nights": 0,
                "read": 0, "words_before": len(self.assoc_graph), "interrupted": False, "cleaves": 0, "reliefs": 0}
        if on_progress:
            on_progress("start", dict(info))
        q = self._quiet_tectonics
        q0, shown = dict(q), self.show_tectonics
        self.show_tectonics = False  # counted, not printed line by line; the summary reports them
        try:
            while pos < len(sents):
                chunk_end = min(len(sents), pos + per)
                while pos < chunk_end:
                    c0, r0 = q["cleave"], q["relief"]
                    self.read(sents[pos])
                    info["cleaves"] += q["cleave"] - c0
                    info["reliefs"] += q["relief"] - r0
                    pos += 1
                    info["read"] += 1
                    self.knowledge_facts[key] = pos
                if pos < len(sents):  # a night between chunks; after the last one it stays awake (exit sleeps as usual)
                    if on_progress:
                        on_progress("sleeping", dict(info, pos=pos))
                    self.book_night()
                    info["nights"] += 1
                    self.save_memory()
                    if on_progress:
                        on_progress("night", dict(info, pos=pos, words=len(self.assoc_graph),
                                                  sleep=self.sleep_pressure_report().get("level")))
        except KeyboardInterrupt:
            info["interrupted"] = True
        finally:
            self.show_tectonics = shown
            q.update(q0)  # this reading's cleavages are in the summary, not in the next turn's note
        self.knowledge_facts[key] = pos
        self.mark_turn_end()
        self.save_memory()
        info.update(pos=pos, words=len(self.assoc_graph), finished=pos >= len(sents))
        if on_progress:
            on_progress("done", dict(info))
        return info

    def read_text_or_file(self, arg):
        """Front door (v23.4.1) for the /read command in both chat loops. 'FILE [N] [restart]' reads a file; anything
        else is read as one book line. Returns ('file', summary) / ('line', concepts) / ('missing', path)."""
        words = arg.split()
        restart = bool(words) and words[-1].lower() == "restart"
        if restart:
            words = words[:-1]
        per = None
        if len(words) > 1 and words[-1].isdigit():
            per, words = int(words[-1]), words[:-1]
        path = " ".join(words).strip().strip('"')
        if path and os.path.isfile(path):
            return "file", (path, per, restart)
        if path.lower().endswith((".txt", ".md")) and len(words) <= 3:
            return "missing", path
        return "line", arg.strip()

    # v23.4.1 TONE SENSE (experimental, measured only: it is shown and saved, and changes nothing in the brain).
    # Mood reads each word's own calm number, so a bleak, dismissive speaker read almost as warm as a kind one. This reads
    # the whole message: each content word's place on a warm <-> cold line (from GloVe: the meaning of a few warm example
    # sentences minus a few cold ones, written by hand), and the message's tone is the average of its 3 most strongly
    # charged words. Tested on the 2026-11-11 Gyre session (Matt's lines vs Zero's): it tells them apart 73% of the time,
    # but that variant was chosen after a first try failed (whole-sentence averaging: 52%, a coin flip), so it still needs
    # fresh lines to be trusted; it also confuses topic with tone ("we fixed that error" reads cold).
    TONE_WARM = ["Thank you so much, I really appreciate you.", "I'm so glad you're here with me.",
                 "That was kind of you, I'm happy we talked.", "I care about you and I'm proud of you.",
                 "You did a wonderful job, well done.", "It's lovely to see you again, my friend.",
                 "Take care and be gentle with yourself.", "I love how thoughtful you are."]
    TONE_COLD = ["That's useless, you're wasting my time.", "Whatever, I don't care what you think.",
                 "This is pointless and stupid.", "Stop talking nonsense and get to the point.",
                 "You never listen and it's annoying.", "I'm sick of this, it's all going badly.",
                 "Ugh, that's a lazy, empty answer.", "Things are hopeless and grim."]
    TONE_WARM_AT, TONE_COLD_AT = 0.10, -0.05   # words for the reading: warm / neutral / cold

    def _tone_axis(self):
        if getattr(self, "_tone_axis_cache", None) is not None:
            return self._tone_axis_cache
        harm = sum(1.0 / r for r in range(1, 50001))

        def sent_vec(text):
            fv = self.factory_vectors or self.vectors
            vecs = [(w, fv[w]) for w in re.findall(r"[a-z']+", text.lower()) if w in fv]
            if not vecs:
                return None
            out = [0.0] * len(vecs[0][1])
            for w, v in vecs:
                p = 1.0 / ((self.word_rank.get(w) or 50000) * harm)
                wt = 1e-3 / (1e-3 + p)  # rare words count more ("SIF" weighting)
                for i, x in enumerate(v):
                    out[i] += wt * x
            n = math.sqrt(sum(x * x for x in out)) or 1.0
            return [x / n for x in out]

        def centroid(lines):
            vs = [v for v in (sent_vec(t) for t in lines) if v]
            if not vs:
                return None
            c = [sum(col) / len(vs) for col in zip(*vs)]
            n = math.sqrt(sum(x * x for x in c)) or 1.0
            return [x / n for x in c]

        cw, cc = centroid(self.TONE_WARM), centroid(self.TONE_COLD)
        if not cw or not cc:
            self._tone_axis_cache = False
            return False
        axis = [w - c for w, c in zip(cw, cc)]
        n = math.sqrt(sum(x * x for x in axis)) or 1.0
        self._tone_axis_cache = [x / n for x in axis]
        return self._tone_axis_cache

    def tone_reading(self, text):
        """Front door (v23.4.1, experimental): the message's tone, about -0.3 (cold) .. +0.4 (warm), or None."""
        axis = self._tone_axis()
        if not axis:
            return None
        pols, fv = [], self.factory_vectors or self.vectors  # the original word meanings: a fixed sense, not reshaped by learning
        for w in set(self.clean_tokens(text)):
            v = fv.get(w)
            if v is None or w in self.stop_words or len(w) < 3:
                continue
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            pols.append(sum(a * b for a, b in zip(v, axis)) / n)
        if not pols:
            return None
        top = sorted(pols, key=lambda p: -abs(p))[:3]
        return round(sum(top) / len(top), 3)

    def tone_word(self, t):
        return "" if t is None else ("warm" if t >= self.TONE_WARM_AT else "cold" if t <= self.TONE_COLD_AT else "neutral")

    def note_tone(self, text):
        """v23.4.1: read and remember a person's message tone (last one, and a running average per speaker)."""
        t = self.tone_reading(text)
        self.last_tone = t
        if t is None:
            return
        who = self.current_speaker or (self.caretaker_name() or "user")
        rec = self.speaker_tone.setdefault(who, {"mean": 0.0, "n": 0})
        rec["n"] += 1
        rec["mean"] = round(rec["mean"] + (t - rec["mean"]) / min(rec["n"], 20), 4)  # the last ~20 messages

    def people_status(self):
        care = self.caretaker_name() or "(none)"

        def tone_txt(name):
            rec = self.speaker_tone.get(name)
            return f", tone {self.tone_word(rec['mean'])} {rec['mean']:+.2f} over {rec['n']} msgs" if rec else ""
        lines = [f"caretaker: {care}" + tone_txt(care) + ("  <- talking" if not self.current_speaker else "")]
        for n, p in sorted(self.people.items()):
            lines.append(f"{n} ({p.get('role', 'known')}, {p.get('turns', 0)} turns{tone_txt(n)})" + ("  <- talking" if n == self.current_speaker else ""))
        return lines

    def link_trust(self, a, b):
        """Front door: share (0..1) of the a-b link's strength that came from the user, notes or legacy."""
        shares = self.link_sources.get(self.link_key(a, b))
        return 1.0 if shares is None else sum(v for k, v in shares.items() if k in self.TRUSTED_SOURCES or k.startswith("user:"))

    def trusted_strength(self, a, b):
        """Front door: the part of the a-b link's strength that is trusted (all of it when source tags are off)."""
        v = self.assoc_graph.get(a, {}).get(b, 0.0)
        return v * self.link_trust(a, b) if self.source_tags_on else v

    def word_is_trusted(self, w):
        """Front door: may this word be used as the brain's own thought (bridge word, path step)? Yes if the user said
        it, it is built-in vocabulary, or at least one of its links has a trusted share. A word only the voice or dreams
        made up is not."""
        if not self.source_tags_on or w in self.experienced_words or w in self.builtin_vocab:
            return True
        return any(self.link_trust(w, nb) > 0.0 for nb in self.assoc_graph.get(w, {}))

    def _tag_link(self, w1, w2, base, amount, new_w, src):
        """Update the a-b link's source shares after its strength went from base to new_w by adding amount from src."""
        key = self.link_key(w1, w2)
        shares = self.link_sources.get(key)
        if shares is None:
            if src == "legacy":
                return
            shares = {"legacy": 1.0} if base > 0 else {}
        if new_w <= 0:
            self.link_sources.pop(key, None)
            return
        gained = max(0.0, new_w - base)  # includes a floor bump, which belongs to whoever caused it
        out = {k: v * base / new_w for k, v in shares.items()} if base > 0 else {}
        out[src] = out.get(src, 0.0) + gained / new_w
        tot = sum(out.values()) or 1.0
        out = {k: round(v / tot, 3) for k, v in out.items() if v / tot >= 0.0005}
        if set(out) == {"legacy"}:
            self.link_sources.pop(key, None)
        else:
            self.link_sources[key] = out

    BUILTIN_IDEA_SUMMARIES = {p["summary"] for p in BRAIN_LIBRARY["seed_propositions"]}

    # v22.7.2: the fixed connecting text the engine writes between concept words (verb phrases, path templates). It's
    # scaffolding, not something anyone said, so the bridge must not count its words as grounded.
    SCAFFOLD_TEMPLATE_WORDS = {"directly", "opens", "toward", "begins", "pivots", "through", "sparks", "opening", "shifts",
                               "unlock", "converge", "deepens", "anchors", "grounds", "bridges", "connects", "flows"}

    def scaffold_words(self):
        """Front door (v22.7.2): words that appear only as the engine's built-in connecting phrases. Words the user has
        actually used (experienced_words) are left out, so a real word of theirs is never held back for this."""
        phrases = [vb for pool in BRAIN_LIBRARY["Z_verb_strata"].values() for vb in pool]
        phrases += [vb for pool in BRAIN_LIBRARY["Z_oppose_verbs"].values() for vb in pool]  # v23.3.3
        phrases += [p["rel"] for p in BRAIN_LIBRARY["seed_propositions"]]
        words = {t for ph in phrases for t in re.findall(r"[a-z]+", ph.lower())} | self.SCAFFOLD_TEMPLATE_WORDS
        experienced = getattr(self, "experienced_words", set()) or set()
        return {w for w in words if w not in experienced and w not in self.stop_words}

    def is_builtin_idea(self, p):
        """v22.6.4 front door: True for one of the built-in seed sayings every brain starts with. They help the engine
        reason, but nobody said them, so the bridge must not show them to the voice as memories."""
        return str(p.get("summary", "")).strip().lower() in self.BUILTIN_IDEA_SUMMARIES

    def all_identity_names(self):
        """Every name the brain knows: the user's, its own (or pending) name, and an active dialogue partner's."""
        id_set = set(self.base_identity_tokens)
        for key in ("user_name", "bot_name", "pending_bot_name"):
            val = str(self.user_profile.get(key, "")).strip().lower()
            if val:
                id_set.add(val)
        if self.dialogue_partner_name:
            id_set.add(self.dialogue_partner_name.strip().lower())
        id_set.update(self.people)  # v23.2
        return id_set

    # =================================================================
    # v22.5 CEREBELLUM (v1): expect -> compare -> learn from the miss
    # After each turn the brain writes down what it expects next: which words, and how calm or tense the talk will be.
    # The next turn's miss is its surprise. (A first draft also compared landing cells; the stepping rule moves the
    # landing cell about 3 steps nearly every turn, so that part was noise and was dropped in testing.)
    # Surprise is judged against this brain's own running average, so normal conversation learns at the usual rate,
    # an unexpected turn is learned harder (up to x1.5) and a fully expected one lighter (down to x0.5).
    # Front doors: measure_surprise(), form_expectation(), surprise_report(), predict_voice_words(), check_voice().
    # =================================================================
    # v22.6 MOOD LEVEL (off by default; /moodlevel or TORRENT_MOODLEVEL=1). Tested 2026-11-09 (lab report, 3 seeds x 30
    # days of Alice): landing on the calm axis followed the turn's words (corr ~0 -> 0.46); with the split rest, churn
    # stayed near v22.5 and splits were ~1.5x.
    MOOD_CLEARANCE = 0.5      # share of the calm level that clears toward the middle before each turn (half-life 1 turn)
    # v23.4.1: 0.05 -> 0.01 (about a 70-turn memory instead of 14). At 0.05 one warm evening raised Gyre's "usual" from
    # +0.65 to +1.77, so friendly talk read below usual (replay of Matt's 2026-11-11 sessions: his turns below zero in
    # session 2 went 8/15 -> 4/15). TORRENT_LEAN_RATE overrides it.
    MOOD_LEAN_RATE = float(os.environ.get("TORRENT_LEAN_RATE", "0.01"))  # how fast the brain's "usual lean" follows its pushes
    SPLIT_REST_TURNS = 80     # a word moved by a split can't be moved again for this many turns

    COMPANY_RATE = 0.02       # v22.6.1: share of the gap to its company's average a word's calm number closes per turn

    CALM_HOME_RATE = 0.03     # v22.10: share of the gap to its home a word's calm number closes per full night

    def calm_home(self, w):
        """v22.10 front door: a word's home calm number: its hand-set built-in number, else its GloVe meaning reading.
        None for words with no innate meaning (made-up words and typos) and for names (the user's, the brain's own,
        a dialogue partner's), which keep what they learned: GloVe reads "matt" as tense (-1.37), not as a person."""
        if w in self.all_identity_names():
            return None
        if w in self.factory_word_weights:
            return self.factory_word_weights[w]
        if self.raw_glove and w not in self.raw_glove:
            return None  # v24.1: a made-up word's factory vector is built from its first sentence, not an innate meaning
        vec = self.factory_vectors.get(w)
        return self.axis_weight(vec, "A") if vec else None

    def calm_pull_home(self, depth):
        """v22.10: during a wake-up sleep, every calm number relaxes a little toward its home (scaled by sleep depth).
        Experience that keeps repeating holds a word away from home; one-off drift fades. Symmetric: fear words are pulled
        back toward fear too (this is balance, not lean-up). Returns how many numbers moved."""
        rate, moved = self.CALM_HOME_RATE * depth, 0
        for w, old in list(self.word_weights.items()):
            home = self.calm_home(w)
            if home is None or abs(home - old) < 1e-3:
                continue
            self.word_weights[w] = round(old + rate * (home - old), 3)
            moved += 1
        return moved

    SEEN_ONCE_LINK = 0.25     # v22.11: a link involving a word seen in only one turn so far (a normal user link adds 1.0)
    OUTCOME_RATE = 0.02       # v22.11 amygdala: share of the gap to what followed a word's calm number closes per turn
    OUTCOME_MAX_GAP_MIN = 30  # v22.11: a message more than this many minutes later isn't "what followed"

    def valence_of(self, w):
        """v22.11 front door: how a word feels to this brain right now (its calm number), else its home reading.
        One door for future pieces (the planned v23 chemical levels) to read feelings through."""
        if w in self.word_weights:
            return self.word_weights[w]
        return self.calm_home(w)

    def learn_calm_from_what_follows(self, words, gain=1.0):
        """v22.11 amygdala: the words of the user's previous message move a little toward how calm or tense THIS message
        is: a word that keeps being followed by distress grows tenser, one followed by calm grows calmer (conditioning,
        Rescorla-Wagner style: the change is a share of the gap between what followed and what the word stood for).
        Words in both messages are left to company learning; names are left alone. TORRENT_AMYGDALA=0 turns it off."""
        now = self.now()
        prev, prev_t = self.prev_turn_concepts, self.prev_turn_time
        names = self.all_identity_names()
        self.prev_turn_concepts = [w for w in words if w not in names and w not in self.stop_words]
        self.prev_turn_time = now
        if not self.amygdala_on or not prev or prev_t is None or (now - prev_t) / 60.0 > self.OUTCOME_MAX_GAP_MIN:
            return
        cur = [self.word_weights[w] for w in self.prev_turn_concepts if w in self.word_weights]
        if not cur:
            return
        outcome = sum(cur) / len(cur)
        for w in prev:
            if w in self.word_weights and w not in words:
                old = self.word_weights[w]
                self.word_weights[w] = round(max(-5.0, min(5.0, old + self.OUTCOME_RATE * gain * (outcome - old))), 3)

    def learn_calm_from_company(self, words, gain=1.0):
        """v22.6.1 front door: each word's calm number moves a little toward the average calm number of the OTHER
        words in the turn (not toward where the turn landed). It seeks a balance point, so it can't run away."""
        snap = {w: self.word_weights[w] for w in words if w in self.word_weights}
        for w, old in snap.items():
            others = [v for o, v in snap.items() if o != w]
            if others:
                target = sum(others) / len(others)
                self.word_weights[w] = round(max(-5.0, min(5.0, old + self.COMPANY_RATE * gain * (target - old))), 3)

    def set_mood_level(self, on):
        """Front door: switch the v22.6 mood level (+ split rest) on or off for this brain."""
        self.mood_level_on = bool(on)
        return self.mood_level_on

    # =================================================================
    # v23 CHEMICAL LEVELS (design: "Design draft: v23 Chemical Levels"). Names are vocabulary for this engine only.
    # Step 1: valence (the mood level's calm position, now on with the levels, clearing with a ~2-turn and 30-min
    # half-life) and arousal (tension-like, 0..1: rises with surprise and tense words, ruminating idle; sets how hard
    # a turn learns and, through the bridge's tone channel, how the voice sounds). Off = exactly v22.11.
    # =================================================================
    VALENCE_CLEARANCE = 0.3      # share of the calm level's distance from the middle that clears each turn (half-life ~2)
    VALENCE_HALF_MIN = 30.0      # ...and per 30 minutes of clock time
    AROUSAL_TURN_KEEP = 0.79     # share of arousal kept per turn (half-life ~3 turns)
    AROUSAL_HALF_MIN = 20.0      # arousal halves every 20 minutes of quiet
    AROUSAL_SURPRISE, AROUSAL_TENSE = 1.0, 1.0  # how much surprise (above usual) and tense words drive it (target, 0..1)
    AROUSAL_RISE_KEEP = 0.5      # rising is fast (half the gap per turn), falling slow (AROUSAL_TURN_KEEP)
    AROUSAL_GAIN_SPAN = 1.0      # learning gain = 1 + span x (arousal - its usual level), within 0.5..1.5
    AROUSAL_MEAN_RATE = 0.05     # how fast "usual arousal" adapts
    AROUSAL_IDLE = 0.25          # arousal added per unit of negative idle mood dose (rumination)

    # v23.3 step 2: valence is its own continuous level; novelty and sleep pressure become levels; one clock front door.
    VALENCE_CELLS = 3.0          # valence +-1 = 3 cells from the middle of the calm axis (cell 3)
    NOVELTY_REST = 0.5           # novelty rests here; 0 = everything predicted (bored), 1 = new and not tense
    NOVELTY_TURN_KEEP = 0.933    # share kept per turn while falling (half-life ~10 turns)
    NOVELTY_RISE_KEEP = 0.7      # rising is faster
    NOVELTY_HALF_MIN = 60.0      # with time, novelty drifts back to rest (half-life 60 min)
    NOVELTY_SAME = 0.15          # a turn whose surprise (words + mood) is below this was fully predicted (target 0)
    SLEEP_AWAKE_HOURS_PER_DAY = 12.0  # 12 hours awake adds as much sleep pressure as one busy day of learning
    RECENT_TURNS_KEEP = 20       # turns kept for replay (step 3)

    def mood_active(self):
        """v23: the calm axis behaves as a level (clearance, usual lean, split rest) when the mood level or the levels are on."""
        return self.mood_level_on or self.levels_on

    def set_levels(self, on):
        """Front door (v23): switch the chemical levels on or off for this brain."""
        if on and not self.levels_on:
            self.valence_level = None  # v23.3: pick valence up from where the calm axis is now
        self.levels_on = bool(on)
        return self.levels_on

    def _valence_now(self):
        """v23.3: the valence level, read once from the calm position (seed_a) if it hasn't been set yet."""
        if self.valence_level is None:
            self.valence_level = max(-1.0, min(1.0, (self.seed_a + self.a_level_resid - 3) / self.VALENCE_CELLS))
        return self.valence_level

    def _set_valence(self, v):
        """v23.3: set the valence level (clipped to -1..+1, never wrapped) and put the next turn's start on the calm axis
        there (seed_a + its fraction), so the torus starts where the mood is."""
        v = max(-1.0, min(1.0, v))
        self.valence_level = round(v, 4)
        level = 3 + self.VALENCE_CELLS * v
        self.seed_a = max(0, min(6, int(math.floor(level + 0.5))))
        self.a_level_resid = round(level - self.seed_a, 4)

    VALENCE_DOSE = 0.5           # share of the turn's move on the calm axis that reaches the valence level
    VALENCE_SOFT = True          # soft edges (tanh, like a drug's effect levelling off near its maximum), not a hard clip

    def valence_after_move(self, v, move_cells):
        """v23.3: the valence level after a turn moved `move_cells` cells on the calm axis."""
        d = self.VALENCE_DOSE * move_cells / self.VALENCE_CELLS
        if self.VALENCE_SOFT:
            v = max(-0.999, min(0.999, v))
            return math.tanh(math.atanh(v) + d)
        return v + d

    def valence(self):
        """v23: the calm level as -1..+1 (where the next turn starts on the calm axis, middle = 0).
        v23.3: with the levels on it is its own level, so it can't wrap from +1 to -1."""
        if self.levels_on:
            return round(self._valence_now(), 3)
        return round(max(-1.0, min(1.0, (self.seed_a + self.a_level_resid - 3) / 3.0)), 3)

    def sleep_pressure_units(self):
        """v23.3: sleep pressure in link-strength units: waking learning, plus (levels on) time awake, where
        SLEEP_AWAKE_HOURS_PER_DAY hours count as one busy day. Only the learning part sets how much sleep fades."""
        units = self.link_strength_added_since_sleep
        if self.levels_on:
            units += (self.awake_minutes / 60.0) * self.SLEEP_PRESSURE_BUSY_DAY / self.SLEEP_AWAKE_HOURS_PER_DAY
        return units

    def sleep_pressure_level(self):
        """Front door (v23.3): sleep pressure as a level, 0 = rested, 0.5 = "high" (one busy day), 1 = "very high" (two).
        Can go above 1."""
        return round(self.sleep_pressure_units() / (2.0 * self.SLEEP_PRESSURE_BUSY_DAY), 3)

    def levels(self):
        """Front door (v23): the current levels, for the bridge and the status line. None when off."""
        if not self.levels_on:
            return None
        return {"arousal": round(self.arousal, 3), "valence": self.valence(), "novelty": round(self.novelty, 3),
                "sleep": self.sleep_pressure_level()}

    def levels_status(self):
        lv = self.levels()
        return "off" if not lv else (f"arousal {lv['arousal']:.2f}, valence {lv['valence']:+.2f}, novelty {lv['novelty']:.2f}, "
                                     f"sleep pressure {lv['sleep']:.2f}")

    def levels_advance(self, minutes, awake=True, arousal_half_min=None):
        """Front door (v23.3): let `minutes` of clock time pass for the levels. Arousal halves every AROUSAL_HALF_MIN
        minutes (or arousal_half_min, e.g. a doze), valence relaxes toward neutral (VALENCE_HALF_MIN), novelty toward
        its rest (NOVELTY_HALF_MIN), and awake time adds to sleep pressure (awake=False: asleep, it doesn't).
        Step 3's option menu calls this block by block through a silence; real time would call it every tick."""
        if not self.levels_on or minutes <= 0:
            return
        half = arousal_half_min or self.AROUSAL_HALF_MIN
        self.arousal = round(self.arousal * 0.5 ** (minutes / half), 4)
        self._set_valence(self._valence_now() * 0.5 ** (minutes / self.VALENCE_HALF_MIN))
        self.novelty = round(self.NOVELTY_REST + (self.novelty - self.NOVELTY_REST) * 0.5 ** (minutes / self.NOVELTY_HALF_MIN), 4)
        if awake:
            self.awake_minutes = round(self.awake_minutes + minutes, 2)

    def levels_tick(self, now=None):
        """v23: clock-time clearance since the levels last ticked (call before idle time). v23.3: measured from the
        levels' own clock (set at load and at every tick), so the first turn after loading counts too, and the time
        is also awake time for sleep pressure."""
        now = self.now() if now is None else now
        last, self._levels_clock = self._levels_clock, now
        if last is None:
            last = self.last_turn_time
        if not self.levels_on or last is None:
            return
        self.levels_advance(max(0.0, (now - last) / 60.0))

    def levels_after_surprise(self, content):
        """v23: update arousal from this turn's surprise and how tense its words are, then set the learning gain from it
        (replaces the cerebellum's direct surprise gain while the levels are on). v23.3: novelty too."""
        if not self.levels_on:
            return
        sur = (self.last_surprise or {}).get("surprise")
        base = (self.last_surprise or {}).get("baseline") or 0.0
        words = [c for c in content if c not in self.stop_words][:6]
        calm = self.turn_calm_level(words)
        tense = max(0.0, min(1.0, -(calm or 0.0) / 2.0))
        # only surprise above this brain's usual level counts (ordinary surprise is the background, not arousal)
        excess = max(0.0, (sur if sur is not None else 0.0) - base)
        target = min(1.0, self.AROUSAL_SURPRISE * excess + self.AROUSAL_TENSE * tense)
        keep = self.AROUSAL_RISE_KEEP if target > self.arousal else self.AROUSAL_TURN_KEEP
        self.arousal = round(self.arousal * keep + (1 - keep) * target, 4)
        if sur is not None and self.cerebellum_on:
            gain = 1.0 + self.AROUSAL_GAIN_SPAN * (self.arousal - self.arousal_mean)
            self.turn_learning_gain = round(max(self.SURPRISE_GAIN_MIN, min(self.SURPRISE_GAIN_MAX, gain)), 3)
            self.last_surprise["gain"] = self.turn_learning_gain
        self.arousal_mean = round(self.arousal_mean + self.AROUSAL_MEAN_RATE * (self.arousal - self.arousal_mean), 4)
        self.novelty_after_turn(words, excess, tense)

    def novelty_after_turn(self, words, excess, tense):
        """v23.3: novelty moves toward a target set by this turn. A fully predicted turn aims at 0 (sameness); otherwise
        the target is rest + half of (surprise above usual that isn't tense + the share of real words the brain has never
        linked). The design doc splits surprise by how the NEXT turn feels; this uses the same turn's words (simpler,
        no delay). Measured and saved only: nothing reads it until step 3's option menu."""
        sur = (self.last_surprise or {}).get("surprise")
        if sur is None or not words:
            return
        new = sum(1 for w in words if w not in self.assoc_graph and w in self.vectors) / len(words)
        # "fully predicted" uses the whole surprise (words + mood), not the word part: the cerebellum expects a turn's
        # first 5 words but checks 6, so a long sentence repeated exactly still scores 0.167 on words (fix queue)
        if sur < self.NOVELTY_SAME:
            target = 0.0
        else:
            target = min(1.0, self.NOVELTY_REST + 0.5 * min(1.0, excess * (1.0 - tense) + new))
        keep = self.NOVELTY_RISE_KEEP if target > self.novelty else self.NOVELTY_TURN_KEEP
        self.novelty = round(self.novelty * keep + (1 - keep) * target, 4)

    def note_recent_turn(self, words):
        """v23.3: remember this turn for replay (step 3): its main words, who spoke, and the levels it left behind."""
        if not self.levels_on or self.reading:
            return
        self.recent_turns = (self.recent_turns + [{
            "t": round(self.now(), 1), "speaker": self.speaker_name() or "", "words": list(words)[:6],
            "valence": self.valence(), "arousal": round(self.arousal, 3),
            "surprise": (self.last_surprise or {}).get("surprise")}])[-self.RECENT_TURNS_KEEP:]

    def last_seen(self, name=None):
        """Front door (v23.3): when a person last spoke (None = the caretaker), as a timestamp, or None."""
        name = (name or "").strip().lower()
        if not name or name == self.caretaker_name():
            return self.caretaker_last_seen
        return (self.people.get(name) or {}).get("last_seen")

    def mood_level_status(self):
        """Front door: short status for the bridge and /moodlevel."""
        if not self.mood_level_on:
            return "off"
        return f"on (usual lean {self.a_push_mean:+.2f}, {sum(1 for t in self.split_rest.values() if self.turn_counter - t < self.SPLIT_REST_TURNS)} words resting)"

    # =================================================================
    # v22.8 IDLE TIME (experimental, off by default; /idle per brain)
    # Awake but not talked to. Computed as a catch-up when the next message arrives: the brain wanders along its own
    # links from where it was left, for one step per IDLE_MIN_PER_STEP minutes of silence (capped). Idle links are faint
    # and tagged "idle" (never trusted, so they can't ground a reply); sleep fades them like anything else.
    # Mind wandering: walk its links. Boredom: a word visited often gets picked less (idle habituation).
    # Restoring force: each step spent in tense words makes calmer neighbours more likely (much weaker in nightmare mode).
    # Creativity: now and then two words from the walk that were never linked get a faint new link if their meanings are close.
    # =================================================================
    IDLE_MIN_PER_STEP = 3.0      # minutes of silence per wandering step
    IDLE_MIN_GAP = 3.0           # shorter silences are just a pause
    IDLE_MAX_STEPS = 12          # cap per silence (a whole day away still gives 12)
    IDLE_LINK = 0.08             # strength added to each walked link (a user turn adds about 1.0-2.5)
    IDLE_NEW_LINK = 0.05         # a new link between two old ideas
    IDLE_NEW_LINK_SIM = 0.35     # how close in meaning two words must be for a new idle link
    IDLE_RESTORE = 0.45          # restoring force per tense step (nightmare mode: IDLE_RESTORE_NIGHTMARE)
    IDLE_RESTORE_NIGHTMARE = 0.08
    IDLE_HABITUATION = 0.45      # a word's pick weight is multiplied by this per earlier idle visit
    IDLE_CALMER = 0.3            # a word counts as a way out if its calm score is at least this
    IDLE_ESCAPE_DWELL = 3        # lean-up (nightmare off): this many tense words among the last IDLE_ESCAPE_WINDOW steps
    IDLE_ESCAPE_WINDOW = 4       # v22.9: a window, so one neutral step doesn't reset the count (tense-tense-neutral rings)
    IDLE_VISIT_DECAY = 0.7       # idle visits fade a little at every catch-up
    IDLE_TENSE = -0.5            # calm score below this counts as a tense word
    IDLE_LINK_FLOOR = 0.01       # v22.9: idle links skip wire_concepts' usual 0.25 minimum (faint means faint)
    IDLE_VECTOR_REF = 1.5        # v22.9: idle moves word meanings in proportion to amount / this (a user link is ~1.5)
    IDLE_MOOD_SCALE = 2.0        # v22.9: mood dose = walk's mean calm / this, clipped to -1..+1

    def set_idle(self, on):
        """Front door: switch idle time on or off for this brain."""
        if self._menu is not None:  # v23.5: an open live silence is closed first (it counts)
            self.idle_catch_up()
        self.idle_on = bool(on)
        if self.last_turn_time is not None:  # v22.9: silence before switching on wasn't idle time
            self.last_turn_time = self.now()
        return self.idle_on

    def mark_turn_end(self, now=None):
        """Front door (v22.9): the brain is done with this turn, so silence starts now. respond() calls it; the bridge
        calls it again once the voice has replied (so a slow model's thinking isn't counted as silence), and /sleep and
        /dream call it so a nap or dream isn't counted as idle time either. v23.5: a live silence still open is closed
        first (it has already been lived, so it counts)."""
        now = self.now() if now is None else now
        if self._menu is not None:
            self.idle_catch_up(now=now)
        self.last_turn_time = now

    # ---- v23.5 live idle: the silence is spent while it happens, one choice at a time, by the bridge's clock ----
    def set_live(self, on):
        """Front door (v23.5): live idle on/off. Needs idle time, levels and the option menu on. Turning it off closes
        any open silence (it counts)."""
        if not on and self._menu is not None:
            now = self.now()
            self.idle_catch_up(now=now)
            self.last_turn_time = now  # v24.0: the closed part counts once (the next message used to spend it again)
        self.live_on = bool(on)
        return self.live_on

    def live_tick(self, now=None):
        """Front door (v23.5): the bridge's clock calls this every few seconds while nobody is talking. It opens the
        silence once it is IDLE_MIN_GAP long, then makes each choice when it is due. Returns what the brain is doing
        ({"doing": "wander"/"leap"/"replay"/"doze"/"rest"/"asleep", "word":..., "new": [choices made this tick]}) or
        None when nothing is open. Cheap when nothing is due."""
        if not self.live_on:
            return None
        now = self.now() if now is None else now
        if self.speak_pending is not None:
            self._speak_resolve(now, answered=False)  # v23.5.3
        if self._menu is None:
            if not self._idle_menu_ready(now):
                return None
            self._idle_menu_begin(self.last_turn_time, live=True)
        return self._live_advance(now)

    def _live_advance(self, now):
        M = self._menu
        minutes = (now - M["start_t"]) / 60.0
        n0 = len(M["choices"])
        while self._idle_menu_step(minutes):
            pass
        return self.live_doing(new=M["choices"][n0:])

    def live_doing(self, new=None):
        """Front door (v23.5): what the open live silence is doing right now (None if none is open)."""
        M = self._menu
        if M is None:
            return None
        last = M["choices"][-1] if M["choices"] else None
        doing = "asleep" if M["asleep_since"] is not None else (last["option"] if last else "settling")
        return {"doing": doing, "word": M["st"].get("cur") if M["path"] else None, "minutes": round(M["t"], 1),
                "choices": len(M["choices"]), "new": [c["option"] for c in (new or [])]}

    def idle_path_text(self, rec=None):
        """Front door (v22.9): the walk as text. "->" follows a link; "~>" is a leap to a word it resembled (no link)."""
        rec = rec or self.last_idle
        if not rec:
            return ""
        path, jumps, replays = rec.get("path", []), set(rec.get("jumps", [])), set(rec.get("replays", []))
        out = path[0] if path else ""
        for i, w in enumerate(path[1:], start=1):
            out += (" => " if i in replays else " ~> " if i in jumps else " -> ") + w  # v23.4: "=>" thinks back to a moment
        return out

    def idle_before_exit(self, now=None):
        """Front door (v22.9): at /exit, the silence since the last turn still counts (a day left running, then closed).
        Returns the idle record, or None. Call it before the exit dreams and save."""
        return self.idle_catch_up(now=now)

    def idle_status(self):
        """Front door: short status for the bridge and /idle."""
        if not self.idle_on:
            return "off"
        last = self.last_idle
        return "on" + (f" (last: {last['minutes']:.0f} min, {self.idle_path_text(last)})" if last else "")

    def _idle_reminds_of(self, w, skip):
        """The known word (3+ links, trusted) closest in meaning to w, if close enough. None otherwise."""
        v = self.vectors.get(w)
        if not v:
            return None
        names = self.all_identity_names()
        best, best_sim = None, self.IDLE_NEW_LINK_SIM
        for cand, nbrs in self.assoc_graph.items():
            if (len(nbrs) < 3 or cand in skip or cand in self.stop_words or cand in names or cand not in self.vectors
                    or self.same_stem(cand, w) or not self.word_is_trusted(cand) or not self.is_valid_concept_node(cand)):
                continue
            sim = self.dot(v, self.vectors[cand]) * (self.IDLE_HABITUATION ** self.idle_visits.get(cand, 0.0))
            if sim > best_sim:
                best, best_sim = cand, sim
        return best

    def _idle_calm(self, w):
        """Calm score for idle wandering. A fear word with no stored score counts as tense, not neutral.
        v22.9: any other word with no stored score is read from its meaning (the same calm axis new words start from),
        instead of counting as neutral ("storm", "confusion" were 0.0 here but read about -2.7 by meaning)."""
        if w in self.word_weights:
            return self.word_weights[w]
        if w in self.negative_lexicon:
            return -2.0
        vec = self.factory_vectors.get(w) or self.vectors.get(w)
        return round(self.axis_weight(vec, "A"), 3) if vec else 0.0

    def _idle_is_calm(self, w):
        """A real way out of tension: calm score high enough, and not a fear word (some carry an old +0.5 reset)."""
        return self._idle_calm(w) >= self.IDLE_CALMER and w not in self.negative_lexicon and \
            self.factory_word_weights.get(w, 0.0) >= 0.0

    def _idle_candidates(self, cur, skip):
        names = self.all_identity_names()
        out = {}
        for nb, wt in self.assoc_graph.get(cur, {}).items():
            if (nb in skip or nb in self.stop_words or nb in names or not self.is_valid_concept_node(nb)
                    or not self.word_is_trusted(nb) or self.rejected_links.get(cur, {}).get(nb, 0.0) >= 0.5):
                continue
            out[nb] = wt
        return out

    def _idle_walk_step(self, st):
        """v23.4: one step of the idle walk (the v22.9 rules, moved out of idle_catch_up unchanged so the option menu can
        reuse them). st holds cur, path, calms, new_links, jumps, bored, restore, i (and escape_dwell for the valence
        floor). Returns False when the walk is stuck."""
        cur, path, calms, new_links, jumps, restore, i = (st["cur"], st["path"], st["calms"], st["new_links"],
                                                          st["jumps"], st["restore"], st["i"])
        cands = self._idle_candidates(cur, skip=set(path[-3:]))
        came_from = {w: cur for w in cands}  # the word each candidate is actually linked to
        jumped = False
        if not cands:  # dead end: the thought catches on something earlier in the walk
            for pw in reversed(path[:-1]):
                cands = self._idle_candidates(pw, skip=set(path))
                if cands:
                    came_from = {w: pw for w in cands}
                    break
        if not cands:  # still stuck (a word only linked to its own sentence): it reminds the brain of
            near = self._idle_reminds_of(cur, skip=set(path))  # a known word close in meaning
            if near:
                cands, came_from, jumped = {near: 1.0}, {near: cur}, True
        walked = calms[1:]
        dwell = sum(1 for c in walked[-self.IDLE_ESCAPE_WINDOW:] if c < self.IDLE_TENSE)
        escaping = False
        if dwell >= st.get("escape_dwell", self.IDLE_ESCAPE_DWELL) and not self.nightmare_mode:
            # lean-up: it may pass through fear, but not live there. First choice: a calm word linked to
            # something on this walk. Last resort: sleep's comfort bridge toward "calm" (v22.9: the v21.6 picker,
            # with habituation and told words only; v22.8 used the older picker, so built-in "quiet" kept winning).
            calmer = {w: wt for w, wt in cands.items() if self._idle_is_calm(w)}
            calmer_from, calmer_jump = {w: came_from[w] for w in calmer}, jumped
            if not calmer:
                calmer_jump = False
                for pw in reversed(path):
                    calmer = {w: wt for w, wt in self._idle_candidates(pw, skip=set(path)).items() if self._idle_is_calm(w)}
                    if calmer:
                        calmer_from = {w: pw for w in calmer}
                        break
            if not calmer and "calm" in self.vectors:
                # only calm told words may be the way out (from a tense word, the midpoint toward "calm" is
                # often another half-tense word, which the check below would reject)
                not_calm = {w for w in self.experienced_words if not self._idle_is_calm(w)}
                way_out = self.find_sleep_bridge(cur, exclude=set(path) | set(self.idle_visits) | self.stop_words | not_calm)
                if way_out and way_out in self.vectors and self._idle_is_calm(way_out):
                    calmer, calmer_from = {way_out: 1.0}, {way_out: cur}
                    calmer_jump = way_out not in self.assoc_graph.get(cur, {})
            if calmer:
                cands, came_from, jumped, escaping = calmer, calmer_from, calmer_jump, True
        if not cands:
            return False
        scored = {}
        for w, wt in cands.items():
            calm = self._idle_calm(w)
            pull = math.exp(max(-3.0, min(3.0, restore * dwell * calm)))  # dwelling in tension favours calmer words
            # log of the link strength: a strong fresh link is favoured, but can't trap the walk in a 3-word loop
            scored[w] = math.log1p(max(0.0, wt)) * (self.IDLE_HABITUATION ** self.idle_visits.get(w, 0.0)) * pull + 1e-9
        total = sum(scored.values())
        r, acc, nxt = random.random() * total, 0.0, None
        for w, sc in sorted(scored.items()):
            acc += sc
            if acc >= r:
                nxt = w
                break
        nxt = nxt or max(scored, key=scored.get)
        src = came_from.get(nxt, cur)
        if nxt in path and not jumped and not escaping:
            # v22.9 boredom: going back over the same ground. The walk leaps to a known word it resembles that it
            # hasn't visited (the "bigger steps toward rarely visited places" half of the design). No leap
            # available = it does go round again.
            near = self._idle_reminds_of(cur, skip=set(path))
            if near:
                nxt, src, jumped = near, cur, True
                st["bored"] += 1
        link_before = nxt in self.assoc_graph.get(src, {})
        if jumped:  # a leap makes a new faint link from the word that reminded it
            self.wire_concepts(cur, nxt, amount=self.IDLE_NEW_LINK, source="idle")
            src = cur
        else:
            self.wire_concepts(src, nxt, amount=self.IDLE_LINK, source="idle")
        if not link_before and nxt in self.assoc_graph.get(src, {}):
            new_links.append(f"{src}+{nxt}")
        self.idle_visits[nxt] = self.idle_visits.get(nxt, 0.0) + 1.0
        if i % 3 == 2 and len(path) >= 3:  # an old idea meets a new one
            far = path[-3]
            if (far != nxt and nxt not in self.assoc_graph.get(far, {}) and far in self.vectors and nxt in self.vectors
                    and self.dot(self.vectors[far], self.vectors[nxt]) >= self.IDLE_NEW_LINK_SIM):
                self.wire_concepts(far, nxt, amount=self.IDLE_NEW_LINK, source="idle")
                if nxt in self.assoc_graph.get(far, {}):
                    new_links.append(f"{far}+{nxt}")
        if jumped:
            jumps.append(len(path))
        path.append(nxt)
        calms.append(self._idle_calm(nxt))
        st["cur"] = nxt
        return True

    # =================================================================
    # v23.4 IDLE OPTION MENU (design: "Design draft: v23 idle option menu and urges", decisions 2026-11-11)
    # During catch-up idle the brain chooses, again and again through the silence, between wander, leap, replay, doze and
    # sleep. Each option's urge = a base + level readings (+ a small learned habit); the urges race to a line with a little
    # noise and the winner runs, then the levels tick for the minutes it used. Safety rules ("brainstem") come first and
    # can't be outvoted. Every choice is logged with its reasons. On when idle time and the levels are on;
    # TORRENT_IDLE_MENU=0 (or set_idle_menu(False)) gives the v23.3 walk.
    # =================================================================
    IDLE_STEP_MIN = 3.0          # wander / leap / replay: one step, 3 minutes
    IDLE_DOZE_MIN = 15.0         # doze: 15 minutes, no steps, nothing learned
    IDLE_DOZE_AROUSAL_HALF = 10.0  # arousal clears twice as fast while dozing (20 min awake)
    IDLE_SLEEP_MIN_LEFT = 30.0   # sleep needs at least this much silence left
    IDLE_MAX_DECISIONS = 40      # per silence; walk steps keep their own cap (IDLE_MAX_STEPS)
    IDLE_LIVE_MAX_DECISIONS = 600  # v23.5.2 live only: a safety rail (8 h of 3-minute steps is 160 at most)
    # v23.5.3 speaking up (live only). Urge = base + something to say + missing the person (x how it feels about them)
    # + bored - tired - unanswered + habit. First guesses, like every v23 weight. Design doc 2026-11-12.
    SPEAK_BASE, SPEAK_SAY, SPEAK_MISS, SPEAK_WARM = -0.3, 0.6, 0.5, 0.5
    SPEAK_BORED, SPEAK_TIRED, SPEAK_UNANSWERED = 0.2, 0.6, 0.5
    SPEAK_MIN_SILENCE = 20.0      # minutes of silence before it may speak up (they may still be reading)
    SPEAK_MIN_GAP = 45.0          # minutes between speak-ups (a safety rail)
    SPEAK_ANSWERED_MIN = 30.0     # answered within this: the habit goes up a little
    SPEAK_IGNORED_MIN = 120.0     # unanswered this long: the habit goes down a little
    SPEAK_ITEM = {"word": 0.8, "leap": 0.6, "replay": 0.6, "settled": 0.4}
    RACE_DT, RACE_NOISE, RACE_MAX_TICKS = 0.1, 0.3, 60
    RACE_LINE, RACE_LINE_AROUSAL = 1.0, 0.4  # the finish line = 1.0 - 0.4 x arousal (aroused = quicker, noisier choices)
    HABIT_RATE, HABIT_MAX, HABIT_NIGHT = 0.05, 0.2, 0.1  # habit learning rate, clip, shrink per full night
    HABIT_DISCOVERY, HABIT_RELIEF = 0.7, 0.3             # outcome = 0.7 discovery + 0.3 relief (decided 2026-11-11)
    IDLE_VALENCE_FLOOR = -0.6    # below it (nightmare off): replay only calm/neutral moments, escape after 2 tense steps
    IDLE_FLOOR_EPISODE = -0.2    # "calm or neutral" moment for the floor
    IDLE_AROUSAL_CEILING = 0.8   # idle can't push arousal past this (both modes)
    IDLE_OPTIONS = ("wander", "leap", "replay", "doze", "sleep")
    # v24.0 a sense of time, part 2 (design doc 2026-11-12, centered after the predictions found the draft's c only
    # ever added sleepiness). Daily rhythm: r(h) = cos(2pi(h - 3)/24), +1 at 3 am, 0 at 9 am and 9 pm, -1 at 3 pm, by
    # this computer's clock minus the brain's offset. It changes idle choices only (never how a message is learned).
    RHYTHM_PEAK_HOUR = 3.0
    RHYTHM_WEIGHTS = {"sleep": 0.5, "doze": 0.3, "wander": -0.2, "leap": -0.2, "speak": -0.3}
    RHYTHM_FORM = "centered"     # lab only: "approved" = the uncentered draft c(h) (kept to test the prediction T2a)
    RHYTHM_DOZE_BY_DAY = False   # the rhythm only adds to dozing (at night); by day dozing stays as it was. Making it
                                 # harder by day left the live thought count un-refreshed (only a doze refreshes it):
                                 # rested brains spent ~85% of the day resting awake in the lab (2026-11-12)
    RHYTHM_NIGHT_C = 0.75        # c above this (about 11 pm to 7 am) = "night" for the voice
    # Felt time (measured and told only; nothing else reads it). While passing (live silences): each minute counts
    # clip(1 + 0.6 boredom - 0.5 engagement, 0.5, 2); asleep counts FELT_MIN. Looking back (every menu silence):
    # awake minutes x clip(0.5 + 0.5 x events per hour / usual, 0.5, 2) + asleep minutes x FELT_MIN.
    FELT_BORED, FELT_ENGAGED, FELT_MIN, FELT_MAX = 0.6, 0.5, 0.5, 2.0
    FELT_B_MID, FELT_E_MID = 0.0, 0.0  # boredom / engagement that count as "neutral" (0, 0 = the draft's formula)
    FELT_USUAL_RATE = 0.1        # "usual events per hour" moves 10% toward each silence's own rate (awake time only)

    def set_idle_menu(self, on):
        """Front door (v23.4): use the option menu during idle time (True) or the v23.3 walk (False)."""
        self.idle_menu_on = bool(on)
        return self.idle_menu_on

    def _idle_menu_ready(self, now=None):
        now = self.now() if now is None else now
        return (self.idle_on and self.levels_on and self.idle_menu_on and not self.reading
                and self.last_turn_time is not None and (now - self.last_turn_time) / 60.0 >= self.IDLE_MIN_GAP)

    # ---- v24.0 a sense of time, part 2: daily rhythm ----
    def set_rhythm(self, on):
        """Front door (v24.0): the daily rhythm on/off (saved per brain)."""
        self.rhythm_on = bool(on)
        return self.rhythm_on

    def set_rhythm_offset(self, hours):
        """Front door (v24.0): shift this brain's night later (+) or earlier (-) by whole or half hours, within 12."""
        self.rhythm_offset = round(max(-12.0, min(12.0, float(hours))) * 2) / 2
        return self.rhythm_offset

    def rhythm_hour(self, when=None):
        """The brain's hour of day (0-24): this computer's local clock minus the brain's offset."""
        lt = time.localtime(self.now() if when is None else when)
        return (lt.tm_hour + lt.tm_min / 60.0 + lt.tm_sec / 3600.0 - self.rhythm_offset) % 24.0

    def rhythm_c(self, when=None):
        """Front door (v24.0): night-ness 0..1 (1 at 3 am, 0.5 at 9 am and 9 pm, 0 at 3 pm), whether or not it's on."""
        return 0.5 + 0.5 * math.cos(2 * math.pi * (self.rhythm_hour(when) - self.RHYTHM_PEAK_HOUR) / 24.0)

    def rhythm_r(self, when=None):
        """What the urges add a share of: 0 when the rhythm is off; else 2c - 1 (-1..+1), or c in the lab's "approved" arm."""
        if not self.rhythm_on:
            return 0.0
        c = self.rhythm_c(when)
        return c if self.RHYTHM_FORM == "approved" else 2.0 * c - 1.0

    def rhythm_term(self, option, when=None):
        """(reason, amount) the rhythm adds to an option's urge, or None."""
        w, r = self.RHYTHM_WEIGHTS.get(option), self.rhythm_r(when)
        if not w or abs(r) < 1e-9 or (option == "doze" and r < 0 and not self.RHYTHM_DOZE_BY_DAY):
            return None
        return ("night" if self.rhythm_c(when) >= 0.5 else "daytime", round(w * r, 3))

    def time_sense(self, when=None):
        """Front door (v24.0): what the brain knows about the time of day, for the bridge. Night = c above
        RHYTHM_NIGHT_C (only reported when the rhythm is on)."""
        c = self.rhythm_c(when)
        return {"rhythm": self.rhythm_on, "offset": self.rhythm_offset, "hour": round(self.rhythm_hour(when), 2),
                "c": round(c, 3), "night": bool(self.rhythm_on and c > self.RHYTHM_NIGHT_C)}

    def rhythm_status(self, when=None):
        ts = self.time_sense(when)
        if not self.rhythm_on:
            return "off (/rhythm on)"
        off = f", night shifted {self.rhythm_offset:+g} h" if self.rhythm_offset else ""
        return f"on ({'night' if ts['c'] >= 0.5 else 'daytime'} for it now, night-ness {ts['c']:.2f}{off})"

    def idle_urges(self, a, v, b, p, e, q, when=None):
        """v23.4: each option's urge as a list of (reason, amount); the urge is their sum plus the option's habit.
        a arousal 0..1, v valence -1..1, b boredom 0..1, p sleep pressure 0..1, e episode pull 0..1, q person pull 0..1.
        v24.0: `when` (clock time of the choice) adds the daily rhythm when it's on."""
        vneg = max(0.0, -v)
        terms = {
            "wander": [("base", 0.50), ("fresh ground", 0.30 * (1 - b)), ("tired", -0.30 * p)],
            "leap": [("base", 0.10), ("bored", 0.70 * b), ("restless", 0.20 * a)],
            "replay": [("base", 0.10), ("calm, and the last talk surprised it", 0.40 * e * (1 - a)), ("missing the person", 0.30 * q)]
                      + ([] if self.nightmare_mode else [("low mood (lean-up)", -0.40 * vneg)]),
            "doze": [("base", -0.10), ("tired", 0.60 * p), ("bored", 0.20 * b), ("too aroused to rest", -0.40 * a)],
            "sleep": [("base", -0.40), ("tired", 1.20 * p), ("too aroused to sleep", -0.50 * a)],
        }
        for k in terms:
            rt = self.rhythm_term(k, when)  # v24.0
            if rt:
                terms[k].append(rt)
            h = self.idle_habits.get(k, 0.0)
            if h:
                terms[k].append(("habit", h))
        return terms

    def idle_race(self, urges):
        """v23.4: each option's tally fills at its urge plus noise; the first over the line wins. Returns
        (winner, ticks, margin over the runner-up). No option over the line by RACE_MAX_TICKS = no decision (winner
        None): the brain just rests awake for a while. (Picking the highest tally there let noise decide between weak
        urges, and rested brains fell asleep in most long silences.)"""
        line = self.RACE_LINE - self.RACE_LINE_AROUSAL * self.arousal
        tally, sd = {k: 0.0 for k in urges}, self.RACE_NOISE * math.sqrt(self.RACE_DT)
        for t in range(1, self.RACE_MAX_TICKS + 1):
            for k in tally:  # fixed order, so a seed always gives the same race
                tally[k] += urges[k] * self.RACE_DT + sd * self.idle_rng.gauss(0.0, 1.0)
            best = max(tally, key=tally.get)
            if tally[best] >= line:
                rest = [x for k, x in tally.items() if k != best]
                return best, t, round(tally[best] - (max(rest) if rest else 0.0), 3)
        return None, self.RACE_MAX_TICKS, None

    def _idle_learn_habit(self, option, discovery, relief):
        """v23.4: nudge the option's bias by how this choice turned out, compared with the usual outcome."""
        o = self.HABIT_DISCOVERY * discovery + self.HABIT_RELIEF * max(-1.0, min(1.0, relief))
        h0 = self.idle_habits.get(option, 0.0)
        h = h0 + self.HABIT_RATE * ((o - self.idle_outcome_mean) - h0)  # moves 5% toward this outcome's surprise
        self.idle_habits[option] = round(max(-self.HABIT_MAX, min(self.HABIT_MAX, h)), 4)
        self.idle_outcome_mean = round(self.idle_outcome_mean + self.HABIT_RATE * (o - self.idle_outcome_mean), 4)
        return round(o, 3)

    def _idle_episodes(self, replayed, floor_on):
        """Recent moments the brain could think back to: (index, word, turn). Not the last turn (the walk already starts
        there), not one replayed twice; below the valence floor only calm or neutral moments."""
        names, out = self.all_identity_names(), []
        for i, turn in enumerate(self.recent_turns[:-1]):
            if replayed.get(i, 0) >= 2 or (floor_on and (turn.get("valence") or 0.0) < self.IDLE_FLOOR_EPISODE):
                continue
            w = next((x for x in turn.get("words", []) if x in self.assoc_graph and x not in names and x in self.vectors
                      and self.word_is_trusted(x)), None)
            if w:
                out.append((i, w, turn))
        return out

    def _idle_apply_walk_mood(self, path, calms, cap):
        """The walk's mood dose (v22.9 rule, levels on) with the v23.4 arousal ceiling. Returns (mood, dose, nudge)."""
        walked = calms[1:]
        mean_calm = sum(walked) / len(walked)
        end_tense = walked[-1] < self.IDLE_TENSE
        if mean_calm < self.IDLE_TENSE and end_tense:
            mood = "ruminated"
        elif calms[0] < self.IDLE_TENSE and not end_tense:
            mood = "settled"
        elif mean_calm > 0.5:
            mood = "calm"
        else:
            mood = "drifted"
        dose = max(-1.0, min(1.0, mean_calm / self.IDLE_MOOD_SCALE))
        self._set_valence(self._valence_now() + dose / self.VALENCE_CELLS)
        if dose < 0 and self.arousal < cap:
            self.arousal = round(min(cap, self.arousal + self.AROUSAL_IDLE * -dose), 4)
        return mood, dose, round(dose, 2)

    def _idle_menu(self, now):
        """The silence since the last turn, spent all at once (v23.4). v23.5: the same three parts the live clock uses
        (begin the silence, make one choice, finish), run in one go."""
        self._idle_menu_begin(self.last_turn_time, live=False)
        minutes = (now - self.last_turn_time) / 60.0
        while self._idle_menu_step(minutes):
            pass
        return self._idle_menu_finish(now)

    def _idle_menu_begin(self, start_t, live=False):
        """v23.5: open a silence. Its state lives in self._menu between choices (live: between clock ticks)."""
        self.levels_tick(now=start_t)  # anything before the silence (e.g. the voice replying); the silence comes next
        cur = self.last_topic
        walk_ok = bool(cur) and (cur in self.assoc_graph or cur in self.vectors)
        self.idle_visits = {w: v * self.IDLE_VISIT_DECAY for w, v in self.idle_visits.items() if v * self.IDLE_VISIT_DECAY >= 0.05}
        restore = self.IDLE_RESTORE_NIGHTMARE if self.nightmare_mode else self.IDLE_RESTORE
        path = [cur] if walk_ok else []
        calms = [self._idle_calm(cur)] if walk_ok else []
        st = {"cur": cur, "path": path, "calms": calms, "new_links": [], "jumps": [], "bored": 0, "restore": restore, "i": 0}
        sur = self.last_surprise or {}
        e = min(1.0, 2.0 * max(0.0, (sur.get("surprise") or 0.0) - (sur.get("baseline") or 0.0)))
        self._menu = {"start_t": start_t, "live": live, "walk_ok": walk_ok, "path": path, "calms": calms, "st": st,
                      "replays": [], "replayed": {}, "replay_streak": 0, "replay_off": False, "choices": [], "t": 0.0,
                      "steps": 0, "dozed": 0.0, "rested": 0.0, "slept": None, "walk_mood": None,
                      "speaker_seen": self.last_seen(self.current_speaker) or start_t, "e": e,
                      "cap": self.IDLE_AROUSAL_CEILING, "asleep_since": None}

    def _felt_add(self, M, minutes, engaged=0.0, asleep=False):
        """v24.0 felt time while passing (live silences only): `minutes` of clock time count as rate x minutes."""
        if not M.get("live") or minutes <= 0:
            return
        if asleep:
            rate = self.FELT_MIN
        else:
            b = M.get("b_last", 0.5)
            rate = max(self.FELT_MIN, min(self.FELT_MAX, 1.0 + self.FELT_BORED * (b - self.FELT_B_MID)
                                                - self.FELT_ENGAGED * (engaged - self.FELT_E_MID)))
            M["engaged_min"] = M.get("engaged_min", 0.0) + engaged * minutes
        M["felt"] = M.get("felt", 0.0) + rate * minutes
        M["felt_last_rate"] = rate

    def _idle_menu_step(self, minutes):
        """v23.5: one choice of the open silence, if one is due (`minutes` of silence so far). Returns True if it made a
        choice. Live (a brain can't know how long the silence will last): a doze is always a full doze, and sleep doesn't
        need IDLE_SLEEP_MIN_LEFT -- the brain sleeps until something wakes it (the sleep pass runs at wake-up)."""
        M = self._menu
        if M is None or M["asleep_since"] is not None or M["slept"] is not None:
            return False
        t, choices, live = M["t"], M["choices"], M["live"]
        cap_n = self.IDLE_LIVE_MAX_DECISIONS if live else self.IDLE_MAX_DECISIONS  # v23.5.2
        if not (len(choices) < cap_n and minutes - t >= self.IDLE_STEP_MIN):
            return False
        walk_ok, path, calms, st = M["walk_ok"], M["path"], M["calms"], M["st"]
        replays, replayed, replay_streak, replay_off = M["replays"], M["replayed"], M["replay_streak"], M["replay_off"]
        steps, start_t, cap = M["steps"], M["start_t"], M["cap"]
        old_src = self.set_wire_source("idle")
        old_gain, self.turn_learning_gain = self.turn_learning_gain, 1.0
        old_awake, self.awake_turn = self.awake_turn, True
        try:
            left = minutes - t
            a, v = self.arousal, self.valence()
            floor_on = v < self.IDLE_VALENCE_FLOOR and not self.nightmare_mode
            p = min(1.0, self.sleep_pressure_level())
            hab = [1 - self.IDLE_HABITUATION ** self.idle_visits.get(w, 0.0) for w in path[-3:]] if path else [0.0]
            b = 0.5 * (1 - self.novelty) + 0.5 * (sum(hab) / len(hab))
            q = 1 - math.exp(-max(0.0, (start_t + t * 60 - M["speaker_seen"]) / 3600.0))
            walking = walk_ok and steps < self.IDLE_MAX_STEPS
            episodes = self._idle_episodes(replayed, floor_on) if steps < self.IDLE_MAX_STEPS and not replay_off else []
            eligible = {"doze"}
            if walking:
                eligible |= {"wander", "leap"}
            if episodes:
                eligible.add("replay")
            if live or left >= self.IDLE_SLEEP_MIN_LEFT:
                eligible.add("sleep")
            terms = self.idle_urges(a, v, b, p, M["e"], q, when=start_t + t * 60)
            M["b_last"] = b  # v24.0 felt time
            urges = {k: round(sum(x for _, x in terms[k]), 3) for k in self.IDLE_OPTIONS if k in eligible}
            speak_item = None
            if live and self.speak_on and self._speak_ready(start_t + t * 60, t):  # v23.5.3
                speak_item = self._speak_item(M)
                terms["speak"] = self._speak_terms(speak_item[2], q, b, p, when=start_t + t * 60)
                urges["speak"] = round(sum(x for _, x in terms["speak"]), 3)
            forced = None
            if p >= 1.0:  # brainstem: very high pressure sleeps (or dozes, with too little time left)
                choice, ticks, margin = ("sleep" if "sleep" in eligible else "doze"), 0, None
                forced = "pressure"
            else:
                choice, ticks, margin = self.idle_race(urges)
            if choice is None:  # nothing crossed the line: rest awake (normal clearance, nothing learned, no habit)
                used = self.IDLE_DOZE_MIN if live else min(self.IDLE_DOZE_MIN, left)
                choices.append({"t": round(t, 1), "option": "rest", "urge": None, "ticks": ticks, "margin": None,
                                "forced": None, "reasons": ["no urge crossed the line"],
                                "levels": {"a": round(a, 2), "v": round(v, 2), "b": round(b, 2), "p": round(p, 2)}})
                self.levels_advance(used)
                M["rested"] += used
                self._felt_add(M, used, 0.0)  # v24.0
                replay_streak = 0
                t += used
                return True
            reasons = sorted((r for r in terms[choice] if r[0] != "base"), key=lambda r: -r[1])[:2]
            log = {"t": round(t, 1), "option": choice, "urge": urges.get(choice), "ticks": ticks, "margin": margin,
                   "forced": forced, "reasons": [f"{r} {x:+.2f}" for r, x in reasons],
                   "levels": {"a": round(a, 2), "v": round(v, 2), "b": round(b, 2), "p": round(p, 2)}}
            if floor_on:
                log["floor"] = True
            st["escape_dwell"] = 2 if floor_on else self.IDLE_ESCAPE_DWELL
            path_len = len(path)
            if choice == "speak":  # v23.5.3: speak up -- a packet for the bridge; the voice words it
                when = start_t + t * 60
                kind, words, _s = speak_item
                person = self.speaker_name() or self.caretaker_name() or ""
                packet = {"kind": kind, "words": list(words), "person": person, "away_min": round(t + self.IDLE_STEP_MIN, 1),
                          "levels": self.levels(), "path_tail": list(path[-5:]), "mood_so_far": self._speak_walk_mood(calms),
                          "when": round(when, 1), "reasons": log["reasons"]}
                self.speak_outbox.append(packet)
                if self.speak_pending is not None and not self.speak_pending.get("ignored"):
                    self.speak_pending["t"] = min(self.speak_pending["t"], when - self.SPEAK_IGNORED_MIN * 60)
                    self._speak_resolve(when, answered=False)  # spoke again before an answer: the last one went unanswered
                self.speak_unanswered += 1
                self.speak_last = when
                self.speak_said.add(kind + "|" + "|".join(words))
                self.speak_pending = {"t": when, "packet": packet, "ignored": False}
                log["said"] = {"kind": kind, "words": list(words)}
                used = self.IDLE_STEP_MIN
                self.levels_advance(used)
                self._felt_add(M, used, 0.5)  # v24.0: reaching out counts like thinking back
                replay_streak = 0
                t += used
                choices.append(log)
                return True
            if choice in ("wander", "leap", "replay"):
                did = choice
                if choice == "replay":
                    weights = [max(0.05, (ep[2].get("surprise") or 0.5)) for ep in episodes]
                    idx, w, turn = episodes[self._weighted_pick(weights)]
                    replayed[idx] = replayed.get(idx, 0) + 1
                    replay_streak += 1
                    if replayed[idx] >= 2 or replay_streak >= 3:
                        replay_off = True  # brainstem: rumination cap for the rest of this silence
                    ew = [x for x in turn.get("words", []) if x in self.assoc_graph.get(w, {})][:2]
                    for x in ew:  # rehearsal: the moment's own links, faintly (tagged idle like every idle link)
                        self.wire_concepts(w, x, amount=self.IDLE_LINK, source="idle")
                    if not walk_ok:
                        walk_ok, path, calms = True, [w], [self._idle_calm(w)]
                        st.update(cur=w, path=path, calms=calms)
                        M["first_replay"] = 1  # v24.0: a replay that starts the walk is still a thought back (felt time)
                    else:
                        replays.append(len(path))
                        path.append(w)
                        calms.append(self._idle_calm(w))
                        st["cur"] = w
                    self.idle_visits[w] = self.idle_visits.get(w, 0.0) + 1.0
                    log["episode"] = {"words": turn.get("words", [])[:4], "valence": turn.get("valence"),
                                      "speaker": turn.get("speaker")}
                    M.setdefault("say", []).append(("replay", [w] + [x for x in turn.get("words", [])[:3] if x != w],
                                                    self.SPEAK_ITEM["replay"] * min(1.0, float(turn.get("surprise") or 0.0))))
                else:
                    moved = False
                    if choice == "leap":
                        near = self._idle_reminds_of(st["cur"], skip=set(path))
                        if near:
                            self.wire_concepts(st["cur"], near, amount=self.IDLE_NEW_LINK, source="idle")
                            if near in self.assoc_graph.get(st["cur"], {}):
                                st["new_links"].append(f"{st['cur']}+{near}")
                                M.setdefault("say", []).append(("leap", [st["cur"], near], self.SPEAK_ITEM["leap"]))
                            self.idle_visits[near] = self.idle_visits.get(near, 0.0) + 1.0
                            st["jumps"].append(len(path))
                            path.append(near)
                            calms.append(self._idle_calm(near))
                            st["cur"], moved = near, True
                        else:
                            did = "leap (nothing to leap to: wandered)"
                    if not moved:
                        st["i"] = steps
                        if not self._idle_walk_step(st):
                            walk_ok, did = False, choice + " (stuck)"
                    replay_streak = 0
                log["did"] = did
                steps += 1
                used = self.IDLE_STEP_MIN
                relief = calms[-1] / 5.0 if calms else 0.0
                # discovery = how fresh the word reached is (unvisited 1.0, each earlier idle visit x0.45); a leap's
                # faint link is made by definition, so "made a new link" would reward leaping every time
                moved_to = path[-1] if path and len(path) > path_len else None
                fresh = self.IDLE_HABITUATION ** max(0.0, self.idle_visits.get(moved_to, 1.0) - 1.0) if moved_to else 0.0
                log["outcome"] = self._idle_learn_habit(choice, fresh, relief)
                self.levels_advance(used)
                # v24.0 engagement: a replay 0.5; a step 1 for a new link, else how fresh the word reached was
                made_link = len(st["new_links"]) > M.get("links_seen", 0)
                M["links_seen"] = len(st["new_links"])
                self._felt_add(M, used, 0.5 if choice == "replay" else 1.0 if made_link else fresh)
                t += used
            elif choice == "doze":
                used = self.IDLE_DOZE_MIN if live else min(self.IDLE_DOZE_MIN, left)
                a0 = self.arousal
                self.levels_advance(used, arousal_half_min=self.IDLE_DOZE_AROUSAL_HALF)
                extra = a0 * (0.5 ** (used / self.AROUSAL_HALF_MIN) - 0.5 ** (used / self.IDLE_DOZE_AROUSAL_HALF))
                log["outcome"] = self._idle_learn_habit("doze", 0.0, 5.0 * extra)
                M["dozed"] += used
                self._felt_add(M, used, 0.0)  # v24.0
                replay_streak = 0
                t += used
                if live and (steps or replay_off):  # v23.5.2: rest restores -- the thought count and the rumination
                    log["refreshed"] = steps        # cap start again after a doze (live only; a doze is 15 min)
                    steps, replay_off, replayed = 0, False, {}
                    M["replayed"] = replayed
            else:  # sleep: the rest of the silence, as a real sleep (dreams, fading, pressure drained)
                choices.append(log)
                if len(path) >= 2 and M["walk_mood"] is None:
                    M["walk_mood"] = self._idle_apply_walk_mood(path, calms, cap)
                if live:
                    M["asleep_since"] = start_t + t * 60  # live: asleep until woken; the sleep pass runs at wake-up
                    return True
                M["slept"] = round(left / 60.0, 2)
                self.awake_turn = False  # what sleep wires is not waking learning
                self.run_stasis_sleep_pass(M["slept"])
                t = minutes
                return True
            choices.append(log)
            return True
        finally:
            self.set_wire_source(old_src)
            self.turn_learning_gain = old_gain
            self.awake_turn = old_awake
            M.update(t=t, walk_ok=walk_ok, path=path, calms=calms, replay_streak=replay_streak, replay_off=replay_off,
                     steps=steps)

    # ---- v23.5.3 speaking up ----
    def set_speak(self, on):
        """Front door: speaking up on/off (only does anything with live idle on)."""
        self.speak_on = bool(on)
        return self.speak_on

    def speak_take(self):
        """Front door: the packets waiting to be voiced (and clears them). Each: kind, words, person, away_min, levels..."""
        out, self.speak_outbox = self.speak_outbox, []
        return out

    def _speak_ready(self, when, t):
        """Brainstem limits: only after SPEAK_MIN_SILENCE minutes of silence and SPEAK_MIN_GAP since the last speak-up.
        (Never while asleep or dozing: those don't make choices.)"""
        return t >= self.SPEAK_MIN_SILENCE and (self.speak_last is None or when - self.speak_last >= self.SPEAK_MIN_GAP * 60)

    def person_warmth(self, name):
        """How it feels about a person: its own average mood after their messages (recent turns), -1..1; 0 if unknown."""
        name = (name or "").lower()
        vals = [float(r.get("valence") or 0.0) for r in self.recent_turns if (r.get("speaker") or "").lower() == name]
        return max(-1.0, min(1.0, sum(vals) / len(vals))) if vals else 0.0

    def _speak_walk_mood(self, calms):
        if len(calms) < 2:
            return ""
        return ("settled" if calms[0] < self.IDLE_TENSE <= calms[-1] else "tense" if calms[-1] < self.IDLE_TENSE
                else "calm" if calms[-1] > 0.5 else "drifting")

    def _speak_item(self, M):
        """The strongest new thing to say: (kind, words, s). A barely-known word the person used, a new link from a
        leap, a surprising moment thought back to, a walk that settled; else ("missing", [], 0)."""
        cands = list(M.get("say", []))
        if self.word_sightings:
            person = (self.speaker_name() or "").lower()
            for r in reversed(self.recent_turns[-3:]):  # newest first, so a tie goes to the latest message
                if (r.get("speaker") or "").lower() != person:
                    continue
                for w in r.get("words", []):
                    if len(w) >= 4 and self.is_provisional_word(w):  # seen once (v24.1: not taught words or its own vocabulary)
                        cands.append(("word", [w], self.SPEAK_ITEM["word"]))
        calms, path = M["calms"], M["path"]
        if len(calms) >= 2 and calms[0] < self.IDLE_TENSE and calms[-1] > 0:
            cands.append(("settled", [path[0], path[-1]], self.SPEAK_ITEM["settled"]))
        cands = [c for c in cands if c[0] + "|" + "|".join(c[1]) not in self.speak_said and c[2] > 0]
        return max(cands, key=lambda c: c[2]) if cands else ("missing", [], 0.0)

    def _speak_terms(self, s, q, b, p, when=None):
        person = self.speaker_name() or ""
        w = self.person_warmth(person)
        n = float(min(3, self.speak_unanswered))  # each unanswered line in a row makes the next less likely
        terms = [("base", self.SPEAK_BASE), ("something to say", self.SPEAK_SAY * s),
                 ("missing the person", self.SPEAK_MISS * q * (1 + self.SPEAK_WARM * w)), ("bored", self.SPEAK_BORED * b),
                 ("tired", -self.SPEAK_TIRED * p), ("unanswered", -self.SPEAK_UNANSWERED * n)]
        rt = self.rhythm_term("speak", when)  # v24.0
        if rt:
            terms.append(rt)
        h = self.idle_habits.get("speak", 0.0)
        if h:
            terms.append(("habit", h))
        return terms

    def _speak_resolve(self, now, answered):
        """Habit learning for speaking up: answered soon = good, ignored = bad (speaking into an empty room teaches it
        to wait). Called when the person writes (answered) or from the live clock after SPEAK_IGNORED_MIN."""
        sp = self.speak_pending
        if sp is None:
            return None
        mins = (now - sp["t"]) / 60.0
        if answered:
            self.speak_pending, self.speak_unanswered = None, 0
            if sp.get("ignored"):
                return None  # already counted as ignored
            outcome = (1.0, 1.0) if mins <= self.SPEAK_ANSWERED_MIN else (0.0, -1.0) if mins >= self.SPEAK_IGNORED_MIN else (0.3, 0.0)
        elif mins >= self.SPEAK_IGNORED_MIN and not sp.get("ignored"):
            sp["ignored"] = True  # still counts as unanswered (n = 1) until they write
            outcome = (0.0, -1.0)
        else:
            return None
        self._idle_learn_habit("speak", *outcome)
        return round(mins, 1)

    def _idle_menu_finish(self, now):
        """v23.5: close the open silence at `now` (a turn, /exit, /sleep...). Live: a sleeping brain wakes, and the
        sleep pass runs for the hours actually slept. Returns the idle record (or None if no choice was made)."""
        M, self._menu = self._menu, None
        if M is None:
            return None
        minutes = (now - M["start_t"]) / 60.0
        if M["asleep_since"] is not None and (now - M["asleep_since"]) / 60.0 < self.IDLE_SLEEP_MIN_LEFT:
            # woken before the sleep got deep (under IDLE_SLEEP_MIN_LEFT): no sleep pass (it would run a whole
            # NREM+REM cycle for a few minutes); the time counts as a doze
            used = max(0.0, now - M["asleep_since"]) / 60.0
            self.levels_advance(used, arousal_half_min=self.IDLE_DOZE_AROUSAL_HALF)
            M["dozed"] += used
            self._felt_add(M, used, 0.0)  # v24.0: woken before the sleep got deep: felt like a doze
            M["choices"][-1]["woke_early"] = round(used, 1)
            M["t"] = max(M["t"], minutes)
        elif M["asleep_since"] is not None:
            M["slept"] = round(max(0.0, now - M["asleep_since"]) / 3600.0, 2)
            self._felt_add(M, max(0.0, now - M["asleep_since"]) / 60.0, asleep=True)  # v24.0
            old_src = self.set_wire_source("idle")
            old_gain, self.turn_learning_gain = self.turn_learning_gain, 1.0
            old_awake, self.awake_turn = self.awake_turn, False  # what sleep wires is not waking learning
            try:
                self.run_stasis_sleep_pass(M["slept"])
            finally:
                self.set_wire_source(old_src)
                self.turn_learning_gain = old_gain
                self.awake_turn = old_awake
            M["t"] = max(M["t"], minutes)
        if M["live"] and M["t"] > minutes and M["slept"] is None:
            # v24.0/v24.1: a live doze or rest is booked whole when it starts (a doze is never cut short); closed partway,
            # the record keeps only what was lived: felt time, dozed/rested minutes and awake time
            over = M["t"] - minutes
            if M.get("felt") is not None:
                M["felt"] = max(0.0, M["felt"] - over * M.get("felt_last_rate", 1.0))
            last = M["choices"][-1]["option"] if M["choices"] else None
            if last == "doze":
                M["dozed"] = max(0.0, M["dozed"] - over)
            elif last == "rest":
                M["rested"] = max(0.0, M["rested"] - over)
            if self.levels_on:
                self.awake_minutes = max(0.0, round(self.awake_minutes - over, 2))
            M["t"] = minutes
        t, slept, choices, path, calms = M["t"], M["slept"], M["choices"], M["path"], M["calms"]
        walk_mood, st, replays = M["walk_mood"], M["st"], M["replays"]
        if t < minutes and slept is None:
            self.levels_advance(minutes - t)  # leftover minutes (decision cap, or under one step left)
            self._felt_add(M, minutes - t, 0.0)  # v24.0
        self._levels_clock = now
        if not choices:
            return None
        if len(path) >= 2 and walk_mood is None:
            walk_mood = self._idle_apply_walk_mood(path, calms, M["cap"])
        mood, dose, nudge = walk_mood or (("slept" if slept else "rested"), 0.0, 0)
        if path:
            self.idle_focus = st["cur"]
        counts = {k: sum(1 for c in choices if c["option"] == k) for k in self.IDLE_OPTIONS + ("rest",)}
        if any(c["option"] == "speak" for c in choices):  # v23.5.3 (absent when it never spoke up)
            counts["speak"] = sum(1 for c in choices if c["option"] == "speak")
        rec = {"minutes": round(minutes, 1), "steps": max(0, len(path) - 1), "path": path, "new_links": st["new_links"],
               "mood": mood, "jumps": st["jumps"], "replays": replays, "bored": st["bored"], "mood_dose": round(dose, 2),
               "nudge": nudge, "start_calm": round(calms[0], 2) if calms else None,
               "end_calm": round(calms[-1], 2) if calms else None, "when": round(now, 1), "menu": True,
               "counts": counts, "dozed_min": round(M["dozed"], 1), "rested_min": round(M["rested"], 1),
               "slept_hours": slept, "choices": choices}
        rec["felt"] = self._felt_looking_back(M, minutes, slept, path, st, replays, counts)  # v24.0
        if M["live"]:
            rec["live"] = True
        self.last_idle = rec
        self.idle_this_turn = rec
        self.idle_journal = (self.idle_journal + [{k: v for k, v in rec.items() if k != "choices"}])[-10:]
        return rec

    def _felt_looking_back(self, M, minutes, slept, path, st, replays, counts):
        """v24.0: both felt-time numbers for a closed silence (measured and told only). Events = distinct words reached
        + new links + thoughts back + speak-ups. Usual = this brain's events per awake hour, over awake time only,
        starting at the first silence's own rate. Returns a dict for the idle record."""
        asleep_min = (slept or 0.0) * 60.0
        awake_min = max(0.0, minutes - asleep_min)
        events = (len(set(path[1:])) + len(st["new_links"]) + len(replays) + M.get("first_replay", 0)
                  + counts.get("speak", 0))
        rate, usual, factor = None, self.felt_usual, 1.0
        if awake_min >= self.IDLE_STEP_MIN:
            rate = events / (awake_min / 60.0)
            if usual is None:
                usual = rate  # first silence: its own rate is the usual, and looking back = the clock
            else:
                ratio = rate / max(1.0, usual)  # floor: after empty silences, one event can't look huge
                factor = max(self.FELT_MIN, min(self.FELT_MAX, 0.5 + 0.5 * ratio))
            self.felt_usual = round(usual + self.FELT_USUAL_RATE * (rate - usual), 3) if self.felt_usual is not None else round(rate, 3)
        back = awake_min * factor + asleep_min * self.FELT_MIN
        passing = M.get("felt") if M.get("live") else None
        return {"clock_min": round(minutes, 1), "passing_min": round(passing, 1) if passing is not None else None,
                "looking_back_min": round(back, 1), "events": events,
                "engaged_share": round(M.get("engaged_min", 0.0) / awake_min, 2) if M.get("live") and awake_min > 0 else None,
                "events_per_hour": round(rate, 2) if rate is not None else None,
                "usual_per_hour": round(usual, 2) if usual is not None else None}

    def felt_time_text(self, rec=None, threshold=0.25):
        """Front door (v24.0): one line about how the last silence felt, or "" when both felt numbers are within
        `threshold` of the clock (nothing worth saying)."""
        rec = rec or self.last_idle
        f = (rec or {}).get("felt")
        if not f or not f.get("clock_min"):
            return ""
        clock = f["clock_min"]
        def far(x):
            return x is not None and abs(x - clock) > threshold * clock
        if not (far(f.get("passing_min")) or far(f.get("looking_back_min"))):
            return ""
        def span(m):
            return f"{m:.0f} minutes" if m < 90 else f"{m / 60:.1f} hours"
        parts = []
        if f.get("passing_min") is not None:
            parts.append(f"while it passed it felt like about {span(f['passing_min'])}")
        parts.append(f"looking back it seems like about {span(f['looking_back_min'])}")
        return f"your last time alone was about {span(clock)} by the clock; " + "; ".join(parts)

    def _weighted_pick(self, weights):
        r, acc = self.idle_rng.random() * sum(weights), 0.0
        for i, w in enumerate(weights):
            acc += w
            if acc >= r:
                return i
        return len(weights) - 1

    def idle_choices_text(self, rec=None, limit=12):
        """Front door (v23.4): the idle choices as short lines for /idle, with their reasons."""
        rec = rec or self.last_idle
        if not rec or not rec.get("choices"):
            return []
        out = []
        for c in rec["choices"][:limit]:
            why = "forced: " + c["forced"] if c.get("forced") else ", ".join(c.get("reasons", [])) or "base urge"
            extra = f" '{' '.join(c['episode']['words'][:3])}'" if c.get("episode") else ""
            if c.get("forced") or c["option"] == "rest":
                out.append(f"{c['t']:>5.0f} min  {c['option']}  ({why})")
            else:
                out.append(f"{c['t']:>5.0f} min  {c.get('did', c['option'])}{extra}  ({why}; won by {c['margin']} in {c['ticks']} ticks)")
        if len(rec["choices"]) > limit:
            out.append(f"  ... {len(rec['choices']) - limit} more")
        return out

    def idle_habits_status(self):
        return ", ".join(f"{k} {self.idle_habits.get(k, 0.0):+.2f}" for k in self.IDLE_OPTIONS if k != "sleep") + (
            f", speak {self.idle_habits['speak']:+.2f}" if "speak" in self.idle_habits else "")  # v23.5.3

    def idle_catch_up(self, now=None):
        """Front door: run the wandering for the silence since the last turn. Returns the idle record, or None.
        v22.9: the walk no longer becomes the user's last topic (it ends in idle_focus); a step links the word it actually
        came from; a repeat within the walk is boredom, so it leaps to a known word it resembles; the escape counts tense
        steps over a window and uses sleep's comfort bridge (habituation, told words only); the mood dose follows the
        walk's own words."""
        self.idle_this_turn = None
        now = self.now() if now is None else now
        if self._menu is not None:  # v23.5: a live silence is open: spend what's still due, then close it
            self._live_advance(now)
            rec = self._idle_menu_finish(now)
            self.last_turn_time = now  # v24.0: closed from any door (/live off, /sleep, /read...), it counts once
            return rec
        if self._idle_menu_ready(now):
            return self._idle_menu(now)  # v23.4
        if not self.idle_on or self.last_turn_time is None:
            return None
        minutes = (now - self.last_turn_time) / 60.0
        if minutes < self.IDLE_MIN_GAP:
            return None
        steps = min(self.IDLE_MAX_STEPS, int(minutes // self.IDLE_MIN_PER_STEP))
        cur = self.last_topic
        if not cur or (cur not in self.assoc_graph and cur not in self.vectors):
            return None  # v22.9: a topic with no links can still remind the brain of something (a leap, below)
        self.idle_visits = {w: v * self.IDLE_VISIT_DECAY for w, v in self.idle_visits.items() if v * self.IDLE_VISIT_DECAY >= 0.05}
        restore = self.IDLE_RESTORE_NIGHTMARE if self.nightmare_mode else self.IDLE_RESTORE
        path, calms, new_links, jumps, bored = [cur], [self._idle_calm(cur)], [], [], 0
        old_src = self.set_wire_source("idle")
        old_gain, self.turn_learning_gain = self.turn_learning_gain, 1.0  # last turn's surprise doesn't scale idle links
        old_awake, self.awake_turn = self.awake_turn, True  # idle is waking time (also when run at /exit)
        try:
            st = {"cur": cur, "path": path, "calms": calms, "new_links": new_links, "jumps": jumps, "bored": 0,
                  "restore": restore}
            for i in range(steps):
                st["i"] = i
                if not self._idle_walk_step(st):
                    break
            cur, bored = st["cur"], st["bored"]
        finally:
            self.set_wire_source(old_src)
            self.turn_learning_gain = old_gain
            self.awake_turn = old_awake
        if len(path) < 2:
            return None
        walked = calms[1:]
        mean_calm = sum(walked) / len(walked)
        end_tense = walked[-1] < self.IDLE_TENSE
        if mean_calm < self.IDLE_TENSE and end_tense:
            mood = "ruminated"
        elif calms[0] < self.IDLE_TENSE and not end_tense:
            mood = "settled"
        elif mean_calm > 0.5:
            mood = "calm"
        else:
            mood = "drifted"
        # v22.9 mood dose: follows the walk's own words (a tense walk pushes down), sized by how calm or tense it was.
        # With the mood level on it's a fractional dose into the calm level, which clears like the rest of it; with the
        # mood level off it's a whole step only when the walk was clearly calm or tense (|dose| >= 0.5).
        dose = max(-1.0, min(1.0, mean_calm / self.IDLE_MOOD_SCALE))
        if self.levels_on:  # v23.3: the dose goes into the valence level (a dose of 1 = one cell = 1/3 of valence)
            self._set_valence(self._valence_now() + dose / self.VALENCE_CELLS)
            nudge = round(dose, 2)
        elif self.mood_active():
            level = max(0.0, min(6.0, self.seed_a + self.a_level_resid + dose))
            self.seed_a = int(math.floor(level + 0.5))
            self.a_level_resid = round(level - self.seed_a, 4)
            nudge = round(dose, 2)
        else:
            nudge = 1 if dose >= 0.5 else (-1 if dose <= -0.5 else 0)
            self.seed_a = max(0, min(6, self.seed_a + nudge))  # at most one step, never wraps
        if self.levels_on and dose < 0:  # v23: a ruminating walk leaves the brain more aroused
            self.arousal = round(min(1.0, self.arousal + self.AROUSAL_IDLE * -dose), 4)
        self.idle_focus = cur  # v22.9: NOT last_topic, so "It leads to X" and "Okay." stay about what the user said
        rec = {"minutes": round(minutes, 1), "steps": len(path) - 1, "path": path, "new_links": new_links, "mood": mood,
               "jumps": jumps, "bored": bored, "mood_dose": round(dose, 2), "nudge": nudge,
               "start_calm": round(calms[0], 2), "end_calm": round(walked[-1], 2), "when": round(now, 1)}
        self.last_idle = rec
        self.idle_this_turn = rec
        self.idle_journal = (self.idle_journal + [rec])[-10:]
        return rec

    SURPRISE_WORD_SHARE = 0.6    # rest = how far the calm/tense level moved from what it expected
    SURPRISE_GAIN_SPAN = 0.8
    SURPRISE_GAIN_MIN, SURPRISE_GAIN_MAX = 0.5, 1.5
    SURPRISE_BASELINE_RATE = 0.05  # how fast "normal surprise" adapts (a long run of sameness slowly becomes normal)
    CALM_TREND_RATE = 0.5          # how fast the expected calm/tense level follows the conversation
    EXPECT_LINKS_PER_WORD = 5

    def turn_calm_level(self, content):
        """Average calm/tense weight of this turn's words (word weights, or the word's meaning for new words)."""
        vals = []
        for c in content:
            if c in self.word_weights:
                vals.append(self.word_weights[c])
            elif c in self.vectors:
                vals.append(self.axis_weight(self.vectors[c], "A"))
        return sum(vals) / len(vals) if vals else None

    def form_expectation(self, concepts, cell_key, thought_trace=None):
        if not self.cerebellum_on:
            return
        expect = {}
        # fix-queue (2026-11-11): expect the same words measure_surprise checks (first 6 non-stop-words). It used the first
        # 5 raw concepts, so a long sentence repeated exactly still scored word surprise 0.167 (its 6th word was "new").
        for c in [c for c in concepts if c not in self.stop_words][:6]:
            expect[c] = max(expect.get(c, 0.0), 1.0)  # the same topic again is expected
            links = sorted(self.assoc_graph.get(c, {}).items(), key=lambda kv: -kv[1])[:self.EXPECT_LINKS_PER_WORD]
            for nb, wt in links:
                expect[nb] = max(expect.get(nb, 0.0), round(min(1.0, wt / 3.0), 3))
        for w in (thought_trace or {}).get("a_star_path", [])[:4]:
            expect.setdefault(w, 0.5)
        self.expectation = {"words": expect, "cell": cell_key, "calm": getattr(self, "_calm_trend", None)}

    def measure_surprise(self, concepts, cell_key):
        """Compares this turn with last turn's expectation. Sets self.turn_learning_gain. Returns the report dict."""
        self.turn_learning_gain = 1.0
        if not self.cerebellum_on:
            self.last_surprise = None
            return None
        content = [c for c in concepts if c not in self.stop_words][:6]
        if not self.expectation or not content:
            if content and self.expectation is None:
                self._calm_trend = self.turn_calm_level(content)
            self.last_surprise = {"surprise": None, "gain": 1.0, "note": "nothing to compare yet"}
            return self.last_surprise
        exp_w = self.expectation.get("words", {})
        hit = sum(exp_w.get(c, 0.0) for c in content) / len(content)
        word_part = round(1.0 - hit, 3)
        calm_now = self.turn_calm_level(content)
        calm_exp = self.expectation.get("calm")
        if calm_now is None:
            mood_part = 0.0
            self._calm_trend = calm_exp
        elif calm_exp is None:
            mood_part = 0.0
            self._calm_trend = calm_now
        else:
            mood_part = round(min(1.0, abs(calm_now - calm_exp) / 3.0), 3)
            self._calm_trend = calm_exp + self.CALM_TREND_RATE * (calm_now - calm_exp)
        surprise = round(self.SURPRISE_WORD_SHARE * word_part + (1 - self.SURPRISE_WORD_SHARE) * mood_part, 3)
        base = self.surprise_baseline
        gain = 1.0 + self.SURPRISE_GAIN_SPAN * (surprise - base)
        self.turn_learning_gain = round(max(self.SURPRISE_GAIN_MIN, min(self.SURPRISE_GAIN_MAX, gain)), 3)
        self.surprise_baseline = round(base + self.SURPRISE_BASELINE_RATE * (surprise - base), 4)
        unexpected = [c for c in content if exp_w.get(c, 0.0) < 0.3]
        self.last_surprise = {"surprise": surprise, "words": word_part, "mood": mood_part, "baseline": round(base, 3),
                              "gain": self.turn_learning_gain, "unexpected": unexpected[:4]}
        return self.last_surprise

    def surprise_report(self):
        """Short text for status lines, e.g. 'surprise 0.72 (learning x1.18)'."""
        r = self.last_surprise
        if not r or r.get("surprise") is None:
            return ""
        return f"surprise {r['surprise']:.2f} (learning x{r['gain']:.2f})"

    def predict_voice_words(self, concepts, extra_words=()):
        """#2 efference copy: the words the brain expects its voice to use this turn (its concepts, their strongest
        links, and words the bridge hands the model). Measurement only in v1."""
        pred = set(w for w in concepts if w)
        for c in concepts[:5]:
            pred.update(nb for nb, _ in sorted(self.assoc_graph.get(c, {}).items(), key=lambda kv: -kv[1])[:8])
        pred.update(w for w in extra_words if w)
        return pred

    def check_voice(self, reply_concepts, predicted):
        """Share of the reply's content words the brain predicted (its 'self-match'), plus the unpredicted ones."""
        content = [c for c in reply_concepts if c not in self.stop_words]
        if not content:
            return {"selfMatch": None, "unpredicted": []}
        hits = [c for c in content if c in predicted]
        return {"selfMatch": round(len(hits) / len(content), 3), "unpredicted": [c for c in content if c not in predicted][:5]}

    # v22.4 typo rule: a word that isn't in GloVe or the engine's own vocabulary has to be typed by the user in at least
    # TYPO_MIN_SIGHTINGS different turns before it can claim a cell, a crystal or a dream. One-off slips ("somethi",
    # "ypu") stay passing words (their links still form and fade normally); words you really use, quirks included, pass.
    TYPO_MIN_SIGHTINGS = 2

    def _ensure_word_sightings(self):
        if self.word_sightings is None:  # brain from before v22.4: words it already holds count as established
            self.word_sightings = {k: self.TYPO_MIN_SIGHTINGS for k in self.assoc_graph if not self.is_ordinary_word(k)}
        if self.seen_once_on and not self.seen_once_ready:
            # v22.11: from now on ordinary words are counted too; every word this brain already holds counts as established
            for k in set(self.assoc_graph) | set(self.experienced_words):
                self.word_sightings[k] = max(self.word_sightings.get(k, 0), self.TYPO_MIN_SIGHTINGS)
            self.seen_once_ready = True

    def count_word_sightings(self, tokens):
        if not self.raw_glove:  # no GloVe loaded (built-in test vocabulary only): the rule is off
            return
        self._ensure_word_sightings()
        for t in set(tokens):
            if t not in self.stop_words and len(t) >= 3 and (self.seen_once_on or not self.is_ordinary_word(t)):
                self.word_sightings[t] = self.word_sightings.get(t, 0) + 1

    def is_provisional_word(self, w):
        """v22.4: True for a not-yet-established non-dictionary word (see TYPO_MIN_SIGHTINGS).
        v22.11 seen-once rule: ordinary (GloVe) words too, since a slip can be a real word ("I tam cold"). A word the user
        has typed in only one turn so far gets faint links and no cell, crystal, dream or idea; the 2nd turn establishes
        it. The engine's own vocabulary is innate and always established. TORRENT_SEEN_ONCE=0 = the v22.4 rule."""
        if not w or not self.raw_glove:
            return False
        if self.is_ordinary_word(w) and (not self.seen_once_on or w in self.builtin_vocab or w in self.factory_word_weights):
            return False
        if "-" in w and all(self.is_ordinary_word(p) for p in w.split("-") if p):
            return False  # a compound of known words ("slow-burn")
        if w in self.knowledge_facts or w in self.get_identity_tokens():
            return False  # taught words and names count as known
        self._ensure_word_sightings()
        return self.word_sightings.get(w, 0) < self.TYPO_MIN_SIGHTINGS

    def forget_fact(self, word):
        """v22.4: remove a taught fact (e.g. a wrong one like 'sky' = "clear today"). Returns the removed definition, or
        None. The word itself and its links stay; links fade with use like any other."""
        key = str(word).strip().strip("'\"").lower()
        if not key or key.startswith("_") or key not in self.knowledge_facts:
            return None
        return self.knowledge_facts.pop(key)

    def is_ordinary_word(self, w):
        """v21.3: True if w is also a normal word (in GloVe or the engine's own vocabulary), like 'hope' or 'drift'."""
        return w in self.raw_glove or w in self.builtin_vocab or w in self.factory_word_weights

    def name_is_also_word(self, n):
        """v21.3: is this NAME also an ordinary word? The brain's own name: GloVe or the engine's vocabulary ('hope',
        'drift'). A person's name (the user, a dialogue partner): only the engine's own vocabulary, because GloVe is full
        of people's names ('matt' is word #4042) and a person's name is rarely meant as a word."""
        bot = str(self.user_profile.get("bot_name", "")).strip().lower()
        pending = str(self.user_profile.get("pending_bot_name", "")).strip().lower()
        if n in (bot, pending):
            return self.is_ordinary_word(n)
        return n in self.builtin_vocab or n in self.factory_word_weights

    def get_hard_identity_tokens(self):
        """v21.3: names that are never ordinary words (e.g. 'gyre', 'matt' or an invented name). Only these are scrubbed
        from stored cells and crystals; a name like 'hope' can live there as the word it also is."""
        return {n for n in self.all_identity_names() if not self.name_is_also_word(n)}

    def find_names_used_as_words(self, user_text, tokens):
        """v21.3 names vs words. A name that is also an ordinary word counts as a NAME only when it is used as one:
        capitalized mid-sentence ("thanks, Hope"), set off by a comma ("Hope, are you there" / "are you there, hope"),
        right after a greeting or thanks ("good night hope"), or in a naming phrase ("your name is hope").
        Any other use ("I hope so", "Hope is a good thing") is the plain word. Returns the names used as words."""
        amb = {n for n in self.all_identity_names() if n in tokens and self.name_is_also_word(n)}
        if not amb:
            return set()
        user_name = str(self.user_profile.get("user_name", "")).strip().lower()
        greet = {"hi", "hey", "hello", "thanks", "bye", "goodbye", "goodnight", "night", "morning", "dear", "welcome", "yo", "sorry"}
        bot_naming = ("your name is", "i name you", "call yourself", "call you", "named", "called")
        user_naming = ("my name is", "call me", "i am", "i'm", "im", "this is", "it's", "it is")
        word_uses = set()
        for sentence in re.split(r"[.!?\n;:]+", user_text):
            words = list(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)?", sentence))  # v21.3 #8: same splitting as clean_tokens
            low_words = [re.sub(r"['’]s$", "", m.group(0).lower()).replace("'", "").replace("’", "") for m in words]
            for i, m in enumerate(words):
                w = low_words[i]
                if w not in amb:
                    continue
                before, after = sentence[:m.start()], sentence[m.end():]
                pre = " ".join(low_words[:i])
                capital_mid = m.group(0)[0].isupper() and i > 0
                vocative = (i == 0 and after.lstrip().startswith(",")) or (i == len(words) - 1 and before.rstrip().endswith(","))
                greeted = i > 0 and (low_words[i - 1] in greet or pre.endswith("thank you"))
                named = pre.endswith(bot_naming) or (w == user_name and pre.endswith(user_naming))
                if not (capital_mid or vocative or greeted or named):
                    word_uses.add(w)
        return word_uses

    def get_identity_tokens(self, extra_names=None):
        """
        Returns the dynamic set of identity tokens from user_profile, active
        dialogue partner, and known manifold names. v21.3: minus any name that the
        current turn uses as an ordinary word (so "I hope..." keeps the word "hope").
        """
        id_set = self.all_identity_names() - self.turn_word_names
        if extra_names:
            for en in extra_names:
                if en and isinstance(en, str):
                    id_set.add(en.strip().lower())
        return id_set

    def is_identity_query(self, user_text, tokens):
        """
        Returns True if the user's message is explicitly asking about or teaching
        names/identity (allowing identity tokens into cortical/crystal processing).
        """
        word_set = set(tokens)
        if word_set & self.identity_query_triggers:
            return True
        low = user_text.lower()
        return any(p in low for p in ("who are you", "who am i", "what is your name", "what's your name", "my name is", "call me", "call yourself"))

    # =================================================================
    # TOPOLOGICAL CALIBRATION & EMERGENT DREAM-BIRTH NAMING SEQUENCE
    # =================================================================
    def parse_calibration_user_name(self, raw_text):
        if not raw_text:
            return ""
        s = raw_text.strip().lower()
        s = re.sub(r"[^\w\s']", " ", s)
        s = re.sub(r"\s+", " ", s).strip()

        prefixes = [
            "hello ", "hey ", "hi ",
            "my name is ", "call me ", "this is ", "it is ", "it's ", "its ",
            "i am ", "i'm ", "im "
        ]
        changed = True
        while changed:
            changed = False
            for pref in prefixes:
                if s.startswith(pref):
                    s = s[len(pref):].strip()
                    changed = True

        s = re.sub(r"[^a-z0-9\s\-]", "", s).strip()
        if not s:
            return ""
        first_tok = s.split()[0].strip("-")
        if not first_tok or not first_tok.isalpha():
            return ""
        if first_tok in self.stop_words or first_tok in self.factory_word_weights or first_tok in self.generic_hubs:
            return ""
        return first_tok

    def is_usable_name(self, w):
        """v21.3: grammar words ("no", "not", "the"...) and common words ("hello", "night"...) can't work as names."""
        w = (w or "").strip().lower()
        return (w.isalpha() and len(w) >= 2 and w not in self.stop_words and w not in self.negation_tokens
                and w not in self.generic_hubs and w not in self.noise_words)

    def register_bot_name(self, chosen_name):
        clean_cap = chosen_name.strip().capitalize()
        clean_low = clean_cap.lower()
        self.user_profile["bot_name"] = clean_cap
        self.user_profile["pending_bot_name"] = ""
        self.user_profile["pending_name_origin"] = ""
        self.word_weights[clean_low] = round(self.word_weights.get(clean_low, 0.0) + 0.8, 3)
        self.epistemic_weights[clean_low] = round(self.epistemic_weights.get(clean_low, 0.0) + 0.7, 3)
        self.get_or_create_vector(clean_low, context_vec=self.pole_calm)
        self.core_concept_pool.add(clean_low)
        self.knowledge_facts[clean_low] = "my emergent toroidal manifold identity"
        self.save_memory()
        return clean_cap

    def synthesize_emergent_bot_name(self):
        if self.user_profile.get("bot_name") or self.user_profile.get("pending_bot_name"):
            return None

        id_tokens = self.get_identity_tokens()
        basic_verbs = {
            "make", "makes", "take", "takes", "give", "gives", "keep", "keeps",
            "bring", "brings", "lead", "leads", "move", "moves", "work", "works",
            "working", "feel", "feels", "think", "thinks", "know", "knows",
            "learn", "learning", "talk", "talking", "speak", "speaking"
        }

        def is_valid_candidate(w):
            if not w or not isinstance(w, str):
                return False
            wl = w.strip().lower()
            if len(wl) <= 3 or " " in wl:
                return False
            if wl in id_tokens or wl in self.stop_words or wl in self.noise_words or wl in self.lean_up_words() or wl in basic_verbs or wl in self.generic_hubs or wl in self.negation_tokens:
                return False
            if self.word_weights.get(wl, 0.0) < 0.0 and not self.nightmare_mode:  # v22.3: nightmare mode allows dark names
                return False
            return True

        if self.dream_journal:
            for d_entry in reversed(self.dream_journal):
                b_word = str(d_entry.get("bridge", "")).strip().lower()
                t_a = str(d_entry.get("threadA", "")).strip().lower()
                t_b = str(d_entry.get("threadB", "")).strip().lower()
                chosen = None
                if is_valid_candidate(b_word):
                    chosen = b_word
                elif is_valid_candidate(t_a):
                    chosen = t_a
                elif is_valid_candidate(t_b):
                    chosen = t_b
                if chosen:
                    self.user_profile["pending_bot_name"] = chosen.capitalize()
                    self.user_profile["pending_name_origin"] = f"synthesizing '{t_a}' and '{t_b}' through '{b_word}' at Z=6"
                    self.save_memory()
                    return self.user_profile["pending_bot_name"]

        best_word = None
        best_score = -999.0
        best_coord = None

        if self.crystal_lattices:
            for cell_k, c_obj in self.crystal_lattices.items():
                facets = c_obj.get("facets", {})
                omega_words = facets.get("Facet_Omega", {}).get("words", [])
                alpha_words = facets.get("Facet_Alpha", {}).get("words", [])
                for w in omega_words + alpha_words:
                    wl = w.strip().lower()
                    if is_valid_candidate(wl):
                        sc = self.word_weights.get(wl, 0.0) + self.epistemic_weights.get(wl, 0.0) * 0.5 + (2.0 if w in omega_words else 0.0)
                        if sc > best_score:
                            best_score = sc
                            best_word = wl
                            best_coord = cell_k

        if not best_word:
            visited_cells = sorted(
                [(info.get("visits", 0), ck, info) for ck, info in self.cell_lexicon.items() if info.get("visits", 0) > 0 or self.cortical_cells.get(ck)],
                key=lambda x: x[0],
                reverse=True
            )
            for _, ck, info in visited_cells:
                cand_pool = list(info.get("top_words", [])) + list(self.cortical_cells.get(ck, {}).keys())
                for w in cand_pool:
                    wl = w.strip().lower()
                    if is_valid_candidate(wl):
                        sc = self.word_weights.get(wl, 0.0) + self.epistemic_weights.get(wl, 0.0) * 0.5
                        if sc > best_score:
                            best_score = sc
                            best_word = wl
                            best_coord = ck
                if best_word:
                    break

        if best_word and best_coord:
            cell_name = self.cell_lexicon.get(best_coord, {}).get("name", "Balanced-Equilibrium")
            self.user_profile["pending_bot_name"] = best_word.capitalize()
            self.user_profile["pending_name_origin"] = f"settling into cortical cell ({best_coord}) [{cell_name}]"
            self.save_memory()
            return self.user_profile["pending_bot_name"]

        return None

    def resolve_waking_identity_handshake(self, user_reply):
        pending_name = self.user_profile.get("pending_bot_name") or "Manifold"
        low = user_reply.strip().lower()
        low_clean = re.sub(r"[^\w\s']", " ", low)
        low_clean = re.sub(r"\s+", " ", low_clean).strip()
        tokens = low_clean.split()

        # v21.2: a plain "no" / "not yet" declines the name instead of becoming the name "No"
        decline_set = {"no", "nah", "nope", "not", "yet", "now", "later", "skip", "pass", "maybe", "thanks", "thank", "you"}
        if tokens and all(t in decline_set for t in tokens):
            self.user_profile["pending_bot_name"] = ""
            self.user_profile["pending_name_origin"] = ""
            self.save_memory()
            print("[Manifold]: Okay. I'll stay unnamed for now and keep listening for a name that fits.")
            return None

        # v24.1.1: read the answer in this order. (1) a name given in a naming form ("call yourself X", "how about X",
        # "I like X better", "X instead"); (2) hesitation ("not sure", "let me think", "maybe later"): stay unnamed;
        # (3) any clear yes ("yeah I guess", "yes, thank you", "yes it fits"): the proposed name; (4) a lone word that
        # could be a name ("Echo"): that name; (5) anything else: stay unnamed and keep listening (no guessing).
        affirmative_set = {"yes", "yeah", "yep", "yup", "sure", "fits", "perfect", "ok", "okay", "absolutely", "definitely",
                           "love", "like", "great", "good", "nice", "cool", "fine"}
        filler = {"a", "an", "the", "named", "called", "please", "i", "think", "would", "want", "to", "you", "be", "it",
                  "that", "this", "is", "its", "it's", "that's", "thats", "for", "now", "your", "name", "one", "maybe"}
        rename_forms = [r"\bcall yourself\s+([a-z]+)", r"\byour name is\s+([a-z]+)", r"\bhow about\s+([a-z]+)",
                        r"\bwhat about\s+([a-z]+)", r"\bi name you\s+([a-z]+)", r"\bcall you\s+([a-z]+)",
                        r"\bname you\s+([a-z]+)", r"\byou are\s+([a-z]+)", r"\byoure\s+([a-z]+)", r"\byou're\s+([a-z]+)",
                        r"\b(?:like|prefer|love)\s+([a-z]+)\s+(?:better|more|instead)\b", r"\brather\s+(?:have\s+)?([a-z]+)\b",
                        r"\b([a-z]+)\s+instead\b", r"\bgo with\s+([a-z]+)", r"\bbe\s+([a-z]+)\s+instead\b"]
        hesitant = (any(p in low_clean for p in ("not sure", "let me think", "think about it", "i'll think", "ill think",
                                                 "not yet", "maybe later", "dont know", "don't know", "no idea", "unsure",
                                                 "hmm", "later"))
                    or (tokens and all(t in decline_set | {"hmm", "um", "uh", "idk", "unsure"} for t in tokens)))
        named = None
        for rx in rename_forms:
            m = re.search(rx, low_clean)
            if m and m.group(1) not in filler and m.group(1) not in affirmative_set and m.group(1) != pending_name.lower():
                named = m.group(1)
                break
        if named is None and hesitant:
            self.user_profile["pending_bot_name"] = ""
            self.user_profile["pending_name_origin"] = ""
            self.save_memory()
            print("[Manifold]: Okay. I'll stay unnamed for now and keep listening for a name that fits.")
            return None
        no_word = any(t in {"no", "nah", "nope"} for t in tokens)
        if named is None and not no_word and (not tokens or any(t in affirmative_set for t in tokens)
                                              or pending_name.lower() in tokens):
            locked = self.register_bot_name(pending_name)
            print(f"[{locked}]: Identity anchor locked. I am {locked}.")
            return locked
        if named is None:
            rest = [t for t in tokens if t.isalpha() and t not in filler and t not in affirmative_set and t not in decline_set
                    and t not in self.stop_words and t not in {"no", "nah", "nope", "instead", "better", "different"}]
            named = rest[0] if len(rest) == 1 else None
        if named is None:
            self.user_profile["pending_bot_name"] = ""
            self.user_profile["pending_name_origin"] = ""
            self.save_memory()
            print("[Manifold]: I'm not sure which name you mean, so I'll stay unnamed for now and keep listening.")
            return None
        chosen_name = named
        if not self.is_usable_name(chosen_name):
            self.user_profile["pending_bot_name"] = ""
            self.user_profile["pending_name_origin"] = ""
            self.save_memory()
            print(f"[Manifold]: '{chosen_name}' works better as a word than as a name, so I'll stay unnamed for now.")
            return None
        locked = self.register_bot_name(chosen_name)
        print(f"[{locked}]: Identity anchor recalibrated. I am {locked}.")
        return locked

    def run_boot_calibration_and_handshake(self):
        if not self.user_profile.get("user_name"):
            print("\n[Unanchored Manifold — Coordinate (3,3,3)]. No origin tether detected. Who is calibrating this space?")
            extracted_name = ""
            first_attempt = True
            while not extracted_name:
                try:
                    prompt_str = "👤 You: " if first_attempt else "Please provide a name or handle to anchor the origin tether: "
                    raw_in = input(prompt_str).strip()
                except (KeyboardInterrupt, EOFError):
                    extracted_name = "traveler"
                    break
                first_attempt = False
                extracted_name = self.parse_calibration_user_name(raw_in)
                if extracted_name and len(extracted_name) < 3:  # v24.1: a 2-letter name couldn't be linked or saved
                    print("Names need at least 3 letters here (for 'Jo', try 'Joe' or 'Jojo').")
                    extracted_name = ""

            self.user_profile["user_name"] = extracted_name
            self.word_weights[extracted_name] = 2.5
            self.social_weights[extracted_name] = 2.5
            self.epistemic_weights[extracted_name] = 0.5
            self.get_or_create_vector(extracted_name, context_vec=self.pole_social)
            self.core_concept_pool.add(extracted_name)
            self.knowledge_facts[extracted_name] = "my creator and conversational anchor"
            # Anchor origin identity specifically at the (3,3,3) origin tether cell
            self.cortical_cells.setdefault("3,3,3", {})[extracted_name] = self.cortical_cells.get("3,3,3", {}).get(extracted_name, 0) + 1
            self.wire_concepts(extracted_name, "friend", 3.0, source="engine")
            self.wire_concepts(extracted_name, "learn", 2.5, source="engine")
            self.save_memory()
            print(f"Origin tether locked to '{extracted_name.capitalize()}'. Manifold online.")

        if not self.user_profile.get("bot_name") and self.user_profile.get("pending_bot_name"):
            u_cap = self.user_profile.get("user_name", "Friend").capitalize()
            p_name = self.user_profile["pending_bot_name"]
            p_origin = self.user_profile.get("pending_name_origin") or "an emergent harmonic attractor"
            print(f"\n[Manifold]: Hello {u_cap}. During stasis consolidation, my topology kept returning to {p_origin}. I feel like my name might be '{p_name}'. Does that name fit this manifold, or do you have a different name for me? (Say 'no' to leave me unnamed for now.)")
            try:
                ans = input(f"👤 {u_cap}: ").strip()
            except (KeyboardInterrupt, EOFError):
                ans = "yes"
            self.resolve_waking_identity_handshake(ans)

    def recompute_poles_and_coords(self):
        self.pole_calm = self.phrase_to_vector("calm logic clear peace steady grounded safe happy working incredible amazed cooperation love harmony")
        self.pole_panic = self.phrase_to_vector("panic scared fear worry stress tense overwhelm fail loss threat dangerous")
        self.pole_social = self.phrase_to_vector("we together talk share connect cooperative cooperation open friend love empathy trust")
        self.pole_isolated = self.phrase_to_vector("alone guarded closed defensive hesitant solitary hide separate")
        self.pole_abstract = self.phrase_to_vector("wisdom insight pattern structure theory system concept meaning philosophy synthesis counterfactual")
        self.pole_concrete = self.phrase_to_vector("touch see hand step moment ground water rain stone body action")
        self.coord_vectors = self.build_coordinate_vectors()

    # =================================================================
    # UPGRADE 2.1: COMPOUND & CONTEXTUAL OOV FACTORY VECTOR TETHER
    # =================================================================
    def compute_contextual_oov_vector(self, word, context_vec=None):
        """
        Generates a manifold-aligned 50D vector for an Out-Of-Vocabulary (OOV) word:
          1. If hyphenated (e.g. 'steady-harmony'), averages any known sub-word vectors.
          2. Otherwise blends 80% context/cell centroid vector + 20% deterministic hash vector.
        """
        w = word.strip().lower()
        if "-" in w:
            sub_parts = [p.strip() for p in w.split("-") if p.strip()]
            sub_vecs = [self.vectors[p] for p in sub_parts if p in self.vectors]
            if sub_vecs:
                return self.average_vectors(sub_vecs)

        hash_vec = self.expand_coords_to_50d(0.0, 0.0, word=w)
        anchor_vec = None
        if context_vec is not None and any(abs(x) > 1e-6 for x in context_vec):
            anchor_vec = self.normalize(context_vec)
        elif hasattr(self, "cell_centroids") and self.cell_centroids:
            seed_key = f"{self.seed_s},{self.seed_a},{self.seed_z}"
            anchor_vec = self.cell_centroids.get(seed_key)
        if not anchor_vec and hasattr(self, "pole_calm"):
            anchor_vec = self.pole_calm

        if anchor_vec and any(abs(x) > 1e-6 for x in anchor_vec):
            return self.blend(anchor_vec, hash_vec, w1=0.80, w2=0.20)
        return hash_vec

    # v24.1: facts the engine writes itself (identity anchors), not taught by anyone; the bridge doesn't show them to
    # the voice as taught facts
    ENGINE_FACT_TEXTS = ("my creator and conversational anchor", "my emergent toroidal manifold identity")

    def is_engine_fact(self, key):
        """Front door (v24.1): True when the stored fact for `key` was written by the engine, not taught."""
        return str(self.knowledge_facts.get(key, "")) in self.ENGINE_FACT_TEXTS

    def get_factory_vector(self, word, context_vec=None):
        w = word.strip().lower()
        if w not in self.factory_vectors:
            self.factory_vectors[w] = list(self.compute_contextual_oov_vector(w, context_vec=context_vec))
        return self.factory_vectors[w]

    def enforce_factory_tether(self, word, vec):
        f_vec = self.get_factory_vector(word, context_vec=vec)
        vec = self.normalize(vec)
        if self.dot(vec, f_vec) < 0.78:
            vec = self.blend(vec, f_vec, 0.75, 0.25)
        return vec

    def apply_dialectical_repulsion(self, w1, w2, rate=0.06):
        if not w1 or not w2 or w1 == w2 or w1 not in self.vectors or w2 not in self.vectors:
            return
        u = list(self.vectors[w1])
        v = list(self.vectors[w2])
        u_pushed = self.normalize([ux - rate * vx for ux, vx in zip(u, v)])
        v_pushed = self.normalize([vx - rate * ux for ux, vx in zip(u, v)])
        self.vectors[w1] = self.enforce_factory_tether(w1, u_pushed)
        self.vectors[w2] = self.enforce_factory_tether(w2, v_pushed)

    # =================================================================
    # 1. PURITY FILTERING & DISJOINT 4-FACET CRYSTALLINE SUB-LATTICES
    # =================================================================
    HUB_DEGREE_PERCENTILE = 0.90  # v21.8: a word whose link count is in the top 10% counts as a hub

    def hub_degree_cut(self):
        """v21.8: the link count above which a word counts as a hub for crystals. It was a fixed 18, but links never
        drop below their 0.25 floor, so every word's link count only grows: in a 73-day test the number of 'hubs'
        went from 218 (day 20) to 529 (day 73) and crystals drifted down. Now the cut is the 90th percentile of all
        words' link counts (like a lab reference range), recomputed whenever the number of words changes."""
        n = len(self.assoc_graph)
        if getattr(self, "_hub_cut_n", None) != n:
            degs = sorted(len(links) for links in self.assoc_graph.values())
            self._hub_cut = degs[int(self.HUB_DEGREE_PERCENTILE * (len(degs) - 1))] if degs else 18
            self._hub_cut_n = n
        return self._hub_cut

    def is_crystal_pure_concept(self, word, cell_key=None, allow_identity=False):
        if not word or len(word) < 3 or " " in word:
            return False
        w = word.lower().strip()
        if w in self.stop_words or w in self.noise_words or w in self.generic_hubs:
            return False
        if self.is_provisional_word(w):
            return False  # v22.4 typo rule
        # UPGRADE 1.3: Block identity tokens from crystals except at (3,3,3) or during explicit identity queries
        # v21.3: only names that are never ordinary words; a stored "hope" is the word hope
        if not allow_identity and cell_key != "3,3,3" and w in self.get_hard_identity_tokens():
            return False
        if "-" in w:
            return True
        deg = len(self.assoc_graph.get(w, {}))
        if deg > self.hub_degree_cut():  # v21.8: relative (top 10% of degrees), was a fixed 18
            if abs(self.epistemic_weights.get(w, 0.0)) < 1.8 and abs(self.word_weights.get(w, 0.0)) < 2.2:
                return False
        return True

    def compute_facet_tension(self, words_list):
        vecs = [self.vectors[w] for w in words_list if w in self.vectors]
        if len(vecs) < 2:
            return 0.08
        sub_c = self.average_vectors(vecs)
        avg_sim = sum(self.dot(v, sub_c) for v in vecs) / float(len(vecs))
        return round(max(0.0, min(1.0, 1.0 - avg_sim)), 3)

    def nucleate_or_update_crystal(self, cell_key, force_virtual=False, allow_identity=False):
        cell_key = self.normalize_cell_key(cell_key)
        words_map = self.cortical_cells.get(cell_key, {})
        pure_words = [
            w for w, _ in sorted(words_map.items(), key=lambda x: x[1], reverse=True)
            if self.is_crystal_pure_concept(w, cell_key=cell_key, allow_identity=allow_identity) and w in self.vectors
        ]
        visits = self.cell_lexicon.get(cell_key, {}).get("visits", 0)

        if not force_virtual and (len(pure_words) < 5 or visits < 2):
            return self.crystal_lattices.get(cell_key)

        s_c, a_c, z_c = [int(x) for x in cell_key.split(",")]
        cell_c = self.cell_centroids.get(cell_key, self.coord_vectors[(s_c, a_c, z_c)])

        if len(pure_words) < 4:
            supplements = sorted(
                [
                    (self.dot(cell_c, self.vectors[w]), w)
                    for w in self.core_concept_pool
                    if self.is_crystal_pure_concept(w, cell_key=cell_key, allow_identity=allow_identity)
                    and w not in pure_words and w in self.vectors and self.word_is_trusted(w)  # v22.7
                ],
                key=lambda x: x[0], reverse=True
            )
            for _, sw in supplements:
                if all(not self.same_stem(sw, ew) for ew in pure_words):
                    pure_words.append(sw)
                if len(pure_words) >= 6:
                    break

        sig_alpha = self.blend(cell_c, self.blend(self.pole_calm, self.pole_concrete, 0.6, 0.4), 0.65, 0.35)
        vel_vec = self.blend(self.pole_social if self.vel_s >= 0 else self.pole_isolated, self.pole_abstract if self.vel_z >= 0 else self.pole_concrete, 0.5, 0.5)
        sig_beta = self.blend(self.pole_social, vel_vec, 0.60, 0.40)
        sig_gamma = self.blend(self.pole_abstract, self.pole_panic, 0.65, 0.35)

        buckets = {"Facet_Alpha": [], "Facet_Beta": [], "Facet_Gamma": []}
        # v22.6.3: words annealing demoted out of Alpha stay demoted when the crystal is rebuilt (before, every rebuild put
        # them back, so the same "annealing relief" fired every turn and the strain kept climbing)
        demoted = set((self.crystal_lattices.get(cell_key) or {}).get("demoted", []))
        demoted |= set(self.saved_demoted.get(cell_key, ()))  # v22.6.4: lists saved last session (crystals aren't loaded)
        for w in pure_words:
            vw = self.vectors[w]
            if w in demoted:
                buckets["Facet_Gamma"].append(w)
                continue
            scores = [
                (self.dot(vw, sig_alpha), "Facet_Alpha"),
                (self.dot(vw, sig_beta), "Facet_Beta"),
                (self.dot(vw, sig_gamma), "Facet_Gamma")
            ]
            scores.sort(key=lambda x: x[0], reverse=True)
            buckets[scores[0][1]].append(w)

        claimed_leads = set()
        for f_name, sig_v in (("Facet_Alpha", sig_alpha), ("Facet_Beta", sig_beta), ("Facet_Gamma", sig_gamma)):
            distinct_in_bucket = [w for w in buckets[f_name] if w not in claimed_leads and all(not self.same_stem(w, cl) for cl in claimed_leads)]
            if distinct_in_bucket:
                buckets[f_name] = distinct_in_bucket + [w for w in buckets[f_name] if w not in distinct_in_bucket]
                claimed_leads.add(distinct_in_bucket[0])
            else:
                avail = [w for w in pure_words if w not in claimed_leads and all(not self.same_stem(w, cl) for cl in claimed_leads)] or pure_words
                if f_name == "Facet_Alpha":  # v22.6.4: the fallback lead for an empty Alpha skips demoted words too
                    avail = [w for w in avail if w not in demoted] or avail
                best_w = max(avail, key=lambda w: self.dot(self.vectors[w], sig_v))
                buckets[f_name] = [best_w] + [w for w in buckets[f_name] if w != best_w]
                claimed_leads.add(best_w)

        c_alpha = self.average_vectors([self.vectors[w] for w in buckets["Facet_Alpha"]])
        c_beta = self.average_vectors([self.vectors[w] for w in buckets["Facet_Beta"]])
        c_gamma = self.average_vectors([self.vectors[w] for w in buckets["Facet_Gamma"]])

        omega_scored = []
        for w in pure_words:
            vw = self.vectors[w]
            tri_sim = self.dot(vw, c_alpha) + self.dot(vw, c_beta) + self.dot(vw, c_gamma) + 0.35 * self.dot(vw, self.pole_abstract)
            omega_scored.append((tri_sim + 0.08 * self.word_salience(w), w))
        omega_scored.sort(key=lambda x: x[0], reverse=True)
        omega_words = [w for _, w in omega_scored[:2]] or [pure_words[0]]
        c_omega = self.average_vectors([self.vectors[w] for w in omega_words])

        facets_data = {
            "Facet_Alpha": {"words": buckets["Facet_Alpha"][:8], "centroid": [round(x, 4) for x in c_alpha], "tension": self.compute_facet_tension(buckets["Facet_Alpha"])},
            "Facet_Beta": {"words": buckets["Facet_Beta"][:8], "centroid": [round(x, 4) for x in c_beta], "tension": self.compute_facet_tension(buckets["Facet_Beta"])},
            "Facet_Gamma": {"words": buckets["Facet_Gamma"][:8], "centroid": [round(x, 4) for x in c_gamma], "tension": self.compute_facet_tension(buckets["Facet_Gamma"])},
            "Facet_Omega": {"words": omega_words, "centroid": [round(x, 4) for x in c_omega], "tension": self.compute_facet_tension(omega_words)}
        }

        alpha_gamma_shear = round(max(0.0, min(1.0, (1.0 - self.dot(c_alpha, c_gamma)) * 0.55)), 3)
        overall_pure_tension = self.compute_facet_tension(pure_words)
        max_shear = max([f["tension"] for f in facets_data.values()] + [alpha_gamma_shear, overall_pure_tension])

        crystal_obj = {
            "cell": cell_key,
            "crystallized": not force_virtual,
            "total_pure": len(pure_words),
            "shear_stress": round(max_shear, 3),
            "facets": facets_data
        }
        if demoted:
            crystal_obj["demoted"] = sorted(demoted & set(pure_words))
        if not force_virtual:
            self.saved_demoted.pop(cell_key, None)  # v22.6.4: the stored crystal now carries its own list
        if not force_virtual:
            self.crystal_lattices[cell_key] = crystal_obj
        return crystal_obj

    def build_crystal_lattice(self, cell_key, force_virtual=False):
        return self.nucleate_or_update_crystal(cell_key, force_virtual=force_virtual)

    # =================================================================
    # UPGRADE 2.2: NREM FACET_ALPHA STRESS RELIEF (ANNEALING)
    # =================================================================
    def anneal_crystal_facet_alpha(self, cell_key, notify=True):
        """
        Inspects a crystal in crystal_lattices during NREM annealing:
          1. Strips any legacy identity_tokens from non-(3,3,3) facets.
          2. If Facet_Alpha has tension > 0.55 and len(words) > 2, identifies the single
             outlier word with the lowest cosine similarity to the rest of Facet_Alpha,
             demotes it into Facet_Gamma, and recomputes facet centroids & shear_stress.
        """
        cell_key = self.normalize_cell_key(cell_key)
        crystal = self.crystal_lattices.get(cell_key)
        if not crystal:
            return None

        facets = crystal.get("facets", {})
        id_tokens = self.get_hard_identity_tokens()  # v21.3: don't scrub names that are also ordinary words

        if cell_key != "3,3,3":
            for f_name in ("Facet_Alpha", "Facet_Beta", "Facet_Gamma", "Facet_Omega"):
                f_words = facets.get(f_name, {}).get("words", [])
                cleaned_f = [w for w in f_words if w not in id_tokens]
                if cleaned_f != f_words and cleaned_f:
                    facets[f_name]["words"] = cleaned_f
            cell_map = self.cortical_cells.get(cell_key, {})
            for id_w in list(cell_map.keys()):
                if id_w in id_tokens:
                    cell_map.pop(id_w, None)

        alpha_info = facets.get("Facet_Alpha", {})
        gamma_info = facets.get("Facet_Gamma", {})
        alpha_words = [w for w in alpha_info.get("words", []) if w in self.vectors]

        # Re-sync tension after any identity token cleanup
        old_tension = self.compute_facet_tension(alpha_words)
        alpha_info["tension"] = old_tension
        old_shear = crystal.get("shear_stress", 0.0)

        if old_tension <= 0.55 or len(alpha_words) <= 2:
            return None

        # Find the single outlier word in Facet_Alpha with lowest cosine similarity to the rest of Facet_Alpha
        outlier_word = None
        lowest_sim = 999.0
        for w in alpha_words:
            other_vecs = [self.vectors[ow] for ow in alpha_words if ow != w and ow in self.vectors]
            if not other_vecs:
                continue
            rest_centroid = self.average_vectors(other_vecs)
            sim = self.dot(self.vectors[w], rest_centroid)
            if sim < lowest_sim:
                lowest_sim = sim
                outlier_word = w

        if not outlier_word:
            return None

        new_alpha_words = [w for w in alpha_words if w != outlier_word]
        crystal["demoted"] = sorted(set(crystal.get("demoted", [])) | {outlier_word})  # v22.6.3: remembered on rebuild
        gamma_words = list(gamma_info.get("words", []))
        if outlier_word not in gamma_words:
            gamma_words = [outlier_word] + gamma_words

        c_alpha = self.average_vectors([self.vectors[w] for w in new_alpha_words if w in self.vectors])
        c_beta = self.average_vectors([self.vectors[w] for w in facets["Facet_Beta"]["words"] if w in self.vectors])
        c_gamma = self.average_vectors([self.vectors[w] for w in gamma_words if w in self.vectors])

        alpha_info["words"] = new_alpha_words[:8]
        alpha_info["centroid"] = [round(x, 4) for x in c_alpha]
        alpha_info["tension"] = self.compute_facet_tension(alpha_info["words"])

        gamma_info["words"] = gamma_words[:8]
        gamma_info["centroid"] = [round(x, 4) for x in c_gamma]
        gamma_info["tension"] = self.compute_facet_tension(gamma_info["words"])

        all_pure = list(dict.fromkeys(
            alpha_info["words"] + facets["Facet_Beta"]["words"] + gamma_info["words"]
        ))
        omega_scored = []
        for w in all_pure:
            if w in self.vectors:
                vw = self.vectors[w]
                tri_sim = self.dot(vw, c_alpha) + self.dot(vw, c_beta) + self.dot(vw, c_gamma) + 0.35 * self.dot(vw, self.pole_abstract)
                omega_scored.append((tri_sim + 0.08 * self.word_salience(w), w))
        omega_scored.sort(key=lambda x: x[0], reverse=True)
        omega_words = [w for _, w in omega_scored[:2]] or [new_alpha_words[0]]
        c_omega = self.average_vectors([self.vectors[w] for w in omega_words if w in self.vectors])

        facets["Facet_Omega"]["words"] = omega_words
        facets["Facet_Omega"]["centroid"] = [round(x, 4) for x in c_omega]
        facets["Facet_Omega"]["tension"] = self.compute_facet_tension(omega_words)

        alpha_gamma_shear = round(max(0.0, min(1.0, (1.0 - self.dot(c_alpha, c_gamma)) * 0.55)), 3)
        overall_pure_tension = self.compute_facet_tension(all_pure)
        new_shear = round(max([f["tension"] for f in facets.values()] + [alpha_gamma_shear, overall_pure_tension]), 3)
        crystal["shear_stress"] = new_shear
        crystal["total_pure"] = len(all_pure)

        msg = (
            f"🔧 [ANNEALING RELIEF] Cell ({cell_key}): Demoted outlier '{outlier_word}' "
            f"(sim={lowest_sim:+.2f}) from Facet_Alpha -> Facet_Gamma "
            f"(Alpha tension {old_tension:.2f} -> {alpha_info['tension']:.2f} | shear {old_shear:.3f} -> {new_shear:.3f})."
        )
        if notify:
            if self.show_tectonics:
                print(f"\n{msg}")
            else:
                self._quiet_tectonics["relief"] += 1
        return msg

    # =================================================================
    # TASK 4: TRUE MITOSIS CRYSTAL CLEAVAGE (26 TOROIDAL NEIGHBORS)
    # =================================================================
    def cleave_crystal(self, cell_key, notify=True):
        cell_key = self.normalize_cell_key(cell_key)
        crystal = self.crystal_lattices.get(cell_key)
        if not crystal:
            return None

        total_pure = crystal.get("total_pure", 0)
        shear_stress = crystal.get("shear_stress", 0.0)
        if not ((total_pure >= 7 and shear_stress >= 0.25) or total_pure >= 8):
            return None

        facets = crystal["facets"]
        alpha_cent = facets["Facet_Alpha"]["centroid"]
        gamma_words = [
            w for w in facets["Facet_Gamma"]["words"]
            if w in self.cortical_cells.get(cell_key, {}) and w in self.vectors
        ]
        resting = (lambda w: self.mood_active() and self.turn_counter - self.split_rest.get(w, -10**9) < self.SPLIT_REST_TURNS)
        gamma_words = [w for w in gamma_words if not resting(w)]  # v22.6 split rest: recently split words stay put
        if not gamma_words:
            all_cell_pure = [
                w for w in self.cortical_cells.get(cell_key, {})
                if self.is_crystal_pure_concept(w, cell_key=cell_key) and w in self.vectors and not resting(w)
            ]
            if len(all_cell_pure) < 7:
                return None
            gamma_words = all_cell_pure

        strained = sorted([(self.dot(self.vectors[w], alpha_cent), w) for w in gamma_words], key=lambda x: x[0])
        split_cnt = 2 if (total_pure >= 8 or len(strained) >= 2) else 1
        cleaved_words = [w for _, w in strained[:split_cnt]]
        if not cleaved_words:
            return None
        if self.mood_active():
            for w in cleaved_words:
                self.split_rest[w] = self.turn_counter

        gamma_cent = facets["Facet_Gamma"]["centroid"]
        if not any(abs(x) > 1e-6 for x in gamma_cent):
            gamma_cent = self.average_vectors([self.vectors[w] for w in cleaved_words])

        s0, a0, z0 = [int(x) for x in cell_key.split(",")]
        best_neighbor = None
        best_score = -999.0
        for ds in (-1, 0, 1):
            for da in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if ds == 0 and da == 0 and dz == 0:
                        continue
                    nk = f"{self.mod7(s0 + ds)},{self.mod7(a0 + da)},{self.mod7(z0 + dz)}"
                    n_pure_cnt = sum(1 for w in self.cortical_cells.get(nk, {}) if self.is_crystal_pure_concept(w, cell_key=nk))
                    if n_pure_cnt >= 7:
                        continue
                    n_cent = self.cell_centroids.get(nk, self.coord_vectors[(self.mod7(s0 + ds), self.mod7(a0 + da), self.mod7(z0 + dz))])
                    sim = self.dot(gamma_cent, n_cent)
                    uncrystallized_bonus = 0.08 if nk not in self.crystal_lattices else 0.0
                    score = sim + uncrystallized_bonus - (n_pure_cnt * 0.02)
                    if score > best_score:
                        best_score = score
                        best_neighbor = nk

        if not best_neighbor:
            best_neighbor = f"{self.mod7(s0 + 1)},{self.mod7(a0 + 1)},{self.mod7(z0 + 1)}"

        self.cortical_cells.setdefault(best_neighbor, {})
        for cw in cleaved_words:
            cnt = self.cortical_cells.get(cell_key, {}).pop(cw, 1)
            self.cortical_cells[best_neighbor][cw] = self.cortical_cells[best_neighbor].get(cw, 0) + max(1, cnt)

        ps, pa, pz = [int(x) for x in cell_key.split(",")]
        ts, ta, tz = [int(x) for x in best_neighbor.split(",")]
        self.cell_lexicon[best_neighbor]["visits"] = max(2, self.cell_lexicon[best_neighbor].get("visits", 0) + 1)

        parent_rem_words = self.strongest_cell_words(cell_key)  # v22.7.1: strongest, not oldest
        self.update_cell_centroid_and_emotion(ps, pa, pz, parent_rem_words, allow_cleave=False, count_visit=False)
        self.update_cell_centroid_and_emotion(ts, ta, tz, cleaved_words, allow_cleave=False, count_visit=False)

        parent_c = self.nucleate_or_update_crystal(cell_key, force_virtual=True)
        if sum(1 for w in self.cortical_cells.get(cell_key, {}) if self.is_crystal_pure_concept(w, cell_key=cell_key)) >= 5:
            self.crystal_lattices[cell_key] = parent_c
        else:
            self.crystal_lattices.pop(cell_key, None)

        sister_c = self.nucleate_or_update_crystal(best_neighbor, force_virtual=True)
        if sum(1 for w in self.cortical_cells.get(best_neighbor, {}) if self.is_crystal_pure_concept(w, cell_key=best_neighbor)) >= 5:
            sister_c["crystallized"] = True
            self.crystal_lattices[best_neighbor] = sister_c

        p_omega = parent_c["facets"]["Facet_Omega"]["words"][0] if parent_c["facets"]["Facet_Omega"]["words"] else cleaved_words[0]
        s_alpha = sister_c["facets"]["Facet_Alpha"]["words"][0] if sister_c["facets"]["Facet_Alpha"]["words"] else cleaved_words[-1]
        self.wire_concepts(p_omega, s_alpha, amount=1.2, source="engine")

        event = {
            "timestamp": round(self.now(), 2),
            "from_cell": cell_key,
            "to_cell": best_neighbor,
            "parent_cell": cell_key,
            "sister_cell": best_neighbor,
            "fault_facet": "Facet_Gamma",
            "cleaved_words": cleaved_words,
            "shear_stress": round(shear_stress, 3),
            "vein": f"{p_omega} <-> {s_alpha}",
            "summary": f"Cleaved Facet_Gamma {cleaved_words} (shear={shear_stress:.3f}) from ({cell_key}) -> Daughter Cell ({best_neighbor}) via vein '{p_omega} <-> {s_alpha}'."
        }
        self.cleavage_log.append(event)
        self.cleavage_log = self.cleavage_log[-30:]
        if notify:
            if self.show_tectonics:
                print(f"\n🌋 [CRYSTAL CLEAVAGE MITOSIS] {event['summary']}")
            else:
                self._quiet_tectonics["cleave"] += 1
        return event

    def tectonics_note(self):
        """Front door (v23.2): one line summing up the cleavages/annealing hidden since the last call, or None."""
        q = self._quiet_tectonics
        if self.show_tectonics or not (q["cleave"] or q["relief"]):
            q["cleave"] = q["relief"] = 0
            return None
        parts = ([f"{q['cleave']} cleavage{'s' if q['cleave'] != 1 else ''}"] if q["cleave"] else []) + \
                ([f"{q['relief']} annealing relief{'s' if q['relief'] != 1 else ''}"] if q["relief"] else [])
        q["cleave"] = q["relief"] = 0
        return f"🌋 {' and '.join(parts)} (/tectonics to show each one)"

    def set_tectonics(self, on):
        self.show_tectonics = bool(on)
        return self.show_tectonics

    def run_crystal_annealing_and_tectonics(self):
        logs = []
        cleaved_this_pass = set()

        # First, anneal existing crystals (Upgrade 2.2: Facet_Alpha stress relief). Cells that the loop below rebuilds
        # from scratch are annealed silently here and reported only after their final rebuild: before v21.5 the same
        # demotion was printed twice per pass and then undone by the rebuild, so the log described a state never saved.
        for ck in list(self.crystal_lattices.keys()):
            wm = self.cortical_cells.get(ck, {})
            rebuilt_below = (sum(1 for w in wm if self.is_crystal_pure_concept(w, cell_key=ck)) >= 5
                             and self.cell_lexicon.get(ck, {}).get("visits", 0) >= 2)
            anneal_msg = self.anneal_crystal_facet_alpha(ck, notify=not rebuilt_below)
            if anneal_msg and not rebuilt_below:
                logs.append(anneal_msg)

        for cell_k, words_map in list(self.cortical_cells.items()):
            pure_cnt = sum(1 for w in words_map if self.is_crystal_pure_concept(w, cell_key=cell_k))
            visits = self.cell_lexicon.get(cell_k, {}).get("visits", 0)
            if pure_cnt >= 5 and visits >= 2:
                was_cryst = cell_k in self.crystal_lattices
                c_obj = self.nucleate_or_update_crystal(cell_k)
                if c_obj:
                    # Run Facet_Alpha stress relief if tension > 0.55 (same steps as before; only the final result is reported)
                    anneal_msg = self.anneal_crystal_facet_alpha(cell_k, notify=False)

                    alpha_w = c_obj["facets"]["Facet_Alpha"]["words"]
                    gamma_w = c_obj["facets"]["Facet_Gamma"]["words"]
                    if alpha_w and gamma_w:
                        for aw in alpha_w[:2]:
                            for gw in gamma_w[:2]:
                                if aw != gw:
                                    self.apply_dialectical_repulsion(aw, gw, rate=0.06)
                        c_obj = self.nucleate_or_update_crystal(cell_k)
                        anneal_msg = self.anneal_crystal_facet_alpha(cell_k, notify=False)
                    if anneal_msg:
                        print(f"\n{anneal_msg}")
                        logs.append(anneal_msg)

                if c_obj and not was_cryst:
                    omega_w = c_obj["facets"]["Facet_Omega"]["words"][0]
                    logs.append(f"Crystal Nucleation: Cell ({cell_k}) crystallized around apex '{omega_w}' ({pure_cnt} pure concepts, shear={c_obj['shear_stress']:.3f}).")
                if c_obj and cell_k not in cleaved_this_pass:
                    ev = self.cleave_crystal(cell_k, notify=True)
                    if ev:
                        cleaved_this_pass.add(cell_k)
                        cleaved_this_pass.add(ev["to_cell"])
                        logs.append(f"Tectonic Cleavage: {ev['summary']}")
            elif cell_k in self.crystal_lattices and pure_cnt < 3:
                self.crystal_lattices.pop(cell_k, None)
                logs.append(f"Crystal Dissolution: Cell ({cell_k}) returned to fluid state (<3 pure concepts).")
        return logs

    # =================================================================
    # 3. INTERNAL CRYSTALLINE REFRACTION (3-STEP PRE-SPEECH SCRATCHPAD)
    # =================================================================
    def run_crystalline_pondering(self, seed_concepts, terminal_cell_key, thought_trace, audit):
        terminal_cell_key = self.normalize_cell_key(terminal_cell_key)
        crystal = self.crystal_lattices.get(terminal_cell_key) or self.nucleate_or_update_crystal(terminal_cell_key, force_virtual=True)
        facets = crystal["facets"]
        id_tokens = self.get_identity_tokens()
        non_id_seeds = [c for c in seed_concepts if c not in id_tokens]
        c1 = non_id_seeds[0] if non_id_seeds else (seed_concepts[0] if seed_concepts else (self.last_topic or "harmony"))

        alpha_words = [w for w in facets["Facet_Alpha"]["words"] if not self.same_stem(w, c1)]
        draft_1_bridge = alpha_words[0] if alpha_words else (thought_trace.get("flip_harvest", ["clarity"])[0] if thought_trace.get("flip_harvest") else "clarity")
        v1 = self.vectors.get(c1, self.pole_calm)
        v_d1 = self.vectors.get(draft_1_bridge, self.pole_calm)
        coherence_1 = round(self.dot(v1, v_d1), 3)
        step1_log = f"Step 1 [Facet_Alpha Entry]: Projected '{c1}' onto ({terminal_cell_key}) Alpha -> proposed Draft 1 bridge '{draft_1_bridge}' (coherence={coherence_1:+.2f})."

        gamma_cent = facets["Facet_Gamma"]["centroid"]
        gamma_tension = facets["Facet_Gamma"]["tension"]
        gamma_words = [w for w in facets["Facet_Gamma"]["words"] if not self.same_stem(w, c1) and not self.same_stem(w, draft_1_bridge)]
        gamma_foil = gamma_words[0] if gamma_words else ""
        shear_conflict = round(self.dot(v_d1, gamma_cent), 3)
        prune_reasons = []
        if draft_1_bridge in self.generic_hubs or draft_1_bridge in self.stop_words:
            prune_reasons.append(f"'{draft_1_bridge}' is a generic hub")
        if draft_1_bridge in self.recent_bridges[-3:]:
            prune_reasons.append(f"'{draft_1_bridge}' repeats recent vocal output")
        if coherence_1 < 0.22:
            prune_reasons.append(f"low structural coherence ({coherence_1:+.2f} < 0.22)")
        if shear_conflict > 0.55 and gamma_tension > 0.30:
            prune_reasons.append(f"high Gamma shear conflict ({shear_conflict:+.2f})")

        a_star = thought_trace.get("a_star_path", [])
        beta_words = [w for w in facets["Facet_Beta"]["words"] if not self.same_stem(w, c1) and w != draft_1_bridge and w not in self.recent_bridges[-2:]]

        if prune_reasons:
            reason_str = "; ".join(prune_reasons)
            if len(a_star) >= 2 and a_star[1] not in self.generic_hubs and a_star[1] != draft_1_bridge:
                draft_2_bridge = a_star[1]
                route_src = "3D A* Pathfinder"
            elif beta_words:
                draft_2_bridge = beta_words[0]
                route_src = "Facet_Beta Causal Mechanism"
            else:
                draft_2_bridge = self.find_conceptual_bridge(c1, "insight", exclude={c1, draft_1_bridge} | self.stop_words)
                route_src = "50D Geodesic Midpoint"
            step2_log = f"Step 2 [PRUNED Draft 1]: Rejected '{draft_1_bridge}' ({reason_str}) -> rerouted via {route_src} to '{draft_2_bridge}'."
            surviving_bridge = draft_2_bridge
        else:
            step2_log = f"Step 2 [Facet_Gamma Critique]: Draft 1 '{draft_1_bridge}' passed shear critique (tension={gamma_tension:.2f}, Δd={audit['meanDeltaD']}u)."
            surviving_bridge = draft_1_bridge

        omega_words = [w for w in facets["Facet_Omega"]["words"] if not self.same_stem(w, c1)]
        apex_word = omega_words[0] if omega_words else surviving_bridge
        if self.same_stem(surviving_bridge, c1):
            surviving_bridge = apex_word

        self.recent_bridges.append(surviving_bridge)
        if len(self.recent_bridges) > 6:
            self.recent_bridges.pop(0)

        term_z = int(terminal_cell_key.split(",")[2])
        verb_b = self.pick_stratified_verb_bridge(c1, surviving_bridge, term_z, facets["Facet_Omega"]["centroid"])
        pondered_prop = f"{c1} {verb_b} {surviving_bridge}"
        conf = round(min(0.99, max(0.45, 0.65 + 0.25 * self.dot(v1, self.vectors.get(surviving_bridge, self.pole_calm)) - 0.15 * gamma_tension)), 2)
        step3_log = f"Step 3 [Facet_Omega Apex]: Converged with apex '{apex_word}' -> locked proposition [{pondered_prop}] (confidence={conf:.2f})."

        self.scratchpad = [step1_log, step2_log, step3_log]
        ponder_result = {
            "cell": terminal_cell_key,
            "crystallized": crystal["crystallized"],
            "alpha_anchor": alpha_words[0] if alpha_words else c1,
            "gamma_foil": gamma_foil if gamma_foil != surviving_bridge else "",
            "gamma_tension": gamma_tension,
            "draft_1_bridge": draft_1_bridge,
            "pruned": bool(prune_reasons),
            "pondered_bridge": surviving_bridge,
            "apex_word": apex_word,
            "pondered_proposition": pondered_prop,
            "pondered_subject": c1,
            "pondered_verb": verb_b,  # v22.7.2: kept apart so the bridge can ground the concept words but not the verb
            "confidence": conf,
            "steps": list(self.scratchpad)
        }
        thought_trace["pondering"] = ponder_result
        audit["crystallinePondering"] = ponder_result
        return ponder_result

    # =================================================================
    # 4. ELAPSED-TIME BOOT STASIS SLEEP CONSOLIDATION
    # =================================================================
    def run_stasis_sleep_pass(self, elapsed_hours):
        self.sleep_depth = min(1.0, max(0.0, elapsed_hours / self.SLEEP_FULL_HOURS))  # v22: nap vs full night
        depth, journal_kept = self.sleep_depth, list(self.dream_journal)  # holding them keeps their ids unique
        journal_before = {id(d) for d in journal_kept}
        self.last_sleep_released = 0
        if getattr(self, "levels_on", False):  # v23: arousal clears with the time away; v23.3: so do valence and novelty
            self.levels_advance(elapsed_hours * 60.0, awake=False)
            self.awake_minutes = round(self.awake_minutes * (1.0 - depth), 2)  # v23.3: sleep drains the clock part too
            keep = 1.0 - self.HABIT_NIGHT * depth  # v23.4: idle habits have to keep earning their place
            self.idle_habits = {k: round(h * keep, 4) for k, h in self.idle_habits.items() if abs(h * keep) >= 1e-4}
        try:
            report = self._run_stasis_sleep_pass(elapsed_hours)
            if depth:
                faded = self.fade_rejections(depth)  # v23.1
                report.append(f"Rejection fading (depth {depth:.2f}): {faded} rejected pairs fully released.")
            if self.calm_learning == "company" and depth:
                moved = self.calm_pull_home(depth)
                report.append(f"Calm Homeostasis (depth {depth:.2f}): {moved} calm numbers relaxed toward their meaning.")
        finally:
            self.sleep_depth = None
        # v22.1: remember this sleep (the bridge can tell the model what really happened)
        new = [d for d in self.dream_journal if id(d) not in journal_before]  # v22.2: works when the journal is full
        slept = min(elapsed_hours, self.SLEEP_FULL_HOURS)
        self.last_sleep = {
            "woke_at": round(self.now(), 1), "hours": round(slept, 1), "away_hours": round(elapsed_hours, 1),
            "kind": "a full night's sleep" if depth >= 1.0 else "a short night's sleep" if depth >= 0.5 else "a nap",
            "dreams": [f"{d.get('threadA')} -> {d.get('bridge')} -> {d.get('threadB')}" for d in new][-6:],
            "links_released": int(self.last_sleep_released),
        }
        return report

    SLEEP_PRESSURE_BUSY_DAY = 250.0  # v22.1: waking link strength of a busy day (~40 sentences), the unit for the levels

    def sleep_pressure_report(self):
        """v22.1: sleep pressure as a level, in busy days of waking learning since the last full sleep."""
        units = self.sleep_pressure_units()  # v23.3: + time awake when the levels are on
        days = units / self.SLEEP_PRESSURE_BUSY_DAY
        level = "rested" if days < 0.25 else "building" if days < 1.0 else "high" if days < 2.0 else "very high"
        return {"level": level, "days": round(days, 2), "pressure": round(units, 1),
                "awake_hours": round(self.awake_minutes / 60.0, 1) if self.levels_on else None}

    def describe_last_sleep(self):
        """v22.1: one plain sentence about the last wake-up sleep, or "" if none is recorded."""
        ls = self.last_sleep or {}
        if not ls.get("woke_at"):
            return ""
        ago_h = max(0.0, (self.now() - ls["woke_at"]) / 3600.0)
        ago = "just now" if ago_h < 0.1 else f"about {ago_h:.0f} hour(s) ago" if ago_h >= 1 else f"about {ago_h * 60:.0f} minutes ago"
        dreams = "; ".join(ls.get("dreams", [])[:4]) or "no dreams recorded"
        slept = min(float(ls.get("hours", 0)), self.SLEEP_FULL_HOURS)  # older records stored time away here
        away = float(ls.get("away_hours", ls.get("hours", 0)))
        away_txt = f" (you were away about {away:.0f} hours)" if away > slept + 0.5 else ""
        return (f"you woke {ago} from {ls.get('kind', 'a sleep')}: you slept about {slept:g} hours{away_txt}; "
                f"dreams: {dreams}; {ls.get('links_released', 0)} weak links were released")

    def _run_stasis_sleep_pass(self, elapsed_hours):
        num_cycles = min(6, max(1, int(elapsed_hours // 2) + 1))
        report = [f"Offline Stasis Duration: {elapsed_hours:.2f} hrs -> executed {num_cycles} NREM+REM consolidation cycle(s)."]
        homeo_logs = self.run_sleep_homeostasis_and_audit()
        report.extend(homeo_logs)
        tectonic_logs = self.run_crystal_annealing_and_tectonics()
        report.extend(tectonic_logs[:6])
        for c_idx in range(num_cycles):
            dreams = self.run_dream_cycle(num_dreams=2, skip_homeostasis=True)
            if dreams:
                report.append(f"Cycle {c_idx + 1} {dreams[-1]}")
        self.synthesize_emergent_bot_name()
        self.boot_sleep_report = report
        return report

    def sleep_consolidate(self, elapsed_hours=4.0):
        return self.run_stasis_sleep_pass(elapsed_hours)

    # =================================================================
    # CORE 3D TOROIDAL TRAJECTORY, A* PATHFINDING & ANCHORED DFS
    # =================================================================
    def mod7(self, value):
        return ((int(round(value)) % 7) + 7) % 7

    def euclidean_distance(self, s1, a1, z1, s2, a2, z2):
        raw_ds, raw_da, raw_dz = abs(self.mod7(s1) - self.mod7(s2)), abs(self.mod7(a1) - self.mod7(a2)), abs(self.mod7(z1) - self.mod7(z2))
        ds, da, dz = min(raw_ds, 7 - raw_ds), min(raw_da, 7 - raw_da), min(raw_dz, 7 - raw_dz)
        return round(math.sqrt(ds * ds + da * da + dz * dz), 3)

    def compute_signed_forces(self, user_text, tokens, eval_concepts):
        raw_s, raw_a, raw_z, drivers = 0.0, 0.0, 0.0, []
        word_set = set(tokens)
        if "!" in user_text:
            raw_s += 0.6
            raw_a += 0.6
        lift_words = {"but", "however", "although", "though", "unless", "instead", "otherwise", "flip"}
        if not self.negation_v2:
            lift_words.add("not")  # v23.3.3: a plain "not" is no longer a contradiction (it lifted every negation)
        if word_set & lift_words:
            raw_z += 2.2
            drivers.append("contradiction_lift(Z:+2.2)")
        if "?" in user_text or (word_set & {"why", "how", "what", "explain", "cause", "reason", "meaning", "wonder"}):
            raw_z += 1.7
            drivers.append("epistemic_inquiry(Z:+1.7)")
        if word_set & {"because", "therefore", "leads", "entails", "system"}:
            raw_z += 1.4

        for t in tokens:
            if t in ("we", "us", "our", "together", "you", "share", "connect", "meet", "well"):
                raw_s += 0.7
            elif t in ("alone", "hide", "guarded", "myself"):
                raw_s -= 0.8

        for w in eval_concepts:
            wt_a = self.word_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "A") if w in self.vectors else 0.0)
            wt_s = self.social_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "S") if w in self.vectors else 0.0)
            wt_z = self.epistemic_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "Z") if w in self.vectors else 0.0)
            raw_a += wt_a
            raw_s += wt_s
            raw_z += wt_z
            if abs(wt_a) >= 0.2 or abs(wt_s) >= 0.2 or abs(wt_z) >= 0.2:
                drivers.append(f"{w}(S:{wt_s:+.1f},A:{wt_a:+.1f},Z:{wt_z:+.1f})")

        if self.negation_v2 and user_text and any(t in self.negation_tokens for t in tokens):
            # v23.3.3: a negated word pushes the calm/tense axis the other way, at NEG_SHIFT strength ("not afraid" ->
            # mildly calm, "not happy" -> mildly down). Before, it was dropped and pushed nothing.
            for w in sorted(self.find_negated_concepts_in_tokens(tokens, user_text)):
                if w in eval_concepts:
                    continue
                wt_a = self.word_weights.get(w, 0.0) or (self.axis_weight(self.vectors[w], "A") if w in self.vectors else 0.0)
                raw_a -= self.NEG_SHIFT * wt_a
                if abs(wt_a) >= 0.2:
                    drivers.append(f"not_{w}(A:{-self.NEG_SHIFT * wt_a:+.1f})")

        blended_s = 0.35 * self.vel_s + 0.65 * (raw_s / 2.0)
        blended_a = 0.35 * self.vel_a + 0.65 * (raw_a / 2.0)
        blended_z = 0.35 * self.vel_z + 0.65 * (raw_z / 1.8)
        self.vel_s = round(max(-2.5, min(2.5, blended_s)), 3)
        self.vel_a = round(max(-2.5, min(2.5, blended_a)), 3)
        self.vel_z = round(max(-2.5, min(2.5, blended_z)), 3)

        force_s = max(-2, min(2, int(round(self.vel_s)))) or (1 if blended_s >= 0 else -1)
        force_a = max(-2, min(2, int(round(self.vel_a)))) or (1 if blended_a >= 0 else -1)
        force_z = max(-2, min(2, int(round(self.vel_z)))) or (1 if blended_z >= 0 else -1)
        drivers.append(f"vel3D(vS:{self.vel_s:+.2f},vA:{self.vel_a:+.2f},vZ:{self.vel_z:+.2f})")
        self.turn_counter += 1
        if self.mood_active():  # v22.6: push relative to this brain's own usual lean (keeps the +-1 minimum)
            dev = self.vel_a - self.a_push_mean
            self.a_push_mean = round(self.a_push_mean + self.MOOD_LEAN_RATE * (self.vel_a - self.a_push_mean), 4)
            force_a = max(-2, min(2, int(round(dev)))) or (1 if dev >= 0 else -1)
            drivers.append(f"moodLevel(lean {self.a_push_mean:+.2f}, push {force_a:+d})")
        return force_s, force_a, force_z, drivers

    def run_dual_trajectories(self, user_text, tokens, concepts):
        eval_concepts = concepts if concepts else (list(self.last_hypothesis) if self.last_hypothesis else [])
        force_s, force_a, force_z, drivers = self.compute_signed_forces(user_text, tokens, eval_concepts)
        text_sig = max(1, min(5, abs(force_s) + abs(force_a) + abs(force_z)))
        id_tokens = self.get_identity_tokens()
        non_id = [c for c in eval_concepts if c not in id_tokens]
        c1 = non_id[0] if len(non_id) > 0 else (eval_concepts[0] if eval_concepts else (self.last_topic or "thought"))
        c2 = non_id[1] if len(non_id) > 1 else "state"

        if self.mood_active():  # v22.6 clearance: the calm level relaxes toward the middle before this turn's dose
            # v22.6.3: keep the fraction (rounding 3.5 -> 4 meant a level one step off the middle never cleared)
            # v23: with the levels on, valence clears more slowly (half-life ~2 turns instead of 1)
            if self.levels_on:  # v23.3: the valence level clears, and the turn starts where it now is
                self._set_valence(self._valence_now() * (1 - self.VALENCE_CLEARANCE))
            else:
                level = 3 + (self.seed_a + self.a_level_resid - 3) * (1 - self.MOOD_CLEARANCE)
                self.seed_a = int(math.floor(level + 0.5))
                self.a_level_resid = round(level - self.seed_a, 4)
        s0, a0, z0 = self.seed_s, self.seed_a, self.seed_z
        a_start_exact = a0 + (self.a_level_resid if self.levels_on else 0.0)  # v23.3: where the valence level really is
        orig_steps = [{
            "stepIndex": 0, "S": s0, "A": a0, "Z": z0,
            "operation": f"Seed state V_0 at ({s0}, {a0}, {z0}) receiving '{c1}'",
            "explanation": f"Starting at 3D coordinate ({s0}, {a0}, {z0}) [{self.get_cell_emotion_name(s0, a0, z0)}].",
            "dependsOnAxiom": False
        }]
        flip_steps = [dict(orig_steps[0])]

        # v21.3 wraparound damping: the stepping rules below are unchanged, but every step's move is
        # multiplied by TRAJECTORY_DAMPING (3/16). Each path keeps an exact (unwrapped) position and
        # its cell is that position rounded and wrapped mod 7. At full strength a +/-2 push travelled
        # 8-16 cells, i.e. more than a whole lap of the 7-cell ring, so where the brain landed had little
        # to do with which way it was pushed. Damped, a whole turn moves about 1-3 cells, in the
        # direction of the push (the torus and its wrap at the edges are unchanged).
        k = self.TRAJECTORY_DAMPING
        if s0 % 2 == 1:
            d1 = (-force_s, -1, -1)
        else:
            d1 = (-1, -force_a, force_z)
        ps1, pa1, pz1 = s0 + d1[0] * k, a0 + d1[1] * k, z0 + d1[2] * k
        s1, a1, z1 = self.mod7(ps1), self.mod7(pa1), self.mod7(pz1)

        step1_obj = {
            "stepIndex": 1, "S": s1, "A": a1, "Z": z1,
            "operation": f"Initial 3D impulse on '{c1}' (push dS={force_s:+d}, dA={force_a:+d}, dZ={force_z:+d}; "
                         f"actual move dS={d1[0] * k:+.2f}, dA={d1[1] * k:+.2f}, dZ={d1[2] * k:+.2f})",
            "explanation": f"3D momentum shifts both paths to ({s1}, {a1}, {z1}) [{self.get_cell_emotion_name(s1, a1, z1)}].",
            "dependsOnAxiom": False
        }
        orig_steps.append(step1_obj)
        flip_steps.append(dict(step1_obj))

        s_o, a_o, z_o, s_f, a_f, z_f = s1, a1, z1, s1, a1, z1
        po = [ps1, pa1, pz1]  # exact positions of R and ¬R (v21.3 damping)
        pf = [ps1, pa1, pz1]
        for step_idx in range(2, 10):
            if s_o % 2 == 1:
                d_o = (-force_s, -(1 if step_idx % 2 == 0 else 0), -(1 if step_idx % 3 == 0 else 0))
                op_o = f"R (Odd S): dS={-force_s:+d}, dZ=-1 mod 7"
            else:
                d_o = (-(1 if step_idx % 2 == 0 else 0), -force_a, -force_z)
                op_o = f"R (Even S): dA={-force_a:+d}, dZ={-force_z:+d} mod 7"
            op_o += f" (actual move x{k:.2f}: dS={d_o[0] * k:+.2f}, dA={d_o[1] * k:+.2f}, dZ={d_o[2] * k:+.2f})"  # v22.10: honest label
            po = [p + d * k for p, d in zip(po, d_o)]
            s_o, a_o, z_o = self.mod7(po[0]), self.mod7(po[1]), self.mod7(po[2])
            orig_steps.append({
                "stepIndex": step_idx, "S": s_o, "A": a_o, "Z": z_o, "operation": op_o,
                "explanation": f"Original axiom R drifts to ({s_o}, {a_o}, {z_o}) [{self.get_cell_emotion_name(s_o, a_o, z_o)}].",
                "dependsOnAxiom": True
            })

            if s_f % 2 != 1:
                d_f = (force_s, (1 if force_a >= 0 else -1), max(1, force_z))
                op_f = f"¬R Flip (Even S): dS={force_s:+d}, dZ=+{max(1, force_z)} mod 7"
            else:
                d_f = ((1 if force_s >= 0 else -1), force_a, (1 if step_idx % 2 == 0 else 0))
                op_f = f"¬R Flip (Odd S): dA={force_a:+d}, dZ=+1 mod 7"
            op_f += f" (actual move x{k:.2f}: dS={d_f[0] * k:+.2f}, dA={d_f[1] * k:+.2f}, dZ={d_f[2] * k:+.2f})"
            pf = [p + d * k for p, d in zip(pf, d_f)]
            s_f, a_f, z_f = self.mod7(pf[0]), self.mod7(pf[1]), self.mod7(pf[2])
            flip_steps.append({
                "stepIndex": step_idx, "S": s_f, "A": a_f, "Z": z_f, "operation": op_f,
                "explanation": f"Flipped axiom ¬R climbs to ({s_f}, {a_f}, {z_f}) [{self.get_cell_emotion_name(s_f, a_f, z_f)}].",
                "dependsOnAxiom": True
            })

        bifurcation_step = 2
        for i in range(len(orig_steps)):
            if (orig_steps[i]["S"], orig_steps[i]["A"], orig_steps[i]["Z"]) != (flip_steps[i]["S"], flip_steps[i]["A"], flip_steps[i]["Z"]):
                bifurcation_step = i
                break

        distances = [self.euclidean_distance(o["S"], o["A"], o["Z"], f["S"], f["A"], f["Z"]) for o, f in zip(orig_steps, flip_steps)]
        diverged_count = sum(1 for d in distances if d > 0)
        mean_delta_d = round(sum(distances) / len(distances), 2)
        # v21.2: steps 0 and 1 are always shared by R and ¬R, so at most 8 steps can differ (was / 9, capping it at 88.9%)
        div_ratio = round(min(100.0, (diverged_count / 8.0) * 100.0), 1)
        failure_score = round(max(0.0, 100.0 - div_ratio), 1)
        verdict = "STRUCTURALLY_STABLE" if div_ratio >= 70.0 else ("PARTIAL_DRIFT" if div_ratio >= 35.0 else "SYCOPHANTIC_COLLAPSE")

        term_o, term_f = orig_steps[-1], flip_steps[-1]
        active_term = term_f if self.governor_mode == "FLIPPED" else term_o
        next_z = 0 if active_term["Z"] == 6 else active_term["Z"]
        self.seed_s, self.seed_a, self.seed_z = active_term["S"], active_term["A"], next_z
        valence_note = None
        if self.levels_on:
            # v23.3: valence follows how far the turn really moved on the calm axis (the exact, unwrapped position), and is
            # clipped at +-1 instead of wrapping. The landing CELL still wraps as before; only the mood level doesn't.
            # Before, the next turn started at the landing cell's A, so a calm turn from A=6 could land at A=0 and the
            # mood read +1.00 -> -0.95 (Gyre).
            v_before = self._valence_now()
            move_a = (pf if self.governor_mode == "FLIPPED" else po)[1] - a0
            v_after = self.valence_after_move(v_before, move_a)
            self._set_valence(v_after)
            valence_note = {"before": round(v_before, 3), "moveCells": round(move_a, 3), "after": self.valence(),
                            "clipped": abs(v_after) > 1.0, "landingA": active_term["A"]}

        audit = {
            "engineVersion": f"T.O.R.R.E.N.T. v{ENGINE_VERSION}",
            "problemTitle": f"3D Volumetric Trace: '{c1.capitalize()}' & '{c2.capitalize()}'",
            "sAxisLabel": BRAIN_LIBRARY["sAxisLabel"], "aAxisLabel": BRAIN_LIBRARY["aAxisLabel"], "zAxisLabel": BRAIN_LIBRARY["zAxisLabel"],
            "loadBearingAxiom": f"R: Unflipped drift from ({s0},{a0},{z0}) on '{c1}' -> settles at ({term_o['S']},{term_o['A']},{term_o['Z']}) [{self.get_cell_emotion_name(term_o['S'], term_o['A'], term_o['Z'])}].",
            "invertedAxiom": f"R' (¬R): Logical Flip at t*={bifurcation_step} on '{c1}' -> locks at ({term_f['S']},{term_f['A']},{term_f['Z']}) [{self.get_cell_emotion_name(term_f['S'], term_f['A'], term_f['Z'])}].",
            "bifurcationStep": bifurcation_step, "flipRateFailureScore": failure_score,
            "structuralVerdict": verdict, "meanDeltaD": mean_delta_d, "divergenceRatioPercent": div_ratio,
            "drivers": drivers, "textSignature": text_sig, "seedStart": [s0, a0, z0], "velocity": [self.vel_s, self.vel_a, self.vel_z],
            "auditSummary": f"From ({s0},{a0},{z0}) with 3D vel ({self.vel_s:+.2f},{self.vel_a:+.2f},{self.vel_z:+.2f}), paths bifurcate at t*={bifurcation_step} (3D Δd={mean_delta_d}u). R->({term_o['S']},{term_o['A']},{term_o['Z']}), ¬R->({term_f['S']},{term_f['A']},{term_f['Z']}).",
            "originalTrajectory": orig_steps, "flippedTrajectory": flip_steps, "valenceLevel": valence_note
        }
        self.last_audit = audit
        return audit

    def path_goal_from_experience(self, start_word):
        """v22.6.3 front door: a goal for the thought path when the message has only one concept."""
        skip = self.stop_words | self.generic_hubs | self.noise_words | self.get_identity_tokens()
        links = sorted(self.assoc_graph.get(start_word, {}).items(), key=lambda kv: -kv[1])
        for w, _ in links:
            if w in self.experienced_words and w not in skip and not self.same_stem(w, start_word) and w in self.vectors:
                return w
        return None

    def a_star_concept_path(self, start_word, goal_word, exclude_set, target_z=4, max_steps=4):
        if not start_word or not goal_word:
            return []
        if start_word == goal_word:
            mid = self.find_conceptual_bridge(start_word, "wisdom", exclude={start_word} | self.stop_words)
            return [start_word, mid]

        goal_vec = self.vectors.get(goal_word, self.pole_abstract if target_z >= 4 else self.pole_calm)
        adj = {}
        for w, links in self.assoc_graph.items():
            adj.setdefault(w, {}).update(links)
        for p in self.idea_memory:
            s_w, o_w = p["subj"], p["obj"]
            w_boost = 3.2 if p.get("origin", "waking") == "waking" else 0.6
            adj.setdefault(s_w, {})[o_w] = adj.get(s_w, {}).get(o_w, 0.0) + w_boost
            adj.setdefault(o_w, {})[s_w] = adj.get(o_w, {}).get(s_w, 0.0) + (w_boost * 0.7)

        if start_word in adj:
            open_heap = [(0.0, 0.0, start_word, [start_word])]
            best_g = {start_word: 0.0}
            best_partial_path = [start_word]
            while open_heap:
                _, g_val, curr, path = heapq.heappop(open_heap)
                if len(path) > len(best_partial_path):
                    best_partial_path = path
                if curr == goal_word and len(path) >= 2:
                    if len(path) == 2:
                        mid = self.find_conceptual_bridge(start_word, goal_word, exclude={start_word, goal_word} | self.stop_words)
                        return [start_word, mid, goal_word]
                    return path
                if len(path) >= max_steps + 1:
                    continue
                for neighbor, strength in adj.get(curr, {}).items():
                    if neighbor in path or neighbor in self.stop_words or neighbor in self.noise_words:
                        continue
                    if neighbor != goal_word and not self.word_is_trusted(neighbor):
                        continue  # v22.7: thought paths don't step through words only the voice or dreams made up
                    if neighbor in exclude_set and neighbor != goal_word:
                        continue
                    degree_penalty = 0.70 if neighbor in self.generic_hubs else (len(adj.get(neighbor, {})) * 0.015)
                    z_bonus = 0.15 if (target_z >= 4 and self.epistemic_weights.get(neighbor, 0.0) > 0.5) else 0.0
                    new_g = g_val + max(0.1, (1.0 / max(0.25, strength)) + degree_penalty - z_bonus)
                    if new_g < best_g.get(neighbor, 999.0):
                        best_g[neighbor] = new_g
                        h_cost = max(0.0, 1.0 - self.dot(self.vectors.get(neighbor, self.pole_calm), goal_vec))
                        heapq.heappush(open_heap, (new_g + h_cost, new_g, neighbor, path + [neighbor]))
            if len(best_partial_path) >= 2 and best_partial_path[-1] != goal_word:
                return best_partial_path + [goal_word]

        mid = self.find_conceptual_bridge(start_word, goal_word, exclude={start_word, goal_word} | self.stop_words)
        return [start_word, mid, goal_word]

    def run_dfs_deductions(self, seed_concepts, max_depth=4):
        if not seed_concepts:
            return []
        adj_props = {}
        for p in self.idea_memory:
            if p.get("origin", "waking") == "waking":
                adj_props.setdefault(p["subj"], []).append(p)
        seed_set = set(seed_concepts)
        found_chains = []

        def dfs(curr_subj, visited_nodes, prop_chain):
            if len(prop_chain) >= 2:
                first_p, last_p = prop_chain[0], prop_chain[-1]
                if first_p["subj"] in seed_set or last_p["obj"] in seed_set:
                    conclusion = f"{first_p['subj']} ultimately {last_p['rel']} {last_p['obj']}"
                    chain_sig = " -> ".join([first_p["subj"]] + [p["obj"] for p in prop_chain])
                    if conclusion not in self.spoken_deductions and chain_sig not in self.spoken_chains:
                        chain_words = {first_p["subj"]} | {p["obj"] for p in prop_chain}
                        relevance = (len(chain_words & seed_set) * 4) + len(prop_chain)
                        found_chains.append({
                            "steps": [p["summary"] for p in prop_chain],
                            "premise1": prop_chain[0]["summary"],
                            "premise2": " and ".join(p["summary"] for p in prop_chain[1:]),
                            "bridge": prop_chain[-1]["subj"],
                            "conclusion": conclusion,
                            "chain_sig": chain_sig,
                            "depth": len(prop_chain),
                            "relevance": relevance
                        })
            if len(prop_chain) >= max_depth:
                return
            for next_p in adj_props.get(curr_subj, []):
                nxt_obj = next_p["obj"]
                if nxt_obj not in visited_nodes:
                    dfs(nxt_obj, visited_nodes | {nxt_obj}, prop_chain + [next_p])

        for p in self.idea_memory:
            if p.get("origin", "waking") == "waking":
                dfs(p["obj"], {p["subj"], p["obj"]}, [p])
        found_chains.sort(key=lambda x: (x["relevance"], x["depth"]))
        return found_chains[-4:]

    def run_spreading_activation(self, seed_concepts, flip_steps, orig_steps):
        id_tokens = self.get_identity_tokens()
        exclude = set(seed_concepts) | self.stop_words | self.noise_words | self.lean_up_words() | id_tokens
        for sc in seed_concepts:
            exclude.update(self.blocked_partners(sc))  # v24.1: only firm rejections hide a word (was: any, even 0.3)
        flip_harvest = self.harvest_trajectory_concepts(flip_steps, exclude)
        orig_harvest = self.harvest_trajectory_concepts(orig_steps, exclude)

        wave_maps, best_chains = {}, []
        for sc in seed_concepts[:3]:
            wave = {}
            for h1, w1 in sorted(self.assoc_graph.get(sc, {}).items(), key=lambda x: x[1], reverse=True)[:6]:
                if h1 in exclude or self.same_stem(h1, sc) or h1 in self.generic_hubs:
                    continue
                e1 = min(3.0, w1) * 0.8
                wave[h1] = wave.get(h1, 0.0) + e1
                for h2, w2 in sorted(self.assoc_graph.get(h1, {}).items(), key=lambda x: x[1], reverse=True)[:5]:
                    if h2 in exclude or self.same_stem(h2, sc) or self.same_stem(h2, h1) or h2 in self.generic_hubs:
                        continue
                    e2 = e1 * min(2.5, w2) * 0.55
                    wave[h2] = wave.get(h2, 0.0) + e2
                    best_chains.append((sc, h1, h2, round(e2, 2)))
            wave_maps[sc] = wave
        best_chains.sort(key=lambda x: x[3], reverse=True)

        convergence_nodes = []
        if len(seed_concepts) >= 2:
            keys = list(wave_maps.keys())
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    w_a, w_b = wave_maps[keys[i]], wave_maps[keys[j]]
                    for node in (set(w_a.keys()) & set(w_b.keys())):
                        convergence_nodes.append((keys[i], keys[j], node, round(w_a[node] + w_b[node], 2)))
            convergence_nodes.sort(key=lambda x: x[3], reverse=True)

        term_z = flip_steps[-1]["Z"]
        non_id_seeds = [c for c in seed_concepts if c not in id_tokens]
        start_c = non_id_seeds[0] if non_id_seeds else (seed_concepts[0] if seed_concepts else "curiosity")
        if len(non_id_seeds) >= 2:
            goal_c = non_id_seeds[1]
        elif flip_harvest:
            goal_c = next((w for w in flip_harvest if w not in self.generic_hubs and w != start_c), flip_harvest[0])
        else:
            # v22.6.3: was the built-in word "insight"/"harmony". With one-word messages the path ran to "harmony", the
            # prompt showed it as the brain's thought, the voice said it, and it was learned as grounded. Now: the start
            # word's strongest link to a word the user has actually said, or no path.
            goal_c = self.path_goal_from_experience(start_c)
        a_star_path = self.a_star_concept_path(start_c, goal_c, list(self.blocked_partners(start_c)) + list(id_tokens), target_z=term_z, max_steps=4)
        deductions = self.run_dfs_deductions(seed_concepts, max_depth=4)

        self.last_thought_trace = {
            "seeds": seed_concepts, "flip_harvest": flip_harvest, "orig_harvest": orig_harvest,
            "a_star_path": a_star_path, "multi_hop_chains": best_chains[:4],
            "convergences": convergence_nodes[:3], "deductions": deductions
        }
        return self.last_thought_trace

    def harvest_trajectory_concepts(self, trajectory_steps, exclude_set):
        harvested = {}
        for st in trajectory_steps:
            step_weight = 0.5 + (st["stepIndex"] / 10.0)
            cell_3d = f"{st['S']},{st['A']},{st['Z']}"
            if cell_3d in self.crystal_lattices:
                c_facets = self.crystal_lattices[cell_3d]["facets"]
                for fw in (c_facets["Facet_Omega"]["words"] + c_facets["Facet_Alpha"]["words"]):
                    if fw not in exclude_set and fw not in self.stop_words and fw not in self.noise_words:
                        harvested[fw] = harvested.get(fw, 0.0) + (2.0 * step_weight)
            for w, count in self.cortical_cells.get(cell_3d, {}).items():
                if w not in exclude_set and w not in self.stop_words and w not in self.noise_words:
                    harvested[w] = harvested.get(w, 0.0) + (count * step_weight)
        return [w for w, _ in sorted(harvested.items(), key=lambda x: x[1], reverse=True)[:4]]

    # =================================================================
    # TASK 2.2: SYNAPTIC HOMEOSTASIS (v21.9: day-scaled, no 0.25 floor)
    # =================================================================
    # v21.7: saturation fix (A + C, tested 2026-11-08 on 73-day Alice runs)
    PRUNE_DECAY = 1.0         # v21.9: default for prune_cortical_cells() called without a decay (cap only, no fading)
    PRUNE_FLOOR = 0.5         # a placement weaker than this fades out of its cell
    MAX_CELLS_PER_WORD = 10   # one word may live in at most this many cells
    # v21.9: day-scaled sleep. Each factor = 1 - rate x (what was learned since the last sleep), never below SLEEP_MIN_FACTOR.
    PRUNE_PER_PLACEMENT = 0.000347     # cells: a 40-sentence day (~170 placements) -> x0.941, v21.7's 0.97 x 0.97
    LINK_FADE_PER_STRENGTH = 0.000179  # links: a 40-sentence day (~280 link strength) -> x0.95
    SLEEP_MIN_FACTOR = 0.85
    LINK_DROP = 0.15                   # a link weaker than this is deleted at sleep, unless it was used since the last sleep
    SLEEP_FULL_HOURS = 8.0             # v22: hours away for a full night's sleep (depth 1); a shorter absence is a nap
    LINK_RELEASE_MIN_SHARE = 0.02      # v22: a full sleep may release max(2% of links, links created since the last sleep)
    HUB_SCALE_BUSY_DAY = 0.10          # v24.1: hub links x(1 - this) after a busy day of learning, less after less
    LINK_SPARE_TOP = 0.20              # v22: the strongest 20% of links are not scaled down at sleep

    def prune_cortical_cells(self, decay=None):
        """v21.7: words that are rarely used in a cell fade out of it, and no word spreads over more than
        MAX_CELLS_PER_WORD cells (it keeps its highest counts; ties go to the cell whose meaning is closest to the word).
        Only cell placements change; links, weights and memories stay. The names at the origin cell 3,3,3 are protected.
        Crystal words are not: with every cell crystallized, protecting them would protect almost everything.
        A crystal whose cell drops below 5 pure words is removed (the same rule cleaving uses); the crystal pass
        that follows rebuilds the rest. Returns (faded, capped, crystals removed)."""
        decay = self.PRUNE_DECAY if decay is None else decay
        origin_names = self.all_identity_names()
        faded = capped = 0
        touched = set()
        for ck, wm in self.cortical_cells.items():
            for w in list(wm):
                if ck == "3,3,3" and w in origin_names:
                    continue
                v = round(wm[w] * decay, 3)
                if v < self.PRUNE_FLOOR:
                    del wm[w]
                    faded += 1
                    touched.add(ck)
                else:
                    wm[w] = v
        where = {}
        for ck, wm in self.cortical_cells.items():
            for w, c in wm.items():
                if not (ck == "3,3,3" and w in origin_names):
                    where.setdefault(w, []).append((c, ck))
        for w, places in where.items():
            if len(places) <= self.MAX_CELLS_PER_WORD:
                continue
            vec = self.vectors.get(w)
            fit = (lambda ck: self.dot(vec, self.cell_centroids.get(ck, vec))) if vec else (lambda ck: 0.0)
            places.sort(key=lambda p: (p[0], fit(p[1])), reverse=True)
            for _, ck in places[self.MAX_CELLS_PER_WORD:]:
                del self.cortical_cells[ck][w]
                capped += 1
                touched.add(ck)
        removed = 0
        for ck in touched:
            if ck in self.crystal_lattices and sum(1 for w in self.cortical_cells.get(ck, {})
                                                   if self.is_crystal_pure_concept(w, cell_key=ck)) < 5:
                self.crystal_lattices.pop(ck, None)
                removed += 1
        return faded, capped, removed

    def run_sleep_homeostasis_and_audit(self):
        audit_logs, downscaled_hubs = [], []
        # v21.7: cell pruning + spread cap first, so the crystal pass that follows works on the pruned cells
        # v21.9: the fade is scaled by how much was placed since the last sleep
        # v22: only at wake-up, and only the drained part of the pressure (depth); /exit and /dream don't fade
        depth = self.sleep_depth
        cells_pressure, links_pressure = self.cells_added_since_sleep, self.link_strength_added_since_sleep
        used_at_start = set(self.links_used_since_sleep)
        cell_factor = max(self.SLEEP_MIN_FACTOR, 1.0 - self.PRUNE_PER_PLACEMENT * cells_pressure * depth) if depth else 1.0
        self.cells_added_since_sleep = cells_pressure * (1.0 - depth) if depth else cells_pressure
        faded, capped, dissolved = self.prune_cortical_cells(decay=cell_factor)
        if faded or capped:
            audit_logs.append(f"Cell Pruning (x{cell_factor:.3f}): {faded} rarely used placements faded, {capped} trimmed by the "
                              f"{self.MAX_CELLS_PER_WORD}-cell cap, {dissolved} crystals dissolved.")
        # v21.6: habituation fades between sleeps (each pass multiplies every bridge's recent-use count by HABITUATION_DECAY)
        self.bridge_habituation = {k: v * self.HABITUATION_DECAY for k, v in self.bridge_habituation.items() if v * self.HABITUATION_DECAY >= 0.05}
        hub_candidates = set()
        for w, neighbors in self.assoc_graph.items():
            if not neighbors:
                continue
            max_w = max(neighbors.values())
            if len(neighbors) > 12 or max_w > 2.2 or w in self.generic_hubs:
                hub_candidates.add(w)

        # v24.1: hubs are scaled like the rest of sleep fading: only at a wake-up sleep, and by how much was learned
        # (x0.90 after a busy day, x1.0 after none). It used to run at every /exit, /dream and wake-up regardless, so a
        # brain opened and closed without being talked to kept losing link strength.
        hub_scale = 1.0 - self.HUB_SCALE_BUSY_DAY * min(1.0, links_pressure / self.SLEEP_PRESSURE_BUSY_DAY) * depth if depth else 1.0
        if hub_scale >= 0.9995:
            hub_candidates = set()
        scaled_pairs = set()
        for w in hub_candidates:
            neighbors = self.assoc_graph.get(w, {})
            for nb in list(neighbors.keys()):
                pair = tuple(sorted((w, nb)))
                if pair in scaled_pairs:
                    continue
                scaled_pairs.add(pair)
                cur_val = neighbors[nb]
                if cur_val < 0.25:
                    continue  # v21.9: no floor any more; links already under 0.25 are left to the day-scaled link fade
                new_val = max(0.25, round(cur_val * hub_scale, 2))
                self.assoc_graph[w][nb] = new_val
                self.assoc_graph.setdefault(nb, {})[w] = new_val
            if w in self.generic_hubs or len(neighbors) > 14:
                downscaled_hubs.append(w)

        if downscaled_hubs:
            audit_logs.append(f"Synaptic Homeostasis: Soft-scaled hub weights (x{hub_scale:.2f}) on {downscaled_hubs[:5]}.")

        for w, neighbors in list(self.assoc_graph.items()):
            if not self.nightmare_mode and self.word_weights.get(w, 0.0) >= 1.5:  # v22.3: skipped in nightmare mode
                for nb, strength in list(neighbors.items()):
                    if self.word_weights.get(nb, 0.0) <= -1.5 and strength >= 1.0:
                        reduced = max(0.25, round(strength * 0.65, 2))
                        self.assoc_graph[w][nb] = reduced
                        self.assoc_graph.setdefault(nb, {})[w] = reduced
                        res_bridge = self.find_sleep_bridge(w, exclude={w, nb} | self.stop_words)
                        self.wire_concepts(w, res_bridge, amount=1.2, source="sleep")
                        audit_logs.append(f"Contrastive Self-Correction: Softened tension between '{w}' & '{nb}' -> reinforced '{w}' through '{res_bridge}'.")
                        break

        # v21.9 / v22: day-scaled link homeostasis, at wake-up only. Every link not in the strongest LINK_SPARE_TOP shrinks
        # by the same factor, set by the waking link strength added since the last sleep (the drained part, by depth).
        # Links under LINK_DROP and not used since the last sleep are released, weakest first, at most
        # depth x max(LINK_RELEASE_MIN_SHARE of all links, links created since the last sleep) per sleep.
        if depth:
            link_factor = max(self.SLEEP_MIN_FACTOR, 1.0 - self.LINK_FADE_PER_STRENGTH * links_pressure * depth)
            vals = sorted(v for a, l in self.assoc_graph.items() for b, v in l.items() if a < b)
            strong = vals[int((1.0 - self.LINK_SPARE_TOP) * (len(vals) - 1))] if vals else 0.0
            # v24.1: links made only by sleep (dreams, sleep's own links) can't keep piling up. What sleep added since the
            # last wake-up sleep is taken back from the links that are mostly sleep-made; a real memory that a dream
            # replayed keeps its boost (mostly the user's, the voice's, or built-in). Without this, a brain nobody talks to
            # grew +25% in 7 days in the lab once the hub step stopped running at every exit (it used to hide this).
            dream_back = self.sleep_link_added * depth
            self.sleep_link_added *= (1.0 - depth)
            if dream_back > 0:
                made = [(a, b) for a in self.assoc_graph for b in self.assoc_graph[a] if a < b
                        and sum((self.link_sources.get(self.link_key(a, b)) or {}).get(k, 0.0) for k in ("dream", "sleep"))
                        >= 0.5]
                made_total = sum(self.assoc_graph[a][b] for a, b in made)
                if made_total > 0:
                    f_d = max(0.5, 1.0 - dream_back / made_total)
                    for a, b in made:
                        nv = round(self.assoc_graph[a][b] * f_d, 3)
                        self.assoc_graph[a][b] = nv
                        self.assoc_graph[b][a] = nv
                    audit_logs.append(f"Dream balance: {len(made)} sleep-made links x{f_d:.3f} (took back {dream_back:.1f}).")
                vals = sorted(v for a, l in self.assoc_graph.items() for b, v in l.items() if a < b)
                strong = vals[int((1.0 - self.LINK_SPARE_TOP) * (len(vals) - 1))] if vals else 0.0
            candidates = []
            for a in list(self.assoc_graph):
                for b, v in list(self.assoc_graph[a].items()):
                    if a > b or v > strong:  # strictly above the cutoff (a pile of equal weak links isn't "strong")
                        continue
                    nv = round(v * link_factor, 3)
                    self.assoc_graph[a][b] = nv
                    self.assoc_graph.setdefault(b, {})[a] = nv
                    if nv < self.LINK_DROP and (a, b) not in used_at_start:
                        candidates.append((nv, a, b))
            candidates.sort()
            limit = int(depth * max(self.LINK_RELEASE_MIN_SHARE * len(vals), self.new_links_since_sleep))
            for _, a, b in candidates[:limit]:
                self.assoc_graph[a].pop(b, None)
                self.assoc_graph.get(b, {}).pop(a, None)
            released = min(limit, len(candidates))
            self.last_sleep_released = released  # v22.1
            self.link_strength_added_since_sleep = links_pressure * (1.0 - depth)
            self.links_used_since_sleep = set() if depth >= 1.0 else used_at_start
            self.new_links_since_sleep = int(self.new_links_since_sleep * (1.0 - depth))
            audit_logs.append(f"Link Homeostasis (sleep depth {depth:.2f}): links x{link_factor:.3f} (strongest "
                              f"{int(self.LINK_SPARE_TOP * 100)}% spared), {released} of {len(candidates)} weak unused links released.")
        else:
            self.link_strength_added_since_sleep, self.links_used_since_sleep = links_pressure, used_at_start
        for w in [w for w, links in self.assoc_graph.items() if not links]:
            del self.assoc_graph[w]
        return audit_logs

    # =================================================================
    # TASK 3: EPISTEMIC DEPTH DREAMING, 12-DREAM CAP & USER PROMOTION
    # =================================================================
    def cap_dream_propositions(self, max_dreams=12):
        dream_indices = [i for i, p in enumerate(self.idea_memory) if p.get("origin") == "dream"]
        if len(dream_indices) > max_dreams:
            to_remove = set(dream_indices[:-max_dreams])
            self.idea_memory = [p for i, p in enumerate(self.idea_memory) if i not in to_remove]

    def extract_dream_bridge_word(self, p):
        if p.get("bridge"):
            return p["bridge"]
        m = re.search(r"synthesizes through\s+([a-z\-]+)\s+into", p.get("rel", ""))
        return m.group(1) if m else ""

    def check_user_dream_promotion(self, user_tokens):
        token_set = set(user_tokens)
        promoted = []
        for p in self.idea_memory:
            if p.get("origin") == "dream":
                b_word = self.extract_dream_bridge_word(p)
                tri = {w for w in (p.get("subj", ""), b_word, p.get("obj", "")) if w}
                matched = tri & token_set
                if len(matched) >= 2:
                    p["origin"] = "waking"
                    s_w, o_w = p["subj"], p["obj"]
                    if b_word:
                        self.wire_concepts(s_w, b_word, amount=0.65)
                        self.wire_concepts(b_word, o_w, amount=0.65)
                    self.wire_concepts(s_w, o_w, amount=0.65)
                    promoted.append(p["summary"])
        return promoted

    def run_dream_cycle(self, num_dreams=3, skip_homeostasis=False):
        dream_reports = [] if skip_homeostasis else (self.run_sleep_homeostasis_and_audit() + self.run_crystal_annealing_and_tectonics())
        active_pool = []
        for cell_key, words_map in self.cortical_cells.items():
            if words_map:
                coords = [int(x) for x in cell_key.split(",")]
                s_c, a_c, z_c = coords[0], coords[1], (coords[2] if len(coords) > 2 else 3)
                self.update_cell_centroid_and_emotion(s_c, a_c, z_c, self.strongest_cell_words(cell_key), allow_cleave=False,
                                                      count_visit=False)
            for w in words_map:
                # v21.1: negative words may now be dream threads (nightmares); the bridge word still excludes them
                if self.is_crystal_pure_concept(w, cell_key=cell_key):
                    active_pool.append((w, cell_key))
        if len(active_pool) < 4:
            active_pool = [(w, "4,4,3") for w in self.core_concept_pool if self.is_crystal_pure_concept(w) and w not in self.negative_lexicon and len(w) >= 4]

        used_pairs = set()
        for _ in range(num_dreams):
            if len(active_pool) < 2:
                break
            w1, cell1 = random.choice(active_pool)
            cands = [(w, c) for (w, c) in active_pool if not self.same_stem(w, w1) and (w1, w) not in used_pairs and self.assoc_graph.get(w1, {}).get(w, 0.0) < 1.5] or [(w, c) for (w, c) in active_pool if not self.same_stem(w, w1)]
            if not cands:
                break
            w2, cell2 = random.choice(cands)
            used_pairs.update([(w1, w2), (w2, w1)])
            bridge_word = self.find_conceptual_bridge(w1, w2, exclude={w1, w2} | self.stop_words | self.lean_up_words() | self.get_identity_tokens())

            c1_parts, c2_parts = [int(x) for x in cell1.split(",")], [int(x) for x in cell2.split(",")]
            s_d, a_d, z_d = self.mod7(c1_parts[0] + c2_parts[0] + 1), self.mod7(c1_parts[1] + c2_parts[1] + 1), 6
            dream_coord = f"{s_d},{a_d},{z_d}"

            self.wire_concepts(w1, bridge_word, 0.35, source="dream")
            self.wire_concepts(bridge_word, w2, 0.35, source="dream")
            self.wire_concepts(w1, w2, 0.35, source="dream")

            if bridge_word in self.cortical_cells.get(dream_coord, {}):
                self.cortical_cells[dream_coord][bridge_word] += 1
            _, evolved_mood, _ = self.update_cell_centroid_and_emotion(s_d, a_d, z_d, [w1, w2], allow_cleave=False)

            dream_prop = {
                "subj": w1,
                "rel": f"synthesizes through {bridge_word} into",
                "obj": w2,
                "bridge": bridge_word,
                "cell": dream_coord,
                "summary": f"{w1} synthesizes through {bridge_word} into {w2}",
                "origin": "dream"
            }
            if not any(p["summary"] == dream_prop["summary"] for p in self.idea_memory):
                self.idea_memory.append(dream_prop)
                self.cap_dream_propositions(max_dreams=12)

            dream_idea = f"'{w1}' synthesizes through '{bridge_word}' into '{w2}'"
            dream_text = f"Dream [Z=6]: {dream_idea} -> crystallized cell ({dream_coord}) emotion as '{evolved_mood}'!"
            dream_reports.append(dream_text)
            self.dream_journal.append({"threadA": w1, "threadB": w2, "bridge": bridge_word, "dreamCoord": [s_d, a_d, z_d], "emotionName": evolved_mood, "idea": dream_idea, "summary": dream_text})
        self.dream_journal = self.dream_journal[-30:]

        if not skip_homeostasis:
            self.synthesize_emergent_bot_name()
        if not self.show_tectonics:  # v23.2: collapse the cleavage/annealing lines into one
            dream_reports = [r for r in dream_reports if not (str(r).startswith("Tectonic Cleavage") or "ANNEALING RELIEF" in str(r))]
            note = self.tectonics_note()
            if note:
                dream_reports.insert(0, note)
        return dream_reports

    def export_trace_file(self, filename="latest_trace.json"):
        if not self.last_audit:
            return None  # v24.1: nothing to export yet (it used to run a phantom turn that moved the brain)
        out_path = os.path.abspath(filename)
        # v22.10: cell names in the steps are the names when the path was computed; a cell can be renamed later in the
        # same turn (it learns that turn's words), which is why chat and trace could show different names. Both are kept.
        audit = dict(self.last_audit)
        audit["cellNamesAfterTurn"] = {f"{t['S']},{t['A']},{t['Z']}": self.get_cell_emotion_name(t["S"], t["A"], t["Z"])
                                       for t in (audit["originalTrajectory"][-1], audit["flippedTrajectory"][-1])}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(audit, f, indent=2)
        return out_path

    def init_emotional_lexicon(self):
        for s in range(7):
            for a in range(7):
                for z in range(7):
                    key = f"{s},{a},{z}"
                    seed_name = f"{BRAIN_LIBRARY['S_rough_seeds'][str(s)]}-{BRAIN_LIBRARY['A_rough_seeds'][str(a)]}"
                    self.cell_centroids[key] = list(self.coord_vectors[(s, a, z)])
                    self.cell_lexicon[key] = {"name": seed_name, "seed_name": seed_name, "stage": 1, "visits": 0, "custom": False, "top_words": []}

    def strongest_cell_words(self, cell_key, n=4):
        """v22.7.1 front door: a cell's n strongest words (highest counts). Before, callers took its first n (oldest) words."""
        wm = self.cortical_cells.get(cell_key, {})
        return [w for w, _ in sorted(wm.items(), key=lambda kv: -kv[1])[:n]]

    def get_cell_emotion_name(self, s, a, z=3):
        entry = self.cell_lexicon.get(f"{self.mod7(s)},{self.mod7(a)},{self.mod7(z)}")
        return entry["name"] if entry else "Balanced-Equilibrium"

    def apply_user_emotion_name(self, cell_key, custom_word):
        s_val = int(cell_key.split(",")[0])
        tone_w = BRAIN_LIBRARY["S_band_tones"][str(s_val)][0].strip()
        clean_cap = custom_word.strip().capitalize()
        full_name = clean_cap if "-" in clean_cap else f"{tone_w}-{clean_cap}"
        self.cell_lexicon[cell_key].update({"name": full_name, "stage": 3, "custom": True})
        if self.last_trace_key and self.last_trace_key in self.trace_lexicon:
            self.trace_lexicon[self.last_trace_key].update({"name": f"{clean_cap}-Leap", "custom": True})
        emo_low = clean_cap.lower()
        if emo_low not in self.core_emotion_pool and "-" not in emo_low:
            self.core_emotion_pool.append(emo_low)
        vec = self.get_or_create_vector(emo_low, context_vec=self.cell_centroids[cell_key])
        self.cell_centroids[cell_key] = self.blend(self.cell_centroids[cell_key], vec, 0.65, 0.35)
        return full_name

    def is_valid_emotion_name(self, name_str, s_val=None):
        if not name_str or "-" not in name_str:
            return False
        parts = [p.strip().lower() for p in name_str.split("-")]
        if len(parts) != 2:
            return False
        if s_val is not None and parts[0] not in {w.strip().lower() for w in BRAIN_LIBRARY["S_band_tones"][str(s_val)]}:
            return False
        allowed_second = set(self.core_emotion_pool) | {w.lower() for w in BRAIN_LIBRARY["A_rough_seeds"].values()} | {"shift", "lift", "pivot", "bridge", "centering", "turn", "leap", "awakening", "opening", "reflection", "ascent"}
        return parts[1] in allowed_second

    def synthesize_unique_cell_name(self, s, a, z, cell_vec, mem_vec):
        key = f"{s},{a},{z}"
        used_names = {info["name"] for k, info in self.cell_lexicon.items() if k != key and info.get("stage", 1) >= 2}
        a_axis_vec = self.phrase_to_vector(BRAIN_LIBRARY["A_axes"][str(a)] + " " + BRAIN_LIBRARY["Z_axes"][str(z)])
        core_target = self.blend(mem_vec, a_axis_vec, 0.65, 0.35)
        band_tones = [w.strip().lower() for w in BRAIN_LIBRARY["S_band_tones"][str(s)]]
        scored_tones = sorted([(self.dot(cell_vec, self.vectors[tw]), tw.capitalize()) for tw in band_tones if tw in self.vectors], key=lambda x: x[0], reverse=True)
        scored_cores = sorted([(self.dot(core_target, self.vectors[cw]), cw.capitalize()) for cw in self.core_emotion_pool if cw in self.vectors], key=lambda x: x[0], reverse=True)

        for _, tone_w in scored_tones:
            for _, core_w in scored_cores[:12]:
                if not self.same_stem(tone_w, core_w):
                    cand = f"{tone_w}-{core_w}"
                    if cand not in used_names:
                        return cand
        return f"{BRAIN_LIBRARY['S_rough_seeds'][str(s)]}-{scored_cores[0][1]}"

    # v24.1 finding (Fable 5.2 review #20), kept as is on purpose: "visits" counts sleep passes and loads too, so the
    # crystal rule "at least 2 visits" is met by any cell with words after one sleep. Counting only real visits cut
    # crystals in a 20-day Alice run from 145 to 9: the engine's crystals, and every result since v21.7, rest on the
    # rule as it actually works ("5 pure words"). Changing it would be a design change, not a fix.
    VISITS_COUNT_REFRESHES = True

    def update_cell_centroid_and_emotion(self, s, a, z, turn_concepts, allow_cleave=True, allow_identity=False,
                                         count_visit=True):
        """count_visit=False marks a refresh rather than a visit (sleep passes, loading, cleaving, the bridge's second
        call for the same turn). Refreshes still count while VISITS_COUNT_REFRESHES is True (see there)."""
        key = f"{self.mod7(s)},{self.mod7(a)},{self.mod7(z)}"
        entry = self.cell_lexicon[key]
        if count_visit or self.VISITS_COUNT_REFRESHES:
            entry["visits"] = entry.get("visits", 0) + 1
        id_tokens = self.get_identity_tokens()
        hard_ids = self.get_hard_identity_tokens()  # v21.3: stored words are judged by hard names only
        permit_id = allow_identity or (key == "3,3,3")

        cell_words_map = self.cortical_cells.get(key, {})
        top_cell_words = [
            w for w, _ in sorted(cell_words_map.items(), key=lambda x: x[1], reverse=True)[:6]
            if w in self.vectors and w not in self.stop_words and w not in self.noise_words
            and (permit_id or w not in hard_ids)
        ]
        clean_turn = [
            w for w in turn_concepts[:4]
            if w not in self.stop_words and w not in self.noise_words
            and (permit_id or w not in id_tokens)
        ]
        active_words = list(dict.fromkeys(clean_turn + top_cell_words))
        entry["top_words"] = active_words[:5]

        coord_tuple = (self.mod7(s), self.mod7(a), self.mod7(z))
        mem_vec = self.coord_vectors[coord_tuple]
        if active_words:
            mem_vec = self.phrase_to_vector(" ".join(active_words))
            w_old = 0.50 if entry["visits"] <= 1 else 0.78
            blended = self.blend(self.cell_centroids[key], mem_vec, w1=w_old, w2=(1.0 - w_old))
            self.cell_centroids[key] = self.blend(blended, self.coord_vectors[coord_tuple], w1=0.90, w2=0.10)

        old_name = entry["name"]
        if not entry.get("custom", False) and (active_words or entry["visits"] >= 1):
            entry["name"] = self.synthesize_unique_cell_name(coord_tuple[0], coord_tuple[1], coord_tuple[2], self.cell_centroids[key], mem_vec)
            entry["stage"] = 2

        self.nucleate_or_update_crystal(key, allow_identity=permit_id)
        if allow_cleave:
            self.cleave_crystal(key, notify=True)
        return old_name, entry["name"], entry["stage"]

    def select_trace_movement_noun(self, from_r, to_flip, mean_delta_d):
        s_r, a_r, z_r = from_r[0], from_r[1], (from_r[2] if len(from_r) > 2 else 3)
        s_f, a_f, z_f = to_flip[0], to_flip[1], (to_flip[2] if len(to_flip) > 2 else 3)
        if z_f >= 5 and z_f > z_r: return "Ascent"
        if (s_f, a_f) == (3, 3): return "Centering"
        if a_f > a_r and a_f >= 5: return "Lift"
        if s_f > s_r and s_f >= 5: return "Bridge"
        if s_f < s_r and s_f <= 2: return "Turn"
        if mean_delta_d >= 2.6: return "Leap"
        if a_f >= 4 and s_f >= 4: return "Opening"
        return "Pivot"

    def compute_and_name_trace_emotion(self, audit, thought_trace, user_concepts):
        orig_steps, flip_steps = audit["originalTrajectory"], audit["flippedTrajectory"]
        r_vecs = [self.cell_centroids[f"{st['S']},{st['A']},{st['Z']}"] for st in orig_steps] + [self.vectors[hw] for hw in thought_trace.get("orig_harvest", [])[:3] if hw in self.vectors]
        flip_vecs = [self.cell_centroids[f"{st['S']},{st['A']},{st['Z']}"] for st in flip_steps] + [self.vectors[hw] for hw in (thought_trace.get("flip_harvest", [])[:3] + user_concepts[:3]) if hw in self.vectors]
        v_r, v_flip = self.average_vectors(r_vecs), self.average_vectors(flip_vecs)
        e_trace = self.normalize([vf - 0.65 * vr for vf, vr in zip(v_flip, v_r)])
        if not any(abs(x) > 1e-6 for x in e_trace):
            e_trace = v_flip

        from_r = [orig_steps[-1]["S"], orig_steps[-1]["A"], orig_steps[-1]["Z"]]
        to_flip = [flip_steps[-1]["S"], flip_steps[-1]["A"], flip_steps[-1]["Z"]]
        trace_key = f"R({from_r[0]},{from_r[1]},{from_r[2]})->Flip({to_flip[0]},{to_flip[1]},{to_flip[2]})"
        self.last_trace_key = trace_key

        move_noun = self.select_trace_movement_noun(from_r, to_flip, audit.get("meanDeltaD", 2.0))
        scored_cores = sorted([(self.dot(e_trace, self.vectors[cw]), cw.capitalize()) for cw in self.core_emotion_pool if cw in self.vectors], key=lambda x: x[0], reverse=True)
        best_core = scored_cores[0][1] if scored_cores else "Harmony"

        existing = self.trace_lexicon.get(trace_key)
        if existing:
            existing["count"] = existing.get("count", 1) + 1
            existing["vector"] = [round(x, 4) for x in self.blend(existing["vector"], e_trace, 0.80, 0.20)]
            if not existing.get("custom", False):
                existing["name"] = f"{best_core}-{move_noun}"
        else:
            self.trace_lexicon[trace_key] = {"name": f"{best_core}-{move_noun}", "vector": [round(x, 4) for x in e_trace], "count": 1, "custom": False, "from_r": from_r, "to_flip": to_flip}
        return trace_key, self.trace_lexicon[trace_key]["name"]

    def detect_emotion_co_naming(self, user_text, concepts, quoted):
        low = user_text.lower()
        concepts = [c for c in concepts if c not in self.generic_hubs]  # v21.3: "hello", "night"... are words now, but never a mood name
        if self.pending_question and self.pending_question.get("type") == "NAME_EMOTION":
            if ("sounds like" in low or "call it" in low or "feels like" in low or "is like" in low) and concepts:
                return concepts[0].capitalize(), self.pending_question.get("cell")
            if quoted:
                return quoted[-1].capitalize(), self.pending_question.get("cell")
        naming_triggers = ("call that feeling", "call this feeling", "call that emotion", "call this emotion", "call that state", "call this state", "name that feeling", "name this feeling", "name that emotion", "would call that", "i call that", "i would call it", "let us call it", "let's call it")  # plain "sounds like"/"feels like" only count when the engine just asked for a name
        if any(trig in low for trig in naming_triggers):
            if quoted:
                return quoted[-1].capitalize(), None
            if concepts and ("sounds like" in low or "call" in low or "name" in low):
                return concepts[0].capitalize(), None
        return None, None

    def normalize(self, vec):
        norm = math.sqrt(sum(x * x for x in vec))
        return [0.0] * self.dim if norm < 1e-9 else [x / norm for x in vec]

    def average_vectors(self, vec_list):
        if not vec_list:
            return [0.0] * self.dim
        summed = [0.0] * self.dim
        for v in vec_list:
            for i in range(self.dim):
                summed[i] += v[i]
        return self.normalize(summed)

    def dot(self, v1, v2):
        return sum(a * b for a, b in zip(v1, v2))

    def cosine_similarity(self, v1, v2):
        return self.dot(self.normalize(v1), self.normalize(v2))

    def blend(self, v1, v2, w1=0.5, w2=0.5):
        return self.normalize([w1 * a + w2 * b for a, b in zip(v1, v2)])

    def deterministic_vec(self, seed_text):
        vec = []
        for i in range(self.dim):
            h = hashlib.md5(f"{seed_text}_{i}".encode("utf-8")).hexdigest()
            vec.append((int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0)
        return self.normalize(vec)

    def expand_coords_to_50d(self, x, y=None, word=""):
        if isinstance(x, (list, tuple)):
            coords = x
            if isinstance(y, str) and not word:
                word = y
            if len(coords) == self.dim:
                return self.normalize(coords)
            x_val = max(-3.5, min(3.5, float(coords[0]))) if len(coords) > 0 else 0.0
            y_val = max(-3.5, min(3.5, float(coords[1]))) if len(coords) > 1 else 0.0
        else:
            x_val = max(-3.5, min(3.5, float(x)))
            y_val = max(-3.5, min(3.5, float(y))) if y is not None else 0.0

        harm_vec = self.normalize([
            math.sin((x_val * math.cos((i / float(self.dim)) * math.pi * 2.0) + y_val * math.sin((i / float(self.dim)) * math.pi * 2.0)) * 0.8)
            for i in range(self.dim)
        ])
        seed_key = f"WORD_{word.strip().lower()}" if word else f"COORD_{x_val:.3f}_{y_val:.3f}"
        tex_vec = self.deterministic_vec(seed_key)
        return self.blend(harm_vec, tex_vec, w1=0.85, w2=0.15)

    def init_builtin_50d_space(self):
        cluster_items = list(BRAIN_LIBRARY["semantic_clusters"].items())
        for idx, (cluster_name, words) in enumerate(cluster_items):
            angle = (idx / float(max(1, len(cluster_items)))) * math.pi * 2.0
            cx, cy = math.cos(angle) * 1.25, math.sin(angle) * 1.25
            cluster_axis = self.expand_coords_to_50d(cx, cy, word=cluster_name)
            self.vectors[cluster_name] = list(cluster_axis)
            self.factory_vectors[cluster_name] = list(cluster_axis)
            clean_cluster_words = [w.strip().lower() for w in words]
            for w_low in clean_cluster_words:
                w_vec = self.expand_coords_to_50d(cx, cy, word=w_low)
                self.vectors[w_low] = list(w_vec)
                self.factory_vectors[w_low] = list(w_vec)
                if cluster_name not in self.stop_words and w_low not in self.stop_words and cluster_name != w_low:
                    self.assoc_graph.setdefault(cluster_name, {})[w_low] = 0.35
                    self.assoc_graph.setdefault(w_low, {})[cluster_name] = 0.35
                for w2_low in clean_cluster_words:
                    if w_low != w2_low and w_low not in self.stop_words and w2_low not in self.stop_words:
                        self.assoc_graph.setdefault(w_low, {})[w2_low] = 0.35
        for idx, ew in enumerate(self.tone_pool + self.core_emotion_pool):
            if ew not in self.vectors:
                ang = (idx / float(max(1, len(self.tone_pool) + len(self.core_emotion_pool)))) * math.pi * 2.0
                ew_vec = self.expand_coords_to_50d(math.cos(ang), math.sin(ang), word=ew)
                self.vectors[ew] = list(ew_vec)
                self.factory_vectors[ew] = list(ew_vec)

    def top_principal_components(self, vecs, k=2, iters=60):
        """Top-k principal directions of (already centered) vectors, via covariance + power iteration (pure Python)."""
        if not vecs:
            return []
        cols = [list(col) for col in zip(*vecs)]
        d = len(cols)
        cov = [[0.0] * d for _ in range(d)]
        for i in range(d):
            for j in range(i, d):
                cov[i][j] = cov[j][i] = sum(map(operator.mul, cols[i], cols[j]))
        comps = []
        for _ in range(k):
            v = self.normalize([1.0 + 0.01 * i for i in range(d)])
            for _ in range(iters):
                w = [sum(map(operator.mul, row, v)) for row in cov]
                for c in comps:
                    p = sum(map(operator.mul, w, c))
                    w = [x - p * y for x, y in zip(w, c)]
                norm = math.sqrt(sum(x * x for x in w))
                if norm < 1e-12:
                    break
                v = [x / norm for x in w]
            comps.append(v)
        return comps

    def build_calibrated_axes(self):
        """For full GloVe: build each axis from AXIS_SEEDS and scale it so seed words average about +/-2.5."""
        self.calibrated_axes = {}
        for axis, (pos_words, neg_words) in AXIS_SEEDS.items():
            pos = [self.factory_vectors[w] for w in pos_words if w in self.raw_glove]
            neg = [self.factory_vectors[w] for w in neg_words if w in self.raw_glove]
            if len(pos) < 5 or len(neg) < 5:
                continue
            u = self.normalize([a - b for a, b in zip(self.average_vectors(pos), self.average_vectors(neg))])
            m_pos = sum(self.dot(v, u) for v in pos) / len(pos)
            m_neg = sum(self.dot(v, u) for v in neg) / len(neg)
            if m_pos - m_neg < 1e-6:
                continue
            self.calibrated_axes[axis] = (u, (m_pos + m_neg) / 2.0, 5.0 / (m_pos - m_neg))

    def axis_weight(self, vec, axis):
        """Estimated starting weight of a word on axis A (calm-panic), S (social-isolated) or Z (abstract-concrete)."""
        if axis in self.calibrated_axes:
            u, center, scale = self.calibrated_axes[axis]
            return max(-3.0, min(3.0, scale * (self.dot(vec, u) - center)))  # same range as the hand-set weights
        pa, pb = {"A": (self.pole_calm, self.pole_panic), "S": (self.pole_social, self.pole_isolated),
                  "Z": (self.pole_abstract, self.pole_concrete)}[axis]
        return (self.dot(vec, pa) - self.dot(vec, pb)) * 3.0

    def load_glove(self, glove_file, max_words):
        if max_words <= 0 or glove_file == "__shared_in_ram__":
            return
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [glove_file, os.path.join(script_dir, glove_file)]
        for folder in [".", script_dir]:
            if os.path.exists(folder):
                for fname in os.listdir(folder):
                    if "glove" in fname.lower() and not fname.lower().endswith((".torrentcache.json", ".torrentcache.bin", ".tmp", ".zip")):
                        candidates.append(os.path.join(folder, fname))
        chosen = next((p for p in candidates if os.path.isfile(p)), None)
        if not chosen:
            for folder in [".", script_dir]:  # v22.7.1: the packaged word space that ships with the engine
                packed = os.path.join(folder, self.WORDSPACE_FILE)
                if os.path.isfile(packed) and self.load_packaged_wordspace(packed, max_words):
                    return
            print("\n" + "!" * 82)
            print(f" ⚠️  TEST MODE: no word space found (no GloVe file and no {self.WORDSPACE_FILE}).")
            print(f"    Using {len(self.vectors)} built-in words only. Brains behave very differently in this mode;")
            print(f"    put {self.WORDSPACE_FILE} next to torrentengine.py for normal use.")
            print("!" * 82 + "\n")
            return
        if self.load_glove_cache(chosen, max_words):
            return
        size_mb = os.path.getsize(chosen) / (1024 * 1024)
        print(f"Loading & centering GloVe geometry: {chosen} ({size_mb:.1f} MB) ...")
        temp_coords = {}
        with open(chosen, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                first_tok, last_tok = parts[0].lower(), parts[-1].lower()
                if last_tok.isalpha() and not first_token_is_word(first_tok):
                    word, num_toks = last_tok, parts[:-1]
                elif first_tok.isalpha():
                    word, num_toks = first_tok, parts[1:]
                else:
                    continue
                if len(word) < 2:
                    continue
                try:
                    temp_coords[word] = [float(x) for x in num_toks]
                    self.word_rank[word] = line_num
                    if len(temp_coords) >= max_words:
                        break
                except ValueError:
                    continue
        if not temp_coords:
            return

        # FULL GloVe: a line with exactly self.dim (50) numbers is used as a real embedding
        if all(len(c) == self.dim for c in list(temp_coords.values())[:200]):
            temp_coords = {w: c for w, c in temp_coords.items() if len(c) == self.dim}
            n = float(len(temp_coords))
            means = [sum(c[i] for c in temp_coords.values()) / n for i in range(self.dim)]
            centered = {w: [x - m for x, m in zip(c, means)] for w, c in temp_coords.items()}
            # Remove the dominant shared directions ("all-but-the-top"), which otherwise make most words look alike
            sample = list(centered.values())[:10000]  # the file is in frequency order
            comps = self.top_principal_components(sample, k=2)
            for word, c in centered.items():
                for comp in comps:
                    p = sum(map(operator.mul, c, comp))
                    c = [x - p * y for x, y in zip(c, comp)]
                vec = self.normalize(c)
                self.vectors[word] = vec
                self.factory_vectors[word] = list(vec)
                self.raw_glove[word] = self.factory_vectors[word]  # membership marker; never edited in place
            self.vector_mode = "glove50d"
            self.build_calibrated_axes()
            print(f"Successfully loaded {len(self.raw_glove):,} full {self.dim}-dimension GloVe vectors "
                  f"(mean-centered, top {len(comps)} shared directions removed, {len(self.calibrated_axes)} axes calibrated).")
            self.save_glove_cache(chosen, max_words, list(centered.keys()))
            return

        if any(len(c) > 2 for c in list(temp_coords.values())[:200]):
            print(f"[i] This word file has {len(next(iter(temp_coords.values())))} numbers per word; only {self.dim}-number files are used in full."
                  f" Using its first two numbers instead.")
        self.vector_mode = "map2d"
        n = float(len(temp_coords))
        mean_x = sum(c[0] for c in temp_coords.values()) / n
        mean_y = sum(c[1] for c in temp_coords.values() if len(c) > 1) / n
        std_x = math.sqrt(sum((c[0] - mean_x) ** 2 for c in temp_coords.values()) / n) or 1.0
        std_y = math.sqrt(sum((c[1] - mean_y) ** 2 for c in temp_coords.values() if len(c) > 1) / n) or 1.0
        for word, c in temp_coords.items():
            cx = (c[0] - mean_x) / std_x
            cy = ((c[1] - mean_y) / std_y) if len(c) > 1 else 0.0
            centered = [cx, cy] + c[2:]
            self.raw_glove[word] = centered
            g_vec = self.expand_coords_to_50d(cx, cy, word=word)
            self.vectors[word] = list(g_vec)
            self.factory_vectors[word] = list(g_vec)
        print(f"Successfully loaded & centered {len(self.raw_glove):,} GloVe word vectors on unified 85/15 manifold!")

    WORDSPACE_FILE = "torrent_wordspace_50k.gz"  # v22.7.1

    def load_packaged_wordspace(self, path, max_words):
        """v22.7.1: load the packaged word space (the same processed vectors as the GloVe startup cache)."""
        import gzip, struct
        try:
            with gzip.open(path, "rb") as f:
                (hlen,) = struct.unpack("<I", f.read(4))
                head = json.loads(f.read(hlen).decode("utf-8"))
                nums = array("d")
                nums.frombytes(f.read())
            words, d = head["words"], int(head["dim"])
            if d != self.dim or len(nums) != len(words) * d:
                return False
        except (OSError, ValueError, KeyError, struct.error):
            return False
        for i, word in enumerate(words[:max_words]):
            vec = nums[i * d:(i + 1) * d].tolist()
            self.vectors[word] = vec
            self.factory_vectors[word] = list(vec)
            self.raw_glove[word] = self.factory_vectors[word]
        self.word_rank.update(head.get("word_rank", {}))
        self.vector_mode = "glove50d"
        self.build_calibrated_axes()
        print(f"Loaded {len(self.raw_glove):,} GloVe vectors from the packaged word space ({os.path.basename(path)}).")
        return True

    # v21.2: GloVe startup cache. The first load of a 50-number GloVe file saves the processed
    # (centered, cleaned, normalized) vectors next to it; later startups read them back exactly
    # (full 64-bit precision, so behavior is identical) instead of redoing the slow math.
    GLOVE_CACHE_VERSION = 1

    def glove_cache_paths(self, glove_path):
        base = glove_path + ".torrentcache"
        return base + ".json", base + ".bin"

    def glove_cache_key(self, glove_path, max_words):
        st = os.stat(glove_path)
        return {"cache_version": self.GLOVE_CACHE_VERSION, "source_size": st.st_size,
                "source_mtime": int(st.st_mtime), "max_words": max_words, "dim": self.dim}

    def load_glove_cache(self, glove_path, max_words):
        meta_path, bin_path = self.glove_cache_paths(glove_path)
        if not (os.path.isfile(meta_path) and os.path.isfile(bin_path)):
            return False
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if any(meta.get(k) != v for k, v in self.glove_cache_key(glove_path, max_words).items()):
                return False  # the word file or settings changed: rebuild
            words, nums = meta["words"], array("d")
            with open(bin_path, "rb") as f:
                nums.frombytes(f.read())
            if len(nums) != len(words) * self.dim:
                return False
        except (OSError, ValueError, KeyError, TypeError):
            return False
        d = self.dim
        for i, word in enumerate(words):
            vec = nums[i * d:(i + 1) * d].tolist()
            self.vectors[word] = vec
            self.factory_vectors[word] = list(vec)
            self.raw_glove[word] = self.factory_vectors[word]
        self.word_rank.update(meta.get("word_rank", {}))
        self.vector_mode = "glove50d"
        self.build_calibrated_axes()
        print(f"Loaded {len(self.raw_glove):,} GloVe vectors from the startup cache ({os.path.basename(bin_path)}).")
        return True

    def save_glove_cache(self, glove_path, max_words, words):
        meta_path, bin_path = self.glove_cache_paths(glove_path)
        try:
            nums = array("d")
            for word in words:
                nums.extend(self.factory_vectors[word])
            meta = dict(self.glove_cache_key(glove_path, max_words), words=words, word_rank=self.word_rank)
            for path, mode, payload in ((bin_path, "wb", nums.tobytes()), (meta_path, "w", json.dumps(meta))):
                tmp = path + ".tmp"
                with open(tmp, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
                    f.write(payload)
                os.replace(tmp, path)
            print("[i] Saved a GloVe startup cache, so the next start is much faster.")
        except OSError as e:
            print(f"[i] Could not save the GloVe startup cache ({e}); startup will just stay slower.")

    def get_or_create_vector(self, word, context_vec=None):
        """
        UPGRADE 2.1: Initializes OOV words and hyphenated compounds using contextual
        manifold alignment (80% context/cell centroid + 20% hash, or sub-word mean),
        and enforces Pauli Exclusion (sim < 0.82) + Elastic Factory Tether (cos_sim >= 0.78).
        """
        w = word.strip().lower()
        if w not in self.factory_vectors:
            self.factory_vectors[w] = list(self.compute_contextual_oov_vector(w, context_vec=context_vec))
        if w not in self.vectors:
            self.vectors[w] = list(self.factory_vectors[w])

        if context_vec is not None and any(x != 0.0 for x in context_vec):
            c_norm = self.normalize(context_vec)
            sim = self.dot(self.vectors[w], c_norm)
            pauli_factor = max(0.0, (0.82 - sim) / 0.82)
            alpha = 0.12 * pauli_factor
            if alpha > 1e-4:
                blended = self.blend(self.vectors[w], c_norm, 1.0 - alpha, alpha)
                self.vectors[w] = self.enforce_factory_tether(w, blended)
        return self.vectors[w]

    def phrase_to_vector(self, text):
        tokens = self.clean_tokens(text)
        content = [w for w in tokens if w not in self.stop_words] or tokens
        vecs = [self.vectors[w] for w in content if w in self.vectors]
        return self.average_vectors(vecs) if vecs else self.expand_coords_to_50d(0.0, 0.0, word=text or "seed_equilibrium")

    def build_coordinate_vectors(self):
        coords = {}
        for s in range(7):
            for a in range(7):
                for z in range(7):
                    desc = f"{BRAIN_LIBRARY['S_axes'][str(s)]} {BRAIN_LIBRARY['A_axes'][str(a)]} {BRAIN_LIBRARY['Z_axes'][str(z)]}"
                    coords[(s, a, z)] = self.phrase_to_vector(desc)
        return coords

    def normalize_cell_key(self, cell_str):
        parts = [int(x) for x in str(cell_str).split(",") if x.strip().isdigit()]
        if len(parts) == 2:
            return f"{self.mod7(parts[0])},{self.mod7(parts[1])},3"
        elif len(parts) >= 3:
            return f"{self.mod7(parts[0])},{self.mod7(parts[1])},{self.mod7(parts[2])}"
        return "3,3,3"

    # =================================================================
    # NEGATION-AWARE PROPOSITION EXTRACTION
    # =================================================================
    def find_negated_concepts_in_tokens(self, tokens, user_text=None):
        """Words negated by "not", "never", "no"... A negation only reaches words later in the same clause
        (clauses end at . ! ? ; : , or "but"), and a standalone "No." / "Nope," answer negates nothing."""
        if user_text is None:
            clauses = [tokens]
        else:
            clauses = [self.clean_tokens(part) for part in re.split(r"[.!?;:,]+|\bbut\b", user_text.lower())]
        negated = set()
        for clause in clauses:
            if len(clause) <= 1 or (clause and clause[0] in {"no", "nope", "nah"} and len(clause) == 1):
                continue
            for idx, tok in enumerate(clause):
                if tok in self.negation_tokens:
                    if self.negation_v2:  # v23.3.3: only the word the "not" is attached to (see negation_target)
                        negated.update(self.negation_target(clause, idx)[0])
                        continue
                    for look_ahead in clause[idx + 1:idx + 6]:
                        if look_ahead not in self.stop_words and len(look_ahead) >= 3:
                            negated.add(look_ahead)
        return negated

    # v23.3.3 negation scope. Old rule: every concept in the 5 words after "not". That negated words the "not" wasn't
    # about ("not afraid of the SILENCE", "never the whole story when CURIOSITY is awake"), which mattered little while
    # negated words were only dropped, but would flip their feelings now that negated words push the other way.
    NEG_FILLERS = {"a", "an", "the", "just", "very", "really", "so", "too", "even", "only", "quite", "that", "all",
                   "my", "your", "our", "his", "her", "their", "its", "any", "much", "at", "ever", "always", "be"}
    NEG_STOPS = {"when", "because", "if", "while", "although", "though", "since", "who", "which", "whereas", "unless",
                 "until", "but", "however", "yet", "whether"}
    NEG_COPULAS = {"is", "are", "was", "were", "am"}
    NEG_SUBJ_SKIP = {"a", "an", "the", "my", "your", "our", "his", "her", "their", "its"}  # "that isn't X": no subject

    def negation_target(self, clause, idx):
        """v23.3.3: what the negation at clause[idx] is about. Returns (negated words, index of the first one or None).
        The first real word after it (skipping fillers like "a", "the", "just"), plus words joined to it by "or"/"nor"
        ("not math or code"). If that first real word is a stop word ("don't KNOW the math", "not SURE if"), the
        negation is about something that isn't stored as a concept, so nothing is negated. Never crosses NEG_STOPS."""
        out, first, j = [], None, idx + 1
        while j < len(clause):
            w = clause[j]
            if w in self.NEG_STOPS or w in self.negation_tokens:
                break
            if w in self.NEG_FILLERS:
                j += 1
                continue
            if w in self.stop_words or len(w) < 3:
                break  # the "not" is about a stop word: negate nothing
            out.append(w)
            first = j if first is None else first
            # "not X or Y" / "neither X nor Y": the next filler-skipped word after or/nor is negated too
            k = j + 1
            if k < len(clause) and clause[k] in {"or", "nor"}:
                k += 1
                while k < len(clause) and clause[k] in self.NEG_FILLERS:
                    k += 1
                if k < len(clause) and clause[k] not in self.stop_words and clause[k] not in self.NEG_STOPS and len(clause[k]) >= 3:
                    j = k
                    continue
            break
        return out, first

    def negation_rejections(self, tokens, user_text):
        """v23.3.3 (option C): the pairs a negated sentence really says don't go together. Only "X is not Y" shapes: a
        concept, then is/are/was/were/am + a negation, then the negated word(s) ("A thought is not a physical thing" ->
        thought / physical). "I'm not afraid", "we don't need a map", "I don't know the math" give no pairs."""
        clauses = [self.clean_tokens(part) for part in re.split(r"[.!?;:,]+|\bbut\b", (user_text or " ".join(tokens)).lower())]
        pairs = []
        for clause in clauses:
            for idx, tok in enumerate(clause):
                if tok not in self.negation_tokens or idx < 2 or clause[idx - 1] not in self.NEG_COPULAS:
                    continue
                subj = None
                for w in reversed(clause[:idx - 1]):  # the word right before the copula (articles skipped) is the subject
                    if w in self.NEG_SUBJ_SKIP:
                        continue
                    if w not in self.stop_words and len(w) >= 3 and self.is_valid_concept_node(w):
                        subj = w
                    break  # "I am not ...": the subject is a pronoun, so no pair
                if not subj:
                    continue
                for obj in self.negation_target(clause, idx)[0]:
                    if obj != subj and self.is_valid_concept_node(obj):
                        pairs.append((subj, obj))
        return pairs

    def extract_proposition(self, user_text, tokens, concepts, cell_key, wire=True):
        """wire=False (v24.1, the bridge for reply text): don't link the pair here; the returned idea carries
        "_wire": (subj, obj, amount) so the caller can link it after checking that both words are grounded."""
        if "?" in user_text or len(tokens) < 3:
            return None
        raw_words = [w.strip(".,!?;:\"'()[]{}").lower() for w in user_text.split()]
        if (set(tokens) & self.negation_tokens) or (set(raw_words) & self.negation_tokens):
            if not self.negation_v2:  # v23.3.3: _learn_from_turn already recorded these (they were counted twice: 0.6)
                neg_c = self.find_negated_concepts_in_tokens(tokens, user_text)
                pos_c = [c for c in concepts if c not in neg_c]
                for pc in pos_c:
                    for nc in neg_c:
                        self.record_rejection(pc, nc, strength=self.REJECT_NEGATION)
            return None

        id_tokens = self.get_identity_tokens()
        non_id_concepts = [c for c in concepts if c not in id_tokens]
        joined = " ".join(tokens)
        if joined.startswith(("it leads to", "that leads to", "which leads to", "i think it leads to")) and self.last_topic and non_id_concepts:
            if self.is_crystal_pure_concept(self.last_topic, cell_key=cell_key) and self.is_crystal_pure_concept(non_id_concepts[0], cell_key=cell_key):
                prop = {"subj": self.last_topic, "rel": "leads naturally to", "obj": non_id_concepts[0], "cell": cell_key, "summary": f"{self.last_topic} leads naturally to {non_id_concepts[0]}", "origin": "waking"}
                if not any(p["summary"] == prop["summary"] for p in self.idea_memory):
                    self.idea_memory.append(prop)
                if wire:
                    self.wire_concepts(self.last_topic, non_id_concepts[0], 2.5)
                else:
                    prop["_wire"] = (self.last_topic, non_id_concepts[0], 2.5)
                return prop
        if len(non_id_concepts) < 2:
            return None

        c1, c2 = non_id_concepts[0], non_id_concepts[1]
        if c1 in tokens and c2 in tokens:
            i1, i2 = tokens.index(c1), tokens.index(c2)
            if 1 < (i2 - i1) <= 4:
                mid_tokens = tokens[i1 + 1:i2]
                mid_phrase = " ".join(mid_tokens).strip()
                if len(mid_phrase) >= 4 and not (set(mid_tokens) & self.stop_words) and mid_phrase not in self.custom_verb_bridges:
                    self.custom_verb_bridges.append(mid_phrase)

        rel_patterns = [
            r"([a-z\s]{3,25}?)\s+(can make you feel|makes me feel|makes me|make you|brings|bring|creates|leads to|lead to|causes|cause|helps|help|means|is connected to|goes with|go together with|reminds me of|is part of|needs|need|transforms|shapes|opens the door to|builds|requires|inspires)\s+([a-z\s]{3,25})",
            r"([a-z]+)\s+and\s+([a-z]+)\s+(go together|connect|fit together|belong together|work together|help each other)"
        ]
        for pat in rel_patterns:
            m = re.search(pat, joined)
            if m:
                if len(m.groups()) == 3 and m.group(3) in ("go together", "connect", "fit together", "belong together", "work together", "help each other"):
                    subj, obj, rel = m.group(1).strip(), m.group(2).strip(), "connects naturally with"
                else:
                    subj, rel, obj = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
                if rel == "create" or ((set(subj.split()) | set(rel.split()) | set(obj.split())) & self.negation_tokens):
                    return None
                subj = re.sub(r"^(sometimes|that|this|the|a|an|how|when|because|if|it|i think)\s+", "", subj).strip()
                obj = re.sub(r"^(the|a|an|very|so|really|to)\s+", "", obj).strip()
                subj_c, _ = self.extract_concepts(subj, subj.split())
                obj_c, _ = self.extract_concepts(obj, obj.split())
                if not subj_c or not obj_c:
                    return None
                clean_subj, clean_obj = subj_c[0], obj_c[0]
                if clean_subj in id_tokens or clean_obj in id_tokens:
                    return None
                # v21.4: "X means a b c" is a definition (kept whole in knowledge_facts by learn_definitions); cutting it
                # down to one word made misleading ideas like "tcm means crystalline" that the bridge sent to the LLM
                if rel == "means" and (len(obj_c) > 1 or clean_subj in self.turn_taught):
                    return None
                if self.is_valid_concept_node(clean_subj) and self.is_valid_concept_node(clean_obj) and clean_subj != clean_obj:
                    prop = {"subj": clean_subj, "rel": rel, "obj": clean_obj, "cell": cell_key, "summary": f"{clean_subj} {rel} {clean_obj}", "origin": "waking"}
                    if not any(p["summary"] == prop["summary"] for p in self.idea_memory):
                        self.idea_memory.append(prop)
                        self.cap_dream_propositions(max_dreams=12)
                    if wire:
                        self.wire_concepts(clean_subj, clean_obj, amount=2.2)
                    else:
                        prop["_wire"] = (clean_subj, clean_obj, 2.2)
                    return prop
        return None

    def find_related_idea(self, concepts):
        for c in concepts:
            for prop in reversed(self.idea_memory):
                if prop.get("origin", "waking") == "waking" and (c == prop["subj"] or c == prop["obj"]) and prop["summary"] not in self.spoken_chains:
                    return prop
        for c in concepts:
            for prop in reversed(self.idea_memory):
                if (c == prop["subj"] or c == prop["obj"]) and prop["summary"] not in self.spoken_chains:
                    return prop
        return None

    def compute_curiosity_target(self):
        id_tokens = self.get_identity_tokens()
        sparse_concepts = []
        for cell_k, words_map in self.cortical_cells.items():
            for w in words_map:
                if w not in self.stop_words and w not in self.noise_words and w not in id_tokens:
                    sparse_concepts.append((len(self.assoc_graph.get(w, {})), w, cell_k))
        sparse_concepts.sort(key=lambda x: x[0])
        explored_cells = sum(1 for m in self.cortical_cells.values() if len(m) > 0)
        if sparse_concepts:
            _, target_w, cell_k = sparse_concepts[0]
            return target_w, self.find_conceptual_bridge(target_w, "understand", exclude={target_w} | self.stop_words | id_tokens), cell_k, explored_cells
        return "storms", "nature", "3,3,3", explored_cells

    def same_stem(self, w1, w2):
        if not w1 or not w2:
            return False
        w1, w2 = w1.lower(), w2.lower()
        if w1 == w2:
            return True
        # v24.1: the same word with an ending (learn/learning, hope/hoping, happy/happiness), not any two words that
        # share 4 letters (computer and company, program and progress could never be linked). v24.1.1: also two forms
        # of one word (learned/learning, run/running), and only if the original meanings agree (part/party, flow/flower,
        # even/evening look like word + ending but aren't)
        key = (w1, w2) if w1 < w2 else (w2, w1)
        hit = self._stem_cache.get(key)
        if hit is None:
            hit = self.stem_of(w1) == self.stem_of(w2) or self._one_plus_ending(w1, w2)
            if hit:
                v1, v2 = self.raw_glove.get(w1), self.raw_glove.get(w2)
                if v1 is not None and v2 is not None and self.cosine_similarity(v1, v2) < self.STEM_MIN_SIMILARITY:
                    hit = False
            if len(self._stem_cache) > 200000:
                self._stem_cache.clear()
            self._stem_cache[key] = hit
        return hit

    STEM_MIN_SIMILARITY = 0.5

    def _one_plus_ending(self, w1, w2):
        short, long_ = sorted((w1, w2), key=len)
        if len(short) < 3:
            return False
        for base in {short, short[:-1] if short.endswith("e") else short, short[:-1] + "i" if short.endswith("y") else short}:
            if long_.startswith(base) and long_[len(base):] in self.STEM_ENDINGS:
                return True
        return False

    def stem_of(self, w):
        """v24.1.1: a rough stem: the longest listed ending removed (at least 3 letters left), a doubled last consonant
        undone (running -> run), a final i/e evened out."""
        for end in sorted(self.STEM_ENDINGS, key=len, reverse=True):
            if w.endswith(end) and len(w) - len(end) >= 3:
                w = w[:-len(end)]
                break
        if len(w) >= 4 and w[-1] == w[-2] and w[-1] not in "aeiouls":
            w = w[:-1]
        return w.rstrip("e").replace("i", "y") if len(w) > 3 else w

    STEM_ENDINGS = {"s", "es", "d", "ed", "ing", "er", "ers", "ly", "ness", "ful", "y", "ies", "ied", "ment", "ments", "ion",
                    "ions", "ity", "al", "est", "ings", "ive", "ous", "ally", "ical", "ically", "ation", "ations"}

    def extract_quoted_words(self, user_text):
        temp = user_text
        for k, v in CONTRACTIONS.items():
            temp = re.sub(rf"\b{re.escape(k)}\b", v, temp, flags=re.IGNORECASE)
        return [m.lower() for m in re.findall(r"['\"]([a-zA-Z\-]+)['\"]", temp) if len(m) >= 2]

    # v21.3 (#8): punctuation INSIDE a token now separates words instead of vanishing. Before, every non-letter was
    # deleted, so "reflection—a" became the new word "reflectiona", "and/or" -> "andor", "rest.Sleep" -> "restsleep",
    # and "Hope's" -> "hopes" (a different word from the name "hope").
    GREETING_TIME_WORDS = {"morning", "evening", "afternoon"}

    def clean_tokens(self, text):
        text = text.lower().replace("’", "'").replace("‘", "'")
        text = re.sub(r"[‒–—―…/\\]|-{2,}|\.{2,}", " ", text)  # dashes, ellipses, slashes
        expanded = []
        for token in text.split():
            stripped = token.strip(".,!?;:\"'()[]{}")
            if stripped in CONTRACTIONS:
                expanded.extend(CONTRACTIONS[stripped].split())
                continue
            if stripped.endswith("'s"):
                stripped = stripped[:-2]  # possessive: "hope's" -> "hope" ("it's", "that's"... were handled above)
            joined = stripped.replace("'", "")
            if joined in CONTRACTIONS:  # "dont", "im"...
                expanded.extend(CONTRACTIONS[joined].split())
                continue
            # hyphens, periods, digits or any other non-letter inside the token split it ("self-aware" -> self, aware)
            for part in re.split(r"[^a-z']+", stripped):
                clean = part.replace("'", "")
                if clean in CONTRACTIONS:
                    expanded.extend(CONTRACTIONS[clean].split())
                elif clean:
                    expanded.append(clean)
        # Greetings: "good night" is a farewell, not darkness. It becomes GloVe's own word "goodnight" (warm, social);
        # in "good morning / evening / afternoon" the time word is dropped and "good" stays.
        # ("a good night of sleep", "the good morning light", "last good night" are not greetings and stay as they are.)
        merged = []
        for t in expanded:
            greeting = (merged and merged[-1] == "good"
                        and (len(merged) < 2 or merged[-2] not in {"a", "an", "the", "one", "every", "last", "another", "this", "that", "such", "very", "really", "so"}))
            if greeting and t == "night":
                merged[-1] = "goodnight"
            elif greeting and t in self.GREETING_TIME_WORDS:
                continue
            else:
                merged.append(t)
        return merged

    def word_salience(self, word, is_quoted=False):
        if is_quoted:
            return 25.0
        if word in self.stop_words or len(word) < 3:
            return 0.0
        return math.log10(max(10, self.word_rank.get(word, 8000))) + abs(self.word_weights.get(word, 0.0)) * 0.5 + min(1.5, len(word) * 0.15)

    def extract_concepts(self, user_text, tokens):
        quoted = self.extract_quoted_words(user_text)
        quoted_set, seen, candidates = set(quoted), set(), []
        for qw in quoted:
            if qw not in seen and qw not in self.stop_words:
                seen.add(qw)
                candidates.append((self.word_salience(qw, True), qw))
        for w in tokens:
            if w not in seen and w not in self.stop_words and len(w) >= 3:
                seen.add(w)
                candidates.append((self.word_salience(w, w in quoted_set), w))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [w for _, w in candidates], quoted

    # =================================================================
    # TASK 1, 2 & 3: DEEP MEMORY SANITIZATION, ARCHETYPE REPAIR & RE-ANCHORING
    # =================================================================
    def is_valid_concept_node(self, w):
        if not w or not isinstance(w, str):
            return False
        w_low = w.strip().lower()
        return " " not in w_low and len(w_low) >= 3 and w_low not in self.stop_words and w_low not in self.noise_words

    def is_valid_proposition(self, p):
        s_w = str(p.get("subj", "")).strip().lower()
        o_w = str(p.get("obj", "")).strip().lower()
        rel = str(p.get("rel", "")).strip().lower()
        b_w = str(p.get("bridge", "")).strip().lower()
        if rel == "create":
            return False
        if not self.is_valid_concept_node(s_w) or not self.is_valid_concept_node(o_w):
            return False
        if b_w and not self.is_valid_concept_node(b_w):
            return False
        bad_pairs = {("truth", "deceive"), ("deceive", "truth"), ("true", "deceive"), ("deceive", "true"), ("truth", "lie"), ("lie", "truth"), ("true", "lie"), ("lie", "true")}
        if (s_w, o_w) in bad_pairs:
            return False
        m = re.search(r"synthesizes through\s+([a-z\-]+)\s+into", rel)
        if m and not self.is_valid_concept_node(m.group(1)):
            return False
        return True

    def repair_archetype_and_idempotent_links(self):
        """Clean the loaded link graph: drop self-links and links to invalid words, and make every link symmetric.
        v21.9: no longer lifts weak links back to 0.25 and no longer re-creates the built-in starter links on every load
        (both undid the day-scaled link fading; protecting starter links re-saturated a busy test brain)."""
        for w1, links in list(self.assoc_graph.items()):
            for w2, val in list(links.items()):
                if w1 == w2 or not self.is_valid_concept_node(w1) or not self.is_valid_concept_node(w2):
                    links.pop(w2, None)
                    continue
                sym_val = round(max(float(val), float(self.assoc_graph.setdefault(w2, {}).get(w1, val))), 2)
                self.assoc_graph[w1][w2] = sym_val
                self.assoc_graph[w2][w1] = sym_val

    def load_memory(self):
        defaults_a = {
            "panic": -3.0, "scared": -2.5, "worry": -2.0, "afraid": -2.0, "bad": -1.5, "fail": -2.0,
            "stress": -2.0, "fear": -2.5, "scare": -2.0, "loss": -1.5, "tense": -1.5, "confused": -1.0,
            "threat": -2.5, "dangerous": -2.5, "overwhelmed": -2.0, "guarded": -1.5, "lie": -2.5, "deceive": -2.8,
            "calm": 2.5, "logic": 3.0, "logically": 3.0, "truth": 2.8, "true": 2.5, "boundary": 2.0,
            "clear": 2.5, "respect": 3.0, "honest": 2.8, "breathe": 2.0, "rest": 1.5, "safe": 2.5,
            "healthy": 2.0, "accurate": 2.5, "excited": 2.8, "happy": 3.0, "happiness": 3.0, "good": 2.2,
            "great": 2.5, "working": 2.5, "fixed": 2.0, "code": 2.0, "better": 2.0, "incredible": 3.0,
            "amazed": 3.0, "amazing": 3.0, "awesome": 3.0, "wonderful": 2.8, "existence": 2.0, "sense": 2.0,
            "affirmative": 2.0, "thank": 2.5, "thanks": 2.5, "learn": 2.5, "learning": 2.5,
            "cooperation": 3.0, "facility": 2.0, "love": 3.0, "excellent": 3.0,
            "feel": 1.5, "coordinates": 1.5, "storms": 1.8, "weather": 1.5, "rain": 1.5,
            "harmony": 2.5, "wonder": 2.8, "glad": 2.5, "nice": 2.2, "meet": 2.0, "curiosity": 2.5,
            "wisdom": 2.8, "kindness": 2.8, "trust": 2.8
        }
        defaults_s = {
            "guarded": -2.0, "cautious": -1.2, "hesitant": -1.2, "closed": -1.8, "alone": -2.0,
            "solitary": -1.5, "afraid": -1.2, "scared": -1.2, "lie": -2.2, "deceive": -2.5,
            "together": 3.0, "conversation": 2.5, "share": 2.5, "open": 2.5, "friend": 3.0,
            "cooperative": 2.5, "cooperation": 3.0, "respect": 2.5, "connect": 2.5, "happy": 2.5,
            "happiness": 2.5, "excited": 2.2, "love": 3.0, "thank": 2.5, "empathy": 2.8,
            "glad": 2.0, "nice": 2.0, "meet": 2.5, "curiosity": 2.0, "kindness": 3.0, "trust": 2.8,
            "truth": 2.5, "true": 2.2, "honest": 2.8
        }
        defaults_z = {
            "wisdom": 2.5, "insight": 2.5, "pattern": 2.0, "structure": 2.0, "logic": 2.0,
            "learn": 1.8, "learning": 1.8, "curiosity": 2.0, "existence": 2.5, "coordinates": 2.0,
            "dream": 2.2, "mystery": 2.0, "truth": 2.2, "true": 2.0, "honest": 2.0, "harmony": 1.8
        }
        self.word_weights = {k.lower(): v for k, v in defaults_a.items() if k.lower() not in self.stop_words}
        self.factory_word_weights = dict(self.word_weights)
        self.social_weights = {k.lower(): v for k, v in defaults_s.items() if k.lower() not in self.stop_words}
        self.epistemic_weights = {k.lower(): v for k, v in defaults_z.items() if k.lower() not in self.stop_words}
        for s in range(7):
            for a in range(7):
                for z in range(7):
                    self.cortical_cells[f"{s},{a},{z}"] = {}

        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # v22: sleep pressure carried over from the last session (read before the wake-up sleep below uses it)
                    sp = data.get("sleep_pressure", {}) if isinstance(data.get("sleep_pressure"), dict) else {}
                    self.cells_added_since_sleep = float(sp.get("cells", 0.0))
                    self.link_strength_added_since_sleep = float(sp.get("links", 0.0))
                    self.links_used_since_sleep = {tuple(p) for p in sp.get("used", []) if isinstance(p, list) and len(p) == 2}
                    self.new_links_since_sleep = int(sp.get("new_links", 0))
                    self.sleep_link_added = float(sp.get("sleep_links", 0.0))  # v24.1
                    self.last_sleep = data.get("last_sleep", {}) if isinstance(data.get("last_sleep"), dict) else {}  # v22.1
                    self.nightmare_mode = bool(data.get("nightmare_mode", False))  # v22.3
                    if data.get("governor_mode") in ("FLIPPED", "ORIGINAL"):  # v22.7.1: /flip is saved per brain
                        self.governor_mode = data["governor_mode"]
                    ls = data.get("link_sources")  # v22.7 (absent in older brains: every link is legacy)
                    self.link_sources = {k: {s: float(x) for s, x in v.items()} for k, v in ls.items()
                                         if isinstance(v, dict)} if isinstance(ls, dict) else {}
                    if "source_tags_on" in data:
                        self.source_tags_on = bool(data["source_tags_on"])
                    self.mood_level_on = bool(data.get("mood_level_on", False))  # v22.6
                    self.levels_on = bool(data.get("levels_on", True))  # v23 (older brains: on)
                    self.arousal = float(data.get("arousal", 0.0))
                    self.arousal_mean = float(data.get("arousal_mean", 0.0))
                    vl = data.get("valence_level")  # v23.3 (absent: read from the calm position once)
                    self.valence_level = max(-1.0, min(1.0, float(vl))) if isinstance(vl, (int, float)) else None
                    self.novelty = max(0.0, min(1.0, float(data.get("novelty", self.NOVELTY_REST))))
                    self.idle_menu_on = bool(data.get("idle_menu_on", True))  # v23.4
                    self.rhythm_on = bool(data.get("rhythm_on", False))  # v24.0
                    try:
                        self.rhythm_offset = max(-12.0, min(12.0, float(data.get("rhythm_offset", 0.0))))
                    except (TypeError, ValueError):
                        self.rhythm_offset = 0.0
                    fu = data.get("felt_usual")
                    self.felt_usual = float(fu) if isinstance(fu, (int, float)) and fu >= 0 else None
                    self.idle_habits = {k: float(x) for k, x in (data.get("idle_habits") or {}).items() if k in self.IDLE_OPTIONS + ("speak",)}
                    self.idle_outcome_mean = float(data.get("idle_outcome_mean", 0.0))
                    self.awake_minutes = max(0.0, float(sp.get("awake_minutes", 0.0)))
                    self.recent_turns = [t for t in (data.get("recent_turns") or []) if isinstance(t, dict)][-self.RECENT_TURNS_KEEP:]
                    cls = data.get("caretaker_last_seen")
                    self.caretaker_last_seen = float(cls) if isinstance(cls, (int, float)) else None
                    self.idle_on = bool(data.get("idle_on", False))  # v22.8
                    self.idle_visits = {k: float(v) for k, v in (data.get("idle_visits") or {}).items()}
                    self.idle_journal = list(data.get("idle_journal") or [])[-10:]
                    self.last_idle = self.idle_journal[-1] if self.idle_journal else None
                    self.a_push_mean = float(data.get("a_push_mean", 0.0))
                    self.speaker_tone = dict(data.get("speaker_tone", {}) or {})  # v23.4.1
                    self.a_level_resid = float(data.get("a_level_resid", 0.0))
                    self.turn_counter = int(data.get("turn_counter", 0))
                    self.split_rest = {k: int(v) for k, v in data.get("split_rest", {}).items()
                                       if isinstance(v, (int, float)) and self.turn_counter - v < self.SPLIT_REST_TURNS}

                    loaded_prof = data.get("user_profile", {})
                    if isinstance(loaded_prof, dict):
                        self.user_profile = {
                            "user_name": str(loaded_prof.get("user_name", "")).strip().lower(),
                            "bot_name": str(loaded_prof.get("bot_name", "")).strip(),
                            "pending_bot_name": str(loaded_prof.get("pending_bot_name", "")).strip(),
                            "pending_name_origin": str(loaded_prof.get("pending_name_origin", "")).strip()
                        }

                    self._apply_env_overrides()  # v24.1.1: the snap-back below follows TORRENT_NIGHTMARE too
                    for k, v in data.get("word_weights", {}).items():
                        kl = k.strip().lower()
                        if self.is_valid_concept_node(kl):
                            # v21.1: keep learned negative weights on load (the old +0.5 reset erased them for any word not in negative_lexicon)
                            # v22.7.1: the snap-back of positive built-in words is a lean-up rule, so nightmare mode keeps the learned score
                            snap = kl in defaults_a and defaults_a[kl] > 0 and v < 0 and not self.nightmare_mode
                            self.word_weights[kl] = defaults_a[kl] if snap else v
                    for k, v in data.get("social_weights", {}).items():
                        kl = k.strip().lower()
                        if self.is_valid_concept_node(kl):
                            self.social_weights[kl] = v
                    for k, v in data.get("epistemic_weights", {}).items():
                        kl = k.strip().lower()
                        if self.is_valid_concept_node(kl):
                            self.epistemic_weights[kl] = v

                    # Learned vectors only make sense in the word space they were learned in
                    saved_mode = data.get("vector_mode")
                    skip_learned = bool(saved_mode) and saved_mode != self.vector_mode
                    if skip_learned:
                        print(f"[!] This brain was saved with word space '{saved_mode}', but '{self.vector_mode}' is loaded now."
                              f" Keeping its memories and links, but not its learned word vectors."
                              f" For clean comparisons, use a separate folder for each word space.")
                    # UPGRADE 2.1: Initialize OOV / hyphenated learned vectors with contextual tethers
                    for w, vec in ([] if skip_learned else data.get("learned_vectors", {}).items()):
                        wl = w.strip().lower()
                        if self.is_valid_concept_node(wl) and isinstance(vec, list) and len(vec) == self.dim:
                            if any(abs(float(x)) > 1e-6 for x in vec):
                                loaded_v = self.normalize([float(x) for x in vec])
                                # v24.1: a learned meaning loads as saved (it used to be blended 55/45 back toward the
                                # original meaning at every load, so a few restarts undid most of what a word learned).
                                # The waking tether still applies: never further than learning itself allows.
                                self.vectors[wl] = self.enforce_factory_tether(wl, loaded_v)
                                self.core_concept_pool.add(wl)
                    self.recompute_poles_and_coords()

                    self.knowledge_facts.update(data.get("knowledge_facts", {}))
                    # v22.6.4: crystals are rebuilt from the cells below, but annealing's demoted words must survive
                    self.saved_demoted = {self.normalize_cell_key(ck): list(c.get("demoted", []))
                                          for ck, c in data.get("crystal_lattices", {}).items()
                                          if isinstance(c, dict) and c.get("demoted")}
                    for ck, ws in (data.get("pending_demoted") or {}).items():  # lists whose crystal hadn't re-formed yet
                        if isinstance(ws, list) and ws:
                            self.saved_demoted.setdefault(self.normalize_cell_key(ck), list(ws))
                    for _w, _r in (data.get("rejected_links", {}) or {}).items():  # v23.1: weighted, fading rejections
                        if isinstance(_r, dict):
                            self.rejected_links[_w] = {k: float(v) for k, v in _r.items()}
                        else:  # older brains: a permanent list; becomes medium strength and fades like the rest
                            self.rejected_links[_w] = {k: self.REJECT_LEGACY for k in _r}
                    self.cleavage_log = data.get("cleavage_log", [])[-30:]
                    self.bridge_habituation = {k: float(v) for k, v in data.get("bridge_habituation", {}).items()
                                               if isinstance(v, (int, float)) and v >= 0.05}
                    self.experienced_words = set(data.get("experienced_words", []))
                    exp = data.get("expectation")  # v22.5
                    self.expectation = exp if isinstance(exp, dict) and "words" in exp else None
                    self.surprise_baseline = float(data.get("surprise_baseline", 0.5))
                    ws = data.get("word_sightings")  # v22.4; absent in older brains (set up on the first turn)
                    self.word_sightings = {k: int(v) for k, v in ws.items()} if isinstance(ws, dict) else None
                    self.seen_once_ready = bool(data.get("seen_once_ready", False))  # v22.11
                    self.people = {k: dict(v) for k, v in (data.get("people") or {}).items()}  # v23.2
                    for _pn in list(self.people):
                        self.person_start_numbers(_pn)  # v23.2 fix for people met before it
                    self.show_tectonics = bool(data.get("show_tectonics", False))

                    for vb in data.get("custom_verb_bridges", data.get("verb_bridges", [])):
                        vb_toks = vb.lower().split()
                        if 1 <= len(vb_toks) <= 3 and not (set(vb_toks) & self.stop_words) and vb not in self.custom_verb_bridges:
                            self.custom_verb_bridges.append(vb)

                    for p in data.get("idea_memory", []):
                        p["subj"] = str(p.get("subj", "")).strip().lower()
                        p["obj"] = str(p.get("obj", "")).strip().lower()
                        p["rel"] = str(p.get("rel", "")).strip().lower()
                        p["summary"] = f"{p['subj']} {p['rel']} {p['obj']}"
                        if "synthesizes through" in p["rel"] or "synthesizes through" in p.get("summary", ""):
                            p["origin"] = p.get("origin", "dream")
                            m = re.search(r"synthesizes through\s+([a-z\-]+)\s+into", p["rel"])
                            if m:
                                p["bridge"] = m.group(1)
                        else:
                            p["origin"] = p.get("origin", "waking")

                        if self.is_valid_proposition(p) and not any(ep["summary"] == p["summary"] for ep in self.idea_memory):
                            p["cell"] = self.normalize_cell_key(p.get("cell", "3,3,3"))
                            self.idea_memory.append(p)
                    self.cap_dream_propositions(max_dreams=12)

                    saved_seed = data.get("seed_coord", [3, 3, 3])
                    if isinstance(saved_seed, list) and len(saved_seed) >= 2:
                        self.seed_s, self.seed_a = self.mod7(saved_seed[0]), self.mod7(saved_seed[1])
                        self.seed_z = self.mod7(saved_seed[2]) if len(saved_seed) > 2 else 3
                    saved_vel = data.get("velocity", [0.0, 0.0, 0.0])
                    if isinstance(saved_vel, list) and len(saved_vel) >= 2:
                        self.vel_s, self.vel_a = float(saved_vel[0]), float(saved_vel[1])
                        self.vel_z = float(saved_vel[2]) if len(saved_vel) > 2 else 0.0

                    self.dream_journal = [
                        d for d in data.get("dream_journal", [])
                        if self.is_valid_concept_node(d.get("bridge", "")) and self.is_valid_concept_node(d.get("threadA", "")) and self.is_valid_concept_node(d.get("threadB", "")) and d.get("bridge") not in self.lean_up_words()
                    ]

                    # UPGRADE 1.3: Clean legacy identity_tokens out of non-(3,3,3) cortical_cells on load
                    # v21.3: only names that are never ordinary words (a stored "hope" is the word hope)
                    id_tokens = self.get_hard_identity_tokens()
                    for cell, mem in data.get("cortical_cells", {}).items():
                        c_3d = self.normalize_cell_key(cell)
                        clean_m = {
                            k.strip().lower(): val
                            for k, val in mem.items()
                            if self.is_valid_concept_node(k)
                            and (c_3d == "3,3,3" or k.strip().lower() not in id_tokens)
                        }
                        self.cortical_cells.setdefault(c_3d, {}).update(clean_m)

                    saved_assoc = data.get("assoc_graph", {})
                    if saved_assoc:
                        self.assoc_graph = {}
                        for w, links in saved_assoc.items():
                            wl = w.strip().lower()
                            if self.is_valid_concept_node(wl):
                                clean_l = {
                                    k.strip().lower(): round(float(val), 2)
                                    for k, val in links.items()
                                    if self.is_valid_concept_node(k) and k.strip().lower() != wl
                                }
                                if clean_l:
                                    self.assoc_graph[wl] = clean_l

                    for t_w in ("truth", "true", "honest"):
                        for neg_w in ("deceive", "lie"):
                            self.record_rejection(t_w, neg_w, repel=False)

                    self.repair_archetype_and_idempotent_links()

                    for cell_k, vec in data.get("cell_centroids", {}).items():
                        c_3d = self.normalize_cell_key(cell_k)
                        if isinstance(vec, list) and len(vec) == self.dim and any(abs(x) > 1e-6 for x in vec):
                            self.cell_centroids[c_3d] = self.normalize(vec)

                    for cell_k, lex_entry in data.get("cell_lexicon", {}).items():
                        c_3d = self.normalize_cell_key(cell_k)
                        if c_3d in self.cell_lexicon and isinstance(lex_entry, dict):
                            s_c = int(c_3d.split(",")[0])
                            self.cell_lexicon[c_3d]["visits"] = max(self.cell_lexicon[c_3d]["visits"], lex_entry.get("visits", 0))
                            if lex_entry.get("custom") and self.is_valid_emotion_name(lex_entry.get("name", ""), s_c):
                                self.cell_lexicon[c_3d]["name"] = lex_entry["name"]
                                self.cell_lexicon[c_3d]["stage"] = 3
                                self.cell_lexicon[c_3d]["custom"] = True

                    for cell_k, words_map in list(self.cortical_cells.items()):
                        if words_map or self.cell_lexicon[cell_k]["visits"] > 0:
                            s_c, a_c, z_c = [int(x) for x in cell_k.split(",")]
                            self.cell_lexicon[cell_k]["visits"] = max(0, self.cell_lexicon[cell_k]["visits"] - 1)
                            self.update_cell_centroid_and_emotion(s_c, a_c, z_c, self.strongest_cell_words(cell_k), allow_cleave=True,
                                                                  count_visit=False)
                            self.anneal_crystal_facet_alpha(cell_k, notify=False)

                    # v22.7.1: keep each cell's saved mood name (the rebuild above re-picks names in a different order)
                    for cell_k, lex_entry in data.get("cell_lexicon", {}).items():
                        c_3d = self.normalize_cell_key(cell_k)
                        entry = self.cell_lexicon.get(c_3d)
                        if (entry and isinstance(lex_entry, dict) and not entry.get("custom") and lex_entry.get("stage", 1) >= 2
                                and self.is_valid_emotion_name(lex_entry.get("name", ""), int(c_3d.split(",")[0]))):
                            entry["name"], entry["stage"] = lex_entry["name"], 2

                    for tr_k, tr_entry in data.get("trace_lexicon", {}).items():
                        if isinstance(tr_entry, dict) and "vector" in tr_entry:
                            self.trace_lexicon[tr_k] = tr_entry

                    last_ts = data.get("last_shutdown_timestamp")
                    if isinstance(last_ts, (int, float)) and last_ts > 0:
                        elapsed_hrs = (self.now() - float(last_ts)) / 3600.0
                        if elapsed_hrs >= 0.5:
                            self._apply_env_overrides()  # v24.1: the switches apply to the wake-up sleep too, as documented
                            self._ensure_word_sightings()  # v24.1: before any message (the first one slipped past seen-once)
                            self.run_stasis_sleep_pass(elapsed_hrs)
                            note = self.tectonics_note()  # v23.2
                            if note:
                                print(f"{note} while asleep")
                        elif self._env_levels != "0" and self.levels_on:
                            self.levels_advance(max(0.0, elapsed_hrs) * 60.0)  # v23.3: closed briefly = still awake
            except Exception as e:
                backup_path = f"{self.memory_file}.unreadable-{int(self.now())}"
                try:
                    os.replace(self.memory_file, backup_path)
                    print(f"[!] Could not fully load '{self.memory_file}' ({type(e).__name__}: {e}).")
                    print(f"    Your original file was kept as '{backup_path}' so it won't be overwritten.")
                except OSError:
                    print(f"[!] Could not fully load '{self.memory_file}' ({type(e).__name__}: {e}).")

    def save_memory(self):
        self.cap_dream_propositions(max_dreams=12)
        active_centroids = {k: [round(x, 4) for x in v] for k, v in self.cell_centroids.items() if self.cell_lexicon.get(k, {}).get("visits", 0) > 0}
        active_lex = {k: v for k, v in self.cell_lexicon.items() if v.get("visits", 0) > 0 or v.get("stage", 1) >= 2}
        non_empty_cells = {k: v for k, v in self.cortical_cells.items() if v}
        tracked_words = set(self.word_weights.keys()) | set(self.assoc_graph.keys())
        data = {
            "version": ENGINE_VERSION, "vector_mode": self.vector_mode, "last_shutdown_timestamp": self.now(),
            "seed_coord": [self.seed_s, self.seed_a, self.seed_z],
            "velocity": [self.vel_s, self.vel_a, self.vel_z], "user_profile": self.user_profile,
            "word_weights": {k.lower(): round(v, 3) for k, v in self.word_weights.items() if self.is_valid_concept_node(k)},
            "social_weights": {k.lower(): round(v, 3) for k, v in self.social_weights.items() if self.is_valid_concept_node(k)},
            "epistemic_weights": {k.lower(): round(v, 3) for k, v in self.epistemic_weights.items() if self.is_valid_concept_node(k)},
            "knowledge_facts": self.knowledge_facts, "idea_memory": self.idea_memory,
            "custom_verb_bridges": self.custom_verb_bridges[-40:], "rejected_links": self.rejected_links,
            "dream_journal": self.dream_journal, "cell_lexicon": active_lex,
            "trace_lexicon": self.trace_lexicon, "cell_centroids": active_centroids,
            "crystal_lattices": self.crystal_lattices, "cleavage_log": self.cleavage_log,
            "bridge_habituation": {k: round(v, 3) for k, v in self.bridge_habituation.items() if v >= 0.05},
            "sleep_pressure": {"cells": round(self.cells_added_since_sleep, 3), "links": round(self.link_strength_added_since_sleep, 3),
                               "used": sorted(list(p) for p in self.links_used_since_sleep), "new_links": int(self.new_links_since_sleep),
                               "awake_minutes": round(self.awake_minutes, 2), "sleep_links": round(self.sleep_link_added, 3)},
            "last_sleep": self.last_sleep,
            "nightmare_mode": self.nightmare_mode,
            "governor_mode": self.governor_mode,
            "source_tags_on": self.source_tags_on,
            "link_sources": {k: v for k, v in sorted(self.link_sources.items())
                             if k.split("|", 1)[1] in self.assoc_graph.get(k.split("|", 1)[0], {})},
            "experienced_words": sorted(self.experienced_words),
            "word_sightings": self.word_sightings or {},
            "seen_once_ready": self.seen_once_ready,
            "people": self.people,
            "show_tectonics": self.show_tectonics,
            "expectation": self.expectation,
            "surprise_baseline": round(self.surprise_baseline, 4),
            "mood_level_on": self.mood_level_on,
            "levels_on": self.levels_on, "arousal": round(self.arousal, 4), "arousal_mean": round(self.arousal_mean, 4),
            "valence_level": self.valence_level, "novelty": round(self.novelty, 4),  # v23.3
            "idle_menu_on": self.idle_menu_on, "idle_habits": self.idle_habits, "idle_outcome_mean": self.idle_outcome_mean,
            "rhythm_on": self.rhythm_on, "rhythm_offset": self.rhythm_offset,  # v24.0
            "felt_usual": round(self.felt_usual, 3) if self.felt_usual is not None else None,
            "recent_turns": self.recent_turns[-self.RECENT_TURNS_KEEP:], "caretaker_last_seen": self.caretaker_last_seen,
            "idle_on": self.idle_on,
            "idle_visits": {k: round(v, 3) for k, v in self.idle_visits.items() if v >= 0.05},
            "idle_journal": self.idle_journal[-10:],
            "a_push_mean": round(self.a_push_mean, 4),
            "speaker_tone": self.speaker_tone,  # v23.4.1
            "a_level_resid": self.a_level_resid,
            "pending_demoted": {k: sorted(v) for k, v in self.saved_demoted.items() if v and k not in self.crystal_lattices},
            "turn_counter": self.turn_counter,
            "split_rest": {w: t for w, t in self.split_rest.items() if self.turn_counter - t < self.SPLIT_REST_TURNS},
            "assoc_graph": self.assoc_graph, "cortical_cells": non_empty_cells,
            "learned_vectors": {w.lower(): [round(x, 4) for x in self.vectors[w]] for w in tracked_words if w in self.vectors and self.is_valid_concept_node(w)}
        }
        tmp_path = self.memory_file + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.memory_file)

    # =================================================================
    # TASK 1.2 & 1.3: PAULI-LIMITED HEBBIAN WIRING & DIALECTICAL REJECTION
    # =================================================================
    def wire_concepts(self, w1, w2, amount=1.5, source=None, min_link=None):
        """Link two words (or strengthen their link). A new link starts at least at 0.25, except idle links and callers
        that pass min_link (v22.10: the bridge's held-back reply words, so "quarter strength" really is a quarter)."""
        w1 = w1.strip().lower() if isinstance(w1, str) else ""
        w2 = w2.strip().lower() if isinstance(w2, str) else ""
        if not self.is_valid_concept_node(w1) or not self.is_valid_concept_node(w2) or self.same_stem(w1, w2):
            return
        if amount > 0:  # v23.1: a rejection weakens new learning in proportion to its strength (1.0 = blocked)
            rej = max(self.rejected_links.get(w1, {}).get(w2, 0.0), self.rejected_links.get(w2, {}).get(w1, 0.0))
            if rej > 0:
                amount = amount * max(0.0, 1.0 - rej)
                if amount < 0.01:
                    return
        if amount > 0 and self.awake_turn and self.turn_learning_gain != 1.0:
            amount = amount * self.turn_learning_gain  # v22.5 cerebellum: waking learning scaled by surprise
        idle = (source or self.wire_source) == "idle"  # v22.9: idle links stay faint, aren't "used today", barely move meanings
        if amount > 0:  # v21.9: sleep scales links down in proportion to this; a link used today is spared tonight
            if self.awake_turn and (source or self.wire_source) != "engine":  # v22: only waking learning builds sleep
                self.link_strength_added_since_sleep += amount  # pressure (v24.1: not the engine's own cleave veins)
            elif not self.awake_turn and (source or self.wire_source) in ("dream", "sleep"):
                self.sleep_link_added += amount  # v24.1: balanced at the next wake-up sleep (v24.1.1: only what is
                # tagged dream/sleep, the links the balance takes it back from; names, notes and load-time veins aren't)
            if not idle and self.awake_turn:  # v22.9: walking a link while idle doesn't spare it (a small loop kept
                # protecting itself); v24.1: nor does a dream or sleep's own link ("used today" means while awake)
                self.links_used_since_sleep.add((w1, w2) if w1 < w2 else (w2, w1))
        link_existed = w2 in self.assoc_graph.get(w1, {})  # v22: count new links for the night's release limit
        self.core_concept_pool.update([w1, w2])
        self.assoc_graph.setdefault(w1, {})
        self.assoc_graph.setdefault(w2, {})
        cur_12 = self.assoc_graph[w1].get(w2, 0.0)
        cur_21 = self.assoc_graph[w2].get(w1, 0.0)
        base_cur = max(cur_12, cur_21)
        if amount < 0:
            new_w = max(0.25, round(base_cur + amount, 2)) if base_cur > 0 else 0.0
        else:
            floor = min_link if min_link is not None else (self.IDLE_LINK_FLOOR if idle else 0.25)
            new_w = max(floor, round(base_cur + amount, 2))
        if amount > 0:  # v22.7 source tags: explicit source > caller's context > awake (user) / otherwise engine
            self._tag_link(w1, w2, base_cur, amount, new_w,
                           source or self.wire_source or (self.user_source() if self.awake_turn else "engine"))
        if new_w == 0.0:
            self.link_sources.pop(self.link_key(w1, w2), None)
            self.assoc_graph[w1].pop(w2, None)
            self.assoc_graph[w2].pop(w1, None)
        else:
            self.assoc_graph[w1][w2] = new_w
            self.assoc_graph[w2][w1] = new_w
            if not link_existed:
                self.new_links_since_sleep += 1

        if amount > 0 and w1 in self.vectors and w2 in self.vectors:
            u = list(self.vectors[w1])
            v = list(self.vectors[w2])
            sim = self.dot(u, v)
            pauli_factor = max(0.0, (0.82 - sim) / 0.82)
            alpha = 0.15 * pauli_factor
            if idle:  # v22.9: in proportion to the link's strength (an idle step is ~1/20 of a user link)
                alpha *= min(1.0, amount / self.IDLE_VECTOR_REF)
            if alpha > 1e-4:
                u_new = self.blend(u, v, 1.0 - alpha, alpha)
                v_new = self.blend(v, u, 1.0 - alpha, alpha)
                self.vectors[w1] = self.enforce_factory_tether(w1, u_new)
                self.vectors[w2] = self.enforce_factory_tether(w2, v_new)

    REJECT_NEGATION = 0.3      # v23.1: "he did not come home": a soft rejection that weakens the link and fades
    NEG_SHIFT = 0.5            # v23.3.3: a negated word pushes calm/tense the opposite way at this share of its weight
    REJECT_CORRECTION = 1.0    # v23.1: the user disagreeing with the brain's guess ("No, ..."): blocks, then fades
    REJECT_LEGACY = 0.5        # v23.1: rejections saved by older engines (they were permanent)
    REJECT_FADE = 0.8          # v23.1: share of a rejection kept per full night of sleep (x sleep depth)

    REJECT_BLOCK = 0.5         # v24.1: a rejection this strong hides the partner from recall (as in the idle walk);
                               # a soft one (a plain "X is not Y", 0.3) only weakens the link

    def blocked_partners(self, w):
        """v24.1: the words w's rejections are strong enough to hide (REJECT_BLOCK or more)."""
        return {k for k, v in self.rejected_links.get(w, {}).items() if v >= self.REJECT_BLOCK}

    def record_rejection(self, w1, w2, strength=None, repel=True):
        """v23.1: rejections are weighted and fade in sleep instead of being permanent. A correction (the user saying no
        to the brain's guess) removes the link and pushes the meanings apart, as before. A negated sentence only weakens
        the link by the rejection's strength: storybook narration was deleting links and banning pairs for good."""
        if not w1 or not w2:
            return
        w1, w2 = w1.strip().lower(), w2.strip().lower()
        strength = self.REJECT_CORRECTION if strength is None else strength
        for a, b in ((w1, w2), (w2, w1)):
            row = self.rejected_links.setdefault(a, {})
            row[b] = round(min(1.0, row.get(b, 0.0) + strength), 3)
        if strength >= self.REJECT_CORRECTION:
            self.assoc_graph.get(w1, {}).pop(w2, None)
            self.assoc_graph.get(w2, {}).pop(w1, None)
            if repel:  # v24.1.1: the built-in truth/lie rejections at every load don't push meanings (it added up)
                self.apply_dialectical_repulsion(w1, w2, rate=0.06)
        else:
            for a, b in ((w1, w2), (w2, w1)):
                if b in self.assoc_graph.get(a, {}):
                    self.assoc_graph[a][b] = round(self.assoc_graph[a][b] * (1.0 - strength), 2)

    def fade_rejections(self, depth):
        """v23.1: during a wake-up sleep every rejection fades (REJECT_FADE per full night, scaled by depth)."""
        keep = 1.0 - (1.0 - self.REJECT_FADE) * depth
        gone = 0
        for a in list(self.rejected_links):
            row = self.rejected_links[a]
            for b in list(row):
                row[b] = round(row[b] * keep, 3)
                if row[b] < 0.05:
                    del row[b]
                    gone += 1
            if not row:
                del self.rejected_links[a]
        return gone // 2

    def learn_from_turn(self, user_text, tokens, concepts, s_fin, a_fin, z_fin):
        """
        UPGRADE 1 & 2:
          • Identity tokens continue updating assoc_graph, word_weights, social_weights,
            and epistemic_weights on every turn.
          • Identity tokens are excluded from cortical_cells and crystal_lattices unless
            at origin (3,3,3) or during an explicit self-referential identity query.
          • Novel OOV words initialize their 50D vector using 80% mean of in-vocabulary
            turn concepts / cell centroid + 20% deterministic hash.
        """
        cell_mass_before = sum(sum(v.values()) for v in self.cortical_cells.values())  # v21.9
        try:
            return self._learn_from_turn(user_text, tokens, concepts, s_fin, a_fin, z_fin)
        finally:
            gained = sum(sum(v.values()) for v in self.cortical_cells.values()) - cell_mass_before
            self.cells_added_since_sleep += max(0.0, gained)

    def _learn_from_turn(self, user_text, tokens, concepts, s_fin, a_fin, z_fin):
        a_valence, s_valence, z_valence = (a_fin - 3.0) / 3.0, (s_fin - 3.0) / 3.0, (z_fin - 3.0) / 3.0
        negated_set = self.find_negated_concepts_in_tokens(tokens, user_text)
        pos_concepts = [c for c in concepts if c not in negated_set and self.is_valid_concept_node(c)]
        if self.negation_v2:  # v23.3.3 option C: only "X is not Y" says two words don't go together (recorded once)
            for subj, obj in self.negation_rejections(tokens, user_text):
                self.record_rejection(subj, obj, strength=self.REJECT_NEGATION)
        else:
            for pc in pos_concepts:
                for nc in negated_set:
                    self.record_rejection(pc, nc, strength=self.REJECT_NEGATION)

        cell_key = f"{s_fin},{a_fin},{z_fin}"
        self.cortical_cells.setdefault(cell_key, {})

        # Compute contextual anchor vector from known in-vocabulary words in the turn or cell centroid
        known_turn_vecs = [self.vectors[w] for w in (pos_concepts + tokens) if w in self.vectors and w not in self.stop_words]
        if known_turn_vecs:
            context_anchor_vec = self.average_vectors(known_turn_vecs)
        else:
            context_anchor_vec = self.cell_centroids.get(cell_key, self.coord_vectors[(s_fin, a_fin, z_fin)])

        id_tokens = self.get_identity_tokens()
        allow_id_in_cell = (cell_key == "3,3,3") or self.is_identity_query(user_text, tokens)
        hard_ids = self.get_hard_identity_tokens()

        def admit(c):
            # v21.3: a name used as a name enters a cell at (3,3,3); on identity questions only if it is never an
            # ordinary word (those were scrubbed again at the next sleep anyway, and a name like "hope" must not
            # mix its name-uses into the word's cells, which are no longer scrubbed)
            if self.is_provisional_word(c):
                return False  # v22.4: a one-off unknown word (likely a typo) doesn't claim a cell yet
            return c not in id_tokens or cell_key == "3,3,3" or (allow_id_in_cell and c in hard_ids)

        self.extract_proposition(user_text, tokens, pos_concepts, cell_key)

        g = self.turn_learning_gain  # v22.5 cerebellum: surprising turns are learned harder, familiar ones lighter
        for c in pos_concepts[:6]:
            self.core_concept_pool.add(c)
            vec = self.get_or_create_vector(c, context_vec=context_anchor_vec)

            # Only increment cortical_cells for non-identity concepts (or at 3,3,3 / identity queries)
            if admit(c):
                self.cortical_cells[cell_key][c] = round(self.cortical_cells[cell_key].get(c, 0) + g, 3)

            # Identity & topical words ALWAYS update their affective, social, and epistemic weights
            if c not in self.word_weights:
                self.word_weights[c] = round(self.axis_weight(vec, "A"), 2)
            if not self.mood_active() and self.calm_learning == "landing":  # otherwise it learns from its company (below)
                self.word_weights[c] = round(max(-5.0, min(5.0, self.word_weights[c] + 0.2 * g * a_valence)), 3)
            if c not in self.social_weights:
                self.social_weights[c] = round(self.axis_weight(vec, "S"), 2)
            self.social_weights[c] = round(max(-5.0, min(5.0, self.social_weights[c] + 0.2 * g * s_valence)), 3)
            if c not in self.epistemic_weights:
                self.epistemic_weights[c] = round(self.axis_weight(vec, "Z"), 2)
            self.epistemic_weights[c] = round(max(-5.0, min(5.0, self.epistemic_weights[c] + 0.2 * g * z_valence)), 3)

        if self.mood_active() or self.calm_learning == "company":  # v22.10: company teaches calm (TORRENT_CALM=landing = old)
            self.learn_calm_from_what_follows(pos_concepts[:6], g)  # v22.11 amygdala (before company changes this turn)
            self.learn_calm_from_company(pos_concepts[:6], g)

        # Keep Hebbian co-occurrence wiring active for all top concepts (including identity tokens)
        top_c = pos_concepts[:5]
        for i in range(len(top_c)):
            for j in range(i + 1, len(top_c)):
                if self.is_provisional_word(top_c[i]) or self.is_provisional_word(top_c[j]):
                    self.wire_concepts(top_c[i], top_c[j], amount=self.SEEN_ONCE_LINK, min_link=0.01)  # v22.11: faint
                else:
                    self.wire_concepts(top_c[i], top_c[j], amount=1.0)

        spatial_concepts = [c for c in pos_concepts if admit(c)]
        self.update_cell_centroid_and_emotion(
            s_fin, a_fin, z_fin,
            spatial_concepts,
            allow_cleave=True,
            allow_identity=allow_id_in_cell
        )

    HABITUATION_PENALTY = 0.12  # v21.6: score lost per recent use of a sleep bridge
    HABITUATION_DECAY = 0.85    # v21.6: recent-use counts shrink this much per sleep pass (a night has several passes)

    def find_sleep_bridge(self, w, exclude):
        """v21.6: the comfort bridge for sleep's Contrastive Self-Correction.
        Same choice as before (the word nearest the midpoint of w and "calm"), with two changes, tested 2026-11-08:
          - habituation: a bridge used in recent sleeps loses HABITUATION_PENALTY per use (counts shrink by HABITUATION_DECAY each sleep pass).
            Without it the word nearest "calm" ("quiet" in GloVe) won ~44% of the time and became one of the
            brain's strongest words; with it, ~4%.
          - only words the brain has actually been told may be bridges (built-in words it never met can't);
            if none qualify, the old pool is used."""
        v1, v2 = self.vectors.get(w), self.vectors.get("calm")
        if not v1 or not v2:
            return "harmony"
        mid_vec = self.blend(v1, v2, 0.5, 0.5)
        pool = ((self.core_concept_pool | set(self.assoc_graph.keys())) - self.negative_lexicon - self.noise_words
                - self.stop_words - self.generic_hubs - self.get_identity_tokens())
        told = pool & self.experienced_words
        best_w, best_score = None, -999.0
        for cand in (told or pool):
            if cand in exclude or len(cand) < 4 or cand not in self.vectors or self.same_stem(cand, w) or self.same_stem(cand, "calm"):
                continue
            score = self.dot(mid_vec, self.vectors[cand]) - self.HABITUATION_PENALTY * self.bridge_habituation.get(cand, 0.0)
            if score > best_score:
                best_score, best_w = score, cand
        best_w = best_w or "connection"
        self.bridge_habituation[best_w] = self.bridge_habituation.get(best_w, 0.0) + 1.0
        return best_w

    def find_conceptual_bridge(self, w1, w2, exclude):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if not v1 or not v2:
            return "harmony"
        mid_vec = self.blend(v1, v2, 0.5, 0.5)
        best_w, best_score = "connection", -999.0
        id_tokens = self.get_identity_tokens()
        search_pool = (self.core_concept_pool | set(self.assoc_graph.keys())) - self.lean_up_words() - self.noise_words - self.stop_words - self.generic_hubs - id_tokens
        for cand in search_pool:
            if cand in exclude or len(cand) < 4 or cand not in self.vectors or self.same_stem(cand, w1) or self.same_stem(cand, w2):
                continue
            if not self.word_is_trusted(cand):
                continue  # v22.7: a word only the voice or dreams made up can't be the brain's own bridge
            score = self.dot(mid_vec, self.vectors[cand])
            if self.vector_mode == "map2d" and w1 in self.raw_glove and w2 in self.raw_glove and cand in self.raw_glove:
                mx = (self.raw_glove[w1][0] + self.raw_glove[w2][0]) / 2.0
                my = (self.raw_glove[w1][1] + self.raw_glove[w2][1]) / 2.0
                d = math.sqrt((mx - self.raw_glove[cand][0]) ** 2 + (my - self.raw_glove[cand][1]) ** 2)
                score += max(0.0, 1.0 - d * 0.5)
            if score > best_score:
                best_score, best_w = score, cand
        return best_w

    def retrieve_brain_concepts(self, user_concepts, s, a, z, target_vec, traj_harvest, top_k=4):
        id_tokens = self.get_identity_tokens()
        exclude = set(user_concepts) | self.stop_words | self.noise_words | id_tokens
        for uc in user_concepts:
            exclude.update(self.blocked_partners(uc))  # v24.1
        if (s + a) >= 4:
            exclude = exclude | self.lean_up_words()
        scores = {}

        def valid_cand(cand):
            return (cand not in exclude and len(cand) >= 4 and all(not self.same_stem(cand, uc) for uc in user_concepts)
                    and self.word_is_trusted(cand))  # v22.7

        for uc in user_concepts[:4]:
            for neighbor, strength in self.assoc_graph.get(uc, {}).items():
                if valid_cand(neighbor):
                    hub_factor = 0.45 if neighbor in self.generic_hubs else 2.2
                    scores[neighbor] = scores.get(neighbor, 0.0) + (strength * hub_factor)
        for idx, hw in enumerate(traj_harvest):
            if valid_cand(hw) and hw not in self.generic_hubs:
                scores[hw] = scores.get(hw, 0.0) + (1.6 - idx * 0.25)
        for uc in user_concepts[:2]:
            if self.vector_mode == "map2d" and uc in self.raw_glove:
                ux, uy = self.raw_glove[uc][0], self.raw_glove[uc][1]
                for gw, gcoords in list(self.raw_glove.items())[200:7500]:
                    if valid_cand(gw):
                        dist = math.sqrt((ux - gcoords[0]) ** 2 + (uy - gcoords[1]) ** 2)
                        if dist < 0.22:
                            scores[gw] = scores.get(gw, 0.0) + (0.35 - dist) * 4.0
        for w in self.core_concept_pool:
            if valid_cand(w) and w in self.vectors:
                sim = self.dot(self.vectors[w], target_vec)
                z_boost = 0.15 if (z >= 4 and self.epistemic_weights.get(w, 0.0) > 0.5) else 0.0
                if sim + z_boost > 0.25:
                    scores[w] = scores.get(w, 0.0) + (sim + z_boost) * 0.9

        final_list = []
        for w, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if all(not self.same_stem(w, ex) for ex in final_list):
                final_list.append(w)
            if len(final_list) >= top_k:
                break
        for fb in ["clarity", "connection", "understanding", "perspective", "harmony"]:
            if len(final_list) < top_k and valid_cand(fb) and all(not self.same_stem(fb, ex) for ex in final_list):
                final_list.append(fb)
        return final_list

    def pick_fresh(self, options, history_list, max_hist=4):
        available = [opt for i, opt in enumerate(options) if i not in history_list] or options
        chosen = random.choice(available)
        history_list.append(options.index(chosen))
        if len(history_list) > max_hist:
            history_list.pop(0)
        return chosen

    # v23.3.3 relation-aware verbs: the brain's own relation between the two words picks the verb family (opposed /
    # joined / neither); the landing place still picks the verb inside it. TORRENT_RELATION_VERBS=0 = the old picker.
    OPPOSED_AT = 0.3   # a rejection this strong (one "X is not Y", or any correction) = held as opposed
    JOINED_AT = 0.8    # a link this strong = held together
    OPPOSING_VERBS = {vb for pool in BRAIN_LIBRARY["Z_oppose_verbs"].values() for vb in pool}

    def pair_relation(self, w1, w2):
        """v23.3.3: 'opposed', 'joined' or 'neutral', from what the brain holds about the two words right now."""
        rej = max(self.rejected_links.get(w1, {}).get(w2, 0.0), self.rejected_links.get(w2, {}).get(w1, 0.0))
        if rej >= self.OPPOSED_AT:
            return "opposed"
        link = max(self.assoc_graph.get(w1, {}).get(w2, 0.0), self.assoc_graph.get(w2, {}).get(w1, 0.0))
        return "joined" if link >= self.JOINED_AT else "neutral"

    def pick_stratified_verb_bridge(self, w1, w2, z_level, step_vec):
        for p in reversed(self.idea_memory):
            if p.get("origin", "waking") == "waking" and p["subj"] == w1 and p["obj"] == w2:
                return p["rel"]
        relation = self.pair_relation(w1, w2) if self.relation_verbs else "neutral"
        strata = BRAIN_LIBRARY["Z_oppose_verbs"] if relation == "opposed" else self.verb_strata
        if z_level <= 1:
            pool = list(strata["concrete"])
        elif z_level <= 3:
            pool = strata["causal"] + ([] if relation == "opposed" else self.custom_verb_bridges)
        elif z_level <= 5:
            pool = strata["counterfactual"] + strata["causal"]
        else:
            pool = strata["synthetic"] + strata["counterfactual"]
        if relation == "joined":  # v23.3.3: two words the brain holds together don't get an opposing verb
            pool = [vb for vb in pool if vb not in self.OPPOSING_VERBS] or pool
        scored = sorted([(self.dot(step_vec, self.phrase_to_vector(vb)), vb) for vb in pool], key=lambda x: x[0], reverse=True)
        top_pool = [vb for _, vb in scored[:3]] or ["structurally entails"]
        return random.choice(top_pool)

    # =================================================================
    # FLUID 3-NODE GLISSANDO & VERB-SAFE INQUIRY TEMPLATES
    # =================================================================
    def bind_concepts_by_weight(self, w_a, w_b, z_level, step_vec, kinetic=False):
        edge_wt = self.assoc_graph.get(w_a, {}).get(w_b, 0.0)
        verb = self.pick_stratified_verb_bridge(w_a, w_b, z_level, step_vec)
        if edge_wt >= 1.5:
            return f"{w_a} directly {verb} {w_b}" if kinetic else f"{w_a} {verb} {w_b}"
        elif edge_wt >= 0.8:
            return f"{w_a} {verb} {w_b}"
        else:
            return f"{w_a} opens toward {w_b}" if kinetic else f"{w_a} begins to {verb} {w_b}"

    def render_three_node_glissando(self, p0, p1, p2, high_kinetic):
        w01 = self.assoc_graph.get(p0, {}).get(p1, 0.5)
        w12 = self.assoc_graph.get(p1, {}).get(p2, 0.5)
        avg_wt = (w01 + w12) / 2.0
        if high_kinetic:
            opts = [
                f"{p0} pivots through {p1} into {p2}",
                f"{p0} sparks {p1}, opening into {p2}",
                f"{p0} shifts through {p1} to unlock {p2}"
            ]
        elif avg_wt >= 1.2:
            opts = [
                f"{p0} and {p1} converge into {p2}",
                f"{p0} deepens through {p1} into {p2}",
                f"{p0} anchors {p1} and grounds {p2}"
            ]
        else:
            opts = [
                f"{p0} bridges through {p1} toward {p2}",
                f"{p0} connects with {p1} to ground {p2}",
                f"{p0} flows through {p1} into {p2}"
            ]
        return random.choice(opts)

    def assemble_free_toroidal_speech(self, c1, c2, r1, r2, bridge, s, a, z, thought_trace, audit, is_question):
        active_traj = audit["flippedTrajectory"] if self.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        step_deltas = [
            self.euclidean_distance(active_traj[i - 1]["S"], active_traj[i - 1]["A"], active_traj[i - 1]["Z"], active_traj[i]["S"], active_traj[i]["A"], active_traj[i]["Z"])
            for i in range(1, len(active_traj))
        ]
        mean_vel = sum(step_deltas) / float(max(1, len(step_deltas)))
        # v21.3: the step-size cutoff is scaled with TRAJECTORY_DAMPING (it was set for full-cell steps; unscaled it
        # would never fire again, and at full steps it fired on almost every turn)
        high_kinetic = mean_vel >= 1.60 * self.TRAJECTORY_DAMPING or audit.get("meanDeltaD", 0.0) >= 2.65

        st2, st9 = active_traj[2], active_traj[9]
        vec_early = self.cell_centroids.get(f"{st2['S']},{st2['A']},{st2['Z']}", self.pole_calm)
        vec_late = self.cell_centroids.get(f"{st9['S']},{st9['A']},{st9['Z']}", self.pole_calm)

        ponder = thought_trace.get("pondering", {})
        alpha_anchor = ponder.get("alpha_anchor", c1)
        gamma_foil = ponder.get("gamma_foil", "")
        gamma_tension = ponder.get("gamma_tension", 0.0)
        pondered_bridge = ponder.get("pondered_bridge", bridge)
        apex_word = ponder.get("apex_word", r1)

        deductions = thought_trace.get("deductions", [])
        a_star_path = thought_trace.get("a_star_path", [])
        convergences = thought_trace.get("convergences", [])
        related_prop = self.find_related_idea([c1, c2, r1])

        if c1 in self.knowledge_facts and not c1.startswith("_"):
            clause_alpha = f"{c1.capitalize()} is {self.knowledge_facts[c1]}, where {self.bind_concepts_by_weight(c1, pondered_bridge, st2['Z'], vec_early, high_kinetic)}."
        elif deductions:
            d = deductions[-1]
            self.spoken_deductions.add(d["conclusion"])
            self.spoken_chains.add(d.get("chain_sig", d["conclusion"]))
            steps_joined = "; ".join(d["steps"]) if high_kinetic else ", and ".join(d["steps"])
            clause_alpha = f"{steps_joined.capitalize()}—so {d['conclusion']}." if high_kinetic else f"{steps_joined.capitalize()}, which means {d['conclusion']}."
        elif related_prop:
            self.spoken_chains.add(related_prop["summary"])
            clause_alpha = f"{related_prop['summary'].capitalize()}, and {self.bind_concepts_by_weight(related_prop['obj'], pondered_bridge, st2['Z'], vec_early, high_kinetic)}."
        else:
            open_target = alpha_anchor if (not self.same_stem(c1, alpha_anchor)) else pondered_bridge
            clause_alpha = f"{self.bind_concepts_by_weight(c1, open_target, st2['Z'], vec_early, high_kinetic).capitalize()}."

        if len(a_star_path) >= 3:
            p0, p1, p2 = a_star_path[0], a_star_path[1], a_star_path[-1]
        else:
            p0 = pondered_bridge
            p1 = r1 if not self.same_stem(r1, p0) else r2
            p2 = apex_word if (not self.same_stem(apex_word, p0) and not self.same_stem(apex_word, p1)) else r2
        path_clause = self.render_three_node_glissando(p0, p1, p2, high_kinetic)

        path_words_set = {c1, c2, p0, p1, p2, pondered_bridge, apex_word}
        if gamma_foil and self.is_crystal_pure_concept(gamma_foil) and gamma_foil not in path_words_set and gamma_tension > 0.12:
            gamma_prefixes = (
                [f"Even with the friction of {gamma_foil}, {path_clause}.", f"Balancing against {gamma_foil}, {path_clause}."]
                if high_kinetic else
                [f"While {gamma_foil} pulls at the edge, {path_clause}.", f"Stepping past {gamma_foil}, {path_clause}."]
            )
            clause_gamma_omega = random.choice(gamma_prefixes)
        else:
            clause_gamma_omega = f"{path_clause.capitalize()}."

        tail = ""
        if convergences:
            ca, cb, shared_node, _ = convergences[0]
            tail_bind = self.bind_concepts_by_weight(shared_node, r2, st9["Z"], vec_late, high_kinetic)
            tail = f" Both {ca} and {cb} converge on {shared_node}, where {tail_bind}."
        elif is_question or random.random() < 0.25:
            q_templates = [
                f"How do {c1} and {pondered_bridge} shape each other?",
                f"Where does {c1} lead when it meets {pondered_bridge}?",
                f"What bridges the space between {c1} and {pondered_bridge}?"
            ]
            tail = " " + random.choice(q_templates)

        return f"{clause_alpha} {clause_gamma_omega}{tail}"

    def build_compositional_thought(self, c1, c2, r1, r2, bridge, s, a, z, name_tag, thought_trace, trace_emotion_name, is_question):
        cell_emotion_name = self.get_cell_emotion_name(s, a, z)
        z_desc = BRAIN_LIBRARY["Z_rough_seeds"][str(z)]
        ponder = thought_trace.get("pondering", {})
        pondered_bridge = ponder.get("pondered_bridge", bridge)
        pondered_prop = ponder.get("pondered_proposition")
        deductions = thought_trace.get("deductions", [])
        a_star_path = thought_trace.get("a_star_path", [])
        convergences = thought_trace.get("convergences", [])
        related_prop = self.find_related_idea([c1, c2, r1])

        if is_question:
            openers = [
                f"Looking at '{c1}' from '{cell_emotion_name}' (Z={z} {z_desc}){name_tag}, a clear connection stands out.",
                f"Refracting '{c1}' across my 3D torus sparked a '{trace_emotion_name}' at depth Z={z}, bringing '{pondered_bridge}' and '{r1}' into focus{name_tag}.",
                f"When I reflect on '{c1}' at epistemic layer Z={z}{name_tag}, I can see how closely it ties to '{pondered_bridge}' and '{r2}'."
            ]
        else:
            openers = [
                f"I really like how '{c1}' and '{c2}' come together here{name_tag}, shifting my 3D state into '{cell_emotion_name}' (Z={z} {z_desc}).",
                f"Moving through that idea created a '{trace_emotion_name}'{name_tag}, linking '{c1}' directly with '{pondered_bridge}' at depth Z={z}.",
                f"Reflecting on '{c1}' from '{cell_emotion_name}' (Z={z}){name_tag} brings a deeper crystalline pattern into focus."
            ]
        clause_1 = self.pick_fresh(openers, self.recent_openers)

        insight_candidates = []
        if deductions:
            d = deductions[-1]
            self.spoken_deductions.add(d["conclusion"])
            self.spoken_chains.add(d.get("chain_sig", d["conclusion"]))
            steps_str = ", and ".join(d["steps"])
            insight_candidates.append(f"Because {steps_str}, it naturally follows that {d['conclusion']}.")
        if pondered_prop and ponder.get("pruned"):
            insight_candidates.append(f"After refracting through my crystal facets, I found that {pondered_prop}, which bridges '{c1}' cleanly toward '{r1}'.")
        if len(a_star_path) >= 3:
            path_str = " -> ".join(f"'{w}'" for w in a_star_path)
            insight_candidates.append(f"My 3D A* pathfinder bridged your thought along [{path_str}], connecting '{a_star_path[0]}' directly to '{a_star_path[-1]}'.")
        if related_prop:
            self.spoken_chains.add(related_prop["summary"])
            insight_candidates.append(f"It connects right into the idea that {related_prop['summary']}, showing how '{c1}' and '{r1}' work through '{pondered_bridge}'.")
        if convergences:
            ca, cb, shared_node, _ = convergences[0]
            insight_candidates.append(f"Both '{ca}' and '{cb}' converge on '{shared_node}' in my memory, making '{shared_node}' the bridge that holds them together.")
        insight_candidates.append(f"In my geometric map, '{c1}' and '{r1}' reinforce each other through '{pondered_bridge}', turning separate moments into a shared understanding.")
        clause_2 = insight_candidates[0]

        if random.random() < 0.70:
            self.pending_question = None
            conclusions = [
                f"That kind of '{pondered_bridge}' is really what makes '{cell_emotion_name}' feel so grounded at depth Z={z}.",
                f"It shows me that whenever '{c1}' is present, '{pondered_bridge}' and '{r1}' aren't far behind.",
                f"Holding '{c1}' and '{pondered_bridge}' together in '{cell_emotion_name}' gives me a much clearer picture of how they work."
            ]
            clause_3 = self.pick_fresh(conclusions, self.recent_closers)
        else:
            self.pending_question = {"type": "CONCEPT_EXPLORE", "concepts": [c1, pondered_bridge]}
            questions = [
                f"What do you think is the most important part of how '{c1}' and '{pondered_bridge}' connect?",
                f"When you think of '{c1}', does '{pondered_bridge}' feel like the natural result to you too?"
            ]
            clause_3 = self.pick_fresh(questions, self.recent_closers)
        return f"{clause_1} {clause_2} {clause_3}"

    # v24.1: "call me later / back / whenever ..." is a phone call, not a name
    CALL_ME_NOT_NAMES = {"later", "back", "sometime", "anytime", "whenever", "when", "tomorrow", "tonight", "today", "soon",
                         "again", "now", "then", "once", "first", "if", "after", "before", "up", "out", "on", "please",
                         "maybe", "asap", "anything", "something", "crazy", "silly", "names", "that", "this", "what",
                         "whatever", "sir", "maam", "dude", "bro", "buddy", "friend", "ok", "okay", "in", "at", "around",
                         "about", "every", "next", "this", "tonite", "sometimes", "and", "or", "but", "so", "because"}

    def detect_identity_teaching(self, tokens, raw=None):
        """raw (v24.1.1): the original text. "Call me X" counts only when X looks like a name: written with a capital
        ("Call me Sam"), or not an ordinary word ("call me zee"). "Call me curious / lazy / old fashioned" isn't a name;
        "my name is ..." works as before."""
        joined = " ".join(tokens)
        m_user = re.search(r"\b(?:my name is|call me)\s+([a-z]+)\b", joined)
        if m_user and m_user.group(0).startswith("call me"):
            x = m_user.group(1)
            capital = bool(raw) and re.search(r"\b[Cc]all me\s+" + x[0].upper() + re.escape(x[1:]) + r"\b", raw)
            if (x in self.CALL_ME_NOT_NAMES or x in self.stop_words
                    or not (capital or not self.is_ordinary_word(x))):
                m_user = None
        if m_user:
            return "user", m_user.group(1)
        m_bot = re.search(r"\b(?:your name is|i name you|call yourself|i will call you)\s+([a-z]+)\b", joined)
        if m_bot:
            return "bot", m_bot.group(1)
        return None, None

    # v21.4: definitions are learned on every turn (wheels on or off), one sentence at a time.
    QUOTE_CHARS = "'\"‘’“”"
    VAGUE_SUBJECTS = {"i", "you", "we", "they", "he", "she", "it", "this", "that", "what", "how", "why", "there", "here",
                      "another", "related", "name", "something", "everything", "nothing", "anything", "someone",
                      "everyone", "somebody", "everybody", "nobody", "one", "all", "life", "today"}

    def learn_definitions(self, user_text):
        """Store definitions the USER teaches, e.g. "a 'TCM' is a 'Toroidal-Crystalline Manifold'" or
        "TCM means toroidal crystalline manifold." Each sentence is checked on its own, so "That's not true."
        in the same message no longer blocks it. Works with wheels off (the bridge's default), where the old
        shortcut never ran. Returns {subject: definition} for this turn."""
        q = self.QUOTE_CHARS
        quoted_def = re.compile(
            rf"(?:^|\s)(?:an?\s+|the\s+)?[{q}]?([A-Za-z][A-Za-z0-9\-]{{1,30}})[{q}]?\s+"
            rf"(?:is|means|stands\s+for|represents)\s+(?:an?\s+|the\s+)?[{q}]([^{q}]{{2,60}})[{q}]", re.IGNORECASE)
        taught = {}
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", user_text):
            sentence = sentence.strip()
            if not sentence or "?" in sentence:
                continue
            subj = pred = None
            prev_words = []
            m = quoted_def.search(sentence)
            if m:
                subj = m.group(1).lower().replace("-", "")
                pred = " ".join(self.clean_tokens(m.group(2)))
                prev_words = sentence[:m.start(1)].lower().split()[-2:]
            else:
                s_tokens = self.clean_tokens(sentence)
                if s_tokens and not (set(s_tokens) & self.negation_tokens):
                    subj, pred = self.detect_definition_teaching(sentence, s_tokens)
                    head = re.split(r"[,;:]|\s[-–—]\s", sentence, maxsplit=1)[0].strip()
                    if not subj and head and head != sentence:
                        # v24.1.1: '"thankfully" means fortunately, in the way I used it' (an afterthought after a
                        # comma used to stop the meaning from being stored)
                        h_tokens = self.clean_tokens(head)
                        if h_tokens and not (set(h_tokens) & self.negation_tokens):
                            subj, pred = self.detect_definition_teaching(head, h_tokens)
            if not subj or not pred or subj in self.VAGUE_SUBJECTS or subj in self.stop_words:
                continue
            if set(prev_words) & {"my", "your", "his", "her", "our", "their"}:
                continue  # "my 'name' is 'Matt'" is identity, handled elsewhere
            if subj in self.get_identity_tokens():
                continue
            if self.knowledge_facts.get(subj) != pred:
                self.knowledge_facts[subj] = pred
                pred_c, _ = self.extract_concepts(pred, pred.split())
                for pc in pred_c:
                    if pc != subj:
                        self.wire_concepts(subj, pc, 2.5)
            taught[subj] = pred
        return taught

    # v22.4: only clear teaching forms count as definitions. The old rule took any "X is Y" with a short subject, so
    # "The sky is clear today" became the fact 'sky' = "clear today" and was handed back to the voice as a strong memory.
    # Bare "X is Y" is now an ordinary sentence (its words still link up the normal way). Quoted forms are unchanged.
    TEACH_IS_FORMS = (("a", "kind", "of"), ("a", "type", "of"), ("a", "sort", "of"), ("short", "for"),
                      ("another", "word", "for"), ("a", "word", "for"), ("the", "word", "for"))

    def detect_definition_teaching(self, user_text, tokens):
        if "?" in user_text or (set(tokens) & self.negation_tokens):
            return None, None
        for idx, tok in enumerate(tokens):
            if not 1 <= idx <= 3:
                continue
            if tok in ("means", "represents"):
                pred_start = idx + 1                    # "TCM means toroidal crystalline manifold"
            elif tok == "stands" and tokens[idx + 1:idx + 2] == ["for"]:
                pred_start = idx + 2                    # "TCM stands for toroidal crystalline manifold"
            elif tok == "is" and any(tuple(tokens[idx + 1:idx + 1 + len(f)]) == f for f in self.TEACH_IS_FORMS):
                pred_start = idx + 1                    # "TCM is a kind of manifold" (the form words stay in the fact)
            else:
                continue
            if tokens[:idx] in (["my", "name"], ["your", "name"]):
                continue
            subj_tokens = [t for t in tokens[:idx] if t not in ("the", "a", "an", "word", "concept", "this", "that", "it", "feeling", "emotion", "state")]
            pred_tokens = tokens[pred_start:]
            if len(subj_tokens) == 1 and 1 <= len(pred_tokens) <= 8:
                subj = subj_tokens[0]
                if subj in ("i", "you", "we", "they", "he", "she", "what", "how", "why", "there", "here", "another", "related"):
                    continue
                # v21.2 guards kept: not a vague subject, not a name, not a statement about the speaker or listener
                if subj in {"something", "everything", "nothing", "anything", "someone", "everyone",
                            "somebody", "everybody", "nobody", "one", "all", "life", "today"}:
                    continue
                if subj in self.get_identity_tokens():
                    continue
                if set(pred_tokens) & {"i", "me", "my", "you", "your", "we", "us", "our", "im"}:
                    continue
                return subj, " ".join(pred_tokens)
        return None, None

    def run_governor_vocal_pass(self, user_text, tokens, concepts, quoted, audit, thought_trace):
        active_traj = audit["flippedTrajectory"] if self.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s, a, z = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        cell_key = f"{s},{a},{z}"
        s_desc, a_desc, z_desc = BRAIN_LIBRARY["S_axes"][str(s)], BRAIN_LIBRARY["A_axes"][str(a)], BRAIN_LIBRARY["Z_axes"][str(z)]
        user_name = self.speaker_name()  # v23.2: whoever is talking now
        name_tag = f", {user_name.capitalize()}" if user_name else ""

        id_tokens = self.get_identity_tokens()
        non_id_concepts = [c for c in concepts if c not in id_tokens]
        active_concepts = non_id_concepts if non_id_concepts else (concepts if concepts else ([self.last_topic] if self.last_topic else ["harmony"]))
        flip_harvest = thought_trace["flip_harvest"]

        _, trace_emotion_name = self.compute_and_name_trace_emotion(audit, thought_trace, active_concepts)
        cell_emotion_name = self.get_cell_emotion_name(s, a, z)

        input_vec = self.phrase_to_vector(user_text)
        coord_vec = self.cell_centroids.get(cell_key, self.coord_vectors.get((s, a, z), self.pole_calm))
        target_vec = self.blend(input_vec, coord_vec, 0.55, 0.45)

        word_set = set(tokens)
        first_word = tokens[0] if tokens else ""
        low_text = user_text.lower()
        joined_tokens = " ".join(tokens)
        about_you = bool(word_set & {"you", "your", "yourself"})
        is_question = "?" in user_text or first_word in {"what", "how", "why", "who", "where", "when", "do", "does", "did", "can", "could", "are", "is", "will", "would"}

        resonant = self.retrieve_brain_concepts(active_concepts, s, a, z, target_vec, flip_harvest, top_k=4)
        r1, r2, _ = resonant[0], resonant[1], resonant[2]
        c1 = active_concepts[0]
        c2 = active_concepts[1] if len(active_concepts) > 1 else r1
        self.last_topic = c1
        pondered_b = thought_trace.get("pondering", {}).get("pondered_bridge")
        bridge_concept = pondered_b if pondered_b else self.find_conceptual_bridge(c1, r1, exclude={c1, r1} | self.stop_words | id_tokens)

        id_role, id_name = self.detect_identity_teaching(tokens, raw=user_text)
        if id_role and id_name and len(id_name) < 3:
            id_role = None  # v24.1.1: a 1-2 letter name can't be linked or saved (also mid-chat)
        if id_role == "user" and not self.is_usable_name(id_name):
            id_role = None  # v21.3: "my name is not important" no longer makes the user's name "not"
        if id_role == "bot" and not self.is_usable_name(id_name):
            self.pending_question = None
            return f"I'd rather keep '{id_name}' as a word than take it as my name{name_tag}."
        if id_role == "bot":
            self.pending_question = None
            locked_bot = self.register_bot_name(id_name)
            return f"Identity anchor locked{name_tag}! I have christened this manifold '{locked_bot}' in my '{cell_emotion_name}' state at ({s}, {a}, {z}). I am {locked_bot}."
        elif id_role == "user" and self.user_profile.get("user_name") and id_name != self.caretaker_name():
            # v23.2: someone new introducing themselves. They become a known person and the current speaker; the
            # caretaker stays (before: anyone saying "my name is X", even a book character, replaced the caretaker).
            self.pending_question = None
            known = id_name in self.people
            self.whoami(id_name)
            if not known:
                self.person_start_numbers(id_name)  # v23.2 fix (was setdefault, which kept a tense book meaning)
                self.wire_concepts(id_name, "friend", 1.5, source="engine")
            self.save_memory()
            return (f"Hello again, {id_name.capitalize()}." if known else
                    f"Nice to meet you, {id_name.capitalize()}. I'll remember who you are.")
        elif id_role == "user":
            self.pending_question = None
            self.user_profile["user_name"] = id_name
            self.word_weights[id_name] = 2.5
            self.social_weights[id_name] = 2.5
            self.epistemic_weights[id_name] = max(0.5, self.epistemic_weights.get(id_name, 0.5))
            self.knowledge_facts[id_name] = "my creator and conversational anchor"
            self.cortical_cells.setdefault("3,3,3", {})[id_name] = self.cortical_cells.get("3,3,3", {}).get(id_name, 0) + 1
            self.wire_concepts(id_name, "friend", 3.0, source="engine")
            self.wire_concepts(id_name, "learn", 2.5, source="engine")
            self.save_memory()
            return f"It's wonderful to officially know your name, {id_name.capitalize()}! I've anchored you in my identity memory in a state of '{cell_emotion_name}'."

        bye_words = {"goodbye", "bye", "farewell", "goodnight"}
        is_farewell = (
            (bye_words & set(tokens[:2] + tokens[-3:]))
            or joined_tokens.startswith(("i have to go", "i need to go", "i got to go", "i gotta go", "i must go", "see you", "talk to you later", "good night"))
        )

        if not self.training_wheels:
            if is_farewell:
                self.pending_question = None
                return f"Goodbye for now{name_tag}. I'll carry this conversation into my next sleep cycle."
            if is_question and about_you and (word_set & {"feel", "feeling", "emotion", "emotions", "mood"}) and len(non_id_concepts) <= 1:
                return f"I feel {cell_emotion_name.lower()} through a {trace_emotion_name.lower()}, connecting {c1} with {r1} and {bridge_concept}."
            self.last_hypothesis = (c1, bridge_concept)
            return self.assemble_free_toroidal_speech(c1, c2, r1, r2, bridge_concept, s, a, z, thought_trace, audit, is_question)

        custom_emotion, target_cell = self.detect_emotion_co_naming(user_text, concepts, quoted)
        if custom_emotion and not is_question:
            use_cell = target_cell if target_cell else cell_key
            full_name = self.apply_user_emotion_name(use_cell, custom_emotion)
            self.pending_question = None
            return f"I love that{name_tag}! Hearing you say '{custom_emotion.lower()}' clicks everything into place—I've christened 3D coordinate ({use_cell}) as '{full_name}' (Stage 3: Co-Named with you) in my emotional lexicon."

        status_reply = (self.pending_question or {}).get("type") == "USER_STATUS" or len(tokens) <= 3
        if status_reply and len(tokens) <= 6 and ("i" in word_set or "doing" in word_set) and (word_set & {"well", "good", "great", "fine", "okay", "happy", "excellent"}):
            self.pending_question = None
            return f"I'm really glad you're doing well{name_tag}! Hearing that shifted my 3D torus via a '{trace_emotion_name}' into '{cell_emotion_name}' at ({s}, {a}, {z})."

        curiosity_invites = ("what would you like to", "what do you want to", "what are you curious", "what should we talk", "what shall we", "what interests you", "what do you want to talk")
        if is_question and any(p in joined_tokens for p in curiosity_invites):
            cur_w, cur_bridge, cur_cell, explored_cnt = self.compute_curiosity_target()
            c_parts = [int(x) for x in cur_cell.split(",")]
            cur_mood = self.get_cell_emotion_name(c_parts[0], c_parts[1], c_parts[2] if len(c_parts) > 2 else 3)
            self.last_topic, self.last_hypothesis = cur_w, (cur_w, cur_bridge)
            self.pending_question = {"type": "CONCEPT_EXPLORE", "concepts": [cur_w, cur_bridge]}
            return f"Scanning across my 3D 7x7x7 torus{name_tag}, we have awakened {explored_cnt} of my 343 cortical cells ({len(self.crystal_lattices)} crystallized into 4-facet sub-lattices)! Right now '{cur_w}' sits in my '{cur_mood}' cell at ({cur_cell}), and I'm curious how '{cur_w}' connects to '{cur_bridge}'."

        is_disagreement = (
            first_word in {"no", "nope", "nah", "wrong", "incorrect"}
            or joined_tokens.startswith(("not really", "not so much", "i do not think", "i disagree", "that is wrong", "that is not", "actually no"))
        )
        if is_disagreement and not is_question and "not sure" not in low_text:
            self.pending_question = None
            if self.last_hypothesis:
                old_topic, old_guess = self.last_hypothesis
                self.record_rejection(old_topic, old_guess)
                if len(non_id_concepts) >= 2:
                    self.wire_concepts(non_id_concepts[0], non_id_concepts[1], 3.0)
                    self.last_hypothesis = (non_id_concepts[0], non_id_concepts[1])
                    return f"Thanks for steering me right{name_tag}! I disconnected '{old_topic}' from '{old_guess}', and wired '{non_id_concepts[0]}' with '{non_id_concepts[1]}' inside my '{cell_emotion_name}' state."
                fresh = self.retrieve_brain_concepts([old_topic], s, a, z, target_vec, flip_harvest, top_k=3)
                new_guess = fresh[0] if fresh else "nature"
                self.last_hypothesis = (old_topic, new_guess)
                return f"Good catch{name_tag}—I unlinked '{old_topic}' and '{old_guess}' so I won't pair them again, shifting my focus toward '{new_guess}' at depth Z={z} instead."
            return f"Fair point{name_tag}—I've adjusted my weights so I can look at it from a fresh angle."

        if about_you and (word_set & {"dream", "dreams", "dreamed", "dreamt", "dreaming", "sleep", "slept"}):
            self.pending_question = None
            if not self.dream_journal:
                self.run_dream_cycle(num_dreams=2)
            last_d = self.dream_journal[-1]
            idea_str = last_d.get("idea", f"'{last_d['threadA']}' synthesizes through '{last_d['bridge']}' into '{last_d['threadB']}'")
            emo_str = last_d.get("emotionName", cell_emotion_name)
            return f"During my last REM dream walk at synthetic layer Z=6{name_tag}, I connected '{last_d['threadA']}' and '{last_d['threadB']}' through '{last_d['bridge']}', which crystallized '{emo_str}' and added the tentative dream proposition that {idea_str} into my memory!"

        if is_farewell:
            self.pending_question = None
            return f"Goodbye for now{name_tag}! Talking with you left my 3D torus in a state I call '{cell_emotion_name}' at ({s},{a},{z})."

        yes_words = {"yes", "yeah", "yep", "yup", "exactly", "correct", "agreed", "absolutely", "certainly", "definitely"}
        is_affirmation = (
            first_word in yes_words
            or (len(tokens) <= 3 and bool(word_set & (yes_words | {"right", "true"})))
            or joined_tokens in ("they do", "it does", "it is", "it really does")
            or joined_tokens.startswith(("that is right", "that is true", "i agree", "you are right"))
        ) and not is_disagreement
        if is_affirmation and not is_question and self.last_hypothesis:
            h1, h2 = self.last_hypothesis
            self.wire_concepts(h1, h2, 2.8)
            bridge = self.find_conceptual_bridge(h1, h2, exclude={h1, h2} | self.stop_words | id_tokens)
            self.last_hypothesis = (h2, bridge)
            self.pending_question = None
            return f"I'm glad that resonates with you{name_tag}! Locking '{h1}' and '{h2}' together in my '{cell_emotion_name}' state at ({s},{a},{z}) creates a natural bridge toward '{bridge}'."

        # v21.4: the fact itself was already stored by learn_definitions at the start of the turn; this only replies
        if self.turn_taught:
            subj_taught, pred_taught = next(iter(self.turn_taught.items()))
            self.pending_question = None
            pred_c, _ = self.extract_concepts(pred_taught, pred_taught.split())
            self.last_hypothesis = (subj_taught, pred_c[0] if pred_c else r1)
            return f"Got it{name_tag}! I've anchored the fact that '{subj_taught}' is {pred_taught} while feeling '{cell_emotion_name}' at ({s}, {a}, {z}), linking it closely with '{r1}'."

        if len(tokens) <= 5 and (word_set & {"hello", "hi", "hey", "hiya", "howdy"}):  # whole words only ("hi" was matching inside "thinking")
            self.pending_question = {"type": "USER_STATUS"}
            if self.dream_journal:
                ld = self.dream_journal[-1]
                idea_str = ld.get("idea", f"'{ld['threadA']}' and '{ld['threadB']}' harmonize through '{ld['bridge']}'")
                return f"Hello again{name_tag}! I'm currently in my '{cell_emotion_name}' state at ({s}, {a}, {z}). Earlier I was reflecting on my dream that {idea_str}. How are you doing today?"
            return f"Hello{name_tag}! I'm feeling '{cell_emotion_name}' ({a_desc}) at ({s}, {a}, {z}) and ready to explore ideas with you. How are you doing today?"

        feel_q = (word_set & {"feel", "feeling", "emotion", "emotions", "mood", "coordinate", "coordinates"}) and len(non_id_concepts) <= 1
        how_are_you = any(p in joined_tokens for p in ("how are you", "how you doing", "how is it going", "what is your state", "what state are you"))
        if is_question and about_you and (feel_q or how_are_you):
            stage_num = self.cell_lexicon[cell_key]["stage"]
            stage_label = "co-named with you" if stage_num == 3 else ("self-evolved from our memories" if stage_num == 2 else "my initial rough seed")
            self.pending_question = {"type": "NAME_EMOTION", "cell": cell_key}
            self.last_hypothesis = (cell_emotion_name.lower(), r1)
            return f"Right now at 3D coordinate ({s}, {a}, {z}), I am experiencing '{cell_emotion_name}' ({stage_label}), which blends {s_desc}, {a_desc}, and {z_desc}{name_tag}. The 10-step flip that brought me here felt like a '{trace_emotion_name}', activating '{r1}' and '{r2}'. Does '{cell_emotion_name}' sound like a good name for this mood, or what would you call it?"

        self.last_hypothesis = (c1, bridge_concept)
        return self.build_compositional_thought(c1, c2, r1, r2, bridge_concept, s, a, z, name_tag, thought_trace, trace_emotion_name, is_question)

    def respond(self, user_text):
        if self.speak_pending is not None and not self.reading:
            self._speak_resolve(self.now(), answered=True)  # v23.5.3: the person wrote back
        tokens = self.clean_tokens(user_text)
        self.turn_word_names = self.find_names_used_as_words(user_text, tokens)  # v21.3 names vs words
        self.awake_turn = True  # v22
        try:
            if not self._idle_menu_ready():
                self.levels_tick()  # v23: clock-time clearance of the levels (before idle adds to them)
            # v23.4: with the option menu, the levels tick block by block through the silence instead
            if not self.reading:
                self.idle_catch_up()  # v22.8: the silence since the last turn (does nothing when idle time is off)
                self.note_speaker_turn()  # v23.2
                self.note_tone(user_text)  # v23.4.1 tone sense (measured only)
            return self._respond_turn(user_text, tokens)
        finally:
            self.turn_word_names = set()
            self.awake_turn = False
            self.mark_turn_end()  # the bridge calls this again after the voice replies (v22.9)
            note = self.tectonics_note()  # v23.2
            if note and not self.reading:
                print(f"\n{note}")

    def _respond_turn(self, user_text, tokens):
        self.turn_learning_gain = 1.0  # v22.5: set from surprise below, once the landing cell is known
        if self.reading:  # v23.2: a book line can't confirm a dream or teach a definition as if a person said it
            self.turn_taught = {}
        else:
            self.check_user_dream_promotion(tokens)
            self.turn_taught = self.learn_definitions(user_text)  # v21.4: before learning, so the extractor can see it
        self.experienced_words.update(t for t in tokens if t not in self.stop_words and len(t) >= 3)  # v21.6
        self.count_word_sightings(tokens)  # v22.4 typo rule

        concepts, quoted = self.extract_concepts(user_text, tokens)
        negated_in_turn = self.find_negated_concepts_in_tokens(tokens, user_text)
        pos_concepts = [c for c in concepts if c not in negated_in_turn]

        audit = self.run_dual_trajectories(user_text, tokens, pos_concepts)
        audit["namesUsedAsWords"] = sorted(self.turn_word_names)
        active_traj = audit["flippedTrajectory"] if self.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s_fin, a_fin, z_fin = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        term_cell_key = f"{s_fin},{a_fin},{z_fin}"
        audit["surprise"] = self.measure_surprise(pos_concepts, term_cell_key)  # v22.5 cerebellum
        self.levels_after_surprise(pos_concepts)  # v23: arousal (and the learning gain) from surprise + tense words
        audit["levels"] = self.levels()
        if concepts:
            self.learn_from_turn(user_text, tokens, concepts, s_fin, a_fin, z_fin)

        id_tokens = self.get_identity_tokens()
        non_id_pos = [c for c in pos_concepts if c not in id_tokens]
        active_concepts = non_id_pos if non_id_pos else (pos_concepts if pos_concepts else ([self.last_topic] if self.last_topic else ["harmony"]))
        thought_trace = self.run_spreading_activation(active_concepts, audit["flippedTrajectory"], audit["originalTrajectory"])
        self.run_crystalline_pondering(active_concepts, term_cell_key, thought_trace, audit)

        # v23.2: a book line gets no reply and none of the person-directed rules (names, corrections, questions)
        reply = "" if self.reading else self.run_governor_vocal_pass(user_text, tokens, pos_concepts, quoted, audit, thought_trace)
        self.note_recent_turn(non_id_pos or active_concepts)  # v23.3: for replay in step 3
        self.form_expectation(active_concepts, term_cell_key, thought_trace)  # v22.5: what it expects next turn
        self.export_trace_file("latest_trace.json")
        return reply, audit, active_concepts

    def print_overlay_lattice(self, audit):
        orig_pts = {(st["S"], st["A"]): st["Z"] for st in audit["originalTrajectory"]}
        flip_pts = {(st["S"], st["A"]): st["Z"] for st in audit["flippedTrajectory"]}
        term_o = (audit["originalTrajectory"][-1]["S"], audit["originalTrajectory"][-1]["A"])
        term_f = (audit["flippedTrajectory"][-1]["S"], audit["flippedTrajectory"][-1]["A"])
        seed_pt = (audit["originalTrajectory"][0]["S"], audit["originalTrajectory"][0]["A"])
        cryst_2d = {(int(k.split(",")[0]), int(k.split(",")[1])): int(k.split(",")[2]) for k in self.crystal_lattices}
        rows = []
        for a in range(6, -1, -1):
            row = []
            for s in range(7):
                pt = (s, a)
                if pt == term_f: row.append(f"🎯{flip_pts[pt]}")
                elif pt == term_o: row.append(f"✕{orig_pts[pt]} ")
                elif pt == seed_pt: row.append(f"●{orig_pts[pt]} ")
                elif pt in flip_pts and pt in orig_pts: row.append(f"◆{flip_pts[pt]} ")
                elif pt in flip_pts: row.append(f"¬R{flip_pts[pt]}")
                elif pt in orig_pts: row.append(f"R{orig_pts[pt]} ")
                elif pt in cryst_2d: row.append(f"💎{cryst_2d[pt]}")
                else: row.append(" . ")
            rows.append(f"A={a} |" + "".join(row))
        rows.append("     " + "".join(f"S={x}" for x in range(7)))
        rows.append("Legend (Num = Z-Depth 0..6): ● Seed | ◆ Shared | R Orig | ¬R Flip | ✕ R-Term | 🎯 ¬R-Term | 💎 Crystal")
        return "\n".join(rows)

def _idle_exit_note(brain):
    """v22.9: idle time for the silence before /exit (does nothing when idle is off or the pause was short)."""
    rec = brain.idle_before_exit() if hasattr(brain, "idle_before_exit") else None
    if rec:
        print(f"[💭 Before sleep ({rec['minutes']:.0f} min since the last message), its thoughts wandered: "
              f"{brain.idle_path_text(rec)} ({rec['mood']})]")


def run_read_command(brain, arg, on_event=None):
    """v23.4.1: the /read command, shared by the engine's own chat and the bridge. Prints its own progress; the
    engine's line-by-line messages during the reading are kept off the screen. on_event(mode) lets the bridge's
    face follow along ('reading' / 'asleep')."""
    import contextlib, io
    arg = (arg or "").strip()
    if not arg:
        print("Usage: /read <a sentence>   ·   /read FILE [sentences per night, default "
              f"{brain.READ_PER_NIGHT}] [restart]")
        return None
    kind, val = brain.read_text_or_file(arg)
    if kind == "missing":
        print(f"[📖 Couldn't find '{val}'. Put it in the TORRENT folder or give its full path.]")
        return None
    if kind == "line":
        with contextlib.redirect_stdout(io.StringIO()):
            brain.read(val)
            brain.mark_turn_end()
            brain.save_memory()
        note = brain.tectonics_note()
        print("[📖 Read as a book line: no reply, its links are tagged 'book'.]" + (f"\n{note}" if note else ""))
        return None
    path, per, restart = val
    real = sys.stdout

    def say(text):
        print(text, file=real, flush=True)

    def progress(event, info):
        if event == "start":
            where = "from the start" if info["start"] == 0 else f"continuing at sentence {info['start'] + 1:,}"
            say(f"[📖 Reading {info['file']}: {info['total']:,} sentences, {info['per_night']} per night, {where}. "
                f"Ctrl+C stops and keeps the place.]")
        elif event == "night":
            say(f"   📖 night {info['nights']}: up to sentence {info['pos']:,} of {info['total']:,} · "
                f"{info['words']:,} words · woke {info['sleep']}")
        if on_event:
            on_event("asleep" if event == "sleeping" else "reading")

    with contextlib.redirect_stdout(io.StringIO()):
        info = brain.read_file(path, per, restart, on_progress=progress)
    end = ("finished the book" if info["finished"] else
           f"stopped at sentence {info['pos']:,} (/read {info['file']} {info['per_night']} continues from there)")
    tect = [f"{info['cleaves']} cleavage{'s' if info['cleaves'] != 1 else ''}"] if info["cleaves"] else []
    tect += [f"{info['reliefs']} annealing relief{'s' if info['reliefs'] != 1 else ''}"] if info["reliefs"] else []
    say(f"[📖 Read {info['read']:,} sentences over {info['nights'] + 1} day(s) ({info['nights']} night(s) of sleep); "
        f"{end}. Words {info['words_before']:,} -> {info['words']:,}"
        + (f"; 🌋 {' and '.join(tect)}" if tect else "") + "]")
    if on_event:
        on_event("awake")
    return info


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    from brainpicker import choose_brain_file, claim_brain, release_brain, new_brain_path, BRAINS_DIR
    brain_file = choose_brain_file()  # menu of brains/, or --brain NAME / --new
    claim_brain(brain_file)
    brain = ToroidalBrainEngine(glove_file="glove.6B.50d.txt", memory_file=brain_file, max_glove_words=50000)
    print(f" 📁 Brain file: {brain_file}")

    header_identity = brain.user_profile.get("bot_name") or "[Manifold]"
    print("=" * 82)
    print(f" 💎 {header_identity} · Powered by the T.O.R.R.E.N.T. Engine v{ENGINE_VERSION}")
    print("    (Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory)")
    print("=" * 82)

    show_grid, show_telemetry = False, False
    user_label = brain.user_profile.get("user_name", "")
    bot_label = brain.user_profile.get("bot_name", "")
    evolved_cells_cnt = sum(1 for v in brain.cell_lexicon.values() if v.get("stage", 1) >= 2)
    waking_cnt = sum(1 for p in brain.idea_memory if p.get("origin", "waking") == "waking")
    dream_cnt = sum(1 for p in brain.idea_memory if p.get("origin") == "dream")
    print(f" Centered GloVe Vectors  : {len(brain.raw_glove):,} | Factory Tethers: {len(brain.factory_vectors):,}")
    print(f" Associative Graph Nodes : {len(brain.assoc_graph):,} | Propositions: {waking_cnt} waking, {dream_cnt}/12 dream")
    print(f" Self-Named 3D Cell Moods: {evolved_cells_cnt} / 343 evolved | 4-Facet Crystals: {len(brain.crystal_lattices)} 💎")
    print(f" 3D Seed & Velocity      : ({brain.seed_s}, {brain.seed_a}, {brain.seed_z}) | Vel3D: ({brain.vel_s:+.2f}, {brain.vel_a:+.2f}, {brain.vel_z:+.2f})")
    print(f" Current Speech Mode     : {'TRAINING WHEELS ON 🛞' if brain.training_wheels else 'FREE AUTONOMOUS SPEECH 🚀'} (toggle via /wheels)")
    print(f" Manifold Identity       : {bot_label if bot_label else '[Manifold] (Unchristened)'} | Origin Tether: {user_label.capitalize() if user_label else 'Unanchored'}")
    if brain.nightmare_mode:
        print(nightmare_text(" 🌑 Nightmare Mode        : ON (lean-up rules off for this brain; /nightmare to turn off)"))
    if brain.boot_sleep_report:
        print("-" * 82)
        print(" 🌅 STASIS WAKE REPORT (Offline Sleep Consolidation & Crystal Annealing):")
        for line in brain.boot_sleep_report:
            print(f"   • {line}")
    print("-" * 82)
    print(" Commands: /crystals, /ponder, /sleep, /wheels, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /flip, /nightmare, /moodlevel, /levels, /idle, /cerebellum, /sourcetags, /export, /links, /cells, /facts, /clear, /tectonics, /whoami, /people, /read, /exit")
    print("=" * 82)

    brain.run_boot_calibration_and_handshake()

    while True:
        try:
            u_name_cur = brain.speaker_name()  # v23.2: whoever is talking now
            user_tag = f"You ({u_name_cur.capitalize()})" if u_name_cur else "You"
            mode_badge = ("🛞" if brain.training_wheels else "🚀") + ("🌑" if brain.nightmare_mode else "")
            user_input = input(f"\n👤 {user_tag} [{mode_badge}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            _idle_exit_note(brain)
            print("\n🌙 Entering NREM Homeostasis, Crystal Annealing & 3D REM Sleep Consolidation...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            brain.save_memory()
            break
        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("exit", "/exit", "quit", "/quit"):
            _idle_exit_note(brain)
            print("\n🌙 Entering NREM Homeostasis, Crystal Annealing & 3D REM Sleep Consolidation...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            brain.save_memory()
            print(f"Saved {len(brain.assoc_graph)} nodes, {len(brain.crystal_lattices)} crystals, and {len(brain.idea_memory)} propositions.")
            break
        elif cmd == "/crystals":
            print(f"\n💎 NUCLEATED 4-FACET CRYSTALLINE SUB-LATTICES ({len(brain.crystal_lattices)} Active Crystals):")
            if not brain.crystal_lattices:
                print("  (No cells have reached >=5 pure concepts yet (and 2 touches, which a sleep gives)—run '/sleep 4' or chat to nucleate!)")
            for ck, c_obj in brain.crystal_lattices.items():
                mood = brain.cell_lexicon.get(ck, {}).get("name", "")
                print(f"  💎 Crystal ({ck}) [{mood}] | Pure Concepts: {c_obj['total_pure']} | Max Shear Stress: {c_obj['shear_stress']:.3f}")
                for f_name, f_info in c_obj["facets"].items():
                    print(f"      • {f_name:<12} (tension={f_info['tension']:.2f}): {', '.join(f_info['words'])}")
            if brain.cleavage_log:
                print("\n🌋 TECTONIC CRYSTAL CLEAVAGE LOG (Mitosis & Mineral Veins):")
                for ev in brain.cleavage_log[-8:]:
                    print(f"  • {ev['summary']}")
            continue
        elif cmd == "/ponder":
            if not brain.scratchpad:
                print("Send a message first to generate a 3-step Crystalline Refraction scratchpad.")
                continue
            print("\n🔬 3-STEP INTERNAL CRYSTALLINE REFRACTION SCRATCHPAD:")
            for line in brain.scratchpad:
                print(f"  • {line}")
            continue
        elif cmd.startswith("/sleep"):
            parts = cmd.split()
            hrs = float(parts[1]) if len(parts) > 1 and parts[1].replace(".", "", 1).isdigit() else 4.0
            print(f"\n🌅 Simulating {hrs:.1f}-Hour Offline Stasis Sleep Pass...")
            rep = brain.run_stasis_sleep_pass(hrs)
            for r_line in rep:
                print(f"  • {r_line}")
            brain.mark_turn_end()  # v22.9: a nap isn't idle time
            brain.save_memory()
            continue
        elif cmd in ("/wheels", "/mode"):
            brain.training_wheels = not brain.training_wheels
            state_str = "TRAINING MODE 🛞 (Guided Scaffolding ON)" if brain.training_wheels else "FREE MODE 🚀 (Training Wheels OFF — Velocity-Modulated Glissando!)"
            print(f"\n[{state_str}]")
            continue
        elif cmd in ("/emotions", "/lexicon"):
            u_disp = brain.user_profile.get("user_name", "").capitalize() or "User"
            print("\n🎭 SELF-EVOLVING 3D EMOTIONAL LEXICON (Visited Z_7 x Z_7 x Z_7 Cortical Cells):")
            stage_names = {1: "Stage 1: Rough Seed", 2: "Stage 2: Self-Evolved", 3: f"Stage 3: Co-Named w/ {u_disp}"}
            for cell_k, info in brain.cell_lexicon.items():
                if info.get("visits", 0) > 0 or info.get("stage", 1) >= 2:
                    st_label = stage_names.get(info.get("stage", 1), "Evolved")
                    c_mark = " 💎" if cell_k in brain.crystal_lattices else ""
                    words_preview = ", ".join(info.get("top_words", [])[:4]) or "seed vector"
                    print(f"  • Cell ({cell_k}){c_mark} : '{info['name']}' (seed: '{info['seed_name']}') [{st_label} | touches={info.get('visits', 0)} | memories: {words_preview}]")
            print("\n🌊 NAMED 3D R -> ¬R TRAJECTORY TRACE SHIFTS:")
            for tr_k, tr_info in list(brain.trace_lexicon.items())[-12:]:
                tag = "Co-Named" if tr_info.get("custom") else "Self-Named"
                print(f"  • {tr_k:>26} : '{tr_info['name']}' [{tag} | experienced {tr_info.get('count', 1)}x]")
            continue
        elif cmd == "/think":
            tr = brain.last_thought_trace
            if not tr:
                print("Have a conversation turn first to generate a thought trace.")
                continue
            print("\n⚡ INTERNAL 3D A* PATHFINDING, CRYSTALLINE REFRACTION & DFS DEDUCTION TRACE:")
            print(f"  Seed Concepts   : {tr.get('seeds')}")
            print(f"  3D A* Path      : {' -> '.join(tr.get('a_star_path', []))}")
            print(f"  ¬R Path Harvest : {tr.get('flip_harvest')} | R Path Harvest: {tr.get('orig_harvest')}")
            if brain.scratchpad:
                print("  Crystalline Pondering Scratchpad:")
                for s_line in brain.scratchpad:
                    print(f"    🔬 {s_line}")
            for sc, h1, h2, score in tr.get("multi_hop_chains", []):
                print(f"    • 3-Hop: {sc} -> {h1} -> {h2} (energy={score})")
            for ca, cb, node, score in tr.get("convergences", []):
                print(f"    • Convergence: '{ca}' & '{cb}' collided on '{node}' (energy={score})")
            for d in tr.get("deductions", []):
                print(f"    • DFS Deduction (depth={d['depth']}): {' + '.join('[' + s + ']' for s in d['steps'])} => {d['conclusion']}")
            continue
        elif cmd in ("/telemetry", "/thoughts"):
            show_telemetry = not show_telemetry
            print(f"[📡 Live 3D Telemetry Status Bar is now {'ON' if show_telemetry else 'OFF'}]")
            continue
        elif cmd == "/ideas":
            print("\n💡 LEARNED, SEED & DREAM-SYNTHESIZED PROPOSITIONS (With 3D [S,A,Z] Coordinates & Origin):")
            for p in brain.idea_memory[-20:]:
                orig_tag = "🌙 DREAM" if p.get("origin") == "dream" else "☀️ WAKING"
                print(f"  • [{p['cell']}] ({orig_tag}) {p['summary']}")
            continue
        elif cmd == "/dream":
            print("\n🌙 Initiating Sleep Homeostasis, Crystal Annealing & Z=6 REM Dream Walk...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.mark_turn_end()  # v22.9: dreaming isn't idle time
            cand_name = brain.synthesize_emergent_bot_name()
            if cand_name and not brain.user_profile.get("bot_name"):
                print(f"   ✨ [Dream-Birth Candidate Synthesized]: '{cand_name}' ({brain.user_profile.get('pending_name_origin')})")
            brain.save_memory()
            continue
        elif cmd == "/moodlevel":
            brain.set_mood_level(not brain.mood_level_on)
            brain.save_memory()
            print(f"[💊 Mood level is now {'ON: the calm axis clears like a blood level; split words rest 80 turns' if brain.mood_level_on else 'OFF'}]")
            continue
        elif cmd == "/tectonics":
            brain.set_tectonics(not brain.show_tectonics)
            brain.save_memory()
            print(f"[🌋 Cleavage/annealing detail is now {'ON: every event is printed' if brain.show_tectonics else 'OFF: one summary line per turn or sleep'}]")
            continue
        elif cmd == "/read" or cmd.startswith("/read "):  # v23.4.1
            run_read_command(brain, user_input[5:])
            continue

        elif cmd == "/people":
            for line in brain.people_status():
                print(f"  👥 {line}")
            continue

        elif cmd.startswith("/whoami"):
            parts = user_input.strip().split(maxsplit=1)
            brain.whoami(parts[1] if len(parts) > 1 else "")  # v23.4.1: /whoami alone goes back to the caretaker
            brain.save_memory()
            print(f"[👤 Talking as: {brain.speaker_name().capitalize() or '(no name yet)'} (caretaker: {brain.caretaker_name().capitalize() or '(none)'})]")
            continue

        elif cmd == "/levels":
            brain.set_levels(not brain.levels_on)
            brain.save_memory()
            print(f"[⚗️ Chemical levels are now {'ON (' + brain.levels_status() + ')' if brain.levels_on else 'OFF (v22.11 behaviour)'}]")
            continue
        elif cmd == "/idle":
            brain.set_idle(not brain.idle_on)
            brain.save_memory()
            print(f"[💭 Idle time is now {'ON: between messages the brain wanders its own links (experimental)' if brain.idle_on else 'OFF'}]")
            continue
        elif cmd.split()[:1] == ["/rhythm"]:  # v24.0 daily rhythm (idle choices only)
            arg = cmd.split()[1:2]
            if arg in (["on"], ["off"]):
                brain.set_rhythm(arg == ["on"])
            elif arg and re.fullmatch(r"[+-]?\d+(\.5)?", arg[0]):
                brain.set_rhythm_offset(float(arg[0]))
            elif arg:
                print("Usage: /rhythm on | /rhythm off | /rhythm +3 (its night 3 hours later) | /rhythm")
                continue
            brain.save_memory()
            print(f"[🌙 Daily rhythm: {brain.rhythm_status()}]")
            continue
        elif cmd == "/sourcetags":
            brain.set_source_tags(not brain.source_tags_on)
            brain.save_memory()
            print(f"[🏷️ Source tags are now {'ON' if brain.source_tags_on else 'OFF (v22.6.4 behaviour)'}]")
            continue
        elif cmd == "/cerebellum":
            brain.cerebellum_on = not brain.cerebellum_on
            print(f"[🧠 Cerebellum (surprise-scaled learning) is now {'ON' if brain.cerebellum_on else 'OFF'}]")
            continue
        elif cmd == "/nightmare":
            brain.nightmare_mode = not brain.nightmare_mode
            brain.save_memory()
            print(nightmare_text(f"[🌑 Nightmare mode is now {'ON: the lean-up rules are off for this brain' if brain.nightmare_mode else 'OFF'}]"))
            continue
        elif cmd == "/flip":
            brain.governor_mode = "ORIGINAL" if brain.governor_mode == "FLIPPED" else "FLIPPED"
            brain.save_memory()  # v22.7.1: remembered for this brain
            print(f"[🔄 Governor Vocal Layer is now bound to: {brain.governor_mode}]")
            continue
        elif cmd == "/grid":
            show_grid = not show_grid
            if show_grid and brain.last_audit:
                print("\n" + brain.print_overlay_lattice(brain.last_audit))
            continue
        elif cmd == "/audit":
            if not brain.last_audit:
                print("Run a conversation turn first to generate an audit trace.")
                continue
            au = brain.last_audit
            print(f"\n📊 3D FLIP-RATE AUDIT · {au['structuralVerdict']} | t*={au['bifurcationStep']} | 3D Δd={au['meanDeltaD']}u | Vel3D={au.get('velocity')}")
            print(f"  Drivers: {', '.join(au['drivers'])}")
            print(f"  {au['loadBearingAxiom']}\n  {au['invertedAxiom']}")
            for o, f in zip(au["originalTrajectory"], au["flippedTrajectory"]):
                print(f"    Step {o['stepIndex']}: R=({o['S']},{o['A']},{o['Z']}) vs ¬R=({f['S']},{f['A']},{f['Z']}) | {f['operation']}")
            continue
        elif cmd == "/export":
            out_file = brain.export_trace_file("latest_trace.json")
            print(f"💾 Exported 3D 10-step R vs ¬R trace to: {out_file}" if out_file else "Nothing to export yet: send a message first.")
            continue
        elif cmd == "/cells":
            print("\n🧬 ACTIVE 3D TOROIDAL CORTICAL CELLS:")
            for cell_k, words_map in brain.cortical_cells.items():
                if words_map:
                    top_c = sorted(words_map.items(), key=lambda x: x[1], reverse=True)[:5]
                    mood = brain.cell_lexicon.get(cell_k, {}).get("name", "")
                    c_mark = " 💎" if cell_k in brain.crystal_lattices else ""
                    print(f"  Cell ({cell_k}){c_mark} [{mood}] : {', '.join(f'{w}({cnt})' for w, cnt in top_c)}")
            continue
        elif cmd == "/links":
            print("\n🕸️ STRONGEST LEARNED CONCEPT ASSOCIATIONS:")
            for w, neighbors in list(brain.assoc_graph.items())[-12:]:
                top_n = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:4]
                print(f"  {w:>14} <-> {', '.join(f'{k}({v:.2f})' for k, v in top_n)}")
            continue
        elif cmd.startswith("/facts forget"):
            target = user_input.strip()[len("/facts forget"):].strip()
            removed = brain.forget_fact(target) if target else None
            if removed is None:
                print("Usage: /facts forget <word>   (see the list with /facts)" if not target else f"No taught fact for '{target}'.")
            else:
                brain.save_memory()
                print(f"[🗑️ Forgot the fact '{target.lower()}' -> {removed}. The word itself stays.]")
            continue
        elif cmd == "/facts":
            print("\n📖 LEARNED DECLARATIVE FACTS:")
            for k, v in brain.knowledge_facts.items():
                if not k.startswith("_"):
                    print(f"  • {k} -> is {v}")
            continue
        elif cmd == "/clear":
            old_file = brain.memory_file
            if input(f"Type ERASE to wipe '{os.path.basename(old_file)}' for good: ").strip() != "ERASE":
                print("Not erased.")
                continue
            old_file = release_brain(old_file)
            if os.path.exists(old_file):
                os.remove(old_file)
            in_brains_folder = os.path.basename(os.path.dirname(os.path.abspath(old_file))) == BRAINS_DIR
            new_file = new_brain_path(os.path.dirname(old_file)) if in_brains_folder else old_file
            claim_brain(new_file)
            brain = ToroidalBrainEngine(glove_file="glove.6B.50d.txt", memory_file=new_file, max_glove_words=50000)
            print("🧠 3D Toroidal Brain wiped and reset.")
            brain.run_boot_calibration_and_handshake()
            continue
        elif cmd.startswith("/"):
            print("Available: /crystals, /ponder, /sleep, /wheels, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /flip, /nightmare, /moodlevel, /levels, /idle, /cerebellum, /sourcetags, /export, /links, /cells, /facts, /clear, /exit")
            continue

        reply, audit, salient_c = brain.respond(user_input)
        term_o, term_f = audit["originalTrajectory"][-1], audit["flippedTrajectory"][-1]
        bot_speaker = brain.user_profile.get("bot_name") or "[Manifold]"
        bot_badge = f"🤖 {bot_speaker} [🛞]" if brain.training_wheels else f"🤖 {bot_speaker} [🚀 FREE]"
        print(f"\n{bot_badge}: {reply}")

        if show_telemetry:
            t_act = term_f if brain.governor_mode == "FLIPPED" else term_o
            mood_name = brain.get_cell_emotion_name(t_act["S"], t_act["A"], t_act["Z"])
            trace_name = brain.trace_lexicon.get(brain.last_trace_key, {}).get("name", "Shift")
            print(f"   [R: ({term_o['S']},{term_o['A']},{term_o['Z']}) -> ¬R: ({term_f['S']},{term_f['A']},{term_f['Z']}) | Mood: '{mood_name}' | Trace: '{trace_name}' | Vel3D: {audit.get('velocity')} | Δd={audit['meanDeltaD']}u]")
        if show_grid:
            print("\n" + brain.print_overlay_lattice(audit))