"""Extract all drawing text and render reference sheets. Run via uv --with pymupdf."""
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'tmp' / 'plans'
DEST.mkdir(parents=True, exist_ok=True)
for filename, prefix, selected in [
    ('Leichhardt_Architectural Plans (1).pdf', 'arch', [6, 7, 8, 11, 12]),
    ('Leichhardt_Engineering Plans (1).pdf', 'engineering', [9, 10, 11, 12, 13, 18, 19]),
    ('Leichhardt_Engineering Roof Truss Frame (1).pdf', 'roof', None),
    ('Leichhardt_Engineering Subfloor Frame (1).pdf', 'floor', None),
]:
    doc = pymupdf.open(ROOT / filename)
    print(f'{prefix}: {len(doc)} pages')
    parts = []
    for i, page in enumerate(doc, 1):
        content = page.get_text()
        parts.append(f'\n--- PAGE {i} ---\n{content}')
        if selected is None or i in selected:
            page.get_pixmap(matrix=pymupdf.Matrix(2400/page.rect.width, 2400/page.rect.width), alpha=False).save(DEST / f'{prefix}-{i:02d}.png')
    (DEST / f'{prefix}.txt').write_text(''.join(parts), encoding='utf-8')
