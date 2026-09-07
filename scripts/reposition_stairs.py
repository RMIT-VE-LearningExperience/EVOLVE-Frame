"""Adjust only the stairs in the user's saved scene; save as a separate revision."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

source = Path(bpy.data.filepath)
dest = source.with_name('Leichhardt_Timber_Frame_Stairs_Corrected.blend')
assert source.name == 'Leichhardt_Timber_Frame.blend'
assert not dest.exists(), 'Do not overwrite an existing corrected revision.'
stairs = [o for o in bpy.data.objects if o.name.startswith(('Stair rough tread', 'Stair stringer'))]
treads = sorted([o for o in stairs if o.name.startswith('Stair rough tread')], key=lambda o:o.name)
stringers = sorted([o for o in stairs if o.name.startswith('Stair stringer')], key=lambda o:o.name)
assert len(treads) == 17 and len(stringers) == 3
assert all(o.parent is None and not o.constraints for o in stairs)

def bounds(objects):
    pts = [o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

def state(ob):
    return {'matrix': [list(row) for row in ob.matrix_world],
            'data': ob.data.name if ob.data else None,
            'hide_render': ob.hide_render, 'hide_viewport': ob.hide_viewport}

unrelated = {o.name:state(o) for o in bpy.data.objects if o not in stairs}
before = {o.name:state(o) for o in stairs}
old_bounds = bounds(treads)
# Infer the model's real wall faces rather than assuming unchanged wall placement.
end_wall = bpy.data.objects['FF East wall | top plate lower']
side_wall = bpy.data.objects['FF North wall | top plate lower']
end_inner_x = bounds([end_wall])[0][0]
side_inner_y = bounds([side_wall])[1][0]
foot = end_inner_x - 2.0
head = foot - 4.0
center_y = side_inner_y - .55
ff = treads[-1].location.z + treads[-1].dimensions.z/2
old_y = sum(o.location.y for o in treads)/len(treads)
for i, ob in enumerate(treads):
    ob.location.x = foot - (i+.5)*4.0/17
    ob.location.y = center_y
    ob.scale.x = 4.0/17
for ob in stringers:
    y = center_y + (ob.location.y-old_y)
    a,b = Vector((foot,y,.08)),Vector((head,y,ff-.08))
    ob.location = (a+b)/2
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = (b-a).to_track_quat('Z','Y')
    ob.scale.z = (b-a).length
for ob in stairs:
    ob['source'] = 'Architectural sheet 08: 4000 stair flight; 2000 entry end; 1100 stair zone'
    ob['modelling_basis'] = 'Dimension-based placement. Existing 1020 rough tread width centred within 1100 zone; rough framing detail remains indicative.'
bpy.context.view_layer.update()
assert all(state(bpy.data.objects[name]) == value for name,value in unrelated.items()), 'Unrelated objects changed'
new_bounds = bounds(treads)
assert abs(new_bounds[0][0]-head)<1e-5 and abs(new_bounds[0][1]-foot)<1e-5
assert abs((end_inner_x-new_bounds[0][1])-2.0)<1e-5
assert abs((side_inner_y-new_bounds[1][1])-.04)<1e-5
assert new_bounds[1][0] >= side_inner_y-1.1

report = {'source':str(source),'corrected_file':str(dest),'modified_objects':len(stairs),
          'preserved_other_objects':len(unrelated),'previous_tread_bounds':old_bounds,
          'corrected_tread_bounds':new_bounds,'wall_inner_x':end_inner_x,'wall_inner_y':side_inner_y,
          'flight_run_m':4.0,'entry_end_gap_m':2.0,'architectural_stair_zone_m':1.1,
          'rough_tread_width_m':1.02,'rough_tread_clearance_each_side_m':.04,
          'centerline_y_adjustment_m':center_y-old_y,'previous_stair_transforms':before,
          'check':'PASS: dimensions, exterior-wall clearance and unrelated-object preservation'}
note = bpy.data.texts.new('STAIR POSITION - sheet 08 correction')
note.write('Stairs aligned to architectural sheet 08. Flight 4000 mm; entry-end gap 2000 mm; width zone 1100 mm.\n'
           'Rough treads retain 1020 mm width, centred with nominal 40 mm each side. This clearance is a modelling assumption, not a detailed stair specification.\n'
           'Upper landing at X %.3f, lower end at X %.3f, centreline Y %.3f metres.\n' % (head,foot,center_y)
           +'The correction preserves all non-stair object geometry and the saved user view. Original edited file remains available.\n'
           +'Sheet 07 shows a different 3190 mm ground-floor stair dimension; this correction follows the 4000 mm flight on sheet 08.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(dest))
dest.with_suffix('.position-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='previous_stair_transforms'},indent=2))
