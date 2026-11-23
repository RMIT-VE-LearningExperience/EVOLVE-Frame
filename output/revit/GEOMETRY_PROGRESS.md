# Leichhardt geometry checkpoint — 10 September 2026

Saved in `Leichhardt_Coordination_Model.rvt`. Native building geometry now exists; the earlier reference checkpoint is historical. Work paused at the user's request to move PCs.

| Geometry | Count |
|---|---:|
| Native walls | 56 |
| Native floors | 5 |
| Native footprint roofs | 3 |
| Native timber members | 2,195 |
| Individual steel web solids | 767 |
| Hosted windows | 19 |
| Hosted doors/passages | 22 |

Timber comprises 369 members in 62 roof trusses, 1,305 wall-frame members and 521 timber pieces in 93 floor joists. Floor webs are structural-framing DirectShapes; timber is native parametric rectangular framing. Roofs/walls/floors are coordination envelopes; layered finishes are not fully specified. Windows and doors are wall-hosted native families with scheduled nominal dimensions; frame subdivisions, glazing and leaf profiles are provisional visual geometry, not manufacturer shop details.

Views `03 Building Geometry - Coordination WIP` and `04 Timber and Trusses - Coordination WIP` provide the shell and exposed framing respectively. Exported `geometry-review` PNGs are included. View 04 was active at save. Roof pitches have been corrected to 25 degrees main / 5 degrees garage and porch after verifying the API's rise/run convention.

## Evidence and limits

`geometry_audit.json` found the expected 2,195 timber members, no duplicate timber marks, no missing members/type-size mismatches, and negligible location-axis deviation from the generated manifests. The last live model check reported zero Revit warnings. Sample actual solids were checked for timber section dimensions and axis extents. These checks establish implementation consistency; they do NOT establish full drawing coordination, clash freedom, load paths or fabrication suitability. The next review should inspect isolated floor framing and extend actual-solid checks.

The source layout was calibrated to written dimensions. Some un-dimensioned member centres/jamb positions were derived from calibrated PDF vectors and remain provisional. Roof webs use square end cuts extended to chord axes; pressed plates and shop end cuts are pending. Floor joist exact written spans and supplier type quantities were retained. Individual fabrication IDs could not be assigned to exact plan positions because the layout labels repeat the type: each instance has a unique coordination mark and its source group recorded.

MultiStrut webs use 1 mm G300 Z275 steel, supported by the [manufacturer's September 2024 specification](https://www.multinail.com.au/wp-content/uploads/2024/09/MultiStrut_09_2024.pdf). Profile outlines follow the supplier drawing; front/back face allocation is inferred from drawing fill. Pressed ribs and nail teeth are omitted. Twenty-five compound outlines were repaired by polygon union before extrusion.

Wall studs follow architectural 90x45 sections, 450 mm maximum GF / 600 mm FF spacing. Head rails in wall frames do not replace the engineered lintels still to be added. Timber grades appear in type names; the shared timber appearance is named MGP10 and needs clearer separation from grade-specific structural material metadata (some hip chords are MGP12). Do not use this appearance material as a certified engineering property.

## Preserved conflicts and remaining scope

- D01: retain first FFL +3140. Supplier 413 mm joists plus 19 mm deck give joist underside +2708; 10 mm ceiling gives +2698, 42 mm below the architectural ceiling. GF framing plate top +2750 overlaps that floor zone. This clash is retained, not resolved.
- D02: porch uses written RL10.734, 172 mm below GF. The separate 226 mm label remains conflicting.
- D03: engineering N1 versus supplier N2 wind classifications; supplier-to-engineer validation not evidenced.
- D04: disputed upper windows use schedule width 2230 mm; plan text says 2300. No invented rough-opening allowance.
- D05: stair not built; GF/FF written runs differ. The upper deck void is present provisionally.
- D06: garage T5 roof support/parapet elevations need review; existing parapet envelope top is +3514 while T5 reaches roughly +3641 before roof skin.

Primary engineered beams/columns/lintels, foundations and founding depths, stair, strongbacks, bracing/ties/connectors, architectural piers, parapet interfaces, soffits/fascias/gutters, and detailed wall/roof finishes remain outstanding. Do not mark the full original coordination scope complete. See TRANSFER_HANDOFF.md at the project root for safe continuation and machine setup.
