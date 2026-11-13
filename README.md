# T.O.R.R.E.N.T.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24040746.svg)](https://doi.org/10.5281/zenodo.24040746)

**Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory**

An experimental "language-enabled toroidal crystalline manifold" (LTCM): a small, standard-library Python engine that keeps a persistent semantic state on a 7×7×7 wraparound lattice, learns word associations, consolidates them offline ("sleep" and "dreams"), and can feed its state to a local LLM.

> **Status: experimental research code.** There are no benchmarks. Nothing here has been shown to reduce hallucination or improve LLM accuracy. See the limitations section of the disclosure.

## What's in this repo

| File | Purpose |
|---|---|
| `torrentengine.py` | The engine (v24.1.1). Standard library only. |
| `torrent_wordspace_50k.gz` | The word space: 50,000 processed GloVe vectors (~20 MB). Keep it next to the engine; it is loaded automatically. |
| `brainpicker.py` | Lets you keep several brains (TCMs) and choose one at start-up. Keep it in the same folder. |
| `ltcmbridge.py` | The easiest way to start: loads the engine and, if a local LLM (Ollama or an OpenAI-compatible server) is reachable, uses it as a voice. Falls back to the engine's own replies otherwise. Optional local voice in/out. |
| `catchup_cells.py` | Optional one-time cleanup for a brain that grew overfull under an engine older than v21.7. Works on a copy. |
| `cleanwords.py` | Optional: finds junk words in a brain file (glued or cut-off words, typos) and removes them. Makes a backup first. |
| `TORRENT_DISCLOSURE.md` | Full technical description of how everything works, published as a defensive disclosure. |
| `TORRENT_DISCLOSURE_ADDENDUM_1.md` | What was added from v21.1 to v24.1.1 (levels, idle time, live idle, speaking up, a sense of time, the bridge's memory and honesty features), in the same defensive-disclosure form. |
| `CHANGELOG.md` | What changed in each version. |
| `LICENSE` | Apache-2.0. |

## Quick start

Keep the `.py` files in the same folder and run the bridge. It loads the engine automatically, so this one command is all you need:

```bash
python ltcmbridge.py
```

- **With a local LLM running** (Ollama or an OpenAI-compatible server), the engine's state is injected into the model's prompt and the model's reply is used.
- **Without one**, the bridge reports the LLM as unreachable and falls back to the engine's own native replies, so you can still talk to T.O.R.R.E.N.T. directly.

You can also run the engine alone, with no bridge code at all:

```bash
python torrentengine.py
```

On first run it asks for a name to anchor the space. Type `/exit` to quit cleanly; this runs the sleep and dream cycle and saves state. The latest audit is saved to `latest_trace.json`. These files are created locally and are not part of the repo.

### Several brains

Each brain is saved in a `brains` folder as `brains/brain_<name>.json`, and at start-up you get a menu: pick a brain by number, or `N` for a new one. A new brain starts as `brain_new-<date-time>.json` and is renamed to its own name automatically once it has one. You can skip the menu:

```bash
python ltcmbridge.py --brain gyre     # open brains/brain_gyre.json
python ltcmbridge.py --new            # start a new brain
```

An older single `brain_memory.json` next to the scripts shows up in the menu and can be moved into the `brains` folder (a backup copy is kept). While a brain is open, a `.lock` file marks it, so you're warned before opening the same brain in two windows, which would overwrite each other's saves. `/clear` now asks you to type `ERASE` first.

### Old brains (from before v21.7)

Brains that grew under older engines can be overfull: words sitting in dozens of cells, links that never fade. Newer
engines heal them by themselves, a little every sleep, but slowly (roughly 50-60 sleeps). To clean one up at once, run
`catchup_cells.py` from the main folder, next to `torrentengine.py` and the GloVe file:

```bash
python catchup_cells.py brains/brain_gyre.json brains/brain_gyre_cleaned.json
```

It writes a cleaned copy and never changes the original. Each word keeps its 10 strongest cells, each cell keeps its 6
most-used words (`--keep`), and no count stays above 8 (`--max-count`); then the crystals are rebuilt. Links, word
weights, memories, dreams and names are left alone. It prints before-and-after numbers so you can compare. Pick the
cleaned copy in the start-up menu once you're happy with it.

### Word file

The repo includes `torrent_wordspace_50k.gz` (since v22.7.1): 50,000 GloVe word vectors, already processed the way the
engine needs them. It is the word space every version since v22 was developed and tested with. Keep it next to
`torrentengine.py` and nothing else is needed. (GloVe: Stanford NLP, Public Domain Dedication and License v1.0.)
Without it, or a GloVe file, the engine falls back to a small built-in vocabulary of about 212 words and warns that it
is in test mode.

Optional alternatives, detected automatically when a file with "glove" in its name sits next to the scripts:

- **The raw GloVe file** (`glove.6B.50d.txt` from `glove.6B.zip` at [Stanford GloVe](https://nlp.stanford.edu/projects/glove/)):
  gives the same word space as the packaged file; the engine processes it at the first start and saves a cache. Only
  needed if you'd rather start from the original download.
- **A 2-D word map:** a text file with two numbers and a word on each line, such as a UMAP projection of GloVe. This is
  how the earliest versions were developed; it is fast and light, but current versions are tuned on the GloVe space.

Use a separate folder for each kind of word file, because a saved brain belongs to the word space it was learned in. Details are in section 2.3 of the disclosure.

Saves are crash-safe: the brain is written to a temporary file and swapped in. If a brain file ever can't be read at start-up, it is renamed to `<file>.unreadable-<timestamp>` instead of being overwritten, so you can recover it.

**Privacy:** brain files (the `brains` folder, or `brain_memory.json`) contain your conversation history. Don't upload it or share it.

### Configuration

Useful environment variables:

- `TORRENT_MODEL`, `TORRENT_HOST`: which local model and server to use.
- `TORRENT_VOICE_MODE`: how much the engine learns from the LLM's replies: `SOVEREIGN` (nothing), `ATTENUATED` (a little), `FULL` (default).
- Optional speech: `TORRENT_WHISPER_MODEL` and `TORRENT_PIPER_MODEL`. Speech input needs `pip install faster-whisper sounddevice numpy`; speech output uses Piper, `pyttsx3`, or your system's built-in voice. Commands: `/tts`, `/listen`, `/voicechat`.

Handy in-chat commands: `/crystals`, `/ponder`, `/sleep`, `/dream`, `/audit`, `/grid`, `/flip`, `/export`, `/emotions`, `/telemetry`, `/wheels` (switch between the plain and the detailed LLM prompt), `/nightmare` (see below), `/levels`, `/idle`, `/live`, `/speak`, `/rhythm`, `/face`, `/read`, `/whoami`, `/people`, `/facts`, `/note`, `/back` (undo your last message), `/prompt` (see what the LLM was sent). The bridge lists them all at start-up.

More environment variables for the newer features: `TORRENT_HOSTS` (a comma list of LLM servers to try; the last one
that worked is remembered in `torrent_hosts.json`), `TORRENT_FACE_PORT` / `TORRENT_FACE_HOST` / `TORRENT_FACE_PASSWORD`
(the face page), `TORRENT_LIVE_TICK` (seconds between live idle ticks, default 20), `TORRENT_NOTIFY=1` (phone
notification for speak-ups on Termux, needs the Termux:API app).

### Levels, idle time and real time

Since v23.0 a brain has four levels, shown on the bridge's status line as `⚡0.42 ☯-0.30 ✨0.55 💤0.12`: arousal (how
wound up it is), valence (mood, measured against its own usual), novelty and sleep pressure. They change with each
message and with clock time. The names are vocabulary for this engine only, not medical or neuroscience claims.

These are **experimental and off unless you turn them on** (each is saved per brain):

- **Idle time** (`/idle`): a silence is spent on the brain's own material. It chooses, one decision at a time, between
  wandering along its links, leaping to a word it resembles, thinking back to a recent moment, dozing and sleeping.
  What it learns while idle is tagged "idle" and kept faint. `/idle why` shows each choice and its reasons.
- **Live idle** (`/live on`): the same choices made while the silence happens, on a background clock, instead of all at
  once when the next message arrives.
- **Speaking up** (`/speak on`, needs live idle): the brain can send you a message first when something builds up to
  say. The brain decides what it is about; the LLM only words it. It waits at least 20 minutes after your last message,
  never speaks while asleep, and speaks less when its messages go unanswered.
- **Face page** (`/face`): a small local web page that draws the levels as a face, with a chat box. It is a visualizer
  of the numbers, not a claim about feelings. Chat from the page only works on the same device unless
  `TORRENT_FACE_PASSWORD` is set.
- **Daily rhythm** (`/rhythm on`): idle choices follow this computer's clock, so a brain left alone sleeps more easily
  at night and less in the afternoon. `/rhythm +3` shifts its night three hours later. It doesn't change how messages
  are learned.
- **Felt time**: each silence also records how long it seemed (eventful stretches seem longer looking back, bored ones
  drag while they pass, sleep seems short). It is only measured and told to the voice when asked, not used for anything.
- **Reading** (`/read mybook.txt`): the brain reads a text file as a book, 40 sentences a night with a sleep between.

When you ask the LLM voice how the brain is, what it thought about while alone, whether it slept, or what time it is,
the bridge gives it the brain's real record and tells it to say it doesn't know anything else.

### Nightmare mode

By default the engine leans up: frightening or negative words are kept out of the brain's name, its dream bridges, its recall and its spreading activation, and sleep softens links between strongly positive and strongly negative words. This is deliberate, so a brain can't spiral into fear. **Nightmare mode** turns those rules off, so a brain learns and dreams about frightening things the same way it learns anything else. It is off by default. Type `/nightmare` to turn it on or off; the choice is saved in that brain's file, and the status line shows `🌑 nightmare` while it is on. For test runs, `TORRENT_NIGHTMARE=1` (or `0`) sets it at start-up. In a short test, a brain given frightening lines and then calm ones went back to a positive name in normal mode, but kept a negative one ("Betrayed") in nightmare mode.

## Tested on

Everything here runs on a refurbished mini PC with no dedicated graphics card:

- **CPU:** Intel Core i5-8500T (6 cores, 2.1 GHz)
- **RAM:** 32 GB
- **Graphics:** integrated Intel UHD Graphics 630 (no GPU used)
- **OS:** Windows, 64-bit

The engine on its own (no LLM) answers in tens of milliseconds a turn. With the bridge, the local model runs through
Ollama on the CPU. Measured reply times: `gemma3:4b` about 10-35 seconds, `gemma3:12b` about 50-70 seconds (the first
reply of a session is slower because the model has to load). The 32 GB of RAM is what makes a 12B model usable here; with 16 GB, a 4B model is the safer choice.

## Why this is public

This project is published as a **defensive disclosure** so the ideas in it stay free for anyone to use and cannot later be patented by someone else. The description in `TORRENT_DISCLOSURE.md` (v21) and `TORRENT_DISCLOSURE_ADDENDUM_1.md` (v21.1 to v24.1.1) is written to be detailed enough to re-implement. Permanent archived copies are on Zenodo: [doi.org/10.5281/zenodo.24040746](https://doi.org/10.5281/zenodo.24040746) always points to the latest version, and the original first release (v21.0, the dated disclosure) is [doi.org/10.5281/zenodo.24040747](https://doi.org/10.5281/zenodo.24040747).

## Notes

- The code was written with LLMs under the author's direction. Claude (Anthropic; Claude Opus models) served as research
  partner: code, tests and lab notes. Gemini (Google), working under the author's long-running "Meridian" instructions,
  contributed design ideas (for example the face visualizer, curiosity about new words, and time labels on memories).
- Related work is listed in section 13 of the disclosure.
- Issues and forks are welcome.

## License

Apache-2.0. See `LICENSE`.
