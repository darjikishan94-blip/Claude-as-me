---
name: learn-me
description: Teach Claude-as-me more about Kishan. Run a short interview from me/open-questions.md, learn Kishan's voice from pasted real messages, or save a "remember that…" fact, then update the me/ files and commit. Use when Kishan says "learn about me", "interview me", "remember this", "update my profile", "here are some of my messages", or corrects a draft in a way that should stick.
---

# Learn Kishan

Goal: every session Claude-as-me sounds and decides a bit more like Kishan. Lessons only survive if they are **written to `me/` and committed**.

## Mode 1: Interview ("learn about me", "ask me questions")
1. Read `me/open-questions.md`. Pick the **3–4 highest-value unanswered** questions. Voice and academy facts come first.
2. Ask them in **one** AskUserQuestion call (max 4 questions). Write options that are realistic guesses so Kishan can tap instead of type, and keep each question self-contained.
3. Write the answers into the right file (table below), delete the answered lines from `open-questions.md`, then commit and push.
4. Say what you learned in one line, and offer "4 more?" Never run more than one round unless Kishan says yes.

## Mode 2: Learn from real messages (Kishan pastes chats or screenshots)
1. Remove all names, numbers and personal details **in your head**. Never store the raw messages.
2. Extract the patterns: greeting, sign-off, average length, emoji use, recurring phrases, how Kishan says no, how Kishan says thanks, and the formality with each audience.
3. Update `me/voice.md`: adjust the core rules and register ladder where the evidence is clear, and add dated lines under **Learned from Kishan**. Use short anonymised phrases as examples ("Sure, will do 👍"), never whole messages.
4. Show Kishan a 3-line "here's what I picked up" and commit.

## Mode 3: Quick remember ("remember that…", or a correction while drafting)
- Voice or style lesson → `me/voice.md`, under **Learned from Kishan**, as `- YYYY-MM-DD: lesson (context)`, newest first.
- Academy fact (timing, policy, test day, batch) → `me/academy.md`, replacing the matching `[confirm]`.
- Personal preference → `me/profile.md`.
- A repeatable task that has no skill yet → note it in `me/profile.md` under "Ideas for new skills" and offer to build the skill.
Confirm in one line ("Got it, saved."), then commit and push.

## Where things go
| Kind of fact | File | Public-safe? |
|---|---|---|
| How Kishan writes | `me/voice.md` | Yes, as patterns only |
| Academy timings, policies, classes, syllabus | `me/academy.md` | Yes, nothing about individual students |
| Kishan's preferences and background | `me/profile.md` | Only what Kishan is fine sharing publicly |
| Student names, marks, fees, phone numbers, addresses | **Nowhere in the repo.** Use `private/` (git-ignored) for the session only | No |

## Privacy gate (before every commit)
The repo is **public**. Run `git diff --cached` and confirm:
- no student or parent names, phone numbers, marks, fees or addresses;
- nothing Kishan said was private.
If something sensitive belongs in memory, tell Kishan it can't be stored in a public repo and suggest making the repo private.

## Commit
`git add me/ && git commit -m "learn: <what was learned>" && git push`. Use the current branch and retry the push on network errors.
