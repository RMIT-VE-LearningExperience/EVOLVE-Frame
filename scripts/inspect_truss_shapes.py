import pdfplumber,json,collections
with pdfplumber.open('Leichhardt_Engineering Roof Truss Frame (1).pdf') as pdf:
 for n in [2,3,5,6,7,20,21,22]:
  p=pdf.pages[n-1]
  shapes=[s for s in p.curves+p.rects if s.get('fill')]
  print('PAGE',n,collections.Counter(str(s.get('non_stroking_color')) for s in shapes))
  if n==2:print(json.dumps(shapes[:10],indent=2))
