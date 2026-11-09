# T.O.R.R.E.N.T.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24040746.svg)](https://doi.org/10.5281/zenodo.24040746)

**Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory**

An experimental "language-enabled toroidal crystalline manifold" (LTCM): a small, standard-library Python engine that keeps a persistent semantic state on a 7×7×7 wraparound lattice, learns word associations, consolidates them offline ("sleep" and "dreams"), and can feed its state to a local LLM.

> **Status: experimental research code.** There are no benchmarks. Nothing here has been shown to reduce hallucination or improve LLM accuracy. See the limitations section of the disclosure.

## What's in this repo

| File | Purpose |
|---|---|
| `torrentengine.py` | The engine (v22.3). Standard library only. |
| `brainpicker.py` | Lets you keep several brains (TCMs) and choose one at start-up. Keep it in the same folder. |
| `ltcmbridge.py` | The easiest way to start: loads the engine and, if a local LLM (Ollama or an OpenAI-compatible server) is reachable, uses it as a voice. Falls back to the engine's own replies otherwise. Optional local voice in/out. |
| `catchup_cells.py` | Optional one-time cleanup for a brain that grew overfull under an engine older than v21.7. Works on a copy. |
| `TORRENT_DISCLOSURE.md` | Full technical description of how everything works, published as a defensive disclosure. |
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

### Word file (optional)

The engine works with no extra files, using a small built-in vocabulary of about 212 words. For a much larger vocabulary, put a word file with "glove" in its name next to the scripts; it is detected automatically:

- **Real GloVe (recommended to try):** download `glove.6B.zip` from [Stanford GloVe](https://nlp.stanford.edu/projects/glove/) and take `glove.6B.50d.txt` out of it. Its vectors are public domain. At start-up the engine removes the shared direction that makes GloVe words look alike and calibrates its emotion, social and depth axes from built-in seed words. This mode is new: the engine's other thresholds were tuned on the smaller 2-D map below, so it may behave differently while it gets retuned.
- **A 2-D word map:** a text file with two numbers and a word on each line, such as a UMAP projection of GloVe. This is how the engine was developed. It's fast and light, which helps on phones.

Use a separate folder for each kind of word file, because a saved brain belongs to the word space it was learned in. Details are in section 2.3 of the disclosure.

Saves are crash-safe: the brain is written to a temporary file and swapped in. If a brain file ever can't be read at start-up, it is renamed to `<file>.unreadable-<timestamp>` instead of being overwritten, so you can recover it.

**Privacy:** brain files (the `brains` folder, or `brain_memory.json`) contain your conversation history. Don't upload it or share it.

### Configuration

Useful environment variables:

- `TORRENT_MODEL`, `TORRENT_HOST`: which local model and server to use.
- `TORRENT_VOICE_MODE`: how much the engine learns from the LLM's replies: `SOVEREIGN` (nothing), `ATTENUATED` (a little), `FULL` (default).
- Optional speech: `TORRENT_WHISPER_MODEL` and `TORRENT_PIPER_MODEL`. Speech input needs `pip install faster-whisper sounddevice numpy`; speech output uses Piper, `pyttsx3`, or your system's built-in voice. Commands: `/tts`, `/listen`, `/voicechat`.

Handy in-chat commands: `/crystals`, `/ponder`, `/sleep`, `/dream`, `/audit`, `/grid`, `/flip`, `/export`, `/emotions`, `/telemetry`, `/wheels` (switch between the plain and the detailed LLM prompt), `/nightmare` (see below).

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

This project is published as a **defensive disclosure** so the ideas in it stay free for anyone to use and cannot later be patented by someone else. The description in `TORRENT_DISCLOSURE.md` is written to be detailed enough to re-implement. Permanent archived copies are on Zenodo: [doi.org/10.5281/zenodo.24040746](https://doi.org/10.5281/zenodo.24040746) always points to the latest version, and the original first release (v21.0, the dated disclosure) is [doi.org/10.5281/zenodo.24040747](https://doi.org/10.5281/zenodo.24040747).

## Notes

- Much of the code and design was developed with LLM assistance.
- Related work is listed in section 13 of the disclosure.
- Issues and forks are welcome.

## License

Apache-2.0. See `LICENSE`.
