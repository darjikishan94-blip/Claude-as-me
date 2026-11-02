#!/usr/bin/env python3
"""Render a Level Up Academy test paper, worksheet or notes sheet to DOCX + PDF.

Usage:
    python3 tools/make_paper.py spec.json [--out DIR] [--no-pdf]

The spec is JSON (see samples/*.json and the test-paper skill for the full format).
Outputs, named from the spec's title:
    <slug>.docx / .pdf              the paper students get
    <slug>-answer-key.docx / .pdf   answers + marking points (only if any answers are given)

Inline markup in any text field:
    **bold**   _{sub}  (H_{2}O)   ^{sup}  (10^{-3}, Fe^{3+})
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401  (kept for easy landscape tweaks)
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT = "Liberation Sans"  # metric-compatible with Arial; present on the render box
PAGE_W, MARGIN = 21.0, 1.7
TEXT_W = PAGE_W - 2 * MARGIN
GREY = RGBColor(0x55, 0x55, 0x55)
ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
LETTERS = "abcdefgh"


# ---------------------------------------------------------------- helpers

def slugify(text):
    s = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return s or "paper"


TOKEN = re.compile(r"(\*\*.+?\*\*|_\{.+?\}|\^\{.+?\})")


def add_rich(par, text, size=None, bold=False, italic=False, color=None):
    """Add text with **bold**, _{sub}, ^{sup} markup to a paragraph."""
    for part in TOKEN.split(str(text)):
        if not part:
            continue
        run_bold, sub, sup = bold, False, False
        if part.startswith("**") and part.endswith("**"):
            part, run_bold = part[2:-2], True
        elif part.startswith("_{"):
            part, sub = part[2:-1], True
        elif part.startswith("^{"):
            part, sup = part[2:-1], True
        run = par.add_run(part)
        run.bold = run_bold
        run.italic = italic
        run.font.subscript = sub
        run.font.superscript = sup
        if size:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color
    return par


def para(doc_or_cell, text="", size=11, bold=False, italic=False, align=None,
         before=0, after=2, color=None, indent=0.0):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    if indent:
        pf.left_indent = Cm(indent)
    if align:
        p.alignment = align
    if text:
        add_rich(p, text, size=size, bold=bold, italic=italic, color=color)
    return p


def bottom_border(p, style="single", sz=6, color="999999"):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    b.set(qn("w:val"), style)
    b.set(qn("w:sz"), str(sz))
    b.set(qn("w:space"), "1")
    b.set(qn("w:color"), color)
    bdr.append(b)
    pPr.append(bdr)


def answer_lines(doc, n, indent=0.9):
    for _ in range(int(n)):
        p = para(doc, " ", size=11, after=0, before=6, indent=indent)
        bottom_border(p, style="dotted", sz=6, color="888888")


def boxed(doc, text=None, height_cm=None, shade=None, size=10.5):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.rows[0].cells[0]
    if shade:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), shade)
        tcPr.append(shd)
    p = cell.paragraphs[0]
    if text:
        lines = text if isinstance(text, list) else [text]
        for i, line in enumerate(lines):
            if i:
                p = cell.add_paragraph()
            add_rich(p, line, size=size)
    if height_cm:
        tr = t.rows[0]._tr
        trPr = tr.get_or_add_trPr()
        h = OxmlElement("w:trHeight")
        h.set(qn("w:val"), str(int(height_cm * 567)))
        h.set(qn("w:hRule"), "atLeast")
        trPr.append(h)
    para(doc, "", after=2)
    return t


def add_page_number_footer(section, label):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rich(p, f"{label}  ·  Page ", size=8, color=GREY)
    for kind, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        run = p.add_run()
        run.font.size = Pt(8)
        run.font.color.rgb = GREY
        if kind:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            run._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            run._r.append(it)


def new_document(footer_label):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for side in ("left_margin", "right_margin"):
        setattr(sec, side, Cm(MARGIN))
    sec.top_margin, sec.bottom_margin = Cm(1.5), Cm(1.5)
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.font.size = Pt(11)
    add_page_number_footer(sec, footer_label)
    return doc


# ---------------------------------------------------------------- marks

def question_marks(q):
    if "marks" in q:
        return float(q["marks"])
    return sum(float(s.get("marks", 0)) for s in q.get("subparts", []))


def check_marks(spec):
    """Return (total, problems). Subparts must add up to their parent's marks."""
    total, problems = 0.0, []
    for s_i, sec in enumerate(spec.get("sections", []), 1):
        for q_i, q in enumerate(sec.get("questions", []), 1):
            m = question_marks(q)
            total += m
            subs = q.get("subparts")
            if subs and "marks" in q:
                sub_total = sum(float(s.get("marks", 0)) for s in subs)
                if abs(sub_total - float(q["marks"])) > 1e-9:
                    problems.append(
                        f"{sec.get('title', f'Section {s_i}')} Q{q_i}: subparts add to "
                        f"{fmt(sub_total)} but question says {fmt(q['marks'])}")
            alt = q.get("or")
            if alt and "marks" in alt and abs(float(alt["marks"]) - m) > 1e-9:
                problems.append(
                    f"{sec.get('title', f'Section {s_i}')} Q{q_i}: OR-choice carries "
                    f"{fmt(alt['marks'])} marks but main question carries {fmt(m)}")
    want = spec.get("total_marks")
    if want is not None and abs(total - float(want)) > 1e-9:
        problems.append(f"Questions add up to {fmt(total)} but total_marks is {fmt(want)}")
    return total, problems


