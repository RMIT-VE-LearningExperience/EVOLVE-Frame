"""Render a selected enclosure view from the saved artifact without changing it."""
import bpy,sys
from pathlib import Path
key=sys.argv[sys.argv.index('--')+1]
if key=='studies':
 scene=bpy.data.scenes['02 Assembly studies'];bpy.context.window.scene=scene
else:
 scene=next(s for s in bpy.data.scenes if s.name!='02 Assembly studies');bpy.context.window.scene=scene
 layer={'cutaway':'06 Enclosure - cutaway','assembled':'07 Enclosure - assembled','wrap':'08 Enclosure - wrap stage'}[key]
 for vl in scene.view_layers:vl.use=vl.name==layer
 bpy.context.window.view_layer=scene.view_layers[layer]
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(Path(bpy.data.filepath).parent/f'enclosure_{key}.png')
bpy.ops.render.render(write_still=True)
print('ENCLOSURE_PREVIEW_COMPLETE',key)
