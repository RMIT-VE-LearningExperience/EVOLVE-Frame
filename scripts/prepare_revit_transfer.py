"""Snapshot the working local Revit connection into this repository (no credentials)."""
from pathlib import Path
import os, zipfile, hashlib, json, re

root = Path(__file__).resolve().parents[1]
dest = root / 'revit-portable' / 'payload'
dest.mkdir(parents=True, exist_ok=True)
local = Path(os.environ['LOCALAPPDATA']) / 'RevitMCP'
addin = Path(os.environ['APPDATA']) / 'Autodesk/Revit/Addins/2027'

def files(base, prefix='', exclude=lambda p: False):
    return [(p, (Path(prefix) / p.relative_to(base)).as_posix())
            for p in base.rglob('*') if p.is_file() and not exclude(p)]

sets = {
    'revit-mcp-runtime.zip':
        files(local / 'node-v22.23.2-win-x64', 'node-v22.23.2-win-x64') +
        files(local / 'node_modules', 'node_modules') +
        [(local / n, n) for n in ['package.json', 'package-lock.json', 'verify-connection.mjs']],
    'revit-addin-2027.zip':
        [(addin / 'mcp-servers-for-revit.addin', 'mcp-servers-for-revit.addin')] +
        files(addin / 'revit_mcp_plugin', 'revit_mcp_plugin',
              lambda p: 'Logs' in p.parts or p.suffix in ['.bak', '.pdb'] or '2026' in p.parts),
    'revit-compiler.zip':
        files(root / 'tmp/revit-compiler/toolset', 'toolset') +
        [(p, p.name) for p in (root / 'tmp/revit-compiler').glob('Evolve*.dll')],
}
inventory = []
for name, entries in sets.items():
    path = dest / name
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for source, archive_name in entries:
            z.write(source, archive_name)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None, name
    inventory.append({'file': name, 'bytes': path.stat().st_size,
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'entries': len(entries)})
    print(name, round(path.stat().st_size/1024**2, 1), 'MiB', flush=True)
(dest / 'SHA256.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')

# Historical reference report stays intact but clearly points to current geometry.
p = root / 'output/revit/REFERENCE_CHECKPOINT.md'
s = p.read_text(encoding='utf-8')
note = '> Historical reference-only checkpoint. The RVT now contains building geometry. See [GEOMETRY_PROGRESS.md](GEOMETRY_PROGRESS.md) and [TRANSFER_HANDOFF.md](../../TRANSFER_HANDOFF.md) for the saved state and continuation.\n\n'
if note not in s:
    s = s.replace('\n\n', '\n\n' + note, 1)
p.write_text(s, encoding='utf-8')
p = root / 'REVIT_MCP_SETUP.md'
s = p.read_text(encoding='utf-8').replace('Current view: 02 Proposed - Ground Coordination.', 'Saved review view: 04 Timber and Trusses - Coordination WIP.')
s = s.replace('Native building geometry has not yet been added; see `output/revit/REFERENCE_CHECKPOINT.md` and `DISCREPANCY_LOG.md`.', 'Building geometry is now saved: see `output/revit/GEOMETRY_PROGRESS.md`. The repository includes portable connection snapshots in `revit-portable/payload`; start with `TRANSFER_HANDOFF.md` on another PC.')
p.write_text(s, encoding='utf-8')
p = root / 'output/revit/DISCREPANCY_LOG.md'
s = p.read_text(encoding='utf-8').replace('Reference checkpoint only; no building geometry yet.', 'Building geometry checkpoint; see GEOMETRY_PROGRESS.md for current scope and limitations.')
s = s.replace('OPEN. User asked whether to retain levels/show clash or provisionally raise levels. No answer yet. Detailed vertical placement held.', 'OPEN. Under the continued modelling instruction, architectural levels are retained and supplier-depth joists have been placed. The 42 mm clash remains explicit; no revised design approval is implied.')
s = s.replace('Use drawing RL only if the discrepancy is explicitly accepted; do not create a definitive porch level yet.', 'Porch coordination slab placed at written RL10.734 (-172 mm). Conflicting 226 mm label remains open.')
s = s.replace('Proposed schedule-controlled openings, with discrepancy visible. Do not infer rough-opening allowances.', 'Hosted windows placed at schedule width2230. Plan conflict remains open; no rough-opening allowance inferred.')
d06 = '| D06 | Garage roof/parapet | Current envelope: garage FFL-86 plus3600 gives top+3514; elevation datum needs review | Roof support coordination required | T5 base+2750 and height891 give approximately+3641 before roof skin | Truss/roof rises above the present parapet envelope | Retain source geometry and review vertical datum/support relationship; do not silently raise parapet. | OPEN |\n'
if '| D06 |' not in s: s = s.replace('| R01 |', d06 + '| R01 |')
s = s.replace('Roof/floor fabrication members must retain supplier type and individual marks when modelling proceeds.', 'Roof/floor members retain supplier types and unique coordination marks. Floor layout does not map individual fabrication IDs to positions; source ID groups are recorded in comments.')
p.write_text(s, encoding='utf-8')
