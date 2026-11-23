"""Above-ground drainage reconstruction from sheets02/04/05/07/08/14.

Marker setout is scaled. Routes/products and falls are illustrative, not a
hydraulic design. Retained structural members are not cut for these routes.
"""
dr_report={'source_sheets':[2,4,5,7,8,14],'pipes':[],'sumps':[],'cuts':[],
 'unresolved':['DP06 changes X between GF07 and FF08/roof04; dogleg above W07 is inferred.',
 'DP03 shifted within end nib to clear retained W02; exact location not dimensioned.',
 'Second garage sump drawn08/14 but omitted04; three total follows08.',
 'Gutter cross sections, rainhead products, overflow and underground drainage design are unspecified.',
 'Porch180-wide channel clears retained T6;300-square sump placed between trusses. This is a visual coordination choice.'],
 'scope':'Above-ground educational reconstruction.90mm diameter per sheet05, straps<=1800 per02; no engineering compliance claim.'}
dr_col=roof_trim
dr_mat=roof_metal

def dr_box(name,lo,hi):return vr_box('Drainage | '+name,lo,hi,dr_col,dr_mat)

def dr_channel(name,x0,x1,y0,y1,z,top,sump_centres):
    pieces=[([x0,y0,z-.004],[x1,y1,z])]
    for sx,sy in sump_centres:
        cut=([sx-.150,sy-.150,z-.01],[sx+.150,sy+.150,z+.01])
        pieces=[p for b in pieces for p in subtract(b,cut)]
    for i,piece in enumerate(pieces):dr_box(name+f' floor{i}',*piece)
    for label,lo,hi in [('A',(x0,y0,z),(x0+.004,y1,top)),('B',(x1-.004,y0,z),(x1,y1,top)),
      ('C',(x0+.004,y0,z),(x1-.004,y0+.004,top)),('D',(x0+.004,y1-.004,z),(x1-.004,y1,top))]:
        # Sumps can extend beyond a narrow channel: cut the intervening wall.
        parts=[(lo,hi)]
        for sx,sy in sump_centres:
            parts=[p for b in parts for p in subtract(b,([sx-.150,sy-.150,z-.01],[sx+.150,sy+.150,top+.01]))]
        for p in parts:dr_box(name+' wall'+label,*p)
    for i,(sx,sy) in enumerate(sump_centres):
        lo=[sx-.150,sy-.150,z-.150];hi=[sx+.150,sy+.150,z]
        dr_box(name+f' sump{i} bottom',lo,(hi[0],hi[1],lo[2]+.004))
        for label,a,b in [('A',(lo[0],lo[1],lo[2]+.004),(lo[0]+.004,hi[1],hi[2])),
                         ('B',(hi[0]-.004,lo[1],lo[2]+.004),(hi[0],hi[1],hi[2])),
                         ('C',(lo[0]+.004,lo[1],lo[2]+.004),(hi[0]-.004,lo[1]+.004,hi[2])),
                         ('D',(lo[0]+.004,hi[1]-.004,lo[2]+.004),(hi[0]-.004,hi[1],hi[2]))]:
            dr_box(name+f' sump{i} side'+label,a,b)
            # Continue perimeter upstands above the gutter floor; leave the
            # channel-facing edge open so water can enter the recessed sump.
            upper=([a[0],a[1],z],[b[0],b[1],top])
            for piece in subtract(upper,([x0+.004,y0+.004,z-.001],[x1-.004,y1-.004,top+.001])):
                dr_box(name+f' sump{i} rim'+label,*piece)
        dr_report['sumps'].append({'name':name+f' sump{i}','bounds':[lo,hi],'nominal_mm':[300,300,150]})

# Replace sloped covering footprints; keep clear of the existing truss ends.
for dr_ob in list(house.objects):
    if dr_ob.name=='Garage concealed metal roof main':
        bpy.data.objects.remove(dr_ob,do_unlink=True)
        dr_ob=garage_panel('Garage concealed metal roof main',.110,6.279,2.725,9.405,garage_z,lambda y:garage_z(y)+.012,roof_metal)
        dr_ob.data.materials[0]=photo_garage_metal
    elif dr_ob.name=='Entry concealed roof':bpy.data.objects.remove(dr_ob,do_unlink=True)
