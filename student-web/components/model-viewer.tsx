'use client';
/* oxlint-disable next/no-img-element -- Static fallback assets; no runtime image service. */
import { useEffect, useRef, useState } from 'react';
import { RotateCcw, RotateCw, Plus, Minus, Maximize2 } from 'lucide-react';
import type { Part, ViewState } from '@/lib/explorer';
import { visiblePart } from '@/lib/explorer';
import type * as THREE from 'three';
import { Switch } from '@/components/ui/switch';

type Engine = {
  apply: (s: ViewState) => void;
  action: (a: string) => void;
  dispose: () => void;
};
export default function ModelViewer({
  state,
  onSelect,
  fallback,
  detailed,
  onQualityChange,
}: {
  state: ViewState;
  onSelect: (key: string | null) => void;
  fallback: string;
  detailed: boolean;
  onQualityChange: (value: boolean) => void;
}) {
  const mount = useRef<HTMLDivElement>(null),
    engine = useRef<Engine | null>(null),
    latest = useRef(state),
    select = useRef(onSelect);
  const [status, setStatus] = useState('Loading 3D model…'),
    [ready, setReady] = useState(false),
    [attempt, setAttempt] = useState(0);
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
      renderer.setClearColor('#24353e');
      renderer.outputColorSpace = T.SRGBColorSpace;
      renderer.toneMapping = T.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      renderer.shadowMap.enabled = detailed;
      renderer.shadowMap.type = T.PCFSoftShadowMap;
      renderer.domElement.setAttribute(
        'aria-label',
        'Interactive 3D model. Drag to orbit, pinch or scroll to zoom. Keyboard camera controls follow.',
      );
      renderer.domElement.setAttribute('role', 'img');
      host.appendChild(renderer.domElement);
      const scene = new T.Scene(),
        camera = new T.PerspectiveCamera(38, 1, 0.01, 1000),
        controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = false;
      controls.maxPolarAngle = Math.PI * 0.93;
      scene.add(new T.HemisphereLight(0xddeaff, 0x70614e, 0.65));
      const pmrem = new T.PMREMGenerator(renderer),
        studio = new RoomEnvironment();
      const environment = pmrem.fromScene(studio, 0.05);
      scene.environment = environment.texture;
      scene.environmentIntensity = 0.55;
      studio.dispose();
      pmrem.dispose();
      const sun = new T.DirectionalLight(0xfff2de, 3.0);
      sun.castShadow = detailed;
      sun.shadow.mapSize.set(2048, 2048);
      sun.shadow.normalBias = 0.012;
      sun.shadow.bias = -0.00012;
      scene.add(sun, sun.target);
      // Assigned after asynchronous loading; disposal can run before it resolves.
      // oxlint-disable-next-line prefer-const
      let root: THREE.Group | undefined;
      const meshes: THREE.Mesh[] = [];
      let radius = 1;
      const center = new T.Vector3();
      const render = () => {
        if (!cancelled) renderer.render(scene, camera);
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
        controls.update();
        render();
      };
      const apply = (s: ViewState) => {
        for (const mesh of meshes) {
          const p = mesh.userData as Part;
          mesh.visible = visiblePart(p, s);
          const ex = p.explode ?? [0, 0, 0];
          mesh.position.set(
            ex[0] * s.explosion,
            ex[2] * s.explosion,
            -ex[1] * s.explosion,
          );
          const mat = mesh.material as THREE.MeshStandardMaterial;
          mat.emissive.set(s.selected === p.key ? 0x486c1c : 0x000000);
          mat.emissiveIntensity = s.selected === p.key ? 0.65 : 0;
        }
        render();
      };
      const action = (a: string) => {
        if (a === 'reset') {
          reset();
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
      const ray = new T.Raycaster();
      let down = [0, 0];
      const pointerdown = (e: PointerEvent) => {
        down = [e.clientX, e.clientY];
      };
      const pointerup = (e: PointerEvent) => {
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
      renderer.domElement.addEventListener('pointerdown', pointerdown);
      renderer.domElement.addEventListener('pointerup', pointerup);
      renderer.domElement.addEventListener('webglcontextlost', contextlost);
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
        renderer.domElement.removeEventListener('pointerup', pointerup);
        renderer.domElement.removeEventListener(
          'webglcontextlost',
          contextlost,
        );
        if (root) disposeObject(root);
        environment.dispose();
        sun.shadow.dispose();
        renderer.dispose();
        renderer.domElement.remove();
      };
      engine.current = { apply, action, dispose: cleanup };
      const gltf = await new GLTFLoader().loadAsync(
        `/models/${state.model}.glb?v=2`,
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
          meshes.push(o);
        }
      });
      const bounds = new T.Box3().setFromObject(root);
      bounds.getCenter(center);
      radius = bounds.getSize(new T.Vector3()).length() / 2;
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
        new T.MeshStandardMaterial({ color: 0x34434a, roughness: 1 }),
      );
      ground.rotation.x = -Math.PI / 2;
      ground.position.set(center.x, bounds.min.y - 0.04, center.z);
      ground.receiveShadow = true;
      scene.add(ground);
      scene.fog = new T.Fog(0x24353e, radius * 4, radius * 10);
      const oldCleanup = cleanup;
      cleanup = () => {
        ground.geometry.dispose();
        ground.material.dispose();
        oldCleanup?.();
      };
      reset();
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
          ['reset', 'Reset view', Maximize2],
        ].map(([action, label, Icon]) => {
          const I = Icon as typeof Plus;
          return (
            <button
              key={String(action)}
              title={String(label)}
              aria-label={String(label)}
              disabled={!ready}
              onClick={() => engine.current?.action(String(action))}
            >
              <I size={18} />
            </button>
          );
        })}
      </div>
      <output className="sr-only">{status}</output>
    </>
  );
}
