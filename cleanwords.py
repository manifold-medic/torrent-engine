"""
cleanwords.py — find and remove junk words from a T.O.R.R.E.N.T. brain file.

Junk words are things like "reflectiona" (glued by the old word splitter), "ndational" (a cut-off summary),
"andnyou" (a line break glued in) or "wbile" (a typo). Since v21.3 the engine no longer makes new ones,
but the old ones stay forever: the engine has no forgetting, and dreams keep wiring them to new words.

Usage
  python cleanwords.py brains/brain_gyre.json            scan, show the list, ask which to remove
  python cleanwords.py brains/brain_gyre.json --scan     only show the list, change nothing
  python cleanwords.py brains/brain_gyre.json --remove wbile,andnyou      remove exactly these words

What it does when it removes words
  * Makes a backup first: brain_gyre.json.before-cleanup-<time>
  * Deletes each word everywhere it lives: weights, links (both directions), cells, crystals, cell memories,
    ideas that use it, dream journal entries that use it, facts, rejections, saved word vectors, verb phrases,
    and the bridge's summary / episode concept lists.
  * Leaves the crystal-split log alone (it's history, and the engine never reads words back from it).

A word is listed if it is not in the full GloVe word file (all 400,000 words), so the script needs
glove.6B.50d.txt (it looks next to this script, in the current folder and one folder up, or use --glove FILE).
Hyphenated words (like "guarded-stillness") are engine-made mood names and are listed separately as kept.
Don't run this on a brain that is open in another window.
"""

import argparse
import json
import os
import re
import shutil
import sys
import time


def find_glove(explicit):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    here = os.path.dirname(os.path.abspath(__file__))
    for folder in (here, os.getcwd(), os.path.dirname(here), os.path.dirname(os.getcwd())):
        cand = os.path.join(folder, "glove.6B.50d.txt")
        if os.path.isfile(cand):
            return cand
    return None


def load_vocab(path):
    """word -> frequency rank (the file is in frequency order)"""
    vocab = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for rank, line in enumerate(f, 1):
            vocab.setdefault(line.split(" ", 1)[0].lower(), rank)
    return vocab


def all_words(d):
    words = set(d.get("word_weights", {})) | set(d.get("social_weights", {})) | set(d.get("epistemic_weights", {}))
    words |= set(d.get("learned_vectors", {})) | set(d.get("assoc_graph", {})) | set(d.get("rejected_links", {}))
    for nbrs in d.get("assoc_graph", {}).values():
        words |= set(nbrs)
    for cell in d.get("cortical_cells", {}).values():
        words |= set(cell)
    for p in d.get("idea_memory", []):
        words |= {p.get("subj", ""), p.get("obj", ""), p.get("bridge", "")}
    for k in d.get("knowledge_facts", {}):
        if not k.startswith("_"):
            words.add(k)
    return {w for w in words if w}


def guess(w, vocab):
    """A short human hint: 'and + you' if it splits into two common words, else 'not a word'."""
    common = lambda x: vocab.get(x, 10 ** 9) <= 50000
    for i in range(2, len(w) - 1):
        a, b = w[:i], w[i:]
        if common(a) and common(b) and len(a) >= 3 and len(b) >= 3:
            # the "n" from a pasted line break ("and\nyou") also shows up as a glued middle letter
            return f"glued: {a} + {b}"
        if w[i] == "n" and common(w[:i]) and common(w[i + 1:]) and i >= 3 and len(w) - i - 1 >= 3:
            return f"glued line break: {w[:i]} + {w[i + 1:]}"
    if not w.isascii():
        return "odd character (keyboard slip?)"
    return "not a word (typo or cut off?)"


def usage(d, w):
    links = len(d.get("assoc_graph", {}).get(w, {}))
    cells = sum(c.get(w, 0) for c in d.get("cortical_cells", {}).values())
    ideas = sum(1 for p in d.get("idea_memory", []) if w in (p.get("subj"), p.get("obj"), p.get("bridge")))
    return links, cells, ideas


