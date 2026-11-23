using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

public static class LeichhardtPhotoAudit
{
    [Serializable] class Shot { public string file; public Vector3 position; public Vector3 target; public float fieldOfView; }
    [Serializable] class Shots { public Shot[] shots; }
    public static void Run()
    {
        EditorSceneManager.OpenScene("Assets/FrameLab/Scenes/Leichhardt.unity");
        Physics.SyncTransforms();
        var shots=JsonUtility.FromJson<Shots>(File.ReadAllText("Builds/Preview/Review/manifest.json")).shots;
        foreach (var s in shots)
        {
            if(s.file!="37-upperbath-from-hall.png" && s.file!="39-powder-window.png" && s.file!="47-robe-fitout.png")continue;
            Vector2 p=s.file.StartsWith("37")?new Vector2(565,400):s.file.StartsWith("39")?new Vector2(800,500):new Vector2(550,450);
            Vector3 f=(s.target-s.position).normalized;
            Vector3 r=Vector3.Cross(Vector3.up,f).normalized,u=Vector3.Cross(f,r);
            float tan=Mathf.Tan(s.fieldOfView*Mathf.Deg2Rad/2);
            Vector3 dir=(f+r*((2*p.x/1600-1)*1.6f*tan)+u*((1-2*p.y/1000)*tan)).normalized;
            if(Physics.Raycast(s.position,dir,out var hit,30,1<<8))
            {
                var renderer=hit.collider.GetComponent<MeshRenderer>();
                Debug.Log("PHOTO_RAY "+s.file+" object="+renderer.name+" material="+renderer.sharedMaterial.name+" point="+hit.point.ToString("F6")+" normal="+hit.normal.ToString("F4")+" triangle="+hit.triangleIndex+" uv2="+hit.textureCoord2+" lightmap="+renderer.lightmapIndex);
            }
        }
    }
}
