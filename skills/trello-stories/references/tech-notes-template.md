# Tech-notes template = goal prompt (English Markdown, given as-is to the implementing agent)

The attachment is the agent's goal prompt. The script builds it as:
header + story part (starts with Goal) + fixed "How to work" block (`agent-workflow.md`) + common part + extra sections.
It must be self-contained: an agent with only this file and repo access can finish the story.

## 1. Story part (one file per story, `notes`, MUST start with `## Goal`)

```markdown
## Goal
Implement <one sentence: what, in which repo> so that <user/business effect>.

Done when:
- <each acceptance criterion of the card, in English and verifiable, e.g. "POST /api/matches/{id}/payment
  returns 409 when the match is already paid">
- Tests for every item above exist and the build is green.
- A PR is open against the default branch of `<org>/<repo>`, linked to the Trello card.

## Story: <short English title>

### Scope
- <exact changes: files/classes/components to add or change, dependency coordinates, config keys with values,
  JSON/YAML snippets, endpoints with paths, DB migrations, screens and texts>
- Behaviour details, edge cases, error handling for this story.

### Pattern
- `<repo>/<path>/<File>` (existing code to copy or follow, and what to copy).

### Tests
- <unit/integration/UI tests to write, edge cases, idempotency, error paths>
```

The script prepends:
```markdown
# <title> (Trello <shortUrl>)

Blocked by: <url a> (<title a>), <url b> (<title b>)      ← {{BLOCKED_BY_LINE}}, omitted if none
Blocks: <url c> (<title c>)                                ← {{BLOCKS_LINE}}, omitted if none
```

## 2. Common part (ONE file for the whole change, `common_notes`)

```markdown
## Common context (read first)

- Change: "<name of the change>", Trello label `<label>` on board <board url>.
- Goal: <2-3 lines, user/business goal>
- Repos: `<org>/<repo>` (<role, stack>). Read the repo's `AGENTS.md` / `README` first and follow it.
- Build and test: `<exact commands>`.
- <Reference implementation / similar feature in the code, if any: copy it wherever possible.>

### Business rules (agreed)
- <every decision from Phase 2/3, precise: values, formats, time zone, rounding, edge cases, texts>

### Path abbreviations
- `<ABBR>` = `<repo>/<path>/...`

### General definition of done
- Tests for the new behaviour; existing tests stay green; build green.
- No change of unrelated behaviour.
- Version bump / changelog according to the repo conventions; PR against the default branch.
```

If the user wants a feature flag, add a `### Feature flag (mandatory)` section: name, where it is configured,
"every new behaviour must be off when the flag is off", tests with flag on AND off.

## 3. Extra sections (optional, `extra_notes`)
Decision-specific sections that apply to some stories only, ending with
`- This story: <what this story must do about it>.`
