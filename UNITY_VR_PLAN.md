# Leichhardt standalone VR build plan

Planning baseline dated 20 November 2026.

Build a standalone Android APK for PICO 4 Ultra Enterprise in Unity with URP. Students enter the Leichhardt house at full scale, learn the controls through a short introduction, and explore the building and its construction layers. Visual priorities are convincing daylight, readable materials, comfortable movement and coherent construction details.

## Latest authoring and budget decisions

The user authorises remodelling, re-skinning and use of Blender, Revit and Unity wherever they improve the result, including lighting bakes. Use installed tools and free assets; no purchases, new subscriptions or usage overage. The authorised narration uses the existing included ElevenLabs allowance, after a quota and overage preflight. The drawings remain the geometry reference. Preserve existing source revisions and make a separate VR model revision.

Blender is the primary geometry tool. Unity URP, the GPU lightmapper, OpenXR/XR Interaction Toolkit and the PICO SDK cover rendering and interaction. The latest environment replaces grass and HDR sky with plain ground, a texture-free sky gradient and inexpensive horizon fog. The palette takes cues from the user's Build Your Path Unity project: warm cream, natural timber and amber controls. Revit and free ProBuilder remain optional tools.

The first new Blender revision corrects W04 to the schedule (905 mm sill, 514 mm high, 1419 mm head), refits its framing and enclosure, removes the generic centre mullion from the fixed light, and exports 0.8 mm timber edge bevels. Other audit items remain open.

The 0.2.0 implementation adds interior wall linings and opening returns, removable ceilings, and an upper deck retaining the stair void. Walls and roof have separate controls; floors remain visible. Enclosed and exposed-wall lighting are baked separately and switched with wall visibility. There are 22 named room/overview destinations across both levels, plus a detached window study. Each destination has floor-support and clearance checks. The full Clara tour starts automatically and narrates each arrival; Next and the room list control movement. A side guide leaves the window centre clear and has a separate persistent Menu recall button. See `unity-vr/README.md` and its test outputs for the current implementation; the remaining sections retain the broader release plan.

## Agreed direction

| Item | Direction |
| --- | --- |
| Target hardware | PICO 4 Ultra Enterprise with controllers |
| Delivery | Standalone APK with the model and experience packaged locally |
| Engine | Unity with URP and OpenXR, using a compatible PICO integration |
| Model authoring | Blender source assets, with corrections and exports tracked by revision |
| Experience | Narrated room-to-room tour with direct room selection and optional narration |
| Navigation | Validated room destinations with short fades and 30-degree snap turns |
| Accuracy | Believable full-scale geometry and correct teaching relationships, with priority given to visible discrepancies and close-up details |
| Overlap requirement | Resolve unintended geometry intersections, duplicate surfaces, flickering faces, overlapping interface panels and obstructed movement |
| Current visual treatment | Warm-neutral daylight without a yellow cast, baked soft shading, pale timber, plain ground and a soft misty horizon |
| Classroom operation | Confirmed independent headset sessions lasting 10–15 minutes |
| Guided content | Confirmed short on-screen prompts with optional narration, supported by captions |

Each student controls their own route and pace. Plan approximately two minutes for the introduction and eight to thirteen minutes for guided stops and free exploration. Keep narration optional and make every required instruction available as text. Revit becomes useful if an editable BIM model becomes a deliverable.

## Student journey

1. Start outside the entry at a comfortable standing or seated height. Present Start, comfort settings and a clear reset action.
2. Spend approximately two minutes learning to point, select, teleport and snap turn. Let experienced users skip the introduction. Use headset tracking for eye height and provide seated calibration.
3. Enter the living area and encounter the first teaching stop. Reveal a selected wall assembly and identify its framing and enclosure layers.
4. Open a detached window detail at a comfortable inspection distance. Select a component, read its purpose and connection, then move the assembly between assembled and exploded positions.
5. Return to the saved building location and orientation. Offer an upstairs destination and allow further exploration.
6. Provide Home and Reset session from every mode so a teacher can prepare the next student quickly.

The proposed introduction covers the entry, living area, wall reveal, window study and upstairs viewpoint. Text appears when needed for an action or selected component. A single information panel handles the current selection. Narration, if included, has replay, mute and captions.

