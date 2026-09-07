import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { initialState, type Part } from './explorer.ts';
import { groupLayers, toggleLayers } from './layer-groups.ts';
const manifest = JSON.parse(
  await readFile(
    new URL('../public/models/manifest.json', import.meta.url),
    'utf8',
  ),
);
void test('categories include every exported layer exactly once in every study', () => {
  for (const [model, data] of Object.entries(manifest.models)) {
    const parts = (data as { parts: Part[] }).parts;
    const grouped = groupLayers(parts, model === 'building').flatMap((g) =>
      g.parts.map((p) => p.key),
    );
    assert.deepEqual(grouped.sort(), parts.map((p) => p.key).sort());
    assert.equal(grouped.length, new Set(grouped).size);
  }
});
void test('group hide, partial restore, and individual toggle preserve unrelated layers', () => {
  const parts = manifest.models.building.parts as Part[];
  const group = groupLayers(parts, true)[0].parts;
  const s = { ...initialState, hidden: ['unrelated'], selected: group[0].key };
  const hidden = toggleLayers(s, group);
  assert.equal(hidden.selected, null);
  assert.ok(group.every((p) => hidden.hidden.includes(p.key)));
  const partial = toggleLayers(hidden, [group[0]]);
  assert.ok(!partial.hidden.includes(group[0].key));
  const restored = toggleLayers(partial, group);
  assert.deepEqual(restored.hidden, ['unrelated']);
  assert.deepEqual(s.hidden, ['unrelated']);
});
void test('group actions cannot reveal future stages or cutaway faces', () => {
  const parts = manifest.models.building.parts as Part[];
  const state = {
    ...initialState,
    stage: 0,
    cutaway: true,
    hidden: parts.map((p) => p.key),
  };
  const result = toggleLayers(state, parts);
  for (const p of parts)
    assert.equal(result.hidden.includes(p.key), p.stage > 0 || p.cut);
  const unavailable = parts.filter((p) => p.stage > 0);
  assert.equal(toggleLayers(state, unavailable), state);
});
