# Leichhardt 3D model review — questions for Chris

**Review phase:** Phase 1 — Blender building and timber-frame geometry only  
**Primary file:** `Leichhardt_Timber_Frame_Stairs_Corrected.blend`  
**Software:** Blender 5.0 or later  
**Prepared:** 2 November 2026  
**Audited revision:** Stair-corrected user revision preserved 7 September 2026  
**File size:** 2,047,783 bytes  
**SHA-256:** `8a0a99d3eb1dd2dc8b14ae20c531698d06dc31fec46e73b2d944adec95b95b9f`  
**Status:** Decision request; not a construction, fabrication or engineering certification

**Chris's role:**  
**Chris's authority for this review:**  
**Decisions Chris must refer to another person:**  

## What we need from Chris

Please review the questions below and record a decision, source and comment for each item you can answer. If an item needs an architect, engineer, truss supplier, builder or site measurement, please identify that person rather than guessing.

Use one of these responses:

- **CONFIRM MODEL** — leave the current geometry unchanged.
- **CORRECT AS NOTED** — apply the correction described in the question.
- **USE OTHER VALUE** — provide the value, measurement basis and source.
- **REFER** — identify who must decide or what evidence is missing.
- **OUT OF SCOPE** — do not resolve in this model review.

No model correction is authorised unless the response identifies the item and decision clearly.

## Review scope

### Included

- Building and frame position, dimensions and levels.
- Wall, opening, stair, floor-frame and roof-frame relationships.
- Timber, steel/LVL, bracing and truss completeness at coordination-model level.
- Conflicts between the architectural, engineering and supplier drawings.
- Whether an unresolved item may remain visibly provisional for teaching use.

### Not included in this phase

- Animation, construction-stage sequencing or camera movement.
- Website behaviour or the interactive student experience.
- Lighting, rendering, presentation cameras or visual effects.
- Final colours, textures, product selections or aesthetic approval.
- Structural certification, fabrication approval or construction sign-off.

## Files to give Chris

1. `output/timber_frame/Leichhardt_Timber_Frame_Stairs_Corrected.blend`
2. This questionnaire.
3. `output/timber_frame/audit/POSITION_AUDIT.md`
4. `output/README.md`
5. `output/revit/DISCREPANCY_LOG.md` — drawing conflicts and later coordination decisions only; it does not describe the Blender object's current state.
6. `Leichhardt_Architectural Plans (1).pdf`
7. `Leichhardt_Engineering Plans (1).pdf`
8. `Leichhardt_Engineering Roof Truss Frame (1).pdf`
9. `Leichhardt_Engineering Subfloor Frame (1).pdf`

The enclosure and learning-experience Blender files are derived from the current frame and should not be used to approve frame positions. They must be regenerated after approved frame corrections.

**Do not review `Leichhardt_Timber_Frame.blend` by mistake.** The filename and SHA-256 above identify the exact corrected file for this review.

## How to inspect the Blender model

1. Open `Leichhardt_Timber_Frame_Stairs_Corrected.blend` in Blender 5.0 or later.
2. Confirm metric units are displayed in millimetres.
3. Use the View Layer selector to inspect the complete frame, ground framing, floor structure, upper walls and roof structure separately.
4. Treat object names and metadata as coordination labels, not a procurement list.
5. Compare written drawing dimensions before relying on scaled PDF or viewport measurements.
6. Record answers by item ID. Screenshots or marked-up plan excerpts are welcome where a written answer is ambiguous.

## P0 — decisions required before geometry is corrected

These questions control multiple downstream objects. Please answer them before individual wall or member moves are approved.

### Q01 — Measurement-face convention

The audit compares many dimensions to the faces of the 90 mm timber frame. Architectural room and external dimensions may instead refer to plasterboard, masonry, lining or finished faces.

**Question:** For internal room and opening setout, which face should the Blender model use as the dimension reference?

- [ ] Timber-frame face
- [ ] Plasterboard/lining face
- [ ] Masonry/external face
- [ ] Finished face
- [ ] Varies by dimension; identify the rule below

**Chris response:**  
**Source or marked-up example:**  
**Who else must confirm:**  

### Q02 — Source precedence

The source package contains architectural drawings issued 20 January 2024, engineering revision C1 dated 3 December 2025, and floor/roof supplier documents from April 2026. Later supplier information does not automatically prove architectural or engineering approval.

**Question:** If known within Chris's role, what is the approved decision path and which source controls geometry before written clarification is received? Otherwise, identify the architect, engineer, supplier or project owner who must decide.

**Chris response:**  
**Source/authority:**  
**Items that must remain on hold:**  

### Q03 — Required model accuracy

The current asset is a drawing-based teaching and coordination model, not a fabrication model.

**Question for the project owner/teaching lead:** What dimensional tolerance is acceptable for this review? Chris may recommend a tolerance or refer this decision.

