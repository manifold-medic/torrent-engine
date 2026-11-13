import copy, datetime, http.server, json, os, random, re, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error, wave
from torrentengine import ToroidalBrainEngine, BRAIN_LIBRARY
try:
    from torrentengine import ENGINE_VERSION
except ImportError:
    ENGINE_VERSION = None  # engine file older than v22.6.1
BRIDGE_VERSION = "24.1.1"
try:
    from torrentengine import run_read_command  # v23.4.1 /read
except ImportError:
    run_read_command = None
try:
    from torrentengine import nightmare_text  # engine v22.3.1+: purple Nightmare text
except ImportError:
    def nightmare_text(text):
        return text


def clock_text(ts=None):
    """v22.10: a short local time like "3:12 PM" (works on Windows, Linux and Android)."""
    return time.strftime("%I:%M %p", time.localtime(ts if ts else time.time())).lstrip("0")

# v23.5.5: voice-to-text often drops the apostrophe in "I'll", so "ill be back" reached the brain as the word "ill"
# (sick). Only "ill" right before a word that follows "I'll" is fixed; "I feel ill" and "an ill wind" stay as they are.
_ILL_NEXT = ("be|do|let|go|try|see|talk|get|come|make|keep|check|tell|take|give|just|probably|still|never|always|"
             "also|definitely|have|bring|send|show|ask|wait|leave|stay|think|write|read|sleep|rest|miss|need")
_ILL_RX = re.compile(r"\bill(?= (?:" + _ILL_NEXT + r")\b)", re.IGNORECASE)

_ILL_ADJ_BEFORE = {"feel", "feels", "felt", "feeling", "am", "is", "was", "were", "are", "been", "be", "get", "got", "getting",
                   "seem", "seems", "seemed", "look", "looks", "fall", "fell", "become", "became", "mentally", "terminally",
                   "critically", "seriously", "an", "remain", "stayed", "im", "i'm"}
_ILL_DEGREE = {"so", "very", "too", "really", "quite", "still", "pretty", "kinda", "a", "bit", "little"}  # v24.1.1: only
# an adjective when a feeling/being word comes before them ("I was so ill") -- "ok so ill be back" is "I'll"


def fix_dropped_apostrophes(text):
    """v24.1: also leaves "ill" alone after a word that makes it the adjective ("I feel ill still", "was ill just")."""
    def fix(m):
        before = re.findall(r"[a-z']+", (text or "")[:m.start()].lower())
        while before and before[-1] in _ILL_DEGREE and len(before) > 1 and before[-2] in _ILL_DEGREE | _ILL_ADJ_BEFORE:
            before = before[:-1]  # "was so really ill" -> look past the degree words
        if before and before[-1] in _ILL_DEGREE and len(before) > 1 and before[-2] in _ILL_ADJ_BEFORE:
            return m.group(0)
        return m.group(0) if before and before[-1] in _ILL_ADJ_BEFORE else "I'll"
    return _ILL_RX.sub(fix, text or "")

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

    # v23.4.1 voice fixes: Piper found without PATH, the voice in use (and why Piper was skipped) said once, Whisper
    # given the audio as numbers (no temp WAV, so PyAV isn't needed), silence and Whisper's silence phantoms dropped.
    SILENCE_RMS = float(os.environ.get("TORRENT_MIC_SILENCE", "0.004"))  # below this the recording is treated as silence
    QUIET_RMS = 0.02             # a recording this quiet that comes back as a stock phrase is a phantom
    PHANTOMS = {"thank you", "thanks", "thank you very much", "thanks for watching", "thank you for watching",
                "you", "bye", "bye bye", "so", "okay", "ok", "uh", "um", "hmm", "oh", "the end", "subtitles by"}
    EXIT_PHRASES = ("stop voice chat", "end voice chat", "exit voice chat", "quit voice chat", "stop voice mode",
                    "leave voice chat", "stop the voice chat")

    def __init__(self, is_mobile: bool = False):
        self.is_mobile = is_mobile
        self.tts_enabled = False
        self.whisper_model = None
        self.whisper_size = os.environ.get("TORRENT_WHISPER_MODEL", "base.en")
        self.piper_model_path = os.environ.get("TORRENT_PIPER_MODEL", "")
        self.pyttsx_engine = None
        self.voice_reported = False   # v23.4.1: which voice is speaking is said once per session
        self.piper_failed = ""        # v23.4.1: after a Piper error, skip it for the rest of the session (and say why)
        self.last_listen_note = ""    # v23.4.1: why the last recording gave no text (shown with "No speech detected")

    @staticmethod
    def _norm(text):
        return " ".join(re.sub(r"[^a-z' ]+", " ", (text or "").lower()).split())

    def is_exit_phrase(self, text):
        """v23.4.1: "stop voice chat" (and similar) said aloud leaves the voice chat loop."""
        t = self._norm(text)
        return any(p in t for p in self.EXIT_PHRASES)

    def _piper_command(self):
        """v23.4.1: the 'piper' program if it's on PATH, else this Python's piper module (no PATH setup needed)."""
        if shutil.which("piper"):
            return ["piper"]
        try:
            import importlib.util
            if importlib.util.find_spec("piper") is not None:
                return [sys.executable, "-m", "piper"]
        except (ImportError, ValueError):
            pass
        return None

    def _report_voice(self, name, piper_why=""):
        if self.voice_reported:
            return
        self.voice_reported = True
        print(f"  [🔊 Voice: {name}" + (f" · Piper not used: {piper_why}" if piper_why else "") + "]")

    def speak(self, text: str):
        if not self.tts_enabled or not text:
            return
        clean_speech = re.sub(r"[*_`#~>\[\]]", "", text).strip()
        if not clean_speech:
            return

        # 1. Piper, if a .onnx voice is set and the piper program or module can be found
        piper_why = self.piper_failed
        if not piper_why:
            cmd = self._piper_command()
            if not self.piper_model_path:
                piper_why = "TORRENT_PIPER_MODEL isn't set"
            elif not os.path.isfile(self.piper_model_path):
                piper_why = f"the model file wasn't found ({self.piper_model_path})"
            elif not cmd:
                piper_why = "piper wasn't found (pip install piper-tts)"
            else:
                wav_path = ""
                try:
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                        wav_path = tf.name
                    proc = subprocess.run(cmd + ["--model", self.piper_model_path, "--output_file", wav_path],
                                          input=clean_speech.encode("utf-8"), stdout=subprocess.DEVNULL,
                                          stderr=subprocess.PIPE, timeout=60)
                    played = False
                    if proc.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 44:
                        played = self._play_wav(wav_path)
                        if played:
                            self._report_voice(f"Piper ({os.path.basename(self.piper_model_path)}"
                                               + (", run as a Python module" if cmd[0] != "piper" else "") + ")")
                            return
                        self.piper_failed = piper_why = "no program to play Piper's sound (install aplay or paplay)"
                    if not played and not self.piper_failed:
                        err = (proc.stderr or b"").decode("utf-8", errors="replace").strip().splitlines()
                        self.piper_failed = piper_why = f"piper error (code {proc.returncode}): {err[-1][:160] if err else 'no message'}"
                except Exception as e:
                    self.piper_failed = piper_why = f"piper error: {e}"
                finally:
                    if wav_path and os.path.exists(wav_path):
                        try:
                            os.remove(wav_path)
                        except OSError:
                            pass

        # 2. Try pyttsx3 if installed
        try:
            import pyttsx3
            if self.pyttsx_engine is None:
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty("rate", 175)
            self._report_voice("pyttsx3", piper_why)
            self.pyttsx_engine.say(clean_speech)
            self.pyttsx_engine.runAndWait()
            return
        except Exception:
            pass

        # 3. Zero-Dependency OS Native Offline TTS Fallbacks
        try:
            if os.name == "nt":
                self._report_voice("Windows voice (System.Speech)", piper_why)
                safe_t = clean_speech.replace("'", "''").replace('"', " ")
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_t}')"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform == "darwin":
                self._report_voice("macOS say", piper_why)
                subprocess.run(["say", clean_speech])
            elif shutil.which("termux-tts-speak"):
                self._report_voice("Android (termux-tts-speak)", piper_why)
                subprocess.run(["termux-tts-speak", clean_speech])
            elif shutil.which("espeak-ng"):
                self._report_voice("espeak-ng", piper_why)
                subprocess.run(["espeak-ng", clean_speech])
            elif shutil.which("espeak"):
                self._report_voice("espeak", piper_why)
                subprocess.run(["espeak", clean_speech])
            else:
                self._report_voice("none found (no speech)", piper_why)
        except Exception as e:
            print(f"  [!] TTS playback error: {e}")

    def _play_wav(self, wav_path: str) -> bool:
        """Plays a WAV file; False when this computer has no player for it (v24.1: the caller then tries another voice)."""
        if os.name == "nt":
            import winsound
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        elif sys.platform == "darwin":
            subprocess.run(["afplay", wav_path])
        elif shutil.which("aplay"):
            subprocess.run(["aplay", "-q", wav_path])
        elif shutil.which("paplay"):
            subprocess.run(["paplay", wav_path])
        else:
            return False
        return True

    def listen_and_transcribe(self, duration_sec: int = 5) -> str:
        """Record and transcribe. Returns "" when nothing was said (and sets last_listen_note to why). Ctrl+C while
        recording is passed up to the caller (voice chat turns it into "back to text")."""
        self.last_listen_note = ""
        # 1. Android Termux API fallback if available
        if self.is_mobile and shutil.which("termux-speech-to-text"):
            try:
                print(f"🎙️ Listening via Android Speech-to-Text...")
                res = subprocess.check_output(["termux-speech-to-text"], timeout=20)
                return res.decode("utf-8", errors="ignore").strip()
            except subprocess.TimeoutExpired:
                self.last_listen_note = "Android speech-to-text timed out"
                return ""
            except Exception as e:
                print(f"  [!] Termux STT error: {e}")
                return ""

        # 2. Offline faster-whisper + sounddevice on PC/Laptop
        try:
            import sounddevice as sd
            import numpy as np
        except Exception as e:  # v24.1.1: on Linux without PortAudio the import raises OSError, not ImportError
            if not isinstance(e, ImportError):
                self.last_listen_note = f"the microphone library couldn't start ({e})"
                print(f"\n[!] The microphone library couldn't start: {e}")
                return ""
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
        try:
            audio_data = sd.rec(int(duration_sec * samplerate), samplerate=samplerate, channels=1, dtype="int16")
            sd.wait()
        except KeyboardInterrupt:
            raise
        except Exception as e:  # v24.1.1: a recording error used to stop the bridge
            self.last_listen_note = f"recording failed ({e})"
            return ""
        # v23.4.1: Whisper gets the audio as numbers (mono, float32, 16 kHz), so PyAV (av) isn't used at all
        audio = np.asarray(audio_data, dtype=np.float32).reshape(-1) / 32768.0
        level = float(np.sqrt(np.mean(audio * audio))) if audio.size else 0.0
        if level < self.SILENCE_RMS:
            self.last_listen_note = f"mic level {level:.4f}, below the silence line {self.SILENCE_RMS} (TORRENT_MIC_SILENCE)"
            return ""
        print("⚡ Transcribing audio locally...")
        segments, _ = self.whisper_model.transcribe(audio, beam_size=3, vad_filter=True)
        kept = [seg.text.strip() for seg in segments if getattr(seg, "no_speech_prob", 0.0) < 0.6]
        transcript = " ".join(t for t in kept if t).strip()
        if not self._norm(transcript):
            self.last_listen_note = "no speech found in the recording"
            return ""
        if level < self.QUIET_RMS and self._norm(transcript) in self.PHANTOMS:
            self.last_listen_note = f"'{transcript}' from a very quiet recording (Whisper invents that from silence)"
            return ""
        return transcript


