---
name: trello-stories
description: Plan a new feature or a change to existing code as Trello stories. Analyse the code repository and the requested feature/change, settle the open points with the user, then cut the change into small implementation stories and create them as Trello cards (simple Spanish card text with Qué/Para quién/Por qué/Criterios de aceptación/Dependencias, story points in the title, acceptance-criteria checklist, blocked-by/blocks card links, and an English tech-notes .md attachment that is the goal prompt for the implementing agent). Use when the user asks to "write the stories on Trello", "crea le storie su Trello", "escribe las historias en Trello", "plan this new feature on Trello", "storie per la nuova feature", "historias para esta modificación", or to plan a new feature or a modification of a repo as Trello cards.
---

# Repo change → Trello stories

Goal: from one repository (or a few) and a description of a **new feature or a change to existing behaviour**
(also refactorings and bug fixes that need several steps), produce the full set of
stories, each small enough for one agent PR, as cards on a Trello board. The output is ONLY Trello cards
(+ their md attachments). Nothing is written to the repo.

**Ask the user whenever something is unclear.** Business rules, scope, cut, numbers, naming: never guess.
Ask with concrete options and a recommendation (use the agent's question tool if it has one, e.g.
AskUserQuestion; batch related questions, max 4 per call). Record every answer as a decision (Phase 3).

Language: talk to the user in their language. **Card text in simple Spanish** (español sencillo: short
sentences, everyday words, no jargon unless it is a technical name). **Tech notes in English.**

## Prerequisites
- `trello` CLI from this repo on PATH (or `$TRELLO_CLI`), with API key + token in the macOS keychain
  (`trello-api-key`, `trello-token`) and a default board (`trello use <board-url>`) or a `board` in stories.json.
  Check with `trello me` and `trello lists`.
- `gh` logged in (to read GitHub repos), `git`, `python3`.
- **All Trello access goes through the `trello` CLI.** If an operation is missing, add it to the CLI; no ad-hoc
  curl in the skill.

## Inputs (ask for what is missing, in this order)
1. **Repository**: GitHub `org/repo` or URL, or a local path. Several repos are fine. Ask which branch is the
   base if it is not the default branch.
2. **What to build or change**: the goal in the user's words — a new feature, or a modification of existing
   behaviour (also refactoring or a bug that needs several steps).
   Ask for links to designs, tickets, docs, examples if they exist.
3. **Board and placement**: board (default from `trello use`), target list (default: first list, usually
   "To Do"), label(s) for this change (existing label, or create one with the user's OK, e.g. one label per
   feature acting as the epic), members to assign (default none).

## Phase 1 – Read everything (no writing yet)
1. Clone each repo into a temporary working folder: `git clone -q --depth 1 <url>` (local path: read in place,
   never modify it).
2. Read `AGENTS.md`, `CLAUDE.md`, `README*`, `CONTRIBUTING*`, build files (package.json, pom.xml, build.gradle,
   pyproject.toml, …), CI config. Note language, framework, test setup, build command, branch/PR conventions.
3. Map the code areas the change touches: modules, entry points, data model/migrations, API, UI screens,
   config, tests. Verify facts in the code; quote file paths, not memory.
4. Check what already exists (half-done work, flags, similar features to copy) so no story repeats done work.
5. Look at the board: `trello cards`, `trello labels` — cards that already cover part of the change, and the
   labels in use.

## Phase 2 – Open points
Write a numbered list of everything the request does not decide or where the code suggests another way
(data model, UX, edge cases, error handling, migrations, compatibility, feature flag yes/no, rollout). For each:
options + your recommendation + why. Ask the user. If the user cannot decide now, keep the point open,
mark it in the plan and continue with the rest. Never fill a gap silently.

## Phase 3 – Decisions record
Keep the agreed points in `decisions.md` next to `stories.json` and update it on every new decision. The same
points go into the "Business rules (agreed)" section of the common tech notes. If a decision changes after the
cards exist, update ALL affected cards and attachments (review mode).

