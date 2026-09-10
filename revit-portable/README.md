# Revit connection files carried by this repository

Start with [TRANSFER_HANDOFF.md](../TRANSFER_HANDOFF.md). This directory holds compressed snapshots of the tested local MCP runtime, Revit 2027 add-in including the compiler repair, and portable Roslyn/modelling helpers. `payload/SHA256.json` records archive checksums. No account credentials or user configuration are included.

On a fresh destination PC, install Revit 2027.2 and close it, then run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File revit-portable/Restore-Connection.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File revit-portable/Prepare-Workspace.ps1
```

The restore refuses to overwrite an existing connection or compiler folder; inspect/merge an existing installation separately. `-CheckOnly` validates without writing. Workspace preparation updates old source paths; it does not relink Revit PDFs or rebuild DLLs. Follow the handoff for both. Restore writes a local MCP configuration snippet for this PC without changing existing assistant settings.

Open `output/revit/Leichhardt_Coordination_Model.rvt`, enable the Revit MCP Switch, then run:

```powershell
& "$env:LOCALAPPDATA/RevitMCP/node-v22.23.2-win-x64/node.exe" "$env:LOCALAPPDATA/RevitMCP/verify-connection.mjs"
```

The RVT and family files open without Python. Python regeneration requires `requirements.txt`; Revit and .NET themselves must be installed on the destination PC. Bundled components retain their included license files. The snapshot is tested on the source PC; destination compatibility must be verified there.

Do not rerun `scripts/prepare_revit_transfer.py` on the new PC until its connection is correctly installed: that maintenance script rebuilds these snapshots from the current PC's installation.
