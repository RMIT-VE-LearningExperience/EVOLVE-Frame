using System;
using System.IO;
using UnityEngine;

namespace FrameLab
{
    // Local USB diagnostics in development APKs only. No network listener and
    // no automatic movement: each action requires an explicit ADB-written file.
    public class FrameLabDeviceCheck : MonoBehaviour
    {
        [Serializable] class Command { public string id, action; public int index; public float value; }
        [Serializable] class State
        {
            public string id, version, room, error;
            public bool changing, focused, guide, narration, detail, isolated;
            public int location, hotspots, visibleParts;
            public float explosion, zoom, rotation;
            public Vector3 eye;
            public bool framing, roofHidden;
            public bool[] fittingsShown;
        }
        string lastId; float nextPoll; FrameLabSession session;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Attach()
        {
            if (!Debug.isDebugBuild || Application.platform != RuntimePlatform.Android) return;
            var owner=FindAnyObjectByType<FrameLabSession>();
            if(owner!=null) owner.gameObject.AddComponent<FrameLabDeviceCheck>().session=owner;
        }
        void Update()
        {
            if (Time.realtimeSinceStartup<nextPoll || session==null || session.Guide==null) return;
            nextPoll=Time.realtimeSinceStartup+.3f;
            string path=Path.Combine(Application.persistentDataPath,"device-command.json");
            if (!File.Exists(path)) return;
            try
            {
                var c=JsonUtility.FromJson<Command>(File.ReadAllText(path));
                if (c == null) return;
                if (string.IsNullOrEmpty(c.id)) return;
                if(c.id!=lastId)
                {
                    if(session.IsChanging) return;
                    lastId=c.id;
                    switch(c.action)
                    {
                        case "goto":session.GoTo(c.index);break;
                        case "menu":session.HandleMenuInput(false);session.HandleMenuInput(true);session.HandleMenuInput(false);break;
                        case "study":if(!session.IsInDetail)session.ToggleDetail();break;
                        case "explode":session.SetExplosionAmount(c.value);break;
                        case "part":session.inspection.SelectPart(c.index);break;
                        case "isolate":session.inspection.ToggleIsolation();break;
                        case "zoom":session.inspection.Zoom(c.value);break;
                        case "rotate":session.inspection.Rotate(c.value);break;
                        case "rotation":session.inspection.SetRotation(c.value);break;
                        case "reset-study":session.inspection.ResetAll();break;
                        case "restart":session.ResetSession();break;
                        case "walls":session.ToggleFraming();break;
                        case "roof":session.ToggleRoof();break;
                        case "fitting":session.ToggleFitting(c.index);break;
                        case "all-fittings":session.SetAllFittings(c.value > .5f);break;
                        case "fittings-panel":session.Guide.ShowFittings(true);break;
                        case "status":break;
                        default:throw new ArgumentException("Unknown device check action");
                    }
                    Debug.Log("FRAME_LAB_DEVICE_COMMAND "+c.id+" "+c.action);
                }
                var s=new State { id=c.id,version=Application.version,room=session.Current.id,
                    location=session.Location,changing=session.IsChanging,focused=Application.isFocused,
                    guide=session.Guide.IsVisible,narration=session.IsSpeaking,detail=session.IsInDetail,
                    hotspots=session.inspection.HotspotCount,visibleParts=session.inspection.VisiblePartCount,
                    explosion=session.inspection.Explosion,zoom=session.inspection.ZoomLevel,rotation=session.inspection.RotationDegrees,
                    isolated=session.inspection.IsIsolated,eye=session.rig.Camera.transform.position,
                    framing=session.IsFraming,roofHidden=session.IsRoofHidden,
                    fittingsShown=Array.ConvertAll(session.fittings.groups,g=>g.shown) };
                File.WriteAllText(Path.Combine(Application.persistentDataPath,"device-state.json"),JsonUtility.ToJson(s,true));
            }
            catch(Exception e) { Debug.LogError("FRAME_LAB_DEVICE_CHECK "+e); }
        }
    }
}
