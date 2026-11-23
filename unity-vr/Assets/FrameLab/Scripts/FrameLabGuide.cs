using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;

namespace FrameLab
{
    public class FrameLabGuide : MonoBehaviour
    {
        FrameLabSession session;
        Canvas menu;
        GameObject guide, roomList, inspection, fittings;
        Text[] fittingLabels;
        Text heading, instructions, prompt, status, nextLabel, wallsLabel, roofLabel, detailLabel, layersLabel, muteLabel, pageLabel;
        readonly Text[] roomLabels = new Text[6];
        readonly Button[] roomButtons = new Button[6];
        int roomPage;
        public bool IsVisible => menu.gameObject.activeSelf;
        public Transform Panel => menu.transform;
        public void Describe(string text) => instructions.text = text;
        void Update()
        {
            status.text = session.IsMuted ? "Narration off · captions remain available" : session.IsSpeaking ?
                "Clara is speaking · continue whenever you're ready" : "Take your time · choose the highlighted next step";
        }
        public void Refresh()
        {
            heading.text = session.Study >= 0 ? session.Current.title : (session.Location + 1) + " / " + session.destinations.Length + "  " + session.Current.title;
            instructions.text = session.Current.caption; prompt.text = session.Current.prompt;
            nextLabel.text = session.Study == 2 ? "Restart tour" : session.IsInDetail ? (session.IsExploded ? "Finish tour" : "Separate layers") :
                session.Location == session.destinations.Length - 1 ? "Window study" : "Next room  >";
            wallsLabel.text = session.IsInDetail ? "Inspect model" : session.IsFraming ? "Show walls" : "Hide walls";
            roofLabel.text = session.IsInDetail ? "Hotspots on / off" : session.IsRoofHidden ? "Show roof" : "Hide roof";
            detailLabel.text = session.IsInDetail ? "Return to room" : "Window study";
            layersLabel.text = session.IsInDetail ? (session.IsExploded ? "Assemble" : "Separate layers") : "Fittings";
            muteLabel.text = session.IsMuted ? "Narration on" : "Narration off";
            for (int i = 0; i < fittingLabels.Length; i++)
                fittingLabels[i].text = (session.fittings.groups[i].shown ? "Hide " : "Show ") + session.fittings.groups[i].label;
        }
        public void Toggle() { bool show = !IsVisible; menu.gameObject.SetActive(show); if (show) Place(); }
        public void Show() => menu.gameObject.SetActive(true);
        public void Place()
        {
            Vector3 forward = Vector3.ProjectOnPlane(session.rig.Camera.transform.forward, Vector3.up).normalized;
            if (forward.sqrMagnitude < 0.5f) forward = Vector3.forward;
            Physics.SyncTransforms();
            // Check the entire panel and its sight lines, including thin studs. Try
            // both sides before moving it closer, retaining the same angular size.
            foreach (float distance in new[] { 1.35f, 1.1f, .85f, .65f, .45f, .3f })
            foreach (float angle in new[] { 48f, -48f, 72f, -72f, 24f, -24f, 0f })
            {
                PosePanel(Quaternion.AngleAxis(angle, Vector3.up) * forward, distance);
                if (HasClearPlacement()) return;
            }
            // Tracking can initially report a head at floor level. A later arrival
            // or A-button recall places the panel again using the tracked pose.
            PosePanel(forward, .45f);
        }
        void PosePanel(Vector3 direction, float distance)
        {
            menu.transform.SetPositionAndRotation(session.rig.Camera.transform.position + direction * distance -
                Vector3.up * distance * .07f, Quaternion.LookRotation(direction, Vector3.up));
            menu.transform.localScale = Vector3.one * (.001f * distance / 1.35f);
        }
        public bool HasClearPlacement()
        {
            Transform panel = menu.transform;
            float scale = panel.lossyScale.x;
            if (Physics.CheckBox(panel.position, new Vector3(350 * scale + .015f, 450 * scale + .015f, .025f),
                panel.rotation, session.obstructionMask, QueryTriggerInteraction.Ignore)) return false;
            Vector3 eye = session.rig.Camera.transform.position;
            for (int x = 0; x <= 4; x++)
            for (int y = 0; y <= 6; y++)
            {
                Vector3 sample = panel.TransformPoint(new Vector3(-350 + 175 * x, -450 + 150 * y, 0));
                Vector3 ray = sample - eye;
                if (Physics.SphereCast(eye, .015f, ray.normalized, out _, ray.magnitude + .01f,
                    session.obstructionMask, QueryTriggerInteraction.Ignore)) return false;
            }
            return true;
        }
        Canvas MakeCanvas(string name, Vector2 size)
        {
            var root = new GameObject(name, typeof(RectTransform), typeof(Canvas), typeof(TrackedDeviceGraphicRaycaster));
            var canvas = root.GetComponent<Canvas>(); canvas.renderMode = RenderMode.WorldSpace; canvas.worldCamera = session.rig.Camera;
            root.GetComponent<RectTransform>().sizeDelta = size; return canvas;
        }
        GameObject Group(string name)
        {
            var group = new GameObject(name, typeof(RectTransform)); group.transform.SetParent(menu.transform, false);
            var rect = group.GetComponent<RectTransform>(); rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one;
            rect.offsetMin = rect.offsetMax = Vector2.zero; return group;
        }
        public void Initialize(FrameLabSession owner)
        {
            session = owner;
            menu = MakeCanvas("Side guide", new Vector2(700, 900));
            menu.gameObject.AddComponent<Image>().color = new Color(0.11f, 0.095f, 0.075f, 1);
            heading = AddText(menu.transform, "Leichhardt", 31, new Vector2(25, -20), new Vector2(650, 65));
            heading.color = new Color(1, 0.85f, 0.57f);
            guide = Group("Guide controls");
            prompt = AddText(guide.transform, "", 25, new Vector2(25, -90), new Vector2(650, 90));
            prompt.color = new Color(1, 0.88f, 0.64f);
            instructions = AddText(guide.transform, "", 23, new Vector2(25, -190), new Vector2(650, 320));
            status = AddText(guide.transform, "", 19, new Vector2(25, -510), new Vector2(650, 45));
            AddButton(guide.transform, "<  Previous", 25, 565, 315, session.Previous);
            nextLabel = AddButton(guide.transform, "Next room  >", 360, 565, 315, session.Next, true);
            wallsLabel = AddButton(guide.transform, "Hide walls", 25, 628, 315, () => { if (session.IsInDetail) ShowInspection(true); else session.ToggleFraming(); });
            roofLabel = AddButton(guide.transform, "Hide roof", 360, 628, 315, () => { if (session.IsInDetail) session.inspection.ToggleHotspots(); else session.ToggleRoof(); });
            detailLabel = AddButton(guide.transform, "Window study", 25, 691, 315, session.ToggleDetail);
            layersLabel = AddButton(guide.transform, "Fittings", 360, 691, 315, () => { if (session.IsInDetail) session.ToggleExploded(); else ShowFittings(true); });
            AddButton(guide.transform, "Replay", 25, 754, 315, session.ReplayNarration);
            muteLabel = AddButton(guide.transform, "Narration off", 360, 754, 315, session.ToggleNarration);
            AddButton(guide.transform, "Rooms", 25, 817, 315, () => ShowRooms(true));
            AddButton(guide.transform, "A · Hide guide", 360, 817, 315, Toggle);
            roomList = Group("Room list");
            AddText(roomList.transform, "Choose a room to visit", 27, new Vector2(25, -110), new Vector2(650, 70));
            for (int i = 0; i < 6; i++)
            {
                int slot = i;
                roomLabels[i] = AddButton(roomList.transform, "", 25, 200 + i * 72, 650, () => session.GoTo(roomPage * 6 + slot));
                roomButtons[i] = roomLabels[i].GetComponentInParent<Button>();
            }
            pageLabel = AddText(roomList.transform, "", 23, new Vector2(25, -650), new Vector2(650, 45));
            AddButton(roomList.transform, "<  Earlier rooms", 25, 710, 315, () => ChangeRoomPage(-1));
            AddButton(roomList.transform, "More rooms  >", 360, 710, 315, () => ChangeRoomPage(1));
            AddButton(roomList.transform, "Back to guide", 25, 800, 650, () => ShowRooms(false));
            inspection = Group("Inspection controls");
            inspection.AddComponent<FrameLabInspectionPanel>().Initialize(session, this);
            fittings = Group("Fittings controls");
            AddText(fittings.transform, "Choose what stays visible", 27, new Vector2(25, -100), new Vector2(650, 45));
            AddButton(fittings.transform, "Hide all fittings", 25, 160, 315, () => session.SetAllFittings(false));
            AddButton(fittings.transform, "Show all fittings", 360, 160, 315, () => session.SetAllFittings(true));
            fittingLabels = new Text[session.fittings.groups.Length];
            for (int i = 0; i < fittingLabels.Length; i++)
            {
                int group = i;
                fittingLabels[i] = AddButton(fittings.transform, "", 25, 235 + i * 65, 650, () => session.ToggleFitting(group));
                fittingLabels[i].transform.parent.name = "Fitting " + i + " button";
            }
            AddText(fittings.transform, "Walls and roof are controlled separately. Hide walls to reveal the timber stairs.", 23,
                new Vector2(25, -640), new Vector2(650, 90));
            AddButton(fittings.transform, "Restart tour", 25, 744, 650, session.ResetSession);
            AddButton(fittings.transform, "Back to guide", 25, 817, 650, () => ShowFittings(false));
            ShowRooms(false);
            if (EventSystem.current == null) new GameObject("XR UI events", typeof(EventSystem), typeof(XRUIInputModule));
        }
        public void ShowRooms(bool show)
        {
            guide.SetActive(!show); roomList.SetActive(show); if (inspection != null) inspection.SetActive(false);
            if (fittings != null) fittings.SetActive(false);
            if (show) { roomPage = session.Location / 6; RefreshRooms(); }
        }
        public void ShowInspection(bool show)
        {
            inspection.SetActive(show); guide.SetActive(!show); roomList.SetActive(false);
            fittings.SetActive(false);
        }
        public void ShowFittings(bool show)
        {
            fittings.SetActive(show); guide.SetActive(!show); roomList.SetActive(false); inspection.SetActive(false);
            Refresh();
        }
        void ChangeRoomPage(int delta) { roomPage = Mathf.Clamp(roomPage + delta, 0, (session.destinations.Length - 1) / 6); RefreshRooms(); }
        void RefreshRooms()
        {
            for (int i = 0; i < 6; i++)
            {
                int index = roomPage * 6 + i; roomButtons[i].gameObject.SetActive(index < session.tour.rooms.Length);
                if (index < session.tour.rooms.Length) roomLabels[i].text = (index + 1) + ". " + session.tour.rooms[index].title;
            }
            pageLabel.text = "Page " + (roomPage + 1) + " / " + ((session.destinations.Length + 5) / 6);
        }
        public static Text AddButton(Transform parent, string label, float x, float y, float width, UnityAction action, bool accent = false)
        {
            var go = new GameObject(label + " button", typeof(RectTransform), typeof(Image), typeof(Button)); go.transform.SetParent(parent, false);
            var rect = go.GetComponent<RectTransform>(); rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = new Vector2(x, -y); rect.sizeDelta = new Vector2(width, 54);
            go.GetComponent<Image>().color = accent ? new Color(0.85f, 0.62f, 0.24f) : new Color(0.27f, 0.23f, 0.18f);
            var button = go.GetComponent<Button>(); button.onClick.AddListener(action);
            var colors = button.colors; colors.highlightedColor = new Color(1, 0.88f, 0.64f); button.colors = colors;
            Text text = AddText(go.transform, label, 24, new Vector2(8, -3), new Vector2(width - 16, 48)); text.alignment = TextAnchor.MiddleCenter;
            if (accent) text.color = new Color(0.12f, 0.085f, 0.04f); return text;
        }
        public static Text AddText(Transform parent, string value, int size, Vector2 position, Vector2 dimensions)
        {
            var go = new GameObject("Label", typeof(RectTransform), typeof(Text)); go.transform.SetParent(parent, false);
            var rect = go.GetComponent<RectTransform>(); rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = position; rect.sizeDelta = dimensions;
            var text = go.GetComponent<Text>(); text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.text = value; text.fontSize = size; text.color = new Color(0.97f, 0.95f, 0.90f); text.raycastTarget = false; return text;
        }
        void OnDestroy() { if (menu != null) Destroy(menu.gameObject); }
    }
}
