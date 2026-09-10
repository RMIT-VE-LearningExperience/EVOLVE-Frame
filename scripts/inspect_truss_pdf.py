import pdfplumber,json
p=pdfplumber.open('Leichhardt_Engineering Roof Truss Frame (1).pdf').pages[21]
print(p.width,p.height)
print('GARAGE',[(round(l['x0'],3),round(l['top'],3),round(l['bottom'],3)) for l in p.edges if abs(l['x0']-l['x1'])<0.1 and l['height']>100 and 98<l['x0']<233])
print('PORCH',[(round(l['x0'],3),round(l['x1'],3),round(l['top'],3)) for l in p.edges if abs(l['top']-l['bottom'])<0.1 and l['width']>15 and 670<l['x0']<705 and 209<l['top']<280])
