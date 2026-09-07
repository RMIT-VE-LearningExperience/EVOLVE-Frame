"""Read-only geometry extraction for the positioning audit; does not save Blender."""
import bpy, json
from pathlib import Path
from mathutils import Vector
out=Path(bpy.data.filepath).parent/'audit'
out.mkdir(exist_ok=True)
rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 points=[ob.matrix_world @ Vector(v) for v in ob.bound_box]
 rows.append({'name':ob.name,'collections':[c.name for c in ob.users_collection],
              'location':list(ob.matrix_world.translation),
              'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],
              'local_dimensions':list(ob.scale),'matrix':[list(r) for r in ob.matrix_world],
              'source':ob.get('source',''),'basis':ob.get('modelling_basis','')})
(out/'measured_geometry.json').write_text(json.dumps({'file':bpy.data.filepath,'objects':rows},indent=2))
for r in rows:
 if any(s in r['name'] for s in ['top plate lower','W04 kitchen sill','D05 north head','1L7 alfresco side head','Floor rim/trimmer','T5-01 bottom','T6-1 bottom']):
  print(r['name'], 'XYZ', [round(x,4) for x in r['location']], 'bounds',[[round(v,4) for v in b] for b in r['bounds']])
print('AUDIT_EXTRACTED',len(rows))
