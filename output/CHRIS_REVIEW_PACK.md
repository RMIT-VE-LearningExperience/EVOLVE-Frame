# Leichhardt discrepancy review pack for Chris

Prepared 2 November 2026 from the two existing logs and the transfer handoff. Nothing here has been resolved; every item needs a decision from Chris before the frame, the Revit model or the student website is corrected. Fill the **Decision** column and date it. Agents then record the answer back into the source log named in each row and only then change a model.

Sources: `timber_frame/audit/POSITION_AUDIT.md` (items A01 to A10 and notes, Blender frame), `revit/DISCREPANCY_LOG.md` (items D01 to D06, R01 to R03, C01, Revit coordination model), `../TRANSFER_HANDOFF.md` (steel portal axis, foundations), `README.md` in this folder (Blender basis). Drawing references use the sheet numbers printed on the Leichhardt architectural (A), engineering (S) and supplier PDFs. Dimensions are millimetres. Model minus drawing is positive when the model is larger.

The Blender frame and the Revit model were built at different times from the same PDFs. Where they disagree with each other, the row says so.

## Part 1. Drawing conflicts: Chris picks which source governs

These cannot be fixed by measurement. Two documents say different things.

| # | Item | What disagrees | Where each model sits now | Question for Chris | Decision |
|---|---|---|---|---|---|
| 1 | First-floor zone (A09, D01) | A12 section: 400 zone. S10: 300-deep FJ1 posi-struts "or equivalent". Supplier layout p47 and FJ details: 413 typical, 360 at showers, which with 19 flooring and 10 ceiling is 442 | Blender: 400 straight chords. Revit: architectural levels kept (first FFL +3140, first ceiling +5730) with 413 supplier joists placed, leaving a 42 clash below the A12 ceiling | Does the architectural level set hold and the supplier adapt, or does the building grow 42 and every upper level, stair and roof move with it? | |
| 2 | Stair run (D05, audit) | A07 ground plan: 3190. A08 first-floor plan: 4000 with 1100 width and 2550 void | Blender follows 4000 with 2000 entry-end clearance. Revit stair not built, void present provisionally | Is 3190 the visible flight and 4000 the floor opening, or is one sheet wrong? | |
| 3 | Upper windows W14, W15, W17, W19 (D04) | A08 plan text: 2300 wide. A11 schedule: 2230 | Revit: 2230 from the schedule. Blender: schedule widths | Schedule or plan? Is any rough-opening allowance intended? | |
| 4 | Porch step (D02) | A06/A07 RLs: GF 10.906, porch 10.734, a 172 difference. The same sheet labels the step 226. S02 repeats 10.734 and asks the architect to confirm | Revit: 172 from written RL. Blender: 226 from the label. The two models disagree | Which figure is right, 172 or 226? | |
| 5 | Wind classification and truss validation (D03) | S18/S19 bracing designed for N1. Roof and floor supplier certificates: N2. S09/S11 state the roof framing was designed without the truss layout, which must be presented to the engineer for validation | Both models show the supplied arrangement and do not claim it is coordinated | Has the engineer validated the supplier layouts? Which classification stands? | |
| 6 | Portal steel axis (handoff) | S09 calibrated portal axis about X12733. Supplier dimension chain gives X12714.5 | Revit: 19 unresolved, not treated as exact | Which chain sets the portal? | |
| 7 | Main roof overhang (R02, audit) | A12: 450 from the finished external face. Supplier: 550 tails from the timber envelope | Both models use 550. The Revit log treats this as closed because 8080 + 2 x 450 equals 7880 + 2 x 550. The Blender audit still lists it | Confirm the cladding-basis reading closes this, so the Blender audit can mark it resolved | |
| 8 | Wall stud section (Blender basis vs Revit progress) | Blender notes: general studs 90x35, ground bottom plate 90x35. Revit notes: studs 90x45 at 450 GF and 600 FF following the architectural note | The two models disagree with each other, not necessarily with the drawings | What do S12/S13 specify for stud and plate sections and spacing on each floor? | |

