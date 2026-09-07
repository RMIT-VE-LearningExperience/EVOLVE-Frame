"""Validate the saved Blender deliverable, including its inspection visibility."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

scene = bpy.context.scene
checks = {}
checks['saved_file'] = bpy.data.filepath
checks['mesh_count'] = sum(o.type == 'MESH' for o in scene.objects)
checks['packed_plan_images'] = [im.name for im in bpy.data.images if im.packed_file]
assert len(checks['packed_plan_images']) >= 2
assert scene.unit_settings.system == 'METRIC'
assert bpy.data.collections['01 Slab datum'].hide_viewport
assert bpy.data.collections['01 Slab datum'].hide_render
checks['invalid_mesh_transforms'] = [o.name for o in scene.objects if o.type == 'MESH' and
    (min(o.scale) <= 0 or not all(math.isfinite(v) for row in o.matrix_world for v in row))]
assert not checks['invalid_mesh_transforms']

checks['inspection_views'] = {}
expected = {
    '02 Ground framing only': ('02 Ground floor walls', 'Ground connections'),
    '03 Floor structure': ('04 First floor joists', 'Floor connections'),
    '04 Upper walls': ('05 Upper floor walls', 'Upper connections'),
    '05 Roof structure': ('06 Upper roof trusses', 'Roof connections'),
}
groups = ['Ground connections', 'Floor connections', 'Upper connections', 'Roof connections']
for name, (primary, connections) in expected.items():
    layer = scene.view_layers[name]
    layer.update()
    assert not layer.layer_collection.children[primary].exclude
    for group in groups:
        excluded = layer.layer_collection.children['09 Bracing and connections'].children[group].exclude
        assert excluded == (group != connections), (name, group)
    assert not bpy.data.objects['Presentation ground'].visible_get(view_layer=layer)
    checks['inspection_views'][name] = {'primary_collection': primary, 'connections': connections}

checks['roof_assembly_counts'] = {
    'T1': sum(o.name.startswith('T1-') and 'bottom chord' in o.name for o in scene.objects),
    'T5': sum(o.name.startswith('T5-') and 'bottom' in o.name for o in scene.objects),
    'T6': sum(o.name.startswith('T6-') and 'bottom' in o.name for o in scene.objects),
}
assert checks['roof_assembly_counts'] == {'T1': 15, 'T5': 8, 'T6': 5}

# Check the interiors of both rectangles in the L-shaped stair/entry void.
voids = [(20.96, 24.30, 6.66, 7.78), (24.41, 26.90, 4.68, 7.78)]
intrusions = []
for ob in bpy.data.collections['04 First floor joists'].objects:
    if 'chord' not in ob.name:
        continue
    bounds = [ob.matrix_world @ Vector(corner) for corner in ob.bound_box]
    xmin, xmax = min(v.x for v in bounds), max(v.x for v in bounds)
    ymin, ymax = min(v.y for v in bounds), max(v.y for v in bounds)
    for x0, x1, y0, y1 in voids:
        if xmin < x1 and xmax > x0 and ymin < y1 and ymax > y0:
            intrusions.append(ob.name)
checks['joist_chords_intruding_into_stair_void'] = intrusions
assert not intrusions
checks['status'] = 'PASS: saved geometry, packed references, view isolation and stair void checks'
Path(bpy.data.filepath).with_name('saved_file_verification.json').write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
