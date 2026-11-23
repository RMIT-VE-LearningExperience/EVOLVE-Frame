# Continue the Leichhardt Revit model on another PC

Prepared 10 September 2026. Read this before the historical ASTRA_REVIT_HANDOFF.md. Modelling is paused for transfer. The user has authorized proposed architecture, primary structure and detailed individual timber/truss members. Do not restart the build or duplicate existing members.

## Moving and opening

1. Use another Windows PC with Autodesk Revit 2027.2, matching the originating installation (27.2.0.39). The model was saved in Revit 2027. Do not use an older Revit version.
2. Clone/pull `https://github.com/RMIT-VE-LearningExperience/EVOLVE-Frame.git`, branch `main`, on the other PC (or copy this entire folder). The source folder's missing Git metadata was reconnected to that existing repository before committing the Revit work. Keep the four PDFs beside this file. Open `output\revit\Leichhardt_Coordination_Model.rvt`.
3. Architectural view: `03 Building Geometry - Coordination WIP`. Detailed framing view: `04 Timber and Trusses - Coordination WIP`. View 04 was active at the last save. Model geometry and loaded families are in the RVT; the MCP connection is not required just to view/edit the model manually.
4. Source PDF references and existing automation contain the OLD absolute workspace path `C:\Users\Stormtrooper\Git\EVOLVE - Frame`. On a different path, relink source PDFs through Revit's link management and update script/source path literals before running scripts. Check `reference_manifest.json`. Do not move/recalibrate the pinned reference instances when only replacing a file path.
5. Open the project folder in the assistant on the new PC and ask: **Read TRANSFER_HANDOFF.md and output/revit/GEOMETRY_PROGRESS.md. Restore and verify the local Revit MCP connection, inspect the existing model, then continue the remaining geometry. Do not rerun initial creation scripts.** This handoff carries the working state without depending on the availability of this chat on the other PC.

The added portable snapshots support the Revit workstream. Other existing project folders were preserved. Save and close the model before committing or copying it so the transfer captures a stable file and avoids Revit's file lock. Keep the original PC's files until the new copy has been opened and checked. Revit backups and generated local configuration are ignored; the current RVT, PDFs, scripts, manifests, families and portable ZIP payloads must be included in the transfer.

## Connection snapshots inside this repository

`revit-portable/payload/revit-mcp-runtime.zip` contains the tested local Node 22.23.2 Windows runtime, node_modules, package files and read-only connection checker. The restore script extracts it to `%LOCALAPPDATA%\RevitMCP` on the new PC.

`revit-portable/payload/revit-addin-2027.zip` contains `mcp-servers-for-revit.addin` and the `revit_mcp_plugin` folder, including the repaired dynamic C# command and command registry. With Revit closed, run `revit-portable/Restore-Connection.ps1` using the command in its README. It verifies hashes, extracts the add-in to `%APPDATA%\Autodesk\Revit\Addins\2027` and restores compiler tools. It refuses to overwrite an existing installation. Restart Revit and enable Add-Ins > Revit MCP Switch. Handle any Revit load prompt locally. The bridge uses port 8080; no router or firewall changes are needed for a local connection.

The portable connection is a snapshot of a working installation, not yet verified on the destination PC. No sign-in credentials or complete user settings are included. Install/sign in to the assistant separately. Register its Revit MCP server using the destination user's paths if desired; the included helper also connects without native tool-catalog registration:

```powershell
& "$env:LOCALAPPDATA/RevitMCP/node-v22.23.2-win-x64/node.exe" "$env:LOCALAPPDATA/RevitMCP/verify-connection.mjs"
```

Once this read-only check succeeds, use `scripts/revit_call.mjs` for dynamic commands. It launches the local MCP server. C# snippets use explicit transactions (`transactionMode: none`). The bridge has a single-read buffer: requests must remain below 7,800 bytes. Execute ONE command at a time. If a command times out or a modal appears, inspect Revit and the model before retrying: a timed-out command may still commit.

## Compiler dependencies and path handling

`revit-portable/payload/revit-compiler.zip` restores `tmp/revit-compiler/` with portable Roslyn, the repaired bridge DLL and modelling helper DLLs. The archive is included despite `tmp/` being ignored by Git. Existing helpers V1/V2 embed the original project path. Run `revit-portable/Prepare-Workspace.ps1` to update source path literals, then compile a NEW helper assembly name before invoking helpers on a different path. Update the wrapper scripts to match. Revit keeps loaded assemblies; overwriting a loaded DLL does not reload it. Workspace preparation does not change the PDF links stored inside the RVT.

The build scripts currently reference Revit 2027 and .NET runtime 10.0.9 under Program Files. Inspect the destination runtime and adapt these paths to an installed compatible .NET 10 runtime. Do not copy Revit or .NET application directories from the old PC. Revit family templates were under `C:\ProgramData\Autodesk\RVT 2027\Family Templates\English`.

The Python generators use the packages listed in `revit-portable/requirements.txt`. They are not needed to open the saved RVT. Install them in a suitable destination Python environment before regenerating. `build_floor_web_manifest.py` also searches `tmp/python_geom_lib`, but normal installed packages work when that directory is absent. Existing generated manifests are included.

## Current geometry and exact next work

See `output/revit/GEOMETRY_PROGRESS.md` for counts, modelling assumptions, missing scope and verification limits. See `output/revit/DISCREPANCY_LOG.md` for source conflicts. These supersede reference-only status in older notes.

Most recent fix: FootPrintRoof.SlopeAngle takes rise/run, not radians (confirmed in installed RevitAPI.xml). Creation scripts now use `Math.Tan(angle)`. All three existing roof pitches were corrected and saved. The updated architectural PNG was visually checked: main trusses no longer project through the roof skin.

Next: create an isolated floor-framing 3D review view and inspect physical joist/web solids; broaden the audit from axes/type dimensions to actual solid dimensions/roll orientation and joins. Continue coordinated primary beams/columns, foundations, stairs, strongbacks, bracing/ties, piers/parapets and finish interfaces as source evidence permits. The source hierarchy and discrepancy handling remain binding. Do not claim this WIP is fully coordinated or fabrication-ready.

Initial wall/floor scripts have creation guards. `revit_correct_ground_suite.cs` deletes/recreates targeted walls and would now delete hosted inserts: do NOT rerun blindly. Roof, wall-frame, floor-frame, web and opening placement scripts generally skip existing marks; still inspect them before use. `revit_fix_wall_view.cs` is obsolete (old garage endpoint and creates a duplicate view). Latest garage partition endpoint is Y7940; access door centre is Y4160, not Y4400.

Primary steel setout remains unresolved: S09 calibrated portal axis is approximately X12733, while supplier dimension chain suggests X12714.5. Do not silently treat this 19 mm discrepancy as exact structural positioning. Foundations have geotechnical founding conditions with unknown absolute depths. Stair dimensions differ between floors. These items need further source coordination, not an invented solution.
