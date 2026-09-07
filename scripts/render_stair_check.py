"""Temporary visibility for a stair-placement preview; never resave the model."""
import bpy
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
for layer in scene.view_layers: layer.use=layer.name=='01 Complete frame'
bpy.context.window.view_layer=scene.view_layers['01 Complete frame']
for col in bpy.data.collections:
    if col.name.startswith(('05 Upper','06 Upper','07 Garage roof','08 Porch roof','11 Roof')):
        col.hide_render=True
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.name!='Presentation ground':
        points=[ob.matrix_world @ Vector(v) for v in ob.bound_box]
        if max(p.x for p in points)<19.9 or min(p.x for p in points)>27.1:
            ob.hide_render=True
        if ob.name.startswith(('Theatre platform','Roof diagonal','T1-','HIP-')):
            ob.hide_render=True
camera=scene.camera
camera.location=(22.6,6.4,25)
camera.rotation_euler=(Vector((22.6,6.4,0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=7.3
scene.render.resolution_x=1400;scene.render.resolution_y=1000
scene.render.filepath=str(Path(bpy.data.filepath).with_name('stairs_position_check.png'))
bpy.ops.render.render(write_still=True,layer='01 Complete frame')
