"""Correct explicit pane layouts and privacy glazing without screen-space blur."""
window_finish_report=[]
clear_glass=bpy.data.materials['ENV Glazing proxy']
aluminium=bpy.data.materials['ENV Aluminium frames - illustrative']
privacy_glass=vr_material('VR Obscure privacy glazing',(.80,.84,.83))
privacy_glass.diffuse_color=(.80,.84,.83,.94)
privacy_bs=privacy_glass.node_tree.nodes.get('Principled BSDF')
privacy_bs.inputs['Base Color'].default_value=(.80,.84,.83,1)
privacy_bs.inputs['Roughness'].default_value=.72
privacy_bs.inputs['Alpha'].default_value=.94

def window_part(root,name,lo,hi,material):
    col=root.users_collection[0]
    ob=vr_box(name,lo,hi,col,material);ob.parent=root
    ob['source']='Architectural sheet11; frame sections illustrative'
    return ob

root=bpy.data.objects['OPENING | W09 void']
for ob in list(root.children):
    if 'glass' in ob.name or 'mullion' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
window_part(root,'W09 void | single fixed glass',(-1.355+.045,-.003,.045),(1.355-.045,.003,1.755),clear_glass)
window_finish_report.append({'window':'W09','layout':'Single fixed light; generic3-pane subdivision removed','basis':'Written2710x1800 and fixed-light diagram on11'})

root=bpy.data.objects['OPENING | W01 bed 1']
for ob in list(root.children):
    if 'glass' in ob.name or 'mullion' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
# Diagram shows a narrow full-height fixed sidelight beside three stacked
# awning panels. The900/2100 split is scaled from the diagram, not dimensioned.
divider=-.600;bar=.035
window_part(root,'W01 bed 1 | sidelight mullion',(divider-bar/2,-.030,.045),(divider+bar/2,.030,2.355),aluminium)
window_part(root,'W01 bed 1 | fixed sidelight glass',(-1.455,-.003,.045),(divider-bar/2,.003,2.355),clear_glass)
for z in (.815,1.585):
    window_part(root,'W01 bed 1 | awning transom',(divider+bar/2,-.030,z-bar/2),(1.455,.030,z+bar/2),aluminium)
for i,(low,high) in enumerate(((.045,.7975),(.8325,1.5675),(1.6025,2.355))):
    window_part(root,f'W01 bed 1 | awning glass {i+1}',(divider+bar/2,-.003,low),(1.455,.003,high),clear_glass)
window_finish_report.append({'window':'W01','layout':'Fixed sidelight and3 stacked awning panes',
 'basis':'Sheet11 topology;900mm side panel is scaled, subdivision dimensions unverified'})
for tag in ('W03 powder','W07 ensuite','W12 bath','W13 WC','W16 bath 2'):
    root=bpy.data.objects['OPENING | '+tag]
    for ob in root.children:
        if ob.type=='MESH' and 'glass' in ob.name:
            ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(privacy_glass)
    window_finish_report.append({'window':tag,'glazing':'Obscure privacy finish','basis':'Explicitly marked OBSCURE GLAZING on11'})
bpy.context.view_layer.update()
(OUT/'window-finish-coordination.json').write_text(json.dumps(window_finish_report,indent=2))
changes.append({'object':'Window schedule finishes','action':'W09 fixed pane, W01 sidelight/3-stack layout, obscure glazing for5 wet-room windows. No runtime blur or refraction.'})
