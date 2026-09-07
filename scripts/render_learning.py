import bpy,sys
from pathlib import Path
key=sys.argv[sys.argv.index('--')+1]
names={'window':'03 Junction - window','eaves':'04 Junction - wall to roof','floor-edge':'05 Junction - floor edge'}
s=bpy.data.scenes[names[key]];bpy.context.window.scene=s;s.frame_set(100)
s.render.filepath=str(Path(__file__).resolve().parents[1]/'output/learning'/f'{key}.png')
bpy.ops.render.render(write_still=True)
