import argparse
import glob
import numpy as np
from collections import defaultdict, Counter
import os
import sys

def main():
    p = argparse.ArgumentParser(description="Check .npy shapes and report mismatches")
    p.add_argument("pattern", help="glob pattern for .npy files (e.g. ../data/mean/X_recording_*.npy)")
    p.add_argument("--axis", type=int, default=None, help="if set, report files that differ on this axis length")
    args = p.parse_args()

    paths = sorted(glob.glob(args.pattern))
    if not paths:
        print("No files matched pattern:", args.pattern)
        sys.exit(1)

    shapes = defaultdict(list)
    bad_loads = []
    for fp in paths:
        try:
            arr = np.load(fp, allow_pickle=True)
            shapes[arr.shape].append(fp)
        except Exception as e:
            bad_loads.append((fp, str(e)))

    print(f"Scanned {len(paths)} files, {len(bad_loads)} failed to load.\n")
    if bad_loads:
        print("Failed loads:")
        for fp, err in bad_loads:
            print("  ", fp, "->", err)
        print()

    # Summarize shapes
    for fp in paths:
        print("  ", fp, "->", os.path.getsize(fp), "bytes, shape:", next(s for s in shapes if fp in shapes[s]))

if __name__ == "__main__":
    main()