# Leichhardt frame positioning audit

Audited file: `Leichhardt_Timber_Frame_Stairs_Corrected.blend`. This is the saved stair-corrected revision containing the user edits preserved on 7 September 2026. No Blender model was changed during this audit. The original inventory/setout files predate the stair correction; measurements below were extracted from the actual corrected Blender file.

The audit identifies confirmed schedule/model mismatches, nominal architectural setout discrepancies, and unresolved differences between source drawings. A nominal wall-face comparison uses the faces of the 90 mm timber model. The architectural lining/finished-face convention still needs confirming before final millimetre setout; small residuals alone do not establish a misplaced wall.

## Findings and proposed corrections

| ID | Item | Model mm | Drawing mm | Difference mm | Basis |
|---|---|---:|---:|---:|---|
| A01 | W04 kitchen sill height | 1,419.0 | 905 | +514.0 | Confirmed schedule mismatch |
| A02a | Garage clear X between timber faces | 6,141.7 | 6,000 | +141.7 | Nominal wall-face mismatch |
| A02b | Garage clear Y between timber faces | 6,723.5 | 6,500 | +223.5 | Nominal wall-face mismatch |
| A03 | Ground-floor WIR clear width | 2,513.9 | 2,270 | +243.9 | Nominal wall-face mismatch |
| A04 | Upper Bath 2 clear width | 2,093.5 | 2,200 | -106.5 | Nominal wall-face mismatch |
| A05a | Stair side-wall clear zone | 1,167.9 | 1,100 | +67.9 | Nominal wall-face mismatch |
| A05b | Void clear width to entry-end wall | 2,360.8 | 2,550 | -189.2 | Nominal wall-face mismatch |
| A06 | D05 model header underside | 2,280.0 | 2,100 | +180.0 | Opening assembly incomplete |
| A07 | Garage wall base versus garage slab datum | -0.0 | -86 | +86.0 | Confirmed model datum mismatch |
| A08a | T5 model bottom chord overall horizontal length | 6,150.0 | 6,680 | -530.0 | Confirmed omitted chord extensions |
| A08b | T6 model bottom chord overall horizontal length | 950.0 | 1,395 | -445.0 | Confirmed omitted chord extensions |
| A09 | Floor frame overall vertical zone | 400.0 | 413 | -13.0 | Drawing conflict / coordination required |
| A10 | Study-side D bracing bay horizontal projection | 2,604.0 | 2,400 | +204.0 | Confirmed bracing bay-length mismatch |

Difference means model minus drawing. For A08, the comparison is overall chord extent, not span. For A09, 413 mm is a conflicting supplier dimension, not an approved replacement datum.

**A01 — W04 kitchen sill height**

Source: Architectural sheet 11, W04. Lower the W04 opening assembly by 514 mm; rebuild associated cripple studs and check the lintel/head.

**A02a — Garage clear X between timber faces**

Source: Architectural sheet 07, garage 6000. Re-establish garage wall setout from the 6000/90/240 dimension chain; keep the adjoining house reference fixed.

**A02b — Garage clear Y between timber faces**

Source: Architectural sheet 07, garage 6500 / overall 6980. Resolve both garage ends with the 1320 projection and roof supplier 6680 overall; do not shift only one roof edge.

**A03 — Ground-floor WIR clear width**

Source: Architectural sheet 07, WIR 2270. Re-set the bedroom/WIR/ensuite partition chain from the entry-end wall, including 4000 bedroom and 90 partitions.

**A04 — Upper Bath 2 clear width**

Source: Architectural sheet 08, bath 2200 in lower dimension chain. Re-set Bath 2 east wall with the adjoining Bed 2/study chain; check its door and W16 relationship.

**A05a — Stair side-wall clear zone**

Source: Architectural sheet 08, stairs 1100. Move the dwarf wall about 68 mm toward the exterior wall, subject to final lining basis; keep the corrected stair centreline.

**A05b — Void clear width to entry-end wall**

Source: Architectural sheet 08, void 2550. Coordinate dwarf-wall return and floor-edge trimmer; nominal east face of the return should be X=24.350 m, not X=24.539 m.

