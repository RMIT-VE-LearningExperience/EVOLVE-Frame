"""Create a separate VR model revision from the current learning Blender source.

Run Blender --background output/learning/Leichhardt_Learning_Experience.blend
    --python scripts/build_vr_model.py
Never overwrites the source .blend or the web exports.
"""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/vr'
OUT.mkdir(parents=True, exist_ok=True)
source = Path(bpy.data.filepath)
assert source.name == 'Leichhardt_Learning_Experience.blend'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
house = bpy.data.scenes['01 Building - enclosure']
bpy.context.window.scene = house
export_layer = house.view_layers.new('VR all visible')
bpy.context.window.view_layer = export_layer
changes = []

def record(o, action):
    changes.append({'object': o.name, 'action': action})

# Architectural sheet 11 explicitly gives sill 905 + height 514 = head 1419.
# The legacy generator mistakenly used the head dimension as the sill.
delta = 0.514
for o in house.objects:
    if not o.name.startswith('GF North wall | W04 kitchen'):
        continue
    if 'king stud' in o.name:
        continue
    if 'head cripple' in o.name:
        o.scale.z += delta
        o.location.z -= delta / 2
    elif 'sill cripple' in o.name or 'jack stud' in o.name:
        assert o.scale.z > delta
        o.scale.z -= delta
        o.location.z -= delta / 2
    else:
        o.location.z -= delta
    o['vr_correction'] = 'W04 coordinated to architectural sheet 11: sill 905, head 1419 mm'
    record(o, 'Coordinated W04 framing to 905 mm sill')

opening = bpy.data.objects['OPENING | W04 kitchen']
assert abs(opening.location.z - 1.419) < 0.002
opening.location.z = 0.905
opening['status'] = 'VR revision: sill and height corrected to architectural sheet 11'
record(opening, 'Lowered complete window proxy 514 mm')
for o in house.objects:
    if o.type != 'MESH' or o.get('associated_frame') != 'GF North wall':
        continue
    if abs(o.location.x - opening.location.x) > 0.003 or abs(o.scale.x - 1.510) > 0.003:
        continue
    low, high = o.location.z - o.scale.z / 2, o.location.z + o.scale.z / 2
    if abs(high - 1.419) < 0.003:
        o.scale.z -= delta
        o.location.z -= delta / 2
    elif abs(low - 1.933) < 0.003:
        o.scale.z += delta
        o.location.z -= delta / 2
    else:
        continue
    record(o, 'Refitted membrane/masonry to corrected W04 opening')

# The schedule depicts one fixed light. Remove the generic two-panel proxy.
glazing = [o for o in opening.children if 'glass' in o.name]
assert len(glazing) == 2
glazing[0].location.x = 0
glazing[0].scale.x = 1.510 - 2 * 0.045
for o in list(opening.children):
    if o == glazing[1] or 'mullion' in o.name:
        record(o, 'Removed generic subdivision from scheduled single fixed light')
        bpy.data.objects.remove(o, do_unlink=True)

bpy.context.view_layer.update()
sill = bpy.data.objects['GF North wall | W04 kitchen sill']
sill_top = max((sill.matrix_world @ Vector(v)).z for v in sill.bound_box)
assert abs(sill_top - 0.905) < 0.00001
assert abs(max((bpy.data.objects['W04 kitchen | head'].matrix_world @ Vector(v)).z
               for v in bpy.data.objects['W04 kitchen | head'].bound_box) - 1.419) < 0.00001

exec(compile((ROOT / 'scripts/vr_structure_fixes.py').read_text(), 'vr_structure_fixes.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_upper_entries.py').read_text(), 'vr_upper_entries.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_architectural_layout.py').read_text(), 'vr_architectural_layout.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_powder_coordination.py').read_text(), 'vr_powder_coordination.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_south_window_registration.py').read_text(), 'vr_south_window_registration.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_photo_registration.py').read_text(), 'vr_photo_registration.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_architectural_bracing.py').read_text(), 'vr_architectural_bracing.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_room_shells.py').read_text(), 'vr_room_shells.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_finish_openings.py').read_text(), 'vr_finish_openings.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_entry_finishes.py').read_text(), 'vr_entry_finishes.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_review_finishes.py').read_text(), 'vr_review_finishes.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_architectural_finishes.py').read_text(), 'vr_architectural_finishes.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_window_schedule_finishes.py').read_text(), 'vr_window_schedule_finishes.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_fixed_fitout.py').read_text(), 'vr_fixed_fitout.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_photo_review.py').read_text(), 'vr_photo_review.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_bathroom_tiles.py').read_text(), 'vr_bathroom_tiles.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_photo_finish045.py').read_text(), 'vr_photo_finish045.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_detail_geometry.py').read_text(), 'vr_detail_geometry.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_architectural_details046.py').read_text(), 'vr_architectural_details046.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_drainage046.py').read_text(), 'vr_drainage046.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_details046_checks.py').read_text(), 'vr_details046_checks.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_powder_checks.py').read_text(), 'vr_powder_checks.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_window_clearance_checks.py').read_text(), 'vr_window_clearance_checks.py', 'exec'))
exec(compile((ROOT / 'scripts/vr_architectural_checks.py').read_text(), 'vr_architectural_checks.py', 'exec'))
classified = []
def descend(col, top, cut=False):
    cut = cut or col.name.startswith('Cutaway removal')
    for o in col.objects:
        if o.type == 'MESH':
            classified.append((o, top.name, cut))
    for child in col.children:
        descend(child, top, cut)

