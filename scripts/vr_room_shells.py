"""Room linings/decks, run inside the VR Blender revision; source model stays intact."""
import bpy, json
from mathutils import Vector

walls = vr_wall_records
outward = {'GF North wall':(0,1), 'GF East entry and bedroom':(1,0),
 'GF South family and suite':(0,-1), 'GF Laundry nook':(0,-1),
 'GF Nook return':(1,0), 'Garage rear':(0,1), 'Garage outer end':(-1,0),
 'Garage south':(0,-1), 'Garage east upstand':(1,0),
 'FF North wall':(0,1), 'FF South wall':(0,-1), 'FF West wall':(-1,0), 'FF East wall':(1,0)}
def group(name):
    c=bpy.data.collections.new(name); house.collection.children.link(c); return c
linings=group('27 Interior linings and ceilings')
decks=group('28 Upper floor decking')
def material(name, color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=.88; return m
plaster=material('VR Warm white plaster',(.89,.86,.80))
deck=material('VR Pale oak decking',(.72,.55,.35))

def subtract(box, cut):
    lo,hi=box; a,b=cut
    l=[max(lo[i],a[i]) for i in range(3)]; h=[min(hi[i],b[i]) for i in range(3)]
    if any(h[i]-l[i]<.00001 for i in range(3)): return [box]
    result=[]; low=list(lo); high=list(hi)
    for i in range(3):
        if l[i]-low[i]>.00001:
            end=high.copy(); end[i]=l[i]; result.append((low.copy(),end)); low[i]=l[i]
        if high[i]-h[i]>.00001:
            start=low.copy(); start[i]=h[i]; result.append((start,high.copy())); high[i]=h[i]
    return result

lining_boxes=[]
def solid(name, bounds, col, mat):
    pieces=[bounds]
    if col==linings:
        for previous in lining_boxes:
            pieces=[piece for box in pieces for piece in subtract(box,previous)]
        lining_boxes.extend(pieces)
    for piece in pieces: raw_solid(name,piece,col,mat)

def raw_solid(name, bounds, col, mat):
    lo,hi=bounds
    if min(hi[i]-lo[i] for i in range(3))<.0001: return
    vertices=[(x,y,z) for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)])
    mesh.materials.append(mat); mesh.update()
    ob=bpy.data.objects.new(name,mesh); col.objects.link(ob)
    ob['source']='Current frame setout; 10 mm illustrative lining, 19 mm deck'

cores=[]
for rec in walls:
    ref=bpy.data.objects[rec['name']+' | top plate lower']
    a=ref.matrix_world@Vector((0,0,-.5)); b=ref.matrix_world@Vector((0,0,.5))
    a.z=b.z=rec['z']; rec['start']=a; rec['end']=b
    horizontal=abs(b.x-a.x)>abs(b.y-a.y)
    lo=[min(a.x,b.x)-(0 if horizontal else .060),min(a.y,b.y)-(.060 if horizontal else 0),rec['z']]
    hi=[max(a.x,b.x)+(0 if horizontal else .060),max(a.y,b.y)+(.060 if horizontal else 0),rec['z']+rec['h']]
    cores.append((lo,hi))

count=0
for index,rec in enumerate(walls):
    a,b=rec['start'],rec['end']; t=(b-a).normalized(); length=(b-a).length
    normals=[Vector((-t.y,t.x,0)),Vector((t.y,-t.x,0))]
    if rec['name'] in outward:
        n=outward[rec['name']]; normals=[Vector((-n[0],-n[1],0))]
    ops=[(c-w/2,c+w/2,.905 if tag.startswith('W04') else s,
          (.905 if tag.startswith('W04') else s)+h) for tag,c,w,s,h in rec['openings']]
    joined=[]
    for endpoint in (a,b):
        joined.append(any(j!=index and all(core[0][k]-.001<=endpoint[k]<=core[1][k]+.001 for k in range(3))
                          for j,core in enumerate(cores)))
    extension=[.060 if join else .01 for join in joined]
    cuts=sorted(set([-extension[0],length+extension[1]]+[max(0,min(length,u)) for op in ops for u in op[:2]]))
    floor=.019 if rec['z']>1 else 0
    for l,r in zip(cuts,cuts[1:]):
        opening=next((o for o in ops if o[0]<(l+r)/2<o[1]),None)
        spans=[(floor,rec['h'])] if opening is None else [(floor,opening[2]),(opening[3],rec['h'])]
        for low,high in spans:
            if high-low<.002: continue
            for n in normals:
                # 5 mm clearance accommodates the existing 4.8 mm bracing sheet.
                p=a+t*l+n*.050+Vector((0,0,low))
                q=a+t*r+n*.060+Vector((0,0,high))
                pieces=[([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)])]
                for j,core in enumerate(cores):
                    if j!=index: pieces=[piece for box in pieces for piece in subtract(box,core)]
                for piece in pieces:
                    solid(rec['name']+' | lining',piece,linings,plaster); count+=1
                if abs(low-floor)<.001:
                    p=a+t*l+n*.060+Vector((0,0,floor));q=a+t*r+n*.067+Vector((0,0,floor+.070))
                    trims=[([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)])]
                    for j,core in enumerate(cores):
                        if j!=index: trims=[piece for box in trims for piece in subtract(box,core)]
                    for piece in trims: solid(rec['name']+' | skirting',piece,linings,plaster)

    # Finish jambs/sills across the timber thickness, projecting into the clear opening.
    # The caps touch the frame faces without occupying its solids.
    cross=Vector((-t.y,t.x,0))
    for end,join in enumerate(joined):
        if join: continue
        left,right=(-.01,0) if end==0 else (length,length+.01)
        p=a+t*left-cross*.050+Vector((0,0,floor));q=a+t*right+cross*.050+Vector((0,0,rec['h']))
        solid(rec['name']+' | end return',([min(p[i],q[i]) for i in range(3)],
             [max(p[i],q[i]) for i in range(3)]),linings,plaster)
    for l,r,sill,head in ops:
        jamb=rec.get('jamb_thickness',.01)
        caps=[(l,l+jamb,max(sill,floor),min(head,rec['h'])),
              (r-jamb,r,max(sill,floor),min(head,rec['h'])),
              (l+jamb,r-jamb,head-jamb,head)]
        if sill>floor+.01: caps.append((l+.01,r-.01,sill,sill+.01))
        for left,right,low,high in caps:
            if high<=low or right<=left: continue
            p=a+t*left-cross*.060+Vector((0,0,low));q=a+t*right+cross*.060+Vector((0,0,high))
            bounds=([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)])
            solid(rec['name']+' | opening return',bounds,linings,plaster)