**A06 — D05 model header underside**

Source: Architectural sheet 11 D05 height 2100; sheet 07 corner opening. Coordinate both corner heads and jambs to the 3600 + 3000 by 2100 opening. Do not infer clear width from beam length.

**A07 — Garage wall base versus garage slab datum**

Source: Architectural sheet 07 garage FFL 10.820 vs house 10.906. Reconcile garage wall base, wall height and roof bearing together. Current garage roof chord base is already 86 mm below the model wall top.

**A08a — T5 model bottom chord overall horizontal length**

Source: Roof truss PDF page 20 (printed 19), maximum transport width 6680. Rebuild T5 using the shop end extensions and bearing positions; 6150 is the listed span, not the whole bottom-chord extent.

**A08b — T6 model bottom chord overall horizontal length**

Source: Roof truss PDF page 21 (printed 20), maximum transport width 1395. Rebuild T6 with 345 and 100 end extensions and specified bearing positions; retain the 950 span definition.

**A09 — Floor frame overall vertical zone**

Source: Subfloor shop sheets (e.g. PDF page 2) and layout page 47; architectural sheet 12 shows 400. Resolve the 400 architectural floor zone versus 413 supplier overall before changing upper floor, stairs or roof levels; map the separate 360 shower members.

**A10 — Study-side D bracing bay horizontal projection**

Source: Engineering S19, D2400 on study/retreat partition. Re-set the brace endpoints to the specified 2400 bay on the corrected wall; preserve the type-D cross arrangement.

## Stair surround: correction not yet complete

The corrected stair flight is now 4000 mm with 2000 mm entry-end clearance, but its surrounding walls were preserved in the previous edit. The dwarf-wall return is physically offset from the floor-edge trimmer: the nearest horizontal faces have a 76.7 mm gap. That is a model coordination defect independent of the nominal architectural clear-width comparison. The side dwarf wall and return need to be corrected together with their support edges. The previous stair update did not establish a fully coordinated stair/landing assembly.

Architectural sheet 07 labels a 3190 mm ground-floor stair dimension while sheet 08 labels 4000 mm. The latest stair revision follows sheet 08. This difference remains unresolved; do not call the staircase fabrication-ready or revise unrelated supporting members solely to make either drawing fit.

## Other room dimension checks

| Room / nominal span | Model mm | Drawing mm | Difference mm | Source |
|---|---:|---:|---:|---|
| GF Bedroom 1 width | 4,071.9 | 4,000 | +71.9 | Arch 07 |
| FF Bedroom 4 width | 4,767.1 | 4,680 | +87.1 | Arch 08 |
| FF Bedroom 5 width | 4,343.7 | 4,310 | +33.7 | Arch 08 |
| FF Bed 2 including robe zone | 4,076.4 | 4,000 | +76.4 | Arch 08 lower chain |
| FF Study width | 2,405.4 | 2,400 | +5.4 | Arch 08 |
| FF Retreat width | 3,006.9 | 3,000 | +6.9 | Arch 08 |
| FF Theatre width | 4,321.5 | 4,300 | +21.5 | Arch 08 |
| FF Bedroom 4 depth | 3,220.2 | 3,200 | +20.2 | Arch 08 |

These are connected dimension chains. Do not apply each difference as an independent wall translation: correcting Bath 2 changes the adjoining Bed 2 width, and correcting the WIR changes the bedroom and ensuite relationships. Residuals around 20–35 mm require the lining/face convention and tracing precision to be checked before declaring an error.

## Items requiring further detailing, not a guessed move

