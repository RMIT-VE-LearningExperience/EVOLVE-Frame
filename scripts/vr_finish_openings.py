"""Finish omitted enclosures, coordinated to architectural sheets 07 and 11.
Runs after vr_structure_fixes and vr_room_shells in the VR-only model revision.
"""
opening_col=bpy.data.collections['26 Windows and doors']
aluminium=bpy.data.materials['ENV Aluminium frames - illustrative']
glazing=bpy.data.materials['ENV Glazing proxy']
doorwood=vr_material('VR Finished door timber',(.52,.39,.25))
for o in house.objects:
    if o.type=='MESH' and o.get('associated_frame')=='GF North wall':
        bb=vr_bounds(o)
        if bb[0][0]<6.38 and bb[0][1]>6.38:
            o.scale.x=bb[0][1]-6.38; o.location.x=(bb[0][1]+6.38)/2
            record(o,'Trimmed exterior skin corner extension out of garage interior')
for o in house.objects:
    if o.type=='MESH' and o.name.startswith(('D01','D02')) and 'door leaf' in o.name:
        o.data=o.data.copy(); o.data.materials.clear(); o.data.materials.append(doorwood)
        record(o,'Replaced structural plywood proxy with finished door timber; schedule D01/D02')

# D05 is a 3600 + 3000 mm corner stacker, 2100 mm high. Locate the corner
# from the existing side head, then use scheduled leg dimensions instead of
# stretching panes over the old approximate beam extents.
head_o=bpy.data.objects['1L7 alfresco side head']; bb=vr_bounds(head_o)
corner_x=(bb[0][0]+bb[0][1])/2; corner_y=bb[1][1]
door_basis=[]
# Complete short returns left by the old approximate corner-opening heads.
def corner_infill(name,a,b,outside):
    a,b=Vector((*a,0)),Vector((*b,0));t=(b-a).normalized();length=(b-a).length;n=Vector((*outside,0))
    frame_col=bpy.data.collections['02 Ground floor walls']
    for label,z,d in [('bottom plate',.0175,.035),('top plate',2.695,.09)]:
        vr_beam(name+' '+label,a+Vector((0,0,z)),b+Vector((0,0,z)),.09,d,frame_col,pine)
    for i,u in enumerate((.0175,length/2,length-.0175)):
        p=a+t*u
        stud=vr_beam(name+f' stud {i}',p+Vector((0,0,.035)),p+Vector((0,0,2.65)),.035,.09,frame_col,pine)
        stud.rotation_mode='XYZ'; stud.rotation_euler.z=math.atan2(t.y,t.x)
    for suffix,low,high,col,mat in [('inside',-.060,-.050,linings,plaster),
          ('outside',.085,.195,bpy.data.collections['23 Ground brick veneer'],bpy.data.materials['ENV Brick veneer - colour unselected'])]:
        p=a+n*low;q=b+n*high+Vector((0,0,2.74))
        solid(name+' '+suffix,([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)]),col,mat)
    p=b-t*.01-n*.060;q=b+n*.195+Vector((0,0,2.74))
    solid(name+' reveal',([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)]),linings,plaster)
corner_infill('D05 meals return',(8.539317,corner_y),(corner_x-3.6,corner_y),(0,-1))
corner_infill('D05 family return',(corner_x,.045),(corner_x,corner_y-3),(-1,0))
def stacker(name,a,b):
    a,b=Vector((*a,0)),Vector((*b,0)); t=(b-a).normalized(); n=Vector((-t.y,t.x,0)); length=(b-a).length
    def p(u,z,offset=0): return a+t*u+n*offset+Vector((0,0,z))
    # Shared outer frame, three framed glass leaves, small staggered tracks.
    for label,z in [('threshold',.018),('head',2.0775)]:
        vr_beam(name+' '+label,p(0,z),p(length,z),.11,.036 if z<1 else .045,opening_col,aluminium)
    for label,u in [('end jamb',.0225),('corner stile',length-.0225)]:
        vr_beam(name+' '+label,p(u,.036),p(u,2.055),.045,.11,opening_col,aluminium)
    clear=length-.09; width=clear/3
    for i in range(3):
        u0=.045+i*width;u1=u0+width;off=(i-1)*.026
        for label,u in [('left',u0+.016),('right',u1-.016)]:
            vr_beam(name+f' leaf {i+1} '+label,p(u,.040,off),p(u,2.052,off),.032,.022,opening_col,aluminium)
        for label,z in [('bottom',.056),('top',2.036)]:
            vr_beam(name+f' leaf {i+1} '+label,p(u0+.032,z,off),p(u1-.032,z,off),.022,.032,opening_col,aluminium)
        # Beam local X is the short perpendicular dimension for these vertical panes.
        ob=vr_box(name+f' glass {i+1}',(-width/2+.032,-.003,-.982),(width/2-.032,.003,.982),opening_col,glazing)
        ob.location=p((u0+u1)/2,1.046,off);ob.rotation_euler.z=math.atan2(t.y,t.x)
    door_basis.append({'name':name,'width_m':length,'height_m':2.1,'panels':3})

