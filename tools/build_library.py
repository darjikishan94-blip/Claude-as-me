#!/usr/bin/env python3
"""Render every spec in library/ to DOCX + PDF and rebuild library/README.md (the index).

Usage:  python3 tools/build_library.py [--all]

- Specs live in library/<area>/<kind>/*.json  (kind = tests | notes | mocks | worksheets | plans)
- Output goes to library/<area>/pdf/
- Only specs that changed since their PDF was built are re-rendered, unless --all is given.
- Every spec goes through the same accuracy checks as make_paper.py (marks, equations, MCQ keys).
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"
sys.path.insert(0, str(ROOT / "tools"))
import make_paper  # noqa: E402

KIND_ORDER = ["tests", "notes", "worksheets", "mocks", "plans"]
KIND_LABEL = {"tests": "Chapter tests (25 marks)", "notes": "Quick revision notes",
              "worksheets": "Worksheets", "mocks": "Full mock papers", "plans": "Plans"}


def slug_for(spec):
    return make_paper.slugify(spec.get("file_name") or " ".join(
        str(x) for x in [f"class{spec.get('class', '')}", spec.get("subject", ""), spec.get("title", "")] if x))


def specs():
    for area in sorted(p for p in LIB.iterdir() if p.is_dir()):
        for kind in KIND_ORDER:
            for f in sorted((area / kind).glob("*.json")) if (area / kind).exists() else []:
                yield area, kind, f


def render(area, spec_path, force):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = area / "pdf"
    out.mkdir(exist_ok=True)
    slug = slug_for(spec)
    pdf = out / f"{slug}.pdf"
    if not force and pdf.exists() and pdf.stat().st_mtime > spec_path.stat().st_mtime:
        return spec, slug, []
    r = subprocess.run([sys.executable, str(ROOT / "tools/make_paper.py"), str(spec_path), "--out", str(out), "--no-pdf"],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stdout, r.stderr)
        sys.exit(f"FAILED: {spec_path}")
    return spec, slug, [Path(line) for line in r.stdout.splitlines() if line.endswith(".docx")]


def to_pdf(docs):
    by_dir = {}
    for d in docs:
        by_dir.setdefault(d.parent, []).append(d)
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    for out, files in by_dir.items():
        for i in range(0, len(files), 20):
            subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", str(out), *map(str, files[i:i + 20])],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)


def write_index(rows):
    lines = ["# Level Up Academy: content library", "",
             "Ready-to-print material made by Claude-as-me. Every paper passes the automatic checks before it is built: "
             "marks add up, every chemical equation is balanced (atoms counted), MCQ keys point at a real option, and "
             "correct answers are spread across (a)–(d).", "",
             "> **Before using a test with students:** this repo is public, so answer keys here can be found online. "
             "Make the repo private (GitHub → Settings → Change visibility) or treat these as practice material.", ""]
    areas = {}
    for area, kind, spec, slug in rows:
        areas.setdefault(area, {}).setdefault(kind, []).append((spec, slug))
    for area, kinds in areas.items():
        lines += [f"## {area.name.replace('-', ' ').title()}", ""]
        for kind in KIND_ORDER:
            if kind not in kinds:
                continue
            lines += [f"### {KIND_LABEL[kind]}", "", "| Title | Files |", "|---|---|"]
            for spec, slug in kinds[kind]:
                rel = f"{area.name}/pdf/{slug}"
                files = [f"[PDF]({rel}.pdf)", f"[Word]({rel}.docx)"]
                if (area / "pdf" / f"{slug}-answer-key.pdf").exists():
                    files.append(f"[Answer key]({rel}-answer-key.pdf)")
                lines.append(f"| {spec.get('title', slug)} | {' · '.join(files)} |")
            lines.append("")
    extra = sorted(p for p in LIB.rglob("*.md") if p.name != "README.md")
    if extra:
        lines += ["## Guides & message kits", ""]
        for p in extra:
            title = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
            lines.append(f"- [{title}]({p.relative_to(LIB).as_posix()})")
        lines.append("")
    lines += ["---", "Rebuild after editing any spec: `python3 tools/build_library.py`"]
    (LIB / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    rows, docs = [], []
    for area, kind, f in specs():
        spec, slug, made = render(area, f, a.all)
        rows.append((area, kind, spec, slug))
        docs += made
        if made:
            print(f"built {f.relative_to(ROOT)}")
    if docs:
        to_pdf(docs)
    write_index(rows)
    print(f"{len(rows)} specs, {len(docs)} documents rendered. Index: library/README.md")


if __name__ == "__main__":
    main()