Narration will use ElevenLabs. The initial voice selection is Clara, listed as Australian Professional Female with Warmth & Trust. Direct the delivery toward a neutral Australian accent, friendly conversational tone and measured teaching pace. The user approved the short Clara introduction sample on 20 November 2026; retain that voice and delivery for subsequent reviewed scripts. [ElevenLabs Australian voices](https://elevenlabs.io/text-to-speech/australian-accent).

Store the development credential in the Git-ignored root file `.env.narration.local` under `ELEVENLABS_API_KEY`. The narration generation tool will load this file locally. Generate reviewed audio clips during development and include those clips in the APK for offline playback. Keep the credential in the development environment. [ElevenLabs API authentication](https://elevenlabs.io/docs/api-reference/authentication).

## Scope by milestone

| Milestone | Deliverable | Completion evidence |
| --- | --- | --- |
| 1 Headset foundation | Small APK with a correctly scaled test area, controllers, menu, teleport and snap turn | Installs and launches on the target headset, renders correctly in both eyes, accepts input, resumes after sleep and works offline |
| 2 Model preparation | Revised route geometry, export manifest, collision surfaces and overlap findings | Entry and living-area route has coherent floors and openings, correct scale and axes, and resolved visible clashes |
| 3 Visual prototype | Polished entry-to-living route, an upstairs teleport destination, one wall reveal and the window study | Lighting, material clarity, navigation and reveal transitions work on the headset within the performance target |
| 4 Building exploration | Both storeys, completed required enclosure, layer controls and the remaining eaves and floor-edge studies | Every accessible route and teaching state passes the geometry, interaction and visibility checks |
| 5 Classroom pilot | Installable release APK, reset flow, brief teacher instructions and test record | Representative first-time users can complete the introduction and explore, followed by a sustained headset test |

The user requested that visual quality be brought forward after reviewing the first flat-colour preview. Establish the sky, ground, material scale and neutral daylight now, and review actual Unity renders before extending the scene. Milestone 1 establishes the toolchain while the route geometry is reviewed. Lighting production follows corrections to the surfaces being baked. Milestone 3 is the visual review point before extending materials and lighting across the house. Set calendar estimates after measuring that prototype's asset preparation and headset optimisation work.

The seven existing teaching stages are the starting content sequence for milestone 4. Foundation alternatives and whole-building explosion need their own navigation and lighting treatment. Introduce those as stationary inspection views after the primary walkthrough works, subject to the same accuracy review as the other teaching content.

## Model preparation and accuracy

The saved learning Blender file is the initial authoring candidate. Its modification time is later than the current web export, so inspect and compare them before choosing the baseline. Record the source revision and export hash with each generated asset. Existing room setout, member roles, source references and approximation notes provide the basis for corrections. [Learning guide](output/learning/LEARNING_GUIDE.md) and [position audit](output/timber_frame/audit/POSITION_AUDIT.md).

| Priority | Work | Required before |
| --- | --- | --- |
| Route surfaces | Complete the walkable floor, align thresholds and check doorway clearance | First building walkthrough |
| W04 kitchen opening | Resolve the recorded 514 mm sill discrepancy and refit connected framing and enclosure | Living-area visual prototype |
| Stair and landing | Coordinate the flight, dwarf wall, void edge, trimmer and supporting geometry using a consistent drawing basis | Opening the stair route to smooth movement |
| Garage | Coordinate slab datum, wall base and roof bearing, and review its connected wall setout | Garage access |
| Upper floor levels | Resolve the 400/413 mm floor-depth conflict together with finishes and stair landing heights | Final upstairs geometry and lighting bake |
| Enclosure | Complete the required decking, interior lining, low roofs and D05 opening for accessible areas | Full-building visual review |
| Roof and bracing | Review T5/T6 extensions, bearings, bracing bays and conspicuous gaps or intersections | Roof and framing teaching views |
| Close-up studies | Check the visible order, support and weathering relationships of the window, eaves and floor edge | Student pilot |

A minor setout difference may remain in the pilot when it causes neither a visible defect nor an incorrect teaching relationship. Conflicting drawings require a recorded governing basis for the affected assembly. Progress can continue elsewhere while that basis is resolved. Keep dimension labels tied to verified measurements. Use the existing review form to collect the outstanding coordination decisions. [Chris review form](output/Chris_Model_Review_Response_Form.docx).

## Geometry and overlap acceptance

Treat an overlap as a defect when it represents an unintended intersection, duplicate surface or obstruction. Construction joints and bearing connections need an explicit interpretation of the intended contact. Bounding-box intersections can identify candidates for inspection, and mesh-level checks and visual review establish which candidates need correction.

- Check duplicate objects and coplanar faces, wall junctions, openings, floor edges, roof bearings and enclosure interfaces.
- Check assembled, cutaway and exploded states, including intermediate animation positions. Adjust travel paths where parts pass through unrelated geometry.
- Build lightmap UVs with adequate padding and unique islands. Inspect for light leaks, seams and dark patches near wall junctions.
- Test teleport destinations using the player's clearance volume, floor support and distance from void edges. A visible destination indicator must agree with where the player lands.
- Review each accessible room and all close-up studies from several angles at headset scale. Check both eyes for flicker, clipping and transparent-surface artefacts.
- Keep the active menu and information panel at a readable distance. Hide obsolete labels on selection changes and reposition panels that intersect nearby geometry.

Record each defect with its object or assembly, state, location, screenshot and resolution. Completion requires zero unresolved visible unintended clashes along accessible routes and in teaching views, plus repeatable checks of the export. This criterion is evaluated against the implemented scenes and test coverage.

## Visual treatment and lighting

Use a coherent afternoon sun direction, warm sunlit surfaces and softer, cooler ambient fill. Maintain readable interior shadow detail and natural material colours. Windows should feel bright while their frames remain legible. Add restrained outdoor ambience and subtle selection feedback to support the setting.

Prepare timber grain at a believable scale, brick coursing aligned to the walls, rough plaster and render, and controlled metal and glass reflections. Use shared materials and efficient texture maps. Small bevels are worthwhile on close-up objects where they improve the silhouette and catch light. Judge material detail at normal viewing distance inside the headset.

Bake indirect light for the stable enclosed walkthrough and use reflection probes and a limited dynamic lighting contribution where needed. The current GLB contains one material UV set, so prepare and validate a second UV set for lightmaps before the production bake.

For the first reveal, test the exposed wall with a lighting treatment that remains plausible after its enclosure is removed. Baked shadows from a hidden wall persist unless its lighting data changes. Prototype an exposed-frame view with its own lighting data and a neutral, readable setup for freely changing construction stages. Detached detail studies can use their own fixed inspection lighting. Compare memory and transition cost before choosing how to load and switch the lighting data.

Keep the mobile rendering baseline lean, with Forward rendering, stereo single-pass or multiview where supported, and MSAA. Begin with 2x MSAA and compare 4x in the headset. Profile Vulkan and the selected PICO runtime together. Add optional rendering effects only when measured cost and visible benefit justify them. [Unity untethered XR guidance](https://docs.unity.com/en-us/engine/6000.0/manual/xr/graphics/untethered-device-optimization).

## Navigation and state changes

Maintain explicit states for introduction, walkthrough, construction inspection, detail study and pause. Each transition updates visible geometry, lighting, collision, available destinations, selection and interface together. Save the building pose and teaching state before opening a detail, and restore them on return.

Teleport uses validated surfaces and destinations. Start with 30-degree snap turning as a tunable default. Provide comfort settings for turn increment and optional smooth movement with adjustable speed and vignette. Test stairs using a smooth collision ramp once the visible stair assembly is coordinated. Keep head tracking responsive during all movement.

A physical lean can take the tracked head through a virtual wall even when controller movement is blocked. Fade the view as the head enters obstructing geometry and restore it on exit. Preserve the headset's own boundary behaviour.

When a teaching stage removes a floor or creates a void, move the user with a brief fade to a validated viewing area before changing that stage. Provide visible support beneath the user and match movement boundaries to the current presentation. Whole-building explosion belongs in a stationary overview or model inspection mode. The user can then return to full-scale exploration.

## Asset and application structure

Proposed project location is `unity-vr/`. The authoring flow is source drawings and reviewed Blender geometry, followed by a repeatable export, Unity import, scene assembly, lighting bake and APK build.

The existing building GLB contains 37 meshes, 13 materials and 88,532 triangles. Use it for the initial import and performance baseline. It batches many members together, so retain stable component identifiers and rebuild export grouping for interactive assemblies. Batch static surfaces by location, material and visibility behaviour. Keep selected teaching parts independently addressable. Whole-house batches can limit culling and precise selection.

Use glTF or FBX through a tested editor import path, with explicit scale, axis, normals, material and metadata checks. Package imported assets in the APK. Recreate the web experience's teaching data and interactions in Unity, including the foundation overlays that are currently generated by web code. [Web implementation status](student-web/IMPLEMENTATION_STATUS.md).

The Unity project should contain the XR rig and locomotion, building presentation, teaching content, detail scenes and a small session controller. Content records hold the component identifier, title, purpose, connection, source basis, review status and optional detail destination. Simplified collision meshes are authored alongside the visible model. Data-driven visibility groups allow a model revision to retain its teaching behaviour.

## Toolchain and build setup

Local inspection found Unity 2022.3.19f1, 2022.3.62f2, 6000.1.9f1 and 6000.6.9f1, each with an Editor executable and Android, ADB, NDK and OpenJDK paths. Blender 5.0 is also present. These checks establish installed files. Editor activation, SDK compatibility and a successful Android build still need verification in milestone 1.

Select and pin a supported Unity 6 editor, URP, XR Interaction Toolkit, Unity OpenXR and PICO package combination after a device smoke test. Check a supported Unity 6 LTS option during selection. Record the headset firmware alongside the locked project versions. PICO's Integration SDK release history documents Unity 6 and OpenXR support, while exact combinations require validation. [PICO SDK releases](https://github.com/Pico-Developer/PICO-Unity-Integration-SDK/releases).

Build for Android ARM64 with IL2CPP using the selected SDK's Android API requirements. Validate the controller profile, tracking origin, graphics API and application lifecycle. Check the resulting package on the actual Enterprise headset before adding substantial scene content.

For distribution, use a stable application identifier, version code and release signing key. Keep signing credentials outside source control and document who holds the key so later APKs can update existing installations. The first delivery can use local installation through PICO Developer Center or ADB. Fleet distribution depends on the institution's existing device management process.

## Performance and release checks

The PICO 4 Ultra Enterprise specification lists a 90 Hz display. Use native 90 fps as the proposed visual prototype target, giving roughly 11.1 ms per frame. Measure application CPU and GPU frame times independently and retain headroom for the runtime. Begin with a target of 95th-percentile CPU and GPU times below 10 ms during exploration, then examine missed frames and transition spikes. These are project targets to validate on hardware. [PICO hardware specifications](https://business.picoxr.com/us/products/pico4-ultra-enterprise/specs).

Set detailed texture, lightmap, draw-call and memory budgets using the measured prototype. Profile the assembled interior, exposed frame, transparent windows, exploded detail and state transitions. A full frame reveal can expose more geometry than the finished building. Occlusion settings must remain valid when walls disappear.

Release acceptance covers the following checks.

- Install, cold start and offline use on the target headset.
- Complete the introduction and reach every intended location with controllers.
- Enter and leave every teaching state, return from details and reset the session.
- Maintain correct geometry, lightmaps, reflections and selection through visibility changes.
- Verify standing and seated calibration, teleport clearance, optional smooth movement and head-obstruction behaviour.
- Test tracking loss, controller disconnection, headset removal, sleep and resume.
- Run for at least 30 minutes, including repeated route and teaching-state changes, and inspect frame timing, thermal behaviour and memory growth.
- Observe representative new users completing the introduction, finding the next destination and recovering through Home or Reset.
- Test the release APK as well as the development build, including update installation with the intended signing key.

The pilot deliverables are the APK, versioned Unity project, reviewed source/export revision, concise installation and reset instructions, and a test record identifying remaining visible limitations.

## Next implementation tasks

1. Confirm the headset firmware and development connection, select the package versions and build the minimal headset foundation.
2. Compare the current saved learning model with the GLB export and establish the source revision.
3. Audit the entry and living-area route for visible geometry defects, then resolve its floors, openings and collision surfaces.
4. Prepare materials and lightmap UVs for that route and build the first daylight treatment.
5. Add the wall reveal and window study, including consistent lighting and return behaviour.
6. Test the APK on the headset and use the results to set the production budgets and remaining schedule.

Independent use, 10–15 minute sessions and optional narration are confirmed requirements. Headset access is the main external dependency for accepting milestones 1 and 3. Drawing decisions affect the specific assemblies listed above and can be collected as those areas enter production.
