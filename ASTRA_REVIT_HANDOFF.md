# EVOLVE - Frame: Revit Modelling Handoff for Astra

## Restart prompt

Use the following instruction when starting the new Astra session:

> Continue the Leichhardt Revit modelling task described in this handoff. Read this entire file before acting. First inspect the four source PDFs and connect to the user's open Autodesk Revit session. Do not modify the Revit model until you have confirmed the Revit version, the active project/template, project units, and the intended modelling scope. Then build the model in the staged order below, verifying each stage against the controlling drawings before proceeding. Preserve source hierarchy, record discrepancies, and never silently guess missing dimensions or resolve document conflicts without flagging them.

## User objective

Create a coordinated Revit model from the four PDF drawing packages in this workspace. The previous session was planning-only; no Revit model was created or edited.

The intended first deliverable is a coordinated architectural and structural model suitable for design coordination, using an initial target of LOD 300 unless the user specifies otherwise.

## Workspace

Workspace root:

`C:\Users\Stormtrooper\Git\EVOLVE - Frame`

At the time of handoff, the workspace contained no `.rvt`, `.rte`, or `.ifc` files. Confirm this again before beginning because the user may add a model or template after this handoff was written.

## Source drawing packages

### 1. Architectural package

File:

`Leichhardt_Architectural Plans (1).pdf`

Known properties:

- 32 pages.
- A3 landscape page geometry was detected.
- Produced from AutoCAD LT 2025.
- The embedded document modification date was 25 June 2026.
- The drawing title template contains the phrase `Single Storey`, but the structural package contains first-floor framing. Do not infer the building is single-storey from the template name.

Embedded sheet titles:

| Page | Sheet title |
|---:|---|
| 1 | Cover Sheet |
| 2 | Notes |
| 3 | Site & Roof Plan |
| 4 | Roof Plan |
| 5 | Site Notes |
| 6 | Slab Plan |
| 7 | Floor Plan (2) |
| 8 | Floor Plan |
| 9 | Elevations |
| 10 | Elevations |
| 11 | Window Schedule (2) |
| 12 | Section A-A (2) |
| 13 | Section Notes |
| 14 | Electrical Plan (2) |
| 15 | Internal Details |
| 16 | Internal Details |
| 17 | Internal Details (2) |
| 18 | Internal Details |
| 19 | Internal Details (2) |
| 20 | Energy Requirements |
| 21 | Notes & Details (2) |
| 22 | Details |
| 23 | Details |
| 24 | Details |
| 25 | Details |
| 26 | 9 AM shadow diagram |
| 27 | 10 AM shadow diagram |
| 28 | 11 AM shadow diagram |
| 29 | 12 PM shadow diagram |
| 30 | 1 PM shadow diagram |
| 31 | 2 PM shadow diagram |
| 32 | 3 PM shadow diagram |

The most important initial modelling references are pages 3, 4, 6-12, and the applicable detail sheets.

### 2. Structural engineering package

File:

`Leichhardt_Engineering Plans (1).pdf`

Known properties:

- 27 pages.
- A3 portrait page geometry was detected in the PDF.
- The embedded document modification date was 25 June 2026.

Embedded sheet register:

| Sheet | Title |
|---|---|
| S00 | Cover Sheet |
| S01 | General Notes |
| S02 | Ground Floor Footing & Slab Plan |
| S03 | Footing & Slab Legend |
| S04 | Footing & Slab Details |
| S05 | Footing & Slab Details |
| S06 | Footing & Slab Details |
| S07 | Site Drainage Details |
| S08 | Site Drainage Details |
| S09 | First Floor Framing Plan |
| S10 | First Floor Framing Schedule |
| S11 | Roof Framing Plan |
| S12 | Framing Details |
| S13 | Framing Details |
| S14 | Framing Details |
| S15 | Framing Details |
| S16 | Framing Details |
| S17 | Framing Details |
| S18 | Ground Floor Wall Bracing Plan |
| S19 | First Floor Wall Bracing Plan |
| S20 | Bracing Details |
| S21 | Bracing Details |
| S22 | Bracing Details |
| S23 | Bracing Details |
| S24 | Bracing Details |
| S25 | Tie-down Schedule & Details |
| S26 | Articulation Joint Plan |

The primary structural modelling references are S02-S06, S09-S11, and S18-S26.

### 3. Roof-truss fabrication package

File:

`Leichhardt_Engineering Roof Truss Frame (1).pdf`

Known properties:

- 22 pages.
- Created by PDF reDirect.
- The embedded creation date was 10 April 2026.
- Treat this as a supplier/fabrication package. Inspect its cover, layout plans, truss identifiers, profiles, reactions, and connection notes before using it.

### 4. Subfloor fabrication package

File:

`Leichhardt_Engineering Subfloor Frame (1).pdf`

Known properties:

- 47 pages.
- Created by PDF reDirect.
- The embedded creation date was 10 April 2026.
- Treat this as a supplier/fabrication package. Inspect its layout, member identifiers, spans, supports, blocking, reactions, and connection details before using it.

## Source hierarchy

Use the following document hierarchy unless the user directs otherwise:

