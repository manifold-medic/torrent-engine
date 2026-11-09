import copy, json, os, random, re, shutil, socket, subprocess, sys, tempfile, time, urllib.request, urllib.error, wave
from torrentengine import ToroidalBrainEngine, BRAIN_LIBRARY

# Speed / connection settings (can be changed with environment variables, e.g. set TORRENT_LLM_TIMEOUT=400):
LLM_TIMEOUT_SEC = float(os.environ.get("TORRENT_LLM_TIMEOUT", "240"))  # longest wait for the model to START answering (includes loading it)
LLM_KEEP_ALIVE = os.environ.get("TORRENT_KEEP_ALIVE", "30m")
LLM_SEED = os.environ.get("TORRENT_SEED", "").strip()  # a number makes the model's randomness repeatable (for tests)           # Ollama keeps the model in memory this long between turns


def cut_at_word(text, limit, keep="start"):
    """Shorten text to at most `limit` characters without cutting a word in half.
    keep="start" keeps the beginning; keep="end" keeps the end (the newest part of a growing summary).
    Fixes fragments like "ndational" (from "foundational") that the model could copy into its reply,
    after which the other brain learned them as new words."""
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    if keep == "end":
        tail = text[-limit:]
        if text[-limit - 1] != " ":
            sp = tail.find(" ")
            tail = tail[sp + 1:] if 0 <= sp < limit // 2 else tail
        return tail
    head = text[:limit + 1]
    sp = head.rfind(" ")
    return (head[:sp] if sp > limit // 2 else text[:limit]).rstrip()


def detect_mobile_platform() -> bool:
    if "--pc" in sys.argv:
        return False
    if "--mobile" in sys.argv:
        return True
    android_keys = ("ANDROID_ROOT", "ANDROID_DATA", "PYDROID_RPC", "TERMUX_VERSION")
    if any(k in os.environ for k in android_keys):
        return True
    return "com.termux" in os.environ.get("PREFIX", "") or os.path.exists("/system/build.prop")


def parse_voice_mode(default_mode: str = None) -> str:
    raw = os.environ.get("TORRENT_VOICE_MODE", "")
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--voice-mode="):
            raw = arg.split("=", 1)[1]
        elif arg == "--voice-mode" and i + 1 < len(sys.argv):
            raw = sys.argv[i + 1]
    c = raw.strip().upper()
    if c in ("SOVEREIGN", "SOV", "READONLY", "READ_ONLY", "GEO"):
        return "SOVEREIGN"
    if c in ("ATTENUATED", "ATT", "LOW", "GYRE"):
        return "ATTENUATED"
    if c in ("FULL", "FULL_PLASTICITY", "PLASTIC", "HOPE"):
        return "FULL_PLASTICITY"
    return default_mode or ""


def strip_performative_directions(text: str) -> str:
    """
    Removes parenthetical stage directions like '(A subtle contraction...)'
    or '*shifts coordinates*' when running in Wheels-Off mode.
    """
    cleaned = re.sub(r"^\s*\([^)]{4,140}\)\s*", "", text)
    cleaned = re.sub(r"^\s*\*[^*]{4,140}\*\s*", "", cleaned)
    cleaned = re.sub(r"\s*\((?:[^)]*(?:manifold|torus|coordinate|contraction|shift|axis|lattice)[^)]*)\)", "", cleaned, flags=re.IGNORECASE)
    # a whole line that is nothing but a parenthetical, e.g. "(A slight adjustment of processing priority ...)"
    cleaned = re.sub(r"(?m)^[ \t]*(?:\([^\n()]{4,200}\)|\*[^\n*]{4,200}\*)[ \t]*$\n?", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip() or text.strip()


class LocalVoiceEngine:
    """
    Zero-Cloud Offline Voice I/O:
      • STT (Input) : Uses 'faster-whisper' + 'sounddevice' on PC, or 'termux-speech-to-text' on Android.
      • TTS (Output): Tries 'piper' CLI (.onnx), then 'pyttsx3', then OS-native offline speech
                      (Windows PowerShell SAPI, macOS 'say', Android 'termux-tts-speak', Linux 'espeak-ng').
    """

    def __init__(self, is_mobile: bool = False):
        self.is_mobile = is_mobile
        self.tts_enabled = False
        self.whisper_model = None
        self.whisper_size = os.environ.get("TORRENT_WHISPER_MODEL", "base.en")
        self.piper_model_path = os.environ.get("TORRENT_PIPER_MODEL", "")
        self.pyttsx_engine = None

    def speak(self, text: str):
        if not self.tts_enabled or not text:
            return
        clean_speech = re.sub(r"[*_`#~>\[\]]", "", text).strip()
        if not clean_speech:
            return

        # 1. Try Piper-TTS if a .onnx voice model path is configured and 'piper' binary exists
        if self.piper_model_path and os.path.isfile(self.piper_model_path) and shutil.which("piper"):
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    wav_path = tf.name
                proc = subprocess.run(
                    ["piper", "--model", self.piper_model_path, "--output_file", wav_path],
                    input=clean_speech.encode("utf-8"),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30
                )
                if proc.returncode == 0 and os.path.exists(wav_path):
                    self._play_wav(wav_path)
                    os.remove(wav_path)
                    return
            except Exception:
                pass

        # 2. Try pyttsx3 if installed
        try:
            import pyttsx3
            if self.pyttsx_engine is None:
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty("rate", 175)
            self.pyttsx_engine.say(clean_speech)
            self.pyttsx_engine.runAndWait()
            return
        except Exception:
            pass

        # 3. Zero-Dependency OS Native Offline TTS Fallbacks
        try:
            if os.name == "nt":
                safe_t = clean_speech.replace("'", "''").replace('"', " ")
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_t}')"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform == "darwin":
                subprocess.run(["say", clean_speech])
            elif shutil.which("termux-tts-speak"):
                subprocess.run(["termux-tts-speak", clean_speech])
            elif shutil.which("espeak-ng"):
                subprocess.run(["espeak-ng", clean_speech])
            elif shutil.which("espeak"):
                subprocess.run(["espeak", clean_speech])
        except Exception as e:
            print(f"  [!] TTS playback error: {e}")

    def _play_wav(self, wav_path: str):
        if os.name == "nt":
            import winsound
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", wav_path])
        elif shutil.which("aplay"):
            subprocess.run(["aplay", "-q", wav_path])

    def listen_and_transcribe(self, duration_sec: int = 5) -> str:
        # 1. Android Termux API fallback if available
        if self.is_mobile and shutil.which("termux-speech-to-text"):
            try:
                print(f"🎙️ Listening via Android Speech-to-Text...")
                res = subprocess.check_output(["termux-speech-to-text"], timeout=20)
                return res.decode("utf-8", errors="ignore").strip()
            except Exception as e:
                print(f"  [!] Termux STT error: {e}")
                return ""

        # 2. Offline faster-whisper + sounddevice on PC/Laptop
        try:
            import sounddevice as sd
            import numpy as np
        except ImportError:
            print("\n[!] Missing audio capture packages. Install via:")
            print("    pip install faster-whisper sounddevice numpy")
            return ""

        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print("\n[!] Missing 'faster-whisper'. Install via:")
            print("    pip install faster-whisper")
            return ""

        if self.whisper_model is None:
            print(f"⏳ Loading offline faster-whisper model ('{self.whisper_size}')...")
            self.whisper_model = WhisperModel(self.whisper_size, device="cpu", compute_type="int8")

        samplerate = 16000
        print(f"🎙️ Recording microphone for {duration_sec} seconds... Speak now!")
        audio_data = sd.rec(int(duration_sec * samplerate), samplerate=samplerate, channels=1, dtype="int16")
        sd.wait()
        print("⚡ Transcribing audio locally...")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            wav_path = tf.name
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())

        try:
            segments, _ = self.whisper_model.transcribe(wav_path, beam_size=3)
            transcript = " ".join(seg.text.strip() for seg in segments).strip()
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

        return transcript


