@AGENTS.md

## Claude Code-specific notes

- Use plan mode (`--permission-mode plan`) for blind analysis and cross-review phases.
- Project permissions are in `.claude/settings.json`. Do not run with `--dangerously-skip-permissions` on a host machine.
- When the task touches the student website, run checks from `student-web/`, not the repository root.
- Scratch and relay files belong in `.collab-runtime/` (ignored), never in the project tree.
