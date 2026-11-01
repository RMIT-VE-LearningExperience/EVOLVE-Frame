# Task contract: <title>

Copy to `collaboration/tasks/<yyyy-mm>-<slug>.md`, fill in every section, then copy or symlink it to `collaboration/TASK.md` for the active run. Agents read `collaboration/TASK.md`.

- Date:
- GitHub issue:
- Base branch: `main`
- Base commit (exact SHA):
- Risk tier: low | medium | high
- Implementation pattern: competing | lead + reviewer
- Lead (if lead + reviewer): Codex | Claude

## Objective

## Non-goals

## Acceptance criteria

- [ ]
- [ ]

## Required tests and checks

From `student-web/`: `npx tsc --noEmit`, `node --experimental-strip-types --test lib/*.test.ts`, `npm run build`, `npm run lint` (no new errors). Add task-specific checks here.

## Files and systems in scope

## Prohibited actions

- Pushing, merging, deploying, publishing, contacting external systems, reading secrets.
- Editing `.blend`, `.rvt`, `.rfa` or the source PDFs unless listed above.
- Resolving a drawing discrepancy without recording it and flagging it for Chris.

## Decisions already made by the user

## Known unknowns

## Escalation triggers specific to this task
