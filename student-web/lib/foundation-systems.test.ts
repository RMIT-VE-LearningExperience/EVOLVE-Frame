import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  foundationParts,
  initialState,
  visiblePart,
} from './explorer.ts';

void test('foundation switching never leaves the incompatible teaching system visible', () => {
  for (const foundation of ['waffle', 'raised'] as const) {
    const state = { ...initialState, foundation, stage: 6 };
    for (const [system, parts] of Object.entries(foundationParts))
      for (const part of parts)
        assert.equal(
          visiblePart(part, state),
          system === foundation && !part.detailOnly,
        );
  }
});

void test('concealed details replace covering layers and follow construction stages', () => {
  const raised = foundationParts.raised;
  const stageZero = { ...initialState, foundation: 'raised' as const, stage: 0 };
  assert.ok(
    visiblePart(raised.find((p) => p.key.endsWith('bearers'))!, stageZero),
  );
  assert.equal(
    visiblePart(raised.find((p) => p.key.endsWith('joists'))!, stageZero),
    false,
  );
  const detailed = { ...stageZero, stage: 1, foundationDetail: true };
  assert.ok(
    visiblePart(
      raised.find((p) => p.key.endsWith('service penetration'))!,
      detailed,
    ),
  );
  assert.equal(
    visiblePart(
      raised.find((p) => p.key.endsWith('sheet flooring'))!,
      detailed,
    ),
    false,
  );
});
