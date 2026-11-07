# T.O.R.R.E.N.T.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24040746.svg)](https://doi.org/10.5281/zenodo.24040746)

**Toroidal Operational Recursive Reasoning Epistemic Network & Trajectory**

An experimental "language-enabled toroidal crystalline manifold" (LTCM): a small, standard-library Python engine that keeps a persistent semantic state on a 7×7×7 wraparound lattice, learns word associations, consolidates them offline ("sleep" and "dreams"), and can feed its state to a local LLM.

> **Status: experimental research code.** There are no benchmarks. Nothing here has been shown to reduce hallucination or improve LLM accuracy. See the limitations section of the disclosure.

## What's in this repo

| File | Purpose |
|---|---|
| `torrentengine.py` | The engine (v21.0). Standard library only. |
| `ltcmbridge.py` | The easiest way to start: loads the engine and, if a local LLM (Ollama or an OpenAI-compatible server) is reachable, uses it as a voice. Falls back to the engine's own replies otherwise. Optional local voice in/out. |
| `TORRENT_DISCLOSURE.md` | Full technical description of how everything works, published as a defensive disclosure. |
| `LICENSE` | Apache-2.0. |

## Quick start

Keep both `.py` files in the same folder and run the bridge. It loads the engine automatically, so this one command is all you need:

```bash
python ltcmbridge.py
```

- **With a local LLM running** (Ollama or an OpenAI-compatible server), the engine's state is injected into the model's prompt and the model's reply is used.
- **Without one**, the bridge reports the LLM as unreachable and falls back to the engine's own native replies, so you can still talk to T.O.R.R.E.N.T. directly.

You can also run the engine alone, with no bridge code at all:

```bash
python torrentengine.py
```

On first run it asks for a name to anchor the space. Type `/exit` to quit cleanly; this runs the sleep and dream cycle and saves state. State is saved to `brain_memory.json` and the latest audit to `latest_trace.json` in the working directory. These files are created locally and are not part of the repo.

### Word file (optional)

The engine works with no extra files, using a small built-in vocabulary of about 212 words. For a much larger vocabulary, put a word file with "glove" in its name next to the scripts; it is detected automatically:

- **Real GloVe (recommended to try):** download `glove.6B.zip` from [Stanford GloVe](https://nlp.stanford.edu/projects/glove/) and take `glove.6B.50d.txt` out of it. Its vectors are public domain. At start-up the engine removes the shared direction that makes GloVe words look alike and calibrates its emotion, social and depth axes from built-in seed words. This mode is new: the engine's other thresholds were tuned on the smaller 2-D map below, so it may behave differently while it gets retuned.
- **A 2-D word map:** a text file with two numbers and a word on each line, such as a UMAP projection of GloVe. This is how the engine was developed. It's fast and light, which helps on phones.

Use a separate folder for each kind of word file, because a saved brain belongs to the word space it was learned in. Details are in section 2.3 of the disclosure.

Saves are crash-safe: the brain is written to a temporary file and swapped in. If `brain_memory.json` ever can't be read at start-up, it is renamed to `brain_memory.json.unreadable-<timestamp>` instead of being overwritten, so you can recover it.

**Privacy:** `brain_memory.json` contains your conversation history. Don't upload it or share it.

### Configuration

Useful environment variables:

- `TORRENT_MODEL`, `TORRENT_HOST`: which local model and server to use.
- `TORRENT_VOICE_MODE`: how much the engine learns from the LLM's replies: `SOVEREIGN` (nothing), `ATTENUATED` (a little), `FULL` (default).
- Optional speech: `TORRENT_WHISPER_MODEL` and `TORRENT_PIPER_MODEL`. Speech input needs `pip install faster-whisper sounddevice numpy`; speech output uses Piper, `pyttsx3`, or your system's built-in voice. Commands: `/tts`, `/listen`, `/voicechat`.

Handy in-chat commands: `/crystals`, `/ponder`, `/sleep`, `/dream`, `/audit`, `/grid`, `/flip`, `/export`, `/emotions`, `/telemetry`, `/wheels` (switch between the plain and the detailed LLM prompt).

## Why this is public

This project is published as a **defensive disclosure** so the ideas in it stay free for anyone to use and cannot later be patented by someone else. The description in `TORRENT_DISCLOSURE.md` is written to be detailed enough to re-implement. Permanent archived copies are on Zenodo: [doi.org/10.5281/zenodo.24040746](https://doi.org/10.5281/zenodo.24040746) always points to the latest version, and the original first release (v21.0, the dated disclosure) is [doi.org/10.5281/zenodo.24040747](https://doi.org/10.5281/zenodo.24040747).

## Notes

- Much of the code and design was developed with LLM assistance.
- Related work is listed in section 13 of the disclosure.
- Issues and forks are welcome.

## License

Apache-2.0. See `LICENSE`.