# The orthogonal frames share one slim corner joint, with no doubled corner solid.
stacker('D05 meals leg',(corner_x-3.6,corner_y),(corner_x,corner_y))
stacker('D05 family leg',(corner_x,corner_y-.055),(corner_x,corner_y-3.0))
# Close the scheduled opening's 640 mm head band; retain existing beams inside it.
solid('D05 meals bulkhead',([corner_x-3.6,corner_y+.320,2.1],[corner_x+.320,corner_y+.330,2.74]),linings,plaster)
solid('D05 meals outer head',([corner_x-3.6,corner_y-.075,2.1],[corner_x-.075,corner_y-.065,2.74]),linings,plaster)
solid('D05 meals head soffit',([corner_x-3.6,corner_y-.065,2.1],[corner_x+.320,corner_y+.320,2.11]),linings,plaster)
solid('D05 family bulkhead',([corner_x+.320,corner_y-3,2.1],[corner_x+.330,corner_y+.330,2.74]),linings,plaster)
solid('D05 family outer head',([corner_x-.075,corner_y-3,2.1],[corner_x-.065,corner_y-.075,2.74]),linings,plaster)
solid('D05 family head soffit',([corner_x-.065,corner_y-3,2.1],[corner_x+.320,corner_y-.065,2.11]),linings,plaster)
solid('D05 meals bulkhead end',([corner_x-3.61,corner_y-.075,2.1],[corner_x-3.60,corner_y+.330,2.74]),linings,plaster)
solid('D05 family bulkhead end',([corner_x-.075,corner_y-3.01,2.1],[corner_x+.330,corner_y-3.0,2.74]),linings,plaster)

# Garage ceiling uses the actual garage footprint and same removable finish group.
pieces=[([0,2.46,2.644],[6.38,9.37,2.654])]
for core in cores: pieces=[piece for box in pieces for piece in subtract(box,core)]
for piece in pieces: solid('Garage ceiling',piece,linings,plaster)

# Two 590 mm alfresco brick piers enclose the steel posts in the finished view.
for prefix in ('C1 alfresco west','C1 alfresco middle'):
    column=bpy.data.objects[prefix+' baseplate']; cx,cy=column.location.x,column.location.y
    for i,(a,b) in enumerate([
        ((cx-.295,cy-.295,-.28),(cx-.185,cy+.295,2.60)),
        ((cx+.185,cy-.295,-.28),(cx+.295,cy+.295,2.60)),
        ((cx-.185,cy-.295,-.28),(cx+.185,cy-.185,2.60)),
        ((cx-.185,cy+.185,-.28),(cx+.185,cy+.295,2.60))]):
        solid(prefix+f' brick pier face {i}',(a,b),bpy.data.collections['23 Ground brick veneer'],bpy.data.materials['ENV Brick veneer - colour unselected'])

