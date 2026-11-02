# Task contract: Discrepancy review pack for Chris

- Date: 2026-11-01
- GitHub issue: (none yet)
- Base branch: `main`
- Base commit (exact SHA): 4aa9a31908ee6d9ab89d70c9b5decc977893eedb
- Risk tier: low (documentation only)
- Implementation pattern: lead + reviewer
- Lead: to be chosen after the blind pass

## Objective

Produce one consolidated review pack that Chris (the teacher) can work through, with a decision field per item, from the two existing logs: `output/timber_frame/audit/POSITION_AUDIT.md` (Blender frame, items A01 to A10 plus notes) and `output/revit/DISCREPANCY_LOG.md` (Revit, items D01 to D06, R01 to R03, C01), plus the steel portal note in `TRANSFER_HANDOFF.md`. Record Chris's answers back into those logs when they arrive.

## Non-goals

- Resolving any discrepancy. Agents prepare questions; Chris answers them.
- Editing `.blend`, `.rvt`, `.rfa`, the source PDFs, or anything under `student-web/`.
- Changing the model exports or the public site.

## Acceptance criteria

- [ ] A single markdown file under `output/` lists every open item below once, with ID, sources, the model's current position, the question for Chris and an empty decision field.
- [ ] Every item traces to a line in `POSITION_AUDIT.md`, `DISCREPANCY_LOG.md` or `TRANSFER_HANDOFF.md`. No new discrepancies are introduced without a drawing citation.
- [ ] The pack states which items are gated on the dimension-basis question (timber face, lining or finished face).
- [ ] `README.md` links the pack beside the existing audit link.
- [ ] No wording describes the model, frame or site as approved, coordinated or fabrication-ready.

## Required tests and checks

Documentation only. Run `npx tsc --noEmit` and the unit tests from `student-web/` to prove nothing under the site changed. Markdown links must resolve (check with a relative-link pass).

## Files and systems in scope

- New: `output/CHRIS_REVIEW_PACK.md` (name may be changed by agreement)
- Edit: `README.md` (one link)
- Read only: the two logs, `TRANSFER_HANDOFF.md`, `output/enclosure/ENCLOSURE_NOTES.md`, `output/learning/LEARNING_GUIDE.md`

## Prohibited actions

- Pushing, merging, deploying, publishing, contacting external systems, reading secrets.
- Moving, resizing or re-labelling any audited member.
- Marking any item resolved.

## Decisions already made by the user

- The consolidated list below is the starting inventory. Items 1 to 7 need Chris to pick a source. The setout basis question gates the room-width items.

### Drawing conflicts, Chris picks a source

| # | Item | Sources disagree | Model now |
|---|---|---|---|
| 1 | First-floor zone (A09, D01) | Arch A12 400 mm. Eng S10 300-deep joists. Supplier 413 typical, 442 built up, 360 at showers | Blender 400. Revit keeps arch levels with supplier joists, 42 mm ceiling clash shown |
| 2 | Stair run (D05, audit) | Arch A07 3190. Arch A08 4000 | Blender follows 4000. Revit stair not built |
| 3 | Upper windows W14/W15/W17/W19 (D04) | A08 plan 2300. A11 schedule 2230 | Revit 2230 |
| 4 | Porch step (D02) | RLs differ by 172 mm. Label says 226 mm | Revit uses written RL |
| 5 | Wind classification (D03) | Eng S18/S19 N1. Suppliers N2. S09/S11 require engineer validation of truss layout | Shown as supplied, not treated as coordinated |
| 6 | Portal steel axis (handoff) | S09 calibrated about X12733. Supplier chain X12714.5 | 19 mm unresolved |
| 7 | Roof overhang (R02, audit) | A12 450. Supplier 550 | Revit log treats as resolved by 100 mm cladding. Blender audit still flags. Confirm |

### Setout basis question

Are architectural room dimensions to timber face, lining or finished face? Gates the room-width items.

### Confirmed model errors, Chris approves the fix

| ID | Item | Model | Drawing | Diff mm |
|---|---|---|---|---|
| A01 | W04 kitchen sill height | 1419 | 905 | +514 |
| A07 | Garage wall base vs garage slab | 0 | -86 | +86 |
| A08a | T5 bottom chord overall length | 6150 | 6680 | -530 |
| A08b | T6 bottom chord overall length | 950 | 1395 | -445 |
| A10 | Study-side D bracing bay | 2604 | 2400 | +204 |
| D06 | Garage truss top vs parapet top | +3641 | +3514 | truss above parapet |
| stair | Dwarf-wall return to floor trimmer | 76.7 mm gap | 0 | coordination defect |

### Room setout mismatches, depend on the basis answer

| ID | Item | Model | Drawing | Diff mm |
|---|---|---|---|---|
| A02a | Garage clear X | 6141.7 | 6000 | +141.7 |
| A02b | Garage clear Y | 6723.5 | 6500 | +223.5 |
| A03 | GF walk-in robe width | 2513.9 | 2270 | +243.9 |
| A04 | Upper Bath 2 width | 2093.5 | 2200 | -106.5 |
| A05a | Stair side-wall zone | 1167.9 | 1100 | +67.9 |
| A05b | Void width to entry wall | 2360.8 | 2550 | -189.2 |

Bed 1, Bed 4, Bed 5 and Bed 2 residuals of 34 to 87 mm are probably tracing noise, same basis question.

### Gaps needing detail, not a guessed move

- Alfresco corner D05: headers about 4140 and 3595 mm, schedule 3600 and 3000 by 2100. Model header underside 2280.
- Bracing: S19 C2700 bay on Bed 4 robe partition missing in model. S18 two D1800 bays on ensuite wall where model has one long cross.
- Steel/LVL ST2, HC1, 1L8, 1L9 not found as named members.
- Special hip trusses, wet-area 360 mm members, theatre platform 420 mm step all schematic.
- Deferred until items 1, 2 and the garage datum are ruled: garage and porch roof coverings, full floor sheeting, D05 glazing, Revit stair.

## Known unknowns

- Whether Chris wants the pack as markdown in the repo, a printed table, or a shared document.
- Whether item 7 is genuinely closed by the cladding measurement basis.

## Escalation triggers specific to this task

- Any agent proposes changing a model dimension.
- The two agents disagree on whether an item is a drawing conflict or a model error.