class TorrentLLMMiddleware:
    def __init__(self, brain: ToroidalBrainEngine, is_mobile: bool = False, model_name: str = None, host: str = None, voice_mode: str = None):
        self.brain = brain
        self.is_mobile = is_mobile
        self.voice_mode = self.resolve_voice_mode(voice_mode)
        self.temperature = 0.65
        self.max_tokens = int(os.environ.get("TORRENT_MAX_TOKENS", "160" if is_mobile else "600"))  # longest reply, in tokens
        self.summary_trigger_len = 6 if is_mobile else 10
        self.keep_raw_len = 2 if is_mobile else 4

        # Start in Absolute Wheels-Off Mode by default
        self.brain.training_wheels = False

        self.chat_history = []
        self.running_summary = ""
        self.episodic_archive = []
        self.last_retrieved_episodes = []
        self.last_post_audit = {}
        self.available_models = []
        self.last_error = ""

        self.load_persistent_chat_memory()

        if is_mobile:
            self.backend = "openai"
            self.base_url = host or "http://127.0.0.1:12434"
            self.endpoint = f"{self.base_url}/v1/chat/completions"
            self.model_name = model_name or "gemma-2-2b-it-Q4_K_M"
            cands = [host] if host else ["http://127.0.0.1:12434", "http://127.0.0.1:8080", "http://127.0.0.1:11434"]
        else:
            self.backend = "ollama"
            self.base_url = host or "http://127.0.0.1:11434"
            self.endpoint = f"{self.base_url}/api/chat"
            self.model_name = model_name or "gemma2"
            cands = [host] if host else ["http://127.0.0.1:11434", "http://127.0.0.1:1234", "http://127.0.0.1:8080", "http://127.0.0.1:12434"]

        # A model chosen with TORRENT_MODEL or /model wins over whatever Ollama has loaded and over the "gemma" default
        self.preferred_model = model_name or str(self.brain.knowledge_facts.get("_preferred_model", "")).strip()
        self.force_merged_role = False  # set if the server rejects a separate system message (400/422)
        # Callosum (2026-11-08): the brain talks to the voice through more than prompt text. Both parts can be switched off
        # with /callosum for the control test. "memory": strength labels on memory lines + careful learning from replies.
        # "tone": the brain's movement sets the model's temperature and a target reply length.
        self.callosum = {"memory": True, "tone": True}
        self.memory_strength, self.turn_tone, self.last_tone = 0.0, None, None
        self.last_prompt_text, self.last_finish_reason, self.last_ground_text = "", "", ""
        self.pinned_notes, self.last_used_notes = [], []      # notes chosen with /recall for the next turn; notes used last turn
        self.undo_snapshot, self.undo_ready = None, False      # /back
        self.connected = False
        self.last_used_fallback = False
        self._warned_unreachable = False
        for cand in cands:
            if cand and self.probe_and_connect(cand, verbose=False):
                self.connected = True
                break

    # =========================================================================
    # NOTES FILE: things the user has confirmed, kept next to the brain file
    # (brains/brain_gyre.json -> brains/brain_gyre.notes.md). Only the user writes notes, never the LLM, so a
    # model's wrong guess can't become one. The file is plain text and can be edited in Notepad; it is re-read
    # every turn. Matching notes are added to the prompt automatically (at most NOTES_PER_TURN) and outrank
    # everything else the model is shown.
    # =========================================================================
    NOTES_PER_TURN = 2

    def notes_path(self) -> str:
        base, _ = os.path.splitext(self.brain.memory_file)
        return base + ".notes.md"

    def load_notes(self) -> list:
        """Each note: {'key': 'TCM' or '', 'text': ..., 'meta': ..., 'line': raw}. Lines that aren't '- ' items are kept as-is."""
        notes = []
        path = self.notes_path()
        if not os.path.exists(path):
            return notes
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line.startswith(("- ", "* ")):
                    continue
                body = line[2:].strip()
                meta = ""
                m = re.search(r"\s*\[([^\[\]]*)\]\s*$", body)
                if m:
                    meta, body = m.group(1), body[:m.start()].rstrip()
                key, text = "", body
                if ":" in body:
                    k, t = body.split(":", 1)
                    if 0 < len(k.strip()) <= 40 and t.strip():
                        key, text = k.strip().strip("*").strip(), t.strip()
                notes.append({"key": key, "text": text, "meta": meta, "line": line})
        return notes

    def write_notes(self, notes: list):
        path = self.notes_path()
        bot = self.brain.user_profile.get("bot_name") or "this brain"
        user = (self.brain.user_profile.get("user_name") or "the user").capitalize()
        header = (f"# Notes for {bot}\n\n"
                  f"Things {user} has confirmed. One note per line, starting with '- '.\n"
                  f"Use 'Key: text' so the note comes up automatically when the key is mentioned.\n"
                  f"You can edit this file in any text editor; the bridge re-reads it every turn.\n\n")
        lines = []
        for n in notes:
            body = f"{n['key']}: {n['text']}" if n["key"] else n["text"]
            lines.append(f"- {body}" + (f"  [{n['meta']}]" if n["meta"] else ""))
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(lines) + ("\n" if lines else ""))
        os.replace(tmp, path)

    def add_note(self, raw: str) -> dict:
        key, text = "", raw.strip()
        if ":" in text:
            k, t = text.split(":", 1)
            if 0 < len(k.strip()) <= 40 and t.strip():
                key, text = k.strip(), t.strip()
        meta = f"cell {self.brain.seed_s},{self.brain.seed_a},{self.brain.seed_z} · {time.strftime('%Y-%m-%d')}"
        notes = [n for n in self.load_notes() if not (key and n["key"].lower() == key.lower())]  # same key = replace
        note = {"key": key, "text": text, "meta": meta, "line": ""}
        notes.append(note)
        self.write_notes(notes)
        # Teach the brain too: a one-word key becomes a definition fact and is wired to the note's words
        if key and re.fullmatch(r"[A-Za-z][A-Za-z0-9\-]{1,30}", key):
            definition = re.split(r"[,;.(]", text, maxsplit=1)[0].strip()[:60]  # the brain gets just the definition; the note keeps the rest
            if definition:
                self.brain.learn_definitions(f"'{key}' means '{definition}'.")
        return note

    def note_words(self, note: dict) -> set:
        return {w for w in self.brain.clean_tokens(note["key"] or note["text"]) if w not in self.brain.stop_words}

    @staticmethod
    def with_singulars(tokens) -> set:
        """The words plus simple singulars ("tcms" -> "tcm", "boxes" -> "box"), so a note or fact keyed "TCM" is found."""
        out = set(tokens)
        for t in tokens:
            if len(t) >= 4 and t.endswith("es"):
                out.add(t[:-2])
            if len(t) >= 4 and t.endswith("s") and not t.endswith("ss"):
                out.add(t[:-1])
        return out

    def match_notes(self, user_text: str, notes: list) -> list:
        """A keyed note matches when all its key words are in the message; a note without a key needs 2 of its words."""
        tokens = self.with_singulars(self.brain.clean_tokens(user_text))
        hits = []
        for n in notes:
            words = self.note_words(n)
            if not words:
                continue
            if n["key"]:
                if words <= tokens:
                    hits.append(n)
            elif len({w for w in words if len(w) >= 3} & tokens) >= 2:
                hits.append(n)
        return hits

    def notes_for_prompt(self, user_text: str) -> list:
        notes = self.load_notes()
        chosen = list(self.pinned_notes)  # notes picked with /recall always go, on top of the automatic ones
        seen = {(c["key"], c["text"]) for c in chosen}
        added = 0
        for n in self.match_notes(user_text, notes):
            if added >= self.NOTES_PER_TURN:
                break
            if (n["key"], n["text"]) not in seen:
                chosen.append(n)
                seen.add((n["key"], n["text"]))
                added += 1
        self.pinned_notes = []
        self.last_used_notes = chosen
        return chosen

    # =========================================================================
    # /back: one-step undo. Before every turn the brain and this bridge's memory are snapshotted in RAM;
    # /back restores them, as if the last message was never sent, and logs the undo in the brain file.
    # =========================================================================
    STATIC_BRAIN_ATTRS = {"raw_glove", "word_rank"}         # never change after loading: shared, not copied
    SHALLOW_BRAIN_ATTRS = {"vectors", "factory_vectors"}    # entries are replaced, never edited in place

    def take_snapshot(self, user_text: str):
        state = {}
        for k, v in self.brain.__dict__.items():
            if k in self.STATIC_BRAIN_ATTRS:
                continue
            state[k] = dict(v) if k in self.SHALLOW_BRAIN_ATTRS else copy.deepcopy(v)
        self.undo_snapshot = {
            "brain": state,
            "random": random.getstate(),
            "chat_history": copy.deepcopy(self.chat_history),
            "episodic_archive": copy.deepcopy(self.episodic_archive),
            "running_summary": self.running_summary,
            "text": user_text,
        }
        self.undo_ready = False  # becomes True once the turn has finished

    def undo_last_turn(self) -> str:
        snap = self.undo_snapshot
        if not snap or not self.undo_ready:
            return ""
        self.brain.__dict__.update(snap["brain"])
        random.setstate(snap["random"])
        self.chat_history = snap["chat_history"]
        self.episodic_archive = snap["episodic_archive"]
        self.running_summary = snap["running_summary"]
        log = []
        try:
            log = json.loads(self.brain.knowledge_facts.get("_undo_log_json", "[]"))
        except ValueError:
            pass
        log.append({"time": time.strftime("%Y-%m-%d %H:%M"), "undone": cut_at_word(snap["text"], 80)})
        self.brain.knowledge_facts["_undo_log_json"] = json.dumps(log[-50:])
        self.save_persistent_chat_memory()
        self.brain.save_memory()
        if self.brain.last_audit is not None:
            self.brain.export_trace_file("latest_trace.json")
        self.undo_snapshot, self.undo_ready = None, False
        return snap["text"]

    def load_persistent_chat_memory(self):
        self.running_summary = str(self.brain.knowledge_facts.get("_running_summary", "")).strip()
        raw_hist = self.brain.knowledge_facts.get("_recent_chat_json", "[]")
        try:
            lh = json.loads(raw_hist) if isinstance(raw_hist, str) else raw_hist
            if isinstance(lh, list):
                self.chat_history = [m for m in lh if isinstance(m, dict) and "role" in m and "content" in m][-self.summary_trigger_len:]
        except Exception:
            self.chat_history = []

        raw_ep = self.brain.knowledge_facts.get("_episodic_archive_json", "[]")
        try:
            lep = json.loads(raw_ep) if isinstance(raw_ep, str) else raw_ep
            if isinstance(lep, list):
                self.episodic_archive = [e for e in lep if isinstance(e, dict)][-60:]
        except Exception:
            self.episodic_archive = []

    def save_persistent_chat_memory(self):
        self.brain.knowledge_facts["_running_summary"] = self.running_summary
        self.brain.knowledge_facts["_recent_chat_json"] = json.dumps(self.chat_history[-self.summary_trigger_len:])
        self.brain.knowledge_facts["_episodic_archive_json"] = json.dumps(self.episodic_archive[-60:])

    def record_turn_and_maybe_summarize(self, user_text: str, llm_reply: str, audit: dict, salient_concepts: list):
        active_traj = audit["flippedTrajectory"] if self.brain.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s, a, z = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        cell_key = f"{s},{a},{z}"
        mood = self.brain.get_cell_emotion_name(s, a, z)
        ponder_prop = self.brain.last_thought_trace.get("pondering", {}).get("pondered_proposition", "")

        if salient_concepts:
            su = cut_at_word(user_text, 90)
            sb = cut_at_word(llm_reply, 110)
            self.episodic_archive.append({
                "timestamp": round(time.time(), 1),
                "cell": cell_key,
                "mood": mood,
                "concepts": salient_concepts[:5],
                "proposition": ponder_prop,
                "summary": f"At ({cell_key}), discussed {', '.join(salient_concepts[:3])}: User said '{su}' -> '{sb}'"
            })
            self.episodic_archive = self.episodic_archive[-60:]

        self.chat_history.append({"role": "user", "content": user_text})
        self.chat_history.append({"role": "assistant", "content": llm_reply})

        if len(self.chat_history) >= self.summary_trigger_len:
            cutoff = len(self.chat_history) - self.keep_raw_len
            older_slice = self.chat_history[:cutoff]
            self.chat_history = self.chat_history[cutoff:]
            self.running_summary = self.compress_turns_into_summary(older_slice)

        self.save_persistent_chat_memory()
        self.brain.save_memory()

    def compress_turns_into_summary(self, older_messages: list) -> str:
        lines = [f"{'User' if m['role'] == 'user' else 'AI'}: {cut_at_word(m['content'], 160)}" for m in older_messages]
        prev = f"Previous Summary: {self.running_summary}\n" if self.running_summary else ""
        sum_prompt = (
            f"{prev}Recent Dialogue:\n" + "\n".join(lines) + "\n\n"
            "Write a concise 2-sentence running summary combining the Previous Summary and Recent Dialogue."
        )
        if self.connected:
            try:
                compressed = self.stream_chat([{"role": "user", "content": sum_prompt}], max_tokens=120, temperature=0.3)
                if compressed:
                    short = cut_at_word(compressed, 420)
                    # end on a full sentence, not mid-thought ("...computational attempts to")
                    return self.trim_to_sentence(short) if short != " ".join(compressed.split()) else short
            except Exception:
                pass

        combined_text = " ".join(m["content"] for m in older_messages)
        tokens = self.brain.clean_tokens(combined_text)
        concepts, _ = self.brain.extract_concepts(combined_text, tokens)
        top_c = ", ".join(concepts[:5]) if concepts else "general reflection"
        recent_props = [p["summary"] for p in self.brain.idea_memory[-2:] if p.get("origin") == "waking"]
        prop_str = f" Key insight: {'; '.join(recent_props)}." if recent_props else ""
        new_note = f"Explored {top_c}.{prop_str}"
        return cut_at_word(f"{self.running_summary} Then: {new_note}", 420, keep="end") if self.running_summary else new_note

    def retrieve_relevant_episodes(self, user_text: str, salient_concepts: list, top_k: int = 3) -> list:
        query_vec = self.brain.phrase_to_vector(user_text)
        seed_set = set(salient_concepts[:5])
        fact_seeds = self.with_singulars(seed_set)  # "tcms" also finds the fact for "tcm"

        hop1_weights = {}
        for c in seed_set:
            for nb, wt in self.brain.assoc_graph.get(c, {}).items():
                if wt >= 0.45 and nb not in seed_set:
                    hop1_weights[nb] = max(hop1_weights.get(nb, 0.0), float(wt))

        candidates, seen = [], set()
        label = self.callosum["memory"]
        strength_of = {}  # text -> strength (4 certain note, 3 strong fact, 2 firm/familiar, 1 faint, 0.5 dream)

        noted = {w for n in self.last_used_notes for w in self.note_words(n)}
        for k, v in self.brain.knowledge_facts.items():
            if k.startswith("_") or k in noted:
                continue
            # Facts come from what the user taught (never from the LLM), so a matching fact outranks old episodes,
            # which can hold a model's wrong guess (e.g. an earlier model's made-up meaning of an acronym)
            teacher = str(self.brain.user_profile.get("user_name", "")).strip().capitalize() or "the user"
            fact_str = f"Fact taught by {teacher}{' (strong)' if label else ''}: '{k}' means {v}"
            strength_of[fact_str] = 3.0
            score = (6.0 if k in fact_seeds else (0.9 * min(1.5, hop1_weights[k]) if k in hop1_weights else 0.0))
            score += max(0.0, self.brain.cosine_similarity(query_vec, self.brain.phrase_to_vector(f"{k} {v}"))) * 1.1
            if score >= 0.55 and fact_str not in seen:
                seen.add(fact_str)
                candidates.append((score, fact_str))

        for p in self.brain.idea_memory:
            subj, obj, summary = p.get("subj", ""), p.get("obj", ""), p.get("summary", "")
            cell, origin = p.get("cell", "3,3,3"), p.get("origin", "waking")
            if not summary:
                continue
            score = (1.8 if (subj in seed_set or obj in seed_set) else 0.0)
            if subj in hop1_weights:
                score += 0.6 * min(1.5, hop1_weights[subj])
            if obj in hop1_weights:
                score += 0.6 * min(1.5, hop1_weights[obj])
            score += max(0.0, self.brain.cosine_similarity(query_vec, self.brain.phrase_to_vector(summary))) * 1.2
            if origin == "waking":
                score += 0.2
            tag = "Waking Memory" if origin == "waking" else "Dream Synthesis"
            if label:
                tag += " · firm" if origin == "waking" else " · dream, not a real event"
            fmt = f"[{tag} @ ({cell})]: {summary}"
            strength_of[fmt] = 2.0 if origin == "waking" else 0.5
            if score >= 0.65 and fmt not in seen:
                seen.add(fmt)
                candidates.append((score, fmt))

        for ep in (self.episodic_archive[:-1] if len(self.episodic_archive) > 1 else []):
            ep_c = set(ep.get("concepts", []))
            ep_sum = ep.get("summary", "")
            if not ep_sum:
                continue
            direct = len(seed_set & ep_c) * 1.5
            hop = sum(0.5 for c in ep_c if c in hop1_weights)
            ep_vec = self.brain.phrase_to_vector(" ".join(ep_c) + " " + ep.get("proposition", ""))
            score = direct + hop + max(0.0, self.brain.cosine_similarity(query_vec, ep_vec)) * 1.25
            if score >= 0.75 and ep_sum not in seen:
                seen.add(ep_sum)
                familiar = int(ep.get("recalled", 0)) >= 3
                ep_text = f"[Past Episode{(' · familiar' if familiar else ' · faint') if label else ''}]: {ep_sum}"
                strength_of[ep_text] = 2.0 if familiar else 1.0
                candidates.append((score, ep_text))
                ep_index_of = getattr(self, "_ep_index_of", {})
                ep_index_of[ep_text] = ep
                self._ep_index_of = ep_index_of

        candidates.sort(key=lambda x: x[0], reverse=True)
        self.last_retrieved_episodes = [text for _, text in candidates[:top_k]]
        # how strong is the best memory this turn (notes are checked in build_state_injection)
        self.memory_strength = max([strength_of.get(t, 1.0) for t in self.last_retrieved_episodes] or [0.0])
        for t in self.last_retrieved_episodes:  # count recalls, so often-recalled episodes become "familiar"
            ep = getattr(self, "_ep_index_of", {}).get(t)
            if ep is not None:
                ep["recalled"] = int(ep.get("recalled", 0)) + 1
        self._ep_index_of = {}
        return self.last_retrieved_episodes

    def resolve_voice_mode(self, requested_mode: str = None) -> str:
        if requested_mode:
            m = requested_mode.strip().upper()
            if m in ("SOVEREIGN", "SOV", "READONLY", "READ_ONLY", "GEO"):
                mode = "SOVEREIGN"
            elif m in ("ATTENUATED", "ATT", "LOW", "GYRE"):
                mode = "ATTENUATED"
            else:
                mode = "FULL_PLASTICITY"
            self.brain.knowledge_facts["_voice_mode"] = mode
            self.brain.save_memory()
            return mode

        saved_mode = str(self.brain.knowledge_facts.get("_voice_mode", "")).strip().upper()
        if saved_mode in ("SOVEREIGN", "ATTENUATED", "FULL_PLASTICITY"):
            return saved_mode

        return "FULL_PLASTICITY"

    def voice_mode_badge(self) -> str:
        return "🔇 SOVEREIGN" if self.voice_mode == "SOVEREIGN" else ("🔉 ATTENUATED" if self.voice_mode == "ATTENUATED" else "🔊 FULL_PLASTICITY")

    def normalize_model_name(self, raw_name: str) -> str:
        cleaned = re.sub(r"\s+", "", raw_name.strip().lower())
        for m in self.available_models:
            if m.lower() == cleaned or m.lower().split(":")[0].split("/")[-1] == cleaned:
                return m
        for m in self.available_models:
            if cleaned in m.lower():
                return m
        return raw_name.strip()

    def probe_and_connect(self, host_str: str, verbose: bool = True) -> bool:
        h = host_str.strip().rstrip("/").replace("http://localhost", "http://127.0.0.1")
        if not h.startswith("http"):
            h = "http://" + h
        for suf in ("/api/chat", "/v1/chat/completions", "/v1"):
            if h.endswith(suf):
                h = h[:-len(suf)]

        default_port = "12434" if self.is_mobile else "11434"
        host_part = h.split("//")[-1]
        ip_str, port_str = (host_part.split(":", 1) if ":" in host_part else (host_part, default_port))
        port_num = int(port_str.split("/")[0])
        h = f"http://{ip_str}:{port_num}"
        self.base_url = h

        try:
            with socket.create_connection((ip_str, port_num), timeout=2.0):
                pass
        except Exception as e:
            self.last_error = f"Port {ip_str}:{port_num} closed ({e})"
            if verbose:
                print(f"  [❌] {self.last_error}")
            return False

        headers = {"Authorization": "Bearer local-lan", "Connection": "close"}
        if not self.is_mobile and port_num == 11434:
            probe_order = [("ollama", f"{h}/api/tags", f"{h}/api/chat"), ("openai", f"{h}/v1/models", f"{h}/v1/chat/completions")]
        else:
            probe_order = [("openai", f"{h}/v1/models", f"{h}/v1/chat/completions"), ("ollama", f"{h}/api/tags", f"{h}/api/chat")]

        found, chosen_backend, chosen_endpoint, running_models = [], None, None, []
        if not self.is_mobile and port_num == 11434:
            try:
                req_ps = urllib.request.Request(f"{h}/api/ps", method="GET")
                with urllib.request.urlopen(req_ps, timeout=2) as r_ps:
                    ps_data = json.loads(r_ps.read().decode("utf-8"))
                    running_models = [m["name"] for m in ps_data.get("models", []) if "name" in m]
            except Exception:
                pass

        for b_type, m_url, c_url in probe_order:
            try:
                req = urllib.request.Request(m_url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=4) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if b_type == "openai":
                        models = [m.get("id") or m.get("name") for m in data.get("data", []) if isinstance(m, dict)]
                    else:
                        models = [m.get("name") for m in data.get("models", []) if isinstance(m, dict)]
                    models = [m for m in models if m]
                    if verbose:
                        print(f"  [✓] {m_url} -> {models}")
                    if chosen_endpoint is None or (models and not found):
                        chosen_backend, chosen_endpoint, found = b_type, c_url, models
                    if models:
                        break
            except Exception as e:
                if verbose:
                    print(f"  [•] {m_url} -> {e}")

        self.available_models = found
        preferred = self.normalize_model_name(self.preferred_model) if self.preferred_model else ""
        if preferred and preferred in found:
            self.model_name = preferred
        elif running_models:
            self.model_name = running_models[0]
        elif found:
            self.model_name = self.normalize_model_name(self.model_name)
            if self.model_name not in found:
                gemma_m = [m for m in found if "gemma" in m.lower()]
                self.model_name = gemma_m[0] if gemma_m else found[0]

        if port_num == 12434:
            self.backend, self.endpoint = "openai", f"{h}/v1/chat/completions"
        elif chosen_endpoint:
            self.backend, self.endpoint = chosen_backend, chosen_endpoint
        else:
            self.backend = "ollama" if port_num == 11434 else "openai"
            self.endpoint = f"{h}/api/chat" if self.backend == "ollama" else f"{h}/v1/chat/completions"

        self.last_error = ""
        if verbose:
            print(f"  [✅] Locked Endpoint: {self.endpoint} ({self.backend.upper()}) | Model: {self.model_name}")
        return True

    # =========================================================================
    # 1. STATE INJECTOR: Absolute Wheels-Off Telemetry vs. Guided Wheels-On
    # =========================================================================
    def build_state_injection(self, user_text: str, pre_reply: str, audit: dict, salient_concepts: list) -> str:
        active_traj = audit["flippedTrajectory"] if self.brain.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s, a, z = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        cell_key = f"{s},{a},{z}"

        bot_name = self.brain.user_profile.get("bot_name") or "Manifold"
        user_name = (self.brain.user_profile.get("user_name") or "Friend").capitalize()

        s_desc = BRAIN_LIBRARY["S_axes"][str(s)]
        a_desc = BRAIN_LIBRARY["A_axes"][str(a)]
        z_desc = BRAIN_LIBRARY["Z_axes"][str(z)]

        thought_trace = self.brain.last_thought_trace
        ponder = thought_trace.get("pondering", {})
        a_star_nodes = thought_trace.get("a_star_path", [])
        a_star_path = " -> ".join(a_star_nodes)
        prop = ponder.get("pondered_proposition", "harmony grounds clarity")
        ponder_bridge = ponder.get("pondered_bridge", "clarity")

        # Gather active semantic weights from the terminal cell & trajectory
        cell_words = list(self.brain.cortical_cells.get(cell_key, {}).keys())[:4]
        weight_anchors = list(dict.fromkeys(salient_concepts[:2] + [ponder_bridge] + a_star_nodes[:3] + cell_words[:2]))
        weight_anchors = [w for w in weight_anchors if w and w not in self.brain.stop_words][:5]
        weights_str = ", ".join(weight_anchors) if weight_anchors else "curiosity and equilibrium"

        top_k_ep = 2 if self.is_mobile else 3
        used_notes = self.notes_for_prompt(user_text)
        notes_line = ""
        if used_notes:
            teacher = (self.brain.user_profile.get("user_name") or "the user").capitalize()
            items = " | ".join((f"{n['key']}: {n['text']}" if n["key"] else n["text"]) for n in used_notes)
            notes_line = f"\nConfirmed notes from {teacher} (true; use these over anything else below): {items}"
        retrieved_episodes = self.retrieve_relevant_episodes(user_text, salient_concepts, top_k=top_k_ep)
        if used_notes:
            self.memory_strength = 4.0
        sleep_line, pressure_line = self.sleep_lines(user_text)
        if sleep_line and self.brain.describe_last_sleep():
            self.memory_strength = max(self.memory_strength, 3.0)  # a real sleep record is a true memory ("no record" isn't)
        self.turn_tone = self.tone_settings(audit, user_text)
        memory_check_line = ""
        if self.callosum["memory"] and self.turn_tone["unsure"]:
            # Goes LAST in the prompt (small models follow the final line best). The 2026-11-08 Gyre test showed the
            # softer wording, placed mid-prompt, was half-obeyed ("my memory is fragmented") and then ignored.
            memory_check_line = ("\nMemory check: nothing in your memory covers this. If the question is about a past event, "
                                 "say plainly in your first sentence that you don't remember it, and do not make up events, "
                                 "logs, data or details to fill the gap.")
        length_hint = f" Keep it to about {self.turn_tone['sentences']} sentences." if self.callosum["tone"] else ""

        # ---------------------------------------------------------------------
        # ABSOLUTE WHEELS-OFF MODE (Default: Raw Spatial Telemetry, Zero Templates)
        # ---------------------------------------------------------------------
        if not self.brain.training_wheels:
            summary_line = f"\nRunning Conversation Context: {self.running_summary}" if self.running_summary else ""
            episodes_line = f"\nRelevant Past Memory Anchors: {' | '.join(retrieved_episodes)}" if retrieved_episodes else ""
            if retrieved_episodes and self.callosum["memory"]:
                episodes_line += " (strength: strong > firm/familiar > faint > dream)"
            self.last_prompt_text = (
                f"You are {bot_name}, speaking with {user_name}.\n"
                f"Current Manifold Coordinate: ({s},{a},{z}) [S={s}: {s_desc}; A={a}: {a_desc}; Z={z}: {z_desc}].\n"
                f"Active semantic weights lean toward: {weights_str}.\n"
                f"Underlying conceptual link: {prop} (path: {a_star_path})."
                f"{notes_line}{summary_line}{episodes_line}{sleep_line}{pressure_line}\n"
                f"Directive: Let the coordinate ({s},{a},{z}) and active semantic weights ({weights_str}) shape your tone and perspective naturally. "
                f"Respond natively without performative stage directions, parenthetical mood actions, or internal engine debug strings.{length_hint}"
                f"{memory_check_line}"
            )
            # What counts as "grounded" for careful learning: the user's words and what the BRAIN supplied (notes, memory
            # lines, its weights and path). Not the running summary (the LLM wrote it, so it would launder invented words)
            # and not the fixed template text (axis descriptions, directive), which would ground words like "reflection" every turn.
            self.last_ground_text = " ".join([user_text, notes_line, " ".join(retrieved_episodes), weights_str, prop, a_star_path,
                                              sleep_line, pressure_line])
            return self.last_prompt_text

        # ---------------------------------------------------------------------
        # TRAINING WHEELS ON (Explicit Scaffolding & Debug Inspection Mode)
        # ---------------------------------------------------------------------
        cell_mood = self.brain.get_cell_emotion_name(s, a, z)
        trace_mood = self.brain.trace_lexicon.get(self.brain.last_trace_key, {}).get("name", "Harmonic-Pivot")
        crystal = self.brain.crystal_lattices.get(cell_key) or self.brain.nucleate_or_update_crystal(cell_key, force_virtual=True)
        facets = crystal.get("facets", {})
        alpha_w = facets.get("Facet_Alpha", {}).get("words", [])[:4]
        gamma_w = facets.get("Facet_Gamma", {}).get("words", [])[:4]
        omega_w = facets.get("Facet_Omega", {}).get("words", [])[:2]

        self.last_prompt_text = (
            f"You are {bot_name} speaking with {user_name} in explicit scaffolding mode.\n"
            f"• Active 3D Coordinate: ({s}, {a}, {z}) | Mood: '{cell_mood}' | Shift: '{trace_mood}'\n"
            f"• Axes: S={s} ({s_desc}) | A={a} ({a_desc}) | Z={z} ({z_desc})\n"
            f"• Crystal Facets: Alpha={alpha_w}, Gamma={gamma_w}, Omega={omega_w}\n"
            f"• 3D A* Path: {a_star_path} | Pondered Proposition: [{prop}]\n"
            f"• Engine Sub-Vocal Draft: \"{pre_reply}\"\n"
            + (f"• {notes_line.strip()}\n" if notes_line else "")
            + (f"• {sleep_line.strip()}\n" if sleep_line else "")
            + (f"• {pressure_line.strip()}\n" if pressure_line else "")
            + f"Directive: Reference your 3D coordinate ({s},{a},{z}), mood '{cell_mood}', and proposition [{prop}] explicitly.{length_hint}"
            + memory_check_line
        )
        self.last_ground_text = " ".join([user_text, notes_line, " ".join(retrieved_episodes), weights_str, prop,
                                          a_star_path, pre_reply, " ".join(alpha_w + gamma_w + omega_w), sleep_line, pressure_line])
        return self.last_prompt_text

    def _parse_response_body(self, raw_text: str) -> str:
        raw_text = raw_text.strip()
        if not raw_text:
            return ""
        if raw_text.startswith("data:"):
            chunks = []
            for line in raw_text.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        obj = json.loads(data_str)
                        delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if not delta:
                            delta = obj.get("choices", [{}])[0].get("message", {}).get("content", "")
                        chunks.append(delta)
                    except Exception:
                        pass
            return "".join(chunks).strip()

        data = json.loads(raw_text)
        if "choices" in data and data["choices"]:
            msg = data["choices"][0].get("message", {})
            if "content" in msg:
                return msg["content"].strip()
            if "text" in data["choices"][0]:
                return data["choices"][0]["text"].strip()
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"].strip()
        if "response" in data:
            return data["response"].strip()
        return ""

    def stream_chat(self, messages: list, max_tokens: int, temperature: float, show_progress: bool = False) -> str:
        """Send one chat request and read the answer as it streams in.
        Streaming matters on a slow PC: the timeout then only covers the wait for the model to START (and each
        pause between pieces), not the whole reply, so a long answer can't time out while the model is still writing."""
        headers = {"Content-Type": "application/json", "Authorization": "Bearer local-lan", "Connection": "close"}
        if self.backend == "ollama":
            payload = {"model": self.model_name, "messages": messages, "stream": True, "keep_alive": LLM_KEEP_ALIVE,
                       "options": {"temperature": temperature, "num_predict": max_tokens}}
            if LLM_SEED.lstrip("-").isdigit():
                payload["options"]["seed"] = int(LLM_SEED)
        else:
            payload = {"model": self.model_name, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "stream": True}
            if LLM_SEED.lstrip("-").isdigit():
                payload["seed"] = int(LLM_SEED)
        self.last_finish_reason = ""
        req = urllib.request.Request(self.endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        pieces, raw_lines, shown = [], [], 0
        if show_progress:
            print(f"   ⏳ {self.model_name} ", end="", flush=True)
        try:
            with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SEC) as resp:
                for raw in resp:
                    line = raw.decode("utf-8", errors="ignore").strip()
                    if not line:
                        continue
                    raw_lines.append(line)
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            ch = json.loads(data).get("choices", [{}])[0]
                            piece = ch.get("delta", {}).get("content") or ch.get("message", {}).get("content") or ""
                            if ch.get("finish_reason"):
                                self.last_finish_reason = str(ch.get("finish_reason"))
                        except (ValueError, AttributeError, IndexError):
                            continue
                    else:
                        try:
                            obj = json.loads(line)
                        except ValueError:
                            continue
                        piece = (obj.get("message") or {}).get("content") or obj.get("response") or ""
                        if obj.get("done"):
                            pieces.append(piece)
                            self.last_finish_reason = str(obj.get("done_reason") or "")
                            break
                    pieces.append(piece)
                    if show_progress and len(pieces) - shown >= 8:
                        print(".", end="", flush=True)
                        shown = len(pieces)
        finally:
            if show_progress:
                print()
        text = "".join(pieces).strip()
        if not text and raw_lines:  # a server that ignored stream=True and sent one ordinary answer
            text = self._parse_response_body("\n".join(raw_lines))
        return text

    # =========================================================================
    # CALLOSUM step 2: TONE. The brain's movement this turn sets HOW the voice speaks, a channel the model can't
    # ignore the way it can ignore prompt text. Velocity (S, A, Z), each about -2.5..+2.5, is the push of this turn:
    #   tense (A < 0)                  -> lower temperature (more careful)
    #   abstract / inquiring (Z > 0)   -> a bit higher temperature, longer reply
    #   a big move (fast, aroused)     -> shorter reply
    #   no clear memory + a question   -> lower temperature (less room to invent)
    # Length is a target number of sentences (a hard token cap just cuts replies off mid-sentence).
    # =========================================================================
    QUESTION_STARTS = ("what", "how", "why", "when", "where", "who", "do", "did", "does", "can", "could", "is", "are",
                       "was", "were", "will", "would", "have", "has", "tell")

    def is_question(self, text: str) -> bool:
        t = text.strip().lower()
        return "?" in t or t.startswith(self.QUESTION_STARTS)

    SLEEP_WORDS = {"sleep", "slept", "sleeping", "asleep", "nap", "napped", "napping", "rest", "rested", "resting", "tired",
                   "sleepy", "woke", "wake", "waking", "dream", "dreams", "dreamed", "dreamt", "dreaming", "goodnight"}

    def sleep_lines(self, user_text: str):
        """Engine v22.1: (1) when the user asks about sleep, the brain's real record of its last sleep, so the model doesn't
        invent one; (2) when sleep pressure is high (or the user asks if it's tired), a plain line about it.
        A brain whose NAME is a sleep word ("Dream") doesn't trigger this by being addressed; only the word does."""
        if not hasattr(self.brain, "sleep_pressure_report"):
            return "", ""
        toks = self.brain.clean_tokens(user_text)
        hits = set(toks) & self.SLEEP_WORDS
        own = (self.brain.user_profile.get("bot_name") or "").strip().lower()
        if own in hits and own not in self.brain.find_names_used_as_words(user_text, toks):
            hits.discard(own)  # "Dream, how are you?" is the name, not the word
        sleep_line = ""
        if hits:
            desc = self.brain.describe_last_sleep()
            sleep_line = (f"\nYour last sleep (true, from your own record): {desc}." if desc
                          else "\nYour last sleep: you have no record of sleeping yet. If asked, say plainly that you "
                               "don't remember it; don't describe what it was like.")
        rep = self.brain.sleep_pressure_report()
        pressure_line = ""
        if rep["level"] in ("high", "very high"):
            pressure_line = (f"\nSleep pressure: {rep['level']} — you have learned a lot since your last full sleep and feel ready to rest. "
                             f"Mention it briefly only if it fits; don't dramatize it.")
        elif hits & {"tired", "sleepy", "rest", "rested", "sleep"}:
            pressure_line = f"\nSleep pressure: {rep['level']} — say so plainly if asked whether you're tired."
        return sleep_line, pressure_line

    def tone_settings(self, audit: dict, user_text: str) -> dict:
        vs, va, vz = (list(audit.get("velocity", [0.0, 0.0, 0.0])) + [0.0, 0.0, 0.0])[:3]
        speed = (vs * vs + va * va + vz * vz) ** 0.5
        temp = self.temperature + 0.06 * vz - 0.08 * max(0.0, -va)
        unsure = self.callosum["memory"] and self.memory_strength <= 1.0 and self.is_question(user_text)
        if unsure:
            temp -= 0.15
        temp = round(min(1.0, max(0.25, temp)), 2)
        length = min(1.3, max(0.5, 1.0 + 0.12 * vz - 0.07 * speed))
        sentences = int(min(8, max(2, round(4.5 * length))))
        return {"temperature": temp, "sentences": sentences, "unsure": unsure,
                "velocity": [round(vs, 2), round(va, 2), round(vz, 2)]}

    @staticmethod
    def trim_to_sentence(text: str) -> str:
        """A reply cut off by the length limit is trimmed back to its last full sentence."""
        ends = [m.end() for m in re.finditer(r"[.!?…][\"'”’)]?(?=\s|$)", text)]
        if ends and ends[-1] >= 0.4 * len(text):
            return text[:ends[-1]].rstrip()
        return text.rstrip() + "…"

    def host_is_reachable(self) -> bool:
        """Quick 2-second check that something is listening on the LLM port."""
        hp = self.base_url.split("//")[-1]
        ip, port = (hp.split(":", 1) + ["11434"])[:2]
        try:
            with socket.create_connection((ip, int(port.split("/")[0])), timeout=2.0):
                return True
        except OSError:
            return False

    def call_local_llm(self, state_block: str, user_text: str, fallback_reply: str) -> str:
        self.last_used_fallback = False
        use_merged_user_role = self.is_mobile or self.force_merged_role or ("gemma" in self.model_name.lower() and self.backend == "openai")

        recent_slice = self.chat_history[-self.keep_raw_len:] if self.keep_raw_len > 0 else []
        if recent_slice and recent_slice[0].get("role") != "user":
            recent_slice = recent_slice[1:]

        if use_merged_user_role:
            messages = list(recent_slice)
            messages.append({"role": "user", "content": f"{state_block}\n\nUser: {user_text}"})
        else:
            messages = [{"role": "system", "content": state_block}]
            messages.extend(recent_slice)
            messages.append({"role": "user", "content": user_text})

        # Not connected: a quick 2 s check first, so an offline host can't stall every turn. If it answers, use the
        # normal timeout. (Before, being "not connected" once meant every later reply got only 5 seconds, which a
        # small PC can't meet, so the bridge looked disconnected for the rest of the session.)
        if not self.connected and not self.host_is_reachable():
            problem = f"nothing is listening at {self.base_url}"
        else:
            try:
                tone = self.turn_tone if (self.turn_tone and self.callosum["tone"]) else None
                temperature = tone["temperature"] if tone else self.temperature
                self.last_tone, self.turn_tone = tone, None
                # The sentence target in the prompt was ignored in the 2026-11-08 test (asked ~4, got ~9), so the target
                # also sets a token ceiling (~45 tokens a sentence, roomy for long sentences); a reply that hits it is
                # trimmed back to its last full sentence below.
                cap = min(self.max_tokens, 45 * tone["sentences"] + 30) if tone else self.max_tokens
                reply = self.stream_chat(messages, cap, temperature, show_progress=True)
                if reply and self.last_finish_reason == "length":
                    reply = self.trim_to_sentence(reply)
                if reply:
                    self.connected = True
                    self._warned_unreachable = False
                    return strip_performative_directions(reply) if not self.brain.training_wheels else reply
                problem = "the model sent back an empty reply"
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                if not use_merged_user_role and e.code in (400, 422):
                    self.force_merged_role = True  # this server wants everything in one user message; retry that way
                    return self.call_local_llm(state_block, user_text, fallback_reply)
                problem = f"HTTP {e.code}: {err_body[:200]}"
            except (TimeoutError, socket.timeout):
                problem = (f"the model didn't start answering within {LLM_TIMEOUT_SEC:.0f}s "
                           f"(it may still be loading; raise TORRENT_LLM_TIMEOUT if this keeps happening)")
            except urllib.error.URLError as e:
                if isinstance(e.reason, (TimeoutError, socket.timeout)):
                    problem = f"the model didn't start answering within {LLM_TIMEOUT_SEC:.0f}s"
                else:
                    self.connected = False  # the server itself is gone (refused / unreachable)
                    problem = f"connection error: {e.reason}"
            except (ConnectionError, OSError) as e:
                self.connected = False
                problem = f"connection error: {e}"

        print(f"\n[!] No LLM reply this turn ({problem}). Using the T.O.R.R.E.N.T. native reply.")
        self.last_used_fallback = True
        return fallback_reply

    def grounded_words(self, user_text: str, user_concepts: list) -> set:
        """Words the model could have got from the user or the brain this turn (see last_ground_text), plus words
        already linked to the user's concepts."""
        ground = self.with_singulars(self.brain.clean_tokens(f"{user_text} {self.last_ground_text}".replace("-", " ")))
        for uc in user_concepts[:5]:
            ground |= {nb for nb, wt in self.brain.assoc_graph.get(uc, {}).items() if wt >= 0.45}
        return ground

    def post_process_llm_response(self, user_text: str, llm_reply: str, audit: dict, user_concepts: list) -> dict:
        active_traj = audit["flippedTrajectory"] if self.brain.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s, a, z = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        cell_key = f"{s},{a},{z}"

        normalized_reply = llm_reply.replace("-", " ")
        llm_tokens = self.brain.clean_tokens(normalized_reply)
        llm_concepts, _ = self.brain.extract_concepts(normalized_reply, llm_tokens)

        stop_echoes = {
            "currently", "apologies", "certainly", "fascinating", "hellohello",
            "ollama", "serve", "export", "indeed", "absolutely", "furthermore"
        }
        pure_llm_concepts = [
            c for c in llm_concepts
            if self.brain.is_crystal_pure_concept(c)
            and c not in stop_echoes
            and c in self.brain.vectors
        ][:6]

        llm_vec = self.brain.phrase_to_vector(normalized_reply)
        cell_vec = self.brain.cell_centroids.get(cell_key, self.brain.coord_vectors[(s, a, z)])
        ponder_bridge = self.brain.last_thought_trace.get("pondering", {}).get("pondered_bridge", "harmony")
        bridge_vec = self.brain.vectors.get(ponder_bridge, self.brain.pole_calm)

        cell_coherence = round(self.brain.cosine_similarity(llm_vec, cell_vec), 3)
        bridge_coherence = round(self.brain.cosine_similarity(llm_vec, bridge_vec), 3)
        combined_coherence = round(0.6 * cell_coherence + 0.4 * bridge_coherence, 3)

        wired_concepts, extracted_prop, tectonic_logs, held_back = [], None, [], []
        cleavage_count_before = len(self.brain.cleavage_log)
        # Engine v22: learning from the reply is waking learning, so it builds sleep pressure like the user's words do
        # (the engine only counts what happens inside respond(), and this runs after it). Older engines ignore this.
        reply_cell_mass_before = sum(sum(v.values()) for v in self.brain.cortical_cells.values())
        self.brain.awake_turn = True

        if self.voice_mode == "SOVEREIGN" or self.last_used_fallback:
            # SOVEREIGN never learns from replies; a native fallback reply is the engine's own output, so it isn't re-learned
            pass
        elif self.voice_mode == "ATTENUATED":
            novel_glove_cands = [
                c for c in pure_llm_concepts
                if (c in self.brain.raw_glove or c in self.brain.core_concept_pool)
                and c not in user_concepts
                and c != ponder_bridge
            ]
            if self.callosum["memory"]:
                # Careful learning applies here too (Gyre runs ATTENUATED): only a grounded word may be the one learned.
                # In the 2026-11-08 test, 'crystalline' from an invented birthday story was wired this way.
                ground = self.grounded_words(user_text, user_concepts)
                held_back = [c for c in novel_glove_cands if c not in ground][:3]
                novel_glove_cands = [c for c in novel_glove_cands if c in ground]
            if novel_glove_cands:
                top_novel = novel_glove_cands[0]
                wired_concepts = [top_novel]
                self.brain.cortical_cells.setdefault(cell_key, {})
                self.brain.cortical_cells[cell_key][top_novel] = self.brain.cortical_cells[cell_key].get(top_novel, 0) + 1
                if ponder_bridge and top_novel != ponder_bridge:
                    self.brain.wire_concepts(ponder_bridge, top_novel, amount=0.20)
                if user_concepts and top_novel != user_concepts[0]:
                    self.brain.wire_concepts(user_concepts[0], top_novel, amount=0.15)
                self.brain.update_cell_centroid_and_emotion(s, a, z, wired_concepts, allow_cleave=False)
        else:
            ideas_before = len(self.brain.idea_memory)
            extracted_prop = self.brain.extract_proposition(normalized_reply, llm_tokens, pure_llm_concepts, cell_key)
            wired_concepts = pure_llm_concepts[:4]
            # Careful learning (callosum step 1): a reply word is "grounded" if it was in the user's words or in what the
            # brain gave the model (prompt, notes, memories), or is already linked to the user's concepts. Grounded words are
            # learned as before. Ungrounded ones (very likely the model inventing) are only linked faintly and don't enter
            # the cell, so they can't crystallize or spread through dreams.
            grounded = set(wired_concepts)
            if self.callosum["memory"]:
                ground = self.grounded_words(user_text, user_concepts)
                grounded = {c for c in wired_concepts if c in ground}
                held_back = [c for c in wired_concepts if c not in grounded]
                if extracted_prop and not ({extracted_prop["subj"], extracted_prop["obj"]} <= ground):
                    # an "idea" built from invented words is not kept as a waking memory
                    self.brain.idea_memory = [p for p in self.brain.idea_memory[:ideas_before]] + \
                        [p for p in self.brain.idea_memory[ideas_before:] if p is not extracted_prop]
                    extracted_prop = None
            self.brain.cortical_cells.setdefault(cell_key, {})
            for c in wired_concepts:
                self.brain.get_or_create_vector(c, context_vec=cell_vec)
                k = 1.0 if c in grounded else 0.25
                if c in grounded:
                    self.brain.cortical_cells[cell_key][c] = self.brain.cortical_cells[cell_key].get(c, 0) + 1
                if ponder_bridge and c != ponder_bridge:
                    self.brain.wire_concepts(ponder_bridge, c, amount=0.65 * k)
                if user_concepts and c != user_concepts[0]:
                    self.brain.wire_concepts(user_concepts[0], c, amount=0.55 * k)
            wired_concepts = [c for c in wired_concepts if c in grounded]

            if combined_coherence < 0.25 and pure_llm_concepts:
                outlier = min(pure_llm_concepts, key=lambda w: self.brain.dot(self.brain.vectors.get(w, cell_vec), cell_vec))
                self.brain.apply_dialectical_repulsion(ponder_bridge, outlier, rate=0.04)

            self.brain.update_cell_centroid_and_emotion(s, a, z, wired_concepts, allow_cleave=True)
            tectonic_logs = self.brain.run_crystal_annealing_and_tectonics()

        self.brain.awake_turn = False
        if hasattr(self.brain, "cells_added_since_sleep"):
            gained = sum(sum(v.values()) for v in self.brain.cortical_cells.values()) - reply_cell_mass_before
            self.brain.cells_added_since_sleep += max(0.0, gained)
        new_cleavages = self.brain.cleavage_log[cleavage_count_before:]
        shear_after = self.brain.crystal_lattices.get(cell_key, {}).get("shear_stress", 0.0)

        post_report = {
            "voiceMode": self.voice_mode,
            "usedNativeFallback": self.last_used_fallback,
            "wheelsOff": not self.brain.training_wheels,
            "terminalCell": cell_key,
            "cellCoherence": cell_coherence,
            "bridgeCoherence": bridge_coherence,
            "combinedCoherence": combined_coherence,
            "llmCandidateConcepts": pure_llm_concepts,
            "llmWiredConcepts": wired_concepts,
            "llmHeldBack": held_back if self.voice_mode != "SOVEREIGN" and not self.last_used_fallback and self.callosum["memory"] else [],
            "tone": self.last_tone,
            "memoryStrength": self.memory_strength,
            "llmPropositionLearned": extracted_prop["summary"] if extracted_prop else None,
            "retrievedPastEpisodes": self.last_retrieved_episodes,
            "postShearStress": shear_after,
            "cleavageEventsTriggered": [ev["summary"] for ev in new_cleavages],
            "tectonicLogs": tectonic_logs
        }

        self.last_post_audit = post_report
        if self.brain.last_audit is not None:
            self.brain.last_audit["llmPostProcessor"] = post_report
        # (no save here: record_turn_and_maybe_summarize saves the brain right after this, so one save per turn)
        self.brain.export_trace_file("latest_trace.json")
        return post_report


