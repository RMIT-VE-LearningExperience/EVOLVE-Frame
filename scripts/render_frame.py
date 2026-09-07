"""Render one saved inspection view per Blender process without changing the asset."""
import bpy
import sys
from pathlib import Path

views = {
    'overview': ('01 Complete frame', '01 Overall frame', 'frame_overview.png'),
    'alfresco': ('01 Complete frame', '02 Garage and alfresco', 'frame_alfresco.png'),
    'ground': ('02 Ground framing only', '03 Ground floor plan', 'ground_frame_plan.png'),
    'upper': ('04 Upper walls', '04 First floor plan', 'upper_frame_plan.png'),
}
key = sys.argv[sys.argv.index('--') + 1]
layer, camera, filename = views[key]
scene = bpy.context.scene
for vl in scene.view_layers:
    vl.use = vl.name == layer
bpy.context.window.view_layer = scene.view_layers[layer]
scene.camera = bpy.data.objects[camera]
scene.render.filepath = str(Path(bpy.data.filepath).parent / filename)
bpy.ops.render.render(write_still=True, layer=layer)
print('PREVIEW_COMPLETE', key)
