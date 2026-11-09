"""
brainpicker.py — choose which TCM brain to open (T.O.R.R.E.N.T. helper)

Keeps every brain in a "brains" folder as  brains/brain_<name>.json
and asks which one to open at startup.

  python torrentengine.py               -> menu of your brains (+ "new manifold")
  python torrentengine.py --brain gyre  -> open brains/brain_gyre.json directly
  python torrentengine.py --new         -> start a new manifold right away

Also:
  * A new brain starts as brains/brain_new-<date-time>.json and is renamed to
    brains/brain_<its name>.json automatically once it has a name (on exit).
  * An old single brain_memory.json next to the engine shows up in the menu
    and can be moved into the brains folder (a backup copy stays behind).
  * A ".lock" file marks a brain as open, so you get a warning before opening
    the same brain in two windows (they would overwrite each other's saves).

This file never changes how the engine thinks. It only picks the file.
"""

import atexit
import json
import os
import re
import shutil
import sys
import time

BRAINS_DIR = "brains"
LEGACY_BRAIN_FILE = "brain_memory.json"
NEW_BRAIN_PREFIX = "brain_new-"

_session = {"path": None, "hooked": False}  # the brain file opened in this window


def brain_slug(name):
    """'Meridian X' -> 'meridian-x' (safe for file names on every system)."""
    slug = re.sub(r"[^a-z0-9_-]+", "-", str(name).strip().lower()).strip("-_")
    return slug or "unnamed"


def brain_path_for_name(name, brains_dir=BRAINS_DIR):
    return os.path.join(brains_dir, f"brain_{brain_slug(name)}.json")


def unique_brain_path(name, brains_dir=BRAINS_DIR):
    """brain_hope.json, or brain_hope_2.json if that one is taken."""
    base = brain_path_for_name(name, brains_dir)
    path, n = base, 2
    while os.path.exists(path):
        path = f"{base[:-5]}_{n}.json"
        n += 1
    return path


def new_brain_path(brains_dir=BRAINS_DIR):
    os.makedirs(brains_dir, exist_ok=True)
    return os.path.join(brains_dir, f"{NEW_BRAIN_PREFIX}{time.strftime('%Y%m%d-%H%M%S')}.json")


def peek_brain(path):
    """Read a brain's name, size and last-used time without starting the engine."""
    info = {"path": path, "name": None, "nodes": 0, "last_used": None, "ok": True}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        info["name"] = (data.get("user_profile") or {}).get("bot_name") or None
        info["nodes"] = len(data.get("assoc_graph") or {})
        info["last_used"] = data.get("last_shutdown_timestamp")
    except Exception:
        info["ok"] = False
    if not info["last_used"]:
        try:
            info["last_used"] = os.path.getmtime(path)
        except OSError:
            pass
    return info


def list_brains(brains_dir=BRAINS_DIR):
    """All brain_*.json files in the folder, most recently used first."""
    if not os.path.isdir(brains_dir):
        return []
    files = [f for f in os.listdir(brains_dir) if f.startswith("brain_") and f.endswith(".json")]
    infos = [peek_brain(os.path.join(brains_dir, f)) for f in files]
    infos.sort(key=lambda i: i["last_used"] or 0, reverse=True)
    return infos


def _age(ts):
    if not ts:
        return "never"
    secs = max(0, time.time() - ts)
    if secs < 90:
        return "just now"
    if secs < 5400:
        return f"{int(secs // 60)} min ago"
    if secs < 129600:
        return f"{int(secs // 3600)} hr ago"
    return f"{int(secs // 86400)} days ago"


def _ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def adopt_legacy_brain(info, brains_dir=BRAINS_DIR):
    """Copy an old brain_memory.json into the brains folder; keep a backup of the original."""
    if info["name"]:
        target = unique_brain_path(info["name"], brains_dir)
    else:
        target = new_brain_path(brains_dir)  # unnamed: gets renamed once it has a name
    answer = _ask(f"Move '{os.path.basename(info['path'])}' into {brains_dir}/ as "
                  f"'{os.path.basename(target)}'? A backup copy stays behind. (Y/n): ")
    if answer.lower() in ("n", "no"):
        return info["path"]
    os.makedirs(brains_dir, exist_ok=True)
    shutil.copy2(info["path"], target)
    backup = f"{info['path']}.adopted-{time.strftime('%Y%m%d-%H%M%S')}"
    os.replace(info["path"], backup)
    print(f"📁 Moved to {target}  (backup of the original: {os.path.basename(backup)})")
    return target


