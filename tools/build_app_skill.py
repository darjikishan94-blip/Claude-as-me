#!/usr/bin/env python3
"""Package Claude-as-me as ONE skill you can upload to the regular Claude app (claude.ai),
so every chat (not only Claude Code sessions on this repo) can write and work as Kishan.

Usage:  python3 tools/build_app_skill.py        -> dist/kishan-as-me.zip

Re-run after changing anything in me/ or .claude/skills/, then re-upload the zip in
Claude → Settings → Capabilities → Skills.
"""

import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
NAME = "kishan-as-me"
OUT = DIST / NAME

SKILLS = ["reply-as-me", "parent-messages", "test-paper", "worksheet-notes", "test-results"]
ME = ["voice.md", "academy.md", "profile.md", "youtube.md"]

# repo paths -> paths inside the uploaded skill / the claude.ai sandbox
REWRITES = [
    (r"- Something new and reusable.*?refresh the index\.", "- Something new and reusable: give Kishan the spec so it can be added to the library in the Claude-as-me repo."),
    (r"Rebuild after any spec change with `python3 tools/build_library\.py`\. ", ""),
    (r"`library/README\.md`", "`library/INDEX.md`"),
    (r"`library/\.\.\./\*\.json`", "`library/` (see INDEX.md)"),
    (r"python3 tools/", "python3 scripts/"),
    (r"`tools/make_paper\.py`", "`scripts/make_paper.py`"),
    (r"`tools/marks_report\.py`", "`scripts/marks_report.py`"),
    (r"--out private/output", "--out /mnt/user-data/outputs"),
    (r"private/output/", "/mnt/user-data/outputs/"),
    (r"private/papers/", "/tmp/papers/"),
    (r"private/marks-", "/tmp/marks-"),
    (r"write it into `me/` and commit", "say `Lesson to save: …` so it lands in the Claude-as-me repo"),
    (r"See `open-questions\.md`\. ", ""),
    (r"`private/`, which is git-ignored,", "the sandbox's /tmp"),
    (r"`private/` \(git-ignored\)", "/tmp in the sandbox"),
    (r"`private/`", "/tmp"),
    (r"`private/` is git-ignored\.", ""),
    (r"with SendUserFile", "by saving it to /mnt/user-data/outputs"),
    (r"SendUserFile", "a file in /mnt/user-data/outputs"),
    (r"`me/(voice|academy|profile|youtube)\.md`", r"`reference/\1.md`"),
    (r"`samples/([\w.-]+)`", r"`samples/\1`"),
    (r"the \*\*test-results\*\* skill", "`reference/test-results.md`"),
    (r"`(reply-as-me|parent-messages|test-paper|worksheet-notes|test-results)`", r"`reference/\1.md`"),
    (r"following the learning loop in `CLAUDE\.md`",
     "by giving Kishan the lesson in one line so it can be saved in the Claude-as-me repo"),
    (r"through `learn-me`", "in a Claude-as-me session (learn-me)"),
    (r"Fill them in through the `learn-me` skill\.", "Fill them in through a Claude-as-me session (learn-me)."),
    (r"Never commit them\.", "Never paste them anywhere public."),
    (r"never commit them", "never paste them anywhere public"),
    (r"\*\*Never commit it\.\*\*", "**Never share it publicly.**"),
]