# Complete the raised theatre platform rather than leaving an apparent loose frame.
platform=[o for o in house.objects if o.name.startswith('Theatre platform')]
pb=[vr_bounds(o) for o in platform]
lo=[min(b[i][0] for b in pb) for i in range(3)];hi=[max(b[i][1] for b in pb) for i in range(3)]
# Finish against the room faces; the traced platform left a narrow side slot.
lo[0]=22.593535; lo[1]=.105
solid('Theatre platform deck',([lo[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]+.019]),linings,deck)
solid('Theatre raised skirting west',([lo[0],lo[1],hi[2]+.019],[lo[0]+.007,hi[1],hi[2]+.089]),linings,plaster)
solid('Theatre raised skirting south',([lo[0]+.007,lo[1],hi[2]+.019],[hi[0],lo[1]+.007,hi[2]+.089]),linings,plaster)
for name,a,b in [
 ('front', [hi[0],lo[1],3.159],[hi[0]+.01,hi[1],hi[2]+.019]),
 ('back', [lo[0]-.01,lo[1],3.159],[lo[0],hi[1],hi[2]+.019]),
 ('left', [lo[0]-.01,lo[1]-.01,3.159],[hi[0]+.01,lo[1],hi[2]+.019]),
 ('right',[lo[0]-.01,hi[1],3.159],[hi[0]+.01,hi[1]+.01,hi[2]+.019])]:
    solid('Theatre platform fascia '+name,(a,b),linings,plaster)

# Door casings finish the thin, bare returns without narrowing the clear opening.
for rec in walls:
    a,b=rec['start'],rec['end'];t=(b-a).normalized();n=Vector((-t.y,t.x,0))
    for tag,c,w,s,h in rec['openings']:
        if s>.001 or tag.startswith('W'): continue
        for sign in (-1,1):
            for u0,u1,z0,z1 in [(c-w/2-.045,c-w/2,.019 if rec['z']>1 else 0,h),
                               (c+w/2,c+w/2+.045,.019 if rec['z']>1 else 0,h),
                               (c-w/2-.045,c+w/2+.045,h,h+.045)]:
                p=a+t*u0+n*(sign*.060)+Vector((0,0,z0));q=a+t*u1+n*(sign*.070)+Vector((0,0,z1))
                solid('Door casing '+tag,([min(p[i],q[i]) for i in range(3)],[max(p[i],q[i]) for i in range(3)]),linings,plaster)
changes.append({'object':'Interior finish coordination','action':'Added garage ceiling, glazed D05 corner stacker, finished door material, doorway casings and theatre platform deck/fascias'})

# Finish the entry canopy over the existing 5-degree porch trusses. All three
# finish materials belong to the roof toggle, preserving the exposed structure.
roof_cover=bpy.data.collections['20 Main roof covering']
roof_trim=bpy.data.collections['22 Fascia and gutters']
roof_metal=bpy.data.materials['ENV Metal roof - colour unselected']
cx0,cx1,cy0,cy1=27.09,28.36,4.45,8.015
def canopy_z(x): return 3.173+(27.235-x)*math.tan(math.radians(5))
vr_extrude('Entry canopy roof',[(cx0,canopy_z(cx0)),(cx1,canopy_z(cx1)),
    (cx1,canopy_z(cx1)+.012),(cx0,canopy_z(cx0)+.012)],cy0,cy1,roof_cover,roof_metal)
for i in range(12):
    y=cy0+.06+i*.305
    vr_extrude(f'Entry canopy standing seam {i}',[(cx0,canopy_z(cx0)+.012),(cx1,canopy_z(cx1)+.012),
        (cx1,canopy_z(cx1)+.032),(cx0,canopy_z(cx0)+.032)],y,y+.015,roof_cover,roof_metal)
for name,ya,yb in [('south',cy0,cy0+.018),('north',cy1-.018,cy1)]:
    vr_extrude('Entry canopy '+name+' fascia',[(cx0,2.535),(cx1-.018,2.535),
        (cx1-.018,canopy_z(cx1-.018)),(cx0,canopy_z(cx0))],ya,yb,roof_trim,plaster)
vr_box('Entry canopy front fascia',(cx1-.018,cy0,2.535),(cx1,cy1,canopy_z(cx1)),roof_trim,plaster)
vr_box('Entry canopy lined soffit',(cx0,cy0+.018,2.525),(cx1,cy1-.018,2.535),roof_trim,plaster)
vr_box('Entry canopy gutter base',(cx1,cy0,3.00),(cx1+.09,cy1,3.012),roof_trim,roof_metal)
vr_box('Entry canopy gutter face',(cx1+.078,cy0,3.012),(cx1+.09,cy1,3.09),roof_trim,roof_metal)
for y in (cy0,cy1-.012):
    vr_box('Entry canopy gutter end',(cx1,y,3.012),(cx1+.078,y+.012,3.09),roof_trim,roof_metal)

