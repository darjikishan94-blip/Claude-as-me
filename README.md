# Claude-as-me

My AI twin. Claude reads this repo and works **as me (Kishan)**. It writes in my voice, runs Level Up Academy admin, and makes tests and study material.

## What it can do
| Say something like… | What you get | Skill |
|---|---|---|
| *"Reply to this"* + paste or screenshot a message | A ready-to-paste reply in my voice. For tricky ones, an "if yes / if no" pair | `reply-as-me` |
| *"Tell Class 9 parents there's no class on Monday"* | WhatsApp notice in the right tone for that group | `parent-messages` |
| *"Reply to this admission enquiry"* | Warm enquiry reply + follow-up | `parent-messages` |
| *"25-mark test, Class 10 CBSE, Chemical Reactions"* | Print-ready **PDF paper + answer key**, with marks checked | `test-paper` |
| *"Practice worksheet on balancing equations"* / *"one-page notes on Motion"* | Printable worksheet / revision sheet + key | `worksheet-notes` |
| *"Here are the marks"* + list, photo or Excel | Class summary, ranked sheet, and one result message per parent | `test-results` |
| *"Interview me"* / *"remember that tests are on Saturdays"* | Claude learns more about me and saves it | `learn-me` |
| *"Fee reminder for Class 8"* | Uses my existing **parent-fee-messages** skill | (on my Claude account) |

You don't need to name the skill. Just ask normally.

## 📚 Ready-made content library
**[library/README.md](library/README.md)** has everything ready to print, all automatically checked (marks add up, equations balanced, answer keys valid):
- **Class 10 Science:** a 25-mark test + answer key for all 13 chapters, and a one-page revision sheet for each
- **Set B re-tests** for every chapter, so each chapter has two different 25-mark tests
- **GSEB-pattern chapter tests** for all 13 chapters (9 objective + 3×2 + 2×3 + 1×4), built from the checked questions
- **Most-expected question banks** for Chemistry, Physics and Biology (1/2/3/5-mark, with answers)
- **Final-revision sheets:** all-chapter equation sheet (75 checked equations), physics formula sheet, diagram checklist
- **Four full 80-mark mock papers**: Mock 1 and Mock 2 in both CBSE and GSEB patterns, with marking schemes
- **Class 9 Foundation practice packs** (Motion, Force & Laws of Motion, Work & Energy, Sound, Atomic Structure, The Cell, Tissues, Mixtures & Separation, States of Matter, Gravitation): 3 levels each, worked answer keys, usable with the old or new Class 9 book
- **Class 9 unit tests** (25 marks, with keys): Motion, Force & Laws of Motion, Work & Energy, Sound, Structure of the Atom, Matter in Our Surroundings, Mixtures & Separation, The Cell, Tissues
- **Class 8 practice packs** (Force & Pressure, Microorganisms, Metals & Non-metals, Combustion & Flame, Sound) and **Class 8 unit tests** (Force & Pressure, Metals & Non-metals, Microorganisms, Combustion & Flame, Sound), with answer keys
- **Two drill sheets:** CBSE assertion–reason + case-based, and GSEB 40 rapid-fire objective questions
- **Parent Handbook** (policies with blanks to fill + acknowledgement page), **year-round parent message calendar**, and a **tough-conversations playbook** (16 difficult situations, with replies)
- **90-day board revision plan** (9 Nov 2026 – 7 Feb 2027) with an error-log page, plus 11 parent WhatsApp messages to go with it
- **Admissions kit 2027-28:** broadcasts, posters, Instagram captions, enquiry replies, demo-class plan, referral and testimonial messages
- **3 YouTube video scripts** (balancing equations, 3-mark answers, 90-day plan), with titles, descriptions, tags and Shorts cuts

Just ask: *"send me the Ch 11 test"*, *"Set B of the Ch 4 test"*, *"the 90-day plan PDF"*.

## How to use it from my phone
1. Open the **Claude** app → **Code** → start a session on **Claude-as-me**.
2. Ask for what you need (examples above). Attach photos, Excel files or screenshots if useful.
3. Messages come back in boxes you can copy with one tap. Papers come back as PDFs.

### Use it in normal Claude chats too
`dist/kishan-as-me.zip` packs everything into one skill. Upload it once in **Claude → Settings → Capabilities → Skills** (easiest from a computer browser). After that, any chat can work as me. Rebuild it after changes with `python3 tools/build_app_skill.py`.

## How it gets better
Every time I correct a draft ("too formal", "I never say that"), Claude fixes it **and writes the lesson into `me/`**, so the next session already knows. Say **"interview me"** anytime to fill the gaps in `me/open-questions.md`.

## What's inside
```
CLAUDE.md              how Claude should behave as me (read automatically)
me/
  profile.md           who I am, how I like to work
  voice.md             how I write: tone, phrases, examples, lessons learned
  academy.md           Level Up Academy facts (no student data)
  youtube.md           channel niche pick + first 10 video ideas
  open-questions.md    what Claude still needs to learn about me
.claude/skills/        the six skills above
library/               ready-made tests, notes, mocks, plans, kits, scripts (see library/README.md)
tools/
  make_paper.py        JSON → printable DOCX + PDF (tests, worksheets, notes)
  check_spec.py        accuracy checks: balanced equations, valid MCQ keys
  balance_mcq.py       spreads correct MCQ answers across (a)–(d)
  build_library.py     builds every library PDF + the library index
  marks_report.py      marks list → summary, ranks, tiers, Excel sheet
  build_app_skill.py   packs everything into dist/kishan-as-me.zip
samples/               example specs + rendered PDFs
private/               real student data during a session (never committed)
```

## ⚠️ Privacy
This repo is **public**. No student names, marks, fees or phone numbers are ever committed. All of that stays in `private/` (git-ignored). For extra safety, make the repo private: GitHub → repo **Settings** → **Danger Zone** → **Change visibility** → Private.
