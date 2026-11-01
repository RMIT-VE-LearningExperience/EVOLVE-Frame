# 0001: Adopt the Claude Code + Codex collaborative agent workflow

- Date: 2026-11-01
- Status: accepted
- Base commit: 4aa9a31908ee6d9ab89d70c9b5decc977893eedb

## Context

The repository carries a Blender teaching model, a Revit coordination model and a public student website for the Leichhardt project. Dozens of unresolved drawing discrepancies are held for the teacher's review. Work has been done by single agents in long sessions, with the risk that one agent silently resolves a conflict or overstates what is coordinated.

The user supplied a workflow in which two independent agents form blind opinions, debate through a bounded relay, cross-review committed diffs, and hand the merge decision to a human.

## Decision

Adopt that workflow. Add the repository layout from its Section 6: `AGENTS.md` as the shared contract with `CLAUDE.md` importing it, `.codex/config.toml`, `.claude/settings.json`, CODEOWNERS, a PR template, a CI workflow, `collaboration/` templates, prompts and policy, and this `docs/decisions/` directory.

Project-specific additions to the contract: the drawing source hierarchy is binding, discrepancies are recorded and flagged for Chris rather than resolved, PDFs are not distributed through the site, model binaries and generated exports are not hand-edited, and nothing is described as approved or fabrication-ready.

## Checks

Verified on the base commit with Node 22:

| Check | Result |
|---|---|
| `npx tsc --noEmit` | pass |
| `node --experimental-strip-types --test lib/*.test.ts` | 13 pass, 0 fail |
| `npm run build` | pass, static export in `dist/client` |
| `npm run lint` | 5 pre-existing errors |

The lint errors are in generated shadcn files: `hooks/use-mobile.ts` (setState in effect), `components/ui/item.tsx` (role list) and three `restrict-template-expressions` errors in `components/ui/chart.tsx`. The lint job is therefore advisory in CI and must not be suppressed. Fixing those five errors and promoting lint to a required check is follow-up work.

`npm ci` failed on the base commit because `package-lock.json` was missing the optional `@emnapi/core` and `@emnapi/runtime` entries. The lockfile was regenerated with `npm install`; no dependency versions changed.

## Consequences

- Agents gain a written authority boundary and a repeatable protocol, at the cost of more ceremony per task.
- Branch protection on `main` must be configured in GitHub settings by the owner; files in the repository cannot enforce it.
- Permission patterns in `.claude/settings.json` are not an operating-system boundary. They should be paired with isolated worktrees and tokens that cannot merge.
- The `.codex/config.toml` is loaded only when the project is trusted in Codex.

## Follow-up

- Fix the five lint errors and make lint a required check.
- Configure the `main` branch ruleset listed in `collaboration/README.md`.
- Run the first contract, `collaboration/tasks/2026-11-chris-discrepancy-review.md`, as a documentation-only task.
