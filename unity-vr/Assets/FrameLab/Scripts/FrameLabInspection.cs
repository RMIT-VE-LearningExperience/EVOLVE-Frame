using System;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
using UnityEngine.XR.Interaction.Toolkit.UI;

namespace FrameLab
{
    public class FrameLabInspection : MonoBehaviour
    {
        [Serializable] public class Part
        {
            public string id, title, shortName, description;
            public MeshRenderer surface;
            public AudioClip audio;
        }
        public Part[] parts;
        public XRGrabInteractable grab;
        FrameLabSession session;
        Vector3 homePosition, homeScale;
        Quaternion homeRotation;
        Vector3[] assembled, offsets;
        Canvas[] hotspots;
        Image[] badges;
        LineRenderer[] leaders;
        Material leaderMaterial;
        float explosion, rotationDegrees;
        Quaternion observedRotation;
        int selected = -1;
        bool isolated, showHotspots = true;
        public float Explosion => explosion;
        public float RotationDegrees => rotationDegrees;
        public float ZoomLevel => transform.localScale.x / homeScale.x;
        public int Selected => selected;
        public bool IsIsolated => isolated;
        public Part Current => selected >= 0 ? parts[selected] : null;
        public Vector3 HomePosition => homePosition;
        public Quaternion HomeRotation => homeRotation;
        public int VisiblePartCount => parts.Count(p => p.surface.enabled);
        public int HotspotCount => hotspots == null ? 0 : hotspots.Length;
        public event Action Changed;