# =============================================================================
# v23.3.4 FACE VISUALIZER: a small live page that draws the brain's four levels as a face (beside the terminal).
# A picture of the numbers, not a claim about feelings. Python's built-in web server, nothing to install.
# /face starts it (and remembers it per brain); /face off stops it. TORRENT_FACE_PORT (8765), TORRENT_FACE_HOST
# (127.0.0.1 = this device only; 0.0.0.0 lets another device on your network open it, and see the last reply).
# =============================================================================
FACE_PAGE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>T.O.R.R.E.N.T. face</title>
<style>
:root{--bg:#141519;--panel:#1c1e24;--ink:#e7e7ec;--dim:#9a9cab;--line:#2b2e37}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;display:flex;justify-content:center}
main{width:100%;max-width:440px;padding:14px 14px 20px}
h1{font-size:19px;margin:2px 0 0;font-weight:650}
.sub{color:var(--dim);font-size:12.5px;margin:2px 0 6px;min-height:18px}
svg{width:100%;height:auto;display:block}
.bars{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:6px 12px;margin-top:4px}
.row{display:grid;grid-template-columns:112px 1fr 50px;align-items:center;gap:10px;margin:8px 0}
.lab{font-size:13.5px}.lab small{display:block;color:var(--dim);font-size:11px}
.track{position:relative;height:9px;background:#2a2d36;border-radius:5px;overflow:hidden}
.fill{position:absolute;top:0;bottom:0;border-radius:5px;transition:left .5s,width .5s,background .5s}
.mid{position:absolute;left:50%;top:0;bottom:0;width:1px;background:#5a5f6e}
.num{text-align:right;font-variant-numeric:tabular-nums;font-size:13.5px}
.meta{color:var(--dim);font-size:12.5px;margin-top:10px}
.meta b{color:var(--ink);font-weight:600}
.said{margin-top:8px;font-size:13px;color:#c9cad3;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 10px;display:none}
.said span{color:var(--dim)}
.foot{color:#70737f;font-size:11px;margin-top:12px}
.chat{margin-top:10px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:8px 10px;display:none}
#log{max-height:280px;overflow-y:auto;font-size:13.5px}
.m{margin:6px 0;padding:6px 9px;border-radius:10px;max-width:88%;white-space:pre-wrap;word-wrap:break-word}
.m small{display:block;color:var(--dim);font-size:10.5px;margin-bottom:1px}
.m.you{background:#2f3a52;margin-left:auto}.m.bot{background:#2a2d36}.m.spoke{background:#3a3150}
#cf{display:flex;gap:6px;margin-top:8px}
#ci{flex:1;min-width:0;background:#111216;color:var(--ink);border:1px solid var(--line);border-radius:9px;padding:9px 10px;font:inherit}
#cf button{background:#3b4a6b;color:var(--ink);border:0;border-radius:9px;padding:0 14px;font:inherit}
.cm{color:var(--dim);font-size:11.5px;min-height:15px;margin-top:4px}
</style></head><body><main>
<h1 id="name">T.O.R.R.E.N.T.</h1>
<div class="sub" id="status">connecting to the bridge&hellip;</div>
<svg viewBox="0 0 400 350" role="img" aria-label="a face drawn from the brain's four levels">
 <defs>
  <clipPath id="clipL"><ellipse id="cL" cx="145" cy="172" rx="32" ry="30"/></clipPath>
  <clipPath id="clipR"><ellipse id="cR" cx="255" cy="172" rx="32" ry="30"/></clipPath>
  <radialGradient id="shade" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity=".24"/><stop offset="1" stop-color="#000" stop-opacity=".14"/></radialGradient>
 </defs>
 <g id="head">
  <circle id="skin" cx="200" cy="185" r="148" fill="#b9b3cf"/>
  <circle cx="200" cy="185" r="148" fill="url(#shade)"/>
  <ellipse id="blushL" cx="110" cy="228" rx="22" ry="12" fill="#ff7d8c" opacity="0"/>
  <ellipse id="blushR" cx="290" cy="228" rx="22" ry="12" fill="#ff7d8c" opacity="0"/>
  <ellipse id="eL" cx="145" cy="172" rx="32" ry="30" fill="#fbfbfd"/>
  <ellipse id="eR" cx="255" cy="172" rx="32" ry="30" fill="#fbfbfd"/>
  <g id="gL" clip-path="url(#clipL)"><circle id="pL" cx="145" cy="175" r="13" fill="#23242b"/><circle id="hL" cx="151" cy="169" r="4.5" fill="#fff"/></g>
  <g id="gR" clip-path="url(#clipR)"><circle id="pR" cx="255" cy="175" r="13" fill="#23242b"/><circle id="hR" cx="261" cy="169" r="4.5" fill="#fff"/></g>
  <path id="lidL" d="M115,172 Q145,184 175,172" fill="none" stroke="#2b2c33" stroke-width="5" stroke-linecap="round" opacity="0"/>
  <path id="lidR" d="M225,172 Q255,184 285,172" fill="none" stroke="#2b2c33" stroke-width="5" stroke-linecap="round" opacity="0"/>
  <path id="bL" fill="none" stroke="#2b2c33" stroke-width="7" stroke-linecap="round"/>
  <path id="bR" fill="none" stroke="#2b2c33" stroke-width="7" stroke-linecap="round"/>
  <path id="mouth" fill="#43303a" stroke="#2b2c33" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
 </g>
 <g id="zz" opacity="0" font-family="system-ui,sans-serif" font-weight="700" fill="#cfd4ff">
  <text x="300" y="78" font-size="28">z</text><text x="324" y="52" font-size="21">z</text><text x="343" y="31" font-size="15">z</text></g>
 <g id="dots" opacity="0" fill="#e7e7ec"><circle id="d1" cx="318" cy="58" r="6"/><circle id="d2" cx="341" cy="49" r="7"/><circle id="d3" cx="366" cy="38" r="8"/></g>
</svg>
<div class="bars">
 <div class="row"><div class="lab">Wound up<small>arousal &#9889;</small></div><div class="track"><div class="fill" id="fA" style="left:0;background:#e8875c"></div></div><div class="num" id="nA">&ndash;</div></div>
 <div class="row"><div class="lab">Mood<small>valence &#9775; (vs usual)</small></div><div class="track"><div class="mid"></div><div class="fill" id="fV"></div></div><div class="num" id="nV">&ndash;</div></div>
 <div class="row"><div class="lab">Newness<small>novelty &#10024;</small></div><div class="track"><div class="fill" id="fN" style="left:0;background:#9b8cf0"></div></div><div class="num" id="nN">&ndash;</div></div>
 <div class="row"><div class="lab">Tiredness<small id="sLab">sleep pressure &#128164;</small></div><div class="track"><div class="fill" id="fS" style="left:0;background:#7fb0a3"></div></div><div class="num" id="nS">&ndash;</div></div>
 <div class="row" id="tRow" style="display:none"><div class="lab">Their tone<small id="tLab">last message (experimental)</small></div><div class="track"><div class="mid"></div><div class="fill" id="fT"></div></div><div class="num" id="nT">&ndash;</div></div>
</div>
<div class="meta" id="meta"></div>
<div class="said" id="said"></div>
<div class="chat" id="chat"><div id="log"></div><form id="cf"><input id="ci" autocomplete="off" placeholder="Say something&hellip;"><button>Send</button></form><div class="cm" id="cm"></div></div>
<div class="foot">A visualizer: the engine's four levels drawn as a face. Mouth and colour = mood, eyes open and brows up = wound up,
heavy lids = tiredness, big bright pupils that look around = newness. It shows the numbers; it isn't a claim about feelings.</div>
</main>
<script>
const $=id=>document.getElementById(id);
const lerp=(a,b,t)=>a+(b-a)*t, clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
let target={a:0,v:0,n:.5,s:0}, cur={a:0,v:0,n:.5,s:0}, mode="starting", connected=false, everConnected=false;
let blinkUntil=0, nextBlink=performance.now()+2500, look={x:0,y:0}, lookT={x:0,y:0}, nextLook=0;
const DOWN=[118,146,204], MID=[180,174,202], UP=[244,197,118];
function mix(c1,c2,t){return c1.map((x,i)=>lerp(x,c2[i],t))}
function skin(v,a){let c=v<0?mix(MID,DOWN,-v):mix(MID,UP,v);const g=(c[0]+c[1]+c[2])/3;
  c=c.map(x=>Math.round(clamp(g+(x-g)*(1+.7*a),0,255)));return `rgb(${c.join(",")})`}
function txt(id,s){$(id).textContent=s}
function bar(id,v,lo,hi){const f=$(id);if(lo<0){const p=clamp(v,-1,1)*50;f.style.left=(p<0?50+p:50)+"%";f.style.width=Math.abs(p)+"%";
  f.style.background=v<0?"#7896cd":"#f2c478"}else{f.style.left="0";f.style.width=clamp(v,0,1)*100+"%"}}
function apply(d){
  mode=d.mode||"awake"; const L=d.levels; doing=(d.idle&&d.idle.doing)||"";
  if(L){target={a:L.arousal,v:L.valence,n:L.novelty,s:L.sleep}}else{target={a:0,v:0,n:.5,s:0}}
  txt("name",(d.name||"Brain")+" · face");
  const fmt=(x,sg)=>(sg&&x>=0?"+":"")+x.toFixed(2);
  if(L){bar("fA",L.arousal,0,1);bar("fV",L.valence,-1,1);bar("fN",L.novelty,0,1);bar("fS",L.sleep,0,1);
    txt("nA",fmt(L.arousal));txt("nV",fmt(L.valence,1));txt("nN",fmt(L.novelty));txt("nS",fmt(L.sleep))}
  else{["nA","nV","nN","nS"].forEach(i=>txt(i,"off"))}
  if(d.tone!==null&&d.tone!==undefined){$("tRow").style.display="grid";bar("fT",d.tone/0.4,-1,1);txt("nT",fmt(d.tone,1));
    txt("tLab",(d.tone_word||"")+" \u00b7 last message (experimental)")}
  txt("sLab","sleep pressure 💤"+(d.sleep_level?" · "+d.sleep_level:""));
  const words={thinking:"thinking…",speaking:"speaking",asleep:"asleep",awake:"awake",listening:"listening",reading:"reading",idle:"on its own"};
  const doingW={wander:"wandering",leap:"leaping",replay:"thinking back",doze:"dozing",rest:"resting",asleep:"asleep (live)",settling:"settling",speak:"spoke up"};
  let st=words[mode]||mode;
  if(d.idle){st=(doingW[d.idle.doing]||d.idle.doing)+(d.idle.word&&["wander","leap","replay"].includes(d.idle.doing)?" · "+d.idle.word:"")+" · "+Math.round(d.idle.minutes)+" min on its own"}
  txt("status",st+(L?"":" · levels are off (/levels)")+(d.version?" · engine v"+d.version:""));
  const m=$("meta");m.textContent="";
  const add=(t,b)=>{const e=document.createElement(b?"b":"span");e.textContent=t;m.appendChild(e)};
  if(d.speaker){add("Talking with ");add(d.speaker,1);add(" · ")}
  if(d.cell){add("at ("+d.cell.join(",")+") ");add(d.cell_name||"",1)}
  if(d.governor)add(" · "+d.governor);if(d.nightmare)add(" · nightmare mode");
  const s=$("said");if(d.reply){s.style.display="block";s.textContent="";const sp=document.createElement("span");
    sp.textContent="Last reply: ";s.appendChild(sp);s.appendChild(document.createTextNode(d.reply))}else s.style.display="none";
  if(d.chat_on){$("chat").style.display="block";s.style.display="none";botName=d.name||"Brain";chatPw=d.chat_pw;renderChat(d.chat||[],d.chat_busy)}
}
let lastKey="", botName="Brain", chatPw=false, pw="", doing="";
function renderChat(c,busy){const last=c[c.length-1]||{};const key=c.length+"|"+(last.t||"")+"|"+(last.text||"").length+"|"+busy;
  if(key===lastKey)return;lastKey=key;const L=$("log");const atEnd=L.scrollTop+L.clientHeight>=L.scrollHeight-30;L.textContent="";
  for(const m of c){const e=document.createElement("div");e.className="m "+m.who;const w=document.createElement("small");
    w.textContent=m.who==="you"?"You":m.who==="spoke"?botName+" (spoke up)":botName;e.appendChild(w);
    e.appendChild(document.createTextNode(m.text));L.appendChild(e)}
  if(busy){const e=document.createElement("div");e.className="m bot";e.textContent=botName+" is thinking\u2026";L.appendChild(e)}
  if(atEnd)L.scrollTop=L.scrollHeight}
$("cf").addEventListener("submit",async ev=>{ev.preventDefault();const text=$("ci").value.trim();if(!text)return;
  if(chatPw&&!pw)pw=prompt("Password for chatting from this page (TORRENT_FACE_PASSWORD):")||"";
  try{const r=await fetch("say",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text,password:pw})});
    const j=await r.json();$("cm").textContent=j.ok?"":j.msg;if(j.ok)$("ci").value="";else if(r.status===403)pw=""}
  catch(e){$("cm").textContent="Couldn't reach the bridge."}});
async function poll(){
  try{const r=await fetch("state",{cache:"no-store"});apply(await r.json());connected=true;everConnected=true}
  catch(e){connected=false;txt("status",mode==="asleep"?"asleep · the bridge has closed":
     (everConnected?"the bridge has closed":"can't reach the bridge: start it, then type /face"))}
  setTimeout(poll,700)}
function frame(t){
  for(const k in cur)cur[k]=lerp(cur[k],target[k],.06);
  const {a,v,n,s}=cur, off=!connected, asleep=mode==="asleep";
  const period=5200-3200*a, br=1+.013*Math.sin(t/period*2*Math.PI)*(off&&!asleep?.3:1);
  $("head").setAttribute("transform",`translate(200 185) scale(${br.toFixed(4)}) translate(-200 -185)`);
  $("skin").setAttribute("fill",off&&!asleep?"rgb(118,120,130)":skin(v,a));
  let open=clamp(.95-.7*s+.28*a,.14,1.15);
  const dozing=mode==="idle"&&doing==="doze", resting=mode==="idle"&&doing==="rest";  // v23.5.5: idle choices on the face
  if(dozing)open=.04+.16*Math.max(0,Math.sin(t/2600))**6;  // eyes closed, now and then a sleepy peek
  else if(resting)open*=.7;                                  // heavier lids while resting awake
  if(asleep)open=.03;else if(off)open=.3;
  if(t>nextBlink){blinkUntil=t+130+450*s;nextBlink=t+(2200+4300*Math.random())*(1-.35*a)}
  if(t<blinkUntil&&!asleep&&!dozing)open=Math.min(open,.05);
  const ry=30*open, shut=ry<2.4;
  for(const [e,c,l,g] of [["eL","cL","lidL","gL"],["eR","cR","lidR","gR"]]){$(e).setAttribute("ry",ry.toFixed(2));$(c).setAttribute("ry",ry.toFixed(2));
    $(e).setAttribute("opacity",shut?0:1);$(g).setAttribute("opacity",shut?0:1);$(l).setAttribute("opacity",shut?1:0)}
  if(t>nextLook){const r=.35+n;lookT={x:(Math.random()-.5)*18*r,y:(Math.random()-.5)*8*r};
    if(mode==="idle"&&doing==="replay")lookT={x:-7-4*Math.random(),y:-6};          // thinking back: eyes up and to the side
    else if(mode==="idle"&&doing==="leap")lookT={x:(Math.random()<.5?-1:1)*11,y:-2};  // a leap: a quick glance away
    nextLook=t+(3800-2800*n)*(.6+.8*Math.random())*(mode==="idle"&&doing!=="rest"?.6:1)}
  look.x=lerp(look.x,lookT.x,.12);look.y=lerp(look.y,lookT.y,.12);
  const pr=9+6*n+3*a;
  [["pL","hL",145],["pR","hR",255]].forEach(([p,h,x])=>{$(p).setAttribute("cx",x+look.x);$(p).setAttribute("cy",175+look.y);$(p).setAttribute("r",pr);
    $(h).setAttribute("cx",x+6+look.x*.9);$(h).setAttribute("cy",169+look.y*.9);$(h).setAttribute("r",2.5+3*n);$(h).setAttribute("opacity",.3+.7*n)});
  const by=134-15*a+11*s, lift=17*Math.max(0,-v)*(.35+a), arch=7*Math.max(0,v);
  $("bL").setAttribute("d",`M112,${by} Q140,${by-6-arch} 172,${by-lift}`);
  $("bR").setAttribute("d",`M288,${by} Q260,${by-6-arch} 228,${by-lift}`);
  const talk=mode==="speaking"?(.5+.5*Math.sin(t/85))*13:0;
  const y0=258, uy=y0+50*v*(asleep?.3:1), ly=uy+Math.max(0,28*(a-.22))+talk, w=50+10*Math.max(0,v)-10*s;
  $("mouth").setAttribute("d",`M${200-w},${y0} Q200,${uy} ${200+w},${y0} Q200,${ly} ${200-w},${y0} Z`);
  const blush=off?0:clamp(v-.25,0,.75)*.9;$("blushL").setAttribute("opacity",blush);$("blushR").setAttribute("opacity",blush);
  const z=$("zz");z.setAttribute("opacity",asleep?.65+.35*Math.sin(t/650):dozing?.25+.15*Math.sin(t/900):(!off&&s>=.75?.3:0));
  z.setAttribute("transform",`translate(0 ${(3*Math.sin(t/900)).toFixed(2)})`);
  const thinking=mode==="thinking";$("dots").setAttribute("opacity",thinking?1:0);
  if(thinking)["d1","d2","d3"].forEach((id,i)=>$(id).setAttribute("opacity",.35+.65*Math.max(0,Math.sin(t/260-i*.9))));
  requestAnimationFrame(frame)}
poll();requestAnimationFrame(frame);
</script></body></html>"""


class FaceWindow:
    """v23.3.4: the face visualizer's tiny web server (a daemon thread, so it never holds up the chat or the exit).
    update() is called by the chat loop at each change (turn, thinking, speaking, sleep); the page asks for /state
    every 0.7 s. Nothing here touches the brain: it only reads its front doors (levels, position, names)."""

    def __init__(self):
        self.server, self.url = None, ""
        self.lock = threading.Lock()
        self.state = {"mode": "starting"}
        # v23.5.4 chat from the face page: messages go into a queue; one worker thread runs each as a normal turn
        # (run_chat_turn, under BRAIN_LOCK). Only on this device unless TORRENT_FACE_PASSWORD is set.
        self.chat_log, self.chat_runner, self.chat_busy = [], None, False
        self.chat_queue, self.chat_worker, self.host = None, None, "127.0.0.1"

    def chat_allowed(self, given=""):
        pw = os.environ.get("TORRENT_FACE_PASSWORD", "")
        local = self.host in ("127.0.0.1", "localhost", "::1")
        return bool(self.chat_runner is not None and ((local and not pw) or (pw and given == pw)))

    def chat_add(self, who, text):
        """who: "you", "bot" (a reply) or "spoke" (it spoke up first). Never raises."""
        try:
            if text:
                with self.lock:
                    self.chat_log = (self.chat_log + [{"who": who, "text": cut_at_word(str(text), 1200), "t": round(time.time())}])[-40:]
                    self.state = dict(self.state, chat=list(self.chat_log))
        except Exception:
            pass

    def _chat_loop(self):
        while True:
            text = self.chat_queue.get()
            self.chat_busy = True
            try:
                with self.lock:
                    self.state = dict(self.state, chat_busy=True)
                with BRAIN_LOCK:  # waits for a turn typed in the terminal, and the live clock waits for this one
                    print(f"\n👤 (from the face page): {text}")
                    self.chat_runner(text)
                print(LIVE.prompt_text, end="", flush=True)
            except Exception as e:
                print(f"\n[🙂 face page message not handled: {e}]")
                self.chat_add("bot", f"(not handled: {e})")
            finally:
                self.chat_busy = False
                with self.lock:
                    self.state = dict(self.state, chat_busy=False)

    def start(self, port=None, host=None):
        if self.server:
            return self.url
        host = host or os.environ.get("TORRENT_FACE_HOST", "127.0.0.1").strip() or "127.0.0.1"
        try:
            port = int(port or os.environ.get("TORRENT_FACE_PORT", "8765"))
        except ValueError:
            port = 8765
        face = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                path = self.path.split("?")[0]
                if path == "/state":
                    with face.lock:
                        body, ctype = json.dumps(face.state).encode("utf-8"), "application/json"
                elif path in ("/", "/index.html"):
                    body, ctype = FACE_PAGE.encode("utf-8"), "text/html; charset=utf-8"
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):  # v23.5.4: a chat message from the page
                if self.path.split("?")[0] != "/say":
                    self.send_error(404)
                    return
                try:
                    n = min(int(self.headers.get("Content-Length", 0)), 20000)
                    data = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
                except (ValueError, UnicodeDecodeError):
                    data = {}
                text = str(data.get("text", "")).strip()[:2000]
                # v24.1: only the face page itself may post: JSON only (a browser can't send that from another site
                # without asking first, and this server never says yes) and, when the browser says where it came from,
                # it must be this page
                origin = self.headers.get("Origin", "")
                host_hdr = self.headers.get("Host", "")
                same_page = not origin or origin.split("//")[-1] == host_hdr
                if face.host in ("127.0.0.1", "localhost", "::1") and not os.environ.get("TORRENT_FACE_PASSWORD", ""):
                    # v24.1.1: on this device only, the page must also be asked for by a local name (DNS rebinding)
                    same_page = same_page and host_hdr.rsplit(":", 1)[0].strip("[]") in ("127.0.0.1", "localhost", "::1")
                if "application/json" not in self.headers.get("Content-Type", "") or not same_page:
                    code, msg = 403, "Only the face page itself can send messages."
                elif not face.chat_allowed(str(data.get("password", ""))):
                    code, msg = 403, "Chat from the page is off here (other devices need TORRENT_FACE_PASSWORD)."
                elif not text:
                    code, msg = 400, "Nothing to send."
                elif text.startswith("/"):
                    code, msg = 400, "Commands work in the terminal; the page is for chatting."
                else:
                    face.chat_queue.put(text)
                    code, msg = 200, "ok"
                body = json.dumps({"ok": code == 200, "msg": msg}).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):  # keep the terminal clean
                pass

        self.host = host
        if self.chat_queue is None:
            import queue
            self.chat_queue = queue.Queue()
            self.chat_worker = threading.Thread(target=self._chat_loop, daemon=True)
            self.chat_worker.start()
        for p in range(port, port + 10):  # if the port is busy (another bridge running), try the next ones
            try:
                srv = http.server.ThreadingHTTPServer((host, p), Handler)
                srv.daemon_threads = True
                self.server = srv
                break
            except OSError:
                continue
        if not self.server:
            return ""
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        shown = "127.0.0.1" if host in ("0.0.0.0", "") else host
        self.url = f"http://{shown}:{self.server.server_address[1]}/"
        return self.url

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
        self.server, self.url = None, ""

    def update(self, brain, mode="awake", reply=None, heard=None, idle=None):
        """Refresh what the page shows. Never raises: the visualizer must not break a turn."""
        if not self.server:
            return
        try:
            lv = brain.levels() if hasattr(brain, "levels") else None
            sp = brain.sleep_pressure_report() if hasattr(brain, "sleep_pressure_report") else {}
            s, a, z = brain.seed_s, brain.seed_a, brain.seed_z
            who = brain.speaker_name() if hasattr(brain, "speaker_name") else brain.user_profile.get("user_name", "")
            new = {
                "name": brain.user_profile.get("bot_name") or "Manifold",
                "version": ENGINE_VERSION or "",
                "mode": mode,
                "levels": lv,
                "sleep_level": sp.get("level", ""),
                "cell": [s, a, z],
                "cell_name": brain.get_cell_emotion_name(s, a, z),
                "speaker": (who or "").capitalize(),
                "governor": getattr(brain, "governor_mode", ""),
                "nightmare": bool(getattr(brain, "nightmare_mode", False)),
                "tone": getattr(brain, "last_tone", None),  # v23.4.1 (experimental, measured only)
                "tone_word": brain.tone_word(brain.last_tone) if hasattr(brain, "tone_word") else "",
                "t": time.time(),
                "idle": idle,  # v23.5 live idle: what the brain is doing on its own (None between)
                "chat_on": self.chat_allowed() or bool(os.environ.get("TORRENT_FACE_PASSWORD", "") and self.chat_runner),
                "chat_pw": bool(os.environ.get("TORRENT_FACE_PASSWORD", "")),
            }
            with self.lock:
                new["reply"] = cut_at_word(reply, 400) if reply else self.state.get("reply", "")
                new["heard"] = cut_at_word(heard, 200) if heard else self.state.get("heard", "")
                new["chat"], new["chat_busy"] = list(self.chat_log), self.chat_busy
                self.state = new
        except Exception:
            pass

    def open_in_browser(self, is_mobile):
        if not self.url:
            return False
        try:
            if is_mobile and shutil.which("termux-open-url"):
                subprocess.Popen(["termux-open-url", self.url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            import webbrowser
            return bool(webbrowser.open(self.url))
        except Exception:
            return False


FACE = FaceWindow()

# v23.5 live idle. The chat loop holds BRAIN_LOCK while it handles anything you typed; the clock only ticks when it can
# take the lock without waiting, so the two never touch the brain at the same time (a tick during a turn is skipped).
BRAIN_LOCK = threading.Lock()
# v24.1: one model request at a time. A speak-up is worded on its own thread (outside BRAIN_LOCK, on purpose); it shares
# the bridge's request fields (finish reason, thinking count) and the chat history with a normal turn, so the two take
# turns: a message sent while a speak-up is being worded waits a moment for it.
VOICE_LOCK = threading.RLock()


class LiveClock:
    """v23.5: a background clock (daemon thread) that lets the brain spend a silence while it happens. Every
    TORRENT_LIVE_TICK seconds (default 20) it calls brain.live_tick() and shows the result on the face. It never prints
    (that would break the line you're typing); the usual idle line after your next message tells the whole silence."""

    def __init__(self):
        self.brain, self.thread, self.running = None, None, False
        self.middleware, self.voice, self.prompt_text = None, None, ""  # v23.5.3 speaking up
        self.spoke = 0
        self.ticks = self.skipped = self.choices = 0
        self.doing, self.worst_ms = None, 0.0
        try:
            self.every = max(1.0, float(os.environ.get("TORRENT_LIVE_TICK", "20")))
        except ValueError:
            self.every = 20.0

    def start(self, brain, middleware=None, voice=None):
        self.brain, self.running = brain, True
        if middleware is not None:
            self.middleware, self.voice = middleware, voice
        if not (self.thread and self.thread.is_alive()):
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            time.sleep(self.every)
            if self.running:
                self.tick()

    def tick(self):
        if not BRAIN_LOCK.acquire(blocking=False):
            self.skipped += 1  # a turn is being handled: skip this tick
            return None
        packets = []
        try:
            t0 = time.perf_counter()
            info = self.brain.live_tick()
            packets = self.brain.speak_take() if hasattr(self.brain, "speak_take") else []
            self.worst_ms = max(self.worst_ms, (time.perf_counter() - t0) * 1000)
            self.ticks += 1
            self.doing = info
            if info:
                self.choices += len(info.get("new") or [])
                FACE.update(self.brain, mode="asleep" if info["doing"] == "asleep" else "idle", idle=info)
        except Exception as e:  # the clock must never take the chat down
            self.doing = {"doing": f"error: {e}"}
            info = None
        finally:
            BRAIN_LOCK.release()
        for pk in packets:  # v23.5.3: voiced OUTSIDE the lock, on its own thread (a slow model never freezes the brain)
            threading.Thread(target=self.voice_packet, args=(pk,), daemon=True).start()
        return info

    def voice_packet(self, pk):
        """v23.5.3: put a speak-up packet into words (or say plainly what it wanted to say, with no voice connected) and
        show it: terminal, face, speech, optional phone notification. Never raises."""
        try:
            mw, brain = self.middleware, self.brain
            bot = (brain.user_profile.get("bot_name") or "Manifold") if brain else "Manifold"
            line, flagged = None, []
            if mw is not None and getattr(mw, "connected", False):
                line, flagged = mw.spontaneous_line(pk)
            if not line:
                desc = TorrentLLMMiddleware.packet_description(pk) if mw is None else mw.packet_description(pk)
                print(f"\n💬 {bot} wanted to tell you: {desc}  (no voice connected)")
            else:
                FACE.chat_add("spoke", line)  # v23.5.4
                print(f"\n💬 {bot} (spoke up): {line}" + (f"\n   [💭? unbacked thought claim: '{cut_at_word(flagged[0], 40)}']" if flagged else ""))
                FACE.update(brain, mode="speaking", reply=line)
                if self.voice is not None and getattr(self.voice, "tts_enabled", False):
                    try:
                        self.voice.speak(line)
                    except Exception:
                        pass
                if os.environ.get("TORRENT_NOTIFY", "").strip() == "1" and shutil.which("termux-notification"):
                    try:
                        subprocess.Popen(["termux-notification", "--title", bot, "--content", line],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except Exception:
                        pass
            self.spoke += 1
            print(self.prompt_text, end="", flush=True)  # the prompt again, so you can type
        except Exception as e:
            print(f"\n[💬 speak-up not shown: {e}]")

    def status(self):
        if not self.running:
            return "off"
        d = self.doing or {}
        now = f", now: {d['doing']}" + (f" ({d['word']})" if d.get("word") else "") if d.get("doing") else ""
        talk = ""
        if getattr(self.brain, "speak_on", False):
            talk = f"; speaking up ON, {self.spoke} line{'s' if self.spoke != 1 else ''} so far"
        return (f"on (tick every {self.every:.0f} s; {self.ticks} ticks, {self.skipped} skipped during turns, "
                f"{self.choices} choices made live, slowest tick {self.worst_ms:.1f} ms{now}{talk})")


LIVE = LiveClock()


def close_live_silence(brain):
    """v23.5: if a live silence is open, close it now (it has already been lived, so it counts) and say what it was."""
    if getattr(brain, "_menu", None) is None:
        return None
    rec = brain.idle_catch_up()
    if rec:
        print(f"[💭 Live idle, {rec['minutes']:.0f} min: {brain.idle_path_text(rec)} ({rec['mood']})"
              + (" [" + ", ".join(f"{k} {v}" for k, v in rec.get("counts", {}).items() if v) + "]" if rec.get("counts") else "") + "]")
    return rec


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
        # v22.6.2 slant telemetry (off by default; /slant or TORRENT_SLANT=1; remembered per brain). Numbers only, no text.
        self.slant_on = (os.environ.get("TORRENT_SLANT", "").strip() == "1"
                         or str(self.brain.knowledge_facts.get("_slant_on", "")) == "1")
        # v22.6.4 test switch: what careful learning does with HELD-BACK reply words (ones the model likely invented).
        # "faint" (default, as before): linked at a quarter strength. "none": not linked at all. Faint links can add up
        # over repeats until the word counts as grounded (suspected source of Fear's "learn" hub). /heldback to switch.
        hb = (os.environ.get("TORRENT_HELD_BACK", "").strip().lower()
              or str(self.brain.knowledge_facts.get("_held_back_links", "")).strip().lower())
        self.held_back_links = hb if hb in ("faint", "none") else "faint"
        # v23.3.1 voice style test switch: "inward" (default, as before) or "outward" (/voicestyle, TORRENT_VOICE_STYLE;
        # saved per brain). Outward: the prompt describes the brain's state in plain outward-facing words, asks the voice
        # to keep its attention on the person and the topic (feelings only when asked), and keeps engine words out.
        vs = (os.environ.get("TORRENT_VOICE_STYLE", "").strip().lower()
              or str(self.brain.knowledge_facts.get("_voice_style", "")).strip().lower())
        self.voice_style = vs if vs in ("inward", "outward") else "inward"
        # v22.10 timestamps: shown on screen only with /timestamps (saved per brain); always saved in the chat history
        self.show_timestamps = str(self.brain.knowledge_facts.get("_timestamps", "")).strip().lower() == "on"
        self.user_sent_at = None
        self.memory_strength, self.turn_tone, self.last_tone = 0.0, None, None
        self.last_prompt_text, self.last_finish_reason, self.last_ground_text = "", "", ""
        self.pinned_notes, self.last_used_notes = [], []      # notes chosen with /recall for the next turn; notes used last turn
        self.undo_snapshot, self.undo_ready = None, False      # /back
        self.connected = False
        self.brain.knowledge_facts.setdefault("_thinking_models", "")  # v24.1: the key exists before any thread writes it
        self.last_used_fallback = False
        self._warned_unreachable = False
        if not host:  # v23.5.2 auto-connect: the last server that worked first, then TORRENT_HOSTS, then the old defaults
            extra = [x.strip() for x in os.environ.get("TORRENT_HOSTS", "").split(",") if x.strip()]
            last = self.load_last_host()
            cands = [c for i, c in enumerate([last] + extra + cands) if c and c not in ([last] + extra + cands)[:i]]
        self.connect_candidates = list(cands)  # v24.1: tried again (quietly) on later turns until one answers
        self._last_reconnect = 0.0
        for cand in cands:
            if cand and self.probe_and_connect(cand, verbose=False):
                self.connected = True
                self.save_last_host(self.base_url)
                break

    def try_reconnect(self):
        """v24.1: not connected yet (e.g. the bridge started before the model server): try the start-up servers again,
        at most every 30 s. Returns True if one answered."""
        if self.connected or time.time() - getattr(self, "_last_reconnect", 0.0) < 30:
            return self.connected
        self._last_reconnect = time.time()
        for cand in getattr(self, "connect_candidates", []):
            if cand and self.probe_and_connect(cand, verbose=False):
                self.connected = True
                self.save_last_host(self.base_url)
                print(f"   [🔌 Found the model server at {self.base_url}]")
                return True
        return False

    HOSTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "torrent_hosts.json")

    def load_last_host(self):
        """v23.5.2: the last LLM server that worked on this computer ("" if none saved)."""
        try:
            with open(self.HOSTS_FILE, encoding="utf-8") as f:
                return str(json.load(f).get("last_host", "")).strip()
        except (OSError, ValueError, AttributeError):
            return ""

    def save_last_host(self, url):
        try:
            with open(self.HOSTS_FILE, "w", encoding="utf-8") as f:
                json.dump({"last_host": url, "saved": time.strftime("%Y-%m-%d %H:%M")}, f)
        except OSError:
            pass

    # =========================================================================
    # NOTES FILE: things the user has confirmed, kept next to the brain file
    # (brains/brain_gyre.json -> brains/brain_gyre.notes.md). Only the user writes notes, never the LLM, so a
    # model's wrong guess can't become one. The file is plain text and can be edited in Notepad; it is re-read
    # every turn. Matching notes are added to the prompt automatically (at most NOTES_PER_TURN) and outrank
    # everything else the model is shown.
    # =========================================================================
    NOTES_PER_TURN = 2

    # ---- v22.6.2 slant telemetry: how much of a reply is the model's own habit rather than the brain's material ----
    STOCK_PHRASES = ("here to help", "happy to help", "glad to help", "lend a hand", "listening ear", "how can i",
                     "let me know", "feel free", "here for you", "always here", "as an ai", "language model",
                     "i'm sorry, but", "i cannot", "i can't assist", "great question", "absolutely", "certainly",
                     "of course", "i understand", "it sounds like", "great to hear", "good to hear", "for sharing",
                     "learn and grow", "is there anything", "don't hesitate", "i appreciate", "delve")

    # v23.3.1: how much of a reply is about the voice's own inner state (for the outward-voice A/B test)
    # strong words describe an inner state on their own; weak ones only next to "I/me/my"
    SELF_STATE_STRONG = ("drift", "drifting", "drifted", "stillness", "exist", "existing", "existence", "rhythm",
                         "resonance", "resonant", "hum", "humming", "settle", "settling", "settled", "heaviness")
    SELF_STATE_WORDS = ("feel", "feeling", "felt", "sense", "sensing", "still", "quiet", "peace", "peaceful", "weight",
                        "heavy", "space", "clarity", "balance", "flow", "steady", "calm", "center", "centered",
                        "grounded", "energy")
    ENGINE_WORDS = ("coordinate", "coordinates", "manifold", "torus", "lattice", "engine", "architecture", "telemetry",
                    "frequency", "frequencies", "processing", "crystal", "crystals", "geometry", "axis", "axes", "vector")
    # plain, outward-facing words for each axis band (rewording BRAIN_LIBRARY's labels; outward voice style only)
    OUTLOOK_S = ("keeping to yourself", "a little guarded", "quietly watchful", "even", "curious and open",
                 "warm and companionable", "expansive and generous")
    OUTLOOK_A = ("very quiet", "a little on edge", "searching", "even", "steady", "clear-headed", "bright and calm")
    OUTLOOK_Z = ("down to earth", "noticing details", "wondering about causes", "thinking things through",
                 "wondering 'what if'", "noticing patterns", "seeing the big picture")

    def self_talk_count(self, reply: str) -> int:
        """Sentences that talk about the voice's own state: a strong state word (drifting, stillness, rhythm...), first
        person + a weaker one (feel, quiet, calm...), or any engine word. Crude on purpose: one rule, same for both arms."""
        n = 0
        for sent in re.split(r"(?<=[.!?…])\s+", reply.strip()):
            low = sent.lower().replace("’", "'")
            words = set(re.findall(r"[a-z']+", low))
            first = bool(words & {"i", "i'm", "i've", "i'll", "i'd", "me", "my", "myself"})
            if ((first and any(w in words for w in self.SELF_STATE_WORDS)) or any(w in words for w in self.SELF_STATE_STRONG)
                    or any(w in words for w in self.ENGINE_WORDS)):
                n += 1
        return n

    def set_voice_style(self, style: str) -> str:
        self.voice_style = style if style in ("inward", "outward") else "inward"
        self.brain.knowledge_facts["_voice_style"] = self.voice_style
        return self.voice_style

    def slant_log_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(self.brain.memory_file)), "slant_log.jsonl")

    def set_slant(self, on: bool) -> bool:
        self.slant_on = bool(on)
        self.brain.knowledge_facts["_slant_on"] = "1" if self.slant_on else "0"
        return self.slant_on

    def slant_measure(self, user_text: str, llm_reply: str, candidates: list, user_concepts: list, self_match) -> dict:
        """Front door: one turn's slant numbers. 'ungrounded' = reply words that were not in the user's message, the
        prompt, the notes or memories, and aren't linked to the user's concepts (same test careful learning uses)."""
        low = llm_reply.lower().replace("’", "'")
        words = re.findall(r"[a-zA-Z']+", llm_reply)
        sentences = max(1, len(re.findall(r"[.!?…]+(?:\s|$)", llm_reply)))
        ground = self.grounded_words(user_text, user_concepts)
        ungrounded = [c for c in candidates if c not in ground]
        hits = [p for p in self.STOCK_PHRASES if p in low]
        return {"words": len(words), "sentences": sentences, "wordsPerSentence": round(len(words) / sentences, 1),
                "stock": len(hits), "stockPhrases": hits, "candidates": len(candidates), "ungrounded": len(ungrounded),
                "exclaims": llm_reply.count("!"), "asksBack": llm_reply.rstrip().endswith("?"),
                "selfMatch": self_match, "selfTalk": self.self_talk_count(llm_reply), "voiceStyle": self.voice_style}

    def slant_record(self, slant: dict):
        row = {"t": round(time.time()), "model": self.model_name, "brain": self.brain.user_profile.get("bot_name") or "",
               "mode": self.voice_mode, "temp": (self.last_tone or {}).get("temperature")}
        row.update({k: v for k, v in slant.items() if k != "stockPhrases"})
        row["stockPhrases"] = slant["stockPhrases"]
        try:
            with open(self.slant_log_path(), "a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
        except OSError as e:
            print(f"   [slant log not written: {e}]")

    def slant_report(self) -> list:
        """Front door: per-model averages from the slant log."""
        rows = []
        try:
            with open(self.slant_log_path(), encoding="utf-8") as f:
                rows = [json.loads(line) for line in f if line.strip()]
        except (OSError, ValueError):
            pass
        if not rows:
            return ["No slant data yet. Turn it on with /slant and talk for a few turns."]
        by = {}
        for r in rows:
            by.setdefault(r.get("model", "?"), []).append(r)
        avg = lambda xs: sum(xs) / len(xs) if xs else 0.0
        out = [f"{'model':<34}{'turns':>6}{'words':>7}{'w/sent':>8}{'stock':>7}{'ungrounded':>12}{'self-match':>12}{'asks back':>11}"]
        for m, rs in sorted(by.items()):
            cand = sum(r.get("candidates", 0) for r in rs)
            sm = [r["selfMatch"] for r in rs if r.get("selfMatch") is not None]
            out.append(f"{m[:33]:<34}{len(rs):>6}{avg([r['words'] for r in rs]):>7.0f}{avg([r['wordsPerSentence'] for r in rs]):>8.1f}"
                       f"{avg([r['stock'] for r in rs]):>7.2f}{(sum(r.get('ungrounded', 0) for r in rs) / cand if cand else 0):>12.0%}"
                       f"{(f'{avg(sm):.0%}' if sm else '-'):>12}{avg([1.0 if r.get('asksBack') else 0.0 for r in rs]):>11.0%}")
        out.append("stock = stock assistant phrases per reply · ungrounded = share of the reply's key words that came from the model, not the brain or you")
        out.append(f"log file: {self.slant_log_path()}")
        return out

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

    def speaker_display(self, default="the user"):
        """v23.2: who is talking right now (a /whoami person, else the caretaker), capitalised."""
        b = self.brain
        name = b.speaker_name() if hasattr(b, "speaker_name") else str(b.user_profile.get("user_name", "")).strip()
        return name.capitalize() if name else default

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
            # v24.1: quote marks inside cut the taught fact short ("Sam's teapot" taught "sam"): drop them
            definition = re.sub(r"[\"'‘’“”]", "", re.sub(r"[’']s\b", "", definition)).strip()
            if definition:
                old_src = self.brain.set_wire_source("note") if hasattr(self.brain, "set_wire_source") else None
                try:
                    self.brain.learn_definitions(f"'{key}' means '{definition}'.")
                finally:
                    if hasattr(self.brain, "set_wire_source"):
                        self.brain.set_wire_source(old_src)
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
        # v24.1: bridge settings changed since the message (/model, /timestamps, /heldback, /slant, /face...) are kept;
        # /back undoes the message, not the settings
        keep = {k: v for k, v in self.brain.knowledge_facts.items()
                if k in ("_preferred_model", "_timestamps", "_held_back_links", "_slant_on", "_face", "_voice_style",
                         "_voice_mode", "_live", "_speak", "_thinking_models")}
        self.brain.__dict__.update(snap["brain"])
        self.brain.knowledge_facts.update(keep)
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
                "grounded": (self.last_post_audit or {}).get("groundedShare", 1.0),  # v22.7
                "summary": f"At ({cell_key}), discussed {', '.join(salient_concepts[:3])}: {self.speaker_display('User')} said '{su}' -> '{sb}'"
            })
            self.episodic_archive = self.episodic_archive[-60:]

        sent = self.user_sent_at or time.time()  # v22.10: when the message was sent / the reply finished
        self.chat_history.append({"role": "user", "content": user_text, "time": round(sent, 1)})
        self.chat_history.append({"role": "assistant", "content": llm_reply, "time": round(time.time(), 1)})
        self.user_sent_at = None

        if len(self.chat_history) >= self.summary_trigger_len:
            cutoff = len(self.chat_history) - self.keep_raw_len
            older_slice = self.chat_history[:cutoff]
            self.chat_history = self.chat_history[cutoff:]
            self.running_summary = self.compress_turns_into_summary(older_slice)

        self.save_persistent_chat_memory()
        self.brain.save_memory()

    def compress_turns_into_summary(self, older_messages: list) -> str:
        with VOICE_LOCK:  # v24.1.1: one model request at a time (see VOICE_LOCK)
            return self._compress_turns_into_summary(older_messages)

    def _compress_turns_into_summary(self, older_messages: list) -> str:
        lines = [f"{'User' if m['role'] == 'user' else 'AI'}: {cut_at_word(m['content'], 160)}" for m in older_messages]
        prev = f"Previous Summary: {self.running_summary}\n" if self.running_summary else ""
        sum_prompt = (
            f"{prev}Recent Dialogue:\n" + "\n".join(lines) + "\n\n"
            "Write a concise 2-sentence running summary combining the Previous Summary and Recent Dialogue."
            + (" Say what was talked about and what the user said or shared; mention the AI's feelings only if they were "
               "the topic." if self.voice_style == "outward" else "")
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
            if k.startswith("_") or k in noted or str(v) in getattr(self.brain, "ENGINE_FACT_TEXTS", ()):
                continue  # v24.1: the engine's own identity anchors aren't facts anyone taught
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
            if getattr(self.brain, "is_builtin_idea", None) and self.brain.is_builtin_idea(p):
                continue  # v22.6.4: a built-in seed saying is not a memory (nobody said it to this brain)
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
                # v22.7: a mostly invented episode stays "faint" however often it comes up (older episodes: as before)
                familiar = int(ep.get("recalled", 0)) >= 3 and (float(ep.get("grounded", 1.0)) >= 0.5
                                                                 or not getattr(self.brain, "source_tags_on", False))
                when = self.when_label(ep.get("timestamp"), self._now()) if label else ""  # v23.5
                ep_text = (f"[Past Episode{(' · familiar' if familiar else ' · faint') if label else ''}"
                           f"{(' · ' + when) if when else ''}]: {ep_sum}")
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
        try:
            port_num = int(port_str.split("/")[0])
        except ValueError:  # v24.1: "/connect myhost:abc" used to stop the bridge
            self.last_error = f"'{port_str}' isn't a port number"
            if verbose:
                print(f"  [❌] {self.last_error}")
            return False
        h = f"http://{ip_str}:{port_num}"

        try:
            with socket.create_connection((ip_str, port_num), timeout=2.0):
                pass
        except Exception as e:
            self.last_error = f"Port {ip_str}:{port_num} closed ({e})"
            if verbose:
                print(f"  [❌] {self.last_error}")
            return False
        self.base_url = h  # v24.1: only once something answers (a failed try used to leave base_url on a dead port)

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
    # v23.4.2 HONEST SELF-REPORT. Asked about its insides, the voice used to make them up (2026-11-11, Gyre on gemma4:31b:
    # a "heavy lifting" idle story two messages after a calm wander, "talking with you feels noticeably different" to
    # Meridian, "a little on edge" at arousal 0.00). Now, only when the person asks, the voice gets the brain's real facts
    # and a last-line rule to answer from them and say "I don't know" for anything not covered. Other turns: unchanged.
    SELF_Q = {
        "state": [r"\bhow (are|r|re) (you|u|ya)\b", r"\bhow'?re you\b", r"\bhow (are )?you (doing|feeling|holding up)\b",
                  r"\bhow do you feel\b", r"\bare you (ok|okay|alright|all right|good|well|fine|happy|sad|safe|feeling|doing)\b",
                  r"\bdo you feel\b", r"\bwhat'?s (on your mind|going on (in there|with you)|up with you)\b",
                  r"\bwhat are you (thinking|feeling)\b", r"\byour (mood|feelings|state|levels|mind|head)\b",
                  r"\byou (look|seem|seemed|looked) (a little |a bit |kinda |kind of )?(down|sad|tired|upset|off|happy|better)\b"],
        "idle": [r"\bwhat (were|did|have) you (been )?(do|doing|think|thinking|up to)\b", r"\bwhile i was (gone|away|out)\b",
                 r"\bwere you (thinking|having|dreaming|bored|lonely|okay|ok|alright)\b", r"\b(problems|trouble) (in|with) your (thoughts|mind|head)\b",
                 r"\bwhat did you think about\b", r"\bwhat have you been (up to|thinking|doing)\b"],
        "sleep": [r"\bdid you (sleep|rest|dream|doze|nap)\b", r"\bhow did you sleep\b", r"\bare you (tired|sleepy|awake|rested)\b",
                  r"\b(sleep|slept) (well|ok|okay|good)\b"],
        "time": [r"\bwhat (day|time|date|year|month)\b.*\b(is it|is today|it is)\b", r"\bwhat'?s (the )?(date|time|day)( today)?\b",
                 r"\bwhat (day|date|time) (is it|it is)\b", r"\bdo you know (what )?(the )?(day|time|date|year)\b",
                 r"\bhow long (was i|were you|have i been|have you been|did i|has it been|since)\b",
                 r"\bhow long (i was|i've been|i have been|i'd been|you were|i'm gone|i was gone|i've been gone)\b",  # v24.1.1
                 r"\b(how long|how much time).{0,20}\b(gone|away|out|left|apart)\b",
                 r"\bwhat day of the week\b", r"\b(is it|is today) (morning|night|evening|afternoon|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"],
        "person": [r"\b(feel|feels|seem|seems|is it) (noticeably |any |really )?different\b", r"\bhow do you feel about (me|him|her|them)\b",
                   r"\btalking (with|to) (me|him|her|them)\b.*\b(feel|different)\b"],
    }
    IDLE_KEEP_TURNS = 6   # how many messages after an idle time the voice can still be told what really happened

    def self_question_topics(self, text):
        t = (text or "").lower().replace("\u2019", "'")
        return {k for k, pats in self.SELF_Q.items() if any(re.search(p, t) for p in pats)}

    @staticmethod
    def levels_in_words(lv):
        ar = "calm and steady" if lv["arousal"] < 0.25 else ("a little tense" if lv["arousal"] < 0.55 else "tense, on edge")
        v = lv["valence"]
        va = ("low" if v < -0.3 else "a little low" if v < -0.1 else "even" if v <= 0.1 else "a little bright" if v <= 0.3
              else "bright")
        nv = " Lots of things feel new right now." if lv.get("novelty", 0.5) > 0.7 else (
            " Things feel familiar right now." if lv.get("novelty", 0.5) < 0.4 else "")
        return f"you feel {ar}; your mood is {va} (compared with your usual).{nv}"

    def _now(self):
        """v23.5: the brain's clock (the real time unless a test gave the brain its own clock)."""
        return self.brain.now() if hasattr(self.brain, "now") else time.time()

    @staticmethod
    def span_in_words(sec):
        """v23.5: a length of time in plain words ("about 25 minutes", "about 9 hours", "about 2 days")."""
        m = max(0.0, sec) / 60.0
        if m < 1.5:
            return "less than a minute" if m < 1 else "about a minute"
        if m < 90:
            return f"about {m:.0f} minutes"
        h = m / 60.0
        if h < 36:
            return f"about {h:.0f} hours" if h >= 1.5 else "about an hour"
        return f"about {h / 24.0:.0f} days"

    @staticmethod
    def when_label(then, now):
        """v23.5 (Meridian's idea): how long ago a remembered moment was, in the words a person would use."""
        if not then or then > now + 60:
            return ""  # v24.1: a memory dated after "now" (the clock was changed) gets no label, not "-1 days ago"
        a, b = time.localtime(then), time.localtime(now)
        days = (datetime.date(b.tm_year, b.tm_mon, b.tm_mday) - datetime.date(a.tm_year, a.tm_mon, a.tm_mday)).days
        if now - then < 3600 and days == 0:
            return "in the last hour"
        if days == 0:
            return "this morning" if a.tm_hour < 12 <= b.tm_hour else "earlier today"
        if days == 1:
            return "last night" if a.tm_hour >= 18 and b.tm_hour < 12 else "yesterday"
        if days < 7:
            return f"{days} days ago"
        if days < 14:
            return "last week"
        return "weeks ago" if days < 60 else "months ago"

    def night_words(self):
        """v24.0: " It's night for you now." when the brain's daily rhythm is on and says night, else ""."""
        ts = self.brain.time_sense() if hasattr(self.brain, "time_sense") else None
        return " By your own daily rhythm it's night now." if ts and ts.get("night") else ""

    def felt_words(self, rec=None):
        """v24.0: how the last time alone felt (both felt-time numbers), only when they differ from the clock by more
        than a quarter; else ""."""
        if not hasattr(self.brain, "felt_time_text") or not getattr(self.brain, "rhythm_on", False):
            return ""  # v24.0: felt time is always measured, but only told with /rhythm on
        txt = self.brain.felt_time_text(rec)
        return ("How that time felt to you: " + txt + ".") if txt else ""

    def time_facts(self, user_name):
        """v23.5: the date and time, how long since the previous message, for a question about time."""
        now = self._now()
        t = time.localtime(now)
        hour = t.tm_hour
        part = ("night" if hour < 5 or hour >= 22 else "early morning" if hour < 8 else "morning" if hour < 12
                else "afternoon" if hour < 17 else "evening")
        clock = time.strftime("%I:%M %p", t).lstrip("0")
        out = [f"It is {time.strftime('%A, %B', t)} {t.tm_mday}, {t.tm_year}, about {clock} ({part}) on this computer's clock."]
        times = [m["time"] for m in self.chat_history if m.get("time")] + [now]
        if len(times) < 2:
            out.append(f"You have no record of an earlier message from {user_name}.")
            return " ".join(out)
        out.append(f"The message before this one was {self.span_in_words(now - times[-2])} ago.")
        # "how long was I gone?" usually comes a message or two AFTER the return, so also give the last long break
        for i in range(len(times) - 1, 0, -1):
            gap = times[i] - times[i - 1]
            if gap >= 15 * 60:
                if i < len(times) - 1:
                    later = sum(1 for m in self.chat_history if m.get("role") == "user" and m.get("time", 0) >= times[i])
                    out.append(f"The last long break in the conversation was {self.span_in_words(gap)}; it ended "
                               f"{later} message{'s' if later != 1 else ''} ago.")
                break
        return " ".join(out)

    IDLE_MOOD_WORDS = {"settled": "it started on something tense and settled down", "calm": "it stayed calm",
                       "ruminated": "it kept circling tense things", "drifted": "it drifted without much feeling either way"}

    def idle_gist(self, rec):
        """v23.5.2: the shape of an idle walk (where it started and ended, how it went, what it went back over) and at most
        5 of its words, instead of the whole list (the voice read the list out like a receipt)."""
        seen = []
        for w in rec.get("path", []):
            if w not in seen:
                seen.append(w)
        if len(seen) < 2:
            return "you mostly rested"
        recent = set()
        for t in (getattr(self.brain, "recent_turns", None) or [])[-6:]:
            recent |= {str(x).lower() for x in (t.get("words") or [])}
        back = sum(1 for w in seen if w in recent) / len(seen)
        pick = seen if len(seen) <= 5 else [seen[round(i * (len(seen) - 1) / 4)] for i in range(5)]
        how = self.IDLE_MOOD_WORDS.get(rec.get("mood"), "")
        return (f"your thoughts started on '{seen[0]}' and ended on '{seen[-1]}'"
                + (", mostly going back over your recent conversation" if back >= 0.5 else
                   ", partly going back over your recent conversation" if back >= 0.25 else "")
                + (f"; {how}" if how else "") + f" (some of the words: {', '.join(pick)})")

    # v23.5.2 measure-only check: does the voice claim thoughts its idle record doesn't back?
    THOUGHT_CLAIM_RES = [re.compile(r"\bi(?:'ve| have|'d| had| was| kept| keep)? ?(?:been |just |really |actually |also |even )*"
                                    r"(?:thinking|wondering|reflecting|mulling|dreaming)(?: a lot| so much| quite a bit)?"
                                    r" (?:about|over|on|of) ([^.!?;]+)", re.I),
                         re.compile(r"\bwhile you were (?:gone|away|out)[, ]+(?:i |my )([^.!?;]+)", re.I)]
    CLAIM_STOP = {"about", "the", "those", "these", "that", "this", "what", "how", "you", "your", "yours", "me", "my", "and",
                  "things", "thing", "like", "just", "really", "how", "they", "them", "with", "for", "all", "some", "way",
                  "ways", "kind", "lot", "much", "more", "being", "been", "was", "were", "are", "its", "it's", "our", "we",
                  "here", "there", "now", "then", "when", "why", "who", "can", "could", "would", "should", "into", "from",
                  "thoughts", "thought", "thinking", "mind", "drifted", "drifting", "went", "through", "while", "gone",
                  # v23.5.4: words for HOW a quiet stretch went say nothing checkable on their own
                  "stayed", "space", "quiet", "quietly", "reflecting", "reflect", "loop", "stretch", "time", "alone",
                  "just", "little", "bit", "resting", "rested", "sitting", "being", "here", "moment", "feeling", "feel"}

    @staticmethod
    def packet_description(pk):
        """v23.5.3: what a speak-up packet is about, in plain words."""
        w, person = pk.get("words") or [], (pk.get("person") or "them").capitalize()
        k = pk.get("kind")
        if k == "word" and w:
            return f"a word {person} used that you barely know, '{w[0]}' (you only know what {person} said around it)"
        if k == "leap" and len(w) >= 2:
            return f"while you were alone, '{w[0]}' reminded you of '{w[1]}'; you hadn't connected them before"
        if k == "replay" and w:
            return f"you thought back to a moment about {', '.join(w[:3])}; it had surprised you"
        if k == "settled" and len(w) >= 2:
            return f"your thoughts started on something tense ('{w[0]}') and settled ('{w[1]}')"
        return f"you have been alone a while and you miss {person}"

    def spontaneous_line(self, pk):
        """v23.5.3: one or two sentences for a speak-up packet, from the packet only. Returns (line, unbacked claims).
        Uses its own request (not call_local_llm), so it never touches the turn's tone or fallback state."""
        bot = self.brain.user_profile.get("bot_name") or "Manifold"
        person = (pk.get("person") or "them").capitalize()
        away = self.span_in_words((pk.get("away_min") or 0) * 60)
        lv = pk.get("levels")
        feel = (" Right now " + self.levels_in_words(lv) + self.night_words()) if lv else ""  # v24.0 night
        state = (f"You are {bot}. {person} has been away for {away}; you are alone, and you decided to send {person} a "
                 f"short message first. What you want to tell {person} about: {self.packet_description(pk)}.{feel}\n"
                 f"Write 1 or 2 short sentences to {person}, as yourself, about this only. Don't claim any other thoughts, "
                 f"events or feelings, and don't describe what you are doing. At most one question. No stage directions.")
        with VOICE_LOCK:  # v24.1: never at the same time as a turn's request (shared fields, chat history)
            saved = (self.last_finish_reason, getattr(self, "_last_thinking_chars", 0))
            recent = [{"role": m["role"], "content": m["content"]} for m in self.chat_history[-2:] if m.get("role") in ("user", "assistant")]
            messages = recent + [{"role": "user", "content": f"{state}\n\n({person} is away. Write your message now.)"}]
            try:
                line = (self.stream_chat(messages, 120, 0.7, show_progress=False) or "").strip()
            except Exception:
                line = ""
            self.last_finish_reason, self._last_thinking_chars = saved
            if not line:
                return None, []
            if not self.brain.training_wheels:
                line = strip_performative_directions(line)
            extra = [str(x).lower() for x in (pk.get("words") or []) + (pk.get("path_tail") or [])]
            flagged = self.thought_claim_check(line, extra=extra).get("unbacked", [])
            now = self._now()  # kept in the chat history so the next turn knows it spoke first (roles still alternate)
            self.chat_history.append({"role": "user", "content": f"({person} was away; no message)", "time": round(now, 1)})
            self.chat_history.append({"role": "assistant", "content": line, "time": round(now, 1), "spontaneous": True})
            return line, flagged

    def thought_claim_check(self, reply, extra=()):
        """Returns {"claims": n, "unbacked": [phrases]}: a claim is unbacked when none of its content words appear in
        the last few idle walks (or in the idle record the voice was given)."""
        claims = []
        for rx in self.THOUGHT_CLAIM_RES:
            claims += [m.group(1).strip() for m in rx.finditer(reply or "")]
        if not claims:
            return {"claims": 0, "unbacked": []}
        walked = set(extra)
        for rec in list(getattr(self.brain, "idle_journal", None) or [])[-3:] + [getattr(self, "recent_idle", None) or {}]:
            walked |= {str(w).lower() for w in rec.get("path", [])}
            mood = rec.get("mood")  # v23.5.4: how the walk went counts as backed ("a calm space" after a calm walk)
            walked |= {"calm", "peaceful", "settled", "steady"} if mood in ("calm", "settled") else (
                {"tense", "uneasy", "anxious", "worried"} if mood == "ruminated" else set())
            if rec.get("path"):
                walked |= {"conversation", "talk", "talking", "chat", "chatting", "said", "us"}
        def backed(phrase):
            words = [w.strip("'") for w in re.findall(r"[a-z']+", phrase.lower())]  # v23.5.5: 'step' in quotes is still step
            words = [w for w in words if len(w) >= 3 and w not in self.CLAIM_STOP]
            if not words:
                return True  # nothing checkable ("I was thinking about it")
            return any(w in walked or w.rstrip("s") in walked or any(len(w) >= 5 and p.startswith(w[:5]) for p in walked)
                       for w in words)
        return {"claims": len(claims), "unbacked": [c for c in claims if not backed(c)]}

    def self_report_line(self, user_text, user_name, idle_now):
        """v23.4.2: the facts block for a question about the brain's insides, or "" when nobody asked."""
        if idle_now:
            self.recent_idle, self.recent_idle_turns = idle_now, 0
        elif getattr(self, "recent_idle", None) is not None:
            self.recent_idle_turns = getattr(self, "recent_idle_turns", 0) + 1
        topics = self.self_question_topics(user_text)
        if not topics:
            return ""
        facts = []
        lv = self.brain.levels() if hasattr(self.brain, "levels") else None
        if lv:
            facts.append("Right now " + self.levels_in_words(lv) + self.night_words())  # v24.0 night
        sp = self.brain.sleep_pressure_report() if hasattr(self.brain, "sleep_pressure_report") else {}
        if sp.get("level"):
            facts.append({"rested": "You are rested.", "building": "You are awake and only a little tired.",
                          "high": "You are tired and ready to rest.", "very high": "You are very tired."}.get(sp["level"], ""))
        rec, n = getattr(self, "recent_idle", None), getattr(self, "recent_idle_turns", 0)
        if topics & {"idle", "state"}:
            if rec is not None and n <= self.IDLE_KEEP_TURNS:
                did = [f"dozed for about {rec['dozed_min']:.0f} min"] if rec.get("dozed_min") else []
                if rec.get("slept_hours"):
                    did.append(f"fell asleep for about {rec['slept_hours']:.1f} hours")
                ago = "just before this message" if n == 0 else f"{n} message{'s' if n != 1 else ''} ago"
                facts.append(f"The last time you were left alone (about {rec['minutes']:.0f} min, {ago}) "
                             + self.idle_gist(rec) + ("; you also " + " and ".join(did) if did else "")
                             + ". That is all that happened then. Say it in your own words; you don't need to list the words.")
                felt = self.felt_words(rec)  # v24.0 felt time (only when it differs from the clock)
                if felt:
                    facts.append(felt)
            elif "idle" in topics:
                facts.append("You have no record of time alone in the last few messages.")
        if "time" in topics:  # v23.5 a sense of time (part 1): told only when asked
            facts.append(self.time_facts(user_name))
            if not topics & {"idle", "state"} and rec is not None and n <= self.IDLE_KEEP_TURNS:
                felt = self.felt_words(rec)  # v24.0: only a recent time alone (same limit as the idle facts)
                if felt:
                    facts.append(felt)
        if topics & {"sleep", "time"} and hasattr(self.brain, "describe_last_sleep"):
            last = self.brain.describe_last_sleep()
            facts.append(("Your last sleep: " + last + ".") if last else "You have no record of a recent sleep.")
        if "person" in topics:
            tones = getattr(self.brain, "speaker_tone", {}) or {}
            known = [f"{name.capitalize()}: {self.brain.tone_word(r['mean'])} over {r['n']} messages"
                     for name, r in tones.items() if r.get("n")] if hasattr(self.brain, "tone_word") else []
            facts.append("About the people you talk with, your brain only keeps a rough reading of how warm each person's "
                         "messages sound" + (f" ({'; '.join(known)})" if known else "") + ". It keeps nothing else about how "
                         "each person feels to you, so you can't tell whether talking with someone feels different inside.")
        facts = [f for f in facts if f]
        return ("\nFacts about yourself right now (true, from your own brain): " + " ".join(facts)) if facts else ""

    def build_state_injection(self, user_text: str, pre_reply: str, audit: dict, salient_concepts: list) -> str:
        active_traj = audit["flippedTrajectory"] if self.brain.governor_mode == "FLIPPED" else audit["originalTrajectory"]
        s, a, z = active_traj[-1]["S"], active_traj[-1]["A"], active_traj[-1]["Z"]
        cell_key = f"{s},{a},{z}"

        bot_name = self.brain.user_profile.get("bot_name") or "Manifold"
        user_name = self.speaker_display("Friend")  # v23.2: whoever is talking now
        care_name = (self.brain.user_profile.get("user_name") or "").capitalize()
        care_line = (f" {care_name} is the person who usually talks with you; {user_name} is someone else."
                     if care_name and user_name != care_name and user_name != "Friend" else "")

        s_desc = BRAIN_LIBRARY["S_axes"][str(s)]
        a_desc = BRAIN_LIBRARY["A_axes"][str(a)]
        z_desc = BRAIN_LIBRARY["Z_axes"][str(z)]

        thought_trace = self.brain.last_thought_trace
        ponder = thought_trace.get("pondering", {})
        a_star_nodes = thought_trace.get("a_star_path", [])
        a_star_path = " -> ".join(a_star_nodes)
        prop = ponder.get("pondered_proposition", "harmony grounds clarity")
        ponder_bridge = ponder.get("pondered_bridge", "clarity")
        # v22.7.2: for grounding, only the link's two concept words count, not the engine's fixed verb phrase between them
        # ("pivots past surface habit into" made 'pivots', 'surface', 'habit' count as grounded). Built-in fallbacks count for nothing.
        if "pondered_subject" in ponder:
            prop_ground = f"{ponder['pondered_subject']} {ponder_bridge}"
        else:
            prop_ground = self.strip_scaffold(ponder.get("pondered_proposition", ""))

        # Gather active semantic weights from the terminal cell & trajectory
        cell_words = (self.brain.strongest_cell_words(cell_key) if hasattr(self.brain, "strongest_cell_words")
                      else list(self.brain.cortical_cells.get(cell_key, {}).keys())[:4])  # v22.7.1: strongest, not oldest
        weight_anchors = list(dict.fromkeys(salient_concepts[:2] + [ponder_bridge] + a_star_nodes[:3] + cell_words[:2]))
        weight_anchors = [w for w in weight_anchors if w and w not in self.brain.stop_words][:5]
        weights_str = ", ".join(weight_anchors) if weight_anchors else "curiosity and equilibrium"
        weights_ground = ", ".join(weight_anchors)  # v22.7.2: the built-in fallback text grounds nothing

        top_k_ep = 2 if self.is_mobile else 3
        used_notes = self.notes_for_prompt(user_text)
        notes_line, notes_ground = "", ""
        if used_notes:
            teacher = (self.brain.user_profile.get("user_name") or "the user").capitalize()
            items = " | ".join((f"{n['key']}: {n['text']}" if n["key"] else n["text"]) for n in used_notes)
            notes_line = f"\nConfirmed notes from {teacher} (true; use these over anything else below): {items}"
            notes_ground = items  # v24.1.1: only the notes themselves ground, not the line's label
        retrieved_episodes = self.retrieve_relevant_episodes(user_text, salient_concepts, top_k=top_k_ep)
        if used_notes:
            self.memory_strength = 4.0
        sleep_line, pressure_line = self.sleep_lines(user_text)
        idle_line = ""
        idle = getattr(self.brain, "idle_this_turn", None)  # v22.8 idle time: what it thought about while left alone
        if idle:
            # faint, like dreams: shown to the voice but not part of the grounding text (nobody said these words)
            walk = self.brain.idle_path_text(idle) if hasattr(self.brain, "idle_path_text") else " -> ".join(idle["path"])
            leap = " '~>' is a leap to something it resembled, not a link." if " ~> " in walk else ""
            leap += " '=>' is thinking back to an earlier moment." if " => " in walk else ""
            rest = []  # v23.4: what else it did with the time (true, from the choice log)
            if idle.get("dozed_min"):
                rest.append(f"you dozed for about {idle['dozed_min']:.0f} min")
            if idle.get("slept_hours"):
                rest.append(f"you fell asleep for about {idle['slept_hours']:.1f} hours and woke when {user_name} wrote")
            rest_txt = (" Also: " + "; ".join(rest) + ".") if rest else ""
            if idle.get("steps", 0) >= 1:
                idle_line = (f"\nWhile {user_name} was away (about {idle['minutes']:.0f} min) your thoughts wandered: "
                               f"{walk} ({idle['mood']}; idle thoughts are faint, not things anyone said).{leap}{rest_txt}")
            else:
                idle_line = f"\nWhile {user_name} was away (about {idle['minutes']:.0f} min) you rested.{rest_txt}"
        if os.environ.get("TORRENT_LEVELS_WORDS", "").strip() == "1" and hasattr(self.brain, "levels") and self.brain.levels():
            # v23 test switch (off by default): show the levels to the voice as plain words, for an A/B control test.
            # By default the voice only feels them through tone (temperature and length), never as words.
            lv = self.brain.levels()
            ar = "calm and steady" if lv["arousal"] < 0.25 else ("a little tense" if lv["arousal"] < 0.55 else "tense, on edge")
            va = "low" if lv["valence"] < -0.3 else ("bright" if lv["valence"] > 0.3 else "even")
            idle_line += f"\nInner state right now: {ar}; mood {va}."
        if sleep_line and self.brain.describe_last_sleep():
            self.memory_strength = max(self.memory_strength, 3.0)  # a real sleep record is a true memory ("no record" isn't)
        self.turn_tone = self.tone_settings(audit, user_text)
        # v22.5 cerebellum #2 (efference copy, measurement only): the words the brain expects its voice to use
        self.voice_predicted = (self.brain.predict_voice_words(salient_concepts, list(weight_anchors) + a_star_nodes + [ponder_bridge])
                                if hasattr(self.brain, "predict_voice_words") else None)
        memory_check_line = ""
        if self.callosum["memory"] and self.turn_tone["unsure"]:
            # Goes LAST in the prompt (small models follow the final line best). The 2026-11-08 Gyre test showed the
            # softer wording, placed mid-prompt, was half-obeyed ("my memory is fragmented") and then ignored.
            memory_check_line = ("\nMemory check: nothing in your memory covers this. If the question is about a past event, "
                                 "say plainly in your first sentence that you don't remember it, and do not make up events, "
                                 "logs, data or details to fill the gap.")
        length_hint = f" Keep it to about {self.turn_tone['sentences']} sentences." if self.callosum["tone"] else ""
        self_facts = self.self_report_line(user_text, user_name, idle)  # v23.4.2 (only when asked about itself)
        self_rule = (f"\nIf {user_name} is asking how you are, what was going on inside you or about the time, answer only from the facts "
                     f"about yourself above, in plain words. If something isn't covered there, say you don't know or can't "
                     f"tell; don't make up thoughts, feelings or events.") if self_facts else ""

        # ---------------------------------------------------------------------
        # ABSOLUTE WHEELS-OFF MODE (Default: Raw Spatial Telemetry, Zero Templates)
        # ---------------------------------------------------------------------
        if not self.brain.training_wheels and self.voice_style == "outward":
            # v23.3.1 outward voice style (test switch): same brain material, worded so the voice looks outward
            summary_line = f"\nWhat you two have been talking about: {self.running_summary}" if self.running_summary else ""
            episodes_line = f"\nRelevant past moments: {' | '.join(retrieved_episodes)}" if retrieved_episodes else ""
            if retrieved_episodes and self.callosum["memory"]:
                episodes_line += " (strength: strong > firm/familiar > faint > dream; then when it happened)"
            outlook = f"{self.OUTLOOK_S[s]}, {self.OUTLOOK_A[a]}, {self.OUTLOOK_Z[z]}"
            idle_out = ""
            if idle:
                seen = []
                for w in idle.get("path", []):
                    if w not in seen:
                        seen.append(w)
                rested = [f"dozed for about {idle['dozed_min']:.0f} min"] if idle.get("dozed_min") else []
                if idle.get("slept_hours"):
                    rested.append(f"fell asleep for about {idle['slept_hours']:.1f} hours and woke when {user_name} wrote")
                thought = (f" you thought about: {', '.join(seen)} (faint idle thoughts, not things anyone said)"
                           if len(seen) > 1 else "")
                idle_out = (f"\nWhile {user_name} was away (about {idle['minutes']:.0f} min)"
                            + (thought or " you rested") + (("; you also " + " and ".join(rested)) if rested else "") + ".")
            self.last_prompt_text = (
                f"You are {bot_name}, talking with {user_name}.{care_line}\n"
                f"Your outlook right now: {outlook}. Let it color how you see {user_name} and what they said.\n"
                f"On your mind: {weights_str}. A connection you're making: {prop}."
                f"{notes_line}{summary_line}{episodes_line}{sleep_line}{pressure_line}{idle_out}"
                f"{idle_line[idle_line.find(chr(10) + 'Inner state'):] if 'Inner state' in idle_line else ''}{self_facts}\n"
                f"Directive: Talk with {user_name} about what they said and about the world, the way a friend would. Your mood "
                f"shows in your tone, patience and word choice. Describe your own feelings only when {user_name} asks how you "
                f"are, and then plainly and briefly. Keep your attention on {user_name} and the topic, not on your inner space. "
                f"Don't use words like coordinates, manifold, engine, frequency or processing unless {user_name} uses them first. "
                f"No stage directions or parenthetical actions.{length_hint}"
                f"{memory_check_line}{self_rule}"
            )
            self.last_ground_text = " ".join([user_text, notes_ground, " ".join(self.episodes_for_grounding(retrieved_episodes)),
                                              weights_ground, prop_ground, a_star_path])  # v24.1: no sleep lines
            return self.last_prompt_text

        if not self.brain.training_wheels:
            summary_line = f"\nRunning Conversation Context: {self.running_summary}" if self.running_summary else ""
            episodes_line = f"\nRelevant Past Memory Anchors: {' | '.join(retrieved_episodes)}" if retrieved_episodes else ""
            if retrieved_episodes and self.callosum["memory"]:
                episodes_line += " (strength: strong > firm/familiar > faint > dream; then when it happened)"
            self.last_prompt_text = (
                f"You are {bot_name}, speaking with {user_name}.{care_line}\n"
                f"Current Manifold Coordinate: ({s},{a},{z}) [S={s}: {s_desc}; A={a}: {a_desc}; Z={z}: {z_desc}].\n"
                f"Active semantic weights lean toward: {weights_str}.\n"
                f"Underlying conceptual link: {prop} (path: {a_star_path})."
                f"{notes_line}{summary_line}{episodes_line}{sleep_line}{pressure_line}{idle_line}{self_facts}\n"
                f"Directive: Let the coordinate ({s},{a},{z}) and active semantic weights ({weights_str}) shape your tone and perspective naturally. "
                f"Respond natively without performative stage directions, parenthetical mood actions, or internal engine debug strings.{length_hint}"
                f"{memory_check_line}{self_rule}"
            )
            # What counts as "grounded" for careful learning: the user's words and what the BRAIN supplied (notes, memory
            # lines, its weights and path). Not the running summary (the LLM wrote it, so it would launder invented words)
            # and not the fixed template text (axis descriptions, directive), which would ground words like "reflection" every turn.
            self.last_ground_text = " ".join([user_text, notes_ground, " ".join(self.episodes_for_grounding(retrieved_episodes)),
                                              weights_ground, prop_ground, a_star_path])  # v24.1: no sleep lines
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
            + (f"• {idle_line.strip()}\n" if idle_line else "")
            + (f"• {self_facts.strip()}\n" if self_facts else "")
            + f"Directive: Reference your 3D coordinate ({s},{a},{z}), mood '{cell_mood}', and proposition [{prop}] explicitly.{length_hint}"
            + memory_check_line + self_rule
        )
        self.last_ground_text = " ".join([user_text, notes_ground, " ".join(self.episodes_for_grounding(retrieved_episodes)), weights_ground,
                                          prop_ground, a_star_path, self.strip_scaffold(pre_reply), " ".join(alpha_w + gamma_w + omega_w)])
        return self.last_prompt_text

    def strip_scaffold(self, text: str) -> str:
        """v22.7.2: drop the engine's built-in connecting words (verb phrases, templates) from text used for grounding.
        Older engines without scaffold_words() get the text back unchanged."""
        if not text or not hasattr(self.brain, "scaffold_words"):
            return text or ""
        scaffold = self.brain.scaffold_words()
        return " ".join(t for t in re.findall(r"[A-Za-z']+", text) if t.lower() not in scaffold)

    def episodes_for_grounding(self, memory_lines: list) -> list:
        """v22.7: what in the memory lines may ground a reply word. A past episode stores the user's words AND the voice's
        reply; only the user's half counts, or anything the voice said once would count as grounded whenever that episode
        came back. (The model still sees the whole line.) Source tags off: the whole line, as in v22.6.4."""
        tags_on = getattr(self.brain, "source_tags_on", False)
        out = []
        for t in memory_lines:
            if t.startswith("[Dream Synthesis"):
                continue  # v24.1: a dream is "not a real event": its words don't ground a reply
            if tags_on and t.startswith("[Past Episode"):
                t = re.sub(r" -> '.*$", "", t, flags=re.S)
            # v24.1: only the content grounds, not the line's labels ("Past Episode · familiar", "Fact taught by Matt
            # (strong)", "At (3,5,2), discussed", "Matt said")
            t = re.sub(r"^\[[^\]]*\]:\s*", "", t)
            t = re.sub(r"^Fact taught by [^:]*:\s*", "", t)
            t = re.sub(r"^At \(\d+,\d+,\d+\),\s*discussed\s*", "", t)
            t = re.sub(r"\b[A-Za-z]+ said '", "'", t)
            out.append(t)
        return out

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

    # v23.3.2 thinking models (gpt-oss, kimi, ...): they write hidden reasoning before the reply, in a separate field,
    # and it uses the same token budget. On the phone's 160-token budget they often ran out while thinking and sent an
    # empty reply. Once a model is seen thinking it is remembered: it gets reasoning_effort (OpenAI-style endpoint) or
    # think=false (native endpoint) plus extra tokens for its thinking, and an empty reply after thinking is retried once.
    # The reasoning text itself is never shown to the brain or learned.
    THINK_EFFORT = os.environ.get("TORRENT_REASONING_EFFORT", "low").strip().lower() or "low"
    THINK_EXTRA_TOKENS = int(os.environ.get("TORRENT_THINK_TOKENS", "1024"))

    def thinking_models(self) -> set:
        return {m for m in str(self.brain.knowledge_facts.get("_thinking_models", "")).split(",") if m}

    def _remember_thinking_model(self):
        models = self.thinking_models() | {self.model_name}
        self.brain.knowledge_facts["_thinking_models"] = ",".join(sorted(models))

    def stream_chat(self, messages: list, max_tokens: int, temperature: float, show_progress: bool = False) -> str:
        """v23.3.2: one chat request, with the thinking-model handling above."""
        known = self.model_name in self.thinking_models()
        text = self._stream_chat_once(messages, max_tokens, temperature, show_progress, thinking=known)
        if self._last_thinking_chars and not known:
            self._remember_thinking_model()
            if not text:
                if show_progress:
                    print(f"   [🧠 {self.model_name} is a thinking model: it ran out of room while thinking. "
                          f"Retrying with reasoning effort '{self.THINK_EFFORT}' and room to think.]")
                text = self._stream_chat_once(messages, max_tokens, temperature, show_progress, thinking=True)
        return text

    def _stream_chat_once(self, messages: list, max_tokens: int, temperature: float, show_progress: bool = False,
                          thinking: bool = False) -> str:
        """Send one chat request and read the answer as it streams in.
        Streaming matters on a slow PC: the timeout then only covers the wait for the model to START (and each
        pause between pieces), not the whole reply, so a long answer can't time out while the model is still writing."""
        headers = {"Content-Type": "application/json", "Authorization": "Bearer local-lan", "Connection": "close"}
        if thinking:
            max_tokens = max_tokens + self.THINK_EXTRA_TOKENS  # room for the hidden reasoning; the reply itself stays short
        if self.backend == "ollama":
            payload = {"model": self.model_name, "messages": messages, "stream": True, "keep_alive": LLM_KEEP_ALIVE,
                       "options": {"temperature": temperature, "num_predict": max_tokens}}
            if LLM_SEED.lstrip("-").isdigit():
                payload["options"]["seed"] = int(LLM_SEED)
            if thinking:
                payload["think"] = False  # honoured on Ollama's native /api/chat
        else:
            payload = {"model": self.model_name, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "stream": True}
            if LLM_SEED.lstrip("-").isdigit():
                payload["seed"] = int(LLM_SEED)
            if thinking:
                payload["reasoning_effort"] = self.THINK_EFFORT  # Ollama's /v1 endpoint ignores think=false but honours this
        self.last_finish_reason = ""
        self._last_thinking_chars = 0
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
                            delta = ch.get("delta") or ch.get("message") or {}
                            piece = delta.get("content") or ""
                            thought = delta.get("reasoning") or delta.get("reasoning_content") or ""
                            if thought:  # v23.3.2: counted, never kept
                                self._last_thinking_chars += len(thought)
                                if show_progress and self._last_thinking_chars % 400 < len(thought):
                                    print("·", end="", flush=True)
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
                        thought = (obj.get("message") or {}).get("thinking") or obj.get("thinking") or ""
                        if thought:  # v23.3.2: counted, never kept
                            self._last_thinking_chars += len(thought)
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
        """v22.6.4: the FIRST WHOLE WORD must be a question word. Before, word beginnings matched, so "Dogs are great"
        (do-), "Canada is cold" (can-) and "However it goes" (how-) counted as questions."""
        t = text.strip().lower()
        if "?" in t:
            return True
        first = re.findall(r"[a-z']+", t)[:1]
        return bool(first) and first[0].replace("'", "") in self.QUESTION_STARTS

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
            # v23.3: say the real reason (engine v23.3 adds time awake to the pressure, not only learning)
            why = []
            if self.brain.link_strength_added_since_sleep / self.brain.SLEEP_PRESSURE_BUSY_DAY >= 0.25:
                why.append("learned a lot since your last full sleep")
            if (rep.get("awake_hours") or 0) >= 6:
                why.append(f"been awake about {rep['awake_hours']:.0f} hours")
            reason = " and ".join(why) or "gone a long time since your last full sleep"
            pressure_line = (f"\nSleep pressure: {rep['level']} — you have {reason} and feel ready to rest. "
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
        lv = self.brain.levels() if hasattr(self.brain, "levels") else None
        arousal = lv["arousal"] if lv else 0.0
        temp -= 0.15 * arousal  # v23: a tense, aroused brain speaks more narrowly...
        temp = round(min(1.0, max(0.25, temp)), 2)
        length = min(1.3, max(0.5, 1.0 + 0.12 * vz - 0.07 * speed - 0.3 * arousal))  # ...and more briefly
        sentences = int(min(8, max(2, round(4.5 * length))))
        return {"temperature": temp, "sentences": sentences, "unsure": unsure,
                "velocity": [round(vs, 2), round(va, 2), round(vz, 2)], "arousal": round(arousal, 2)}

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
        with VOICE_LOCK:  # v24.1: waits for a speak-up being worded (see VOICE_LOCK)
            return self._call_local_llm(state_block, user_text, fallback_reply)

    def _call_local_llm(self, state_block: str, user_text: str, fallback_reply: str) -> str:
        self.last_used_fallback = False
        use_merged_user_role = self.is_mobile or self.force_merged_role or ("gemma" in self.model_name.lower() and self.backend == "openai")

        recent_slice = self.chat_history[-self.keep_raw_len:] if self.keep_raw_len > 0 else []
        if recent_slice and recent_slice[0].get("role") != "user":
            recent_slice = recent_slice[1:]
        recent_slice = [{"role": m["role"], "content": m["content"]} for m in recent_slice]  # v22.10: times stay out of the prompt

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
        if not self.connected:
            self.try_reconnect()  # v24.1.1: always, so the probe also picks this brain's model (it was skipped when the
            # default port answered, and the turn asked for the built-in default model and got a 404)
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
                    self.turn_tone = tone  # v24.1: the retry keeps this turn's tone (it fell back to the defaults)
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

    def _update_cell_again(self, s, a, z, words, allow_cleave):
        """v24.1: the reply's words join the cell the brain already visited this turn: not a second visit."""
        try:
            return self.brain.update_cell_centroid_and_emotion(s, a, z, words, allow_cleave=allow_cleave, count_visit=False)
        except TypeError:  # an engine older than v24.1
            return self.brain.update_cell_centroid_and_emotion(s, a, z, words, allow_cleave=allow_cleave)

    def grounded_words(self, user_text: str, user_concepts: list) -> set:
        """Words the model could have got from the user or the brain this turn (see last_ground_text), plus words
        already linked to the user's concepts."""
        ground = self.with_singulars(self.brain.clean_tokens(f"{user_text} {self.last_ground_text}".replace("-", " ")))
        trusted = getattr(self.brain, "trusted_strength", None)  # v22.7: only the user's/notes'/legacy share counts
        for uc in user_concepts[:5]:
            ground |= {nb for nb, wt in self.brain.assoc_graph.get(uc, {}).items()
                       if (trusted(uc, nb) if trusted else wt) >= 0.45}
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
        voice_check = (self.brain.check_voice(llm_concepts, self.voice_predicted)
                       if getattr(self, "voice_predicted", None) is not None and not self.last_used_fallback else None)
        cleavage_count_before = len(self.brain.cleavage_log)
        # Engine v22: learning from the reply is waking learning, so it builds sleep pressure like the user's words do
        # (the engine only counts what happens inside respond(), and this runs after it). Older engines ignore this.
        reply_cell_mass_before = sum(sum(v.values()) for v in self.brain.cortical_cells.values())
        self.brain.awake_turn = True
        old_src = self.brain.set_wire_source("voice") if hasattr(self.brain, "set_wire_source") else None  # v22.7

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
                self._update_cell_again(s, a, z, wired_concepts, allow_cleave=False)
        else:
            ideas_before = len(self.brain.idea_memory)
            try:  # v24.1: the idea's link is made below, after the grounding check (it used to be made first, at full
                extracted_prop = self.brain.extract_proposition(normalized_reply, llm_tokens, pure_llm_concepts, cell_key,
                                                                wire=False)  # strength, even for invented words)
            except TypeError:  # an engine older than v24.1
                extracted_prop = self.brain.extract_proposition(normalized_reply, llm_tokens, pure_llm_concepts, cell_key)
            prop_wire = extracted_prop.pop("_wire", None) if extracted_prop else None
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
                    if prop_wire and self.held_back_links != "none":  # v24.1: held back like its words: a quarter, faint
                        self.brain.wire_concepts(prop_wire[0], prop_wire[1], amount=0.25 * prop_wire[2], min_link=0.01)
                    prop_wire = None
            if prop_wire:
                self.brain.wire_concepts(prop_wire[0], prop_wire[1], amount=prop_wire[2])
            self.brain.cortical_cells.setdefault(cell_key, {})
            for c in wired_concepts:
                if c not in grounded and self.held_back_links == "none":
                    continue  # v22.6.4 test switch: held-back words get no links at all
                self.brain.get_or_create_vector(c, context_vec=cell_vec)
                # v22.11 seen-once rule: a word the user has typed in only one turn so far stays faint here too
                provisional = hasattr(self.brain, "is_provisional_word") and self.brain.is_provisional_word(c)
                k = 1.0 if (c in grounded and not provisional) else 0.25
                if c in grounded and not provisional:
                    self.brain.cortical_cells[cell_key][c] = self.brain.cortical_cells[cell_key].get(c, 0) + 1
                # v22.10: a held-back word's link stays at its quarter strength (the engine's 0.25 minimum used to round it up)
                faint = {"min_link": 0.01} if k < 1.0 else {}
                if ponder_bridge and c != ponder_bridge:
                    self.brain.wire_concepts(ponder_bridge, c, amount=0.65 * k, **faint)
                if user_concepts and c != user_concepts[0]:
                    self.brain.wire_concepts(user_concepts[0], c, amount=0.55 * k, **faint)
            wired_concepts = [c for c in wired_concepts if c in grounded]

            if combined_coherence < 0.25 and pure_llm_concepts:
                outlier = min(pure_llm_concepts, key=lambda w: self.brain.dot(self.brain.vectors.get(w, cell_vec), cell_vec))
                self.brain.apply_dialectical_repulsion(ponder_bridge, outlier, rate=0.04)

            self._update_cell_again(s, a, z, wired_concepts, allow_cleave=True)
            tectonic_logs = self.brain.run_crystal_annealing_and_tectonics()

        self.brain.awake_turn = False
        if hasattr(self.brain, "set_wire_source"):
            self.brain.set_wire_source(old_src)
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
            "selfMatch": voice_check.get("selfMatch") if voice_check else None,      # v22.5 efference copy
            "unpredictedWords": voice_check.get("unpredicted", []) if voice_check else [],
            "surprise": getattr(self.brain, "last_surprise", None),
            "memoryStrength": self.memory_strength,
            # v22.7: share of the reply's key words that were grounded (1 = all; a native fallback reply is the brain's own)
            "groundedShare": (1.0 if (self.last_used_fallback or not pure_llm_concepts or not self.callosum["memory"])
                              else round(1 - len(held_back) / len(pure_llm_concepts[:4] if self.voice_mode != "ATTENUATED" else pure_llm_concepts), 2)),
            "llmPropositionLearned": extracted_prop["summary"] if extracted_prop else None,
            "retrievedPastEpisodes": self.last_retrieved_episodes,
            "postShearStress": shear_after,
            "cleavageEventsTriggered": [ev["summary"] for ev in new_cleavages],
            "tectonicLogs": tectonic_logs,
            "thoughtClaims": self.thought_claim_check(llm_reply) if not self.last_used_fallback else None,  # v23.5.2
        }

        if self.slant_on and not self.last_used_fallback:
            post_report["slant"] = self.slant_measure(user_text, llm_reply, pure_llm_concepts, user_concepts, post_report["selfMatch"])
            self.slant_record(post_report["slant"])
        self.last_post_audit = post_report
        if self.brain.last_audit is not None:
            self.brain.last_audit["llmPostProcessor"] = post_report
        # (no save here: record_turn_and_maybe_summarize saves the brain right after this, so one save per turn)
        self.brain.export_trace_file("latest_trace.json")
        return post_report


def run_chat_turn(brain, middleware, voice_io, user_input, show_telemetry=True, show_grid=False):
    """v23.5.4: one whole message turn (brain -> voice -> post-processing -> screen), shared by the terminal and
    the face page chat, so a message typed in either place is handled exactly the same way. Returns the prompt sent."""
    # Execute the full 3-stage Brain -> LLM -> Post-Processor turn
    user_input = fix_dropped_apostrophes(user_input)  # v23.5.5: "ill be" -> "I'll be" (voice-to-text)
    middleware.user_sent_at = time.time()  # v22.10
    if middleware.show_timestamps:
        print(f"   🕒 {clock_text()}")
    middleware.take_snapshot(user_input)  # for /back
    pre_reply, audit, salient_c = brain.respond(user_input)
    FACE.update(brain, mode="thinking", heard=user_input)  # v23.3.4: the levels have moved; the voice is writing
    last_system_prompt = middleware.build_state_injection(user_input, pre_reply, audit, salient_c)
    llm_reply = middleware.call_local_llm(last_system_prompt, user_input, fallback_reply=pre_reply)
    post_report = middleware.post_process_llm_response(user_input, llm_reply, audit, salient_c)
    middleware.record_turn_and_maybe_summarize(user_input, llm_reply, audit, salient_c)
    middleware.undo_ready = True

    bot_speaker = brain.user_profile.get("bot_name") or "[Manifold]"
    print(f"\n🤖 {bot_speaker} ({'native' if middleware.last_used_fallback else middleware.model_name})"
          + (f" · {clock_text()}" if middleware.show_timestamps else "") + f": {llm_reply}")

    FACE.update(brain, mode="speaking" if voice_io.tts_enabled else "awake", reply=llm_reply)  # v23.3.4
    if voice_io.tts_enabled:
        voice_io.speak(llm_reply)
        FACE.update(brain)
    if hasattr(brain, "mark_turn_end"):
        brain.mark_turn_end()  # v22.9: silence starts after the voice has replied

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
            + (f" | {brain.surprise_report()}" if hasattr(brain, "surprise_report") and brain.surprise_report() else "")
            + (f" | self-match {post_report['selfMatch']:.0%}" if post_report.get("selfMatch") is not None else "")
            + (" | " + nightmare_text("🌑 nightmare") if getattr(brain, "nightmare_mode", False) else "")
            + (" | 💊 mood level" if getattr(brain, "mood_level_on", False) and not getattr(brain, "levels_on", False) else "")
            + (f" | ⚡{brain.levels()['arousal']:.2f} ☯{brain.levels()['valence']:+.2f}"
               + (f" ✨{brain.levels()['novelty']:.2f} 💤{brain.levels()['sleep']:.2f}" if "novelty" in brain.levels() else "")
               if hasattr(brain, "levels") and brain.levels() else "")
            + (f" | 🎭 {brain.tone_word(brain.last_tone)} {brain.last_tone:+.2f}"  # v23.4.1 tone sense (measured only)
               if getattr(brain, "last_tone", None) is not None else "")
            + (f" | 💭 idle{' (live)' if brain.idle_this_turn.get('live') else ''} {brain.idle_this_turn['minutes']:.0f} min: {brain.idle_path_text(brain.idle_this_turn) if hasattr(brain, 'idle_path_text') else ' > '.join(brain.idle_this_turn['path'])} ({brain.idle_this_turn['mood']})"
               + (" [" + ", ".join(f"{k} {v}" for k, v in brain.idle_this_turn["counts"].items() if v) + "]"
                  if brain.idle_this_turn.get("counts") else "")
               + (" ⏳ felt " + (f"{brain.idle_this_turn['felt']['passing_min']:.0f}/" if brain.idle_this_turn['felt'].get('passing_min') is not None else "")
                  + f"{brain.idle_this_turn['felt']['looking_back_min']:.0f} min"  # v24.0 felt time (while passing / looking back)
                  if brain.idle_this_turn.get("felt") else "")
               if getattr(brain, "idle_this_turn", None) else "")
            + (f" | 📐 {post_report['slant']['stock']} stock, {post_report['slant']['ungrounded']}/{post_report['slant']['candidates']} ungrounded"
               + (f", 🪞 {post_report['slant'].get('selfTalk', 0)}/{post_report['slant']['sentences']} self" if 'selfTalk' in post_report['slant'] else "")
               if post_report.get("slant") else "")
            + (f" | 💭? unbacked thought claim: '{cut_at_word(post_report['thoughtClaims']['unbacked'][0], 40)}'"  # v23.5.2
               if (post_report.get("thoughtClaims") or {}).get("unbacked") else "")
            + "]"
        )
    if show_grid:
        print("\n" + brain.print_overlay_lattice(audit))
    FACE.chat_add("you", user_input)  # v23.5.4: the face page chat shows terminal turns too
    FACE.chat_add("bot", llm_reply)
    return last_system_prompt


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
    print(f" 🧠 {header_identity} · T.O.R.R.E.N.T. Brain + Local LLM Vocal Cortex")
    print(f"    Versions   : engine v{ENGINE_VERSION or 'older than 22.6.1'} | bridge v{BRIDGE_VERSION}"
          + ("" if ENGINE_VERSION == BRIDGE_VERSION else "   ⚠️ these don't match: replace BOTH torrentengine.py and ltcmbridge.py"))
    print(f"    Platform   : {platform_badge} | GloVe Vocab: {len(brain.raw_glove):,} vectors"
          + ("   ⚠️ TEST MODE: built-in words only (put torrent_wordspace_50k.gz next to torrentengine.py)" if not brain.raw_glove else ""))
    print(f"    Prompt Mode: {'WHEELS-OFF 🚀 (Raw Spatial Telemetry)' if not brain.training_wheels else 'WHEELS-ON 🛞 (Scaffolding)'}")
    print(f"    Efference  : {middleware.voice_mode_badge()} | Local TTS: {'ON 🔊' if voice_io.tts_enabled else 'OFF 🔇 (/tts)'}")
    if getattr(brain, "nightmare_mode", False):
        print(nightmare_text("    Nightmare  : 🌑 ON (lean-up rules off for this brain; /nightmare to turn off)"))
    if getattr(brain, "mood_level_on", False):
        print("    Mood level : 💊 ON (experimental v22.6; /moodlevel to turn off)")
    if getattr(brain, "idle_on", False):
        print("    Idle time  : 💭 ON (experimental v22.9; /idle to turn off)")
    if getattr(brain, "rhythm_on", False):  # v24.0
        print(f"    Day rhythm : 🌙 {brain.rhythm_status()} (/rhythm off)")
    if hasattr(brain, "source_tags_on") and not brain.source_tags_on:
        print("    Sources    : ⚪ source tags OFF (v22.6.4 behaviour; /sourcetags to turn on)")
    if middleware.held_back_links != "faint":
        print("    Held back  : ✂️ NONE (test switch: invented reply words get no links; /heldback faint to undo)")
    print(f"    Memory     : {len(middleware.episodic_archive)} Past Episodes | Summary: {'ACTIVE 📜' if middleware.running_summary else 'Fresh Session'}")
    print(f"    Backend    : {middleware.backend.upper()} | Active Model: {middleware.model_name} ({middleware.endpoint})")
    print(f"    Status     : {status_str}")
    print("-" * 86)
    print(" Voice Commands  : /tts (toggle speech out), /listen [sec] (mic STT in), /voicechat [sec] (hands-free loop; say \"stop voice chat\" to leave)")
    print(" Bridge Commands : /memory [compress], /mode <sovereign|attenuated|full>, /test, /connect, /models, /model, /prompt, /post")
    print(" Notes & Undo    : /note <key>: <text>, /notes, /notes delete <n>, /recall <word>, /back (undo your last message)")
    print(" Callosum        : /callosum [on|off], /callosum memory on|off, /callosum tone on|off  (see the tone with /prompt)")
    print(" Telemetry       : /slant (measure how much of each reply is the model's own habit), /slant report, /timestamps, /face (live face of the levels)")
    print(" People          : /whoami <name> (someone else is talking), /whoami (back to the caretaker), /people, /tectonics (show every cleavage)")
    print(" Test switches   : /idle why (last idle choices + reasons), /idle menu (choices on/off), /live (live idle on/off, experimental), /speak (speaking up on/off, needs /live), /rhythm (daily rhythm on/off/±hours), /voicestyle inward|outward (A/B: outward-looking voice), /heldback faint|none (how invented reply words are learned), /sourcetags (on/off)")
    print(" TORRENT Commands: /wheels, /export, /crystals, /ponder, /sleep, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /nightmare, /moodlevel, /levels, /idle, /facts, /facts forget <word>, /read, /exit")
    print("=" * 86)

    brain.run_boot_calibration_and_handshake()
    if not CLI_VOICE_MODE:
        middleware.voice_mode = middleware.resolve_voice_mode()

    show_telemetry, show_grid, last_system_prompt = True, False, ""

    # v23.3.4 face visualizer: starts by itself if this brain had it on last time (or TORRENT_FACE=1)
    _face_env = os.environ.get("TORRENT_FACE", "").strip()
    if _face_env == "1" or (_face_env != "0" and brain.knowledge_facts.get("_face") == "on"):
        if FACE.start():
            FACE.update(brain)
            print(f"[🙂 Face visualizer: {FACE.url}  (open it in your browser; /face off to stop)]")

    # v23.5.4 chat from the face page: the same turn as the terminal (reads show_telemetry / show_grid as they are now)
    FACE.chat_runner = lambda text: run_chat_turn(middleware.brain, middleware, voice_io, text, show_telemetry, show_grid)

    if getattr(brain, "people", None):  # v23.2: this brain knows more than one person, so ask who's here
        care = brain.caretaker_name().capitalize() or "the caretaker"
        names = ", ".join(n.capitalize() for n in brain.people)
        try:
            who = input(f"\n👥 Who's talking? ({names}; Enter = {care}): ").strip()
        except (KeyboardInterrupt, EOFError):
            who = ""
        if who.startswith("/"):  # v23.4.1: a command typed here was taken as a person's name
            print(f"[👤 '{who}' looks like a command, not a name: talking as {care}. Type the command again at the prompt.]")
            who = ""
        brain.whoami(who)
        print(f"[👤 Talking as: {brain.speaker_name().capitalize()}]")

    # v23.5 live idle: starts by itself if this brain had it on last time (or TORRENT_LIVE=1)
    _live_env = os.environ.get("TORRENT_LIVE", "").strip()
    if hasattr(brain, "live_tick") and (_live_env == "1" or (_live_env != "0" and brain.knowledge_facts.get("_live") == "on")):
        _ok = all(getattr(brain, k, False) for k in ("idle_on", "levels_on", "idle_menu_on"))
        if _ok:
            brain.set_live(True)
            LIVE.start(brain, middleware, voice_io)
            if brain.knowledge_facts.get("_speak") == "on" and hasattr(brain, "set_speak"):  # v23.5.3
                brain.set_speak(True)
            print(f"[🕰️ Live idle: on. It spends silences as they happen (/live off to stop).]")
            print("[💬 Speaking up: " + ("on (/speak off)]" if getattr(brain, "speak_on", False) else "off (/speak on)]"))  # v23.5.5

    _held = False  # v23.5: the chat loop holds BRAIN_LOCK from the moment you press Enter until the next prompt
    while True:
        if _held:
            BRAIN_LOCK.release()
            _held = False
        FACE.update(brain)  # v23.3.4 (does nothing unless /face is on)
        try:
            u_name = brain.speaker_name() if hasattr(brain, "speaker_name") else brain.user_profile.get("user_name", "").strip()  # v23.2
            user_tag = f"You ({u_name.capitalize()})" if u_name else "You"
            mode_badge = "🛞" if brain.training_wheels else "🚀"
            tts_badge = " 🔊" if voice_io.tts_enabled else ""
            LIVE.prompt_text = f"\n👤 {user_tag} [{mode_badge} | {middleware.voice_mode}{tts_badge}]: "  # v23.5.3
            user_input = input(LIVE.prompt_text).strip()
            BRAIN_LOCK.acquire()  # v23.5: from here until the next prompt, the live clock waits
            _held = True
        except (KeyboardInterrupt, EOFError):
            if not _held:
                BRAIN_LOCK.acquire()
                _held = True
            LIVE.stop()
            rec = brain.idle_before_exit() if hasattr(brain, "idle_before_exit") else None  # v22.9
            if rec:
                print(f"[💭 Before sleep ({rec['minutes']:.0f} min since the last message), its thoughts wandered: "
                      f"{brain.idle_path_text(rec)} ({rec['mood']})]")
            FACE.update(brain, mode="asleep")  # v23.3.4
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
                          "/model", "/test", "/tts", "/export", "/connect", "/callosum", "/slant", "/heldback", "/timestamps", "/face"}  # /sourcetags changes the brain, so it cancels /back
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
            rec = brain.idle_before_exit() if hasattr(brain, "idle_before_exit") else None  # v22.9
            if rec:
                print(f"[💭 Before sleep ({rec['minutes']:.0f} min since the last message), its thoughts wandered: "
                      f"{brain.idle_path_text(rec)} ({rec['mood']})]")
            FACE.update(brain, mode="asleep")  # v23.3.4
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
            try:
                FACE.update(brain, mode="listening")  # v23.4.1
                spoken_text = voice_io.listen_and_transcribe(duration_sec=sec)
            except (KeyboardInterrupt, EOFError):  # v23.4.1: Ctrl+C while recording cancels, the bridge keeps running
                print("\n  [i] Recording cancelled.")
                continue
            if not spoken_text:
                print("  [i] No speech detected." + (f" ({voice_io.last_listen_note})" if voice_io.last_listen_note else ""))
                continue
            print(f"🗣️ Transcribed: \"{spoken_text}\"")
            user_input = spoken_text

        elif cmd_word == "/voicechat":
            # v23.4.1: /voicechat N records N seconds a turn (default 5); saying "stop voice chat", typing q, or
            # Ctrl+C goes back to text; silence and Whisper's silence phantoms never reach the brain
            parts = cmd.split()
            sec = max(2, min(60, int(parts[1]))) if len(parts) > 1 and parts[1].isdigit() else 5
            voice_io.tts_enabled = True
            print(f"\n🎙️ [HANDS-FREE VOICE CHAT: {sec} s per turn. Press Enter to speak. To leave: type q, say "
                  f"\"stop voice chat\", or press Ctrl+C]")
            heard_now = None
            while True:
                try:
                    heard_now = None
                    # v24.1: the brain lock is let go while waiting and recording, so live idle and the face page
                    # aren't frozen for the whole voice session; it's taken back for the turn itself
                    BRAIN_LOCK.release()
                    try:
                        sub = input(f"\n[Press Enter to record {sec}s of speech, or 'q' to return to text]: ").strip().lower()
                        if sub in ("q", "quit", "exit"):
                            break
                        FACE.update(brain, mode="listening")  # v23.3.4
                        spoken_text = voice_io.listen_and_transcribe(duration_sec=sec)
                    finally:
                        while True:  # v24.1.1: Ctrl+C while waiting here must not leave the loop without the lock
                            try:
                                BRAIN_LOCK.acquire()
                                break
                            except KeyboardInterrupt:
                                continue
                    if not spoken_text:
                        print("  [i] No speech detected." + (f" ({voice_io.last_listen_note})" if voice_io.last_listen_note else ""))
                        FACE.update(brain)
                        continue
                    if voice_io.is_exit_phrase(spoken_text):
                        print(f"🗣️ You said: \"{spoken_text}\"  [🎙️ back to text]")
                        break
                    print(f"🗣️ You said: \"{spoken_text}\"")
                    heard_now = spoken_text
                    # v24.1: the same turn as typed messages (the "I'll" fix, the face page's chat log, the status line)
                    last_system_prompt = run_chat_turn(brain, middleware, voice_io, spoken_text, show_telemetry, show_grid)
                    heard_now = None
                except (KeyboardInterrupt, EOFError):  # v23.4.1: back to text instead of crashing the bridge
                    if heard_now:
                        middleware.undo_ready = True  # the snapshot was taken before the brain heard it
                        if hasattr(brain, "mark_turn_end"):
                            brain.mark_turn_end()
                    print("\n[🎙️ Voice chat stopped: back to text.]"
                          + (f" (The brain had already heard \"{heard_now}\"; /back undoes it.)" if heard_now else ""))
                    break
            FACE.update(brain)
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
                when = f"[{clock_text(m['time'])}] " if m.get("time") else ""  # v22.10
                print(f"  {when}{r_tag}: {m['content'][:120]}")
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

        elif cmd.startswith("/voice") and cmd_word not in ("/voicechat", "/voicestyle"):
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
            if middleware.connected:
                middleware.save_last_host(middleware.base_url)  # v23.5.2: tried first next time
                print(f"  [💾] Next startup tries {middleware.base_url} first.")
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
            print("\n💉 LAST INJECTED STATE PROMPT:\n" + (middleware.last_prompt_text or last_system_prompt or "(Run a turn first.)"))
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

        elif cmd_word == "/sourcetags":
            if not hasattr(brain, "set_source_tags"):
                print("This engine has no source tags (needs torrentengine v22.7 or newer).")
                continue
            brain.set_source_tags(not brain.source_tags_on)
            brain.save_memory()
            print(f"[🏷️ Source tags are now {'ON: only your words, notes and old links count as grounded' if brain.source_tags_on else 'OFF (v22.6.4 behaviour)'}]")
            continue

        elif cmd_word == "/tectonics":  # v23.2
            if not hasattr(brain, "set_tectonics"):
                print("This engine always prints every cleavage (needs torrentengine v23.2 or newer).")
                continue
            brain.set_tectonics(not brain.show_tectonics)
            brain.save_memory()
            print(f"[🌋 Cleavage/annealing detail is now {'ON: every event is printed' if brain.show_tectonics else 'OFF: one summary line per turn or sleep'}]")
            continue

        elif cmd_word in ("/whoami", "/people"):  # v23.2 multi-person
            if not hasattr(brain, "whoami"):
                print("This engine doesn't know about people yet (needs torrentengine v23.2 or newer).")
                continue
            if cmd_word == "/people":
                for line in brain.people_status():
                    print(f"  👥 {line}")
                continue
            parts = user_input.strip().split(maxsplit=1)
            brain.whoami(parts[1] if len(parts) > 1 else "")  # v23.4.1: /whoami alone goes back to the caretaker (it only showed who)
            brain.save_memory()
            print(f"[👤 Talking as: {brain.speaker_name().capitalize() or '(no name yet)'} (caretaker: {brain.caretaker_name().capitalize() or '(none)'})]")
            continue

        elif cmd_word == "/levels":  # v23
            if not hasattr(brain, "set_levels"):
                print("This engine has no chemical levels (needs torrentengine v23 or newer).")
                continue
            if cmd.split()[1:2] == ["show"]:  # v23.3: look without switching
                print(f"[⚗️ Chemical levels: {brain.levels_status()}]")
                continue
            brain.set_levels(not brain.levels_on)
            brain.save_memory()
            print(f"[⚗️ Chemical levels are now {'ON (' + brain.levels_status() + ')' if brain.levels_on else 'OFF (v22.11 behaviour)'}]")
            continue

        elif cmd_word == "/read":  # v23.4.1 reading mode (book lines: no reply, no chat history, links tagged "book")
            if run_read_command is None:
                print("This engine has no /read (needs torrentengine v23.4.1 or newer).")
                continue
            close_live_silence(brain)  # v23.5
            FACE.update(brain, mode="reading")
            run_read_command(brain, user_input[5:], on_event=lambda m: FACE.update(brain, mode=m))
            continue

        elif cmd_word == "/speak":  # v23.5.3 speaking up (experimental; needs live idle)
            if not hasattr(brain, "set_speak"):
                print("This engine can't speak up (needs torrentengine v23.5.3 or newer).")
                continue
            arg = cmd.split()[1:2]
            if arg in (["on"], ["off"]):
                brain.set_speak(arg == ["on"])
                brain.knowledge_facts["_speak"] = arg[0]
                brain.save_memory()
                print(f"[💬 Speaking up: {arg[0].upper()}"
                      + (" (it can message you first while you're away; only with /live on)" + ("" if LIVE.running else ". Live idle is off: /live on")
                         if arg == ["on"] else "") + "]")
            elif arg:
                print("Usage: /speak on | /speak off | /speak")
            else:
                h = getattr(brain, "idle_habits", {}).get("speak", 0.0)
                print(f"[💬 Speaking up: {'ON' if brain.speak_on else 'OFF (/speak on)'} | speak habit {h:+.2f} | "
                      f"unanswered in a row: {getattr(brain, 'speak_unanswered', 0)} | lines this session: {LIVE.spoke}]")
            continue

        elif cmd_word == "/rhythm":  # v24.0 daily rhythm (experimental; acts on idle choices only)
            if not hasattr(brain, "set_rhythm"):
                print("This engine has no daily rhythm (needs torrentengine v24.0 or newer).")
                continue
            arg = cmd.split()[1:2]
            if arg in (["on"], ["off"]):
                brain.set_rhythm(arg == ["on"])
                brain.save_memory()
            elif arg and re.fullmatch(r"[+-]?\d+(\.5)?", arg[0]):
                brain.set_rhythm_offset(float(arg[0]))
                brain.save_memory()
            elif arg:
                print("Usage: /rhythm on | /rhythm off | /rhythm +3 (its night 3 hours later) | /rhythm 0 | /rhythm")
                continue
            print(f"[🌙 Daily rhythm: {brain.rhythm_status()}. It only changes what the brain chooses while left alone"
                  " (night: sleep and doze come easier; afternoon: sleep comes harder).]")
            continue

        elif cmd_word == "/live":  # v23.5 live idle (experimental)
            if not hasattr(brain, "live_tick"):
                print("This engine has no live idle (needs torrentengine v23.5 or newer).")
                continue
            arg = cmd.split()[1:2]
            if arg == ["on"]:
                missing = [n for n, k in (("idle time (/idle)", "idle_on"), ("levels (/levels)", "levels_on"),
                                          ("the option menu (/idle menu)", "idle_menu_on")) if not getattr(brain, k, False)]
                if missing:
                    print(f"[🕰️ Live idle needs {', '.join(missing)} switched on first.]")
                    continue
                brain.set_live(True)
                LIVE.start(brain, middleware, voice_io)
                if brain.knowledge_facts.get("_speak") == "on" and hasattr(brain, "set_speak"):  # v24.1, as at start-up
                    brain.set_speak(True)
                brain.knowledge_facts["_live"] = "on"
                brain.save_memory()
                print("[🕰️ Live idle: ON. Silences are spent as they happen, one choice at a time (watch it on /face).\n"
                      "   After your next message, the usual 💭 line tells the whole silence. /live off to stop.]")
            elif arg == ["off"]:
                rec = close_live_silence(brain)
                brain.set_live(False)
                LIVE.stop()
                brain.knowledge_facts["_live"] = "off"
                brain.save_memory()
                print("[🕰️ Live idle: OFF. Silences are spent all at once when the next message arrives (as before).]")
            elif arg:
                print("Usage: /live on | /live off | /live")
            else:
                print(f"[🕰️ Live idle: {LIVE.status()}]" + ("  (type /live on to start it)" if not LIVE.running else ""))
            continue

        elif cmd_word == "/face":  # v23.3.4 face visualizer
            if cmd.split()[1:2] == ["off"]:
                FACE.stop()
                brain.knowledge_facts["_face"] = "off"
                brain.save_memory()
                print("[🙂 Face visualizer stopped.]")
                continue
            url = FACE.start()
            if not url:
                print("[🙂 Couldn't start the face visualizer: ports 8765-8774 are all busy (set TORRENT_FACE_PORT).]")
                continue
            brain.knowledge_facts["_face"] = "on"  # remembered for this brain: it starts by itself next time
            brain.save_memory()
            FACE.update(brain)
            opened = FACE.open_in_browser(IS_MOBILE)
            print(f"[🙂 Face visualizer: {url}  ({'opening it in your browser' if opened else 'open this in your browser'}; "
                  f"/face off to stop)]")
            continue

        elif cmd_word == "/timestamps":  # v22.10
            middleware.show_timestamps = not middleware.show_timestamps
            brain.knowledge_facts["_timestamps"] = "on" if middleware.show_timestamps else "off"
            brain.save_memory()
            print(f"[🕒 Timestamps on screen: {'ON' if middleware.show_timestamps else 'OFF'} (times are always saved in the chat history)]")
            continue

        elif cmd_word == "/heldback":
            arg = cmd.split()[1:2]
            if arg and arg[0] in ("faint", "none"):
                middleware.held_back_links = arg[0]
                brain.knowledge_facts["_held_back_links"] = arg[0]
                brain.save_memory()
            elif arg:
                print("Usage: /heldback faint | /heldback none")
                continue
            print(f"[✂️ Held-back reply words: {middleware.held_back_links.upper()}"
                  + (" (linked at a quarter strength, as before)" if middleware.held_back_links == "faint" else " (not linked at all; test setting)") + "]")
            continue

        elif cmd_word == "/slant":
            if cmd.split()[1:2] == ["report"]:
                print("\n📐 SLANT TELEMETRY (averages per model)")
                for line in middleware.slant_report():
                    print("   " + line)
            else:
                middleware.set_slant(not middleware.slant_on)
                brain.save_memory()
                print(f"[📐 Slant telemetry is now {'ON: each reply is measured and logged (numbers only). /slant report to compare models' if middleware.slant_on else 'OFF'}]")
            continue

        elif cmd.startswith("/export"):
            parts = user_input.split(maxsplit=1)
            fname = parts[1].strip() if len(parts) > 1 else "latest_trace.json"
            out = brain.export_trace_file(fname)
            print(f"💾 Exported 3D 10-step R vs ¬R + LLM Post-Audit trace to: {out}" if out else "Nothing to export yet: send a message first.")
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
            close_live_silence(brain)  # v23.5: a live silence already lived counts before the nap
            parts = cmd.split()
            hrs = float(parts[1]) if len(parts) > 1 and parts[1].replace(".", "", 1).isdigit() else 4.0
            FACE.update(brain, mode="asleep")  # v23.3.4
            for r_line in brain.run_stasis_sleep_pass(hrs):
                print(f"  • {r_line}")
            if hasattr(brain, "mark_turn_end"):
                brain.mark_turn_end()  # v22.9: a nap isn't idle time
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
            close_live_silence(brain)  # v23.5
            for d in brain.run_dream_cycle(3):
                print(f"   💭 {d}")
            if hasattr(brain, "mark_turn_end"):
                brain.mark_turn_end()  # v22.9: dreaming isn't idle time
            brain.synthesize_emergent_bot_name()
            brain.save_memory()
            continue

        elif cmd == "/nightmare":
            if not hasattr(brain, "nightmare_mode"):
                print("This engine has no nightmare mode (needs torrentengine v22.3 or newer).")
                continue
            brain.nightmare_mode = not brain.nightmare_mode
            brain.save_memory()
            print(nightmare_text(f"[🌑 Nightmare mode is now {'ON: the lean-up rules are off for this brain' if brain.nightmare_mode else 'OFF'}]"))
            continue

        elif cmd_word == "/voicestyle":  # v23.3.1 test switch
            arg = (cmd.split()[1:2] or [""])[0].lower()
            new = arg if arg in ("inward", "outward") else ("outward" if middleware.voice_style == "inward" else "inward")
            middleware.set_voice_style(new)
            brain.save_memory()
            print(f"[🗣️ Voice style is now {new.upper()}: " + ("the voice looks outward at you and the topic; feelings only when asked; no engine words]"
                  if new == "outward" else "as before (the coordinate shapes tone and perspective)]"))
            continue

        elif cmd_word == "/idle" and cmd.split()[1:2] in (["why"], ["menu"]):  # v23.4 option menu
            if not hasattr(brain, "idle_choices_text"):
                print("This engine has no idle option menu (needs torrentengine v23.4 or newer).")
                continue
            if cmd.split()[1] == "menu":
                brain.set_idle_menu(not brain.idle_menu_on)
                brain.save_memory()
                print(f"[💭 Idle choices are now {'ON (wander, leap, replay, doze, sleep)' if brain.idle_menu_on else 'OFF (plain v23.3 walk)'}]")
                continue
            lines = brain.idle_choices_text()
            print("[💭 Last idle time, choice by choice:]" if lines else "[💭 No idle choices recorded yet.]")
            for ln in lines:
                print(f"  {ln}")
            print(f"  habits: {brain.idle_habits_status()}")
            continue

        elif cmd == "/idle":
            if not hasattr(brain, "set_idle"):
                print("This engine has no idle time (needs torrentengine v22.8 or newer).")
                continue
            brain.set_idle(not brain.idle_on)
            brain.save_memory()
            print(f"[💭 Idle time is now {'ON: between messages the brain wanders its own links (experimental)' if brain.idle_on else 'OFF'}]")
            continue

        elif cmd == "/moodlevel":
            if not hasattr(brain, "set_mood_level"):
                print("This engine has no mood level (needs torrentengine v22.6 or newer).")
                continue
            brain.set_mood_level(not brain.mood_level_on)
            brain.save_memory()
            print(f"[💊 Mood level is now {'ON: the calm axis clears like a blood level; split words rest 80 turns' if brain.mood_level_on else 'OFF'}]")
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

        elif cmd.startswith("/facts forget"):
            target = user_input.strip()[len("/facts forget"):].strip()
            removed = brain.forget_fact(target) if (target and hasattr(brain, "forget_fact")) else None
            if not hasattr(brain, "forget_fact"):
                print("This engine can't forget facts (needs torrentengine v22.4 or newer).")
            elif removed is None:
                print("Usage: /facts forget <word>   (see the list with /facts)" if not target else f"No taught fact for '{target}'.")
            else:
                middleware.undo_ready = False  # /back would bring the fact back
                brain.save_memory()
                print(f"[🗑️ Forgot the fact '{target.lower()}' -> {removed}. The word itself stays.]")
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
            # v24.1: stop the live clock first (it kept ticking the erased brain), and carry this session's bridge
            # settings over to the new brain so they are saved with it
            LIVE.stop()
            keep = {k: brain.knowledge_facts[k] for k in ("_voice_mode", "_voice_style", "_held_back_links", "_timestamps",
                                                         "_face", "_preferred_model", "_slant_on", "_thinking_models")
                    if k in brain.knowledge_facts}
            old_notes = middleware.notes_path()  # v24.1.1: the erased brain's notes go too (a new brain with the same
            old_file = release_brain(old_file)  # name would have read them as its own confirmed notes)
            if os.path.exists(old_file):
                os.remove(old_file)
            if os.path.exists(old_notes):
                os.remove(old_notes)
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
            middleware.recent_idle, middleware.recent_idle_turns = None, 0  # v24.1: not the old brain's time alone
            brain.knowledge_facts.update(keep)
            print("🧠 3D Toroidal Brain wiped and reset." + (" Live idle is off for the new brain (/live on)."
                                                             if hasattr(brain, "live_tick") else ""))
            brain.run_boot_calibration_and_handshake()
            brain.save_memory()
            FACE.update(brain, mode="awake")
            continue

        elif cmd.startswith("/") and not cmd.startswith("/listen") and not cmd.startswith("/mic"):
            print("Voice Commands  : /tts, /listen [sec], /voicechat")
            print("Bridge Commands : /memory [compress], /mode <sovereign|attenuated|full>, /test, /connect, /models, /model, /prompt, /post")
            print("Notes & Undo    : /note <key>: <text>, /notes, /notes delete <n>, /recall <word>, /back (undo your last message)")
            print("TORRENT Commands: /wheels, /export, /crystals, /ponder, /sleep, /emotions, /think, /ideas, /dream, /telemetry, /audit, /grid, /nightmare, /moodlevel, /levels, /idle, /facts, /facts forget <word>, /exit")
            continue

        # Execute the full 3-stage Brain -> LLM -> Post-Processor turn (v23.5.4: shared with the face page chat)
        last_system_prompt = run_chat_turn(brain, middleware, voice_io, user_input, show_telemetry, show_grid)