def fmt(x):
    x = float(x)
    return str(int(x)) if x.is_integer() else f"{x:g}"


# ---------------------------------------------------------------- paper

def header_block(doc, spec, key=False):
    academy = spec.get("academy", "Level Up Academy")
    para(doc, academy.upper(), size=17, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
    meta = " | ".join(x for x in [
        f"Class {spec['class']}" if spec.get("class") else "",
        spec.get("board", ""), spec.get("subject", "")] if x)
    if meta:
        para(doc, meta, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=0, color=GREY)
    title = spec.get("title", "")
    if key:
        para(doc, "ANSWER KEY & MARKING SCHEME", size=10, bold=True,
             align=WD_ALIGN_PARAGRAPH.CENTER, before=4, after=0, color=GREY)
    para(doc, title, size=13.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=4, after=0)
    if spec.get("chapter"):
        para(doc, f"Chapter / Topic: {spec['chapter']}", size=10.5, italic=True,
             align=WD_ALIGN_PARAGRAPH.CENTER, after=4)

    if key:
        para(doc, "For teacher use only. Do not distribute to students.", size=9,
             italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, after=6)
        return

    # Name / roll / date line, then time / marks line (tab stops, so nothing wraps)
    rows = [
        ("Name: ______________________________", "Roll No.: _______",
         f"Date: {spec.get('date') or '___________'}", False),
        (f"Time: {spec['time']}" if spec.get("time") else "", "",
         f"Max. Marks: {fmt(spec['total_marks'])}" if spec.get("total_marks") is not None
         else "Marks obtained: ______", True),
    ]
    for left, mid, right, bold in rows:
        p = para(doc, "", after=4, before=4)
        tabs = p.paragraph_format.tab_stops
        tabs.add_tab_stop(Cm(TEXT_W * 0.62), WD_TAB_ALIGNMENT.CENTER)
        tabs.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
        add_rich(p, f"{left}\t{mid}\t{right}", size=10.5, bold=bold)
    rule = para(doc, "", after=4)
    bottom_border(rule, sz=12, color="000000")

    ins = spec.get("instructions") or []
    if ins:
        para(doc, "General instructions:", size=10, bold=True, after=1)
        for i, line in enumerate(ins, 1):
            para(doc, f"{i}. {line}", size=9.5, after=0, indent=0.4)
        para(doc, "", after=2)


def q_line(doc, number, text, marks, indent=0.0, hang=0.9, keep=False):
    """Question paragraph: number, text, and [marks] flush right."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Pt(5), Pt(2)
    pf.keep_with_next = keep  # only glue to options/subparts/answer lines that follow
    pf.left_indent = Cm(indent + hang)
    pf.first_line_indent = Cm(-hang)
    pf.tab_stops.add_tab_stop(Cm(indent + hang))
    pf.tab_stops.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
    add_rich(p, f"{number}\t", bold=True)
    add_rich(p, text)
    if marks is not None:
        add_rich(p, f"\t[{fmt(marks)}]", bold=True, size=10)
    return p


def options_block(doc, options, indent):
    labels = [f"({LETTERS[i]}) {o}" for i, o in enumerate(options)]
    short = all(len(re.sub(r"[*_^{}]", "", o)) <= 30 for o in options)
    if short and len(options) == 4:
        half = TEXT_W - indent
        for row in (labels[:2], labels[2:]):
            p = para(doc, "", after=0, indent=indent)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(indent + half / 2))
            add_rich(p, row[0] + "\t" + row[1], size=10.5)
    else:
        for lab in labels:
            para(doc, lab, size=10.5, after=0, indent=indent)


def render_question(doc, number, q, worksheet, indent=0.0):
    marks = question_marks(q) if ("marks" in q or q.get("subparts")) else None
    has_body = bool(q.get("options") or q.get("subparts") or q.get("or") or q.get("box_cm")
                    or (worksheet and q.get("lines", default_lines(q))))
    q_line(doc, number, q["q"], marks, indent=indent, keep=has_body)
    body_indent = indent + 0.9

    if q.get("options"):
        options_block(doc, q["options"], body_indent)
    for i, sub in enumerate(q.get("subparts", [])):
        q_line(doc, f"({ROMAN[i]})", sub["q"], sub.get("marks"), indent=body_indent, hang=0.8,
               keep=bool(sub.get("options") or worksheet))
        if sub.get("options"):
            options_block(doc, sub["options"], body_indent + 0.8)
        if worksheet:
            answer_lines(doc, sub.get("lines", default_lines(sub)), indent=body_indent + 0.8)
    if q.get("box_cm"):
        boxed(doc, height_cm=float(q["box_cm"]))
    if worksheet and not q.get("subparts"):
        answer_lines(doc, q.get("lines", default_lines(q)), indent=body_indent)

    alt = q.get("or")
    if alt:
        orp = para(doc, "OR", size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, before=2, after=0)
        orp.paragraph_format.keep_with_next = True
        q_line(doc, "", alt["q"], None, indent=indent,
               keep=bool(alt.get("options") or worksheet))
        if alt.get("options"):
            options_block(doc, alt["options"], body_indent)
        if worksheet:
            answer_lines(doc, alt.get("lines", default_lines(alt)), indent=body_indent)


def default_lines(q):
    if q.get("options"):
        return 0
    m = float(q.get("marks", 2))
    return int(min(10, max(2, m * 2)))


def render_paper(spec, path):
    worksheet = spec.get("type", "test") == "worksheet"
    doc = new_document(f"{spec.get('academy', 'Level Up Academy')}  ·  {spec.get('title', '')}")
    header_block(doc, spec)
    n = 0
    for sec in spec.get("sections", []):
        if sec.get("title"):
            sec_marks = sum(question_marks(q) for q in sec.get("questions", []))
            p = para(doc, "", before=8, after=1)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
            p.paragraph_format.keep_with_next = True
            add_rich(p, sec["title"].upper(), size=11.5, bold=True)
            if sec_marks and not worksheet:
                add_rich(p, f"\t{fmt(sec_marks)} marks", size=9.5, color=GREY)
            bottom_border(p, sz=4, color="BBBBBB")
        if sec.get("note"):
            para(doc, sec["note"], size=9.5, italic=True, after=2, color=GREY)
        for q in sec.get("questions", []):
            n += 1
            render_question(doc, f"Q{n}.", q, worksheet)
    closing = spec.get("closing", "All the best!")
    if closing:
        para(doc, f"~ {closing} ~", size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
             before=14)
    doc.save(path)


def has_answers(spec):
    for sec in spec.get("sections", []):
        for q in sec.get("questions", []):
            if q.get("answer") or any(s.get("answer") for s in q.get("subparts", [])):
                return True
    return False


def render_key(spec, path):
    doc = new_document(f"Answer key  ·  {spec.get('title', '')}  ·  teacher copy")
    header_block(doc, spec, key=True)
    n = 0
    for sec in spec.get("sections", []):
        if sec.get("title"):
            p = para(doc, sec["title"].upper(), size=11.5, bold=True, before=8, after=2)
            bottom_border(p, sz=4, color="BBBBBB")
        for q in sec.get("questions", []):
            n += 1
            key_entry(doc, f"Q{n}.", q)
    doc.save(path)


def key_entry(doc, number, q, indent=0.0):
    marks = question_marks(q) if ("marks" in q or q.get("subparts")) else None
    q_line(doc, number, short(q["q"]), marks, indent=indent, keep=True)
    body = indent + 0.9
    if q.get("answer"):
        para(doc, f"**Answer:** {q['answer']}", size=10.5, after=1, indent=body)
    for pt in q.get("marking", []):
        para(doc, f"• {pt}", size=10, after=0, indent=body + 0.3)
    for i, sub in enumerate(q.get("subparts", [])):
        mk = f"  [{fmt(sub['marks'])}]" if "marks" in sub else ""
        para(doc, f"({ROMAN[i]}) {sub.get('answer', '')}{mk}", size=10.5, after=0, indent=body)
        for pt in sub.get("marking", []):
            para(doc, f"• {pt}", size=10, after=0, indent=body + 0.6)
    alt = q.get("or")
    if alt and alt.get("answer"):
        para(doc, f"**OR, answer:** {alt['answer']}", size=10.5, after=0, indent=body)
        for pt in alt.get("marking", []):
            para(doc, f"• {pt}", size=10, after=0, indent=body + 0.3)


def short(text, n=110):
    """Truncate to about n visible characters without breaking **bold** / _{sub} / ^{sup} markup."""
    flat = " ".join(str(text).split())
    out, seen = [], 0
    for part in TOKEN.split(flat):
        if not part:
            continue
        visible = len(re.sub(r"^\*\*|\*\*$|^[_^]\{|\}$", "", part))
        if seen + visible <= n:
            out.append(part)
            seen += visible
            continue
        if TOKEN.fullmatch(part):  # don't split a markup token
            break
        out.append(part[: max(0, n - seen)].rstrip())
        break
    result = "".join(out)
    return result if result == flat else result.rstrip() + "…"


# ---------------------------------------------------------------- notes

def render_notes(spec, path):
    doc = new_document(f"{spec.get('academy', 'Level Up Academy')}  ·  {spec.get('title', '')}")
    academy = spec.get("academy", "Level Up Academy")
    para(doc, academy.upper(), size=15, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
    meta = " | ".join(x for x in [f"Class {spec['class']}" if spec.get("class") else "",
                                  spec.get("board", ""), spec.get("subject", "")] if x)
    if meta:
        para(doc, meta, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY, after=0)
    para(doc, spec.get("title", ""), size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         before=4, after=2)
    rule = para(doc, "", after=4)
    bottom_border(rule, sz=12, color="000000")
    for block in spec.get("blocks", []):
        if "h" in block:
            para(doc, block["h"], size=12.5, bold=True, before=8, after=2)
        elif "p" in block:
            para(doc, block["p"], size=11, after=3)
        elif "bullets" in block:
            for b in block["bullets"]:
                bp = para(doc, f"•\t{b}", size=11, after=1, indent=0.9)
                bp.paragraph_format.first_line_indent = Cm(-0.5)
                bp.paragraph_format.tab_stops.add_tab_stop(Cm(0.9))
        elif "box" in block:
            para(doc, "", after=0, size=4)
            boxed(doc, block["box"], shade="F2F2F2")
        elif "table" in block:
            rows = block["table"]
            t = doc.add_table(rows=len(rows), cols=len(rows[0]))
            t.style = "Table Grid"
            for r, row in enumerate(rows):
                for c, txt in enumerate(row):
                    add_rich(t.rows[r].cells[c].paragraphs[0], txt, size=10, bold=(r == 0))
            para(doc, "", after=3)
        elif "lines" in block:
            answer_lines(doc, block["lines"], indent=0)
    doc.save(path)


# ---------------------------------------------------------------- main

def to_pdf(docx_path, out_dir):
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        print("  (LibreOffice not found, so DOCX only)")
        return None
    subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir),
                    str(docx_path)], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=180)
    pdf = Path(out_dir) / (Path(docx_path).stem + ".pdf")
    return pdf if pdf.exists() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", default="private/output")
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = slugify(spec.get("file_name") or
                   " ".join(str(x) for x in [f"class{spec.get('class', '')}", spec.get("subject", ""),
                                              spec.get("title", "")] if x))
    kind = spec.get("type", "test")

    made = []
    if kind == "notes":
        p = out / f"{slug}.docx"
        render_notes(spec, p)
        made.append(p)
    else:
        total, problems = check_marks(spec)
        if problems:
            print("MARKS CHECK FAILED:")
            for pr in problems:
                print("  -", pr)
            sys.exit(2)
        print(f"Marks check OK: {fmt(total)} marks")
        p = out / f"{slug}.docx"
        render_paper(spec, p)
        made.append(p)
        if has_answers(spec):
            k = out / f"{slug}-answer-key.docx"
            render_key(spec, k)
            made.append(k)

    for d in list(made):
        if not args.no_pdf:
            pdf = to_pdf(d, out)
            if pdf:
                made.append(pdf)
    for m in made:
        print(m)


if __name__ == "__main__":
    main()
