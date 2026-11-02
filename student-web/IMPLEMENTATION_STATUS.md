# EVOLVE learning experience — implementation status

Updated from Chris Nguyen’s three project discussions recorded on 14 September 2026.

## Current implementation

- Seven-step ground-up teaching sequence: footings/slab, ground floor, ground walls, upper floor, upper walls, roof frame and enclosure.
- Primary waffle-slab teaching overlay with separate surface, pods/ribs, reinforcement and membrane visibility.
- Alternative raised-floor teaching overlay with stumps, bearers, representative bearer joints over supports, joists, sheet flooring and a visible service penetration.
- System switching removes the incompatible foundation system and changes the first two construction stages.
- Vertical exploded view separates floor, wall, roof and enclosure assemblies while the ground system remains anchored.
- Eye-level walkthrough mode provides entry, ground-floor and upstairs viewpoints at a 1.6 m reference height, constrained to the selected floor level, with keyboard and on-screen movement controls.
- Reveal-framing, layer visibility, selection highlighting, reset, prepared viewpoints and detached junction studies remain available.
- Hotspots now identify the component, purpose, connection relationship, drawing/reference basis, supported measurements and review status.
- Existing GLB geometry, audited dimensions and Blender source files are unchanged.

## Source basis and limits

- Building geometry: current exported teaching model and `output/timber_frame/audit/POSITION_AUDIT.md`.
- Architecture: supplied Leichhardt architectural drawing set.
- Structure: supplied engineering drawings, subfloor shop drawings and roof-truss documentation.
- Recordings: Chris’s 14 September 2026 discussions establish teaching priorities and interaction preferences, not structural dimensions.
- Waffle-slab and raised-floor web overlays are relationship diagrams. They do not assert pod spacing, rib or beam sizes, reinforcement schedules, cover, footing sizes, member spans, fixing schedules, penetration zones or soil classification.
- AS 1684, AS 2870, AS 4440 and NCC references require edition, applicability and clause verification before student-facing compliance claims are added.
- Manufacturer imagery must not be redistributed without approval. Connector close-ups currently use project geometry and text explanations only.

## Still unresolved

- Project-verified waffle-slab dimensions, reinforcement, steps, rebates and penetration details.
- Governing raised-floor design, member schedule, footing arrangement, connections and approved service-penetration zones.
- Exact camera collision volumes around walls and stairs; the current walkthrough prevents vertical drift through floors but does not claim full wall collision.
- Detailed connector geometry for tie-downs, roof-truss connectors, wall-to-floor connections and structural steel connections.
- Model corrections listed in the position audit, including W04, garage setout and datum, stair surround, floor-depth conflict, T5/T6 extensions and bracing discrepancies.
- Browser/device acceptance testing for classroom hardware and touch navigation.

## Concise questions for Chris

1. Which engineering sheet/detail should govern the waffle-slab pods, ribs, beams, reinforcement, cover, steps and brick rebates shown to students?
2. Can you provide or approve the raised-floor layout, member schedule and the permitted bearer/joist joint and service-penetration details?
3. Which representative connectors should be modelled first: wall tie-down, roof-truss connector, joist/bearer connection or structural steel connection?
4. Confirm the editions and project applicability of AS 1684, AS 2870, AS 4440 and the NCC references before any clause or compliance text is displayed.
5. Should the current walkthrough prioritise a guided route with collision boundaries, or retain free eye-level exploration with prepared viewpoints?

## Developer requirements

- Preserve the saved Blender assets and audited geometry unless a separately approved model-revision task authorises changes.
- Keep technical statements linked to an identified project drawing or clearly labelled as illustrative.
- Do not package the source PDFs into the public website without permission.
- Run `npx tsc --noEmit`, `node --experimental-strip-types --test lib/*.test.ts` and a static build after interaction changes.
- Verify foundation switching, stages, walkthrough viewpoints, reveal-framing, hotspots and detached-detail return behaviour in a browser before release.
