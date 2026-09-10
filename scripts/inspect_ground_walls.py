import pdfplumber
p=pdfplumber.open('Leichhardt_Architectural Plans (1).pdf').pages[6]
S=35.277741;X=211.0248;Y=554.1332
result=set()
for l in p.edges:
 x=(l['x0']-X)*S;y0=(Y-l['bottom'])*S;y1=(Y-l['top'])*S
 if abs(l['x0']-l['x1'])<.01 and 17500<x<20500 and l['height']*S>300 and 100<y0<4400 and 300<y1<5000:result.add((round(x),round(y0),round(y1)))
print('ENS VERTICAL',sorted(result))
result=set()
for l in p.edges:
 x0=(l['x0']-X)*S;x1=(l['x1']-X)*S;y=(Y-l['top'])*S
 if abs(l['top']-l['bottom'])<.01 and 17500<x0<27000 and x1-x0>300 and 3900<y<4800:result.add((round(x0),round(x1),round(y)))
print('NORTH HORIZ',sorted(result))
result=set()
for l in p.edges:
 x=(l['x0']-X)*S;y0=(Y-l['bottom'])*S;y1=(Y-l['top'])*S
 if abs(l['x0']-l['x1'])<.01 and 22500<x<23000 and l['height']*S>200 and 100<y0<4700 and 300<y1<4800:result.add((round(x),round(y0),round(y1)))
print('BED VERTICAL',sorted(result))
print('GARAGE ACCESS',sorted(set((round((l['x0']-X)*S),round((Y-l['bottom'])*S),round((Y-l['top'])*S)) for l in p.edges if l['width']<.01 and 6200<(l['x0']-X)*S<6330 and l['height']*S>200 and 2500<(Y-l['bottom'])*S<7000 and (Y-l['top'])*S<8100)))