dr_channel('Garage box gutter',.110,6.279,2.425,2.725,2.950,3.045,[(.280,2.575),(6.050,2.575)])
# Porch sump protrudes inward only between T6-4 and T6-5, so no truss is cut.
dr_porch_sump=(28.245,7.390)
for dr_name,x0,x1,y0,y1 in [('main',27.235,28.215,4.925,7.240),('sump return',27.235,28.095,7.240,7.540)]:
    vr_extrude('Entry concealed roof '+dr_name,[(x0,photo_roof_z(x0)),(x1,photo_roof_z(x1)),
       (x1,photo_roof_z(x1)+.012),(x0,photo_roof_z(x0)+.012)],y0,y1,roof_cover,roof_metal)
for dr_cut in [([28.215,4.925,3.220],[28.395,7.540,3.260]),([28.095,7.240,3.220],[28.395,7.540,3.260])]:
    detail_cut_objects([o for o in house.objects if o.type=='MESH' and o.name.startswith('Photo revision | Porch front beam cap')],dr_cut,dr_report['cuts'])
dr_channel('Porch box gutter',28.215,28.395,4.925,7.540,2.990,3.140,[dr_porch_sump])

def dr_open_outlet(identifier,point):
    bpy.context.view_layer.update()
    p=Vector(point)
    candidates=[o for o in house.objects if o.type=='MESH' and (o.name.startswith('gutter base') or o.name.startswith('Drainage | '+identifier+' rainhead floor'))]
    for o in candidates:
        bb=detail_box_bounds(o)
        if not (bb[0][0]+.060-.00002<=p.x<=bb[1][0]-.060+.00002 and bb[0][1]+.060-.00002<=p.y<=bb[1][1]-.060+.00002 and bb[0][2]-.01<=p.z<=bb[1][2]+.01):continue
        col=o.users_collection[0]
        cut=([p.x-.060,p.y-.060,bb[0][2]-.001],[p.x+.060,p.y+.060,bb[1][2]+.001])
        detail_replace_box(o,subtract(bb,cut))
        verts=[]
        for z,inner in [(bb[0][2],False),(bb[0][2],True),(bb[1][2],True),(bb[1][2],False)]:
            for i in range(16):
                c=math.cos(2*math.pi*i/16);s=math.sin(2*math.pi*i/16)
                radius=.045 if inner else .060/max(abs(c),abs(s))
                verts.append((p.x+radius*c,p.y+radius*s,z))
        faces=[]
        for ring in range(4):
            nxt=(ring+1)%4
            faces.extend((ring*16+i,ring*16+(i+1)%16,nxt*16+(i+1)%16,nxt*16+i) for i in range(16))
        vr_mesh('Drainage | '+identifier+' open gutter outlet',verts,faces,col,dr_mat)
        p.z=bb[0][2]
        dr_report.setdefault('open_outlets',[]).append({'id':identifier,'position':list(p),'diameter_mm':90})
        return tuple(p)
    raise AssertionError(('No gutter/rainhead floor for outlet',identifier,list(p)))

