import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { hotspots, availableHotspots, studyHotspots } from './hotspots.ts';
import {
  foundationParts,
  initialState,
  modelKeys,
  modelParts,
  type Part,
} from './explorer.ts';
const manifest = JSON.parse(
  await readFile(
    new URL('../public/models/manifest.json', import.meta.url),
    'utf8',
  ),
);
const parts = manifest.models.building.parts as Part[];
void test('building teaching topics reference model or system layers and identify their evidence status', () => {
  assert.equal(hotspots.length, 13);
  assert.equal(new Set(hotspots.map((h) => h.id)).size, hotspots.length);
  const allParts = [
    ...parts,
    ...foundationParts.waffle,
    ...foundationParts.raised,
  ];
  for (const h of hotspots) {
    assert.ok(allParts.some((p) => p.key === h.part));
    assert.ok(
      h.what &&
        h.purpose &&
        h.connects &&
        h.question &&
        h.basis &&
        h.reference &&
        h.status,
    );
    if (h.detail) assert.ok(modelKeys.includes(h.detail));
  }
});
void test('hotspots follow stage, hidden layers, cutaway and model navigation', () => {
  const waffleParts = modelParts(parts, initialState);
  assert.equal(availableHotspots(initialState, waffleParts).length, 8);
  assert.equal(
    availableHotspots(
      { ...initialState, stage: 0, foundationDetail: true },
      waffleParts,
    ).length,
    2,
  );
  assert.equal(
    availableHotspots({ ...initialState, model: 'window' }, []).length,
    0,
  );
  assert.equal(
    availableHotspots(
      { ...initialState, hidden: hotspots.map((h) => h.part) },
      waffleParts,
    ).length,
    0,
  );
  assert.equal(
    availableHotspots(
      { ...initialState, cutaway: true },
      waffleParts.map((p) => ({ ...p, cut: true })),
    ).length,
    0,
  );
  assert.match(hotspots.find((h) => h.id === 'garage')!.basis, /UNRESOLVED/);
});
void test('each detached study has named hotspots for every layer and hides them with the layer', () => {
  for (const model of modelKeys.filter((m) => m !== 'building')) {
    const parts = manifest.models[model].parts as Part[];
    const all = studyHotspots(model, parts);
    assert.equal(all.length, parts.length);
    assert.equal(new Set(all.map((h) => h.id)).size, parts.length);
    assert.deepEqual(
      all.map((h) => h.part),
      parts.map((p) => p.key),
    );
    assert.ok(all.every((h) => h.title && !/^\d+\s/.test(h.title)));
    assert.equal(
      availableHotspots({ ...initialState, model, explosion: 1 }, parts).length,
      parts.length,
    );
    assert.equal(
      availableHotspots(
        { ...initialState, model, hidden: parts.map((p) => p.key) },
        parts,
      ).length,
      0,
    );
  }
});
