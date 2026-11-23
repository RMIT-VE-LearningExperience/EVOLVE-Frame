using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using FrameLab;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

public static class FrameLabPhoto045
{
    public static void Run()
    {
        SessionState.SetBool("Photo045",true);
        EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        EditorApplication.EnterPlaymode();
    }
    [InitializeOnLoadMethod] static void Register()
    {
        EditorApplication.playModeStateChanged += state => {
            if (state==PlayModeStateChange.EnteredPlayMode && SessionState.GetBool("Photo045",false))
            { SessionState.SetBool("Photo045",false); new GameObject("Photo045").AddComponent<FrameLabPhoto045Runner>(); }
        };
    }
}
public class FrameLabPhoto045Runner : MonoBehaviour
{
    [Serializable] public class Shot { public string file,title,category; public Vector3 position,target; public float fieldOfView; }
    [Serializable] public class Set { public Shot[] shots; }
    IEnumerator Start()
    {
        yield return new WaitForSecondsRealtime(1.5f);
        var s=UnityEngine.Object.FindAnyObjectByType<FrameLabSession>();
        if(s.Guide.IsVisible)s.Guide.Toggle();
        var path="Builds/Preview/Review/manifest.json";
        var shots=new List<Shot>(JsonUtility.FromJson<Set>(File.ReadAllText(path)).shots);
        void Take(string file,string title,Vector3 position,Vector3 target,float fov=70)
        {
            s.rig.Camera.fieldOfView=fov;
            FrameLabBuild.RenderPreview(s.rig.Camera,position,target,"Review/"+file+".png");
            shots.RemoveAll(v=>v.file==file+".png");
            shots.Add(new Shot{file=file+".png",title=title,category="Photo corrections",position=position,target=target,fieldOfView=fov});
        }
        Take("65-lined-eave","Bedroom4 west window and lined eave",new Vector3(-7.5f,4.8f,-6.15f),new Vector3(-6.05f,5.5f,-6.15f));
        Take("67-study-skirting","Study wall and skirting junction",new Vector3(-18.0f,4.45f,-1.2f),new Vector3(-17.035f,3.24f,-.25f));
        Take("68-retreat-skirting","Retreat wall and skirting junction",new Vector3(-20.6f,4.45f,-1.3f),new Vector3(-19.525f,3.24f,-.25f));
        Take("69-bedroom2-skirting","Bedroom2 wall and skirting junction",new Vector3(-15.3f,4.45f,-1.2f),new Vector3(-16.225f,3.24f,-.25f));
        s.ToggleDetail();yield return new WaitForSecondsRealtime(.7f);
        s.inspection.SelectPart(3);s.inspection.ToggleIsolation();s.inspection.SetExplosion(.45f);s.inspection.SetRotation(45);
        s.Guide.Show();s.Guide.ShowInspection(true);s.Guide.Place();
        yield return null;
        Take("70-window-rotation-slider","Window inspection rotation slider",s.rig.Camera.transform.position,s.Guide.Panel.position,65);
        // Preserve the review numbers used in the user's earlier feedback.
        int ReviewNumber(Shot shot) => shot.file.StartsWith("room-")
            ? 10 + int.Parse(shot.file.Substring(5,2)) : int.Parse(shot.file.Substring(0,2));
        shots.Sort((a,b)=>ReviewNumber(a).CompareTo(ReviewNumber(b)));
        File.WriteAllText(path,JsonUtility.ToJson(new Set{shots=shots.ToArray()},true));
        Debug.Log("PHOTO045_CAPTURE_PASS count="+shots.Count);
        EditorApplication.Exit(0);
    }
}