def dr_pipe(identifier,kind,points,wall_axis,wall_face,strap_levels,source_location):
    points=list(points);points[0]=dr_open_outlet(identifier,points[0])
    ob=detail_pipe('Drainage | '+identifier+' '+kind,points,.045,dr_col,dr_mat,16,True)
    ob['source']=source_location;ob['status']='Scaled route; educational reconstruction'
    # Each clamp follows the vertical stem at the requested height.
    mounts=[]
    for z in strap_levels:
        seg=next(((Vector(a),Vector(b)) for a,b in zip(points,points[1:]) if abs(a[0]-b[0])<1e-5 and abs(a[1]-b[1])<1e-5 and min(a[2],b[2])<=z<=max(a[2],b[2])),None)
        assert seg,(identifier,z)
        p=seg[0].copy();p.z=z
        face=wall_face(z) if callable(wall_face) else wall_face
        mount=p.copy();mount[wall_axis]=face
        # Collar is a narrow ring, with its back fastened to the wall.
        collar=[p+Vector((.048*math.cos(2*math.pi*i/12),.048*math.sin(2*math.pi*i/12),0)) for i in range(13)]
        detail_pipe('Drainage | '+identifier+' strap',collar,.006,dr_col,dr_mat,4,True)
        end=p.copy();end[wall_axis]+=(1 if face>p[wall_axis] else -1)*.048
        detail_pipe('Drainage | '+identifier+' bracket',[end,mount],.008,dr_col,dr_mat,6)
        mounts.append({'z':z,'wall_point':list(mount),'pipe_point':list(p)})
    assert all(b-a<=1.8001 for a,b in zip(sorted(strap_levels),sorted(strap_levels)[1:]))
    dr_report['pipes'].append({'id':identifier,'kind':kind,'diameter_mm':90,'centreline':points,'mounts':mounts,'source_location':source_location,
       'basis':'Scaled marker, joined elbows and inferred above-ground route; not designed pipework.'})
    return ob

for dr_id,x in [('DP01',6.73),('DP02',15.23),('DP03',26.59)]:
    dr_pipe(dr_id,'DP',[(x,8.50,5.559),(x,8.50,5.38),(x,8.10,5.02),(x,8.10,-.27)],1,lambda z:7.980 if z>3.14 else 8.030,[.35,1.90,3.45,4.90],'East/page-top wall07/08; DP03 end-nib adjustment explicitly logged.')
for dr_id,x,y,face in [('DP04',6.425,-.32,lambda z:-.25 if z<2.6 else -.10),('DP05',13.12,-.22,lambda z:-.15 if z<3.14 else -.10),('DP07',26.50,-.22,lambda z:-.15 if z<3.14 else -.10)]:
    dr_pipe(dr_id,'DP',[(x,-.62,5.559),(x,-.62,5.38),(x,y,5.02),(x,y,-.27)],1,face,[.35,1.90,3.45,4.90],'West/page-bottom07/08, DP04 against alfresco pier.')
dr_pipe('DP06','DP',[(19.30,-.62,5.559),(19.30,-.62,5.38),(19.30,-.22,5.02),(19.30,-.22,3.05),
       (18.14,-.22,2.65),(18.14,-.22,-.27)],1,lambda z:-.15 if z<3.14 else -.10,[.35,1.90,3.45,4.90],
       '07 ground marker near18.14 versus08/04 upper marker near19.30; inferred dogleg above W07.')
dr_pipe('DP08','DP',[(27.61,.18,5.559),(27.61,.18,5.38),(27.21,.18,5.02),(27.21,.18,-.27)],0,
       lambda z:27.090 if z>3.14 else 27.140,[.35,1.90,3.45,4.90],
       'South/page-right wall near lower corner;750 labels W01 setback, not pipe centre.')

def dr_rainhead(identifier,x,y,face,outward,sump,z):
    # Hollow open rainhead,300 wide,220 projecting and300 high. Product size
    # is illustrative. Its connecting scupper is also opened through masonry.
    xa,xb=x-.150,x+.150;ya,yb=sorted((face,face+outward*.220))
    for label,lo,hi in [('floor',(xa,ya,z-.300),(xb,yb,z-.296)),('left',(xa,ya,z-.296),(xa+.004,yb,z)),
       ('right',(xb-.004,ya,z-.296),(xb,yb,z)),('back',(xa+.004,ya,z-.296),(xb-.004,ya+.004,z)),
       ('front',(xa+.004,yb-.004,z-.296),(xb-.004,yb,z))]:dr_box(identifier+' rainhead '+label,lo,hi)
    scupper_z=z-.160
    cut=([x-.051,min(sump[1],y)-.02,scupper_z-.051],[x+.051,max(sump[1],y)+.02,scupper_z+.051])
    candidates=[o for o in house.objects if o.type=='MESH' and (o.name.startswith(('Photo revision | Garage south parapet','Photo revision | Porch pier1')) or o.name.startswith('Drainage | '+identifier+' rainhead') or ('sump' in o.name and o.name.startswith('Drainage | '))) and 'cap' not in o.name]
    detail_cut_objects(candidates,cut,dr_report['cuts'])
    route=[(sump[0],sump[1],scupper_z)]
    if abs(sump[0]-x)>.001:route.append((x,sump[1],scupper_z))
    route.append((x,y,scupper_z))
    detail_pipe('Drainage | '+identifier+' sump scupper',route,.05,dr_col,dr_mat,12,True)
    dr_pipe(identifier,'DP/RWH',[(x,y,z-.300),(x,y,-.27)],1,face,[.30,1.55,2.60],
       'Rainhead symbol07/08; connected to300x300x150 sump. Rainhead shape and scupper route illustrative.')