1. Architectural drawings govern spatial layout, wall and opening locations, appearance, room arrangement, and architectural levels.
2. Structural engineering drawings govern footings, slabs, load-bearing elements, framing sizes, bracing, tie-downs, articulation joints, and structural connections.
3. Roof-truss and subfloor supplier packages govern manufactured member identities and fabrication setout where they agree with the engineer and architecture.
4. Never silently resolve a conflict. Record it in the discrepancy log and ask the user when it materially affects geometry or structural intent.

Written dimensions take priority over scaling from the PDF. Scale from a PDF only to establish a provisional reference and validate it against at least two known dimensions in different directions.

## Required checks before editing Revit

Confirm all of the following before the first model change:

- Autodesk Revit version.
- Whether an existing `.rvt` project is open or a new model is required.
- Required `.rte` template, if any.
- Project units. Default assumption is millimetres, but verify it.
- Whether the model should include existing, demolition, and proposed phases or proposed construction only.
- Required model scope: architecture, primary structure, detailed timber framing, documentation sheets, quantities, or a subset.
- Desired LOD. Default planning assumption is LOD 300.
- Required coordinate system, survey point, and project base point.
- Whether shared coordinates or consultant links exist.
- Required Revit worksharing/central-model arrangement.
- Required output filename and save location.

If any item is unknown, continue only with reversible reference setup that cannot distort the later model. Do not guess critical elevations, coordinates, member sizes, or construction assemblies.

## Recommended Revit file setup

Suggested new-model filename if the user has no naming standard:

`Leichhardt_Coordination_Model.rvt`

Recommended browser organisation:

- `00 Coordination`
- `01 Existing` if existing conditions are in scope
- `02 Proposed Architectural`
- `03 Structural`
- `04 Framing Coordination`
- `05 QA`

Recommended dedicated PDF reference views:

- `REF_A03_Site_Roof`
- `REF_A06_Slab`
- `REF_A07_Floor_1`
- `REF_A08_Floor_2`
- `REF_A09_A10_Elevations`
- `REF_A12_Section_AA`
- `REF_S02_Footing_Slab`
- `REF_S09_First_Floor_Framing`
- `REF_S11_Roof_Framing`
- `REF_S18_Ground_Bracing`
- `REF_S19_First_Bracing`
- `REF_Roof_Truss_Layout`
- `REF_Subfloor_Layout`

Keep imported or linked PDF references in dedicated views, calibrate them using written dimensions, align them to stable datums, pin them, and prevent them from printing on production sheets unless explicitly required.

## Modelling sequence

### Stage 0 - Audit and establish controls

1. Inspect the complete drawing register and revision information in all packages.
2. Identify the current revision and any superseded sheets.
3. Check that architectural and engineering plans refer to the same design revision.
4. Create a discrepancy log.
5. Confirm Revit version, template, units, phases, model scope, coordinates, and output location.
6. Save the initial model before adding geometry.

Stage gate: do not proceed until the controlling drawing revision and project units are known.

### Stage 1 - Datums and references

1. Derive levels from architectural sections and elevations.
2. Cross-check structural vertical relationships and floor zones.
3. Create named levels for ground floor, first floor, roof/eaves, and any slab or framing offsets shown.
4. Establish grids from the clearest dimensioned structural or architectural plan.
5. Set project north and true north from the site plan.
6. Establish the project base point and survey relationship.
7. Link the controlling PDF pages into dedicated reference views.
8. Calibrate each PDF against at least two written dimensions.
9. Align and pin each reference.

Stage gate: levels, grids, orientation, origin, and PDF calibration must be checked before model geometry begins.

### Stage 2 - Architectural shell

1. Model external walls using provisional assemblies only when the full build-up is not yet known.
2. Model internal walls and distinguish load-bearing walls where the engineering drawings identify them.
3. Create ground and upper floors with correct boundaries, openings, and vertical offsets.
4. Add major openings, voids, stairs, and shafts.
5. Add doors and windows using schedule identifiers where available.
6. Model the roof geometry, pitches, ridges, hips, valleys, eaves, and openings.
7. Check all four elevations and Section A-A against the model.

Stage gate: plans, elevations, and section must agree before structural framing is added.

### Stage 3 - Foundations and slab

1. Use S02 as the primary setout drawing.
2. Use S03-S06 for symbols, member types, reinforcement intent, and details.
3. Model slab edges, thickenings, strip footings, pads, piers, steps, rebates, and major penetrations that are in scope.
4. Preserve structural type marks from the drawings in Revit parameters.
5. Cross-check architectural slab boundaries and levels.

Stage gate: foundation geometry and vertical offsets must be coordinated before upper framing begins.

### Stage 4 - First-floor and subfloor framing

1. Use S09 for the engineering framing layout and S10 for the framing schedule.
2. Compare the supplier subfloor layout with S09 and the architectural floor plan.
3. Model primary beams, bearers, joists, rim members, blocking, posts, and supports that are within scope.
4. Map supplier member IDs into a dedicated parameter rather than using them as family type names unless the user's standard requires that.
5. Record mismatched spans, supports, openings, or member designations.
6. Check stair, plumbing, duct, and floor-opening coordination.

