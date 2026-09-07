# Leichhardt frame-stage Blender model

Open `Leichhardt_Frame.blend`. Metric model: one Blender unit is one metre; dimension display is millimetres. Individual members remain editable and are named by role. Collections separate the ground walls, structural steel/LVL, first-floor joists, upper walls, main roof, garage roof, porch roof, bracing, stairs and battens. Four cameras and four inspection view layers are included. Plan images are packed in the hidden reference collection.

This is a plan-referenced visual reconstruction of the whole frame stage, with simplified details. It is not a fabrication model or a verified structural coordination model. The component inventory reports modeled objects, not a procurement/cut list.

## Drawing basis

- `Leichhardt_Architectural Plans (1).pdf`: sheets 06, 07, 08, 11 and 12 establish the layout, openings and levels. The wall lines are manually traced and calibrated to the timber envelope. Window/door widths and heights are taken from the schedule, with nominal openings; installation allowances are not added.
- `Leichhardt_Engineering Plans (1).pdf`: S09-S13 establish steel/LVL members, lintel sizes, stud/plate sizes and spacing. S18-S25 establish the bracing and connection vocabulary. Steel member designations are retained.
- `Leichhardt_Engineering Subfloor Frame (1).pdf`: April 2026 MSJ-400-45 floor members, 450 mm spacing and the final layout establish the floor system and stair void. Timber chords are 90x45. Individual supplier FJ shop panel arrangements are simplified into alternating metal webs. Model FJ numbers are instance IDs, not the supplier FJ type numbers. Span zones, strongbacks and rims are approximate traces.
- `Leichhardt_Engineering Roof Truss Frame (1).pdf`: April 2026 T1 geometry, 15 standard trusses, 7,880 mm span, 25 degree pitch, 550 mm overhang, 900 mm typical spacing; eight garage T5 and five porch T6 assemblies. T1 Fink web layout follows the detail. Hip girders, truncated trusses, hips and jack trusses are simplified to the roof envelope rather than fully replicated from every shop detail.
- RMIT Tools framing overview is used for explanatory context only. House geometry comes from the PDFs.

## Levels and differences retained for review

Ground-floor reference Z=0 corresponds to architectural FFL 10.906. Ground wall height 2.740 m, floor zone 0.400 m, upper floor reference Z=3.140 m, upper wall height 2.590 m. These treat architectural ceiling lines as frame datums; finish thicknesses and any plate/ceiling offsets need coordination. Garage slab is -86 mm; porch is -226 mm.

The structural S10 schedule specifies 300-deep floor joists, while the architectural section shows a 400 mm floor zone and the later supplier sheets specify MSJ-400-45. The model uses the supplier's 400 mm overall zone. The 413 mm shop sketch dimension/camber is not introduced into the straight visual chords. Floor sheeting is omitted for visibility and its thickness has not been coordinated with FFL.

Architectural section 12 shows 450 mm overhang; supplier roof sheets show 550 mm. The model uses 550 mm. Supplier timber envelope is 20,610 x 7,880 mm; architectural exterior first-floor envelope is 20,810 x 8,080 mm. Cladding is omitted and timber positions are calibrated to the supplier envelope. The roof supplier uses N2 while structural bracing drawings state N1: the model displays the supplied arrangement without resolving this engineering discrepancy.

## Simplifications and unverified details

- Internal wall positions and opening centres are traced rather than surveyed. Some nibs, robe openings and stair-side walls are interpreted. Head clearances and the corner sliding-door support need detailed coordination.
- General wall studs are 90x35 at no more than 450 mm nominal centres; ground bottom plate 90x35, upper bottom plate 90x45, double 90x45 top plates. Jamb stud packs, upper double-bottom-plate conditions and point-load transfer blocks are not exhaustively matched to every engineer callout.
- Steel profile families and nominal depths follow S10; flange/web thicknesses are visual approximations. Inverted-T garage plates use the stated plate sizes. Baseplates, anchor bolts, washers, truss plates and ties are representative, without individual nails, teeth, welds or a complete fastener setout.
- Bracing bays are traced from S18/S19; several short hardboard panels and secondary bays are illustrative rather than exhaustive. Roof batten sections, stair stringers/treads, strongback sizes and unscheduled perimeter rim sections are assumptions.
- Garage/porch truss placement and bearing details, hip-jack intersections, wet-area joist recesses, theatre platform support framing and service penetrations need further detailing. A 2,300 mm wide, 420 mm high theatre seating platform is interpreted from architectural sheet 08; its framing sections are assumed. Wet-area floor recesses are not modeled.
- The slab is a context surface only. Footings, waffle pods, reinforcement, masonry, insulation, cladding, glazing, floor sheeting and roof coverings are excluded.

## Files

`frame_overview.png` and `frame_alfresco.png`: assembled frame previews.
`ground_frame_plan.png` and `upper_frame_plan.png`: overhead framing inspection previews.
`member_inventory.csv`: modeled components with source and approximation metadata.
`wall_setout.json`: editable traced wall/nominal opening data.
`model_checks.json`: dimensions, counts and basic geometry validation.
`../scripts/build_frame.py`: reproducible Blender generator. Run from Blender background mode; it rebuilds the file and renders.
