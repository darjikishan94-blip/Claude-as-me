#!/usr/bin/env python3
"""Find questions in a spec that (nearly) repeat questions already in the library.

Usage:  python3 tools/check_duplicates.py SPEC.json [SPEC2.json ...] [--threshold 0.82] [--within]

Compares every question (and subpart and OR-choice) in the given specs against every question in
library/**/*.json, using normalised text similarity. Prints near-matches so they can be reworded.
--within also compares the given specs against each other.
Exit code 1 if any match is found at or above the threshold.
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"


def norm(t):
    t = re.sub(r"[_^]\{([^}]*)\}", r"\1", str(t))
    t = re.sub(r"\*\*|\\n", " ", t)
    t = re.sub(r"[^a-z0-9→+=. ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def questions(spec):
    for s in spec.get("sections", []):
        for q in s.get("questions", []):
            yield from _walk(q)


def _walk(q):
    if q.get("q"):
        # an MCQ is only a repeat if its options repeat too, so compare stem + options
        yield q["q"] + (" | " + " / ".join(map(str, q["options"])) if q.get("options") else "")
    for sp in q.get("subparts", []) or []:
        if isinstance(sp, dict):
            yield from _walk(sp)
    if isinstance(q.get("or"), dict):
        yield from _walk(q["or"])


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+")
    ap.add_argument("--threshold", type=float, default=0.82)
    ap.add_argument("--within", action="store_true")
    a = ap.parse_args()
    targets = [Path(s).resolve() for s in a.specs]
    pool = []
    for p in sorted(LIB.rglob("*.json")):
        if p.resolve() in targets and not a.within:
            continue
        for q in questions(load(p)):
            n = norm(q)
            if len(n) > 25:
                pool.append((p.relative_to(ROOT), q, n))
    hits = 0
    for t in targets:
        for q in questions(load(t)):
            n = norm(q)
            if len(n) <= 25:
                continue
            for src, oq, on in pool:
                if src == t.relative_to(ROOT) and on == n:
                    continue
                sm = difflib.SequenceMatcher(None, n, on)
                if sm.real_quick_ratio() < a.threshold or sm.quick_ratio() < a.threshold:
                    continue
                r = sm.ratio()
                if r >= a.threshold:
                    hits += 1
                    print(f"{r:.2f}  {t.name}: {q[:90]}\n      ~ {src}: {oq[:90]}")
    print(f"{hits} near-duplicate(s) at ≥ {a.threshold}")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