def pick_from_folder(brains_dir=BRAINS_DIR, legacy_file=None, title="Choose a brain", allow_new=True):
    """Numbered menu. Returns a file path, or None if the person quits."""
    infos = list_brains(brains_dir)
    options = [("open", i) for i in infos]
    if legacy_file and os.path.exists(legacy_file):
        options.append(("legacy", peek_brain(legacy_file)))
    if not options:
        if not allow_new:
            print(f"[!] No brains found in {brains_dir}/")
            return None
        print("No brains yet. Starting a new manifold.")
        return new_brain_path(brains_dir)

    print("=" * 72)
    print(f" 🧠 {title}")
    print("-" * 72)
    for idx, (kind, info) in enumerate(options, 1):
        label = info["name"] or "(unnamed)"
        tag = "  [old single-brain file]" if kind == "legacy" else ""
        broken = "  ⚠️ unreadable" if not info["ok"] else ""
        print(f"  {idx:>2}. {label:<18} {info['nodes']:>6,} nodes · last used {_age(info['last_used']):<12}"
              f" · {os.path.basename(info['path'])}{tag}{broken}")
    if allow_new:
        print("   N. New manifold")
    print("   Q. Quit")
    print("=" * 72)

    while True:
        choice = _ask("Pick a number" + (", N" if allow_new else "") + " or Q: ").lower()
        if choice in ("q", "quit", "exit"):
            return None
        if allow_new and choice in ("n", "new"):
            return new_brain_path(brains_dir)
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            kind, info = options[int(choice) - 1]
            return adopt_legacy_brain(info, brains_dir) if kind == "legacy" else info["path"]
        print("Didn't catch that — type one of the numbers shown.")


def _arg_value(argv, flag):
    for i, arg in enumerate(argv):
        if arg.startswith(flag + "="):
            return arg.split("=", 1)[1]
        if arg == flag and i + 1 < len(argv):
            return argv[i + 1]
    return None


def choose_brain_file(argv=None, base_dir="."):
    """Decide which brain file to open (--brain NAME, --new, or the menu). Exits if the person quits."""
    argv = sys.argv[1:] if argv is None else argv
    brains_dir = os.path.join(base_dir, BRAINS_DIR)
    legacy = os.path.join(base_dir, LEGACY_BRAIN_FILE)

    wanted = _arg_value(argv, "--brain")
    if wanted:
        if wanted.endswith(".json") and os.path.exists(wanted):
            return wanted
        direct = brain_path_for_name(wanted, brains_dir)
        if os.path.exists(direct):
            return direct
        for info in list_brains(brains_dir):  # also match the name stored inside the file
            if info["name"] and brain_slug(info["name"]) == brain_slug(wanted):
                return info["path"]
        print(f"[!] No brain called '{wanted}' in {brains_dir}/. Showing the menu instead.")

    if "--new" in argv:
        return new_brain_path(brains_dir)

    picked = pick_from_folder(brains_dir, legacy_file=legacy)
    if picked is None:
        print("Okay, nothing opened.")
        sys.exit(0)
    return picked


# ---------------------------------------------------------------------------
# Open-brain lock + automatic naming on exit
# ---------------------------------------------------------------------------
def lock_path(path):
    return path + ".lock"


def brain_is_locked(path):
    return os.path.exists(lock_path(path))


def claim_brain(path):
    """Mark this brain as open in this window. Warns (and asks) if it already looks open."""
    lp = lock_path(path)
    if os.path.exists(lp):
        try:
            with open(lp, "r", encoding="utf-8") as f:
                holder = f.read().strip() or "no details"
        except OSError:
            holder = "unknown"
        print(f"\n[!] '{os.path.basename(path)}' looks like it's already open in another window ({holder}).")
        print("    If that window crashed or was closed with the X button, this is just a leftover marker.")
        answer = _ask("    Open it anyway? Two open copies overwrite each other's saves. (y/N): ")
        if answer.lower() not in ("y", "yes"):
            print("Okay, nothing opened.")
            sys.exit(0)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(lp, "w", encoding="utf-8") as f:
        f.write(f"opened {time.strftime('%Y-%m-%d %H:%M:%S')}, process {os.getpid()}")
    _session["path"] = path
    if not _session["hooked"]:
        atexit.register(_on_exit)
        _session["hooked"] = True


def name_new_brain_file(path):
    """If this is a brain_new-... file and the brain now has a name, rename it. Returns the final path."""
    if not path or not os.path.basename(path).startswith(NEW_BRAIN_PREFIX) or not os.path.exists(path):
        return path
    name = peek_brain(path)["name"]
    if not name:
        return path
    target = unique_brain_path(name, os.path.dirname(path) or ".")
    os.replace(path, target)
    print(f"📁 This manifold is named now, so its file was renamed to: {os.path.basename(target)}")
    return target


def _on_exit():
    path = _session.get("path")
    if not path:
        return
    try:
        if os.path.exists(lock_path(path)):
            os.remove(lock_path(path))
        _session["path"] = name_new_brain_file(path)
    except OSError as e:
        print(f"[!] Brain picker cleanup problem: {e}")


def release_brain(path=None):
    """Use when switching brains mid-session (e.g. /clear): unlock and name the old file now."""
    path = path or _session.get("path")
    if path and os.path.exists(lock_path(path)):
        os.remove(lock_path(path))
    final = name_new_brain_file(path)
    if _session.get("path") == path:
        _session["path"] = None
    return final
