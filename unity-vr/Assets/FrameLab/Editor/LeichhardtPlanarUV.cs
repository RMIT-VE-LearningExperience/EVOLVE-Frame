using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

// Preserve one lightmap chart across each connected planar finish. glTF can
// split vertices at triangle normals/UVs; coordinate welding here is for chart
// membership only and does not change the model's geometry or visible normals.
public static class LeichhardtPlanarUV
{
    sealed class Chart
    {
        public readonly List<int> triangles = new();
        public Vector3 u,v;
        public Vector2 min,max;
    }

    public static Mesh Build(Mesh source)
    {
        var vertices=source.vertices;var normals=source.normals;
        var primary=source.uv;var tangents=source.tangents;var colors=source.colors;
        var indices=source.triangles;int count=indices.Length/3;
        var parent=Enumerable.Range(0,count).ToArray();
        int Find(int t) { while(parent[t]!=t){parent[t]=parent[parent[t]];t=parent[t];}return t; }
        void Join(int a,int b) { parent[Find(a)]=Find(b); }
        var contacts=new Dictionary<(int,int,int,int,int,int,int),int>();
        var faceNormals=new Vector3[count];
        for(int t=0;t<count;t++)
        {
            Vector3 a=vertices[indices[t*3]],b=vertices[indices[t*3+1]],c=vertices[indices[t*3+2]];
            Vector3 n=Vector3.Cross(b-a,c-a).normalized;
            if(n.sqrMagnitude<.5f)n=normals[indices[t*3]];
            faceNormals[t]=n;
            int nx=Mathf.RoundToInt(n.x*1000),ny=Mathf.RoundToInt(n.y*1000),nz=Mathf.RoundToInt(n.z*1000);
            int plane=Mathf.RoundToInt(Vector3.Dot(n,a)*1000);
            for(int j=0;j<3;j++)
            {
                Vector3 p=vertices[indices[t*3+j]];
                var key=(nx,ny,nz,plane,Mathf.RoundToInt(p.x*10000),Mathf.RoundToInt(p.y*10000),Mathf.RoundToInt(p.z*10000));
                if(contacts.TryGetValue(key,out int other))Join(t,other);else contacts[key]=t;
            }
        }
        var chartMap=new Dictionary<int,Chart>();
        for(int t=0;t<count;t++)
        {
            int root=Find(t);
            if(!chartMap.TryGetValue(root,out var chart))
            {
                Vector3 n=faceNormals[t];
                Vector3 u=Vector3.Cross(n,Mathf.Abs(n.y)<.9f?Vector3.up:Vector3.forward).normalized;
                chart=new Chart {u=u,v=Vector3.Cross(n,u),min=new Vector2(float.PositiveInfinity,float.PositiveInfinity),max=new Vector2(float.NegativeInfinity,float.NegativeInfinity)};
                chartMap[root]=chart;
            }
            chart.triangles.Add(t);
            for(int j=0;j<3;j++)
            {
                Vector3 p=vertices[indices[t*3+j]];
                Vector2 uv=new Vector2(Vector3.Dot(p,chart.u),Vector3.Dot(p,chart.v));
                chart.min=Vector2.Min(chart.min,uv);chart.max=Vector2.Max(chart.max,uv);
            }
        }
        var charts=chartMap.Values.ToArray();
        var tiles=charts.Select(c=>new Texture2D(Mathf.Max(8,Mathf.CeilToInt((c.max.x-c.min.x)*32)),Mathf.Max(8,Mathf.CeilToInt((c.max.y-c.min.y)*32)),TextureFormat.RGBA32,false)).ToArray();
        var atlas=new Texture2D(2,2,TextureFormat.RGBA32,false);
        Rect[] rects=atlas.PackTextures(tiles,8,4096,false);
        if(rects.Length!=charts.Length)throw new InvalidOperationException("Planar lightmap packing failed: "+source.name);
        var outVertices=new List<Vector3>();var outNormals=new List<Vector3>();var outUV=new List<Vector2>();var lightUV=new List<Vector2>();
        var outTangents=new List<Vector4>();var outColors=new List<Color>();var outIndices=new List<int>();
        for(int k=0;k<charts.Length;k++)
        {
            var chart=charts[k];var rect=rects[k];var remap=new Dictionary<int,int>();
            foreach(int t in chart.triangles)
            for(int j=0;j<3;j++)
            {
                int original=indices[t*3+j];
                if(!remap.TryGetValue(original,out int mapped))
                {
                    mapped=outVertices.Count;remap[original]=mapped;
                    Vector3 p=vertices[original];Vector2 span=chart.max-chart.min;
                    float x=(Vector3.Dot(p,chart.u)-chart.min.x)/Mathf.Max(span.x,.000001f);
                    float y=(Vector3.Dot(p,chart.v)-chart.min.y)/Mathf.Max(span.y,.000001f);
                    outVertices.Add(p);outNormals.Add(normals[original]);
                    outUV.Add(primary.Length==vertices.Length?primary[original]:Vector2.zero);
                    lightUV.Add(new Vector2(rect.x+rect.width*x,rect.y+rect.height*y));
                    if(tangents.Length==vertices.Length)outTangents.Add(tangents[original]);
                    if(colors.Length==vertices.Length)outColors.Add(colors[original]);
                }
                outIndices.Add(mapped);
            }
        }
        var result=new Mesh { name=source.name+" planar lighting",indexFormat=outVertices.Count>65535?IndexFormat.UInt32:IndexFormat.UInt16 };
        result.SetVertices(outVertices);result.SetNormals(outNormals);result.SetUVs(0,outUV);result.SetUVs(1,lightUV);result.SetTriangles(outIndices,0);
        if(outTangents.Count==outVertices.Count)result.SetTangents(outTangents);else result.RecalculateTangents();
        if(outColors.Count==outVertices.Count)result.SetColors(outColors);
        result.RecalculateBounds();
        foreach(var tile in tiles)UnityEngine.Object.DestroyImmediate(tile);
        UnityEngine.Object.DestroyImmediate(atlas);
        Debug.Log("LEICHHARDT_PLANAR_UV "+source.name+" triangles="+count+" charts="+charts.Length+" vertices="+outVertices.Count);
        return result;
    }
}
