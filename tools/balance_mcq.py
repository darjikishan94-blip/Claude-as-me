#!/usr/bin/env python3
"""Spread MCQ correct answers evenly across (a)-(d) so students can't guess a favourite letter.

Usage:  python3 tools/balance_mcq.py spec.json [more.json ...]     (rewrites the files in place)

For each eligible MCQ it moves the correct option to the least-used letter so far, keeping the
other options in their original order, and updates the answer letter.
Skipped (left exactly as written):
  - Assertion–Reason questions (their four options have a fixed standard order)
  - options containing "all of the above", "none of the above", "both" or "neither"
  - questions marked "fixed_order": true
"""

import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

LOCKED = re.compile(r"all of the above|none of the above|\bboth\b|\bneither\b", re.I)


def eligible(q):
    opts = q.get("options")
    if not opts or len(opts) != 4 or q.get("fixed_order"):
        return False
    if "Assertion" in q.get("q", "") or any(LOCKED.search(o) for o in opts):
        return False
    return bool(re.match(r"^\([a-d]\)", str(q.get("answer", ""))))


def balance(spec, seed):
    rng = random.Random(seed)
    used = Counter()
    mcqs = [q for sec in spec.get("sections", []) for q in sec.get("questions", []) if q.get("options")]
    for q in mcqs:  # count locked ones first so the total evens out
        if not eligible(q):
            m = re.match(r"^\(([a-d])\)", str(q.get("answer", "")))
            if m:
                used[m.group(1)] += 1
    moved = 0
    for q in mcqs:
        if not eligible(q):
            continue
        cur = "abcd".index(q["answer"][1])
        low = min(used[c] for c in "abcd")
        target = "abcd".index(rng.choice([c for c in "abcd" if used[c] == low]))
        opts = q["options"]
        correct = opts[cur]
        others = [o for i, o in enumerate(opts) if i != cur]
        others.insert(target, correct)
        q["options"] = others
        q["answer"] = f"({'abcd'[target]})" + q["answer"][3:]
        used["abcd"[target]] += 1
        moved += cur != target
    return used, moved


def main():
    for path in sys.argv[1:]:
        p = Path(path)
        spec = json.loads(p.read_text(encoding="utf-8"))
        used, moved = balance(spec, seed=p.stem)
        p.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{p.name}: {dict(sorted(used.items()))} ({moved} moved)")


if __name__ == "__main__":
    main()
