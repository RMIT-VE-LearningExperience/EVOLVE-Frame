# Leichhardt timber frame

Open `Leichhardt_Timber_Frame.blend` in Blender 5.0 or later. The building opens with exposed timber framing, required steel supports and connections. The optional slab context is hidden. Individual framing members are named and editable. Model units are metres with millimetre dimension display.

Use the View Layer dropdown at the top right to switch between Complete frame, Ground framing only, Floor structure, Upper walls and Roof structure. These views include only the appropriate storey's connections. The presentation ground, lights and cameras are hidden in the modelling viewport, but available for rendering. The two architectural plan images are packed into the hidden reference collection.

The four PDFs in the project are the drawing basis. The RMIT framing overview provides visual context for studs, noggings, plates, trusses, bracing and ties:
https://rmit.buildingtools.co/tools/structure-framing-overview-timber?zoom=0.8162978768908519&shareId=0eVwmY-1788744053352&menu_id=8-3-0&x=474.3952100893788&y=331.74745575048047

This version continues the existing project model. It restores the missing reference-image preparation step, provides a frame-only default, separates connections by storey, and fixes the inspection layers so isolated floor and upper-wall views no longer retain unrelated lower walls or overhead connections. The original Blender file remains in the parent output directory.

The primary model dimensions remain: ground walls 2740 mm, upper floor datum 3140 mm, upper walls 2590 mm, roof span 7880 mm, main roof pitch 25 degrees and nominal overhang 550 mm. These are visual frame datums derived from the drawing sets; finish build-ups are not coordinated.

The detailed scope and assumptions are in `../README.md` and embedded in the Blender text block `START HERE - Model scope and drawing differences`. Corrections to those earlier notes: floor strongbacks are explicitly scheduled 140 x 35 mm on the last subfloor PDF page; their line positions remain approximate. The floor shop sheets label MSJ-400-45 but draw 413 mm overall depth, while the layout calls for 413/360 mm members and the architectural section shows a 400 mm floor zone. The current straight visual model retains 400 mm pending coordination; the 13 mm difference must not be treated as verified camber. Recessed shower members and detailed special hip trusses remain simplified.

This is a drawing-based visual model, not a fabrication or structurally verified model. No finishes, glazing, cladding or roof covering are included. Steel supports and metal webs remain because they are part of the supplied frame design.

## Rebuild

From the project directory in PowerShell:

```powershell
uv run --with pymupdf python scripts/prepare_references.py
& 'C:/Program Files/Blender Foundation/Blender 5.0/blender.exe' --factory-startup --background --python scripts/build_frame.py
```

Outputs include the Blender asset, two perspective previews, two plan previews, member inventory, wall setout and model check report. Rebuilding replaces outputs within this directory only. Source PDFs and the original parent-directory model are retained.
