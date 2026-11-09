"""catchup_cells.py: one-time cleanup for a brain that saturated before engine v21.7.

v21.7 fades rarely used words out of cells a little every sleep, so an old, overfull brain heals by itself,
but slowly (about 50-60 sleeps). This script cleans the cells up at once instead, on a COPY:
  1. the 10-cell cap: each word keeps only its 10 strongest cells (as v21.7 does at its first sleep);
  2. each cell keeps only its KEEP most-used words (default 6, just under the 7 that set off cleaving);
  3. no count stays above MAX_COUNT (default 8), so even the oldest placements fade within ~90 sleeps unless used.
Then one crystal pass rebuilds the crystals from the cleaned-up cells. Links, word weights, memories, dreams and
names are not touched; only which words sit in which cells. The names at the origin cell 3,3,3 are kept.
(Tested 2026-11-08: simply running 30-45 sleep-fades at once left ~2 words per cell and 3 crystals, because most
old placements had counts of 1-2. Keeping each cell's strongest words keeps the brain's history.)

Run it from the main TORRENT folder (next to torrentengine.py v21.7 and the GloVe file):

  python catchup_cells.py brains/brain_gyre.json brains/brain_gyre_cleaned.json
  python catchup_cells.py brains/brain_gyre.json brains/brain_gyre_cleaned.json --keep 6 --max-count 8

The original file is never changed (the script refuses to write over it). It prints before/after numbers.
"""
import argparse, json, os, shutil, statistics, subprocess, sys, time
from collections import Counter


def stats(cells, crystals):
    sizes = [len(v) for v in cells.values() if v]
    spread = Counter(w for v in cells.values() for w in v)
    return (f"cells in use {len(sizes)}/343 | words per cell median {statistics.median(sizes) if sizes else 0}, "
            f"max {max(sizes) if sizes else 0} | placements {sum(sizes)} | crystals {len(crystals)} | "
            f"most spread {spread.most_common(1)[0] if spread else '-'}")


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":  # same fixed hash seed as growthtest.py, so results repeat
        env = dict(os.environ, PYTHONHASHSEED="0")
        sys.exit(subprocess.call([sys.executable, os.path.abspath(__file__)] + sys.argv[1:], env=env))
    ap = argparse.ArgumentParser(description="One-time cell cleanup for a pre-v21.7 brain (works on a copy).")
    ap.add_argument("brain"); ap.add_argument("out")
    ap.add_argument("--keep", type=int, default=6, help="words kept per cell (default 6)")
    ap.add_argument("--max-count", type=float, default=8.0, help="highest count kept (default 8)")
    ap.add_argument("--glove", default="glove.6B.50d.txt")
    a = ap.parse_args()
    if os.path.abspath(a.brain) == os.path.abspath(a.out):
        sys.exit("Refusing to overwrite the original brain. Give a different output file.")
    if os.path.exists(a.out):
        sys.exit(f"{a.out} already exists. Delete it or pick another name.")
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import torrentengine as te
    if not hasattr(te.ToroidalBrainEngine, "prune_cortical_cells"):
        sys.exit("This torrentengine.py has no cell pruning. It needs engine v21.7 or newer.")

    before = json.load(open(a.brain, encoding="utf-8"))
    print("Before:", stats(before.get("cortical_cells", {}), before.get("crystal_lattices", {})))
    shutil.copyfile(a.brain, a.out)
    before["last_shutdown_timestamp"] = time.time()  # load the copy without an overnight sleep (no dreams)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(before, f)

    brain = te.ToroidalBrainEngine(glove_file=a.glove, memory_file=a.out, max_glove_words=50000)
    saved_decay = brain.PRUNE_DECAY
    brain.PRUNE_DECAY = 1.0  # cap only, no fading
    _, capped, _ = brain.prune_cortical_cells()
    brain.PRUNE_DECAY = saved_decay
    origin = brain.all_identity_names()
    trimmed = 0
    for ck, wm in brain.cortical_cells.items():
        protected = {w: c for w, c in wm.items() if ck == "3,3,3" and w in origin}
        rest = sorted(((c, w) for w, c in wm.items() if w not in protected), reverse=True)
        keep = {w: min(c, a.max_count) for c, w in rest[:a.keep]}
        trimmed += len(rest) - len(keep)
        wm.clear(); wm.update(protected); wm.update(keep)
    for ck in list(brain.crystal_lattices):
        if sum(1 for w in brain.cortical_cells.get(ck, {}) if brain.is_crystal_pure_concept(w, cell_key=ck)) < 5:
            brain.crystal_lattices.pop(ck, None)
    brain.run_crystal_annealing_and_tectonics()
    brain.save_memory()
    after = json.load(open(a.out, encoding="utf-8"))
    print(f"Trimmed {capped} placements with the {brain.MAX_CELLS_PER_WORD}-cell cap and {trimmed} more to keep "
          f"{a.keep} words per cell (counts capped at {a.max_count:g}).")
    print("After: ", stats(after["cortical_cells"], after["crystal_lattices"]))
    print(f"Saved the cleaned copy as {a.out}. The original {a.brain} was not changed.")


if __name__ == "__main__":
    main()
