"""Dimension-driven internal setout for the separate Leichhardt VR revision.

Run after vr_upper_entries, before linings. Preserves original learning .blend.
Metres, drawing X right / Y up. Written room chains govern wall faces; nominal
door leaves get explicit illustrative jamb allowances. Unspecified details stay
in the report instead of being described as drawing-approved.
"""
import ast
import copy

arch_report={'source':'Architectural sheets 07, 08, 15, 17-19',
 'basis':'Written dimension chains, existing perimeter inner frame faces x6.470/26.900 and y0.090/7.790.',
 'walls':[], 'assumptions':['Door jambs 22 mm and side reveals 3 mm; un-dimensioned door nib offsets are visual setout allowances.',
 'Theatre platform height is unresolved; the former 420 mm height was a misread horizontal dimension.',
 'Theatre 2340 mm door conflicts with the 340 mm bulkhead below a 2590 mm ceiling; not resolved by this wall setout.']}
arch_source=(ROOT/'scripts/build_frame.py').read_text()
arch_node=next(n for n in ast.parse(arch_source).body if isinstance(n,ast.FunctionDef) and n.name=='wall')
arch_code=ast.get_source_segment(arch_source,arch_node)
# Clip end jamb/lintel members to their wall run; shared corner walls provide
# the adjacent support rather than leaving projecting slivers at small nibs.
arch_code=arch_code.replace("if hi-lo>.003:\n   o=box", "if hi-lo>.003:\n   u0=max(0,u-width/2);u1=min(L,u+width/2)\n   if u1-u0<.003:return\n   u=(u0+u1)/2;width=u1-u0\n   o=box")
arch_code=arch_code.replace("if v-u>.003:return beam", "u=max(0,u);v=min(L,v)\n  if v-u>.003:return beam")
def arch_box(name,loc,dims,col,material,source='',status=''):
    loc,dims=Vector(loc),Vector(dims)
    ob=vr_box(name,loc-dims/2,loc+dims/2,col,material)
    ob['source']=source;ob['modelling_basis']='Dimension-chain VR revision; illustrative framing sections'
    return ob
def arch_beam(name,a,b,width,depth,col,material,source='',status=''):
    ob=vr_beam(name,a,b,width,depth,col,material)
    ob['source']=source;return ob
arch_env={'Vector':Vector,'math':math,'box':arch_box,'beam':arch_beam,
 'wood':pine,'lvl':bpy.data.materials['LVL beams'],
 'zinc':bpy.data.materials['Galvanised connectors'],
 'B':bpy.data.collections['09 Bracing and connections'],'wall_records':[]}
exec(compile(arch_code,'dimension_driven_wall','exec'),arch_env)

def arch_wall(name,a,b,level=0,ops=(),height=None,source='Written room chains 07/08'):
    """ops = (tag, WORLD centre along variable axis, nominal width, height, kind)."""
    old=next((r for r in vr_wall_records if r['name']==name),None)
    for ob in list(house.objects):
        if ob.name.startswith(name+' |'):
            bpy.data.objects.remove(ob,do_unlink=True)
    axis=0 if abs(b[0]-a[0])>abs(b[1]-a[1]) else 1
    assert b[axis]>a[axis],name
    z=3.14 if level else 0;h=height or (2.59 if level else 2.74)
    openings=[]
    for tag,centre,width,opening_height,kind in ops:
        jamb=.01 if kind=='passage' else .022
        rough_width=width+2*jamb+(0 if kind=='passage' else .006)
        head=opening_height+jamb if kind=='passage' else opening_height+(0.019 if level else 0)+.028
        openings.append([tag,centre-a[axis],rough_width,0,head])
    col=bpy.data.collections['05 Upper floor walls' if level else '02 Ground floor walls']
    arch_env['wall'](name,a,b,z,h,col,openings,True)
    rec=arch_env['wall_records'][-1]
    rec['jamb_thickness']=.01 if ops and all(o[4]=='passage' for o in ops) else .022
    rec['architectural_basis']=source
    rec['nominal_openings']=[dict(tag=o[0],width=o[2],height=o[3],kind=o[4]) for o in ops]
    if old: vr_wall_records[vr_wall_records.index(old)]=rec
    else: vr_wall_records.append(rec)
    arch_report['walls'].append(copy.deepcopy(rec))
    return rec

# Ground floor: 3110 entry / 90 wall / 4500 bedroom; the bedroom wall is
# intentionally 720 mm north of the suite wall, rather than collinear with it.
arch_wall('Entry bedroom division',(22.81,4.635),(26.90,4.635),
          ops=[('Bedroom 1 door',23.435,.820,2.340,'hinged')])
