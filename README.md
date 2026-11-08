# T.O.R.R.E.N.T.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24040746.svg)](https://doi.org/10.5281/zenodo.24040746)

**Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory**

An experimental "language-enabled toroidal crystalline manifold" (LTCM): a small, standard-library Python engine that keeps a persistent semantic state on a 7×7×7 wraparound lattice, learns word associations, consolidates them offline ("sleep" and "dreams"), and can feed its state to a local LLM.

> **Status: experimental research code.** There are no benchmarks. Nothing here has been shown to reduce hallucination or improve LLM accuracy. See the limitations section of the disclosure.

## What's in this repo

| File | Purpose |
|---|---|
| `torrentengine.py` | The engine (v21.3). Standard library only. |
| `brainpicker.py` | Lets you keep several brains (TCMs) and choose one at start-up. Required: keep it in the same folder. |
| `ltcmbridge.py` | The easiest way to start: loads the engine and, if a local LLM (Ollama or an OpenAI-compatible server) is reachable, uses it as a voice. Falls back to the engine's own replies otherwise. Optional local voice in/out. |
| `replay.py` | Runs the same list of sentences through one or two engine versions on a temporary copy of a brain and compares them turn by turn. Your real brain file is never changed. |
| `cleanwords.py` | Finds junk words in a brain file (glued words, typos, cut-off fragments made by older versions), lets you pick which to remove, and backs the file up first. |
| `TORRENT_DISCLOSURE.md` | Full technical description of how everything works, published as a defensive disclosure. |
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
- `TORRENT_LLM_TIMEOUT`: how many seconds to wait for the model to *start* answering, including loading it (default 240). Replies are streamed, so a long reply can't time out while it is being written. Raise this on a slow computer if the first reply after starting times out.
- `TORRENT_KEEP_ALIVE`: how long Ollama keeps the model loaded between turns (default `30m`), so it isn't reloaded after a pause.
- `/model <name>` switches the model and is remembered for that brain; `/connect` reconnects after the LLM server was restarted (the bridge also reconnects by itself).
- Optional speech: `TORRENT_WHISPER_MODEL` and `TORRENT_PIPER_MODEL`. Speech input needs `pip install faster-whisper sounddevice numpy`; speech output uses Piper, `pyttsx3`, or your system's built-in voice. Commands: `/tts`, `/listen`, `/voicechat`.

Handy in-chat commands: `/crystals`, `/ponder`, `/sleep`, `/dream`, `/audit`, `/grid`, `/flip`, `/export`, `/emotions`, `/telemetry`, `/wheels` (switch between the plain and the detailed LLM prompt).

## Changes since v21.0

- **v21.1:** learned negative feelings are kept when a brain is loaded (they used to reset to +0.5); dreams can include negative words.
- **v21.2:** brain picker; the divergence ratio divides by 8, since steps 0 and 1 are always shared (it was capped at 88.9%); a GloVe start-up cache; the "X is Y" teaching trigger ignores vague subjects, names and sentences about I/you/we; answering "no" to the naming question leaves the brain unnamed.
- **v21.3:**
  - *Names vs words:* a name that is also an ordinary word (Hope, Drift) only counts as a name when it is used as one ("Hope, are you there?"); "I hope so" keeps the word *hope*.
  - *Filler words:* words like *together, talk, people, hello, goodbye, morning, night* now count as words instead of being thrown away.
  - *Wraparound damping:* each trajectory step moves 3/16 of a cell, so a turn moves about 1 to 3 cells in the direction of its push instead of lapping the 7-cell ring.
  - *Word splitting:* dashes, slashes, "..." and hyphens separate words instead of gluing them ("reflection—a" no longer becomes "reflectiona"); "good night" is read as the farewell *goodnight*.
  - *Bridge:* streamed replies, a model kept loaded between turns, no more getting stuck "disconnected", summaries cut at word boundaries.

The disclosure still describes v21.0 in detail (plus section 11b, below); these changes will be added to it.

## Brain-to-brain dialogue (described, not included)

The author also runs a separate bridge in which two LTCMs talk to each other through one local LLM: each brain's reply is voiced from its own state, and each brain takes in the other's reply as a normal turn, so both are changed by the conversation. That bridge is a personal side project and isn't in this repository, but the method is described in section 11b of the disclosure so the idea stays public.

## Why this is public

This project is published as a **defensive disclosure** so the ideas in it stay free for anyone to use and cannot later be patented by someone else. The description in `TORRENT_DISCLOSURE.md` is written to be detailed enough to re-implement. Permanent archived copies are on Zenodo: [doi.org/10.5281/zenodo.24040746](https://doi.org/10.5281/zenodo.24040746) always points to the latest version, and the original first release (v21.0, the dated disclosure) is [doi.org/10.5281/zenodo.24040747](https://doi.org/10.5281/zenodo.24040747).

## Notes

- Much of the code and design was developed with LLM assistance.
- Related work is listed in section 13 of the disclosure.
- Issues and forks are welcome.

### Considered for later: adding the dialogue bridge

The dialogue bridge stays out of the repo for now. Before it could be added:

- **Make it general:** remove the built-in persona and the personal names and defaults, and turn it into a `/dialogue` command in `ltcmbridge.py` that pairs any two brains from the `brains` folder.
- **Bring it up to the main bridge:** streaming, the reply length limit and the newer error handling.
- **Treat both brains equally:** the partner brain should write its own trace file and keep its own summary and episodes, and be marked as open (locked) while it is talking.
- **Decide about names:** should each brain learn the partner's name as a concept? Today neither does.
- **Run experiments first:** measure how much of the exchange is echo (the LLM agreeing with itself), compare against a control where one brain gets shuffled replies, and compare voice modes.
- **Cost:** each round is two LLM calls, which is slow on small computers.

## License

Apache-2.0. See `LICENSE`.
