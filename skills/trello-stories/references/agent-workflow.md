## How to work (mandatory)
1. Read this whole file first, then the repo's `AGENTS.md` / `CLAUDE.md` / `README` / `CONTRIBUTING`, and follow
   them. On a conflict this file wins for the business rules, the repo files win for conventions (build, style,
   versioning).
2. Default branch: `gh repo view <org>/<repo> --json defaultBranchRef` (or `git remote show origin`). Branch
   `feature/{{SHORTLINK}}-<short-slug>` from it; the PR targets it. Never base the work on another feature branch
   unless the developer tells you so.
3. Implement only the scope of this story. Work that belongs to another story (see "Blocked by" / "Blocks") stays
   out; if this story cannot be done without it, stop and report.
4. Write the tests of the "Tests" section plus anything the "Done when" list needs. Run the full build and test
   suite locally; it must be green.
5. Commit messages and PR title: short, imperative, in English, describing what changed. No AI/assistant
   attribution in commits or PR. PR description: what changed and why, how it was tested, and the Trello card
   {{URL}}.
6. **If anything is unclear, contradicts the code, or a business rule is missing: do not guess.** Stop, write the
   question (with the options you see and your recommendation) to the developer, and continue only with the answer.
7. Final report to the developer: PR link, what was done per "Done when" item, tests run, open points. If the
   `trello` CLI is available, also comment the PR link on the card: `trello comment {{SHORTLINK}} "PR: <url>"`.