arch_wall('WIR bedroom division',(22.855,.090),(22.855,4.590),
          # North finished jamb aligns with the adjoining suite faceY3.855.
          # Retain800 clear, shifting15mm rather than exposing the corner stud.
          ops=[('WIR access',3.455,.800,2.400,'passage')])
arch_wall('Entry suite division',(17.970,3.915),(22.810,3.915))
# Sheet07/17: the 500-deep family recess lies west of the flat ensuite
# back wall. Its north/south boxes differ in length (420 and510 clear).
arch_wall('Ensuite west',(18.515,.090),(18.515,3.870),
          source='Sheets07/17: 5100 family +500 recess +90 wall; ensuite1800 clear')
arch_wall('Family recess north box west',(18.015,3.450),(18.015,3.870))
arch_wall('Family recess north box return',(17.970,3.405),(18.470,3.405))
arch_wall('Family recess south box west',(18.015,.090),(18.015,.600))
arch_wall('Family recess south box return',(17.970,.645),(18.470,.645))
arch_wall('Ensuite WIR division',(20.405,.090),(20.405,3.870),
          ops=[('Ensuite access',1.950,.720,2.340,'cavity')],
          source='Sheet07 double90 wall; sheet17 720x2340 cavity slider; centre scaled')
arch_wall('Ensuite WIR second skin',(20.495,.090),(20.495,3.870),
          ops=[('Ensuite access second skin',1.950,.720,2.340,'cavity')])
arch_wall('Ensuite WC partition',(18.560,1.035),(20.360,1.035),
          ops=[('WC door',19.880,.720,2.340,'hinged')])
arch_wall('Ensuite shower nib',(18.560,2.925),(19.460,2.925))
arch_wall('Powder west',(19.975,5.200),(19.975,7.790))
arch_wall('Powder east',(21.665,5.200),(21.665,7.790))
arch_wall('Powder south',(19.930,5.155),(21.710,5.155),
          ops=[('Powder door',21.150,.820,2.340,'hinged')],
          source='Sheets07/15: 1600x2590 frame-face clear; door east-hinged, centre scaled')

# Upper floor: north/south room chains close exactly to the 20430 mm clear
# perimeter span. The southern rooms are 3200 deep; hall 1120; north rooms3200.
arch_wall('FF Bed 4 and robes',(6.470,4.545),(11.240,4.545),1,
          [('WIR4 slider',9.900,.820,2.400,'cavity')])
arch_wall('FF WIR3 and WIR4 division',(8.815,3.380),(8.815,4.500),1)
arch_wall('FF Robes hall wall',(6.470,3.335),(11.240,3.335),1,
          [('WIR3 slider',7.420,.820,2.400,'cavity')])
arch_wall('FF WIR4 east',(11.195,3.380),(11.195,4.500),1)
arch_wall('FF Bed 4 WC division',(11.195,4.590),(11.195,7.790),1,
          [('Bed 4 door',5.075,.820,2.340,'hinged')])
arch_wall('FF WC bath division',(12.285,4.500),(12.285,7.790),1)
arch_wall('FF WC south',(11.240,5.635),(12.240,5.635),1,
          [('WC door',11.740,.720,2.340,'hinged')])
arch_wall('FF Bath hall',(12.330,4.545),(15.020,4.545),1,
          [('Bathroom door',12.830,.720,2.340,'hinged'),
           ('Upper linen sliders',14.220,1.240,2.400,'sliding')])
arch_wall('FF Bath robe division',(14.375,5.190),(14.375,7.790),1)
arch_wall('FF Linen north',(13.330,5.145),(15.020,5.145),1)
arch_wall('FF Linen west',(13.375,4.590),(13.375,5.100),1)
arch_wall('FF Bed 5 west',(15.065,4.500),(15.065,7.790),1,
          [('Bed 5 robe sliders',6.490,2.160,2.400,'sliding')])
arch_wall('FF Bed 5 south',(15.110,4.545),(19.420,4.545),1,
          [('Bed 5 door',15.645,.820,2.340,'hinged')])
arch_wall('FF Bed 5 east',(19.465,4.500),(19.465,7.790),1)
arch_wall('FF Bed 2 study hall',(12.840,3.335),(19.510,3.335),1)
arch_wall('FF Bed 2 study division',(16.975,.090),(16.975,3.290),1)
arch_wall('FF Bed 2 robe front',(16.285,.090),(16.285,3.290),1,
          [('Bed 2 robe sliders',1.690,2.460,2.400,'sliding')])
arch_wall('FF Study retreat division',(19.465,.090),(19.465,3.290),1,
          [('Study door',2.805,.820,2.340,'hinged')])
arch_wall('FF Bath 2 bedroom wall',(10.550,2.245),(12.840,2.245),1,
          [('Bath 2 door',12.270,.720,2.340,'hinged')])
