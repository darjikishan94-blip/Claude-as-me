---
name: test-paper
description: Make printable test papers (unit tests, chapter tests, weekly tests, mock and prelim papers) with an answer key and marking scheme for Level Up Academy, in CBSE or GSEB style, as DOCX + PDF. Use for "make a test", "question paper", "unit test", "25 marks paper", "mock paper", "set B", "MCQ test" and similar.
---

# Test papers

Output a **print-ready paper plus a separate answer key** (DOCX + PDF), built with `tools/make_paper.py`. Accuracy matters more than speed: one wrong answer in a key costs Kishan's credibility in front of students.

## 0. Check the library first
`library/README.md` lists ready-made, checked material. For Class 10 Science there is a 25-mark test for every chapter, two full mocks (CBSE and GSEB pattern), revision notes and a 90-day plan.
- If the request matches something there, send that PDF and its answer key straight away. For an editable copy, send the DOCX.
- If Kishan wants a different version ("Set B", another mark total, a mix of chapters), copy the closest spec from `library/.../*.json` to `private/papers/`, change the questions, and build it. Don't start from zero.
- **GSEB batch?** Every Class 10 chapter also has a GSEB-pattern test (`chNNg-*.json`, 9×1 objective, 3×2, 2×3, 1×4), rebuilt from the checked Set A + Set B questions by `python3 tools/remix_gseb.py`.
- Something new and reusable (no student data) can go into `library/<area>/<kind>/`. Run `python3 tools/build_library.py` to build it and refresh the index.

## 1. Pin down the brief
Fill these from the request. Ask only for what's missing and can't be inferred.

| Field | Default if not given |
|---|---|
| Class, board | **Ask.** Board decides the pattern. "Both" means CBSE style, header "CBSE / GSEB" |
| Subject, chapters/topics | **Ask** if not given. Use Kishan's chapter names exactly |
| Total marks | 25 |
| Time | 25 marks → 50 min · 40 → 1 h 30 min · 80 → 3 h |
| Difficulty | about 30% easy · 50% medium · 20% challenging |
| Date | blank line on the paper |

**Syllabus caution:** NCERT has new books for Class 8 (*Curiosity*) and Class 9 (*Exploration*, 2026-27). Don't rely on old chapter numbers. Use the topic names Kishan gives, or the chapter list in `me/academy.md`. If you're unsure whether a topic is still in this year's book, say so in your reply.

## 2. Blueprint (pick by board and size)
These follow the latest **reported** board patterns. Confirm each year against the official sample paper (CBSE: cbseacademic.nic.in · GSEB: gseb.org). If Kishan pastes the official blueprint into `me/academy.md`, that wins.

**CBSE style (Class 9–10 Science)**: section types are A = MCQ + Assertion–Reason (1), B = very short answer (2), C = short answer (3), D = long answer (5), E = case-based with subparts (4).
| Total | A | B | C | D | E |
|---|---|---|---|---|---|
| 25 | 6×1 | 2×2 | 2×3 | 1×5 | 1×4 |
| 40 | 9×1 | 3×2 | 4×3 | 1×5 | 2×4 |
| 80 (full board pattern) | 20×1 | 6×2 | 7×3 | 3×5 | 3×4 |
Give internal choice (`"or"`) in about one question per section from B onwards. At 80 marks, split roughly Biology 30 · Chemistry 25 · Physics 25 if the paper is full-syllabus.

**GSEB style (Std 9–10 Science)**: A = objective (MCQ, fill in the blank, true/false, one-word, match: 1 each), B = short answer (2), C = short answer + diagrams (3), D = long answer + diagrams (4).
| Total | A | B | C | D |
|---|---|---|---|---|
| 25 | 9×1 | 3×2 | 2×3 | 1×4 |
| 40 | 12×1 | 4×2 | 4×3 | 2×4 |
| 80 (full board pattern) | 24×1 | 9×2 | 6×3 | 5×4 |

**Class 8 / school tests**: a mix of MCQ, fill in the blank, true/false, match the following, short answer, one diagram and one long answer. Keep the language simple.

