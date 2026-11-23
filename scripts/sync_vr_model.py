"""Copy the separately authored VR GLB and its part manifest into Unity."""
import json
import shutil
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'output/vr/building.glb'
target = root / 'unity-vr/Assets/FrameLab/Models'
data = source.read_bytes()
length = struct.unpack_from('<I', data, 12)[0]
document = json.loads(data[20:20 + length])
parts = []
for node in document['nodes']:
    if 'mesh' not in node:
        continue
    mesh = document['meshes'][node['mesh']]
    assert len(mesh['primitives']) == 1
    material = document['materials'][mesh['primitives'][0]['material']]
    pbr = material.get('pbrMetallicRoughness', {})
    extra = node.get('extras', {})
    parts.append({'name': node['name'], 'title': extra.get('label', node['name']),
        'note': extra.get('note', ''), 'material': material['name'],
        'color': pbr.get('baseColorFactor', [1, 1, 1, 1]),
        'metallic': pbr.get('metallicFactor', 1),
        'roughness': pbr.get('roughnessFactor', 1)})
assert len(parts) >= 39
shutil.copy2(source, target / 'building.glb')
(target / 'building.parts.json').write_text(json.dumps({'parts': parts}, indent=2))
shutil.copy2(root / 'output/vr/model-revision.json', target / 'model-revision.json')
shutil.copy2(root / 'output/vr/opening-clearances.json', target / 'opening-clearances.json')
shutil.copy2(root / 'output/vr/powder-window-coordination.json', target / 'powder-window-coordination.json')
print(f'Synced {len(parts)} material batches from the VR model revision.')