arch_wall('FF Bath 2 west',(10.595,.090),(10.595,2.200),1)
arch_wall('FF Bath 2 east',(12.885,.090),(12.885,3.290),1,
          [('Bed 2 door',2.805,.820,2.340,'hinged')])
arch_wall('FF Bed 3 hall stub',(11.195,2.290),(11.195,3.290),1,
          [('Bed 3 door',2.805,.820,2.340,'hinged')])

# Theatre: full-height outer wall and two boxed returns. The inset dashed
# edges between these boxes belong to the overhead bulkhead, not full walls.
arch_wall('FF Theatre west',(22.555,.090),(22.555,4.590),1)
arch_wall('FF Theatre north',(22.510,4.635),(26.900,4.635),1,
          [('Theatre entry',23.570,.820,2.340,'hinged')])
arch_wall('FF Theatre entry box return',(22.975,4.170),(22.975,4.590),1)
arch_wall('FF Theatre entry box face',(22.600,4.125),(23.020,4.125),1)
arch_wall('FF Theatre far box return',(22.975,.090),(22.975,.510),1)
arch_wall('FF Theatre far box face',(22.600,.555),(23.020,.555),1)

# Ground-floor stair enclosure replaces the unsupported open picket design.
arch_wall('GF stair enclosure',(21.710,6.600),(24.900,6.600))
for ob in list(house.objects):
    if ob.name.startswith(('Stair newel','Stair baluster','Stair oak handrail','Stair landing handrail')):
        bpy.data.objects.remove(ob,do_unlink=True)

bpy.context.view_layer.update()
theatre_frame_face=4.680
# Extend the retained void dwarf wall to the newly dimensioned theatre wall.
for ob in house.objects:
    if not ob.name.startswith('FF void balustrade |'):continue
    if 'plate' in ob.name:
        points=[ob.matrix_world@v.co for v in ob.data.vertices]
        old_low=min(p.y for p in points); old_high=max(p.y for p in points)
        ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if abs(p.y-old_low)<.00001:p.y=theatre_frame_face;v.co=inv@p
    elif 'stud' in ob.name and ob.location.y<4.75:
        ob.location.y=theatre_frame_face+.0175
    elif 'nogging' in ob.name:
        bb=vr_bounds(ob)
        if bb[1][0]<theatre_frame_face+.035:
            ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
            for v in ob.data.vertices:
                p=ob.matrix_world@v.co
                if p.y<theatre_frame_face+.035:p.y=theatre_frame_face+.035;v.co=inv@p

# Keep the floor opening edges beneath the moved theatre wall. These edits
# restore the architectural edge; they do not alter member section sizes.
for name,axis,value,which in [('Floor rim/trimmer 8',1,4.635,'centre'),
                              ('Floor rim/trimmer 4',1,4.635,'max'),
                              ('Floor rim/trimmer 7',1,4.6575,'min'),
                              ('1B7 2-300x45',1,4.635,'max')]:
    ob=bpy.data.objects[name]
    if which=='centre': ob.location[axis]+=value-(sum(vr_bounds(ob)[axis])/2)
    else:
        bounds=vr_bounds(ob)[axis]; edge=bounds[0 if which=='min' else 1]
        ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if abs(p[axis]-edge)<.00001:p[axis]=value;v.co=inv@p

# Existing two finished-door routines use these records; update their source
# positions rather than leaving leaves and casing at the old traced portal.
entry_report['partitions']=[]
entry_report['doors']=[]
for wall_name,tag in [('FF Bed 5 south','Bed 5 door'),('FF Bath hall','Bathroom door')]:
    rec=next(r for r in vr_wall_records if r['name']==wall_name)
    op=next(o for o in rec['openings'] if o[0]==tag)
    nominal=next(o for o in rec['nominal_openings'] if o['tag']==tag)
    c,w=op[1],op[2]
    entry_report['doors'].append({'name':tag,'wall':wall_name,
      'nominal_leaf_width_mm':round(nominal['width']*1000),'nominal_leaf_height_mm':2340,
      'rough_width_mm':round(w*1000),'jamb_clear_width_mm':round((w-.044)*1000),
      'finished_head_above_floor_mm':2346,'hinge_edge_x':rec['a'][0]+c-w/2,
      'centre_x':rec['a'][0]+c,'wall_y':rec['a'][1]})
bpy.context.view_layer.update()
(OUT/'architectural-wall-setout.json').write_text(json.dumps(arch_report,indent=2))
changes.append({'object':'Dimension-driven interior layout','action':f"Rebuilt {len(arch_report['walls'])} wall runs from architectural chains, including correct bedroom/WIR/linen door locations, theatre boxes and stair enclosure."})