dr_rainhead('DP10',.280,2.240,2.3135,-1,(.280,2.575),3.020)
dr_rainhead('DP11',6.050,2.240,2.3135,-1,(6.050,2.575),3.020)
dr_rainhead('DP09',28.320,8.200,8.130,1,dr_porch_sump,3.060)

for identifier,x,y,outx,outy,bottom,face in [('DP12',6.16,7.65,5.76,7.65,3.70,6.280),('DP13',27.20,7.65,27.61,7.65,3.42,27.090)]:
    route=[(outx,outy,5.559),(outx,outy,5.38),(x,y,5.02),(x,y,bottom if identifier=='DP12' else 3.52)]
    if identifier=='DP13':route.append((27.65,7.15,bottom))
    dr_pipe(identifier,'S/DP',route,0,face,
       [bottom+.30,4.90],'08 filled marker: upper roof spreader onto garage/porch; lower roof location scaled.')
    if identifier=='DP13':x,y=27.65,7.15
    # A visible horizontal spreader at roof level, with four downward outlets.
    detail_pipe('Drainage | '+identifier+' spreader',[(x,y-.30,bottom),(x,y+.30,bottom)],.045,dr_col,dr_mat,12)
    for j in range(4):
        yy=y-.225+j*.15
        detail_pipe('Drainage | '+identifier+f' spreader outlet{j}',[(x,yy,bottom),(x,yy,bottom-.09)],.022,dr_col,dr_mat,8,True)

bpy.context.view_layer.update()
dr_counts={kind:sum(r['kind']==kind for r in dr_report['pipes']) for kind in ('DP','DP/RWH','S/DP')}
assert dr_counts=={'DP':8,'DP/RWH':3,'S/DP':2}
assert len(dr_report['sumps'])==3
assert len(dr_report['open_outlets'])==13
dr_report['counts']=dr_counts
# No drainage solid may project across scheduled glass in elevation. Test
# every route segment's expanded envelope, not only the sparse window rays.
dr_aperture_failures=[]
for opening in [o for o in house.objects if o.name.startswith('OPENING | W')]:
    axis=0 if abs((opening.matrix_world.to_quaternion()@Vector((0,1,0))).x)>.5 else 1
    across=1-axis
    panes=[o for o in opening.children if o.type=='MESH' and 'glass' in o.name]
    for pane in panes:
        bb=vr_bounds(pane)
        for row in dr_report['pipes']:
            for a,b in zip(row['centreline'],row['centreline'][1:]):
                # Ignore pipes belonging to the opposite facade.
                if min(abs(a[axis]-bb[axis][0]),abs(b[axis]-bb[axis][0]))>1:continue
                if min(max(a[across],b[across])+.045,bb[across][1])-max(min(a[across],b[across])-.045,bb[across][0])>0 and min(max(a[2],b[2])+.045,bb[2][1])-max(min(a[2],b[2])-.045,bb[2][0])>0:
                    dr_aperture_failures.append([row['id'],pane.name])
dr_report['window_projection_conflicts']=dr_aperture_failures
(ad_out/'drainage.json').write_text(json.dumps(dr_report,indent=2))
assert not dr_aperture_failures,dr_aperture_failures
changes.append({'object':'Drainage046','action':'8 downpipes,3 rainheads,2 spreaders,connected garage/porch channels and3 sumps;90mm pipes; source conflicts explicit.'})
print('ARCH046_DRAINAGE_PASS',dr_counts,flush=True)
