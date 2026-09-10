import pdfplumber,json,collections
pdf=pdfplumber.open('Leichhardt_Engineering Subfloor Frame (1).pdf');p=pdf.pages[46]
print('VERT EDGES',[(round(s['x0'],2),round(s['top'],2),round(s['bottom'],2)) for s in p.edges if s['width']<.01 and s['height']>20 and 148<s['x0']<175 and 185<s['top']<392])
words=p.extract_words(line_dir_rotated='ttb',char_dir_rotated='ltr',extra_attrs=['non_stroking_color'])
print('LABELS',[(w['text'],round(w['x0'],2),round(w['x1'],2),round(w['top'],2),round(w['bottom'],2)) for w in words if 'FJ' in w['text'] or 'JF' in w['text']])
p=pdf.pages[1];print('COLORS',collections.Counter(str(s.get('non_stroking_color')) for s in p.curves+p.rects if s.get('fill')))
print('FILLS',[(s['object_type'],s['non_stroking_color'],s['width'],s['height']) for s in p.curves+p.rects if s.get('fill') and 200<s['top']<500][:20])
