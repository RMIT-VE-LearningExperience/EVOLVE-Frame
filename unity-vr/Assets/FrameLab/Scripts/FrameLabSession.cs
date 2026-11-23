using System.Collections;
using Unity.XR.CoreUtils;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;
using UnityEngine.XR.Interaction.Toolkit.Locomotion.Turning;

namespace FrameLab
{
    public class FrameLabSession : MonoBehaviour
    {
        public XROrigin rig;
        public Transform[] destinations;
        public Transform detailDestination;
        public FrameLabTour tour;
        public GameObject building, detail, detailFloor;
        public Renderer[] enclosure, walls, roof;
        public LayerMask obstructionMask;
        public FrameLabLightingState lighting;
        public FrameLabFittings fittings;
        public Renderer[] stairPaintedStructure;
        public Material stairFinishMaterial, stairTimberMaterial;
        public FrameLabInspection inspection;
        FrameLabGuide guide;
        AudioSource narrator;
        Material fadeMaterial;
        SnapTurnProvider[] turnProviders;
        bool changing, framing, roofHidden, inDetail, menuPressed, pausedAudio, headObstructed, muted;
        float fadeOpacity;
        int location, savedLocation, study = -1;
        public bool IsChanging => changing;
        public bool IsInDetail => inDetail;
        public bool IsFraming => framing;
        public bool IsExploded => inspection.Explosion > .001f;
        public bool IsRoofHidden => roofHidden;
        public bool IsMuted => muted;
        public int Location => location;
        public int Study => study;
        public FrameLabGuide Guide => guide;
        public FrameLabStop Current => study >= 0 ? tour.studies[study] : tour.rooms[location];
        public bool IsSpeaking => narrator.isPlaying;

