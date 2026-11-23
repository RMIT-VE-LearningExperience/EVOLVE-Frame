using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using FrameLab;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

public static class FrameLabPhoto046
{
    public static void Run()
    {
        SessionState.SetBool("Photo046", true);
        EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        EditorApplication.EnterPlaymode();
    }
    [InitializeOnLoadMethod] static void Register()
    {
        EditorApplication.playModeStateChanged += state => {
            if (state == PlayModeStateChange.EnteredPlayMode && SessionState.GetBool("Photo046", false))
            { SessionState.SetBool("Photo046", false); new GameObject("Photo046").AddComponent<FrameLabPhoto046Runner>(); }
        };
    }
}
public class FrameLabPhoto046Runner : MonoBehaviour
{
    IEnumerator Start()
    {
        yield return new WaitForSecondsRealtime(1.5f);
        var session=UnityEngine.Object.FindAnyObjectByType<FrameLabSession>();
        if(session.Guide.IsVisible)session.Guide.Toggle();
        var path="Builds/Preview/Review/manifest.json";
        var shots=new List<FrameLabPhoto045Runner.Shot>(JsonUtility.FromJson<FrameLabPhoto045Runner.Set>(File.ReadAllText(path)).shots);
        Vector3 B(float x,float y,float z)=>new Vector3(-x,z,-y);
        void Take(string file,string title,Vector3 position,Vector3 target,float fov=65)
        {
            session.rig.Camera.fieldOfView=fov;
            FrameLabBuild.RenderPreview(session.rig.Camera,position,target,"Review/"+file+".png");
            shots.RemoveAll(v=>v.file==file+".png");
            shots.Add(new FrameLabPhoto045Runner.Shot{file=file+".png",title=title,category="Architectural details",position=position,target=target,fieldOfView=fov});
        }
        Take("71-laundry-bulkhead","Laundry bulkhead and cupboard junction",B(7.25f,5.65f,1.75f),B(8.65f,6.40f,2.30f));
        Take("72-ensuite-niche","Ensuite recessed niche and shower",B(20.00f,2.40f,1.65f),B(19.45f,3.85f,1.35f));
        Take("73-bath2-niche","Bath2 recessed niche and tiled walls",B(11.70f,.75f,4.75f),B(10.64f,1.73f,4.58f));
        Take("74-upper-bath-niche","Upper bathroom recessed niche",B(13.00f,6.25f,4.8f),B(14.32f,7.10f,4.6f));
        Take("75-powder-tiling","Powder tile finishes and mounted holder",B(21.40f,6.2f,1.65f),B(20.45f,7.65f,1.1f));
        Take("76-ensuite-wc","Ensuite WC finishes and holder",B(20.05f,.80f,1.45f),B(19.10f,.15f,.9f));
        Take("77-upper-wc-finishes","Upper WC plaster walls and 100mm tiled skirting",B(11.75f,5.75f,4.75f),B(11.8f,7.65f,4.1f));
        Take("78-west-drainage","West elevation downpipes and offset",B(21.0f,-9.0f,4.5f),B(18.6f,-.2f,3.0f),58);
        Take("79-garage-gutters","Garage box gutter and two sumps",B(3.2f,5.3f,6.2f),B(3.2f,2.575f,2.97f),65);
        Take("80-porch-drainage","Porch channel rainhead and spreader",B(30.8f,9.7f,5.9f),B(28.1f,7.2f,3.4f),65);
        Take("81-east-drainage","East elevation pipe connections",B(18.0f,17.0f,5.7f),B(16.0f,8.2f,3.0f),75);
        Take("82-bath2-fittings","Bath2 towel rail and paper holder",B(11.1f,1.45f,4.75f),B(12.1f,.4f,4.2f));
        session.ToggleFraming();
        session.SetAllFittings(false);
        yield return new WaitForSecondsRealtime(.5f);
        Take("83-niche-timber","Illustrative niche framing - load path not assessed",B(19.48f,2.4f,1.55f),B(19.48f,3.85f,1.5f),55);
        int ReviewNumber(FrameLabPhoto045Runner.Shot shot)=>shot.file.StartsWith("room-")?10+int.Parse(shot.file.Substring(5,2)):int.Parse(shot.file.Substring(0,2));
        shots.Sort((a,b)=>ReviewNumber(a).CompareTo(ReviewNumber(b)));
        File.WriteAllText(path,JsonUtility.ToJson(new FrameLabPhoto045Runner.Set{shots=shots.ToArray()},true));
        Debug.Log("PHOTO046_CAPTURE_PASS count="+shots.Count);
        EditorApplication.Exit(0);
    }
}
