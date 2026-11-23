using UnityEngine;
using UnityEngine.UI;

namespace FrameLab
{
    public class FrameLabInspectionPanel : MonoBehaviour
    {
        FrameLabInspection inspection;
        Slider slider, rotationSlider;
        Text amount, rotationAmount, selected, description, isolate, zoom;
        public void Initialize(FrameLabSession session, FrameLabGuide guide)
        {
            inspection = session.inspection;
            FrameLabGuide.AddButton(transform, "Tour guide", 25, 95, 315, () => guide.ShowInspection(false));
            FrameLabGuide.AddButton(transform, "A · Hide guide", 360, 95, 315, guide.Toggle);
            FrameLabGuide.AddText(transform, "Point and hold the grip to move or rotate.\nSelect a number to learn about that component.", 21, new Vector2(25, -163), new Vector2(650, 55));
            amount = FrameLabGuide.AddText(transform, "", 24, new Vector2(25, -225), new Vector2(650, 35));
            var root = new GameObject("Explosion slider", typeof(RectTransform), typeof(Slider)); root.transform.SetParent(transform, false);
            var rect = root.GetComponent<RectTransform>(); rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = new Vector2(40, -265); rect.sizeDelta = new Vector2(620, 28);
            var track = new GameObject("Track", typeof(RectTransform), typeof(Image)); track.transform.SetParent(root.transform, false);
            track.GetComponent<RectTransform>().sizeDelta = new Vector2(620, 16); track.GetComponent<Image>().color = new Color(.36f, .33f, .28f);
            var handle = new GameObject("Handle", typeof(RectTransform), typeof(Image)); handle.transform.SetParent(root.transform, false);
            var handleRect = handle.GetComponent<RectTransform>(); handleRect.sizeDelta = new Vector2(34, 48);
            var handleImage = handle.GetComponent<Image>(); handleImage.color = new Color(1, .75f, .32f);
            slider = root.GetComponent<Slider>(); slider.minValue = 0; slider.maxValue = 1; slider.handleRect = handleRect;
            slider.targetGraphic = handleImage; slider.direction = Slider.Direction.LeftToRight;
            slider.onValueChanged.AddListener(session.SetExplosionAmount);
            FrameLabGuide.AddButton(transform, "Zoom −", 25, 320, 205, () => inspection.Zoom(1 / 1.15f));
            zoom = FrameLabGuide.AddButton(transform, "Zoom +", 247, 320, 205, () => inspection.Zoom(1.15f));
            FrameLabGuide.AddButton(transform, "Reset all", 470, 320, 205, inspection.ResetAll);
            rotationAmount = FrameLabGuide.AddText(transform, "", 21, new Vector2(25, -377), new Vector2(420, 30));
            var rotationRoot = new GameObject("Rotation slider", typeof(RectTransform), typeof(Slider));
            rotationRoot.transform.SetParent(transform, false);
            var rotationRect = rotationRoot.GetComponent<RectTransform>();
            rotationRect.anchorMin = rotationRect.anchorMax = rotationRect.pivot = new Vector2(0, 1);
            rotationRect.anchoredPosition = new Vector2(40, -415); rotationRect.sizeDelta = new Vector2(390, 24);
            var rotationTrack = new GameObject("Track", typeof(RectTransform), typeof(Image));
            rotationTrack.transform.SetParent(rotationRoot.transform, false);
            rotationTrack.GetComponent<RectTransform>().sizeDelta = new Vector2(390, 16);
            rotationTrack.GetComponent<Image>().color = new Color(.36f, .33f, .28f);
            var rotationHandle = new GameObject("Handle", typeof(RectTransform), typeof(Image));
            rotationHandle.transform.SetParent(rotationRoot.transform, false);
            var rotationHandleRect = rotationHandle.GetComponent<RectTransform>();
            rotationHandleRect.sizeDelta = new Vector2(34, 40);
            var rotationHandleImage = rotationHandle.GetComponent<Image>();
            rotationHandleImage.color = new Color(1, .75f, .32f);
            rotationSlider = rotationRoot.GetComponent<Slider>();
            rotationSlider.minValue = -180; rotationSlider.maxValue = 180;
            rotationSlider.handleRect = rotationHandleRect; rotationSlider.targetGraphic = rotationHandleImage;
            rotationSlider.direction = Slider.Direction.LeftToRight;
            rotationSlider.onValueChanged.AddListener(inspection.SetRotation);
            isolate = FrameLabGuide.AddButton(transform, "Isolate part", 470, 383, 205, inspection.ToggleIsolation);
            for (int i = 0; i < inspection.parts.Length; i++)
            {
                int index = i;
                FrameLabGuide.AddButton(transform, (i + 1) + " · " + inspection.parts[i].shortName,
                    25 + (i % 3) * 222.5f, 466 + (i / 3) * 61, 205, () => inspection.SelectPart(index));
            }
            selected = FrameLabGuide.AddText(transform, "", 24, new Vector2(25, -656), new Vector2(650, 34));
            selected.color = new Color(1, .85f, .57f);
            description = FrameLabGuide.AddText(transform, "", 20, new Vector2(25, -701), new Vector2(650, 112));
            FrameLabGuide.AddButton(transform, "All parts", 25, 825, 205, inspection.ShowAll);
            FrameLabGuide.AddButton(transform, "Replay part", 247, 825, 205, inspection.ReplayPart);
            FrameLabGuide.AddButton(transform, "Return to room", 470, 825, 205, session.ToggleDetail);
            inspection.Changed += Refresh; Refresh();
        }
        void Refresh()
        {
            slider.SetValueWithoutNotify(inspection.Explosion);
            rotationSlider.SetValueWithoutNotify(inspection.RotationDegrees);
            rotationAmount.text = "Rotate  " + Mathf.RoundToInt(inspection.RotationDegrees) + "°";
            amount.text = "Explode  " + Mathf.RoundToInt(inspection.Explosion * 100) + "%   ·   Size " + Mathf.RoundToInt(inspection.ZoomLevel * 100) + "%";
            isolate.text = inspection.IsIsolated ? "End isolation" : "Isolate part";
            selected.text = inspection.Current == null ? "Explore all nine components" : inspection.Current.title;
            description.text = inspection.Current == null ? "Drag the slider to separate the assembly. Choose a hotspot or component button, then Isolate part for an unobstructed view. Reset all restores its position, rotation, size and assembly." : inspection.Current.description;
        }
        void OnDestroy() { if (inspection != null) inspection.Changed -= Refresh; }
    }
}
