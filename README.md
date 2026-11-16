# trello-cli

Minimal Trello CLI (Python 3 stdlib only) to use a Trello board Jira-style.

## Setup

```bash
# credentials (API key from https://trello.com/power-ups/admin → app → Autorizzazione Trello)
security add-generic-password -U -a trello -s trello-api-key -w
security add-generic-password -U -a trello -s trello-token -w
ln -sf ~/Projects/trello-cli/trello ~/.local/bin/trello
trello use https://trello.com/b/<shortLink>/<board-name>   # default board
```

Override board per call with `--board <shortLink|id|URL>` or env `TRELLO_BOARD`.

## Story convention

| Jira            | Trello                                         |
|-----------------|------------------------------------------------|
| story points    | title prefix `[3] Title` (`--points`)          |
| description     | card description (Markdown)                    |
| acceptance crit.| checklist `Acceptance Criteria` (`--ac`)       |
| type / epic     | labels                                         |
| status          | lists                                          |
| link / blocks   | card-link attachment (`--link`, `--both-ways`) |

Cards are referenced by board number (`7` / `#7`), shortLink, id or URL.
Lists, labels and members match case-insensitive, unique substring OK.

## Commands

```bash
trello me | boards | lists | labels | members      # --json available
trello cards [--list Doing] [--label "Feature"] [--mine] [--archived]
trello show 7
trello search "sponsor"
trello create "Title" --points 3 --desc-file story.md --label "Feature" \
    --ac "criterion 1" --ac "criterion 2" --member me --due 2026-12-01 \
    --attach tech-notes.md --link 4 --both-ways [--list "To Do"] [--json]
trello update 7 [--title ..] [--points 5] [--desc-file f.md] [--add-label X] \
    [--remove-label X] [--add-member me] [--ac "extra criterion"] [--due ""]
trello move 7 Doing
trello comment 7 "text"            # or --file f.md / --file -
trello checklist 7 "Tasks" a b c [--replace]
trello check 7 "criterion 1"       # substring or 1-based index; --undo
trello attach 7 file.pdf|https://… [--replace]   # URLs are attached once
trello link 7 4 [--both-ways]
trello label-create "Bug" --color red
trello list-create "Ready" --after "To Do"
trello archive 7 [--undo]
```

`create` / `update` accept `--json` (prints `id`, `idShort`, `shortLink`, `shortUrl`, `name`) for scripting.

## Skill: trello-stories

`skills/trello-stories/` is an agent skill (Claude Code `SKILL.md` format) that turns a requested change of
a repository into Trello story cards:

1. asks for the repo(s), what should change, the board/list/label;
2. reads the repo (AGENTS.md, README, build, code areas), lists open points and asks;
3. proposes the story cut (points, blocked by / blocks) and waits for an OK;
4. writes each card in **simple Spanish** (Qué / Para quién / Por qué / Criterios de aceptación /
   Dependencias) plus an **English tech-notes `.md`** attachment that is the goal prompt for the
   implementing agent;
5. creates everything with `scripts/create_stories.py stories.json` (dry run, then `--apply`; resumable,
   review mode for existing cards).

Install for Claude Code:

```bash
ln -sfn ~/Projects/trello-cli/skills/trello-stories ~/.claude/skills/trello-stories
```
