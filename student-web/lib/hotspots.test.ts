import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { hotspots, availableHotspots } from './hotspots.ts';
import { initialState, modelKeys, type Part } from './explorer.ts';
const manifest = JSON.parse(
  await readFile(
    new URL('../public/models/manifest.json', import.meta.url),
    'utf8',
  ),
);
const parts = manifest.models.building.parts as Part[];
void test('six unique teaching topics reference exported layers and valid studies', () => {
  assert.equal(hotspots.length, 6);
  assert.equal(new Set(hotspots.map((h) => h.id)).size, 6);
  for (const h of hotspots) {
    assert.ok(parts.some((p) => p.key === h.part));
    assert.ok(h.what && h.purpose && h.question && h.basis);
    if (h.detail) assert.ok(modelKeys.includes(h.detail));
  }
});
void test('hotspots follow stage, hidden layers, cutaway and model navigation', () => {
  assert.equal(availableHotspots(initialState, parts).length, 6);
  assert.equal(
    availableHotspots({ ...initialState, stage: 0 }, parts).length,
    5,
  );
  assert.equal(
    availableHotspots({ ...initialState, model: 'window' }, parts).length,
    0,
  );
  assert.equal(
    availableHotspots(
      { ...initialState, hidden: hotspots.map((h) => h.part) },
      parts,
    ).length,
    0,
  );
  assert.equal(
    availableHotspots(
      { ...initialState, cutaway: true },
      parts.map((p) => ({ ...p, cut: true })),
    ).length,
    0,
  );
  assert.match(hotspots.find((h) => h.id === 'garage')!.basis, /UNRESOLVED/);
});
