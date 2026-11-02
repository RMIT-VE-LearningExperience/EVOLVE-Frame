'use client';
/* oxlint-disable next/no-img-element -- Static fallback assets; no runtime image service. */
import { useEffect, useRef, useState } from 'react';
import {
  RotateCcw,
  RotateCw,
  Plus,
  Minus,
  Maximize2,
  MoveVertical,
} from 'lucide-react';
import type { Part, ViewState } from '@/lib/explorer';
import {
  buildingExplosionHeight,
  foundationParts,
  verticalExplosionOffset,
  visiblePart,
} from '@/lib/explorer';
import type * as THREE from 'three';
import { Switch } from '@/components/ui/switch';
import { studyHotspots, type Hotspot } from '@/lib/hotspots';
import { layoutCallouts } from '@/lib/callouts';
import { studyLights, shadowType, environmentIntensity } from '@/lib/lighting';

type Engine = {
  apply: (s: ViewState) => void;
  action: (a: string) => void;
  setVerticalMove: (enabled: boolean) => void;
  setWalkthrough: (enabled: boolean) => void;
  setViewpoint: (view: 'overview' | 'entry' | 'ground' | 'upper') => void;
  dispose: () => void;
};
export default function ModelViewer({
  state,
  onSelect,
  fallback,
  detailed,
  onQualityChange,
  hotspots,
  onHotspot,
  parts,
  onWalkthroughStart,
}: {
  state: ViewState;
  onSelect: (key: string | null) => void;
  fallback: string;
  detailed: boolean;
  onQualityChange: (value: boolean) => void;
  hotspots: Hotspot[];
  onHotspot: (hotspot: Hotspot) => void;
  parts: Part[];
  onWalkthroughStart: () => void;
}) {
  const mount = useRef<HTMLDivElement>(null),
    engine = useRef<Engine | null>(null),
    latest = useRef(state),
    select = useRef(onSelect);
  const hotspotState = useRef(hotspots),
    hotspotSelect = useRef(onHotspot),
    verticalMoveState = useRef(false),
    walkthroughState = useRef(false);
  useEffect(() => {
    hotspotState.current = hotspots;
    hotspotSelect.current = onHotspot;
    engine.current?.apply(latest.current);
  }, [hotspots, onHotspot]);
  const [status, setStatus] = useState('Loading 3D model…'),
    [ready, setReady] = useState(false),
    [attempt, setAttempt] = useState(0),
    [verticalMove, setVerticalMove] = useState(false),
    [walkthrough, setWalkthrough] = useState(false),
    [viewpoint, setViewpoint] = useState<
      'overview' | 'entry' | 'ground' | 'upper'
    >('overview');
  useEffect(() => {
    verticalMoveState.current = verticalMove;
    engine.current?.setVerticalMove(verticalMove);
  }, [verticalMove]);
  useEffect(() => {
    walkthroughState.current = walkthrough;
    engine.current?.setWalkthrough(walkthrough);
  }, [walkthrough]);
  useEffect(() => {
    latest.current = state;
    select.current = onSelect;
    engine.current?.apply(state);
  }, [state, onSelect]);
  useEffect(() => {
    let cancelled = false,
      cleanup: (() => void) | undefined;
    async function init() {
      const [
        T,
        { OrbitControls },
        { GLTFLoader },
        { RoomEnvironment },
        { displayMaterial },
      ] = await Promise.all([
        import('three'),
        import('three/addons/controls/OrbitControls.js'),
        import('three/addons/loaders/GLTFLoader.js'),
        import('three/addons/environments/RoomEnvironment.js'),
        import('@/lib/model-materials'),
      ]);
      if (cancelled || !mount.current) return;
      const host = mount.current;
      const renderer = new T.WebGLRenderer({ antialias: true, alpha: false });
      renderer.setPixelRatio(
        Math.min(window.devicePixelRatio, detailed ? 2 : 1),
      );
      renderer.setClearColor('#252a40');
      renderer.outputColorSpace = T.SRGBColorSpace;
      renderer.toneMapping = T.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      renderer.shadowMap.enabled = detailed;
      renderer.shadowMap.type = shadowType;
      renderer.domElement.setAttribute(
        'aria-label',
        'Interactive 3D model. Drag to orbit, pinch or scroll to zoom, then use vertical move mode or Shift-drag to pan up and down.',
      );
      renderer.domElement.setAttribute('role', 'img');
      host.appendChild(renderer.domElement);
      const scene = new T.Scene(),
        camera = new T.PerspectiveCamera(38, 1, 0.01, 1000),
        controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = false;
      controls.maxPolarAngle = Math.PI * 0.93;
      const { sky, sun } = studyLights(detailed);
      scene.add(sky);
      const pmrem = new T.PMREMGenerator(renderer),
        studio = new RoomEnvironment();
      const environment = pmrem.fromScene(studio, 0.04);
      scene.environment = environment.texture;
      scene.environmentIntensity = environmentIntensity;
      studio.dispose();
      pmrem.dispose();
      scene.add(sun, sun.target);
      // Assigned after asynchronous loading; disposal can run before it resolves.
      // oxlint-disable-next-line prefer-const
      let root: THREE.Group | undefined;
      const meshes: THREE.Mesh[] = [];
      const baseMaterials = new WeakMap<
        THREE.Material,
        { opacity: number; transparent: boolean; depthWrite: boolean }
      >();
      let radius = 1,
        baseHeight = 1,
        framedExplosion = -1,
        groundFloorY = 0,
        walkthroughEnabled = false;
      const center = new T.Vector3();
      const navigationBounds = new T.Box3();
      const markers: {
        button: HTMLButtonElement;
        number: HTMLSpanElement;
        point: THREE.Vector3;
        mesh: THREE.Mesh;
        line: SVGPolylineElement;
        hotspot: Hotspot;
      }[] = [];
      const leaders = document.createElementNS(
        'http://www.w3.org/2000/svg',
        'svg',
      );
      leaders.classList.add('hotspot-leaders');
      leaders.setAttribute('aria-hidden', 'true');
      host.appendChild(leaders);
      const render = () => {
        if (!cancelled) {
          renderer.render(scene, camera);
          const anchors = markers.flatMap((marker) => {
            const p = marker.mesh
              .localToWorld(marker.point.clone())
              .project(camera);
            const x = ((p.x + 1) * host.clientWidth) / 2,
              y = ((1 - p.y) * host.clientHeight) / 2;
            return marker.mesh.visible &&
              p.z > -1 &&
              p.z < 1 &&
              x >= 0 &&
              x <= host.clientWidth &&
              y >= 0 &&
              y <= host.clientHeight &&
              hotspotState.current.some((h) => h.id === marker.hotspot.id)
              ? [
                  {
                    id: marker.hotspot.id,
                    x,
                    y,
                    selected: latest.current.selected === marker.hotspot.part,
                  },
                ]
              : [];
          });
          const positions = layoutCallouts(
            anchors,
            host.clientWidth,
            host.clientHeight,
          );
          for (const marker of markers) {
            const activeNumber = hotspotState.current.findIndex(
              (h) => h.id === marker.hotspot.id,
            );
            marker.number.textContent = String(activeNumber + 1);
            const position = positions.find((p) => p.id === marker.hotspot.id);
            marker.button.hidden = !position;
            marker.line.style.display = position ? '' : 'none';
            if (!position) continue;
            marker.button.dataset.side = position.side;
            marker.button.style.left = `${position.left}px`;
            marker.button.style.top = `${position.top}px`;
            marker.button.style.width = `${position.width}px`;
            const dx = position.circleX - position.x,
              dy = position.circleY - position.y;
            const distance = Math.hypot(dx, dy);
            marker.line.setAttribute(
              'points',
              `${position.x},${position.y} ${position.circleX - (dx / distance) * 20},${position.circleY - (dy / distance) * 20}`,
            );
            marker.button.setAttribute(
              'aria-pressed',
              String(latest.current.selected === marker.hotspot.part),
            );
          }
        }
      };
      controls.addEventListener('change', render);
      const resize = () => {
        const w = host.clientWidth,
          h = host.clientHeight;
        if (!w || !h) return;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        render();
      };
      const observer = new ResizeObserver(resize);
      observer.observe(host);
      resize();
      const reset = () => {
        const distance =
          (radius /
            (Math.tan(T.MathUtils.degToRad(camera.fov / 2)) *
              Math.min(camera.aspect, 1))) *
          1.2;
        controls.target.copy(center);
        camera.position
          .copy(center)
          .add(
            new T.Vector3(0.85, 0.65, 1).normalize().multiplyScalar(distance),
          );
        controls.minDistance = radius * 0.12;
        controls.maxDistance = distance * 4;
        camera.near = Math.max(0.03, radius / 100);
        camera.far = distance * 6;
        camera.updateProjectionMatrix();
        controls.minPolarAngle = 0;
        controls.maxPolarAngle = Math.PI * 0.93;
        framedExplosion = -1;
        frameExplosion(latest.current, true);
      };
      const frameExplosion = (s: ViewState, force = false) => {
        if (!force && framedExplosion === s.explosion) return;
        const height = buildingExplosionHeight(s);
        const viewRadius = Math.max(radius, (baseHeight + height) / 2);
        const distance =
          (viewRadius /
            (Math.tan(T.MathUtils.degToRad(camera.fov / 2)) *
              Math.min(camera.aspect, 1))) *
          1.2;
        const direction = camera.position.clone().sub(controls.target);
        if (direction.lengthSq() === 0)
          direction.set(0.85, 0.65, 1).normalize();
        else direction.normalize();
        const viewCenter = center
          .clone()
          .add(new T.Vector3(0, height / 2, 0));
        controls.target.copy(viewCenter);
        camera.position
          .copy(viewCenter)
          .add(direction.multiplyScalar(distance));
        controls.minDistance = radius * 0.12;
        controls.maxDistance = distance * 4;
        camera.near = Math.max(0.03, radius / 100);
        camera.far = distance * 6;
        camera.updateProjectionMatrix();
        framedExplosion = s.explosion;
        controls.update();
      };
      const apply = (s: ViewState) => {
        for (const mesh of meshes) {
          const p = mesh.userData as Part;
          mesh.visible = visiblePart(p, s);
          const ex = p.explode ?? [0, 0, 0];
          if (s.model === 'building') {
            const base = (mesh.userData.basePosition as number[] | undefined) ?? [
              0, 0, 0,
            ];
            mesh.position.set(
              base[0],
              base[1] + verticalExplosionOffset(p, s),
              base[2],
            );
          } else {
            mesh.position.set(
              ex[0] * s.explosion,
              ex[2] * s.explosion,
              -ex[1] * s.explosion,
            );
          }
          const mat = mesh.material as THREE.MeshStandardMaterial;
          let base = baseMaterials.get(mat);
          if (!base) {
            base = {
              opacity: mat.opacity,
              transparent: mat.transparent,
              depthWrite: mat.depthWrite,
            };
            baseMaterials.set(mat, base);
          }
          if (mat.alphaHash) {
            mat.alphaHash = false;
            mat.needsUpdate = true;
          }
          mat.opacity = base.opacity;
          mat.transparent = base.transparent;
          mat.depthWrite = base.depthWrite;
          mesh.castShadow =
            p.stage === 0 ||
            mesh.userData.material_kind !== 'glass';
          mat.emissive.set(s.selected === p.key ? 0x712036 : 0x000000);
          mat.emissiveIntensity = s.selected === p.key ? 0.65 : 0;
        }
        frameExplosion(s);
        render();
      };
      const action = (a: string) => {
        if (a === 'reset') {
          if (walkthroughEnabled) setPreparedView('entry');
          else reset();
          return;
        }
        if (a.startsWith('walk-')) {
          const forward = camera.getWorldDirection(new T.Vector3());
          forward.y = 0;
          if (forward.lengthSq() === 0) forward.set(0, 0, -1);
          forward.normalize();
          const right = new T.Vector3().crossVectors(forward, camera.up).normalize();
          const step = Math.max(0.35, radius * 0.018),
            movement =
              a === 'walk-forward'
                ? forward.multiplyScalar(step)
                : a === 'walk-back'
                  ? forward.multiplyScalar(-step)
                  : a === 'walk-left'
                    ? right.multiplyScalar(-step)
                    : right.multiplyScalar(step);
          const next = camera.position.clone().add(movement);
          next.x = T.MathUtils.clamp(
            next.x,
            navigationBounds.min.x,
            navigationBounds.max.x,
          );
          next.z = T.MathUtils.clamp(
            next.z,
            navigationBounds.min.z,
            navigationBounds.max.z,
          );
          movement.x = next.x - camera.position.x;
          movement.z = next.z - camera.position.z;
          camera.position.add(movement);
          controls.target.add(movement);
          controls.update();
          render();
          return;
        }
        const v = camera.position.clone().sub(controls.target);
        if (a === 'left' || a === 'right')
          v.applyAxisAngle(new T.Vector3(0, 1, 0), a === 'left' ? 0.25 : -0.25);
        else v.multiplyScalar(a === 'in' ? 0.8 : 1.25);
        v.clampLength(controls.minDistance, controls.maxDistance);
        camera.position.copy(controls.target).add(v);
        controls.update();
        render();
      };
      const setPreparedView = (
        view: 'overview' | 'entry' | 'ground' | 'upper',
      ) => {
        if (view === 'overview') {
          reset();
          return;
        }
        const eye = view === 'upper' ? groundFloorY + 3.14 + 1.6 : groundFloorY + 1.6,
          depth = Math.max(2.4, navigationBounds.getSize(new T.Vector3()).z * 0.28),
          x =
            view === 'ground'
              ? center.x - navigationBounds.getSize(new T.Vector3()).x * 0.12
              : center.x,
          z =
            view === 'entry'
              ? navigationBounds.max.z - depth * 0.12
              : center.z + depth * 0.18;
        camera.position.set(x, eye, z);
        controls.target.set(x, eye, z - depth);
        camera.near = 0.03;
        camera.far = Math.max(100, radius * 10);
        camera.updateProjectionMatrix();
        controls.minDistance = 0.2;
        controls.maxDistance = Math.max(6, radius * 1.5);
        controls.minPolarAngle = Math.PI / 2;
        controls.maxPolarAngle = Math.PI / 2;
        controls.update();
        render();
      };
      const setWalkthroughMode = (enabled: boolean) => {
        walkthroughEnabled = enabled;
        controls.enablePan = !enabled;
        if (enabled) setPreparedView('entry');
        else reset();
      };
      const ray = new T.Raycaster();
      let down = [0, 0],
        previousY = 0,
        verticalDragging = false,
        verticalMoveEnabled = false;
      const setVerticalMoveMode = (enabled: boolean) => {
        verticalMoveEnabled = enabled;
        renderer.domElement.style.cursor = enabled ? 'ns-resize' : '';
      };
      const pointerdown = (e: PointerEvent) => {
        renderer.domElement.focus({ preventScroll: true });
        down = [e.clientX, e.clientY];
        if (e.button !== 0 || (!verticalMoveEnabled && !e.shiftKey)) return;
        e.preventDefault();
        verticalDragging = true;
        previousY = e.clientY;
        controls.enabled = false;
        renderer.domElement.style.cursor = 'grabbing';
        renderer.domElement.setPointerCapture(e.pointerId);
      };
      const pointermove = (e: PointerEvent) => {
        if (!verticalDragging) return;
        e.preventDefault();
        const deltaY = e.clientY - previousY;
        previousY = e.clientY;
        const distance = camera.position.distanceTo(controls.target);
        const verticalDelta =
          (deltaY * distance * 1.35) / Math.max(host.clientHeight, 1);
        camera.position.y += verticalDelta;
        controls.target.y += verticalDelta;
        render();
      };
      const finishVerticalDrag = (e: PointerEvent) => {
        if (!verticalDragging) return false;
        verticalDragging = false;
        controls.enabled = true;
        renderer.domElement.style.cursor = verticalMoveEnabled
          ? 'ns-resize'
          : '';
        if (renderer.domElement.hasPointerCapture(e.pointerId))
          renderer.domElement.releasePointerCapture(e.pointerId);
        render();
        return true;
      };
      const pointerup = (e: PointerEvent) => {
        if (finishVerticalDrag(e)) return;
        if (Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
        const r = renderer.domElement.getBoundingClientRect();
        ray.setFromCamera(
          new T.Vector2(
            ((e.clientX - r.left) / r.width) * 2 - 1,
            (-(e.clientY - r.top) / r.height) * 2 + 1,
          ),
          camera,
        );
        const hit = ray.intersectObjects(
          meshes.filter((m) => m.visible),
          false,
        )[0];
        select.current(hit ? String(hit.object.userData.key) : null);
      };
      const contextlost = (e: Event) => {
        e.preventDefault();
        setReady(false);
        setStatus(
          '3D graphics paused. Retry the model, or use the image and lesson below.',
        );
      };
      const keydown = (e: KeyboardEvent) => {
        if (!walkthroughEnabled) return;
        const actions: Record<string, string> = {
          w: 'walk-forward',
          ArrowUp: 'walk-forward',
          s: 'walk-back',
          ArrowDown: 'walk-back',
          a: 'walk-left',
          ArrowLeft: 'walk-left',
          d: 'walk-right',
          ArrowRight: 'walk-right',
        };
        const next = actions[e.key];
        if (!next) return;
        e.preventDefault();
        action(next);
      };
      renderer.domElement.tabIndex = 0;
      renderer.domElement.addEventListener('pointerdown', pointerdown);
      renderer.domElement.addEventListener('pointermove', pointermove);
      renderer.domElement.addEventListener('pointerup', pointerup);
      renderer.domElement.addEventListener('pointercancel', finishVerticalDrag);
      renderer.domElement.addEventListener('webglcontextlost', contextlost);
      renderer.domElement.addEventListener('keydown', keydown);
      const disposeObject = (object: THREE.Object3D) =>
        object.traverse((o) => {
          if (o instanceof T.Mesh) {
            o.geometry.dispose();
            const mats = Array.isArray(o.material) ? o.material : [o.material];
            mats.forEach((m) => m.dispose());
          }
        });
      cleanup = () => {
        observer.disconnect();
        controls.dispose();
        renderer.domElement.removeEventListener('pointerdown', pointerdown);
        renderer.domElement.removeEventListener('pointermove', pointermove);
        renderer.domElement.removeEventListener('pointerup', pointerup);
        renderer.domElement.removeEventListener(
          'pointercancel',
          finishVerticalDrag,
        );
        renderer.domElement.removeEventListener(
          'webglcontextlost',
          contextlost,
        );
        renderer.domElement.removeEventListener('keydown', keydown);
        if (root) disposeObject(root);
        for (const mesh of meshes.filter((m) => m.userData.system)) {
          mesh.geometry.dispose();
          const mats = Array.isArray(mesh.material)
            ? mesh.material
            : [mesh.material];
          mats.forEach((m) => m.dispose());
          mesh.removeFromParent();
        }
        markers.forEach((m) => m.button.remove());
        leaders.remove();
        environment.dispose();
        sun.shadow.dispose();
        renderer.dispose();
        renderer.domElement.remove();
      };
      engine.current = {
        apply,
        action,
        setVerticalMove: setVerticalMoveMode,
        setWalkthrough: setWalkthroughMode,
        setViewpoint: setPreparedView,
        dispose: cleanup,
      };
      setVerticalMoveMode(verticalMoveState.current);
      const gltf = await new GLTFLoader().loadAsync(
        `./models/${state.model}.glb?v=2`,
      );
      if (cancelled) {
        disposeObject(gltf.scene);
        return;
      }
      root = gltf.scene;
      scene.add(root);
      root.traverse((o) => {
        if (o instanceof T.Mesh) {
          const old = o.material as THREE.MeshStandardMaterial;
          o.material = displayMaterial(
            old,
            String(o.userData.material_kind ?? 'plain'),
            detailed,
          );
          o.castShadow = o.userData.material_kind !== 'glass';
          o.receiveShadow = true;
          o.userData.basePosition = o.position.toArray();
          meshes.push(o);
        }
      });
      const sourceBounds = new T.Box3().setFromObject(root);
      groundFloorY = sourceBounds.min.y;
      navigationBounds.copy(sourceBounds);
      navigationBounds.min.x += 0.35;
      navigationBounds.max.x -= 0.35;
      navigationBounds.min.z += 0.35;
      navigationBounds.max.z -= 0.35;
      if (state.model === 'building') {
        const size = sourceBounds.getSize(new T.Vector3()),
          floorY = sourceBounds.min.y,
          systemWidth = size.x * 0.76,
          systemDepth = size.z * 0.72,
          systemCenter = sourceBounds.getCenter(new T.Vector3());
        const foundationGroup = new T.Group();
        foundationGroup.name = 'Teaching foundation systems';
        const byKey = new Map(
          [...foundationParts.waffle, ...foundationParts.raised].map((p) => [
            p.key,
            p,
          ]),
        );
        const material = (
          color: number,
          options: { opacity?: number; metalness?: number; roughness?: number } = {},
        ) =>
          new T.MeshStandardMaterial({
            color,
            roughness: options.roughness ?? 0.78,
            metalness: options.metalness ?? 0,
            opacity: options.opacity ?? 1,
            transparent: (options.opacity ?? 1) < 1,
          });
        const addBox = (
          key: string,
          dimensions: [number, number, number],
          position: [number, number, number],
          finish: THREE.MeshStandardMaterial,
        ) => {
          const part = byKey.get(key);
          if (!part) throw new Error(`Unknown teaching part: ${key}`);
          const mesh = new T.Mesh(
            new T.BoxGeometry(...dimensions),
            finish.clone(),
          );
          mesh.position.set(...position);
          mesh.userData = {
            ...part,
            material_kind: 'plain',
            basePosition: [...position],
          };
          mesh.castShadow = detailed;
          mesh.receiveShadow = true;
          foundationGroup.add(mesh);
          meshes.push(mesh);
          return mesh;
        };
        const concrete = material(0xb9bdc4),
          pod = material(0xe8edf0),
          steel = material(0xbfc8cd, { metalness: 0.72, roughness: 0.34 }),
          membrane = material(0x386f93, { opacity: 0.48 }),
          timber = material(0xb98a55),
          stump = material(0x9fa5aa),
          flooring = material(0xc6a46d),
          service = material(0x2aa9df, { metalness: 0.12, roughness: 0.42 });
        addBox(
          '00 Waffle slab membrane',
          [systemWidth, 0.025, systemDepth],
          [systemCenter.x, floorY - 0.48, systemCenter.z],
          membrane,
        );
        const podColumns = 6,
          podRows = 4,
          cellX = systemWidth / podColumns,
          cellZ = systemDepth / podRows;
        for (let x = 0; x < podColumns; x++)
          for (let z = 0; z < podRows; z++)
            addBox(
              '00 Waffle slab pods and ribs',
              [cellX * 0.72, 0.34, cellZ * 0.68],
              [
                systemCenter.x - systemWidth / 2 + cellX * (x + 0.5),
                floorY - 0.27,
                systemCenter.z - systemDepth / 2 + cellZ * (z + 0.5),
              ],
              pod,
            );
        for (let x = 0; x <= podColumns; x++)
          addBox(
            '00 Waffle slab pods and ribs',
            [0.12, 0.38, systemDepth],
            [
              systemCenter.x - systemWidth / 2 + cellX * x,
              floorY - 0.25,
              systemCenter.z,
            ],
            concrete,
          );
        for (let z = 0; z <= podRows; z++)
          addBox(
            '00 Waffle slab pods and ribs',
            [systemWidth, 0.38, 0.12],
            [
              systemCenter.x,
              floorY - 0.25,
              systemCenter.z - systemDepth / 2 + cellZ * z,
            ],
            concrete,
          );
        addBox(
          '00 Waffle slab surface',
          [systemWidth, 0.18, systemDepth],
          [systemCenter.x, floorY - 0.05, systemCenter.z],
          concrete,
        );
        for (let x = 0; x < 8; x++)
          addBox(
            '00 Waffle slab reinforcement',
            [0.018, 0.018, systemDepth * 0.96],
            [
              systemCenter.x - systemWidth * 0.43 + (systemWidth * 0.86 * x) / 7,
              floorY + 0.01,
              systemCenter.z,
            ],
            steel,
          );
        for (let z = 0; z < 6; z++)
          addBox(
            '00 Waffle slab reinforcement',
            [systemWidth * 0.96, 0.018, 0.018],
            [
              systemCenter.x,
              floorY + 0.012,
              systemCenter.z - systemDepth * 0.42 + (systemDepth * 0.84 * z) / 5,
            ],
            steel,
          );

        const supportXs = [-0.38, 0, 0.38],
          supportZs = [-0.34, 0.34];
        for (const nx of supportXs)
          for (const nz of supportZs)
            addBox(
              '00 Raised floor stumps',
              [0.34, 0.9, 0.34],
              [
                systemCenter.x + systemWidth * nx,
                floorY - 0.45,
                systemCenter.z + systemDepth * nz,
              ],
              stump,
            );
        for (const nz of supportZs) {
          const z = systemCenter.z + systemDepth * nz;
          addBox(
            '00 Raised floor bearers',
            [systemWidth * 0.48, 0.28, 0.22],
            [systemCenter.x - systemWidth * 0.25, floorY + 0.04, z],
            timber,
          );
          addBox(
            '00 Raised floor bearers',
            [systemWidth * 0.48, 0.28, 0.22],
            [systemCenter.x + systemWidth * 0.25, floorY + 0.04, z],
            timber,
          );
        }
        for (let x = 0; x < 12; x++)
          addBox(
            '00 Raised floor joists',
            [0.09, 0.24, systemDepth * 0.86],
            [
              systemCenter.x - systemWidth * 0.44 + (systemWidth * 0.88 * x) / 11,
              floorY + 0.28,
              systemCenter.z,
            ],
            timber,
          );
        addBox(
          '00 Raised floor sheet flooring',
          [systemWidth * 0.94, 0.08, systemDepth * 0.9],
          [systemCenter.x, floorY + 0.44, systemCenter.z],
          flooring,
        );
        const pipe = new T.Mesh(
          new T.CylinderGeometry(0.07, 0.07, systemDepth * 0.42, 18),
          service,
        );
        pipe.rotation.x = Math.PI / 2;
        pipe.position.set(
          systemCenter.x + systemWidth * 0.18,
          floorY + 0.3,
          systemCenter.z,
        );
        pipe.userData = {
          ...byKey.get('00 Raised floor service penetration')!,
          material_kind: 'metal',
          basePosition: pipe.position.toArray(),
        };
        pipe.castShadow = detailed;
        foundationGroup.add(pipe);
        meshes.push(pipe);
        scene.add(foundationGroup);
      }
      const bounds = new T.Box3().setFromObject(root);
      for (const mesh of meshes)
        if (mesh.userData.system)
          bounds.union(new T.Box3().setFromObject(mesh));
      {
        const markerParts =
          state.model === 'building'
            ? [
                ...foundationParts.waffle,
                ...foundationParts.raised,
                ...parts.filter((p) => !p.system),
              ]
            : parts;
        for (const [i, hotspot] of studyHotspots(
          state.model,
          markerParts,
        ).entries()) {
          const members = meshes.filter((m) => m.userData.key === hotspot.part);
          if (!members.length) continue;
          const box = new T.Box3();
          members.forEach((m) => box.union(new T.Box3().setFromObject(m)));
          const target = box.getCenter(new T.Vector3());
          // Anchor to real exported geometry, never to an empty batch centre.
          let best = Infinity;
          let anchorMesh = members[0];
          const point = target.clone(),
            v = new T.Vector3();
          for (const member of members) {
            const positions = member.geometry.getAttribute('position');
            for (let n = 0; n < positions.count; n++) {
              v.fromBufferAttribute(positions, n).applyMatrix4(
                member.matrixWorld,
              );
              const distance = v.distanceToSquared(target);
              if (distance < best) {
                best = distance;
                point.copy(v);
                anchorMesh = member;
              }
            }
          }
          const button = document.createElement('button');
          button.className = 'hotspot-callout';
          const number = document.createElement('span');
          number.className = 'hotspot-number';
          number.textContent = String(i + 1);
          const label = document.createElement('span');
          label.className = 'hotspot-label';
          label.textContent = hotspot.title;
          button.appendChild(number);
          button.appendChild(label);
          button.title = hotspot.title;
          button.setAttribute(
            'aria-label',
            `Hotspot ${i + 1}: ${hotspot.title}`,
          );
          button.onclick = () => hotspotSelect.current(hotspot);
          host.appendChild(button);
          const line = document.createElementNS(
            'http://www.w3.org/2000/svg',
            'polyline',
          );
          leaders.appendChild(line);
          markers.push({
            button,
            number,
            point: anchorMesh.worldToLocal(point),
            mesh: anchorMesh,
            line,
            hotspot,
          });
        }
      }
      bounds.getCenter(center);
      const modelSize = bounds.getSize(new T.Vector3());
      radius = modelSize.length() / 2;
      baseHeight = modelSize.y;
      if (state.model !== 'building') radius *= 1.32;
      sun.position
        .copy(center)
        .add(new T.Vector3(-0.6, 1.3, 0.8).multiplyScalar(radius));
      sun.target.position.copy(center);
      const shadowCamera = sun.shadow.camera;
      shadowCamera.left = -radius;
      shadowCamera.right = radius;
      shadowCamera.top = radius;
      shadowCamera.bottom = -radius;
      shadowCamera.near = 0.1;
      shadowCamera.far = radius * 5;
      shadowCamera.updateProjectionMatrix();
      const ground = new T.Mesh(
        new T.PlaneGeometry(radius * 15, radius * 15),
        new T.MeshStandardMaterial({ color: 0x373b50, roughness: 1 }),
      );
      ground.rotation.x = -Math.PI / 2;
      ground.position.set(center.x, bounds.min.y - 0.04, center.z);
      ground.receiveShadow = true;
      scene.add(ground);
      scene.fog = new T.Fog(0x252a40, radius * 4, radius * 10);
      const oldCleanup = cleanup;
      cleanup = () => {
        ground.geometry.dispose();
        ground.material.dispose();
        oldCleanup?.();
      };
      if (walkthroughState.current) setWalkthroughMode(true);
      else reset();
      apply(latest.current);
      setReady(true);
      setStatus('3D model ready');
    }
    init().catch(() => {
      if (!cancelled) {
        cleanup?.();
        engine.current = null;
        setStatus(
          'The 3D model could not load. Retry, or use the image and lesson below.',
        );
        setReady(false);
      }
    });
    return () => {
      cancelled = true;
      cleanup?.();
      engine.current = null;
    };
  }, [state.model, attempt, detailed]);
  return (
    <>
      <div className="quality-control">
        <span>Detailed lighting</span>
        <Switch
          aria-label="Detailed lighting and materials"
          checked={detailed}
          onCheckedChange={(v) => {
            setReady(false);
            setStatus('Loading 3D model…');
            onQualityChange(v);
          }}
        />
        <span className="quality-note">
          {detailed ? 'Shadows + finishes' : 'Lighter on your device'}
        </span>
      </div>
      <div
        className="three-mount"
        ref={mount}
        style={{ visibility: ready ? 'visible' : 'hidden' }}
      />
      {!ready && (
        <div className="model-fallback">
          <img
            src={fallback}
            alt={
              state.model === 'building'
                ? 'Reference enclosure render; not synchronised with the 3D stage controls'
                : `Exploded ${state.model} assembly reference`
            }
          />
          <output className="load-state">
            {status}
            {!status.startsWith('Loading') && (
              <button
                onClick={() => {
                  setReady(false);
                  setStatus('Loading 3D model…');
                  setAttempt((v) => v + 1);
                }}
              >
                Retry 3D
              </button>
            )}
          </output>
        </div>
      )}
      <div className="camera-tools" aria-label="Camera controls">
        {[
          ['left', 'Orbit left', RotateCcw],
          ['right', 'Orbit right', RotateCw],
          ['in', 'Zoom in', Plus],
          ['out', 'Zoom out', Minus],
          ['vertical', 'Move view vertically', MoveVertical],
          ['reset', 'Reset view', Maximize2],
        ].map(([action, label, Icon]) => {
          const I = Icon as typeof Plus;
          return (
            <button
              key={String(action)}
              title={String(label)}
              aria-label={String(label)}
              aria-pressed={
                action === 'vertical' ? verticalMove : undefined
              }
              disabled={!ready || (action === 'vertical' && walkthrough)}
              onClick={() => {
                if (action === 'vertical')
                  setVerticalMove((enabled) => !enabled);
                else engine.current?.action(String(action));
              }}
            >
              <I size={18} />
            </button>
          );
        })}
      </div>
      {state.model === 'building' && (
        <div className="walkthrough-tools" aria-label="Interior walkthrough controls">
          <div className="walkthrough-heading">
            <strong>Interior walkthrough</strong>
            <button
              aria-pressed={walkthrough}
              disabled={!ready}
              onClick={() => {
                const enabled = !walkthrough;
                if (enabled) onWalkthroughStart();
                setWalkthrough(enabled);
                setViewpoint(enabled ? 'entry' : 'overview');
                engine.current?.setWalkthrough(enabled);
              }}
            >
              {walkthrough ? 'Return to overview' : 'Enter at eye level'}
            </button>
          </div>
          {walkthrough && (
            <>
              <div className="viewpoint-buttons" aria-label="Prepared viewpoints">
                {(
                  [
                    ['entry', 'Entry'],
                    ['ground', 'Ground floor'],
                    ['upper', 'Upstairs'],
                  ] as const
                ).map(([view, label]) => (
                  <button
                    key={view}
                    aria-pressed={viewpoint === view}
                    onClick={() => {
                      setViewpoint(view);
                      engine.current?.setViewpoint(view);
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <div className="walk-pad" aria-label="Walk controls">
                <button
                  aria-label="Walk forward"
                  onClick={() => engine.current?.action('walk-forward')}
                >
                  ↑
                </button>
                <button
                  aria-label="Walk left"
                  onClick={() => engine.current?.action('walk-left')}
                >
                  ←
                </button>
                <button
                  aria-label="Walk backwards"
                  onClick={() => engine.current?.action('walk-back')}
                >
                  ↓
                </button>
                <button
                  aria-label="Walk right"
                  onClick={() => engine.current?.action('walk-right')}
                >
                  →
                </button>
              </div>
              <small>1.6 m eye-height reference · drag to look · WASD or arrows to move</small>
            </>
          )}
        </div>
      )}
      <output className="sr-only">{status}</output>
    </>
  );
}
