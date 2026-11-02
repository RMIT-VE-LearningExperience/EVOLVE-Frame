# Decision: Discrepancy review pack for Chris

- Date: 2026-11-02
- Task/issue: `collaboration/tasks/2026-11-chris-discrepancy-review.md`
- Base commit: 4aa9a31908ee6d9ab89d70c9b5decc977893eedb
- Risk tier: low (documentation only)
- Codex branch/commit: not yet run
- Claude branch/commit: `claude/discrepancies-chris-teacher-4annp0`, this commit
- Integration commit: pending

## Context

Two logs hold unresolved drawing conflicts and model errors for the Leichhardt project: the Blender frame audit (A01 to A10 plus notes) and the Revit discrepancy log (D01 to D06, R01 to R03, C01). The transfer handoff adds the steel portal axis and foundations. Chris, the teacher, is the reviewer of record. Nothing can be corrected until he rules on each item. The task is to give him one pack with a decision field per item.

This run is a bootstrap. Claude Code performed its blind pass in a cloud session under direct user instruction. Codex has not yet been installed; its blind pass is to be run on the user's PC from the same base commit without sight of this report, then relayed per `collaboration/README.md` section 4.

## Options considered

1. One markdown pack under `output/`, grouped by the kind of decision Chris must make. Chosen for the blind pass.
2. Annotate the two existing logs in place with a Decision column. Rejected for the first pass: the two logs use different formats and Chris would work across three files.
3. A spreadsheet or shared document. Deferred to Chris's preference, recorded as a known unknown in the contract.

## Claude position and evidence

### 1. Recommendation

Produce `output/CHRIS_REVIEW_PACK.md` with six parts: drawing conflicts where Chris picks a source, the single setout-basis question, confirmed model errors awaiting approval, room setout mismatches gated on the basis answer, missing detail where Chris supplies information, and items already closed by measurement. Each open row carries an empty Decision cell. Answers are copied back into the source log before any correction is contracted.

### 2. Repository evidence

- `output/timber_frame/audit/POSITION_AUDIT.md` table rows A01 to A10, the stair surround section, the room-dimension table, the "further detailing" list and the "checks that match" list. Measured values confirmed against `position_audit.json` (`other_measurements`: 76.7 mm dwarf-return gap, named members ST2/HC1/1L8/1L9 not found, garage roof chord bottom 2654 vs wall top 2740).
- `output/revit/DISCREPANCY_LOG.md` rows D01 to D06, R01 to R03, C01, and `GEOMETRY_PROGRESS.md` "Preserved conflicts" confirming D01 to D06 are still open at the last Revit save.
- `TRANSFER_HANDOFF.md`: portal axis X12733 vs X12714.5; founding depths unknown.
- `output/README.md` (Blender basis): porch at -226, studs 90x35, floor zone 400, overhang 550.
- `output/enclosure/ENCLOSURE_NOTES.md` and `student-web/lib/hotspots.ts`: confirm which items the enclosure study and the site are holding for Chris.

### 3. Assumptions

- Chris is content to work in a markdown table. If he prefers a spreadsheet, the same rows convert directly.
- The Revit log's R02 reasoning (8080 + 2 x 450 equals 7880 + 2 x 550) is arithmetically sound, so item 7 is presented as "confirm closed" rather than open.
- Sheet numbers quoted in the two logs are correct; I did not re-open the PDFs for this pass.

### 4. Risks and edge cases

- Three cross-model disagreements were not in either log and are new rows: porch 172 (Revit) vs 226 (Blender); studs 90x45 (Revit notes) vs 90x35 (Blender notes); foundations unmodelled with unknown depths. If my reading of the two READMEs is wrong, those rows mislead Chris. Confidence on each is given below.
- The pack repeats numbers from the logs. If a log is later corrected, the pack goes stale. The "How answers are recorded" section makes the logs the system of record and the pack a view.
- A reader could mistake Part 3 "confirmed model errors" for permission to edit. The pack and the contract both say no model changes on the strength of the pack.

### 5. Test plan

Documentation only. Verified: `npx tsc --noEmit` and the 13 unit tests from `student-web/` still pass, proving no site file changed; all relative links in the pack and the README resolve; no wording describes the model as approved, coordinated or fabrication-ready (grep for those words in the new files).

### 6. Uncertainties

- Whether item 7 (overhang) should be presented as closed. The Blender audit's author chose to leave it listed. I kept it in Part 1 as "confirm closed".
- The stud-section disagreement (item 8) may be a documentation inconsistency rather than a modelling one. I have not opened either binary to check.
- Whether Chris wants Part 4's small residuals shown at all. They are included so nothing is silently dropped.

### 7. Confidence

0.86 on the pack as a faithful consolidation of the existing logs. 0.70 on the three new cross-model rows (items 4 Blender side, 8 and 17), because they rest on prose in two READMEs rather than measured geometry.

### 8. Escalation required

No. No dimension was changed, no discrepancy was resolved, and the contract's two task-specific triggers did not fire. The three new rows are flagged for Codex's cross-review rather than escalated, since they add questions for Chris and do not answer any.

## Codex position and evidence

Not yet run. To be completed from Codex's blind pass on the user's PC. Do not paste the Claude report above into Codex's inbox until Codex has produced its own.

## Disagreements

Pending Codex's report.

## Decisive tests or documentation

The two logs and the handoff are the ground truth for this task. A row is correct if it cites a line in one of them. Codex's cross-review should check every row against its cited source and flag any number or sheet reference that does not trace.

## Decision

Pending. The pack is a draft until Codex's blind pass and cross-review are complete and the user approves.

## User input or override

- 2026-11-01: user approved lifting the project `git push` deny rule once to publish the scaffold commit. Recorded in PR #1.
- 2026-11-02: user directed Claude to run its blind pass in the cloud session now and Codex later on the PC ("go"). This departs from simultaneous blind passes; independence is preserved as long as Codex does not see this report first.

## Consequences and residual risks

Chris gets one document to work through. The two logs remain the system of record. Risk: the pack ages if the logs change before Chris answers.

## Verification performed

See section 5 above. Results recorded in the commit message.

## Follow-up work

- Run Codex blind pass, relay, one debate round, Codex cross-review of this diff.
- Fill the Codex, Disagreements and Decision sections above.
- After Chris answers: contract the correction tasks, one chain at a time, per the audit's correction sequence.