## Part 2. Setout basis: one answer that unlocks Part 3

| # | Question for Chris | Why it matters | Decision |
|---|---|---|---|
| 9 | Are the architectural room dimensions on A07/A08 taken to timber face, to plasterboard lining, or to finished face? | Every room-width residual in Part 3 was measured between timber faces of the 90 mm frame. A lining convention moves each face by 10 to 13, so residuals of 20 to 35 may be nothing. Residuals over 100 are real whichever convention applies. | |

## Part 3. Model errors already confirmed: Chris approves the correction

The drawing is unambiguous. The model is wrong. These wait only for the go-ahead and for Part 1 items that interact with them.

| ID | Item | Model | Drawing | Diff | Source | Proposed correction | Interacts with | Decision |
|---|---|---:|---:|---:|---|---|---|---|
| A01 | W04 kitchen sill height | 1419 | 905 | +514 | A11 | Lower the W04 assembly 514, rebuild cripple studs, check lintel | none | |
| A07 | Garage wall base vs garage slab datum | 0 | -86 | +86 | A07: garage FFL 10.820 vs house 10.906 | Reconcile garage wall base, wall height and roof bearing together | D06 | |
| A08a | T5 bottom chord overall length | 6150 | 6680 | -530 | Truss PDF p20: transport width 6680 | Rebuild T5 with shop end extensions; 6150 is span, not chord extent | A02b, D06 | |
| A08b | T6 bottom chord overall length | 950 | 1395 | -445 | Truss PDF p21: transport width 1395 | Rebuild T6 with 345 and 100 end extensions | item 4 | |
| A10 | Study-side type D bracing bay | 2604 | 2400 | +204 | S19: D2400 | Re-set brace endpoints to the 2400 bay, keep the cross arrangement | item 9 | |
| D06 | Garage T5 top vs parapet top | +3641 | +3514 | truss above parapet | Garage FFL -86 plus 3600 parapet; T5 base +2750 plus 891 | Review vertical datum and support relationship; do not raise the parapet silently | A07, A08a | |
| stair-1 | Dwarf-wall return to floor trimmer | 76.7 gap | 0 | coordination defect | Audit, stair surround section | Correct side dwarf wall, return and trimmers as one assembly | item 2 | |

## Part 4. Room setout mismatches: measured, but gated on item 9

| ID | Item | Model | Drawing | Diff | Source | Proposed correction | Decision |
|---|---|---:|---:|---:|---|---|---|
| A02a | Garage clear X between timber faces | 6141.7 | 6000 | +141.7 | A07 | Re-set from the 6000/90/240 chain, keep the house reference fixed | |
| A02b | Garage clear Y between timber faces | 6723.5 | 6500 | +223.5 | A07: 6500, overall 6980 | Resolve both garage ends with the 1320 projection and 6680 roof overall | |
| A03 | Ground-floor WIR clear width | 2513.9 | 2270 | +243.9 | A07 | Re-set the bedroom/WIR/ensuite chain from the entry-end wall | |
| A04 | Upper Bath 2 clear width | 2093.5 | 2200 | -106.5 | A08 lower chain | Re-set Bath 2 east wall with the Bed 2/study chain | |
| A05a | Stair side-wall clear zone | 1167.9 | 1100 | +67.9 | A08 | Move the dwarf wall about 68 toward the exterior wall | |
| A05b | Void clear width to entry-end wall | 2360.8 | 2550 | -189.2 | A08 | Return east face to X 24.350, not 24.539 | |

Smaller residuals, all probably within tracing and lining tolerance. Listed so they are not forgotten; no action proposed until item 9 is answered.

