# EVOLVE Frame / Frame Lab

**Current Revit work / move to another PC:** read [TRANSFER_HANDOFF.md](TRANSFER_HANDOFF.md), then [geometry progress](output/revit/GEOMETRY_PROGRESS.md). The saved model is `output/revit/Leichhardt_Coordination_Model.rvt`. Tested connection snapshots and destination restore scripts are in [revit-portable/](revit-portable/README.md). The sections below describe the separate educational Blender/website workstream.

An educational Blender model and student-facing construction explorer for the Leichhardt project.

**Public student experience:** https://leichhardt-frame-lab.lawrence-makoona.chatgpt.site

## Project contents

- `student-web/`: complete website source, model exports, learning content and tests. See its README for development instructions. The live site is now public; owner-only access described there was the initial review setting.
- `output/learning/Leichhardt_Learning_Experience.blend`: latest learning revision with detached window, eaves and floor-edge junctions, plus staged building views.
- `output/learning/LEARNING_GUIDE.md`: teaching prompts, sources and limitations.
- `output/enclosure/`: provisional enclosure revision and material assumptions.
- `output/timber_frame/audit/POSITION_AUDIT.md`: discrepancies held for Chris's review.
- `scripts/`: model generation, auditing and rendering tools.

The original project PDFs and initial model remain in their existing locations. The website does not distribute the PDFs.

## Learning status

This is a provisional teaching model, not a construction specification. Frame positions and unresolved drawing conflicts remain flagged for teacher review. Junction dimensions, products and installation details are illustrative unless explicitly identified otherwise. The building's existing geometry is preserved in the learning revision.

The construction-stage sequence is a teaching reveal order, not an approved site programme. Classroom release should include teacher review and browser/device testing.

## Source and hosting

This GitHub repository contains the full website source as ordinary files, not a submodule. Sites hosts the current public student experience. The local website also retains its separate Sites source history; changing GitHub alone does not automatically publish a new website version.

Local Blender backup files, dependencies, generated website builds and temporary deployment archives are excluded from version control.