        public void Initialize(FrameLabSession owner)
        {
            session = owner;
            homePosition = transform.position; homeScale = transform.localScale;
            assembled = new Vector3[parts.Length]; offsets = new Vector3[parts.Length];
            var bounds = parts.Select(p => LocalBounds(p.surface)).ToArray();
            float total = bounds.Sum(b => b.size.z) + .20f * (parts.Length - 1);
            float depth = -total / 2;
            for (int i = 0; i < parts.Length; i++)
            {
                assembled[i] = parts[i].surface.transform.localPosition;
                offsets[i] = new Vector3((i - (parts.Length - 1) / 2f) * .20f, 0, depth - bounds[i].min.z);
                depth += bounds[i].size.z + .20f;
            }
            homeRotation = Quaternion.Euler(0, 35, 0);
            transform.rotation = homeRotation;
            observedRotation = homeRotation;
            CreateHotspots(); ApplyParts();
        }
        public Bounds LocalBounds(MeshRenderer surface)
        {
            Bounds mesh = surface.GetComponent<MeshFilter>().sharedMesh.bounds;
            var matrix = transform.worldToLocalMatrix * surface.transform.localToWorldMatrix;
            Bounds result = new Bounds(matrix.MultiplyPoint3x4(mesh.center), Vector3.zero);
            for (int i = 0; i < 8; i++)
                result.Encapsulate(matrix.MultiplyPoint3x4(mesh.center + Vector3.Scale(mesh.extents,
                    new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1))));
            return result;
        }
        public void SetExplosion(float value)
        {
            explosion = Mathf.Clamp01(value); ApplyParts(); Changed?.Invoke();
        }
        void ApplyParts()
        {
            for (int i = 0; i < parts.Length; i++)
            {
                Transform item = parts[i].surface.transform;
                item.localPosition = assembled[i] + item.parent.InverseTransformVector(transform.TransformVector(offsets[i] * explosion));
                bool visible = !isolated || i == selected;
                parts[i].surface.enabled = visible;
                foreach (var collider in item.GetComponents<Collider>()) collider.enabled = visible;
            }
            if (isolated && selected >= 0)
            {
                var part = parts[selected].surface;
                part.transform.position += transform.position - part.bounds.center;
            }
            Physics.SyncTransforms();
        }
        public void SelectPart(int index)
        {
            if (index < 0 || index >= parts.Length) return;
            selected = index; ApplyParts(); Changed?.Invoke(); ReplayPart();
            session.Guide.ShowInspection(true);
            if (!session.Guide.IsVisible) { session.Guide.Show(); session.Guide.Place(); }
        }
        public void ReplayPart()
        {
            if (Current != null) session.SpeakInspection(Current.audio);
        }
        public void ToggleIsolation()
        {
            if (selected < 0) selected = 0;
            isolated = !isolated; ApplyParts(); Changed?.Invoke();
        }
        public void ShowAll() { isolated = false; ApplyParts(); Changed?.Invoke(); }
        void ReleaseGrab()
        {
            if (grab == null || grab.interactionManager == null) return;
            foreach (var interactor in grab.interactorsSelecting.ToArray()) grab.interactionManager.SelectExit(interactor, grab);
        }
        public void Zoom(float multiplier)
        {
            ReleaseGrab();
            float oldBottom = DisplayBounds().min.y;
            transform.localScale = homeScale * Mathf.Clamp(ZoomLevel * multiplier, .55f, 1.5f);
            transform.position += Vector3.up * (oldBottom - DisplayBounds().min.y);
            Physics.SyncTransforms(); Changed?.Invoke();
        }
        public void Rotate(float angle)
        {
            SyncRotation();
            SetRotation(Mathf.DeltaAngle(0, rotationDegrees + angle));
        }
        public void SetRotation(float degrees)
        {
            ReleaseGrab(); SyncRotation();
            float target = Mathf.Clamp(degrees, -180, 180);
            transform.RotateAround(DisplayBounds().center, Vector3.up, target - rotationDegrees);
            rotationDegrees = target; observedRotation = transform.rotation;
            Physics.SyncTransforms(); Changed?.Invoke();
        }
        void SyncRotation()
        {
            if (Quaternion.Angle(observedRotation, transform.rotation) < .01f) return;
            rotationDegrees = Mathf.DeltaAngle(homeRotation.eulerAngles.y, transform.eulerAngles.y);
            observedRotation = transform.rotation;
        }
        public void ResetAll()
        {
            ReleaseGrab();
            transform.SetPositionAndRotation(homePosition, homeRotation); transform.localScale = homeScale;
            rotationDegrees = 0; observedRotation = homeRotation;
            explosion = 0; selected = -1; isolated = false; ApplyParts(); Changed?.Invoke();
        }
        public void ToggleHotspots() { showHotspots = !showHotspots; }
        Bounds DisplayBounds()
        {
            var visible = parts.Where(p => p.surface.enabled).ToArray();
            Bounds result = visible[0].surface.bounds;
            foreach (var part in visible.Skip(1)) result.Encapsulate(part.surface.bounds);
            return result;
        }
        void CreateHotspots()
        {
            hotspots = new Canvas[parts.Length]; badges = new Image[parts.Length]; leaders = new LineRenderer[parts.Length];
            leaderMaterial = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
            leaderMaterial.SetColor("_BaseColor", new Color(.24f, .29f, .32f));
            for (int i = 0; i < parts.Length; i++)
            {
                int index = i;
                var go = new GameObject("Hotspot " + (i + 1) + " " + parts[i].id, typeof(RectTransform), typeof(Canvas), typeof(TrackedDeviceGraphicRaycaster));
                go.transform.SetParent(transform, true);
                hotspots[i] = go.GetComponent<Canvas>(); hotspots[i].renderMode = RenderMode.WorldSpace; hotspots[i].worldCamera = session.rig.Camera;
                go.GetComponent<RectTransform>().sizeDelta = new Vector2(90, 70);
                var badge = new GameObject("Select component", typeof(RectTransform), typeof(Image), typeof(Button)); badge.transform.SetParent(go.transform, false);
                var rect = badge.GetComponent<RectTransform>(); rect.sizeDelta = new Vector2(90, 70);
                badges[i] = badge.GetComponent<Image>();
                badge.GetComponent<Button>().onClick.AddListener(() => SelectPart(index));
                var label = new GameObject("Number", typeof(RectTransform), typeof(Text)); label.transform.SetParent(badge.transform, false);
                label.GetComponent<RectTransform>().sizeDelta = new Vector2(90, 70);
                var text = label.GetComponent<Text>(); text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                text.text = (i + 1).ToString(); text.fontSize = 40; text.color = Color.white; text.alignment = TextAnchor.MiddleCenter; text.raycastTarget = false;
                var line = new GameObject("Component leader").AddComponent<LineRenderer>(); line.transform.SetParent(transform, true);
                line.sharedMaterial = leaderMaterial; line.positionCount = 2; line.startWidth = line.endWidth = .003f;
                line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; line.receiveShadows = false; leaders[i] = line;
            }
        }
        void LateUpdate()
        {
            if (session == null || !session.IsInDetail) return;
            if (Quaternion.Angle(observedRotation, transform.rotation) > .01f)
            {
                SyncRotation(); Changed?.Invoke();
            }
            var bounds = DisplayBounds();
            Vector3 eye = session.rig.Camera.transform.position;
            Vector3 facing = (bounds.center - eye).normalized;
            Vector3 right = Vector3.Cross(Vector3.up, facing).normalized;
            float halfWidth = Mathf.Abs(right.x) * bounds.extents.x + Mathf.Abs(right.z) * bounds.extents.z;
            for (int i = 0; i < parts.Length; i++)
            {
                bool visible = showHotspots && (!isolated || i == selected);
                hotspots[i].gameObject.SetActive(visible); leaders[i].enabled = visible;
                if (!visible) continue;
                int row = i / 2; float side = i % 2 == 0 ? -1 : 1;
                Vector3 anchor = bounds.center + right * side * (halfWidth + .20f) + Vector3.up * (.95f - row * .47f) - facing * .12f;
                if (isolated) anchor = bounds.center + right * (halfWidth + .2f);
                hotspots[i].transform.SetPositionAndRotation(anchor, Quaternion.LookRotation(anchor - eye, Vector3.up));
                hotspots[i].transform.localScale = Vector3.one * (.0017f / transform.lossyScale.x);
                badges[i].color = i == selected ? new Color(.65f, .30f, .055f) : new Color(.075f, .12f, .15f);
                // The line ends on the nearest surface point, rather than in an empty frame opening.
                var surface = parts[i].surface;
                Vector3 end = surface.bounds.ClosestPoint(anchor);
                var collider = surface.GetComponent<Collider>();
                Vector3 direction = surface.bounds.center - anchor;
                if (collider != null && collider.Raycast(new Ray(anchor, direction.normalized), out var hit, direction.magnitude + bounds.size.magnitude)) end = hit.point;
                leaders[i].SetPosition(0, anchor); leaders[i].SetPosition(1, end);
            }
        }
        void OnDestroy() { if (leaderMaterial != null) Destroy(leaderMaterial); }
    }
}
