# Revit MCP connection

Verified on 10 September 2026. This supersedes the connection limitation recorded in ASTRA_REVIT_HANDOFF.md.

## Current status

- Revit 2027.2 is open with `output/revit/Leichhardt_Coordination_Model.rvt`.
- The existing mcp-servers-for-revit add-in is enabled through Add-Ins > Revit MCP Switch.
- Codex's user configuration registers a STDIO server named `revit`.
- MCP initialization and tool discovery passed: 26 tools.
- Live read-only calls `get_current_view_info` and `analyze_model_statistics` both passed.
- Initial read-only checks returned L1 - Architectural and two template levels. The statistics tool reports elevations in internal feet.
- The user subsequently authorized modelling and explicitly included detailed timber and truss members.
- The coordination reference checkpoint is saved: five architectural levels, seven coordination grids, sixteen source views and eighteen pinned PDF instances. Saved review view: 04 Timber and Trusses - Coordination WIP.
- Building geometry is now saved: see `output/revit/GEOMETRY_PROGRESS.md`. The repository includes portable connection snapshots in `revit-portable/payload`; start with `TRANSFER_HANDOFF.md` on another PC.

## Dynamic command repair

The installed dynamic compiler originally included duplicate Autodesk assemblies from multiple Revit load contexts. A dedicated `EvolveRevitCodeCommand.dll` deduplicates metadata references by assembly name. Source and reproducible compilation script are in `scripts/revit_bridge/`. Only the `send_code_to_revit` registry entry was redirected; the original registry is backed up as `commandRegistry.json.before-compiler-fix.bak` beside it.

The local MCP tool schema/forwarder now accepts `transactionMode` (`auto` or `none`). This permits read-only code, explicit transaction ownership and SaveAs outside a transaction. Live preflight, SaveAs, datum/grid transactions, PDF linking, coordinate transforms and view exports passed on Revit2027.2. The helper `scripts/revit_call.mjs` detects nested command failures and limits requests to the bridge's single-read buffer. Reinstalling the upstream npm package may overwrite the transaction-mode patch.

## Installed components

- Add-in: `%APPDATA%/Autodesk/Revit/Addins/2027/mcp-servers-for-revit.addin`
- Server: `%LOCALAPPDATA%/RevitMCP/node_modules/mcp-server-for-revit/build/index.js` (version 1.0.0)
- Dedicated runtime: `%LOCALAPPDATA%/RevitMCP/node-v22.23.2-win-x64/node.exe`
- Config: `%USERPROFILE%/.codex/config.toml`, table `[mcp_servers.revit]`
- Config backup: `%USERPROFILE%/.codex/config.toml.before-revit-20260910-141016.bak`
- Read-only verification client: `%LOCALAPPDATA%/RevitMCP/verify-connection.mjs`
- Verification report: `%LOCALAPPDATA%/RevitMCP/connection-check.json`

The dedicated Node 22 runtime was needed for the package's better-sqlite3 dependency. Its archive was checked against Node's published SHA256 checksum. The system Node installation was unchanged.

## Reconnect and verify

Keep Revit and the intended project open. If the bridge is not listening, enable Add-Ins > Revit MCP Switch. It uses local TCP port 8080. The installed bridge was observed listening on 0.0.0.0; no firewall rules were changed by the agent. Windows security prompts must be handled by the user.

Restart the Codex extension to load the newly registered server into its tool catalog. The already-tested local MCP client can also access it without an extension restart:

```powershell
& "$env:LOCALAPPDATA/RevitMCP/node-v22.23.2-win-x64/node.exe" "$env:LOCALAPPDATA/RevitMCP/verify-connection.mjs"
```

This verification script only discovers tools and queries the active view and model statistics. The repaired dynamic command was separately verified during the authorized reference build. Discovery alone does not verify the remaining commands on Revit2027.

## Documentation

- [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Revit MCP upstream](https://github.com/mcp-servers-for-revit/mcp-servers-for-revit)
