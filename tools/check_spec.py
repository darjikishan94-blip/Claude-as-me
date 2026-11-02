#!/usr/bin/env python3
"""Accuracy checks for a paper/worksheet/notes spec. make_paper.py runs these before rendering.

Checks:
  1. Every chemical equation (anything with →) found in questions, options, answers, marking
     points and notes is balanced: atoms are counted on both sides.
  2. MCQs have 4 options and an answer that starts with a valid option letter, e.g. "(b)".
  3. In a test, every question (or every subpart) has an answer for the key.

Usage:  python3 tools/check_spec.py spec.json [more.json ...]
Mark a question or section with "unbalanced": true when its equations are meant to be
unbalanced, e.g. "balance this" exercises or wrong MCQ distractors. Its question text and
options are then skipped, but answers are still checked.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ELEMENTS = set("""H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn
Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu
Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U""".split())
NON_SPECIES = {"heat", "energy", "light", "sunlight", "electricity", "Heat", "Energy", "Light"}
STATE = re.compile(r"\((s|l|g|aq)\)$")


def plain(text):
    text = re.sub(r"\^\{[^}]*\}", "", str(text))        # drop charges / powers
    text = re.sub(r"_\{([^}]*)\}", r"\1", text)          # subscripts -> digits
    return text.replace("**", "").replace("↓", "").replace("↑", "")


def parse_group(s):
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)|\[|\]", s)
    if not s or "".join(tokens) != s:
        return None
    stack, i = [Counter()], 0
    while i < len(tokens):
        t = tokens[i]
        if t in "([":
            stack.append(Counter())
        elif t in ")]":
            if len(stack) == 1:
                return None
            grp, n = stack.pop(), 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n, i = int(tokens[i + 1]), i + 1
            for k, v in grp.items():
                stack[-1][k] += v * n
        elif t.isdigit():
            return None
        else:
            if t not in ELEMENTS:
                return None
            n = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n, i = int(tokens[i + 1]), i + 1
            stack[-1][t] += n
        i += 1
    return stack[0] if len(stack) == 1 else None


def parse_species(tok):
    """'2H2O(l)' -> Counter of atoms (with coefficient). None if not a formula. 'skip' for heat/energy."""
    tok = tok.strip().rstrip(",.;:!?\"'”’)✓").lstrip("\"'“‘")
    if tok.count("(") > tok.count(")"):  # e.g. "4H2(g" after stripping a closing bracket: restore it
        tok += ")"
    if tok in NON_SPECIES:
        return "skip"
    tok = STATE.sub("", tok)
    m = re.match(r"^(\d+)?(.+)$", tok)
    if not m:
        return None
    coef = int(m.group(1)) if m.group(1) else 1
    total = Counter()
    for j, part in enumerate(m.group(2).split("·")):
        pm = re.match(r"^(\d+|x)?(.+)$", part) if j else re.match(r"^()(.+)$", part)
        if pm.group(1) == "x":
            return "unknown"
        mult = int(pm.group(1)) if pm.group(1) else 1
        c = parse_group(pm.group(2))
        if c is None:
            return None
        for k, v in c.items():
            total[k] += v * mult
    return Counter({k: v * coef for k, v in total.items()})


def side(tokens):
    """Collect species from a token list (already ordered outward from the arrow)."""
    atoms, found, expect_species = Counter(), 0, True
    for tok in tokens:
        if expect_species:
            sp = parse_species(tok)
            if sp is None:
                break
            if sp == "unknown":
                return None, -1
            if sp != "skip":
                atoms += sp
                found += 1
            expect_species = False
        else:
            if tok != "+":
                break
            expect_species = True
    return atoms, found


def equations(text):
    """Yield (equation_text, left_atoms, right_atoms) for each → in text."""
    t = plain(text)
    for m in re.finditer("→", t):
        left_tokens = t[: m.start()].split()[::-1]
        right_tokens = t[m.end():].split()
        L, nl = side(left_tokens)
        R, nr = side(right_tokens)
        if L is None or R is None or nl < 1 or nr < 1:
            continue
        snippet = t[max(0, m.start() - 60): m.end() + 60].strip()
        yield snippet, L, R


def check_text(text, where, errors):
    for snippet, L, R in equations(text):
        if L != R:
            diff = {k: (L.get(k, 0), R.get(k, 0)) for k in sorted(set(L) | set(R)) if L.get(k, 0) != R.get(k, 0)}
            pretty = ", ".join(f"{k}: {a} vs {b}" for k, (a, b) in diff.items())
            errors.append(f"{where}: UNBALANCED [{pretty}] in: …{snippet}…")


def walk_question(q, where, errors, warnings, is_test, skip_q):
    if not skip_q:
        check_text(q.get("q", ""), where, errors)
        for o in q.get("options", []):
            check_text(o, where + " option", errors)
    for fld in ("answer",):
        if q.get(fld):
            check_text(q[fld], where + " answer", errors)
    for pt in q.get("marking", []):
        check_text(pt, where + " marking", errors)
    opts = q.get("options")
    if opts:
        if len(opts) != 4:
            warnings.append(f"{where}: MCQ has {len(opts)} options (expected 4)")
        ans = str(q.get("answer", ""))
        m = re.match(r"^\(([a-h])\)", ans)
        if is_test and not m:
            errors.append(f"{where}: MCQ answer should start with the option letter, e.g. '(b) …'")
        elif m and "abcdefgh".index(m.group(1)) >= len(opts):
            errors.append(f"{where}: answer letter ({m.group(1)}) has no matching option")
    subs = q.get("subparts", [])
    for i, s in enumerate(subs, 1):
        walk_question(s, f"{where}({i})", errors, warnings, is_test, skip_q or s.get("unbalanced"))
    if is_test and not subs and not q.get("answer"):
        errors.append(f"{where}: no answer for the key")
    if q.get("or"):
        walk_question(q["or"], where + " OR", errors, warnings, is_test, skip_q or q["or"].get("unbalanced"))


def check_spec(spec):
    errors, warnings = [], []
    is_test = spec.get("type", "test") == "test"
    n = 0
    for sec in spec.get("sections", []):
        for q in sec.get("questions", []):
            n += 1
            walk_question(q, f"Q{n}", errors, warnings, is_test,
                          bool(sec.get("unbalanced") or q.get("unbalanced")))
    for i, b in enumerate(spec.get("blocks", []), 1):
        for key in ("p", "h", "box", "bullets", "table"):
            if key in b:
                vals = b[key]
                flat = vals if isinstance(vals, list) else [vals]
                for v in flat:
                    for cell in (v if isinstance(v, list) else [v]):
                        if not b.get("unbalanced"):
                            check_text(cell, f"notes block {i}", errors)
    return errors, warnings


def main():
    bad = 0
    for path in sys.argv[1:]:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
        errors, warnings = check_spec(spec)
        for w in warnings:
            print(f"{path}: WARN {w}")
        for e in errors:
            print(f"{path}: ERROR {e}")
        bad += bool(errors)
        if not errors:
            print(f"{path}: OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
