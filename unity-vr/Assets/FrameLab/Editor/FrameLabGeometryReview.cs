using System.Collections;
using System.IO;
using FrameLab;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Early geometry/material inspection; explicitly separate from the baked
// release screenshots and the full session test. Never claims a lighting pass.
public static class FrameLabGeometryReview
{
    public static void Run()
    {
        SessionState.SetBool("LeichhardtGeometryReview", true);
        EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        EditorApplication.EnterPlaymode();
    }
    [InitializeOnLoadMethod]
    static void Register()
    {
        EditorApplication.playModeStateChanged += state => {
            if (state != PlayModeStateChange.EnteredPlayMode || !SessionState.GetBool("LeichhardtGeometryReview", false)) return;
            SessionState.SetBool("LeichhardtGeometryReview", false);
            new GameObject("Geometry review capture").AddComponent<LeichhardtGeometryCapture>();
        };
    }
}
public class LeichhardtGeometryCapture : MonoBehaviour
{
    IEnumerator Start()
    {
        yield return new WaitForSecondsRealtime(1.5f);
        var session = FindAnyObjectByType<FrameLabSession>();
        if (session == null) { Debug.LogError("Missing session for geometry review"); EditorApplication.Exit(1); yield break; }
        if (session.Guide.IsVisible) session.Guide.Toggle();
        Directory.CreateDirectory("Builds/Preview/Geometry");
        session.rig.Camera.fieldOfView = 75;
        void Shot(string name, Vector3 eye, Vector3 target) => FrameLabBuild.RenderPreview(session.rig.Camera, eye, target, "Geometry/" + name + ".png");
        Shot("01-exterior",new Vector3(-35,10,15),new Vector3(-15,2,-4));
        Shot("02-theatre",new Vector3(-26,4.809f,-2.4f),new Vector3(-23.2f,5,-2.4f));
        Shot("03-family-recess",new Vector3(-16,1.65f,-1.9f),new Vector3(-18.5f,1.4f,-1.9f));
        Shot("04-ensuite",new Vector3(-19.85f,1.65f,-1.9f),new Vector3(-18.6f,1.4f,-2));
        Shot("05-powder",new Vector3(-21.05f,1.45f,-6.1f),new Vector3(-21.15f,1.5f,-7.9f));
        Shot("06-stairs",new Vector3(-26.2f,1.65f,-7.12f),new Vector3(-22.3f,2.1f,-7.12f));
        Shot("07-kitchen",new Vector3(-17.2f,1.65f,-4.3f),new Vector3(-15.4f,1.2f,-6.6f));
        Shot("08-laundry",new Vector3(-7.6f,1.65f,-5.4f),new Vector3(-8.5f,1.2f,-6.6f));
        Shot("09-upperbath",new Vector3(-13.15f,4.809f,-5.65f),new Vector3(-14f,4.3f,-6.75f));
        File.WriteAllText("Builds/Preview/Geometry/status.txt","Actual imported Unity scene in play mode. Geometry/material review only; final lighting acceptance and headset checks are separate.\n");
        Debug.Log("LEICHHARDT_GEOMETRY_CAPTURE_COMPLETE");
        EditorApplication.Exit(0);
    }
}