Stage gate: support conditions, member directions, openings, and supplier IDs must be verified.

### Stage 5 - Roof and truss framing

1. Use S11 as the engineering roof-framing control.
2. Compare the 22-page roof-truss package with S11 and the architectural roof plan.
3. Model trusses, girders, rafters, beams, hips, valleys, overhangs, and supports to the agreed scope.
4. Retain supplier truss IDs in a dedicated parameter.
5. Coordinate truss profiles against roof geometry, ceilings, voids, and service penetrations.
6. Flag reaction or support locations that do not coincide with suitable walls, beams, posts, or foundations.

Stage gate: roof geometry, truss profiles, supports, and reactions must agree before bracing and documentation work.

### Stage 6 - Bracing, tie-downs, and articulation

1. Model or annotate ground-floor bracing from S18.
2. Model or annotate first-floor bracing from S19.
3. Apply details and type references from S20-S24.
4. Coordinate tie-down requirements from S25.
5. Add articulation joints from S26 and compare them with architectural finishes and openings.
6. Use shared parameters for bracing and tie-down type marks if schedules are required.

### Stage 7 - Coordination and QA

1. Compare every model level with the architectural elevations and Section A-A.
2. Compare wall, floor, and roof extents with architectural plans.
3. Compare structural setout and member types with engineering plans.
4. Compare supplier IDs, supports, and framing directions with the fabrication packages.
5. Check stairs, openings, wet areas, service penetrations, roof voids, and load paths.
6. Review Revit warnings and resolve modelling errors without altering design intent.
7. Create coordination views with architectural, structural, and supplier-reference overlays.
8. Record all unresolved discrepancies with source sheet references and screenshots where useful.
9. Save a verified checkpoint model before documentation or detailing begins.

## Revit modelling conventions

- Work in millimetres unless the project confirms another unit system.
- Use levels and grids as primary constraints; avoid unconstrained geometry.
- Use native Revit system families for walls, floors, roofs, foundations, and framing wherever practical.
- Do not over-model fabrication detail at LOD 300.
- Use type parameters for properties shared by every instance and instance parameters for unique supplier marks or local variations.
- Preserve drawing IDs in parameters such as `Type Mark`, `Mark`, or a project-specific shared parameter.
- Avoid in-place families unless ordinary system/loadable families cannot represent the required geometry.
- Do not trace tiny PDF inaccuracies. Use written dimensions and rational alignments.
- Pin calibrated references and datums after verification.
- Save verified stage checkpoints using the user's file/versioning convention.

## Discrepancy log format

Use a table with the following fields:

| ID | Location | Architectural source | Structural source | Supplier source | Issue | Proposed interpretation | Status/decision |
|---|---|---|---|---|---|---|---|

Do not mark an item resolved without either clear controlling documentation or the user's decision.

## Suggested first modelling sprint

The first active Revit session should stop after a verified reference model is established:

1. Connect to the open Revit project or create the approved new project.
2. Confirm version, units, template, phases, scope, and save location.
3. Create project levels from the architectural elevations and Section A-A.
4. Create the primary grids.
5. Establish project and true north.
6. Link and calibrate architectural pages 3, 6-8, and 12.
7. Link and calibrate structural sheets S02, S09, and S11.
8. Verify that all references align at a common origin.
9. Save a checkpoint.
10. Show the user the datum/reference setup before tracing model geometry.

This checkpoint is intentionally early: an incorrect origin, scale, grid, or level would contaminate every later modelling stage.

## Current connection status

The previous session attempted to discover native desktop apps, but the available computer-control runtime returned no native apps and did not expose a Revit binding. It also rejected a direct Autodesk Revit app request because native app control was unavailable in that session.

Therefore:

- No Revit session was connected.
- No Revit project was opened, created, saved, or edited.
- No PDFs were imported or linked into Revit.
- No model elements were created.

In the next session, use an available native-app/Revit connector if exposed. If Revit still cannot be controlled, report the exact connection limitation and prepare the remaining work without pretending the model was modified.

## Immediate questions for the user if not already answered

Ask only what is still necessary after inspecting the active Revit session:

1. Which Revit version and project/template should be used?
2. Is the required output architecture plus primary structure at LOD 300, or should detailed timber/truss fabrication geometry also be modelled?
3. Should the model include existing/demolition phases or proposed work only?
4. Is there a required coordinate origin, survey file, or company BIM standard?
5. Where should the `.rvt` file be saved and what should it be named?

## Definition of done for the coordination model

The model is complete only when:

- Levels, grids, north orientation, and coordinates are verified.
- Architectural plans, elevations, and sections agree with the model.
- Foundations, first-floor framing, and roof framing agree with the structural engineer's drawings.
- Supplier subfloor and roof-truss layouts are reconciled with engineering and architecture.
- Major openings and support/load paths are coordinated.
- Bracing, tie-downs, and articulation joints are represented to the agreed scope.
- Revit warnings have been reviewed.
- Unresolved drawing conflicts are documented rather than hidden.
- The final model is saved to the approved path with a clear checkpoint/version name.

