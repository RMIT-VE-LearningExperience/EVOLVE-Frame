"""Compare saved model measurements with explicitly cited drawing dimensions."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/timber_frame/audit'
data=json.loads((OUT/'measured_geometry.json').read_text())
objects={r['name']:r for r in data['objects']}
def plate(name):return objects[name+' | top plate lower']
def face(name,axis,side):return plate(name)['bounds'][axis][side]
def gap(low,high,axis):return (face(high,axis,0)-face(low,axis,1))*1000
def mm(value):return round(value*1000,1)
rows=[]
def check(id,item,current,target,source,confidence,action):
 rows.append({'id':id,'item':item,'model_mm':round(current,1),'drawing_mm':target,
              'difference_mm':round(current-target,1),'source':source,'confidence':confidence,'proposed_action':action})
check('A01','W04 kitchen sill height',objects['GF North wall | W04 kitchen sill']['bounds'][2][1]*1000,905,
      'Architectural sheet 11, W04','Confirmed schedule mismatch','Lower the W04 opening assembly by 514 mm; rebuild associated cripple studs and check the lintel/head.')
check('A02a','Garage clear X between timber faces',gap('Garage outer end','GF Laundry west',0),6000,
      'Architectural sheet 07, garage 6000','Nominal wall-face mismatch','Re-establish garage wall setout from the 6000/90/240 dimension chain; keep the adjoining house reference fixed.')
check('A02b','Garage clear Y between timber faces',gap('Garage south','Garage rear',1),6500,
      'Architectural sheet 07, garage 6500 / overall 6980','Nominal wall-face mismatch','Resolve both garage ends with the 1320 projection and roof supplier 6680 overall; do not shift only one roof edge.')
check('A03','Ground-floor WIR clear width',gap('Ensuite WIR division','WIR bedroom division',0),2270,
      'Architectural sheet 07, WIR 2270','Nominal wall-face mismatch','Re-set the bedroom/WIR/ensuite partition chain from the entry-end wall, including 4000 bedroom and 90 partitions.')
check('A04','Upper Bath 2 clear width',gap('FF Bath 2 west','FF Bath 2 east',0),2200,
      'Architectural sheet 08, bath 2200 in lower dimension chain','Nominal wall-face mismatch','Re-set Bath 2 east wall with the adjoining Bed 2/study chain; check its door and W16 relationship.')
check('A05a','Stair side-wall clear zone',gap('FF stair balustrade','FF North wall',1),1100,
      'Architectural sheet 08, stairs 1100','Nominal wall-face mismatch','Move the dwarf wall about 68 mm toward the exterior wall, subject to final lining basis; keep the corrected stair centreline.')
check('A05b','Void clear width to entry-end wall',gap('FF void balustrade','FF East wall',0),2550,
      'Architectural sheet 08, void 2550','Nominal wall-face mismatch','Coordinate dwarf-wall return and floor-edge trimmer; nominal east face of the return should be X=24.350 m, not X=24.539 m.')
check('A06','D05 model header underside',objects['Alfresco D05 north head']['bounds'][2][0]*1000,2100,
      'Architectural sheet 11 D05 height 2100; sheet 07 corner opening','Opening assembly incomplete','Coordinate both corner heads and jambs to the 3600 + 3000 by 2100 opening. Do not infer clear width from beam length.')
check('A07','Garage wall base versus garage slab datum',objects['Garage rear | bottom plate']['bounds'][2][0]*1000,-86,
      'Architectural sheet 07 garage FFL 10.820 vs house 10.906','Confirmed model datum mismatch','Reconcile garage wall base, wall height and roof bearing together. Current garage roof chord base is already 86 mm below the model wall top.')
check('A08a','T5 model bottom chord overall horizontal length',objects['T5-01 bottom']['local_dimensions'][2]*1000,6680,
      'Roof truss PDF page 20 (printed 19), maximum transport width 6680','Confirmed omitted chord extensions','Rebuild T5 using the shop end extensions and bearing positions; 6150 is the listed span, not the whole bottom-chord extent.')
check('A08b','T6 model bottom chord overall horizontal length',objects['T6-1 bottom']['local_dimensions'][2]*1000,1395,
      'Roof truss PDF page 21 (printed 20), maximum transport width 1395','Confirmed omitted chord extensions','Rebuild T6 with 345 and 100 end extensions and specified bearing positions; retain the 950 span definition.')
floor_objects=[o for o in objects.values() if o['name'].startswith('FJ-') and ('top chord' in o['name'] or 'bottom chord' in o['name'])]
floor_low=min(o['bounds'][2][0] for o in floor_objects)
floor_high=max(o['bounds'][2][1] for o in floor_objects)
check('A09','Floor frame overall vertical zone',(floor_high-floor_low)*1000,413,
      'Subfloor shop sheets (e.g. PDF page 2) and layout page 47; architectural sheet 12 shows 400','Drawing conflict / coordination required','Resolve the 400 architectural floor zone versus 413 supplier overall before changing upper floor, stairs or roof levels; map the separate 360 shower members.')
study_brace=objects['FF Study D diagonal']
check('A10','Study-side D bracing bay horizontal projection',abs(study_brace['matrix'][1][2])*1000,2400,
      'Engineering S19, D2400 on study/retreat partition','Confirmed bracing bay-length mismatch','Re-set the brace endpoints to the specified 2400 bay on the corrected wall; preserve the type-D cross arrangement.')

room_checks=[
 ('GF Bedroom 1 width',gap('WIR bedroom division','GF East entry and bedroom',0),4000,'Arch 07'),
 ('FF Bedroom 4 width',gap('FF West wall','FF Bed 4 WC division',0),4680,'Arch 08'),
 ('FF Bedroom 5 width',gap('FF Bed 5 west','FF Bed 5 east',0),4310,'Arch 08'),
 ('FF Bed 2 including robe zone',gap('FF Bath 2 east','FF Bed 2 study division',0),4000,'Arch 08 lower chain'),
 ('FF Study width',gap('FF Bed 2 study division','FF Study retreat division',0),2400,'Arch 08'),
 ('FF Retreat width',gap('FF Study retreat division','FF Theatre west',0),3000,'Arch 08'),
 ('FF Theatre width',gap('FF Theatre west','FF East wall',0),4300,'Arch 08'),
 ('FF Bedroom 4 depth',gap('FF Bed 4 and robes','FF North wall',1),3200,'Arch 08'),
]
return_ob=plate('FF void balustrade')
trimmer=objects['Floor rim/trimmer 7']
return_gap=mm(return_ob['bounds'][0][0]-trimmer['bounds'][0][1])
extras={
 'upper_timber_envelope_mm':[mm(face('FF East wall',0,1)-face('FF West wall',0,0)),mm(face('FF North wall',1,1)-face('FF South wall',1,0))],
 'dwarf_return_to_trimmer_horizontal_gap_mm':return_gap,
 'garage_wall_top_mm':mm(face('Garage rear',2,1)+.045),
 'garage_roof_chord_bottom_mm':mm(objects['T5-01 bottom']['bounds'][2][0]),
 'floor_chord_zone_mm':[mm(floor_low),mm(floor_high)],
 'additional_room_comparisons':[{'item':n,'model_mm':round(v,1),'drawing_mm':t,'difference_mm':round(v-t,1),'source':s} for n,v,t,s in room_checks],
 'named_scheduled_members_not_found':[tag for tag in ['ST2','HC1','1L8','1L9'] if not any(o.startswith(tag+' ') for o in objects)]
}
(OUT/'position_audit.json').write_text(json.dumps({'audited_file':data['file'],'checks':rows,'other_measurements':extras},indent=2))
lines=['# Leichhardt frame positioning audit','',
 'Audited file: `Leichhardt_Timber_Frame_Stairs_Corrected.blend`. This is the saved stair-corrected revision containing the user edits preserved on 7 September 2026. No Blender model was changed during this audit. The original inventory/setout files predate the stair correction; measurements below were extracted from the actual corrected Blender file.','',
 'The audit identifies confirmed schedule/model mismatches, nominal architectural setout discrepancies, and unresolved differences between source drawings. A nominal wall-face comparison uses the faces of the 90 mm timber model. The architectural lining/finished-face convention still needs confirming before final millimetre setout; small residuals alone do not establish a misplaced wall.','',
 '## Findings and proposed corrections','',
 '| ID | Item | Model mm | Drawing mm | Difference mm | Basis |',
 '|---|---|---:|---:|---:|---|']
for r in rows:lines.append(f"| {r['id']} | {r['item']} | {r['model_mm']:,.1f} | {r['drawing_mm']:,} | {r['difference_mm']:+,.1f} | {r['confidence']} |")
lines+=['','Difference means model minus drawing. For A08, the comparison is overall chord extent, not span. For A09, 413 mm is a conflicting supplier dimension, not an approved replacement datum.','']
for r in rows:lines += [f"**{r['id']} — {r['item']}**",'',f"Source: {r['source']}. {r['proposed_action']}",'']
lines += ['## Stair surround: correction not yet complete','',
 f"The corrected stair flight is now 4000 mm with 2000 mm entry-end clearance, but its surrounding walls were preserved in the previous edit. The dwarf-wall return is physically offset from the floor-edge trimmer: the nearest horizontal faces have a {return_gap:.1f} mm gap. That is a model coordination defect independent of the nominal architectural clear-width comparison. The side dwarf wall and return need to be corrected together with their support edges. The previous stair update did not establish a fully coordinated stair/landing assembly.",'',
 'Architectural sheet 07 labels a 3190 mm ground-floor stair dimension while sheet 08 labels 4000 mm. The latest stair revision follows sheet 08. This difference remains unresolved; do not call the staircase fabrication-ready or revise unrelated supporting members solely to make either drawing fit.','',
 '## Other room dimension checks','',
 '| Room / nominal span | Model mm | Drawing mm | Difference mm | Source |','|---|---:|---:|---:|---|']
for n,v,t,s in room_checks:lines.append(f'| {n} | {v:,.1f} | {t:,} | {v-t:+,.1f} | {s} |')
lines += ['','These are connected dimension chains. Do not apply each difference as an independent wall translation: correcting Bath 2 changes the adjoining Bed 2 width, and correcting the WIR changes the bedroom and ensuite relationships. Residuals around 20–35 mm require the lining/face convention and tracing precision to be checked before declaring an error.','',
 '## Items requiring further detailing, not a guessed move','',
 '- **Alfresco corner:** model headers are approximately 4140 and 3595 mm long; schedule D05 gives two nominal clear openings of 3600 and 3000 mm. Those are different measurement types. Jamb and support details must establish the openings before a positional correction can be prescribed.',
 '- **Window/door horizontal centres:** many were manually traced. This audit confirms the W04 vertical mistake, but does not certify every opening centre or installation allowance. Re-measure opening centres from written setout dimensions after walls are corrected.',
 '- **Special hip trusses:** main roof envelope and typical T1 assemblies exist, but hip girders, truncated trusses and jacks were simplified. Rebuild their types and positions from roof shop sheets and the final supplier layout; the envelope alone does not verify them.',
 '- **Steel/LVL schedule coverage:** no explicitly named ST2, HC1, 1L8 or 1L9 assemblies were found. Generic lintels may represent some areas; reconcile objects against S09/S10 visually before labelling each member absent or adding duplicates.',
 '- **Lintel and stud packs:** the generator uses generic packs and can limit lintel depth to the available head space. Check actual sizes and bearings against S12/S13 after opening and level coordination; do not shift whole walls to accommodate the simplified lintels.',
 '- **Wet areas:** the model has a uniform 400 mm floor zone. The supplier layout includes 360 shower members and recess details; local lowered top chords and their supports have not been reproduced.',
 '- **Bracing:** S19 shows a C2700 bay on the horizontal Bed 4/robe partition; there is no corresponding diagonal object on that wall in the model. S18 shows two D1800 bays along the ensuite-side wall, while the model represents that wall with one long cross. These are arrangement/coverage errors, not just translations. Reconcile the remaining bays and connections after wall setout.',
 '- **Theatre platform:** the 2300 mm model width follows a written dimension, but its support geometry and the interpretation of the 420 mm step remain schematic. Resolve its footprint/levels against architectural sheet 08 before detailing supports.','',
 '## Checks that do match the stated model basis','',
 '- Main upper timber outer envelope measures 20610 x 7880 mm, matching the supplier envelope. Architectural 20810 x 8080 includes the different exterior build-up and is not a reason to enlarge this timber rectangle.',
 '- The corrected stair tread run is 4000 mm and its entry-end gap is 2000 mm, as selected from architectural sheet 08. Rough tread width remains an assumed 1020 mm centred within the 1100 mm architectural zone.',
 '- The saved model has 15 standard T1, eight T5 and five T6 assemblies; count alone does not validate support location or special-truss geometry.',
 '- Main roof nominal pitch is 25 degrees and the model uses the supplier 550 mm overhang. Architectural section 12 shows 450 mm, so this remains a documented drawing difference rather than an automatic 100 mm translation.',
 '- Nominal ground and upper wall heights remain 2740 and 2590 mm from architectural section 12. Treating ceiling heights as top-of-frame datums remains an assumption; the floor/finish build-up needs resolving before approving Z positions.','',
 '## Correction sequence','',
 '1. Establish one reference coordinate system and identify which drawing dimensions refer to timber, masonry, linings or finished faces. Resolve the stair dimension and floor-depth conflicts before final supporting-member/level changes.',
 '2. Re-set the garage and the WIR/bedroom/ensuite and upper Bath 2/Bed 2/study wall chains. Keep the verified main upper timber envelope as the initial reference. Validate room dimensions and junctions.',
 '3. Coordinate the stair side wall, void return, floor trimmers, landing and bearing members as one assembly. Confirm the saved 4000 stair interpretation against the selected drawing basis.',
 '4. Correct W04, then check all other opening centres, heights and lintels. Resolve the complete D05 corner opening with the structural support plan.',
 '5. Correct garage base/roof bearing levels and rebuild T5/T6 chord extensions and bearings. Detail the supplier floor system, wet-area recesses and special hip trusses.',
 '6. Complete the steel/LVL, bracing, stud-pack and platform audit; regenerate previews and the component inventory from the resulting model.','',
 'Implement by group in a new revision, retain the current file, and check that unrelated geometry has not changed. This report authorises no automatic model edits; it is the requested correction plan.','',
 '## Evidence','',
 '- [Architectural plans — sheets 07, 08, 11, 12](../../../Leichhardt_Architectural%20Plans%20(1).pdf)',
 '- [Engineering plans — S09, S10, S12/S13 and S18/S19](../../../Leichhardt_Engineering%20Plans%20(1).pdf)',
 '- [Roof truss shop drawings and final layout](../../../Leichhardt_Engineering%20Roof%20Truss%20Frame%20(1).pdf)',
 '- [Subfloor shop drawings and final layout](../../../Leichhardt_Engineering%20Subfloor%20Frame%20(1).pdf)',
 '- `measured_geometry.json`: measured saved-object transforms, bounds and source metadata.',
 '- `position_audit.json`: comparison values and classifications.','']
(OUT/'POSITION_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'checks':rows,'other_measurements':extras},indent=2))
