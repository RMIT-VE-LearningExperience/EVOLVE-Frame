import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { Box3, Mesh, Vector3 } from 'three';
import {
  initialState,
  modelKeys,
  visiblePart,
  validateNavigation,
  type Part,
} from './explorer.ts';
const manifest = JSON.parse(
  await readFile(
    new URL('../public/models/manifest.json', import.meta.url),
    'utf8',
  ),
);
void test('navigation accepts valid state and rejects invalid or unrelated fields', () => {
  assert.deepEqual(validateNavigation({ model: 'window', explosion: 0.5 }), {
    model: 'window',
    stage: 0,
    cutaway: false,
    explosion: 0.5,
    hidden: [],
    selected: null,
  });
  for (const input of [
    null,
    [],
    {},
    { model: 'unknown' },
    { model: 'building', stage: 4 },
    { model: 'building', stage: 1.3 },
    { model: 'window', explosion: NaN },
    { model: 'window', explosion: 2 },
    { model: 'window', cutaway: 1 },
    { model: 'window', delete: true },
  ])
    assert.throws(() => validateNavigation(input));
});
for (const key of modelKeys)
  void test(`${key}: load GLB, verify geometry and layer metadata`, async () => {
    const file = await readFile(
      new URL(`../public/models/${key}.glb`, import.meta.url),
    );
    assert.equal(file.byteLength, manifest.models[key].bytes);
    const gltf = await new GLTFLoader().parseAsync(
      file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength),
      '',
    );
    const bounds = new Box3().setFromObject(gltf.scene),
      size = bounds.getSize(new Vector3());
    assert.ok(size.x > 1 && size.y > 1 && size.z > 0);
    assert.ok(size.toArray().every(Number.isFinite));
    const meshes: Mesh[] = [];
    gltf.scene.traverse((o) => {
      if (o instanceof Mesh) meshes.push(o);
    });
    assert.equal(meshes.length, manifest.models[key].batches);
    for (const mesh of meshes) {
      const p = mesh.userData as Part;
      assert.ok(p.key);
      assert.ok(p.label);
      assert.equal(p.explode.length, 3);
      assert.ok(p.explode.every(Number.isFinite));
      assert.ok(
        manifest.models[key].parts.some((part: Part) => part.key === p.key),
      );
      assert.ok(mesh.geometry.attributes.position.count > 0);
    }
    if (key === 'building') {
      // Hidden components previously collapsed to overlapping unit cubes here.
      for (const mesh of meshes) {
        const pos = mesh.geometry.attributes.position;
        for (let i = 0; i < pos.count; i++)
          assert.ok(
            Math.max(
              Math.abs(pos.getX(i)),
              Math.abs(pos.getY(i)),
              Math.abs(pos.getZ(i)),
            ) > 0.501,
            'Unexpected geometry at the export origin',
          );
        if (String(mesh.userData.key).startsWith('20 ')) {
          mesh.geometry.computeBoundingBox();
          assert.ok(
            mesh.geometry.boundingBox!.min.y > 5,
            'Roof covering below roof datum',
          );
        }
        assert.ok(
          mesh.geometry.attributes.uv,
          'Missing member texture coordinates',
        );
        assert.ok(
          mesh.userData.material_kind,
          'Missing material classification',
        );
      }
      const counts = [0, 1, 2, 3].map(
        (stage) =>
          meshes.filter((m) =>
            visiblePart(m.userData as Part, { ...initialState, stage }),
          ).length,
      );
      assert.ok(counts[0] > 0);
      assert.ok(counts.every((n, i) => i === 0 || n > counts[i - 1]));
      assert.ok(
        meshes.filter((m) =>
          visiblePart(m.userData as Part, {
            ...initialState,
            stage: 3,
            cutaway: true,
          }),
        ).length < counts[3],
      );
      assert.ok(size.x > 25 && size.x < 30 && size.y > 7 && size.y < 10);
    }
    const p = meshes[0].userData as Part;
    assert.equal(
      visiblePart(p, {
        ...initialState,
        model: key,
        stage: 3,
        hidden: [p.key],
      }),
      false,
    );
  });