- [ ] Teaching model only; tolerance: ______ mm
- [ ] Coordination model; tolerance: ______ mm
- [ ] REFER to project owner/teaching lead

**Chris response:**  

### Q03A — Blender coordinate origin and fixed references

The correction sequence requires one stable coordinate system. The later Revit model uses a local origin at the west garage boundary/external face, the main ground-floor south external face and ground FFL, but that convention is not automatically approval for the Blender file.

**Question:** Confirm the Blender origin, axes and fixed reference faces to retain while connected wall chains are corrected, or identify who must approve them.

**Chris response:**  
**Approved origin/fixed references:**  
**Source/authority:**  

### Q04 — Floor and vertical datum

Architectural sheet 12 shows a 400 mm floor zone. Supplier information shows 413 mm typical members, 360 mm recessed wet-area members, 19 mm flooring and a 10 mm direct ceiling. The 413 + 19 + 10 mm build-up is 442 mm, which is 42 mm deeper than the architectural zone. The engineering schedule also refers to 300-deep posi-struts or equivalent. The Blender frame currently keeps a 400 mm zone and assumes the architectural 2740/2590 ceiling heights can act as frame wall-top datums.

**Question:** What exact structural depth, deck thickness and finished-floor datum should control the upper floor, stair, ceiling and roof levels?

**Chris response:**  
**Typical joist depth:**  
**Wet-area joist depth/recess:**  
**Deck thickness:**  
**Ceiling lining thickness:**  
**Confirmed upper FFL relative to ground FFL:**  
**Do 2740/2590 refer to finished ceilings or frame wall tops?:**  
**Source/authority:**  

### Q05 — Stair interpretation

Architectural sheet 07 labels a 3190 mm ground-floor stair dimension; sheet 08 labels 4000 mm and shows a 1100 mm stair zone and 2550 mm void dimension. The corrected Blender stair uses a 4000 mm run, but surrounding walls and trimmers are not fully coordinated. A 76.7 mm physical gap remains between the dwarf-wall return and floor-edge trimmer.

**Question:** Which stair dimension governs, what does each conflicting dimension measure, and may the model coordinate the wall, return, landing and trimmers around the 4000 mm interpretation?

- [ ] Refer to architect/stair supplier/engineer
- [ ] Keep the 4000 mm model interpretation and coordinate surrounding framing
- [ ] Use 3190 mm; explain what it controls
- [ ] Use another interpretation shown below

**Chris response:**  
**Required stair width:**  
**Required void size:**  
**Source/marked-up detail:**  

### Q06 — Garage and porch vertical levels

The garage FFL is RL 10.820 versus house FFL RL 10.906, a difference of 86 mm. The porch written RL 10.734 is 172 mm below the house FFL, while a drawing label says a 226 mm step. The Blender frame documentation currently uses a 226 mm porch drop. The later Revit coordination model used the written RL value (-172 mm), and engineering sheet S02 says the architectural FFL must be confirmed.

**Question:** Confirm only the garage and porch level values and identify whether each refers to slab, structural frame, or finished surface. Refer the porch conflict to the architect if Chris cannot approve it. Q14 separately addresses the garage wall/roof assembly.

**Garage level relative to house FFL:**  
**Porch level relative to house FFL:**  
**Measurement surface/basis:**  
**Source/authority:**  

### Q07 — Wind classification and supplier validation

Engineering bracing drawings refer to N1. Supplier floor/roof documents refer to N2, and the engineering notes say the truss layout must be presented for validation.

**Question:** If known, cite the approved record showing that the supplier arrangement was reviewed against the engineering design. Otherwise refer the N1/N2 decision to the engineer and truss supplier; Chris is not being asked to certify it.

- [ ] Validated; record attached/reference: ____________________
- [ ] Not validated; keep the assembled frame marked provisional
- [ ] Refer to engineer/truss supplier

**Chris response:**  

## P1 — specific geometry decisions

### Q08 — W04 kitchen sill

The model sill is 1419 mm; architectural window schedule W04 gives 905 mm. The model is 514 mm high.

**Question:** May W04 be lowered by 514 mm and its cripple studs, jambs, lintel/head and window proxy rebuilt to the schedule?

- [ ] CORRECT AS NOTED
- [ ] CONFIRM MODEL
- [ ] USE OTHER VALUE: ______ mm
- [ ] REFER

**Chris response/source:**  

### Q09 — Garage plan setout

Measured between current timber faces, the garage is approximately 6141.7 mm by 6723.5 mm. Architectural sheet 07 shows 6000 mm by 6500 mm and an overall 6980 mm chain. T5 transport-width and extension questions are handled separately in Q15.

**Question:** What do the 6000, 6500 and 6980 dimensions each measure, which adjoining house reference remains fixed, and what exact timber-face setout should be used?