- **Alfresco corner:** model headers are approximately 4140 and 3595 mm long; schedule D05 gives two nominal clear openings of 3600 and 3000 mm. Those are different measurement types. Jamb and support details must establish the openings before a positional correction can be prescribed.
- **Window/door horizontal centres:** many were manually traced. This audit confirms the W04 vertical mistake, but does not certify every opening centre or installation allowance. Re-measure opening centres from written setout dimensions after walls are corrected.
- **Special hip trusses:** main roof envelope and typical T1 assemblies exist, but hip girders, truncated trusses and jacks were simplified. Rebuild their types and positions from roof shop sheets and the final supplier layout; the envelope alone does not verify them.
- **Steel/LVL schedule coverage:** no explicitly named ST2, HC1, 1L8 or 1L9 assemblies were found. Generic lintels may represent some areas; reconcile objects against S09/S10 visually before labelling each member absent or adding duplicates.
- **Lintel and stud packs:** the generator uses generic packs and can limit lintel depth to the available head space. Check actual sizes and bearings against S12/S13 after opening and level coordination; do not shift whole walls to accommodate the simplified lintels.
- **Wet areas:** the model has a uniform 400 mm floor zone. The supplier layout includes 360 shower members and recess details; local lowered top chords and their supports have not been reproduced.
- **Bracing:** S19 shows a C2700 bay on the horizontal Bed 4/robe partition; there is no corresponding diagonal object on that wall in the model. S18 shows two D1800 bays along the ensuite-side wall, while the model represents that wall with one long cross. These are arrangement/coverage errors, not just translations. Reconcile the remaining bays and connections after wall setout.
- **Theatre platform:** the 2300 mm model width follows a written dimension, but its support geometry and the interpretation of the 420 mm step remain schematic. Resolve its footprint/levels against architectural sheet 08 before detailing supports.

## Checks that do match the stated model basis

- Main upper timber outer envelope measures 20610 x 7880 mm, matching the supplier envelope. Architectural 20810 x 8080 includes the different exterior build-up and is not a reason to enlarge this timber rectangle.
- The corrected stair tread run is 4000 mm and its entry-end gap is 2000 mm, as selected from architectural sheet 08. Rough tread width remains an assumed 1020 mm centred within the 1100 mm architectural zone.
- The saved model has 15 standard T1, eight T5 and five T6 assemblies; count alone does not validate support location or special-truss geometry.
- Main roof nominal pitch is 25 degrees and the model uses the supplier 550 mm overhang. Architectural section 12 shows 450 mm, so this remains a documented drawing difference rather than an automatic 100 mm translation.
- Nominal ground and upper wall heights remain 2740 and 2590 mm from architectural section 12. Treating ceiling heights as top-of-frame datums remains an assumption; the floor/finish build-up needs resolving before approving Z positions.

## Correction sequence

1. Establish one reference coordinate system and identify which drawing dimensions refer to timber, masonry, linings or finished faces. Resolve the stair dimension and floor-depth conflicts before final supporting-member/level changes.
2. Re-set the garage and the WIR/bedroom/ensuite and upper Bath 2/Bed 2/study wall chains. Keep the verified main upper timber envelope as the initial reference. Validate room dimensions and junctions.
3. Coordinate the stair side wall, void return, floor trimmers, landing and bearing members as one assembly. Confirm the saved 4000 stair interpretation against the selected drawing basis.
4. Correct W04, then check all other opening centres, heights and lintels. Resolve the complete D05 corner opening with the structural support plan.
5. Correct garage base/roof bearing levels and rebuild T5/T6 chord extensions and bearings. Detail the supplier floor system, wet-area recesses and special hip trusses.
6. Complete the steel/LVL, bracing, stud-pack and platform audit; regenerate previews and the component inventory from the resulting model.

Implement by group in a new revision, retain the current file, and check that unrelated geometry has not changed. This report authorises no automatic model edits; it is the requested correction plan.

## Evidence

- [Architectural plans — sheets 07, 08, 11, 12](../../../Leichhardt_Architectural%20Plans%20(1).pdf)
- [Engineering plans — S09, S10, S12/S13 and S18/S19](../../../Leichhardt_Engineering%20Plans%20(1).pdf)
- [Roof truss shop drawings and final layout](../../../Leichhardt_Engineering%20Roof%20Truss%20Frame%20(1).pdf)
- [Subfloor shop drawings and final layout](../../../Leichhardt_Engineering%20Subfloor%20Frame%20(1).pdf)
- `measured_geometry.json`: measured saved-object transforms, bounds and source metadata.
- `position_audit.json`: comparison values and classifications.