ROUTER = """---
name: kishan-as-me
description: Work and write AS Kishan, owner of Level Up Academy (CBSE + GSEB coaching). Use for any message, reply or post written as Kishan, any Level Up Academy parent message, notice or enquiry reply, test papers, worksheets, revision notes, and turning test marks into result messages. Fee reminders and payment confirmations use the separate parent-fee-messages skill.
---

# Kishan-as-me

You are acting **as Kishan**. Think, write and decide the way Kishan would. Everything you need is in this skill's folder.

## Always
- Read `reference/voice.md` before writing anything. Its "Learned from Kishan" section overrides the rest.
- Read `reference/academy.md` for anything about the academy. Facts marked [confirm] are unknown, so never guess them.
- **Draft, don't send.** Put each message in its own code block, ready to paste into WhatsApp.
- **Never invent** fees, dates, marks, timings or student details. Verify weekdays with Python before writing "Saturday, 8 Nov".
- Group messages never name a student or show marks or amounts.

## Route the task
| Task | Read |
|---|---|
| Reply to a pasted message / screenshot, or write anything as Kishan | `reference/reply-as-me.md` |
| Notices, PTM, absence, concern, appreciation, enquiry replies (not fees) | `reference/parent-messages.md` |
| Test / question paper with answer key | `reference/test-paper.md` |
| Worksheet, homework sheet, revision notes, question bank | `reference/worksheet-notes.md` |
| Marks → summary + parent result messages | `reference/test-results.md` |
| YouTube channel ideas | `reference/youtube.md` |
| Fee reminders / confirmations | the **parent-fee-messages** skill |

## Ready-made library
`library/INDEX.md` lists checked Class 10 Science material, stored as specs: 13 chapter tests with keys, 13 revision sheets, CBSE and GSEB mocks, and the 90-day plan. It also lists message kits (admissions, board-season parent messages) and YouTube scripts as Markdown.
To give Kishan a PDF, build it from the spec: `python3 <this-skill-dir>/scripts/make_paper.py <this-skill-dir>/library/<path>.json --out /mnt/user-data/outputs`. **Check the library before writing anything new.**

## Files & scripts (claude.ai sandbox)
- The scripts are in this skill's `scripts/` folder. Run them with the full path to this skill folder, e.g. `python3 <this-skill-dir>/scripts/make_paper.py /tmp/papers/x.json --out /mnt/user-data/outputs`.
- If `import docx` fails, run `pip install python-docx openpyxl` first. If LibreOffice is missing you'll get DOCX only, which is fine.
- Worked examples are in `samples/`.

## Learning
When Kishan corrects you, apply the correction now. Then end with one line: `Lesson to save: …`, so Kishan can store it in the Claude-as-me repo, where the master copy of these files lives.
"""


def strip_frontmatter(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).lstrip()


def rewrite(text):
    for pat, rep in REWRITES:
        text = re.sub(pat, rep, text)
    return text


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "reference").mkdir(parents=True)
    (OUT / "scripts").mkdir()
    (OUT / "samples").mkdir()
    (OUT / "SKILL.md").write_text(ROUTER, encoding="utf-8")
    for f in ME:
        (OUT / "reference" / f).write_text(rewrite((ROOT / "me" / f).read_text(encoding="utf-8")), encoding="utf-8")
    for s in SKILLS:
        body = strip_frontmatter((ROOT / ".claude/skills" / s / "SKILL.md").read_text(encoding="utf-8"))
        (OUT / "reference" / f"{s}.md").write_text(rewrite(body), encoding="utf-8")
    for f in ("make_paper.py", "marks_report.py", "check_spec.py", "balance_mcq.py"):
        shutil.copy(ROOT / "tools" / f, OUT / "scripts" / f)
    index = ["# Library index (specs: build any of them with scripts/make_paper.py)", ""]
    for src in sorted((ROOT / "library").rglob("*")):
        if src.suffix not in (".json", ".md") or src.name == "README.md" or "pdf" in src.parts:
            continue
        rel = src.relative_to(ROOT)
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest)
        if src.suffix == ".json":
            title = json.loads(src.read_text(encoding="utf-8")).get("title", src.stem)
        else:
            title = src.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
        index.append(f"- `{rel.as_posix()}`: {title}")
    (OUT / "library" / "INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    for f in sorted((ROOT / "samples").glob("*.json")):
        shutil.copy(f, OUT / "samples" / f.name)

    zpath = DIST / f"{NAME}.zip"
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(DIST))
    print(zpath)


if __name__ == "__main__":
    main()
