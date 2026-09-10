from pathlib import Path
import json,pdfplumber
root=Path(__file__).resolve().parents[1]
files={ 'A':'Leichhardt_Architectural Plans (1).pdf','S':'Leichhardt_Engineering Plans (1).pdf','R':'Leichhardt_Engineering Roof Truss Frame (1).pdf','F':'Leichhardt_Engineering Subfloor Frame (1).pdf'}
definitions=[('A',7,'REF_A07_Floor_1',100),('A',8,'REF_A08_Floor_2',100),('A',6,'REF_A06_Slab',100),('A',3,'REF_A03_Site_Roof',125),('A',9,'REF_A09_Elevations',100),('A',10,'REF_A10_Elevations',100),('A',12,'REF_A12_Section_AA',50),('S',3,'REF_S02_Footing_Slab',100),('S',10,'REF_S09_First_Floor_Framing',100),('S',12,'REF_S11_Roof_Framing',100),('S',19,'REF_S18_Ground_Bracing',100),('S',20,'REF_S19_First_Bracing',100),('R',22,'REF_Roof_Truss_Layout',100),('F',47,'REF_Subfloor_Layout',100),('S',11,'REF_S10_Framing_Schedule',100),('A',11,'REF_A11_Opening_Schedule',100)]
# PDF vector dimension tick centres, top-left PDF coordinate convention.
# Sheet A07 red upper-wall inner-face lines independently check the A08 alignment.
calibrations={
 3:dict(x0=295.0938,x1=975.4092,y0=306.8078,y1=522.2408,dx=30000,dy=9500,model_x=0,model_y=0),
 12:dict(x0=312.0768,x1=337.59,y0=377.555,y1=532.8932,dx=450,dy=2740,model_x=-450,model_y=0),
 7:dict(x0=211.0248,x1=1016.9154,y0=284.8424,y1=554.1332,dx=28430,dy=9500,model_x=0,model_y=0),
 8:dict(x0=378.9288,x1=968.8176,y0=308.0138,y1=537.053,dx=20810,dy=8080,model_x=6130,model_y=50),
 6:dict(x0=275.4252,x1=1081.314,y0=231.503,y1=500.7938,dx=28430,dy=9500,model_x=0,model_y=0)}
rows=[]
for package,page,name,scale in definitions:
 with pdfplumber.open(root/files[package]) as pdf:
  q=pdf.pages[page-1]; width,height=q.width,q.height
 mm_per_pt=scale*25.4/72
 x=y=0
 status='REFERENCE ONLY - nominal sheet scale; alignment/calibration pending'
 controls=None
 c=calibrations.get(page) if package=='A' else None
 if package=='R':
  c=dict(x0=229.8,x1=672.36,y0=207.96,y1=377.16,dx=20610,dy=7880,model_x=6230,model_y=150)
 if package=='F':
  c=dict(x0=149.76,x1=684.96,y0=186.84,y1=391.44,dx=20610,dy=7880,model_x=6230,model_y=150)
 if package=='S' and page in (3,10,12,19,20):
  bounds={3:(282.72,1088.64,176.72,446.0),10:(197.28,1003.2,88.88,358.16),12:(297.78,887.64,156.8,385.82),19:(170.34,976.20,148.58,417.92),20:(352.08,941.94,204.86,433.94)}[page]
  upper=page in (12,20)
  c=dict(x0=bounds[0],x1=bounds[1],y0=bounds[2],y1=bounds[3],dx=20810 if upper else 28430,dy=8080 if upper else 9500,model_x=6130 if upper else 0,model_y=50 if upper else 0)
 if c:
  mm_per_pt=c['dx']/(c['x1']-c['x0'])
  ycheck=(c['y1']-c['y0'])*mm_per_pt
  assert abs(ycheck-c['dy'])<5,(package,page,ycheck)
  x=c['model_x']-c['x0']*mm_per_pt
  y=c['model_y']-(height-c['y1'])*mm_per_pt
  controls={**c,'mm_per_point':mm_per_pt,'y_check_mm':ycheck,'y_error_mm':ycheck-c['dy']}
  status=f"CALIBRATED: {c['dx']} mm horizontal / {c['dy']} mm vertical; residual {ycheck-c['dy']:.3f} mm. " + ('Section-local X / GF FFL Z=0.' if package=='A' and page==12 else 'Local GF reference origin.')
  if package=='S':
   status=status.replace('CALIBRATED:', 'REGISTERED TO ARCHITECTURAL WRITTEN EXTENTS:')+' Underlay alignment only; do not derive structural dimensions by scaling.'
 rows.append(dict(name=name,file=str(root/files[package]),page=page,scale=scale,width_mm=width*mm_per_pt,x_mm=x,y_mm=y,status=status,controls=controls))
(root/'output/revit/reference_manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([r for r in rows if r['controls']],indent=2))
