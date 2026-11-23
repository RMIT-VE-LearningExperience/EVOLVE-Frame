using System;
using System.Linq;
using System.Collections.Generic;
using System.IO;
using Autodesk.Revit.DB;
using Newtonsoft.Json.Linq;
namespace EvolveRevit {
 public static class Components {
  const string Root=@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\";
  public static object CreateFamilies(Document d){
   var rows=JArray.Parse(File.ReadAllText(Root+"openings_manifest.json"));
   var existing=new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().Select(f=>f.Name).ToHashSet();int count=0;
   foreach(var row in rows.GroupBy(r=>(string)r["family"]).Select(g=>g.First()).Where(r=>!existing.Contains((string)r["family"])).Take(5)){
    bool window=(bool)row["window"];var f=d.Application.NewFamilyDocument(@"C:\ProgramData\Autodesk\RVT 2027\Family Templates\English\Metric "+(window?"Window":"Door")+".rft");
    try{using(var t=new Transaction(f,"A11 opening family")){t.Start();var fm=f.FamilyManager;fm.NewType("A11 nominal size");double w=(double)row["width"],h=(double)row["height"];
     fm.SetFormula(fm.get_Parameter(BuiltInParameter.FAMILY_WIDTH_PARAM),w+" mm");fm.SetFormula(fm.get_Parameter(BuiltInParameter.FAMILY_HEIGHT_PARAM),h+" mm");
     var sill=fm.Parameters.Cast<FamilyParameter>().FirstOrDefault(p=>p.Definition.Name=="Default Sill Height");if(sill!=null)fm.Set(sill,0.0);
     var desc=fm.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION);if(desc!=null)fm.Set(desc,(string)row["note"]);
     foreach(var e in new FilteredElementCollector(f).OfClass(typeof(Extrusion)).ToList())f.Delete(e.Id);
     var host=new FilteredElementCollector(f).OfClass(typeof(Wall)).Cast<Wall>().First();((LocationCurve)host.Location).Curve=Line.CreateBound(new XYZ(-Math.Max(w/2+500,2000)/304.8,0,0),new XYZ(Math.Max(w/2+500,2000)/304.8,0,0));
     var metal=Material.Create(f,"LC Aluminium - charcoal coordination");((Material)f.GetElement(metal)).Color=new Color(67,72,76);((Material)f.GetElement(metal)).MaterialClass="Metal";
     var glass=Material.Create(f,"LC Glazing - specification pending");var gm=(Material)f.GetElement(glass);gm.Color=new Color(150,187,195);gm.Transparency=(bool)row["obscure"]?35:65;gm.MaterialClass="Glass";
     var timber=Material.Create(f,"LC Door timber - selected finish pending");((Material)f.GetElement(timber)).Color=new Color(133,92,58);((Material)f.GetElement(timber)).MaterialClass="Wood";
     var plane=SketchPlane.Create(f,Plane.CreateByNormalAndOrigin(XYZ.BasisZ,XYZ.Zero));
     Action<double,double,double,double,double,double,ElementId> box=(x0,x1,y0,y1,z0,z1,mat)=>{var pts=new[]{new XYZ(x0/304.8,y0/304.8,0),new XYZ(x1/304.8,y0/304.8,0),new XYZ(x1/304.8,y1/304.8,0),new XYZ(x0/304.8,y1/304.8,0)};var ca=new CurveArray();for(int i=0;i<4;i++)ca.Append(Line.CreateBound(pts[i],pts[(i+1)%4]));var profile=new CurveArrArray();profile.Append(ca);var ex=f.FamilyCreate.NewExtrusion(true,profile,plane,(z1-z0)/304.8);ex.StartOffset=z0/304.8;ex.EndOffset=z1/304.8;ex.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM).Set(mat);};
     string style=(string)row["style"];var frame=style=="timber"||style=="passage"?timber:metal;double k=50;
     box(-w/2,-w/2+k,-50,50,0,h,frame);box(w/2-k,w/2,-50,50,0,h,frame);box(-w/2+k,w/2-k,-50,50,h-k,h,frame);
     if(window||style=="glazed"||style=="garage")box(-w/2+k,w/2-k,-50,50,0,k,frame);
     var vs=row["verticals"].Select(v=>(double)v).ToList();var hs=row["horizontals"].Select(v=>(double)v).ToList();
     if(style=="garage")for(int i=1;i<6;i++)hs.Add(i/6.0);
     foreach(var v in vs)box(-w/2+w*v-20,-w/2+w*v+20,-50,50,k,h-k,frame);
     foreach(var z in hs)box(-w/2+k,w/2-k,-50,50,h*z-20,h*z+20,frame);
     if(window||style=="glazed"){
      var xx=new List<double>{-w/2+k};xx.AddRange(vs.Select(v=>-w/2+w*v));xx.Add(w/2-k);var zz=new List<double>{k};zz.AddRange(hs.Select(v=>h*v));zz.Add(h-k);
      for(int i=0;i<xx.Count-1;i++)for(int j=0;j<zz.Count-1;j++)box(xx[i],xx[i+1],-3,3,zz[j],zz[j+1],glass);
     }else if(style!="passage"){
      var xx=new List<double>{-w/2+k};xx.AddRange(vs.Select(v=>-w/2+w*v));xx.Add(w/2-k);for(int i=0;i<xx.Count-1;i++)box(xx[i]+2,xx[i+1]-2,-20,20,4,h-k,style=="garage"?metal:timber);
     }
     t.Commit();}
     f.SaveAs(Root+"families\\"+(string)row["family"]+".rfa",new SaveAsOptions{OverwriteExistingFile=true});f.LoadFamily(d,new OverwriteFamily());count++;
    }finally{f.Close(false);}
   }return new{created=count};
  }
 }
}