## 3. Write the questions
- **Every question has exactly one correct answer.** For MCQs, use 4 plausible options with one clearly right; no "all of the above" tricks. Rotate where the correct option sits.
- **Check science atom by atom and unit by unit.** Balance every equation (count each element on both sides). Solve every numerical fully, with units and sensible numbers.
- Mix textbook-style questions with **fresh variants** (changed numbers, new contexts, Indian everyday examples). Don't just copy exercise questions.
- CBSE style needs competency questions: case-based passages, assertion–reason (use the standard 4 options, see the sample), "give reason" and application questions.
- Diagram questions: "Draw a neat, labelled diagram of …" and add `"box_cm": 6` for drawing space if answers are written on the paper. The renderer can't draw figures. For "label this figure" questions, describe the figure in words, or ask Kishan for an image and say it's not embedded.
- Never use real student names. Fictional first names in case studies are fine.
- Write the **answer and marking points** for every question as you go (`answer`, `marking`).

## 4. Build the files
1. Write the spec to `private/papers/<class>-<subject>-<topic>.json`. `private/` is git-ignored.
2. Run `python3 tools/balance_mcq.py private/papers/<file>.json`. This spreads correct MCQ answers evenly across (a)–(d) and keeps numeric options in ascending order. It leaves Assertion–Reason and "all of the above" questions alone.
3. Run `python3 tools/make_paper.py private/papers/<file>.json --out private/output`.
   The script **refuses to build** if the marks don't add up (section totals, subparts, OR choices, `attempt` sections), if any chemical equation is unbalanced (it counts atoms), or if an MCQ key doesn't point at a real option. Fix the spec and re-run. Mark deliberately unbalanced text (a "balance this" question, wrong MCQ options) with `"unbalanced": true`.
4. **Self-check pass.** Re-read the key as a strict examiner: re-solve every numerical, re-balance every equation, confirm each MCQ has exactly one defensible answer, and check that the time allotted is realistic. Fix and rebuild if anything is off.
5. Send with SendUserFile: the **paper PDF** and the **answer key PDF**, plus the paper DOCX only if Kishan may edit it.

## 5. Reply (short)
- One line: `Class 10 CBSE · Chemical Reactions · 25 marks / 50 min · 6 MCQ, 2×2, 2×3, 1×5, 1 case study`.
- Anything Kishan should check (a topic that may have moved in the new book, a figure not included).
- Offer one next step: "Want a **Set B** (same pattern, different questions) or a matching practice worksheet?"

## Spec format (JSON)
See `samples/class10-science-ch1-unit-test.json` for a complete example.
```json
{
  "type": "test",
  "title": "Unit Test: <topic>", "class": "10", "board": "CBSE", "subject": "Science",
  "chapter": "<chapter names>", "time": "50 minutes", "total_marks": 25, "date": "",
  "instructions": ["All questions are compulsory.", "..."],
  "sections": [
    {"title": "Section A", "note": "Choose the correct option.", "questions": [
      {"q": "Question with H_{2}O and 10^{-3} markup", "marks": 1,
       "options": ["...", "...", "...", "..."], "answer": "(b) ..."}
    ]},
    {"title": "Section C", "questions": [
      {"q": "Stem / case text", "subparts": [
        {"q": "Part (i)", "marks": 1, "answer": "..."},
        {"q": "Part (ii)", "marks": 2, "answer": "...", "marking": ["point: 1", "point: 1"]}
      ]},
      {"q": "Main question", "marks": 3, "answer": "...",
       "or": {"q": "Alternative question", "marks": 3, "answer": "..."}}
    ]}
  ],
  "closing": "All the best!"
}
```
Inline markup: `**bold**`, `H_{2}O` (subscript), `Fe^{3+}` (superscript), and `\n` for a line break (e.g. between (a) and (b) of an OR question).
Optional per question: `"box_cm": 6` (drawing box), `"lines": 4` (answer lines, worksheets only), `"image": "fig.png"` with `"image_width_cm": 7` (path relative to the spec), `"unbalanced": true`, `"fixed_order": true` (balancer won't move options).
Optional per section: `"attempt": 9` for GSEB-style "answer any 9" (every question in that section must carry the same marks), and `"unbalanced": true`.
Optional top-level: `"file_name"` and `"academy"`.
Assertion–Reason in a big paper: put the four standard choices once in the section `note` and give each A–R question only an `answer` such as "(a)". See `library/class10-science/mocks/cbse-mock-1.json`.
