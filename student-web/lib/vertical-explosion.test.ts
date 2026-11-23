import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  buildingExplosionHeight,
  initialState,
  verticalExplosionOffset,
  visiblePart,
  type Part,
} from './explorer.ts';
import { availableHotspots } from './hotspots.ts';
const part = (stage: number): Part => ({
  key: '26 Windows and doors',
  stage,
  cut: false,
  label: '',
  note: '',
  explode: [],
});
void test('building systems separate vertically while the ground frame stays anchored', () => {
  const state = { ...initialState, explosion: 1 };
  assert.equal(
    verticalExplosionOffset(
      { ...part(0), key: '02 Ground floor walls' },
      state,
    ),
    0,
  );
  assert.equal(
    verticalExplosionOffset(
      { ...part(0), key: '04 First floor joists' },
      state,
    ),
    11.25,
  );
  assert.equal(
    verticalExplosionOffset(
      { ...part(0), key: '20 Main roof covering' },
      state,
    ),
    51,
  );
  assert.equal(
    verticalExplosionOffset(
      { ...part(0), key: '20 Main roof covering' },
      { ...state, explosion: 0.5 },
    ),
    25.5,
  );
  assert.equal(buildingExplosionHeight(state), 51);
  assert.equal(
    verticalExplosionOffset(
      { ...part(0), key: '10 Stair framing' },
      state,
    ),
    0,
  );
});
void test('vertical explosion preserves visibility rules and only affects the building', () => {
  assert.equal(
    visiblePart(part(0), { ...initialState, hidden: [part(0).key] }),
    false,
  );
  assert.equal(
    visiblePart(part(2), { ...initialState, stage: 0 }),
    false,
  );
  assert.equal(
    visiblePart(
      { ...part(2), cut: true },
      { ...initialState, cutaway: true },
    ),
    false,
  );
  assert.equal(
    availableHotspots({ ...initialState, stage: 0 }, [part(2)]).length,
    0,
  );
  assert.equal(
    verticalExplosionOffset(part(3), {
      ...initialState,
      model: 'window',
      explosion: 1,
    }),
    0,
  );
});
