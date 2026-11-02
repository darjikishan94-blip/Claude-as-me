---
name: parent-messages
description: Draft Level Up Academy's WhatsApp messages to parents and prospective parents, other than fee messages. Covers holiday/no-class notices, timetable changes, extra classes, test announcements, PTM invites, absence check-ins, progress concerns, appreciation, welcome messages, admission enquiry replies and follow-ups, new batch announcements, festival wishes and exam good-luck. Use for any "message to parents", "notice", "announcement", "enquiry reply" or "tell parents that…". Fee reminders and payment confirmations use the parent-fee-messages skill instead.
---

# Parent messages (non-fee)

Read `me/voice.md` (the register ladder) and `me/academy.md` (classes, groups, policies) first. For seasonal and routine messages (new session, rain closures, Navratri, Diwali, Uttarayan, PTM, re-enrolment…), start from `library/admin/parent-message-calendar.md`. For difficult one-to-one situations, use `library/admin/tough-conversations-playbook.md`. Fee messages go to the **parent-fee-messages** skill. Test result messages are drafted best through the **test-results** skill, which works from the marks.

## Steps
1. **Choose the type and audience:** a class group (notice), one parent (about one child), or a prospective parent (enquiry).
2. **Collect the facts:** class, dates, times, chapters. If one is missing and can't be found in `me/academy.md`, ask or leave `[blank]`. Never guess.
3. **Verify every date's weekday** before writing "Saturday, 8 Nov": `python3 -c "import datetime;print(datetime.date(2026,11,8).strftime('%A'))"`
4. **Fill the template** below, then adjust tone for the group (see Group tone).
5. **Check against the Rules**, then present.

## Rules
- **Group messages never name a student and never show marks or amounts.** Every parent reads them.
- Anything about one child (absence, marks, behaviour, a concern) goes **one-to-one only**.
- Never compare a child with other students in a message to their parent.
- No pressure words ("strictly", "compulsory", "immediately", "failing which") unless Kishan asks.
- Write dates as `Sat, 8 Nov` or `Saturday, 8 November` and times as `5:30 PM`. Use one format per message.
- Keep it short: notices in 2–5 lines, one-to-one messages in 3–6.

## Group tone
| Group | Adjust |
|---|---|
| 9th Foundation | Open with "Respected Parents," and close with "Thank you." No emoji. Soft asks ("Kindly…"). Nothing that sounds like pressure. |
| 8th Science group | It's science-only, so say "class" or "test", not "science class". |
| Everyone else | Warm and casual, as in the templates (at most one emoji). |

## Templates
Fill the `[brackets]`. Wording can flex to sound natural, but keep the order of information.

**1. Holiday / no class** (group)
```
Hello Parents,
There will be no class on [day, date] for [reason, e.g. Diwali]. Regular classes resume on [day, date].
[Optional: Wishing you all a very happy Diwali! 🪔]
Thank you!
```

**2. Timetable change / extra class** (group)
```
Hello Parents,
Quick update: [Class X]'s class on [day, date] will be at [new time] instead of [old time].
[Or: We're keeping an extra class on [day, date] at [time] to complete [chapter/revision].]
Thank you!
```

**3. Test announcement** (group; can go to the students' group too)
```
Hello Parents,
[Class X] will have a test on [day, date] at [time].
Chapters: [list]
Marks: [n] | Duration: [time]
Please encourage them to revise the [diagrams / numericals / definitions] 🙂
Thank you!
```

**4. PTM invite** (group), then a one-to-one slot confirmation
```
Hello Parents,
We're holding a short parent-teacher meeting for [Class X] on [day, date], [time window].
It's a good chance to talk about your child's progress and the plan for [exams/term].
Please reply with a time that suits you. Thank you!
```
```
Hi! Your slot is confirmed for [day, date] at [time]. See you then 🙂
```

**5. Absence check-in** (one-to-one)
```
Hi! Hope everything is okay. [Name] wasn't in class [today / on date].
We covered [topic]. I'll share the notes so [he/she] can catch up.
```
After 2+ absences in a row, add: "Do let me know if there's anything I should be aware of."

**6. Progress concern** (one-to-one): positive → one specific issue → plan → partnership
```
Hi! Hope you're doing well.
[Name] has been [genuine positive: regular / attentive / asking good questions] 🙂
I've noticed [one specific issue: homework incomplete / losing marks in numericals / distracted lately].
Plan: [what you'll do] + [what would help at home, one small thing].
Happy to talk anytime.
```

**7. Appreciation** (one-to-one). Send these often; parents love them.
```
Hi! Just wanted to share a proud moment 😊
[Name] [specific achievement: scored 24/25 / solved a tough question in class / improved a lot in diagrams].
Please do tell [him/her] we noticed!
```

**8. Welcome a new student** (one-to-one)
```
Hi! Welcome to Level Up Academy 🙂
[Name]'s classes start on [day, date] at [time].
Please bring [notebook / textbook / anything else].
I'll add you to the [Class X] parents' group for updates. Feel free to message me anytime.
```

**9. Admission enquiry reply** (prospective parent). Use only facts from `me/academy.md`.
```
Hi! Thanks for reaching out to Level Up Academy 🙂
Yes, we have batches for [Class X, Board] [Science/…].
[Timings: … | Location: …]
[One reason to join: small batches / regular tests / personal attention, whichever is true]
You're welcome to visit [or: bring [child] for a demo class]. When would suit you?
```
Fees in the first reply: only if `me/academy.md` says it's OK. Otherwise: "Happy to share the fee details when we talk, or when you visit."

**10. Enquiry follow-up** (2–3 days later, once only)
```
Hi! Just following up on [child]'s admission for [Class X].
Do let me know if you have any questions. Happy to help 🙂
```

**11. New batch / admissions open** (broadcast, status or public post)
```
📚 Admissions open at Level Up Academy!
[Class X–Y] | [CBSE & GSEB] | [Subjects]
✅ [true benefit 1]  ✅ [true benefit 2]  ✅ [true benefit 3]
Batch starts: [date]
Message us to book a demo class: [contact]
```

**12. Festival wishes** (group)
```
Hello Parents,
Wishing you and your family a very happy [festival]! [one warm line] 🪔
[Holiday info, if any]
```

**13. Exam good-luck** (group)
```
Hello Parents,
[Board / term] exams start [day, date]. The students have worked really hard 💪
A good night's sleep and a calm morning will help more than last-minute studying.
All the best to every one of them!
```

**14. Reply to a complaint** (one-to-one). Use the holding pattern from `reply-as-me`: thank → acknowledge → action + time → offer a call. Flag it for Kishan under "Check before sending".

## Present
- **Ready to send:** one code block per message, labelled with audience (e.g. `9th Foundation group` or `Parent of [first name], Class 8`).
- **Check before sending:** complaints, concerns, anything with a `[blank]`, and any fact you weren't sure of.
