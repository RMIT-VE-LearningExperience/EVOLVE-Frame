# Leichhardt

An educational Blender model and student-facing construction explorer for the Leichhardt project.

**Public student experience:** https://rmit-ve-learningexperience.github.io/EVOLVE-Frame/

Standalone **Leichhardt 0.4.6** APKs are also available for PICO 4 Ultra Enterprise and Meta Quest 3/3S. See [the Unity project](unity-vr/README.md) for the current build, validation scope and architectural limitations. Quest 3 is installed and passed automated checks plus basic wearer confirmation; Quest 3S hardware testing remains pending. [Private model review gallery](https://leichhardt-model-review.lolepaille.chatgpt.site/) contains 83 Unity images.

## Project contents

- `student-web/`: complete website source, model exports, learning content and tests. See its README for development instructions. GitHub Pages publishes the public classroom version from the tested static export.
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

This GitHub repository contains the full website source as ordinary files, not a submodule. GitHub Actions builds and publishes `student-web` to GitHub Pages when relevant files change on `main`. A separate private Sites deployment may be used for owner review, but it is not the public classroom URL.

Local Blender backup files, dependencies, generated website builds and temporary deployment archives are excluded from version control.