## Phase 4 – Story cut (show the plan, get an OK)
Cut by repo and by deliverable, small enough for one agent PR (1–3 points; 5 only with a reason). Usual set
(adapt, ask when unsure):
- `Preparación: …` – enablers (config, flag, dependencies, accounts, data).
- `<repo>: <qué>` – one story per deliverable in each repo (data model, API, screen, job, …).
- `<Nombre corto>: Documentación`, `<Nombre corto>: Publicación` (release/deploy) if they apply.
- Bugs or prerequisites found on the way: own story (ask whether it belongs to this change).
Present a table to the user: Sxx | title | repo | points | blocked by | blocks | goal parts covered.
**Every story has its dependencies in both directions** ("blocked by" and "blocks"); only the first stories
have no blocker and only the last ones block nothing. Check the graph has no cycles and no isolated story
unless the user agrees. Every part of the requested change must be covered by at least one story; list
uncovered parts explicitly. Wait for OK before Phase 5.

Titles: Spanish, short, form `<repo>: …`, `Preparación: …`, `<Nombre corto>: …`. Points go in `stories.json`,
the script puts them in the title as `[3] …`.

## Phase 5 – Write the stories
For every story write two files in the working folder, following the templates exactly:
- Card description (simple Spanish, Trello Markdown): `references/story-description-template.md`.
  Acceptance criteria go ONLY in `stories.json` (`ac`): the script renders them in the description
  (`{{AC}}`) and as the checklist "Criterios de aceptación".
- Tech notes = **goal prompt for the implementing agent** (English Markdown):
  `references/tech-notes-template.md`. The story part starts with `## Goal` + "Done when" (the story's
  acceptance criteria, in English and verifiable, plus tests/build/PR); the script adds the header, the fixed
  "How to work" block (`references/agent-workflow.md`) and the "Common context" block (same for all stories,
  one file). The file must be self-contained: an agent with only this file and repo access can finish the story.

Then write `stories.json` (format in the `scripts/create_stories.py` docstring).

## Phase 6 – Create on Trello
1. `python3 <this skill's folder>/scripts/create_stories.py stories.json` → dry run: shows every card, checklist,
   attachment and link, and renders all files into `rendered/`. Show the summary (and one rendered card) to the
   user and get an explicit OK.
2. `… --apply`. The script is resumable (state file next to stories.json): a rerun never duplicates.
3. Verify: `trello show <card>` on 2 cards (title with points, description, checklist, md attachment, links in
   both directions), `trello cards --label "<label>"` lists exactly the planned cards.

## Phase 7 – Report
Report to the user (in their language): table of created cards (number, URL, title, points, blocked by), open
points left, where `decisions.md` and `rendered/` are.

## Review mode (cards already exist)
Same phases, but the cards exist. Read them with `trello show <card> --json`. Rewrite only the cards the user
names; before rewriting a card that is in progress, check its comments and the repo for branches/PRs so no
running work is overwritten. In `stories.json` give each existing story its `card` (number, shortLink or URL):
the script updates title, points, description, checklist (replaced) and attachment (replaced by name), and adds
missing links. New stories (no `card`) in the same file get created.

## Conventions
- Card title: `[<points>] <Spanish title>`.
- Description sections (bold headings): **Qué**, **Para quién**, **Por qué**, **Criterios de aceptación**,
  **Dependencias** (`Bloqueada por:` / `Bloquea:` with card URLs — Trello renders them as card previews),
  **Detalles técnicos**, **Referencias**.
- Checklist "Criterios de aceptación", one item per criterion (same text as in the description).
- Dependencies: Trello has no "blocks" link type → written in the description of both cards AND attached as
  card links on both cards.
- Attachment: `<project>_<Sxx>_<slug>_tech-notes.md`, one per story, English.
- Labels: the change's label on every card (ask). No members unless the user asks.
- Never write to Trello without the user's OK on the concrete content.
