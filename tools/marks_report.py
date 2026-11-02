#!/usr/bin/env python3
"""Turn a marks list into a class result summary + a ranked sheet. All maths is done here, never by hand.

Usage:
    python3 tools/marks_report.py private/marks.csv --max 25 [--name Name] [--marks Marks]
        [--prev "Test 1"] [--sheet "Class 9"] [--out private/output/results.xlsx]

Input: CSV or XLSX with one row per student. Absent is written as AB / A / absent / blank.
Prints a Markdown summary (for Claude to read) and writes an .xlsx with ranks and tiers.
Tiers: top >= 80%, steady 50-79%, support < 50%. These are used to choose the parent message template.
"""

import argparse
import csv
import statistics
import sys
from pathlib import Path

ABSENT = {"", "ab", "a", "absent", "abs", "-", "na", "n/a"}


def load_rows(path, sheet=None):
    path = Path(path)
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        from openpyxl import load_workbook
        wb = load_workbook(path, data_only=True, read_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        rows = [[("" if c is None else c) for c in r] for r in ws.iter_rows(values_only=True)]
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    rows = [r for r in rows if any(str(c).strip() for c in r)]
    if not rows:
        sys.exit("No rows found.")
    header = [str(h).strip() for h in rows[0]]
    return header, rows[1:]


def to_num(v):
    s = str(v).strip()
    if s.lower() in ABSENT:
        return None
    try:
        return float(s)
    except ValueError:
        return "bad"


def pick(header, wanted, rows, numeric):
    if wanted:
        for i, h in enumerate(header):
            if h.lower() == wanted.lower():
                return i
        sys.exit(f"Column '{wanted}' not found. Columns: {header}")
    # auto: first mostly-text column for names, last mostly-numeric column for marks
    idx = range(len(header)) if not numeric else reversed(range(len(header)))
    for i in idx:
        vals = [r[i] for r in rows if i < len(r) and str(r[i]).strip()]
        nums = sum(isinstance(to_num(v), float) for v in vals)
        if vals and ((nums / len(vals) > 0.6) == numeric):
            return i
    sys.exit(f"Couldn't detect the {'marks' if numeric else 'name'} column. Pass --{'marks' if numeric else 'name'}.")


def fmt(x):
    return str(int(x)) if float(x).is_integer() else f"{x:.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--max", type=float, required=True, help="maximum marks of the test")
    ap.add_argument("--name")
    ap.add_argument("--marks")
    ap.add_argument("--prev", help="column with the previous test's marks (same max), for change")
    ap.add_argument("--prev-max", type=float, help="max marks of the previous test if different")
    ap.add_argument("--sheet")
    ap.add_argument("--out", default="private/output/results.xlsx")
    a = ap.parse_args()

    header, rows = load_rows(a.file, a.sheet)
    ni = pick(header, a.name, rows, numeric=False)
    mi = pick(header, a.marks, rows, numeric=True)
    pi = pick(header, a.prev, rows, numeric=True) if a.prev else None
    prev_max = a.prev_max or a.max

    students, problems = [], []
    for r in rows:
        name = str(r[ni]).strip() if ni < len(r) else ""
        if not name:
            continue
        m = to_num(r[mi]) if mi < len(r) else None
        if m == "bad" or (isinstance(m, float) and not 0 <= m <= a.max):
            problems.append(f"{name}: marks value '{r[mi]}' is not valid for max {fmt(a.max)}")
            continue
        p = to_num(r[pi]) if pi is not None and pi < len(r) else None
        p = p if isinstance(p, float) else None
        students.append({"name": name, "marks": m, "prev": p})

    if problems:
        print("FIX THESE BEFORE CONTINUING:")
        for pr in problems:
            print("  -", pr)
        sys.exit(2)

    present = [s for s in students if s["marks"] is not None]
    absent = [s for s in students if s["marks"] is None]
    for s in present:
        s["pct"] = 100 * s["marks"] / a.max
        s["tier"] = "top" if s["pct"] >= 80 else "steady" if s["pct"] >= 50 else "support"
        if s["prev"] is not None:
            s["change"] = s["pct"] - 100 * s["prev"] / prev_max
    # competition ranking: 1, 2, 2, 4
    ordered = sorted(present, key=lambda s: -s["marks"])
    for i, s in enumerate(ordered):
        s["rank"] = 1 if i == 0 else (ordered[i - 1]["rank"] if s["marks"] == ordered[i - 1]["marks"] else i + 1)

    marks = [s["marks"] for s in present]
    print(f"# Result summary: {header[mi]} (out of {fmt(a.max)})\n")
    print(f"- Students: {len(students)} | Appeared: {len(present)} | Absent: {len(absent)}")
    if marks:
        avg = statistics.mean(marks)
        print(f"- Class average: {fmt(avg)}/{fmt(a.max)} ({avg / a.max * 100:.0f}%) | "
              f"Median: {fmt(statistics.median(marks))} | Highest: {fmt(max(marks))} | Lowest: {fmt(min(marks))}")
        bands = [("90-100%", 90, 101), ("75-89%", 75, 90), ("50-74%", 50, 75), ("33-49%", 33, 50), ("below 33%", 0, 33)]
        print("- Bands: " + " · ".join(f"{lbl}: {sum(lo <= s['pct'] < hi for s in present)}" for lbl, lo, hi in bands))
    for tier, label in (("top", "Top (>= 80%)"), ("steady", "Steady (50-79%)"), ("support", "Needs support (< 50%)")):
        group = [s for s in ordered if s["tier"] == tier]
        print(f"\n## {label}: {len(group)}")
        for s in group:
            ch = f" | change {s['change']:+.0f} pts" if "change" in s else ""
            print(f"- #{s['rank']} {s['name']}: {fmt(s['marks'])}/{fmt(a.max)} ({s['pct']:.0f}%){ch}")
    if absent:
        print(f"\n## Absent: {len(absent)}")
        for s in absent:
            print(f"- {s['name']}")
    movers = [s for s in present if abs(s.get("change", 0)) >= 10]
    if movers:
        print("\n## Big changes vs previous test (>= 10 percentage points)")
        for s in sorted(movers, key=lambda s: -s["change"]):
            print(f"- {s['name']}: {s['change']:+.0f} pts")

    # spreadsheet
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"
    cols = ["Rank", "Name", f"Marks (/{fmt(a.max)})", "%", "Tier"] + (["Change (pts)"] if pi is not None else [])
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True)
    fills = {"top": "E2F0D9", "steady": "FFF2CC", "support": "FCE4D6"}
    for s in ordered + absent:
        row = [s.get("rank", ""), s["name"], s["marks"] if s["marks"] is not None else "AB",
               round(s["pct"], 1) if "pct" in s else "", s.get("tier", "absent")]
        if pi is not None:
            row.append(round(s["change"], 1) if "change" in s else "")
        ws.append(row)
        if s.get("tier") in fills:
            for c in ws[ws.max_row]:
                c.fill = PatternFill("solid", fgColor=fills[s["tier"]])
    for col, w in zip("ABCDEF", (6, 26, 12, 8, 10, 12)):
        ws.column_dimensions[col].width = w
    wb.save(out)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
