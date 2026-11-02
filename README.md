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
tools/
  make_paper.py        JSON → printable DOCX + PDF (tests, worksheets, notes)
  marks_report.py      marks list → summary, ranks, tiers, Excel sheet
  build_app_skill.py   packs everything into dist/kishan-as-me.zip
samples/               example specs + rendered PDFs
private/               real student data during a session (never committed)
```

## ⚠️ Privacy
This repo is **public**. No student names, marks, fees or phone numbers are ever committed. All of that stays in `private/` (git-ignored). For extra safety, make the repo private: GitHub → repo **Settings** → **Danger Zone** → **Change visibility** → Private.
