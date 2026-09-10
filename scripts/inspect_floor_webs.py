import pdfplumber,collections,json
p=pdfplumber.open('Leichhardt_Engineering Subfloor Frame (1).pdf').pages[1]
wood=[s for s in p.curves+p.rects if s.get('fill') and isinstance(s.get('non_stroking_color'),tuple) and len(s['non_stroking_color'])==3 and .9<s['non_stroking_color'][0]<1 and .65<s['non_stroking_color'][1]<.82 and .3<s['non_stroking_color'][2]<.5]
l=min(s['x0'] for s in wood);r=max(s['x1'] for s in wood);t=min(s['top'] for s in wood);b=max(s['bottom'] for s in wood)
print(l,r,t,b)
for s in p.curves+p.rects:
 if s['x0']>=l-.1 and s['x1']<=r+.1 and s['top']>=t-.1 and s['bottom']<=b+.1 and s['height']>10:
  print(s['object_type'],s.get('fill'),s.get('non_stroking_color'),s.get('stroking_color'),len(s['pts']),[s[k] for k in ['x0','x1','top','bottom']])
