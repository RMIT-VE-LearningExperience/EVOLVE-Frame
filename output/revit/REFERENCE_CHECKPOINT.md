# Leichhardt reference checkpoint 01

> Historical reference-only checkpoint. The RVT now contains building geometry. See [GEOMETRY_PROGRESS.md](GEOMETRY_PROGRESS.md) and [TRANSFER_HANDOFF.md](../../TRANSFER_HANDOFF.md) for the saved state and continuation.

Saved 10 September 2026 to `Leichhardt_Coordination_Model.rvt` in this directory. The initial `Project1.rvt` remains in the workspace root.

The handoff's first sprint establishes and shows a datum/reference checkpoint before building geometry. This checkpoint contains **no walls, floors, roofs, studs or trusses**. Detailed timber/truss modelling is included in the accepted scope and remains to be done.

## Revit and bridge

- Revit2027.2, build27.2.0.39; metric multidisciplinary template, millimetres, non-workshared.
- Proposed construction scope. Existing/New Construction template phases retained.
- MCP read tools and the repaired C# command passed live checks. A SaveAs, transactions, PDF links, coordinate transforms and image exports succeeded.
- Compiler fix deduplicates assembly references by assembly name. The custom command replaces only `send_code_to_revit`; registry backup retained. Transaction mode `none` permits explicit transaction ownership and saving.

## Reference controls

| Control | Value |
|---|---:|
| Ground FFL | local0 / drawingRL10.906 |
| Garage and alfresco FFL | -86 mm |
| Ground ceiling, A12 | +2740 mm |
| First FFL, A12 | +3140 mm, subject to D01 |
| First ceiling, A12 | +5730 mm, subject to D01 |
| CX0 / CX1 / CX2 / CX3 | X0 /6130 /26990 /28430 mm |
| CY0 / CY1 / CY2 | Y0 /8180 /9500 mm |

CX/CY are added external-face **coordination controls**, not engineer-issued structural grids. They are pinned. A03 project-to-true-north transformation was checked numerically: increasing localX runs along bearing185deg24min40sec, consistent with the printed north arrow and undirected boundary bearing05deg24min40sec. The stored Revit angle is -95.411111 degrees. Shared XY are local; the map location is unverified.

Sixteen dedicated linked PDF views cover site, slab, floor plans, elevations, section, opening schedule, structural plans/schedule, bracing and supplier layouts. Two additional instances provide the ground and first coordination plan underlays. All18 instances are pinned.

- A03/A06/A07/A08/A12 calibrated to two perpendicular written dimensions; cross-direction error under0.16 mm at model scale.
- Roof and floor supplier layouts calibrated to20610 x7880 mm; residuals0.36 and1.07 mm respectively. Their printed title-block scales do not reflect the final PDF resize.
- S02/S09/S11/S18/S19 registered to matching architectural external-face footprints. Maximum cross-direction residual2.07 mm. This is underlay registration, not permission to scale structural setout.
- A09/A10 and the two schedules remain standalone sheet references at nominal scale. No geometry is derived from those scales.
- Plan-to-plan origin checks include28430 x9500 ground extents;20810 x8080 first-floor finished extents;100 mm cladding offsets; A07 red wall-over inner-face outline.

`reference_manifest.json` records original source paths, PDF page numbers, vector-coordinate control points, scales, offsets and residuals. `source_audit/` contains extracted text and the package/page register. Source dates are drawing title-block dates, not PDF metadata modification dates.

## QA and next stage

Live checkpoint QA: five levels, seven grids, sixteen reference views, eighteen pinned PDF instances, zero Revit warnings, zero walls. Ground and first-floor views were exported and visually inspected. The coordinate view is open in Revit.

Resolve or explicitly carry the choices in `DISCREPANCY_LOG.md` before dependent geometry:400/300/413 mm floor definitions, porch172/226 mm step, N1/N2 bracing classification, window widths and stair run. The floor-zone question is pending. Do not mark the building or its load paths coordinated on the strength of this reference checkpoint.
