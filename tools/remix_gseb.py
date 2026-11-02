#!/usr/bin/env python3
"""Build a 25-mark GSEB-pattern chapter test from a chapter's Set A + Set B tests (CBSE style).

Every question is reused from already-checked specs, so accuracy carries over. Only the
layout changes, to the GSEB 25-mark blueprint used by the test-paper skill:
    A: 9 × 1 objective · B: 3 × 2 · C: 2 × 3 · D: 1 × 4   (= 25)
Assertion–Reason questions are left out (GSEB doesn't use them), and OR-choices are dropped.

Usage:  python3 tools/remix_gseb.py [chapter numbers…]    (default: all 13)
Writes library/class10-science/tests/chNNg-<slug>.json
"""

import copy
import json
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent.parent / "library/class10-science/tests"


def load(nn, suffix):
    files = sorted(TESTS.glob(f"ch{nn:02d}{suffix}-*.json"))
    return (json.loads(files[0].read_text(encoding="utf-8")), files[0]) if files else (None, None)


def section(spec, letter):
    for sec in spec["sections"]:
        if sec.get("title", "").strip().upper() == f"SECTION {letter}":
            return sec["questions"]
    return []


def clean(q):
    q = copy.deepcopy(q)
    q.pop("or", None)
    return q


def interleave(a, b):
    out = []
    for i in range(max(len(a), len(b))):
        if i < len(a):
            out.append(a[i])
        if i < len(b):
            out.append(b[i])
    return out


def build(nn):
    a, fa = load(nn, "")
    b, _ = load(nn, "b")
    if not a or not b:
        print(f"ch{nn:02d}: Set A or Set B missing, skipped")
        return None
    mcq = [clean(q) for q in interleave(section(a, "A"), section(b, "A"))
           if q.get("options") and "Assertion" not in q["q"]]
    two = [clean(q) for q in interleave(section(a, "B"), section(b, "B"))]
    three = [clean(q) for q in interleave(section(a, "C"), section(b, "C"))]
    four = [clean(q) for q in section(a, "E") + section(b, "E")]
    if len(mcq) < 9 or len(two) < 3 or len(three) < 2 or not four:
        print(f"ch{nn:02d}: not enough questions in the pools, skipped")
        return None
    title = a["title"].split(":", 1)[1].strip()
    spec = {
        "type": "test",
        "file_name": f"c10-ch{nn:02d}-test-gseb-" + fa.stem.split("-", 1)[1],
        "title": f"Ch {nn} Test (GSEB pattern): {title}",
        "class": "10", "board": "GSEB", "subject": "Science",
        "chapter": a.get("chapter", title),
        "time": "50 minutes", "total_marks": 25,
        "instructions": [
            "All questions are compulsory.",
            "Section A: objective questions, 1 mark each. Section B: 2 marks each. Section C: 3 marks each. Section D: 4 marks.",
            "Write balanced equations and draw neat, labelled diagrams wherever needed.",
        ],
        "sections": [
            {"title": "Section A", "note": "Choose the correct option.", "questions": mcq[:9]},
            {"title": "Section B", "questions": two[:3]},
            {"title": "Section C", "questions": three[:2]},
            {"title": "Section D", "note": "Read the passage and answer the questions that follow.", "questions": four[:1]},
        ],
        "closing": "All the best!",
    }
    out = TESTS / f"ch{nn:02d}g-{fa.stem.split('-', 1)[1]}.json"
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ch{nn:02d}: wrote {out.name}")
    return out


def main():
    chapters = [int(x) for x in sys.argv[1:]] or list(range(1, 14))
    for nn in chapters:
        build(nn)


if __name__ == "__main__":
    main()