if __name__ == "__main__":
    IS_MOBILE = detect_mobile_platform()
    CLI_VOICE_MODE = parse_voice_mode()

    if not IS_MOBILE:
        os.system("cls" if os.name == "nt" else "clear")
    else:
        print("🚀 Booting T.O.R.R.E.N.T. + Local LLM Bridge (Wheels-Off Mode)...")

    glove_limit = 50000
    from brainpicker import choose_brain_file, claim_brain, release_brain, new_brain_path, BRAINS_DIR
    brain_file = choose_brain_file()  # menu of brains/, or --brain NAME / --new
    claim_brain(brain_file)
    brain = ToroidalBrainEngine(glove_file="glove.6B.50d.txt", memory_file=brain_file, max_glove_words=glove_limit)
    print(f" 📁 Brain file: {brain_file}")

    middleware = TorrentLLMMiddleware(
        brain=brain,
        is_mobile=IS_MOBILE,
        model_name=os.environ.get("TORRENT_MODEL", None),
        host=os.environ.get("TORRENT_HOST", None),
        voice_mode=CLI_VOICE_MODE
    )
    voice_io = LocalVoiceEngine(is_mobile=IS_MOBILE)

    header_identity = brain.user_profile.get("bot_name") or "[Manifold]"
    platform_badge = "MOBILE 📱" if IS_MOBILE else "DESKTOP PC 🖥️"
    status_str = (
        f"ONLINE ✅ ({middleware.backend.upper()} API | Models: {', '.join(middleware.available_models) or middleware.model_name})"
        if middleware.connected else f"UNREACHABLE ⚠️ ({middleware.last_error})"
    )

    print("=" * 86)
    print(f" 🧠 {header_identity} · T.O.R.R.E.N.T. v22.3 Brain + Local LLM Vocal Cortex")
    print(f"    Platform   : {platform_badge} | GloVe Vocab: {len(brain.raw_glove):,} vectors")
    print(f"    Prompt Mode: {'WHEELS-OFF 🚀 (Raw Spatial Telemetry)' if not brain.training_wheels else 'WHEELS-ON 🛞 (Scaffolding)'}")
    print(f"    Efference  : {middleware.voice_mode_badge()} | Local TTS: {'ON 🔊' if voice_io.tts_enabled else 'OFF 🔇 (/tts)'}")
    if getattr(brain, "nightmare_mode", False):
        print("    Nightmare  : 🌑 ON (lean-up rules off for this brain; /nightmare to turn off)")
    print(f"    Memory     : {len(middleware.episodic_archive)} Past Episodes | Summary: {'ACTIVE 📜' if middleware.running_summary else 'Fresh Session'}")
    print(f"    Backend    : {middleware.backend.upper()} | Active Model: {middleware.model_name} ({middleware.endpoint})")
    print(f"    Status     : {status_str}")
    print("-" * 86)
    print(" Voice Commands  : /tts (toggle speech out), /listen [sec] (mic STT in), /voicechat (hands-free loop)")
    print(" Bridge Commands : /memory [compress], /mode <sovereign|attenuated|full>, /test, /connect, /models, /model, /prompt, /post")
    print(" Notes & Undo    : /note <key>: <text>, /notes, /notes delete <n>, /recall <word>, /back (undo your last message)")
    print(" Callosum        : /callosum [on|off], /callosum memory on|off, /callosum tone on|off  (see the tone with /prompt)")
    print(" TORRENT Commands: /wheels, /export, /crystals, /ponder, /sleep, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /nightmare, /exit")
    print("=" * 86)

    brain.run_boot_calibration_and_handshake()
    if not CLI_VOICE_MODE:
        middleware.voice_mode = middleware.resolve_voice_mode()

    show_telemetry, show_grid, last_system_prompt = True, False, ""

    while True:
        try:
            u_name = brain.user_profile.get("user_name", "").strip()
            user_tag = f"You ({u_name.capitalize()})" if u_name else "You"
            mode_badge = "🛞" if brain.training_wheels else "🚀"
            tts_badge = " 🔊" if voice_io.tts_enabled else ""
            user_input = input(f"\n👤 {user_tag} [{mode_badge} | {middleware.voice_mode}{tts_badge}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n🌙 Entering NREM Homeostasis, Crystal Annealing & 3D REM Sleep Consolidation...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            middleware.save_persistent_chat_memory()
            brain.save_memory()
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        cmd_word = cmd.split()[0] if cmd.startswith("/") else ""
        # /back only undoes the last MESSAGE: any command that could change the brain in between cancels it
        READ_ONLY_CMDS = {"/back", "/notes", "/recall", "/facts", "/prompt", "/post", "/audit", "/crystals", "/emotions",
                          "/lexicon", "/telemetry", "/thoughts", "/ideas", "/links", "/cells", "/grid", "/models",
                          "/model", "/test", "/tts", "/export", "/connect", "/flip", "/callosum"}
        if cmd_word and cmd_word not in READ_ONLY_CMDS and not (cmd_word in ("/memory", "/history") and len(cmd.split()) == 1):
            middleware.undo_ready = False

        if cmd_word == "/back":
            undone = middleware.undo_last_turn()
            if undone:
                print(f"[↩️ Undid your last message: \"{cut_at_word(undone, 80)}\"]")
                print("   The brain, chat history and memories are back to how they were before it. (Logged in the brain file.)")
            else:
                print("[↩️ Nothing to undo. /back works once, right after a message, before any other command that changes the brain.]")
            continue

        if cmd_word == "/note":
            body = user_input[len("/note"):].strip()
            if not body:
                print("Usage: /note TCM: Toroidal-Crystalline Manifold   (or /note any sentence you want remembered)")
                continue
            note = middleware.add_note(body)
            label = f"{note['key']}: {note['text']}" if note["key"] else note["text"]
            print(f"[📝 Noted: {label}]")
            print(f"   Saved in {middleware.notes_path()}" + (f" · '{note['key']}' was also taught to the brain" if note["key"] and note["key"].lower() in brain.knowledge_facts else ""))
            continue

        if cmd_word in ("/notes", "/unnote"):
            parts = user_input.split()
            notes = middleware.load_notes()
            if cmd_word == "/unnote" or (len(parts) >= 2 and parts[1].lower() in ("delete", "del", "remove")):
                num = parts[1] if cmd_word == "/unnote" and len(parts) >= 2 else (parts[2] if len(parts) >= 3 else "")
                if not num.isdigit() or not (1 <= int(num) <= len(notes)):
                    print(f"Which note? e.g. /notes delete 2 (there are {len(notes)}).")
                    continue
                gone = notes.pop(int(num) - 1)
                middleware.write_notes(notes)
                print(f"[🗑️ Removed note: {gone['key'] + ': ' if gone['key'] else ''}{gone['text']}]")
                continue
            if not notes:
                print(f"No notes yet. Add one with /note TCM: Toroidal-Crystalline Manifold  (file: {middleware.notes_path()})")
                continue
            print(f"📝 Notes ({middleware.notes_path()}):")
            for i, n in enumerate(notes, 1):
                print(f"  {i:>2}. {n['key'] + ': ' if n['key'] else ''}{n['text']}" + (f"   [{n['meta']}]" if n["meta"] else ""))
            continue

        if cmd_word == "/recall":
            word = user_input[len("/recall"):].strip().lower()
            notes = middleware.load_notes()
            hits = [n for n in notes if word and (word in n["key"].lower() or word in n["text"].lower())] if word else notes
            if not hits:
                print(f"No notes mention '{word}'." if word else "No notes yet.")
                continue
            for i, n in enumerate(hits, 1):
                print(f"  {i:>2}. {n['key'] + ': ' if n['key'] else ''}{n['text']}")
            ans = input("Add these to your next message? (y/n, or numbers like 1,3): ").strip().lower()
            if ans in ("y", "yes"):
                middleware.pinned_notes = hits
            elif ans and ans != "n":
                picked = [int(x) for x in re.split(r"[,\s]+", ans) if x.isdigit() and 1 <= int(x) <= len(hits)]
                middleware.pinned_notes = [hits[i - 1] for i in picked]
            if middleware.pinned_notes:
                print(f"[📌 {len(middleware.pinned_notes)} note(s) will go with your next message.]")
            continue

        if cmd in ("exit", "/exit", "quit", "/quit"):
            print("\n🌙 Entering NREM Homeostasis, Crystal Annealing & 3D REM Sleep Consolidation...")
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            middleware.save_persistent_chat_memory()
            brain.save_memory()
            print(f"Saved {len(brain.assoc_graph)} nodes, {len(brain.crystal_lattices)} crystals, and {len(middleware.episodic_archive)} episodic memories.")
            break

        # --- Local Voice Commands (/tts, /listen, /voicechat) ---
        elif cmd == "/tts":
            voice_io.tts_enabled = not voice_io.tts_enabled
            print(f"[🔊 Local Text-to-Speech Output is now {'ON' if voice_io.tts_enabled else 'OFF'}]")
            if voice_io.tts_enabled:
                voice_io.speak("Voice output online.")
            continue

        elif cmd.startswith("/listen") or cmd.startswith("/mic"):
            parts = cmd.split()
            sec = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
            spoken_text = voice_io.listen_and_transcribe(duration_sec=sec)
            if not spoken_text:
                print("  [i] No speech detected.")
                continue
            print(f"🗣️ Transcribed: \"{spoken_text}\"")
            user_input = spoken_text

        elif cmd == "/voicechat":
            voice_io.tts_enabled = True
            print("\n🎙️ [HANDS-FREE VOICE CHAT LOOP ACTIVE — Press Enter to speak, or type 'q' + Enter to exit voice mode]")
            while True:
                sub = input("\n[Press Enter to record 5s of speech, or 'q' to return to text]: ").strip().lower()
                if sub in ("q", "quit", "exit"):
                    break
                spoken_text = voice_io.listen_and_transcribe(duration_sec=5)
                if not spoken_text:
                    print("  [i] No speech detected.")
                    continue
                print(f"🗣️ You said: \"{spoken_text}\"")
                middleware.take_snapshot(spoken_text)  # for /back
                pre_reply, audit, salient_c = brain.respond(spoken_text)
                last_system_prompt = middleware.build_state_injection(spoken_text, pre_reply, audit, salient_c)
                llm_reply = middleware.call_local_llm(last_system_prompt, spoken_text, fallback_reply=pre_reply)
                post_report = middleware.post_process_llm_response(spoken_text, llm_reply, audit, salient_c)
                middleware.record_turn_and_maybe_summarize(spoken_text, llm_reply, audit, salient_c)
                middleware.undo_ready = True
                bot_speaker = brain.user_profile.get("bot_name") or "[Manifold]"
                print(f"\n🤖 {bot_speaker} ({'native' if middleware.last_used_fallback else middleware.model_name}): {llm_reply}")
                voice_io.speak(llm_reply)
            continue

        elif cmd.startswith("/memory") or cmd.startswith("/history"):
            parts = cmd.split()
            if len(parts) > 1 and parts[1] in ("compress", "summarize"):
                if middleware.chat_history:
                    middleware.running_summary = middleware.compress_turns_into_summary(middleware.chat_history)
                    middleware.chat_history = middleware.chat_history[-middleware.keep_raw_len:]
                    middleware.save_persistent_chat_memory()
                    brain.save_memory()
                    print(f"\n📜 [Compressed Sliding History into Running Summary]:\n  {middleware.running_summary}")
                else:
                    print("\n[i] No active sliding turns to compress yet.")
                continue

            print("\n📜 TIER 1: RUNNING NARRATIVE SUMMARY:")
            print(f"  {middleware.running_summary or '(No summary compressed yet)'}")
            print(f"\n💬 TIER 1: ACTIVE SLIDING WINDOW ({len(middleware.chat_history)}/{middleware.summary_trigger_len} messages):")
            for m in middleware.chat_history:
                r_tag = "👤 User" if m["role"] == "user" else "🤖 AI  "
                print(f"  {r_tag}: {m['content'][:120]}")
            print(f"\n🧠 TIER 2: EPISODIC ARCHIVE ({len(middleware.episodic_archive)} stored episodes):")
            for ep in middleware.episodic_archive[-5:]:
                print(f"  • {ep['summary']}")
            continue

        elif cmd.split()[0] == "/mode":  # exact word, so "/model ..." and "/models" aren't caught here
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                arg = parts[1].strip().upper()
                valid_modes = ("SOVEREIGN", "SOV", "READONLY", "READ_ONLY", "GEO", "ATTENUATED", "ATT", "LOW", "GYRE", "FULL", "FULL_PLASTICITY", "PLASTIC", "HOPE")
                if arg in valid_modes:
                    middleware.voice_mode = middleware.resolve_voice_mode(arg)
                    print(f"[🎚️ Efference Gain Mode saved & locked to: {middleware.voice_mode_badge()}]")
                else:
                    print("Usage: /mode sovereign | /mode attenuated | /mode full")
            else:
                print(f"[Current Efference Mode: {middleware.voice_mode_badge()} | Usage: /mode <sovereign|attenuated|full>]")
            continue

        elif cmd.startswith("/voice") and cmd != "/voicechat":
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                middleware.voice_mode = middleware.resolve_voice_mode(parts[1])
                print(f"[🎚️ Efference Gain Mode saved & locked to: {middleware.voice_mode_badge()}]")
            else:
                print(f"[Current Efference Mode: {middleware.voice_mode_badge()} | Usage: /voice <sovereign|attenuated|full>]")
            continue

        elif cmd == "/test":
            print(f"\n🔬 Sending test ping to '{middleware.model_name}' at {middleware.endpoint} ...")
            test_payload = {"model": middleware.model_name, "messages": [{"role": "user", "content": "Say hello in one short sentence."}], "stream": False}
            if middleware.backend != "ollama":
                test_payload["max_tokens"] = 40
            try:
                req = urllib.request.Request(
                    middleware.endpoint,
                    data=json.dumps(test_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer local-lan", "Connection": "close"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=60) as r:
                    print(f"  [✅ RAW RESPONSE]: {r.read().decode('utf-8', errors='ignore')[:300]}")
            except Exception as ex:
                print(f"  [❌ ERROR]: {ex}")
            continue

        elif cmd.startswith("/connect"):
            parts = user_input.split(maxsplit=1)
            middleware.connected = middleware.probe_and_connect(parts[1] if len(parts) > 1 else middleware.base_url, verbose=True)
            middleware._warned_unreachable = False
            continue

        elif cmd == "/models":
            if middleware.probe_and_connect(middleware.base_url, verbose=True):
                for m in middleware.available_models:
                    print(f"  • {m}{' (ACTIVE)' if m == middleware.model_name else ''}")
            continue

        elif cmd.startswith("/model"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                middleware.model_name = middleware.normalize_model_name(parts[1])
                middleware.preferred_model = middleware.model_name
                brain.knowledge_facts["_preferred_model"] = middleware.model_name
                brain.save_memory()
                print(f"[🔄 Switched model to: '{middleware.model_name}' (remembered for next time)]")
            else:
                print(f"Current model: {middleware.model_name}")
            continue

        elif cmd == "/post":
            print("\n🔬 LAST LLM POST-PROCESSOR COHERENCE & TECTONIC REPORT:")
            print(json.dumps(middleware.last_post_audit, indent=2))
            continue

        elif cmd == "/prompt":
            print("\n💉 LAST INJECTED STATE PROMPT:\n" + (last_system_prompt or "(Run a turn first.)"))
            if middleware.last_tone:
                t = middleware.last_tone
                print(f"\n🎚️ Tone sent with it: temperature {t['temperature']} · ~{t['sentences']} sentences"
                      f" · velocity (S,A,Z) {tuple(t['velocity'])}" + (" · memory unsure" if t["unsure"] else ""))
            continue

        elif cmd_word == "/callosum":
            parts = cmd.split()
            if len(parts) == 3 and parts[1] in ("memory", "tone") and parts[2] in ("on", "off"):
                middleware.callosum[parts[1]] = parts[2] == "on"
            elif len(parts) == 2 and parts[1] in ("on", "off"):
                middleware.callosum = {k: parts[1] == "on" for k in middleware.callosum}
            elif len(parts) > 1:
                print("Usage: /callosum  ·  /callosum on|off  ·  /callosum memory on|off  ·  /callosum tone on|off")
                continue
            print(f"[🧬 Callosum · memory (strength labels + careful learning): {'ON' if middleware.callosum['memory'] else 'OFF'}"
                  f" · tone (brain sets temperature + reply length): {'ON' if middleware.callosum['tone'] else 'OFF'}]")
            continue

        elif cmd.startswith("/export"):
            parts = user_input.split(maxsplit=1)
            fname = parts[1].strip() if len(parts) > 1 else "latest_trace.json"
            print(f"💾 Exported 3D 10-step R vs ¬R + LLM Post-Audit trace to: {brain.export_trace_file(fname)}")
            continue

        elif cmd == "/crystals":
            print(f"\n💎 NUCLEATED 4-FACET CRYSTALLINE SUB-LATTICES ({len(brain.crystal_lattices)} Active Crystals):")
            for ck, c_obj in brain.crystal_lattices.items():
                mood = brain.cell_lexicon.get(ck, {}).get("name", "")
                print(f"  💎 Crystal ({ck}) [{mood}] | Pure: {c_obj['total_pure']} | Shear: {c_obj['shear_stress']:.3f}")
                for f_name, f_info in c_obj["facets"].items():
                    print(f"      • {f_name:<12} (tension={f_info['tension']:.2f}): {', '.join(f_info['words'])}")
            continue

        elif cmd == "/ponder":
            for line in (brain.scratchpad or ["(Send a message first.)"]):
                print(f"  • {line}")
            continue

        elif cmd.startswith("/sleep"):
            parts = cmd.split()
            hrs = float(parts[1]) if len(parts) > 1 and parts[1].replace(".", "", 1).isdigit() else 4.0
            for r_line in brain.run_stasis_sleep_pass(hrs):
                print(f"  • {r_line}")
            brain.save_memory()
            continue

        elif cmd == "/wheels":
            brain.training_wheels = not brain.training_wheels
            print(f"[Prompt Mode: {'WHEELS-ON 🛞 (Explicit Scaffolding)' if brain.training_wheels else 'WHEELS-OFF 🚀 (Raw Spatial Telemetry)'}]")
            continue

        elif cmd in ("/emotions", "/lexicon"):
            u_disp = brain.user_profile.get("user_name", "").capitalize() or "User"
            stage_names = {1: "Stage 1: Rough Seed", 2: "Stage 2: Self-Evolved", 3: f"Stage 3: Co-Named w/ {u_disp}"}
            for cell_k, info in brain.cell_lexicon.items():
                if info.get("visits", 0) > 0 or info.get("stage", 1) >= 2:
                    c_mark = " 💎" if cell_k in brain.crystal_lattices else ""
                    words_p = ", ".join(info.get("top_words", [])[:4]) or "seed vector"
                    print(f"  • Cell ({cell_k}){c_mark} : '{info['name']}' [{stage_names.get(info.get('stage', 1))} | visits={info.get('visits', 0)} | {words_p}]")
            continue

        elif cmd == "/think":
            tr = brain.last_thought_trace
            if not tr:
                print("Have a conversation turn first to generate a thought trace.")
                continue
            print(f"  Seed Concepts : {tr.get('seeds')}\n  3D A* Path    : {' -> '.join(tr.get('a_star_path', []))}")
            for s_line in brain.scratchpad:
                print(f"    🔬 {s_line}")
            continue

        elif cmd in ("/telemetry", "/thoughts"):
            show_telemetry = not show_telemetry
            print(f"[📡 Live 3D Telemetry Status Bar is now {'ON' if show_telemetry else 'OFF'}]")
            continue

        elif cmd == "/ideas":
            for p in brain.idea_memory[-20:]:
                orig_tag = "🌙 DREAM" if p.get("origin") == "dream" else "☀️ WAKING"
                print(f"  • [{p['cell']}] ({orig_tag}) {p['summary']}")
            continue

        elif cmd == "/dream":
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            brain.synthesize_emergent_bot_name()
            brain.save_memory()
            continue

        elif cmd == "/nightmare":
            if not hasattr(brain, "nightmare_mode"):
                print("This engine has no nightmare mode (needs torrentengine v22.3 or newer).")
                continue
            brain.nightmare_mode = not brain.nightmare_mode
            brain.save_memory()
            print(f"[🌑 Nightmare mode is now {'ON: the lean-up rules are off for this brain' if brain.nightmare_mode else 'OFF'}]")
            continue

        elif cmd == "/flip":
            brain.governor_mode = "ORIGINAL" if brain.governor_mode == "FLIPPED" else "FLIPPED"
            print(f"[🔄 Governor Vocal Layer is now bound to: {brain.governor_mode}]")
            continue

        elif cmd == "/grid":
            show_grid = not show_grid
            if show_grid and brain.last_audit:
                print("\n" + brain.print_overlay_lattice(brain.last_audit))
            continue

        elif cmd == "/audit":
            if not brain.last_audit:
                print("Run a conversation turn first.")
                continue
            au = brain.last_audit
            print(f"\n📊 3D AUDIT · {au['structuralVerdict']} | t*={au['bifurcationStep']} | Δd={au['meanDeltaD']}u")
            for o, f in zip(au["originalTrajectory"], au["flippedTrajectory"]):
                print(f"  Step {o['stepIndex']}: R=({o['S']},{o['A']},{o['Z']}) vs ¬R=({f['S']},{f['A']},{f['Z']}) | {f['operation']}")
            continue

        elif cmd == "/cells":
            for cell_k, words_map in brain.cortical_cells.items():
                if words_map:
                    top_c = sorted(words_map.items(), key=lambda x: x[1], reverse=True)[:5]
                    mood = brain.cell_lexicon.get(cell_k, {}).get("name", "")
                    print(f"  Cell ({cell_k}) [{mood}] : {', '.join(f'{w}({cnt})' for w, cnt in top_c)}")
            continue

        elif cmd == "/links":
            for w, neighbors in list(brain.assoc_graph.items())[-12:]:
                top_n = sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:4]
                print(f"  {w:>14} <-> {', '.join(f'{k}({v:.2f})' for k, v in top_n)}")
            continue

        elif cmd == "/facts":
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
            brain = ToroidalBrainEngine(glove_file="glove.6B.50d.txt", memory_file=new_file, max_glove_words=glove_limit)
            brain.training_wheels = False
            middleware.brain = brain
            middleware.chat_history = []
            middleware.running_summary = ""
            middleware.episodic_archive = []
            middleware.pinned_notes, middleware.undo_snapshot, middleware.undo_ready = [], None, False
            print("🧠 3D Toroidal Brain wiped and reset.")
            brain.run_boot_calibration_and_handshake()
            continue

        elif cmd.startswith("/") and not cmd.startswith("/listen") and not cmd.startswith("/mic"):
            print("Voice Commands  : /tts, /listen [sec], /voicechat")
            print("Bridge Commands : /memory [compress], /mode <sovereign|attenuated|full>, /test, /connect, /models, /model, /prompt, /post")
            print("Notes & Undo    : /note <key>: <text>, /notes, /notes delete <n>, /recall <word>, /back (undo your last message)")
            print("TORRENT Commands: /wheels, /export, /crystals, /ponder, /sleep, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /nightmare, /exit")
            continue

        # Execute the full 3-stage Brain -> LLM -> Post-Processor turn
        middleware.take_snapshot(user_input)  # for /back
        pre_reply, audit, salient_c = brain.respond(user_input)
        last_system_prompt = middleware.build_state_injection(user_input, pre_reply, audit, salient_c)
        llm_reply = middleware.call_local_llm(last_system_prompt, user_input, fallback_reply=pre_reply)
        post_report = middleware.post_process_llm_response(user_input, llm_reply, audit, salient_c)
        middleware.record_turn_and_maybe_summarize(user_input, llm_reply, audit, salient_c)
        middleware.undo_ready = True

        bot_speaker = brain.user_profile.get("bot_name") or "[Manifold]"
        print(f"\n🤖 {bot_speaker} ({'native' if middleware.last_used_fallback else middleware.model_name}): {llm_reply}")

        if voice_io.tts_enabled:
            voice_io.speak(llm_reply)

        if show_telemetry:
            term_o, term_f = audit["originalTrajectory"][-1], audit["flippedTrajectory"][-1]
            t_act = term_f if brain.governor_mode == "FLIPPED" else term_o
            mood_name = brain.get_cell_emotion_name(t_act["S"], t_act["A"], t_act["Z"])
            print(
                f"   [🧠 Coord: ({t_act['S']},{t_act['A']},{t_act['Z']}) '{mood_name}' | "
                f"Mode: {middleware.voice_mode} | "
                f"Coherence: {post_report['combinedCoherence']:+.2f} | "
                f"Recalled: {len(middleware.last_retrieved_episodes)} ep | "
                f"LLM Wired: {post_report['llmWiredConcepts']}"
                + (f" · held back: {post_report['llmHeldBack']}" if post_report.get("llmHeldBack") else "")
                + (f" | Tone: temp {post_report['tone']['temperature']}, ~{post_report['tone']['sentences']} sentences"
                   + (", unsure" if post_report['tone']['unsure'] else "") if post_report.get("tone") else "")
                + (f" | Sleep: {brain.sleep_pressure_report()['level']}" if hasattr(brain, "sleep_pressure_report") else "")
                + (" | 🌑 nightmare" if getattr(brain, "nightmare_mode", False) else "")
                + "]"
            )
        if show_grid:
            print("\n" + brain.print_overlay_lattice(audit))