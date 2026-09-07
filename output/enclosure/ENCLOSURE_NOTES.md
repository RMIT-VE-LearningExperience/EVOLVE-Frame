# Enclosure preparation - Leichhardt

Open `Leichhardt_Enclosure_Study.blend`. This continues the saved stair-corrected frame with its geometry preserved. It is a provisional enclosure study while Chris reviews the positioning audit; it is not a coordinated construction or product specification.

## Views

- **06 Enclosure - cutaway** opens by default: selected exterior layers are removed to show the timber frame.
- **07 Enclosure - assembled** shows the provisional main enclosure.
- **08 Enclosure - wrap stage** shows the frame with membrane layers, before external skins.
- Existing frame inspection views remain available and exclude the new enclosure objects.
- Switch the Scene dropdown to **02 Assembly studies** for four exploded examples: brick veneer wall, upper foam/render wall, roof and floor. Press Numpad 0 (View > Cameras > Active Camera) to see the composed study view.

Collections beginning `20` through `29` separate the construction layers. Their children distinguish the removable cutaway portions. Objects have source, specification-status and associated-frame metadata. `ENCLOSURE_CONFIG.json` records editable settings used by the generator. Named window/door roots allow whole opening assemblies to be moved together.

## Material register

| Layer | Drawing basis | Model treatment |
|---|---|---|
| Main roof | Architectural 03/09/10/12: selected Colorbond, 25 degrees, roof sarking | Generic charcoal metal appearance and schematic ribs. Manufacturer profile, sheet gauge and colour are not selected. Existing supplier-based 550 mm overhang retained pending Chris's review of the 450 mm architectural overhang. |
| Roof sarking | Architectural 12 | Separate thin visual membrane; its 1 mm display thickness is illustrative. |
| Fascia and gutters | Architectural 09/10/12: selected Colorbond | Simplified main-roof fascia and open gutter channels. Profiles, falls, outlets and downpipes are not designed. |
| Ground-floor skin | Architectural 07/09/10/12: face brickwork, nominal 240 mm exterior wall | Provisional 110 mm brick leaf and 40 mm cavity around the existing 90 mm frame. The leaf/cavity split is a modelling assumption to match 240 mm total, not an explicitly verified wall detail. Mortar and brick colours are illustrative. |
| Upper skin | Architectural 08/09/10/12: 100 mm foam with rendered finish | 100 mm external layer, light rendered appearance. Render is represented by the surface material, not an additional assumed build-up. Product, fixings and junction details await specification. |
| Wall wrap | Prepared enclosure component; final wall-system documentation required | Separate visual membrane at the outer frame face. Product, vapour properties, continuity and thickness are unselected. |
| Windows | Architectural 11 | Editable aluminium/glass proxies fitted to the CURRENT model openings, not shop drawings. Frame sections, glazing thickness and detailed opening operation are illustrative. W04 stays in the audited frame position pending Chris; its root is explicitly tagged. |
| External doors | Architectural 11 | Editable proxies for D01-D04. Detailed hardware and installation clearances are not specified. Alfresco D05 is withheld pending corner-opening coordination. |
| Internal lining | Architectural 12: 10 mm plasterboard | Included in the detached wall and floor assembly studies, not installed throughout the house. |
| Upper floor sheeting | Subfloor layout PDF page 47: 3600 x 900 x 19 | 19 mm panel example in the detached floor study. Full house decking is withheld until the 400/413 mm floor zone and finish levels are coordinated. |
| Insulation | Architectural 02/12: selected wall and ceiling insulation; energy report governs | Illustrative infill in the wall study only. No R-value, product or performance is claimed. |

## Held for Chris

The audit at `../timber_frame/audit/POSITION_AUDIT.md` remains the reference. No audited frame member was moved or resized here. Garage/porch roof coverings, full floor sheeting and the D05 corner glazing are deliberately not fitted: their bearings, extents or levels depend on the unresolved findings. The provisional brick/foam panels and window proxies follow existing positions and must be refitted after corrections.

The main ground-floor skins extend over the current 400 mm floor edge to the upper-wall datum. That continuity is provisional until the floor build-up is resolved. In the detached assembly scene, partial panels and expanded gaps intentionally expose the underlying layers; exploded gaps are not installation dimensions.

The original slab remains optional context. Footings, reinforcement, masonry piers/parapets, rendered blueboard packing, cavity flashings, weep holes, wall ties, window flashings, weather seals, downpipes, service penetrations and final waterproofing details are not completed by this study. An assembled exterior view is not a claim that the building is weather-tight.

## Next actions

1. Chris confirms the coordinate/dimension basis and the items in the position audit.
2. Correct the frame in a new revision, then regenerate the enclosure against that revision.
3. Confirm brick/cavity details, foam system, insulation specification, roof profile/colour and opening products.
4. Fit the deferred deck, low roofs, D05 opening and the remaining enclosure junctions.

## Rebuild

Run `scripts/build_enclosure.py` in Blender background mode while loading the stair-corrected source file. It creates a new enclosure output, verifies that all source mesh geometry is preserved, and packs these notes in the Blender text editor. Render `scripts/render_enclosure.py` with `-- cutaway`, `-- assembled`, or `-- studies` in separate background processes.
