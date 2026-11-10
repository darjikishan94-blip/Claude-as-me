#!/usr/bin/env python3
"""Build the "Level Up Library" web page: one browsable, searchable home for everything in library/.

Usage:  python3 tools/build_library_site.py

Run `python3 tools/build_library.py` first so every PDF/DOCX is up to date. This script:
  1. converts the Markdown kits (message kits, admissions kit, YouTube scripts) to Word + PDF,
  2. reads every spec and kit and sorts it onto a shelf (Class 10 / 9 / 8, Admin, YouTube, Setup),
  3. writes dist/library-site/index.html (the page), copies every file it links to into
     dist/library-site/files/, and writes files-batch-N.json (Artifact `files` lists, <= 240 each).

Publish (keeps the same link): Artifact publish with file_path=dist/library-site/index.html,
root=dist/library-site, files=<contents of files-batch-1.json>, and on a first publish
capabilities={"downloads": true}. Republish later batches to the same file_path.
Artifacts only serve PDF / text types, so Word files and the skill .zip stay out of the site.
Live library: https://claude.ai/artifact/2HPHX5ohg3F6GYLhrge6dF
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "library"
OUT = ROOT / "dist" / "library-site"
sys.path.insert(0, str(ROOT / "tools"))
import build_library  # noqa: E402

SHELVES = [
    {"id": "class-10", "name": "Class 10 Science", "short": "Class 10",
     "blurb": "The board year. Two CBSE-style tests and a GSEB version for every chapter, daily practice, six full mocks, revision sheets, question banks and the 90-day plan.",
     "sections": [
         {"name": "Chapter tests", "ledger": True,
          "note": "Set A and Set B are CBSE-style 25-mark tests. GSEB is the same chapter in Gujarat Board format (9 objective, 3×2, 2×3, 1×4)."},
         {"name": "Daily practice",
          "note": "Three short practice days per chapter, in the order of the 90-day plan. About 25 minutes a day, answer key included."},
         {"name": "Mock papers"}, {"name": "Revision notes"}, {"name": "Final revision sheets"},
         {"name": "Question banks"}, {"name": "Drills"}, {"name": "Plans"}]},
    {"id": "class-9", "name": "Class 9 Science", "short": "Class 9",
     "blurb": "Topic-based, so it works with the old or the new NCERT book. Check each topic against the book your students use.",
     "sections": [{"name": "Unit tests"}, {"name": "Annual exam practice", "note": "Full-syllabus practice papers with answer keys. Check the topic list against your school's syllabus."}, {"name": "Practice packs"}, {"name": "Revision notes"}]},
    {"id": "class-8", "name": "Class 8 Science", "short": "Class 8",
     "blurb": "Topic-based for the 8th Science group, at Class 8 level.",
     "sections": [{"name": "Unit tests"}, {"name": "Annual exam practice", "note": "Full-syllabus practice papers with answer keys. Check the topic list against your school's syllabus."}, {"name": "Practice packs"}, {"name": "Revision notes"}]},
    {"id": "admin", "name": "Academy admin", "short": "Admin",
     "blurb": "Parent communication in your voice: the handbook, a message for every month, replies for difficult conversations, and the admissions kit.",
     "sections": [{"name": "Parent handbook"}, {"name": "Forms and templates"}, {"name": "Message kits"}, {"name": "Admissions 2027-28"}]},
    {"id": "youtube", "name": "YouTube", "short": "YouTube",
     "blurb": "Scripts for the first 10 videos, with titles, descriptions, tags and Shorts cuts.",
     "sections": [{"name": "Video scripts"}]},
    {"id": "setup", "name": "Claude-as-me setup", "short": "Setup",
     "blurb": "What Claude knows about you and the academy, and the skill bundle that brings all of this into normal Claude chats.",
     "sections": [{"name": "Your profile"}, {"name": "Skill bundle"}]},
]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)


def pages(pdf):
    try:
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=60).stdout
        m = re.search(r"Pages:\s+(\d+)", out)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def md_title(md):
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return md.stem.replace("-", " ").title()


def md_html(md):
    html = subprocess.run(["pandoc", "-f", "gfm", "-t", "html5", str(md)], capture_output=True, text=True, check=True).stdout
    return re.sub(r"^\s*<h1[^>]*>.*?</h1>\s*", "", html, count=1, flags=re.S)  # title shows in the reader bar


def convert_kit(md, out_dir):
    """Markdown kit -> Word + PDF next to the area's other files (only when the Markdown changed)."""
    out_dir.mkdir(exist_ok=True)
    docx = out_dir / f"kit-{md.stem}.docx"
    pdf = out_dir / f"kit-{md.stem}.pdf"
    if not docx.exists() or docx.stat().st_mtime < md.stat().st_mtime:
        run(["pandoc", "-f", "gfm", str(md), "-o", str(docx)])
    if not pdf.exists() or pdf.stat().st_mtime < docx.stat().st_mtime:
        run([shutil.which("soffice") or "libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx)])
    return docx, pdf


def save_name(cls, title, ext, suffix=""):
    base = re.sub(r"\s*:\s*", " - ", title)
    base = re.sub(r"[\\/*?\"<>|]", "", base).strip()
    if cls and not base.lower().startswith("class"):
        base = f"Class {cls} - {base}"
    return f"{base}{suffix}.{ext}"


def search_text(*parts):
    return " ".join(str(p) for p in parts if p).lower()


def main():
    files, items = {}, []

    def add_file(src, pub_name):
        pub = f"files/{pub_name}"
        files[pub] = str(Path(src).relative_to(ROOT))
        return pub

    # ---- specs (papers, notes, worksheets, mocks, plans, handbook)
    for area, kind, spec_path in build_library.specs():
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        slug = build_library.slug_for(spec)
        pdf_dir = area / "pdf"
        pdf, key = pdf_dir / f"{slug}.pdf", pdf_dir / f"{slug}-answer-key.pdf"
        docx = pdf_dir / f"{slug}.docx"
        if not pdf.exists():
            print(f"skip (no PDF built): {spec_path.relative_to(ROOT)}")
            continue
        cls = spec.get("class", "")
        stem = spec_path.stem
        item = {"id": slug, "title": spec.get("title", slug), "kind": "paper", "cls": cls,
                "board": spec.get("board", ""), "marks": spec.get("total_marks"), "time": spec.get("time", ""),
                "pages": pages(pdf), "files": {}, "save": {}}
        a = area.name
        if a == "class10-science":
            item["shelf"] = "class-10"
            m = re.match(r"ch(\d\d)([bg]?)-", stem)
            if kind == "tests" and m:
                item.update(section="Chapter tests", chapter_no=int(m.group(1)), chapter=spec.get("chapter", ""),
                            variant={"": "Set A", "b": "Set B", "g": "GSEB"}[m.group(2)])
            elif kind == "dpp":
                item.update(section="Daily practice", chapter_no=int(stem[2:4]) if stem[2:4].isdigit() else None)
            elif kind == "mocks":
                item["section"] = "Mock papers"
            elif kind == "notes":
                item["section"] = "Final revision sheets" if stem.startswith("sheet-") else "Revision notes"
            elif kind == "worksheets":
                item["section"] = "Question banks" if stem.startswith("bank-") else "Drills"
            elif kind == "plans":
                item["section"] = "Plans"
            else:
                item["section"] = "Plans"
        elif a in ("class9-science", "class8-science"):
            item["shelf"] = "class-9" if a.startswith("class9") else "class-8"
            item["section"] = {"tests": "Unit tests", "notes": "Revision notes", "mocks": "Annual exam practice"}.get(kind, "Practice packs")
        elif a == "admin":
            item.update(shelf="admin", section="Forms and templates" if stem.startswith("form-") else "Parent handbook")
        else:
            item.update(shelf="setup", section="Your profile")
        if spec.get("type") == "notes":
            item["marks"] = None
        item["sub"] = item.get("chapter") or (spec.get("chapter", "") if "Topic-based" not in spec.get("chapter", "") else "")
        item["files"]["pdf"] = add_file(pdf, pdf.name)
        item["save"]["pdf"] = save_name(cls, item["title"], "pdf")
        if key.exists():
            item["files"]["key"] = add_file(key, key.name)
            item["save"]["key"] = save_name(cls, item["title"], "pdf", " (answer key)")
        item["search"] = search_text(item["title"], item.get("sub"), item["section"], item["board"], f"class {cls}",
                                     item.get("variant"), "answer key" if key.exists() else "", item["shelf"])
        items.append(item)

    # ---- Markdown kits
    kit_places = [
        (LIB / "admin", "admin", "Message kits", ""),
        (LIB / "admissions", "admin", "Admissions 2027-28", ""),
        (LIB / "class10-science" / "plans", "class-10", "Plans", "10"),
        (LIB / "youtube", "youtube", "Video scripts", ""),
    ]
    for folder, shelf, section, cls in kit_places:
        for md in sorted(folder.glob("*.md")):
            if md.name == "README.md":
                continue
            out_dir = (folder.parent if folder.name == "plans" else folder) / "pdf"
            docx, pdf = convert_kit(md, out_dir)
            title = md_title(md)
            item = {"id": "kit-" + md.stem, "title": title, "kind": "kit", "cls": cls, "shelf": shelf, "section": section,
                    "html": md_html(md), "pages": pages(pdf), "files": {}, "save": {}}
            item["files"]["pdf"] = add_file(pdf, pdf.name)
            item["files"]["md"] = add_file(md, f"kit-{md.stem}.md")
            item["save"]["pdf"] = save_name("", title, "pdf")
            item["save"]["md"] = save_name("", title, "md")
            item["search"] = search_text(title, section, shelf, re.sub(r"<[^>]+>", " ", item["html"])[:4000])
            items.append(item)

    # ---- Setup: profile docs + skill bundle
    names = {"voice.md": "Your voice guide", "academy.md": "Academy facts", "profile.md": "Your profile",
             "youtube.md": "YouTube channel plan", "open-questions.md": "Questions Claude still has for you"}
    for md in sorted((ROOT / "me").glob("*.md"), key=lambda p: list(names).index(p.name) if p.name in names else 99):
        title = names.get(md.name, md_title(md))
        items.append({"id": "me-" + md.stem, "title": title, "kind": "doc", "cls": "", "shelf": "setup",
                      "section": "Your profile", "html": md_html(md), "sub": md_title(md),
                      "files": {"md": add_file(md, f"me-{md.name}")}, "save": {"md": f"{title}.md"},
                      "search": search_text(title, "setup profile voice academy", md.read_text(encoding="utf-8")[:3000])})
    zip_path = ROOT / "dist" / "kishan-as-me.zip"
    if zip_path.exists():
        items.append({"id": "skill-bundle", "title": "Claude skill bundle (kishan-as-me)", "kind": "zip", "cls": "",
                      "shelf": "setup", "section": "Skill bundle",
                      "sub": "Lets any Claude chat write as you and rebuild these papers.",
                      "files": {}, "save": {},
                      "howto": "Artifacts can't hold .zip files, so get it from Claude: in a Claude-as-me session, say \"send me the skill bundle\". Then, on a computer, open Claude → Settings → Capabilities → Skills → Upload skill, and choose the file.",
                      "search": "claude skill bundle zip setup kishan as me upload"})

    # ---- order items by shelf/section as declared
    order = {(s["id"], sec["name"]): (i, j) for i, s in enumerate(SHELVES) for j, sec in enumerate(s["sections"])}
    items.sort(key=lambda it: order.get((it["shelf"], it["section"]), (99, 99)))

    count = lambda pred: sum(1 for i in items if pred(i))  # noqa: E731
    tally = [
        (count(lambda i: i["section"] in ("Chapter tests", "Unit tests")), "test papers"),
        (count(lambda i: i["section"] in ("Mock papers", "Annual exam practice")), "full mock papers"),
        (count(lambda i: i["section"] == "Daily practice"), "daily practice packs"),
        (count(lambda i: "key" in i["files"]), "answer keys"),
        (count(lambda i: i["section"] in ("Revision notes", "Final revision sheets", "Question banks", "Drills", "Practice packs")), "revision & practice sheets"),
        (count(lambda i: i["kind"] == "kit"), "kits & scripts"),
    ]
    data = {
        "shelves": SHELVES, "items": items, "tally": tally,
        "footer": (f"Built from the Claude-as-me repository on {date.today():%-d %B %Y}. Every paper passed the automatic checks: "
                   "marks add up, chemical equations are balanced, and answer keys point at real options. Check Class 8–9 topics "
                   "against your students' book, and the CBSE/GSEB patterns against this year's official sample papers."),
    }
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    template = (ROOT / "tools" / "library_site_template.html").read_text(encoding="utf-8")
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "files").mkdir(parents=True)
    (OUT / "index.html").write_text(template.replace("/*__DATA__*/", blob), encoding="utf-8")
    (OUT / "files.json").write_text(json.dumps(files, indent=1), encoding="utf-8")
    # stage copies next to the page, so it publishes with root=dist/library-site
    for pub, src in files.items():
        shutil.copy2(ROOT / src, OUT / pub)

    # batches for publishing (<= 240 files and <= 55 MB each), as Artifact `files` lists
    batches, cur, size = [], [], 0
    for pub, src in files.items():
        s = (ROOT / src).stat().st_size
        if cur and (len(cur) >= 240 or size + s > 55e6):
            batches.append(cur); cur, size = [], 0
        cur.append({"path": pub}); size += s
    if cur:
        batches.append(cur)
    for n, b in enumerate(batches, 1):
        (OUT / f"files-batch-{n}.json").write_text(json.dumps(b), encoding="utf-8")
    total = sum((ROOT / s).stat().st_size for s in files.values())
    print(f"{len(items)} items, {len(files)} files ({total / 1e6:.1f} MB) in {len(batches)} batch(es); "
          f"page {(OUT / 'index.html').stat().st_size / 1e3:.0f} KB -> {OUT.relative_to(ROOT)}/index.html")
    for t in tally:
        print(f"  {t[0]} {t[1]}")


if __name__ == "__main__":
    main()
