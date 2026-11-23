try{
var data=Newtonsoft.Json.Linq.JArray.Parse(System.IO.File.ReadAllText(@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\wall_frame_manifest.json"));
var existing=new FilteredElementCollector(document).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Select(e=>e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString()).ToHashSet();var created=new List<long>();
using(var tx=new Transaction(document,"Leichhardt - wall studs plates and noggings")){tx.Start();
 var test=new FilteredElementCollector(document).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().FirstOrDefault(e=>e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString()=="TEST-T1-BC");if(test!=null)document.Delete(test.Id);
 var symbols=new FilteredElementCollector(document).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(s=>s.FamilyName=="LC Rectangular Timber").ToList();var baseSymbol=symbols.Single(s=>s.Name=="90x35 MGP10");
 var level=new FilteredElementCollector(document).OfClass(typeof(Level)).Cast<Level>().Single(l=>l.Name.StartsWith("00 Ground FFL"));
 Func<Newtonsoft.Json.Linq.JToken,XYZ> point=q=>new XYZ((double)q[0]/304.8,(double)q[1]/304.8,(double)q[2]/304.8);
 foreach(var row in data.Where(r=>!existing.Contains((string)r["mark"])).Take(250)){
  var typeName=(int)row["depth"]+"x"+(int)row["width"]+" "+(string)row["grade"];var s=symbols.FirstOrDefault(s=>s.Name==typeName);
  if(s==null){s=(FamilySymbol)baseSymbol.Duplicate(typeName);s.LookupParameter("b").Set((double)row["width"]/304.8);s.LookupParameter("h").Set((double)row["depth"]/304.8);s.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set("LC-T-"+typeName);symbols.Add(s);}
  if(!s.IsActive){s.Activate();document.Regenerate();}
  var a=point(row["a"]);var b=point(row["b"]);var e=document.Create.NewFamilyInstance(Line.CreateBound(a,b),s,level,Autodesk.Revit.DB.Structure.StructuralType.Beam);
  Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(e,0);Autodesk.Revit.DB.Structure.StructuralFramingUtils.DisallowJoinAtEnd(e,1);e.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).Set(1);e.get_Parameter(BuiltInParameter.Y_JUSTIFICATION).Set(1);
  e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set((string)row["mark"]);e.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set((string)row["source"]);
  if(Math.Abs(b.X-a.X)+Math.Abs(b.Y-a.Y)<1e-7){document.Regenerate();var axis=(b-a).Normalize();var current=e.GetTransform().BasisY;var desired=new XYZ((double)row["normal"][0],(double)row["normal"][1],0);var angle=Math.Atan2(axis.DotProduct(current.CrossProduct(desired)),current.DotProduct(desired));var bend=e.get_Parameter(BuiltInParameter.STRUCTURAL_BEND_DIR_ANGLE);bend.Set(bend.AsDouble()+angle);}
  created.Add(e.Id.Value);
 }
 tx.Commit();}
document.Save();return new{created=created.Count,totalRequested=data.Count,warnings=document.GetWarnings().Select(w=>w.GetDescriptionText()).ToArray()};
}catch(Exception ex){return new{failure=ex.ToString()};}