# Close the exposed floor edge over the alfresco, aligned to the upper render.
solid('Alfresco front fascia',([6.28,-.1,2.59],[12.99,-.09,3.14]),linings,plaster)
solid('Alfresco west fascia',([6.27,-.1,2.59],[6.28,2.46,3.14]),linings,plaster)
pieces=[([6.28,-.09,2.59],[corner_x,2.46,2.60]),
        ([8.539317,2.46,2.59],[corner_x,corner_y,2.60])]
for core in cores: pieces=[piece for box in pieces for piece in subtract(box,core)]
for prefix in ('C1 alfresco west','C1 alfresco middle'):
    p=bpy.data.objects[prefix+' baseplate'].location
    cut=([p.x-.295,p.y-.295,0],[p.x+.295,p.y+.295,3])
    pieces=[piece for box in pieces for piece in subtract(box,cut)]
for piece in pieces: solid('Alfresco continuous soffit',piece,linings,plaster)
changes.append({'object':'Entry canopy and alfresco','action':'Completed matching pitched metal canopy with fascia, soffit and gutter; enclosed exposed alfresco floor edge and added continuous lower soffit'})

# Garage covering follows the actual T5 truss pitch (5 degrees, high at rear).
def garage_z(y): return 3.587+(y-9.05)*math.tan(math.radians(5))
def garage_panel(name,x0,x1,y0,y1,bottom,top,mat):
    verts=[(x,y,f(y)) for x in (x0,x1) for y in (y0,y1) for f in (bottom,top)]
    return vr_mesh(name,verts,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],roof_cover if mat==roof_metal else roof_trim,mat)
gx0,gx1,gy0,gy1=-.25,6.398,2.26,9.57
garage_panel('Garage metal roof',gx0,gx1,gy0,gy1,garage_z,lambda y:garage_z(y)+.012,roof_metal)
for i in range(22):
    x=gx0+.04+i*.30
    garage_panel(f'Garage standing seam {i}',x,x+.015,gy0,gy1,lambda y:garage_z(y)+.012,lambda y:garage_z(y)+.032,roof_metal)
for name,x0,x1,y0,y1 in [('west',gx0,gx0+.018,gy0,gy1),('east',gx1-.018,gx1,gy0,gy1),
                       ('south',gx0+.018,gx1-.018,gy0,gy0+.018),('north',gx0+.018,gx1-.018,gy1-.018,gy1)]:
    garage_panel('Garage '+name+' fascia',x0,x1,y0,y1,lambda y:2.74,garage_z,plaster)
vr_box('Garage gutter base',(gx0,gy0-.10,2.93),(gx1,gy0,2.942),roof_trim,roof_metal)
vr_box('Garage gutter face',(gx0,gy0-.10,2.942),(gx1,gy0-.088,3.02),roof_trim,roof_metal)
for x in (gx0,gx1-.012):
    vr_box('Garage gutter end',(x,gy0-.088,2.942),(x+.012,gy0,3.02),roof_trim,roof_metal)
for batten in [o for o in house.objects if o.name.startswith('Garage batten')]:
    assert max((batten.matrix_world@Vector(v)).z-garage_z((batten.matrix_world@Vector(v)).y) for v in batten.bound_box)<0
solid('House floor edge above garage',([6.27,2.46,2.74],[6.28,7.98,3.14]),linings,plaster)
changes.append({'object':'Garage roof','action':'Completed metal covering on measured T5 pitch, seams, perimeter fascia and gutter; retained roof toggle'})
(OUT/'opening-coordination.json').write_text(json.dumps({'d05':door_basis,'corner':[corner_x,corner_y],
 'source':'Architectural sheets 07 and 11; frame profiles illustrative','garage_ceiling':True,'theatre_platform_finished':True},indent=2))
