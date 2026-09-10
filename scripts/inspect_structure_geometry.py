import pdfplumber,collections
p=pdfplumber.open('Leichhardt_Engineering Plans (1).pdf').pages[9]
print(p.width,p.height,collections.Counter(str(s.get('non_stroking_color')) for s in p.curves+p.rects if s.get('fill')))
for s in p.curves+p.rects:
 if s.get('fill') and 195<s['x0']<1005 and 85<s['top']<360 and max(s['width'],s['height'])>20:print(s['object_type'],s.get('non_stroking_color'),[round(s[k],2) for k in ['x0','x1','top','bottom']])
