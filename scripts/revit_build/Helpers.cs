using System;
using System.Linq;
using Autodesk.Revit.DB;
namespace EvolveRevit {
 public class OverwriteFamily : IFamilyLoadOptions {
  public bool OnFamilyFound(bool inUse,out bool overwrite){overwrite=true;return true;}
  public bool OnSharedFamilyFound(Family shared,bool inUse,out FamilySource source,out bool overwrite){source=FamilySource.Family;overwrite=true;return true;}
 }
 public static class Helpers {
  public static string UpdateTimber(Document d){
   var family=new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().Single(f=>f.Name=="LC Rectangular Timber");
   var f=d.EditFamily(family);
   try{using(var t=new Transaction(f,"Timber material and type identifiers")){t.Start();
    var mat=new FilteredElementCollector(f).OfClass(typeof(Material)).Cast<Material>().Single(m=>m.Name=="LC Timber - MGP10");mat.Color=new Color(201,159,92);mat.MaterialClass="Wood";
    foreach(var e in new FilteredElementCollector(f).OfClass(typeof(Extrusion)).Cast<Extrusion>())e.get_Parameter(BuiltInParameter.MATERIAL_ID_PARAM).Set(mat.Id);
    var fm=f.FamilyManager;foreach(FamilyType ft in fm.Types){fm.CurrentType=ft;var p=fm.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK);if(p!=null)fm.Set(p,"LC-T-"+ft.Name);}
    t.Commit();}
    f.SaveAs(@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\families\LC Rectangular Timber.rfa",new SaveAsOptions{OverwriteExistingFile=true});f.LoadFamily(d,new OverwriteFamily());return "Timber material updated";
   }finally{f.Close(false);}
  }
 }
}