**Chris response:**  
**Confirmed timber-face dimensions:**  
**Fixed reference:**  
**Source/marked-up plan:**  

### Q10 — Ground-floor bedroom/WIR/ensuite chain

The current WIR clear width is approximately 2513.9 mm; architectural sheet 07 shows 2270 mm. The connected chain also includes the 4000 mm Bedroom 1 dimension and 90 mm partitions.

**Question:** Using the measurement-face convention decided in Q01, confirm the complete approved chain. Which wall should move, and which reference must remain fixed?

**Chris response:**  
**Approved chain:**  
**Fixed reference:**  

### Q11 — Upper Bath 2/Bed 2/Study chain

The current Bath 2 clear width is approximately 2093.5 mm; architectural sheet 08 shows 2200 mm. Moving its east wall changes Bed 2, the study chain, the door and W16 relationship.

**Question:** Confirm the complete chain and the correct wall/opening positions rather than approving an isolated 106.5 mm move.

**Chris response:**  
**Approved chain:**  
**Opening impacts:**  

### Q12 — Stair-side wall and void return

The current stair-side clear zone is approximately 1167.9 mm versus a 1100 mm drawing dimension. The void clear width is approximately 2360.8 mm versus 2550 mm. These are connected to Q05 and the 76.7 mm wall-return/trimmer gap.

**Question:** After Q05 is answered, confirm the final stair-side wall face, void return face, trimmer position and lining allowance.

**Chris response:**  
**Target dimensions and faces:**  

### Q13 — D05 alfresco corner opening

Architectural information indicates two corner openings of 3600 mm and 3000 mm by 2100 mm. The model header underside is approximately 2280 mm, and the current model headers are approximately 4140 mm and 3595 mm long. Beam lengths cannot be treated as clear opening widths.

**Question:** If known, confirm whether the dimensions are clear openings, nominal window/door units or rough structural openings. Cite the approved corner jamb/post, head, bearing and support detail; otherwise refer the assembly to the architect/engineer rather than designing it in this review.

**Chris response:**  
**Opening basis:**  
**Required support detail/source:**  

### Q14 — Garage wall, roof bearing and parapet relationship

The garage frame currently starts at the house datum instead of the garage level. The roof chord is already 86 mm below the current model wall top. The Blender frame does not contain a completed masonry parapet. Separately, the later Revit discrepancy D06 records a provisional parapet top of about +3514 mm and T5 roof height of about +3641 mm before roof covering.

**Question:** Using the level decided in Q06, confirm the intended garage wall height and truss bearing elevation. If a parapet is part of the design, cite the approved parapet/roof interface; otherwise refer this assembly for architectural/engineering coordination.

**Chris response:**  
**Confirmed elevations:**  
**Required detail/source:**  

### Q15 — T5 and T6 chord extensions

The Blender model uses 6150 mm for T5 and 950 mm for T6 as overall bottom-chord lengths. Roof truss PDF page 20 (printed 19) gives a 6680 mm maximum transport width for T5. Page 21 (printed 20) gives a 1395 mm maximum transport width for T6, comprising a 950 mm span plus 345 mm and 100 mm extensions. The audit does not establish the T5 extension split, and transport width should not be assumed to equal bottom-chord extent without supplier confirmation.

**Question:** Confirm the exact T5/T6 bottom-chord extensions and bearing positions from the supplier details. May the trusses then be rebuilt while retaining the listed 6150/950 mm spans?

- [ ] CONFIRM MODEL
- [ ] CORRECT USING CONFIRMED SUPPLIER EXTENSIONS
- [ ] USE OTHER VALUE/DETAIL
- [ ] REFER TO TRUSS SUPPLIER/ENGINEER

**Chris response/source:**  

### Q16 — Main timber envelope and roof overhang

The model uses a 20610 x 7880 mm timber envelope and 550 mm roof tails. The architecture shows a 20810 x 8080 mm exterior envelope including 100 mm cladding each side and a 450 mm overhang from the finished face. The later Revit discrepancy register treats these as the same overall roof width after accounting for cladding, but that interpretation is not itself approval of the Blender model.

**Question:** Is the 100 mm-cladding measurement explanation accepted for the Blender model, or should its roof geometry use the 450 mm architectural overhang on another basis?

- [ ] CONFIRM MODEL
- [ ] CORRECT TO 450 MM ARCHITECTURAL OVERHANG; state reference face
- [ ] USE OTHER INTERPRETATION
- [ ] REFER

**Chris response/source:**  

### Q17 — Bracing arrangement

The study/retreat D brace projects approximately 2604 mm versus D2400 on engineering sheet S19. A C2700 bay at Bed 4/robe is not represented, and two D1800 bays on engineering sheet S18 at the ensuite-side wall appear as one long cross in the model. This also depends on the wind-classification decision in Q07.