# Three abutting rectangles retain the actual L-shaped stair void.
footprints=[(6.38,20.9505,0,7.88),(20.9505,24.35,0,6.60),(24.35,26.99,0,theatre_frame_face+.015)]
for i,(x0,x1,y0,y1) in enumerate(footprints):
    pieces=[([x0,y0,3.14],[x1,y1,3.159])]
    for core in cores: pieces=[piece for box in pieces for piece in subtract(box,core)]
    for piece in pieces: solid('Upper floor deck '+str(i),piece,decks,deck)
    pieces=[([x0,y0,2.73],[x1,y1,2.74])]
    # The alfresco soffit sits under its lower steel heads, at 2.59 m.
    for cut in [([6.28,-.09,2.7],[12.6789265,2.46,2.8]),
                ([8.539317,2.46,2.7],[12.6789265,3.6403849,2.8])]:
        pieces=[piece for box in pieces for piece in subtract(box,cut)]
    for core in cores: pieces=[piece for box in pieces for piece in subtract(box,core)]
    for piece in pieces: solid('Ground ceiling '+str(i),piece,linings,plaster)
# Wall cores reserve space for framing, but doorway thresholds need their deck.
for rec in walls:
    if rec['z']<1: continue
    a,b=rec['start'],rec['end']; t=(b-a).normalized(); n=Vector((-t.y,t.x,0))
    for tag,c,w,s,h in rec['openings']:
        if s>.001: continue
        p=a+t*(c-w/2+.01)-n*.060; q=a+t*(c+w/2-.01)+n*.060
        solid('Door threshold '+tag,([min(p.x,q.x),min(p.y,q.y),3.14],
              [max(p.x,q.x),max(p.y,q.y),3.159]),decks,deck)
# Upper ceiling is removable together with the walls for structural inspection.
pieces=[([6.38,0,5.700],[26.99,7.88,5.710])]
for core in cores: pieces=[piece for box in pieces for piece in subtract(box,core)]
for piece in pieces: solid('Upper ceiling',piece,linings,plaster)
# Close the floor-depth band where the stair void exposes the external wall.
solid('North stair-void lining',([20.9505,7.775,2.74],[26.895,7.785,3.159]),linings,plaster)
solid('East stair-void lining',([26.885,theatre_frame_face+.015,2.74],[26.895,7.775,3.159]),linings,plaster)
# Continuous stair-void fascias meet the wall lining and cover the floor depth.
for name,lo,hi in [
 ('Stair void fascia',(20.9505,6.70,2.73),(24.40,6.71,3.159)),
 ('Void return fascia',(24.40,theatre_frame_face+.015,2.73),(24.41,6.71,3.159)),
 ('Void edge soffit',(20.9505,6.60,2.73),(24.40,6.70,2.74)),
 ('Void return soffit',(24.35,theatre_frame_face+.015,2.73),(24.40,6.60,2.74))]:
    solid(name,(lo,hi),linings,plaster)
solid('Void deck edge finish',([20.9505,6.66,3.14],[24.40,6.70,3.159]),decks,deck)
# Dwarf-wall caps finish the exposed horizontal plaster edge.
for name,lo,hi in [
 ('Stair dwarf wall cap',(20.90,6.535,4.34),(24.285,6.665,4.365)),
 ('Void dwarf wall cap',(24.285,theatre_frame_face+.015,4.34),(24.415,6.665,4.365))]:
    solid(name,(lo,hi),linings,deck)
changes.append({'object':'Room shell','action':f'{count} opening-aware lining pieces; deck retains stair void; ceilings removable'})
print('VR_ROOM_SHELLS',count)
door_checks=[]
for rec in walls:
    a,b=rec['start'],rec['end']; t=(b-a).normalized(); n=Vector((-t.y,t.x,0))
    for tag,c,w,s,h in rec['openings']:
        if s>.001 or tag.startswith(('W','D0')): continue
        p=a+t*c; floor=rec['z']+(.019 if rec['z']>1 else 0)
        door_checks.append({'name':rec['name']+' / '+tag,'position':{'x':-p.x,'y':floor,'z':-p.y},
          'storage':any(word in tag.lower() for word in ('robe sliders','linen sliders')),
          'normal':{'x':-n.x,'y':0,'z':-n.y},'clear_width_m':w-2*rec.get('jamb_thickness',.01),
          'height_m':h-rec.get('jamb_thickness',.01)-(.019 if rec['z']>1 else 0)})
(OUT/'opening-clearances.json').write_text(json.dumps({'doors':door_checks},indent=2))