        void Awake()
        {
            Application.targetFrameRate = 90;
            narrator = gameObject.AddComponent<AudioSource>();
            narrator.playOnAwake = false; narrator.spatialBlend = 0;
            turnProviders = rig.GetComponentsInChildren<SnapTurnProvider>(true);
            inspection.Initialize(this);
            inspection.Changed += () => { if (inDetail) { study = IsExploded ? 1 : 0; if (guide != null) guide.Refresh(); } };
            detail.SetActive(false); detailFloor.SetActive(false);
            CreateFade();
            guide = gameObject.AddComponent<FrameLabGuide>(); guide.Initialize(this);
        }
        IEnumerator Start()
        {
            yield return null; yield return null;
            PlaceRig(destinations[0]); guide.Place(); guide.Refresh();
            while (Application.isMobilePlatform && !Application.isFocused) yield return null;
            ReplayNarration();
            Debug.Log("FRAME_LAB_SESSION_READY " + Application.version + " room=" + Current.id + " guide=" + guide.IsVisible + " narration=" + IsSpeaking);
        }
        void Update()
        {
            var right = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
            right.TryGetFeatureValue(UnityEngine.XR.CommonUsages.primaryButton, out bool aPressed);
            var left = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
            left.TryGetFeatureValue(UnityEngine.XR.CommonUsages.menuButton, out bool leftMenu);
            bool keyboardMenu = Keyboard.current != null && Keyboard.current.mKey.wasPressedThisFrame;
            HandleMenuInput(aPressed || leftMenu || keyboardMenu);
            if (changing) return;
            headObstructed = Physics.CheckSphere(rig.Camera.transform.position, headObstructed ? 0.12f : 0.08f,
                obstructionMask, QueryTriggerInteraction.Ignore);
            SetFade(Mathf.MoveTowards(fadeOpacity, headObstructed ? 1 : 0, Time.unscaledDeltaTime * 10));
        }
        public void HandleMenuInput(bool pressed)
        {
            if (pressed && !menuPressed && !changing) guide.Toggle();
            menuPressed = pressed;
        }
        public void Next()
        {
            if (changing) return;
            if (study == 2) { ResetSession(); return; }
            if (inDetail)
            {
                if (study == 0) ToggleExploded();
                else StartCoroutine(Travel(destinations.Length - 1, false, true));
            }
            else if (location < destinations.Length - 1) GoTo(location + 1);
            else ToggleDetail();
        }
        public void Previous()
        {
            if (changing) return;
            if (inDetail) { if (study == 1) ToggleExploded(); else ToggleDetail(); }
            else GoTo(Mathf.Max(0, location - 1));
        }
        public void GoTo(int index)
        {
            if (changing || index < 0 || index >= destinations.Length) return;
            StartCoroutine(Travel(index, false));
        }
        IEnumerator Travel(int index, bool enterDetail, bool complete = false, bool reset = false)
        {
            changing = true;
            foreach (var turn in turnProviders) turn.enabled = false;
            narrator.Stop(); pausedAudio = false;
            yield return Fade(fadeOpacity, 1);
            if (enterDetail) savedLocation = location;
            inDetail = enterDetail;
            detail.SetActive(inDetail); detailFloor.SetActive(inDetail); building.SetActive(!inDetail);
            inspection.ResetAll();
            if (reset)
            {
                framing = roofHidden = false;
                SetSurfaces(walls, true); SetSurfaces(roof, true);
                fittings.SetAll(true); SetStairTimber(false);
                if (lighting != null) lighting.Apply(true);
            }
            location = index; study = enterDetail ? 0 : complete ? 2 : -1;
            PlaceRig(enterDetail ? detailDestination : destinations[index]);
            guide.Show(); guide.ShowRooms(false); guide.Place(); guide.Refresh();
            if (inDetail) guide.ShowInspection(true);
            yield return Fade(1, 0);
            foreach (var turn in turnProviders) turn.enabled = true;
            changing = false; ReplayNarration();
        }
        void PlaceRig(Transform destination)
        {
            rig.MatchOriginUpCameraForward(Vector3.up, destination.forward);
            float eyeHeight = rig.CameraInOriginSpaceHeight;
            rig.MoveCameraToWorldLocation(destination.position + Vector3.up * eyeHeight);
        }
        public static void SetSurfaces(Renderer[] surfaces, bool visible)
        {
            foreach (var surface in surfaces)
            {
                surface.enabled = visible;
                foreach (var collider in surface.GetComponents<Collider>()) collider.enabled = visible;
            }
        }
        public void ToggleFraming()
        {
            if (changing || inDetail) return;
            framing = !framing; SetSurfaces(walls, !framing);
            SetStairTimber(framing);
            ApplyVisibilityLighting();
            guide.Refresh(); if (guide.IsVisible) guide.Place();
        }
        public void ToggleRoof()
        {
            if (changing || inDetail) return;
            roofHidden = !roofHidden; SetSurfaces(roof, !roofHidden); guide.Refresh();
            ApplyVisibilityLighting();
            if (guide.IsVisible) guide.Place();
        }
        public void ToggleDetail()
        {
            if (!changing) StartCoroutine(Travel(inDetail ? savedLocation : location, !inDetail));
        }
        public void SetStairTimber(bool timber)
        {
            foreach (var surface in stairPaintedStructure)
                surface.sharedMaterial = timber ? stairTimberMaterial : stairFinishMaterial;
        }
        void ApplyVisibilityLighting()
        {
            if (lighting != null) lighting.Apply(!framing, !roofHidden, fittings.AnyHidden);
        }
        public void ToggleFitting(int index)
        {
            if (changing || inDetail || index < 0 || index >= fittings.groups.Length) return;
            fittings.Set(index, !fittings.groups[index].shown); RefreshFittings();
        }
        public void SetAllFittings(bool shown)
        {
            if (changing || inDetail) return;
            fittings.SetAll(shown); RefreshFittings();
        }
        void RefreshFittings()
        {
            ApplyVisibilityLighting(); guide.Refresh();
            if (guide.IsVisible) guide.Place();
        }
        void SetExploded(bool value)
        {
            inspection.SetExplosion(value ? 1 : 0);
        }
        public void SetExplosionAmount(float value)
        {
            if (!inDetail || changing) return;
            inspection.SetExplosion(value); study = IsExploded ? 1 : 0; guide.Refresh();
        }
        public void ToggleExploded()
        {
            if (!inDetail || changing) return;
            SetExploded(!IsExploded); study = IsExploded ? 1 : 0; guide.Refresh(); ReplayNarration();
        }
        public void SpeakInspection(AudioClip clip)
        {
            narrator.Stop(); narrator.clip = clip;
            if (!muted && clip != null) narrator.Play();
        }
        public void DescribePart(string description)
        {
            if (inDetail && !changing) guide.Describe(description + "\n\nChoose Replay to restore the guide explanation.");
        }
        public void ReplayNarration()
        {
            narrator.Stop(); narrator.clip = Current.audio; guide.Describe(Current.caption);
            if (!muted) narrator.Play();
        }
        public void ResetSession() { if (!changing) StartCoroutine(Travel(0, false, false, true)); }
        public void ToggleNarration()
        {
            muted = !muted;
            if (muted) { narrator.Stop(); pausedAudio = false; } else ReplayNarration();
            guide.Refresh();
        }
        void OnApplicationPause(bool paused) => PauseNarration(paused);
        void OnApplicationFocus(bool focused) { if (Application.isMobilePlatform) PauseNarration(!focused); }
        void PauseNarration(bool paused)
        {
            if (narrator == null) return;
            if (paused) { pausedAudio |= narrator.isPlaying; narrator.Pause(); }
            else if (pausedAudio && !muted) { narrator.UnPause(); pausedAudio = false; }
        }
        void CreateFade()
        {
            var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere); sphere.name = "Comfort fade";
            Destroy(sphere.GetComponent<Collider>()); sphere.transform.SetParent(rig.Camera.transform, false);
            sphere.transform.localScale = Vector3.one * 0.25f;
            fadeMaterial = new Material(Shader.Find("FrameLab/ComfortFade"));
            sphere.GetComponent<Renderer>().sharedMaterial = fadeMaterial; SetFade(0);
        }
        IEnumerator Fade(float from, float to)
        {
            float elapsed = 0;
            while (elapsed < 0.15f)
            {
                elapsed += Time.unscaledDeltaTime; SetFade(Mathf.Lerp(from, to, elapsed / 0.15f)); yield return null;
            }
            SetFade(to);
        }
        void SetFade(float opacity) { fadeOpacity = opacity; fadeMaterial.SetFloat("_Opacity", opacity); }
        void OnDestroy() { if (fadeMaterial != null) Destroy(fadeMaterial); }
    }
}