def scrub_text(text, junk):
    for w in junk:
        text = re.sub(rf"\b{re.escape(w)}\b", "", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def remove_words(d, junk):
    junk = set(junk)
    report = {}

    def count(key, n=1):
        report[key] = report.get(key, 0) + n

    for field in ("word_weights", "social_weights", "epistemic_weights", "learned_vectors"):
        for w in junk:
            if d.get(field, {}).pop(w, None) is not None:
                count(field)

    g = d.get("assoc_graph", {})
    for w in junk:
        if g.pop(w, None) is not None:
            count("words removed from the link graph")
    for nbrs in g.values():
        for w in junk:
            if nbrs.pop(w, None) is not None:
                count("links removed")
    for k in [k for k, v in g.items() if not v]:
        g.pop(k)  # a word left with no links at all

    rej = d.get("rejected_links", {})
    for w in junk:
        rej.pop(w, None)
    for k in list(rej):
        rej[k] = [x for x in rej[k] if x not in junk]

    for cell in d.get("cortical_cells", {}).values():
        for w in junk:
            if cell.pop(w, None) is not None:
                count("cell entries removed")
    d["cortical_cells"] = {k: v for k, v in d.get("cortical_cells", {}).items() if v}

    for entry in d.get("cell_lexicon", {}).values():
        if isinstance(entry.get("top_words"), list):
            entry["top_words"] = [x for x in entry["top_words"] if x not in junk]

    for crystal in d.get("crystal_lattices", {}).values():
        for facet in crystal.get("facets", {}).values():
            before = len(facet.get("words", []))
            facet["words"] = [x for x in facet.get("words", []) if x not in junk]
            if len(facet["words"]) < before:
                count("crystal facet words removed", before - len(facet["words"]))

    ideas = d.get("idea_memory", [])
    keep = [p for p in ideas if not ({p.get("subj"), p.get("obj"), p.get("bridge")} & junk)]
    if len(keep) < len(ideas):
        count("ideas removed", len(ideas) - len(keep))
    d["idea_memory"] = keep

    dj = d.get("dream_journal", [])
    keep = [e for e in dj if not ({e.get("threadA"), e.get("threadB"), e.get("bridge")} & junk)]
    if len(keep) < len(dj):
        count("dream journal entries removed", len(dj) - len(keep))
    d["dream_journal"] = keep

    vb = d.get("custom_verb_bridges", [])
    d["custom_verb_bridges"] = [v for v in vb if not (set(v.lower().split()) & junk)]

    facts = d.get("knowledge_facts", {})
    for w in junk:
        if facts.pop(w, None) is not None:
            count("facts removed")
    # bridge memory (ltcmbridge / meridianbridge): the summary goes into the language model's prompt, and the model
    # can copy a junk word back out of it, so scrub it there too; episode concept lists are cleaned the same way
    if isinstance(facts.get("_running_summary"), str):
        new = scrub_text(facts["_running_summary"], junk)
        if new != facts["_running_summary"]:
            facts["_running_summary"] = new
            count("bridge summary cleaned")
    if isinstance(facts.get("_episodic_archive_json"), str):
        try:
            eps = json.loads(facts["_episodic_archive_json"])
            changed = 0
            for ep in eps:
                if isinstance(ep, dict) and isinstance(ep.get("concepts"), list):
                    new = [c for c in ep["concepts"] if c not in junk]
                    changed += len(new) < len(ep["concepts"])
                    ep["concepts"] = new
            if changed:
                facts["_episodic_archive_json"] = json.dumps(eps)
                count("bridge episodes cleaned", changed)
        except ValueError:
            pass
    return report


def main():
    ap = argparse.ArgumentParser(description="Find and remove junk words from a T.O.R.R.E.N.T. brain file.")
    ap.add_argument("brain", help="brain file, e.g. brains/brain_gyre.json")
    ap.add_argument("--scan", action="store_true", help="only list suspicious words; change nothing")
    ap.add_argument("--remove", help="comma-separated words to remove, e.g. wbile,andnyou")
    ap.add_argument("--glove", help="path to glove.6B.50d.txt")
    args = ap.parse_args()

    if os.path.exists(args.brain + ".lock"):
        sys.exit(f"'{args.brain}' looks open in another window (found a .lock file). Close it first.")
    with open(args.brain, "r", encoding="utf-8") as f:
        d = json.load(f)

    if args.remove:
        chosen = [w.strip().lower() for w in args.remove.split(",") if w.strip()]
    else:
        glove = find_glove(args.glove)
        if not glove:
            sys.exit("Couldn't find glove.6B.50d.txt. Put this script next to it, or use --glove FILE.")
        print(f"Reading the full word list from {glove} ...")
        vocab = load_vocab(glove)
        odd = sorted(w for w in all_words(d) if w not in vocab)
        hyphen = [w for w in odd if "-" in w]
        suspects = [w for w in odd if "-" not in w]
        name = d.get("user_profile", {}).get("bot_name") or os.path.basename(args.brain)
        print(f"\n{name}: {len(all_words(d))} words, {len(suspects)} not in GloVe:\n")
        for i, w in enumerate(suspects, 1):
            links, cells, ideas = usage(d, w)
            print(f"  {i:>2}. {w:<20} {guess(w, vocab):<34} links {links:>3}  cells {cells:>2}  ideas {ideas}")
        if hyphen:
            print(f"\n  Kept (hyphenated mood names the engine makes on purpose): {', '.join(hyphen)}")
        if not suspects or args.scan:
            print("\nNothing changed.")
            return
        print("\nSome of these may be real words you want (a name, a word you made up). Only pick the junk.")
        ans = input("Numbers to remove (e.g. 1,2,5), 'all', or just Enter to cancel: ").strip().lower()
        if not ans:
            print("Nothing changed.")
            return
        if ans == "all":
            chosen = suspects
        else:
            try:
                chosen = [suspects[int(x) - 1] for x in re.split(r"[,\s]+", ans) if x]
            except (ValueError, IndexError):
                sys.exit("Couldn't read that list. Nothing changed.")

    present = [w for w in chosen if w in all_words(d)]
    missing = [w for w in chosen if w not in present]
    if missing:
        print(f"Not in this brain (skipped): {', '.join(missing)}")
    if not present:
        print("Nothing to remove. Nothing changed.")
        return

    backup = f"{args.brain}.before-cleanup-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(args.brain, backup)
    report = remove_words(d, present)
    tmp = args.brain + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, args.brain)
    print(f"\nRemoved: {', '.join(present)}")
    for k, v in report.items():
        print(f"  {k}: {v}")
    print(f"Backup of the old file: {backup}")


if __name__ == "__main__":
    main()
