---
name: worksheet-notes
description: Make printable study material for Level Up Academy students as DOCX + PDF. This covers practice worksheets, homework sheets, revision sheets, chapter question banks, one-page notes, formula and definition sheets, and "important questions" lists, with answer keys. Use for "worksheet", "practice sheet", "homework", "revision notes", "short notes", "formula sheet", "important questions", "question bank". For graded tests use test-paper.
---

# Worksheets & notes

Same engine and the same accuracy bar as `test-paper`. Read its sections **1 (brief)** and **3 (write the questions)**. The differences are below.

## Pick the format
| Request | `type` | Shape |
|---|---|---|
| Practice / homework / revision worksheet | `worksheet` | Questions with answer lines (`"lines": n`), no marks needed, plus a separate answer key |
| Chapter question bank / important questions | `worksheet` | Grouped by type (1-mark, 2-mark, 3-mark, 5-mark), `"lines": 0`, plus answer key |
| Short notes / one-page revision / formula sheet | `notes` | `blocks`: headings, paragraphs, bullets, tables, boxed "Remember" tips |

## Worksheets
- Build in order: warm-up (recall), then core practice, then 1–2 challenge questions.
- Default length: 10–15 questions, which fit on 1–2 pages.
- Answer lines scale with the answer: one-word 1 line, short answer 2–3 lines, explanation 4–6 lines, numerical 4 lines.
- Add a one-line tip in `instructions` in Kishan's voice ("Count every atom on both sides!").
- `closing` gets a warm line ("Keep practising, you've got this!").
- Example spec: `samples/class10-balancing-worksheet.json`.

## Notes
- One page where possible, two at most. Students should be able to revise from it the night before.
- Structure: key terms (table: term | meaning) → core ideas (bullets) → equations/formulas (box) → common mistakes (bullets) → 3 quick self-check questions (lines).
- Only the most-tested points. Use short phrases, not paragraphs.

Notes spec:
```json
{
  "type": "notes", "title": "Quick Revision: <topic>", "class": "9", "board": "CBSE", "subject": "Science",
  "blocks": [
    {"h": "Key terms"},
    {"table": [["Term", "Meaning"], ["Speed", "Distance travelled per unit time"]]},
    {"h": "Must-know points"},
    {"bullets": ["...", "..."]},
    {"box": ["Remember: v = u + at", "s = ut + ½at^{2}"]},
    {"h": "Quick check"},
    {"p": "1. ..."}, {"lines": 2}
  ]
}
```

## Build & deliver
1. Write the spec to `private/papers/<name>.json`.
2. Run `python3 tools/make_paper.py private/papers/<name>.json --out private/output`.
3. Self-check: re-solve every answer, re-balance every equation, and check units.
4. Send the PDF(s) with SendUserFile: the worksheet and the answer key. Add the DOCX only if Kishan will edit it.
5. Reply in one line, then offer the natural next thing ("Want the matching 25-mark test?").
