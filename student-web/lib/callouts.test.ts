import { test } from 'node:test';
import assert from 'node:assert/strict';
import { layoutCallouts } from './callouts.ts';
void test('callout rails avoid overlap, screen edges, controls, and their attachment point', () => {
  for (const width of [320, 480, 800, 1200]) {
    const anchors = Array.from({ length: 12 }, (_, i) => ({
      id: String(i),
      x: width / 2 + i * 2,
      y: 300 + i * 3,
    }));
    const labels = layoutCallouts(anchors, width, 700);
    assert.ok(labels.length > 0);
    for (const label of labels) {
      assert.ok(label.left >= 0 && label.left + label.width <= width);
      assert.ok(label.top >= 140 && label.top + 48 < 700 - 180);
      assert.ok(
        Math.hypot(label.circleX - label.x, label.circleY - label.y) >= 56,
      );
      assert.ok(label.top >= 240 || label.left + label.width <= width - 70);
      for (const other of labels.filter((l) => l !== label)) {
        assert.ok(
          label.left + label.width <= other.left ||
            other.left + other.width <= label.left ||
            label.top + 48 <= other.top ||
            other.top + 48 <= label.top,
        );
      }
    }
  }
});
void test('offscreen anchors and tiny surfaces safely fall back to the text list', () => {
  assert.deepEqual(layoutCallouts([{ id: 'x', x: -20, y: 300 }], 800, 700), []);
  assert.deepEqual(layoutCallouts([{ id: 'x', x: 100, y: 100 }], 240, 300), []);
});
