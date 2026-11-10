---
name: test-results
description: Turn a test's marks into a class result summary, a ranked sheet, and individual WhatsApp result messages to parents in Kishan's voice, plus a list of students who need extra support. Use when Kishan shares marks (pasted list, photo of a mark list, CSV or Excel) or asks "send results", "result messages", "who needs help", "analyse the test".
---

# Test results → parent messages

**Privacy first:** marks are student data. Work only in `private/` (git-ignored) and never commit them. Don't paste the full mark list back into chat unless Kishan asks.

## Steps
1. **Get the data in.**
   - Pasted list or photo: write it to `private/marks-<class>-<test>.csv` with columns `Name,Marks` (add a previous-test column if Kishan gives one). Read a photo carefully, then show Kishan any name or number you weren't sure of **before** going further.
   - Excel/CSV: use it as-is.
   - Confirm **max marks**. Never assume it.
2. **Run the numbers.** Don't do the maths by hand:
   `python3 tools/marks_report.py private/marks-....csv --max 25 [--prev "Test 1"] --out private/output/<class>-<test>-results.xlsx`
   It validates the marks, computes average, median, bands, ranks and tiers, and writes a coloured sheet.
3. **Give Kishan the summary** in 4–6 lines: average, highest, lowest, how many are in each tier, big movers, absentees, and one teaching insight if the data shows it (e.g. "most marks lost in Section C, so numericals need another round").
4. **Draft the parent messages** (below), one per student, using the tier from the report.
5. **Send** the results xlsx with SendUserFile.

## Parent message templates (one-to-one only)
First name only. Exact marks as `22/25`. **Never mention rank, class average or any other child** unless Kishan asks for that.

**Top (≥ 80%)**
```
Hi! Happy to share [Name]'s result in the [chapter/test] test: [marks]/[max] 🎉
[One specific line: great with numericals / neat diagrams / consistent effort.]
Please do give [him/her] a pat on the back from us!
```

**Steady (50–79%)**
```
Hi! Sharing [Name]'s result in the [chapter/test] test: [marks]/[max].
[One genuine positive.] [One specific thing to improve, e.g. writing complete answers / units in numericals.]
We'll keep working on it in class 🙂
```

**Needs support (< 50%)**: positive → specific → plan → partnership
```
Hi! Sharing [Name]'s result in the [chapter/test] test: [marks]/[max].
[He/She] [genuine positive: is regular / participates well], so I know [he/she] can do better.
Most marks were lost in [area, if known]. I'll [plan: extra practice sheet / short revision with [him/her]].
It would really help if [he/she] [one small habit at home, e.g. revises 20 minutes daily this week]. Happy to talk anytime.
```

**Improved a lot** (change ≥ +10 points): add "That's a big jump from last time 👏" to whichever template fits.

**Absent**
```
Hi! [Name] missed the [chapter/test] test on [day, date]. Hope all is well 🙂
[He/She] can take it on [day/time] [or: we'll include these chapters in the next test].
```

## Group message (optional, no names, no marks)
```
Hello Parents,
Results of the [chapter] test have been shared with each of you individually.
[One class-level line, e.g. "Many students did really well in the MCQs. We'll do extra practice on numericals this week."]
Thank you!
```
Only name toppers in a group if Kishan explicitly asks. If Kishan does, record that preference in `me/voice.md`.

## Present
1. The summary (4–6 lines).
2. **Ready to send:** one code block per student, labelled `[Name]: [marks]/[max] · [tier]`, ordered top → support → absent.
3. **Check before sending:** the "needs support" messages, where the specific "area" is only known if Kishan told you or the paper analysis shows it (otherwise leave `[area]` for Kishan), and any uncertain readings from a photo.
4. Offer a follow-up: "Want a practice worksheet for the [n] students who need support?" (see `worksheet-notes`).

## Printed report card (PTM / end of term)
`library/admin/notes/form-progress-report.json` is a blank one-page **Student Progress Report** (details, test record, skills grid, teacher's note, parent's note). It prints from the Level Up Library (Admin → Forms and templates). Teachers fill it in by hand. If Kishan wants filled-in cards, generate them only into `private/` from the marks he shares, and never commit them.