for col in house.collection.children:
    if col.name[:2].isdigit() and 2 <= int(col.name[:2]) <= 28:
        descend(col, col)

exec(compile((ROOT / 'scripts/vr_visibility_groups.py').read_text(), 'vr_visibility_groups.py', 'exec'))

deps = bpy.context.evaluated_depsgraph_get()
batches = {}
bevelled = 0
duplicate_objects = []
signatures = set()
for o, group, cut in classified:
    ev = o.evaluated_get(deps)
    evaluated = ev.to_mesh()
    # Exact same material/topology/transform instances are duplicate solids, unlike
    # opposing faces at ordinary construction joints. Remove only exact duplicates.
    signature = (group, cut, tuple(round(v, 6) for row in ev.matrix_world for v in row),
                 tuple(tuple(round(c, 6) for c in v.co) for v in evaluated.vertices),
                 tuple(tuple(p.vertices) for p in evaluated.polygons),
                 tuple(m.name if m else '' for m in evaluated.materials))
    if signature in signatures:
        duplicate_objects.append(o.name)
        ev.to_mesh_clear()
        continue
    signatures.add(signature)
    bm = bmesh.new()
    bm.from_mesh(evaluated)
    bm.transform(ev.matrix_world)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    timber = len(evaluated.materials) == 1 and any(
        word in evaluated.materials[0].name.lower() for word in ('pine', 'lvl', 'timber'))
    if timber and len(evaluated.vertices) == 8 and len(evaluated.polygons) == 6:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.0008, segments=1,
                        affect='EDGES', clamp_overlap=True)
        bevelled += 1
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    inverse = ev.matrix_world.inverted()
    scale = ev.matrix_world.to_scale()
    for mi in {f.material_index for f in bm.faces}:
        mat = evaluated.materials[mi]
        key = (group, mat.name, cut)
        batch = batches.setdefault(key, {'vertices': [], 'faces': [], 'smooth': [], 'uv': [], 'material': mat})
        start = len(batch['vertices'])
        for vertex in bm.verts:
            batch['vertices'].append(tuple(vertex.co))
            local = inverse @ vertex.co
            u, v = local.x * scale.x + local.y * scale.y, local.z * scale.z
            if group.startswith('28') or o.name.startswith('Stair finished tread'):
                u, v = local.x * scale.x, local.y * scale.y
            if 'floor porcelain' in mat.name:
                u, v = vertex.co.x - 12.345, vertex.co.y - 4.605
            elif 'wall porcelain' in mat.name:
                u, v = vertex.co.x + vertex.co.y - 16.950, vertex.co.z - 3.159
            # The LVL veneer scan has horizontal grain; pine has vertical grain.
            batch['uv'].append((v, u) if 'LVL' in mat.name else (u, v))
        batch['faces'].extend(tuple(start + v.index for v in f.verts)
                              for f in bm.faces if f.material_index == mi)
        batch['smooth'].extend(f.smooth for f in bm.faces if f.material_index == mi)
    bm.free()
    ev.to_mesh_clear()

house['vr_revision'] = 'W04 corrected; exact duplicate solids filtered during export; 0.8 mm timber edge bevels'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'Leichhardt_VR.blend'))
export = bpy.data.scenes.new('VR export')
bpy.context.window.scene = export
materials = {}
for (group, matname, cut), batch in batches.items():
    mesh = bpy.data.meshes.new(group)
    mesh.from_pydata(batch['vertices'], [], batch['faces'])
    for polygon, smooth in zip(mesh.polygons, batch['smooth']): polygon.use_smooth = smooth
    mesh.update()
    uv = mesh.uv_layers.new(name='Member metres')
    for loop in mesh.loops:
        uv.data[loop.index].uv = batch['uv'][loop.vertex_index]
    mat = materials.get(matname)
    if mat is None:
        src = batch['material']
        mat = bpy.data.materials.new('LEARN Web ' + matname)
        mat.use_nodes = True
        bs = mat.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value = src.diffuse_color
        source_bs = src.node_tree.nodes.get('Principled BSDF') if src.use_nodes else None
        if source_bs:
            bs.inputs['Metallic'].default_value = source_bs.inputs['Metallic'].default_value
            bs.inputs['Roughness'].default_value = source_bs.inputs['Roughness'].default_value
        materials[matname] = mat
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(group + (' cut' if cut else ''), mesh)
    export.collection.objects.link(obj)
    obj['key'] = group
    obj['label'] = group[3:]
    obj['cut'] = cut
    obj['note'] = 'VR revision; W04 corrected. Remaining coordination items recorded in the position audit.'
bpy.ops.export_scene.gltf(filepath=str(OUT / 'building.glb'), export_format='GLB',
    use_active_scene=True, export_extras=True, export_animations=False, export_cameras=False,
    export_lights=False, export_apply=True)
manifest = {'source': str(source.relative_to(ROOT)), 'source_sha256': source_hash,
    'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == source_hash,
    'w04_sill_mm': round(sill_top * 1000), 'w04_head_mm': 1419,
    'bevelled_timber_members': bevelled, 'bevel_width_mm': 0.8,
    'removed_exact_duplicate_solids': duplicate_objects,
    'triangles': sum(len(b['faces']) for b in batches.values()),
    'batches': len(batches), 'changes': changes,
    'remaining': 'Other position-audit items remain open; this is a partial coordinated revision.'}
assert manifest['source_unchanged']
(OUT / 'model-revision.json').write_text(json.dumps(manifest, indent=2))
print('VR_MODEL_REVISION ' + json.dumps({k:v for k,v in manifest.items() if k != 'changes'}))