**Question:** If Chris has an approved mark-up, identify the required bracing bays, wall faces and start/end points. Otherwise refer S18/S19 and the corrected wall setout to the engineer for confirmation.

**Chris response:**  
**Approved bracing mark-up/source:**  

### Q18 — Opening centres and allowances

Many horizontal opening centres were traced from calibrated drawings. The model uses scheduled nominal widths/heights without confirmed rough-opening or installation allowances. Upper windows W14/W15/W17/W19 also have a 2230 mm schedule width versus 2300 mm plan text.

**Question:** Which opening source controls, what rough-opening/installation allowance applies, and who confirms the final centreline setout?

**Chris response:**  
**Upper-window width decision:**  
**Allowance rule:**  
**Authority/source:**  

### Q18A — Other connected room dimensions

The audit also records the following model-minus-drawing differences. These are connected wall chains and must not be applied as independent translations.

| Room/span | Difference |
|---|---:|
| Ground-floor Bedroom 1 width | +71.9 mm |
| First-floor Bedroom 4 width | +87.1 mm |
| First-floor Bedroom 5 width | +33.7 mm |
| First-floor Bed 2 including robe zone | +76.4 mm |
| First-floor Study width | +5.4 mm |
| First-floor Retreat width | +6.9 mm |
| First-floor Theatre width | +21.5 mm |
| First-floor Bedroom 4 depth | +20.2 mm |

**Question:** After Q01 and the main wall-chain decisions are answered, identify which differences are acceptable, which require a connected-chain correction, and which need a marked-up plan or site confirmation.

**Chris response:**  
**Accepted differences/tolerance basis:**  
**Chains to correct:**  

## P2 — completeness and detailing decisions

### Q19 — Special roof trusses

Hip girders, truncated trusses, jack trusses and hip intersections are simplified to the roof envelope.

**Question:** Which special truss types must be modelled individually for the intended teaching/review use, and which may remain simplified?

**Chris response:**  

### Q20 — Named steel/LVL members

The audit did not find objects explicitly named ST2, HC1, 1L8 or 1L9. Generic objects may represent some locations.

**Question:** Confirm each member's required location, section, bearing and label before any new object is added, so existing generic members are not duplicated.

**Chris response/mark-up:**  

### Q21 — Lintels, studs and point-load transfer

The model uses generic jamb packs and can limit lintel depth to available head space. It does not exhaustively reproduce all stud packs, bearings and point-load transfer blocks from engineering sheets S12/S13.

**Question:** Which openings and load paths require detailed member-by-member modelling in this phase?

**Chris response:**  

### Q22 — Wet-area floor framing

The current model has a uniform floor zone. Supplier documents include 360 mm recessed shower members and local recess details.

**Question:** Confirm the wet-area locations, recess depth, deck/finish relationship and supporting members to model.

**Chris response/source:**  

### Q23 — Theatre platform

The 2300 mm wide, 420 mm high theatre platform follows written architectural dimensions, but its footprint interpretation and support framing are schematic.

**Question:** Should the platform remain an illustrative architectural volume, or should its structural framing be detailed? If detailed, provide the approved level and support information.

**Chris response:**  

### Q24 — Elements intentionally omitted

Footings, reinforcement, detailed slab construction, masonry, insulation, full cladding, glazing systems, floor sheeting, roof coverings, service penetrations and complete connection/fastener sets are outside the corrected timber-frame file.

**Question:** Are any of these required for the immediate 3D model review? List only items that must be included before Phase 1 is accepted.

**Chris response:**  

## Additional observations from Chris

Please list any model error or missing item not covered above. Include the location, drawing/detail reference, expected geometry and priority.

| New ID | Location/item | Required change or question | Source/detail | Priority |
|---|---|---|---|---|
| C01 |  |  |  |  |
| C02 |  |  |  |  |
| C03 |  |  |  |  |

## Chris review sign-off

This sign-off records review decisions for revising the coordination/teaching model. It does not certify structural design, fabrication or construction compliance.

**Reviewer name:**  
**Role/authority:**  
**Review date:**  
**Model filename reviewed:**  
**Model revision/date shown:**  
**Questions answered:**  
**Questions referred or left open:**  
**May the team create a new Blender revision from the answered items?** Yes / No / With conditions  
**Conditions:**  

## What happens after Chris replies

1. Record each answer against its question ID and retain the source or marked-up evidence.
2. Separate confirmed corrections from items that still need architect, engineer, supplier, builder or site confirmation.
3. Copy the current `.blend` file to a new revision; do not overwrite the reviewed source.
4. Correct connected assemblies as groups rather than moving isolated objects.
5. Re-run the geometry audit, model checks, inventory and review renders.
6. Independently review the exact revised model and document every remaining provisional item.
7. Regenerate the enclosure and learning derivatives only after the frame revision is accepted.