| Room | Model | Drawing | Diff | Source |
|---|---:|---:|---:|---|
| GF Bedroom 1 width | 4071.9 | 4000 | +71.9 | A07 |
| FF Bedroom 4 width | 4767.1 | 4680 | +87.1 | A08 |
| FF Bedroom 5 width | 4343.7 | 4310 | +33.7 | A08 |
| FF Bed 2 incl. robe | 4076.4 | 4000 | +76.4 | A08 |
| FF Theatre width | 4321.5 | 4300 | +21.5 | A08 |
| FF Bedroom 4 depth | 3220.2 | 3200 | +20.2 | A08 |
| FF Study width | 2405.4 | 2400 | +5.4 | A08 |
| FF Retreat width | 3006.9 | 3000 | +6.9 | A08 |

These are connected chains. Correcting Bath 2 changes Bed 2; correcting the WIR changes Bedroom 1 and the ensuite. They are corrected as chains, not as independent translations.

## Part 5. Missing detail: Chris supplies information, nobody guesses a move

| # | Item | What the model has | What the drawings give | What is needed | Decision / information |
|---|---|---|---|---|---|
| 10 | Alfresco corner opening D05 (A06) | Two headers about 4140 and 3595 long, underside 2280 | A11: two clear openings 3600 and 3000, height 2100. A07 corner | Jamb, post and support detail so the clear openings can be set. Beam length is not clear width | |
| 11 | Bracing coverage | One long cross on the ensuite-side wall. No diagonal on the Bed 4/robe partition | S18: two D1800 bays on the ensuite wall. S19: C2700 bay on the Bed 4/robe partition | Confirm bay positions after wall setout. These are arrangement errors, not translations | |
| 12 | Named steel and LVL members | No objects named ST2, HC1, 1L8 or 1L9. Generic lintels in some places | S09/S10 schedule them | Confirm their positions so they can be matched or added without duplicates | |
| 13 | Lintels and stud packs | Generic packs; lintel depth sometimes limited to head space | S12/S13 sizes and bearings | Confirm sizes after opening and level coordination. Walls are not shifted to suit simplified lintels | |
| 14 | Wet-area floor | Uniform 400 zone | Supplier: 360 shower members and recess details | Which rooms get recessed members, and the recess extents | |
| 15 | Special hip trusses | Envelope and typical T1 only; girders, truncated and jacks simplified | Roof shop sheets and final layout | Confirm the supplier layout is the one to follow once item 5 is settled | |
| 16 | Theatre platform | 2300 wide, 420 step, schematic supports | A08 written 2300 and 420 | Footprint, levels and support intent | |
| 17 | Foundations | Not modelled | S02 and geotechnical notes; founding depths not given | Founding depths or confirmation that the model stops at slab level | |
| 18 | Floor and roof fabrication IDs | Unique coordination marks per member; source group recorded | Supplier layouts repeat the type labels, so individual IDs cannot be placed | Confirm this is acceptable for teaching, or obtain a marked-up layout | |

## Part 6. Closed by measurement, listed so they are not reopened

| ID | Item | Why it is closed |
|---|---|---|
| R01 | Upper footprint 20810 x 8080 (A08) vs 20610 x 7880 (supplier) | Architecture includes 100 cladding each side. Timber outer faces checked against the A07 wall-over outline |
| R03 | Revision relationship | S03 names architectural issue 042224 of 20 January 2024. Title-block dates govern, not PDF metadata. Supplier validation stays open under item 5 |
| C01 | Local coordinate origin | Local setup verified against A03 bearing and north arrow. Global map location remains unverified and is not needed for teaching |

## What is waiting on this pack

Deliberately unbuilt until the rows above are decided: garage and porch roof coverings, full floor sheeting, D05 corner glazing, the Revit stair, engineered beams and lintels, bracing ties and connectors, and the frame correction revision. The student website shows the uncorrected frame with its notes stating that Chris's review is pending.

## How answers are recorded

1. Chris writes a decision and date in the row.
2. An agent copies the decision into the Status column of `revit/DISCREPANCY_LOG.md` or a new Decision paragraph under the item in `timber_frame/audit/POSITION_AUDIT.md`, citing this pack.
3. Only then is a correction task contracted under `collaboration/`. No model is changed on the strength of this pack alone.
