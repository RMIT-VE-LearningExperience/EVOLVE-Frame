var manifest=System.Text.Json.JsonDocument.Parse(System.IO.File.ReadAllText(@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\reference_manifest.json"));
var names=new FilteredElementCollector(document).OfClass(typeof(View)).Cast<View>().Select(v=>v.Name).ToHashSet();
var entries=manifest.RootElement.EnumerateArray().Where(e=>!names.Contains(e.GetProperty("name").GetString())).Take(3).ToArray();
var type=new FilteredElementCollector(document).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x=>x.ViewFamily==ViewFamily.Drafting);
var textType=new FilteredElementCollector(document).OfClass(typeof(TextNoteType)).FirstElementId();
var results=new List<object>();
foreach(var e in entries){
 using(var tx=new Transaction(document,"Leichhardt - link "+e.GetProperty("name").GetString())) {
  tx.Start();
  var v=ViewDrafting.Create(document,type.Id); v.Name=e.GetProperty("name").GetString(); v.Scale=e.GetProperty("scale").GetInt32();
  using(var options=new ImageTypeOptions(e.GetProperty("file").GetString(),false,ImageTypeSource.Link)){
   options.PageNumber=e.GetProperty("page").GetInt32(); options.Resolution=150;
   var imageType=ImageType.Create(document,options);
   var instance=ImageInstance.Create(document,v,imageType.Id,new ImagePlacementOptions(XYZ.Zero,BoxPlacement.BottomLeft));
   instance.LockProportions=true; instance.Width=e.GetProperty("width_mm").GetDouble()/304.8;
   instance.SetLocation(new XYZ(e.GetProperty("x_mm").GetDouble()/304.8,e.GetProperty("y_mm").GetDouble()/304.8,0),BoxPlacement.BottomLeft);
   instance.Pinned=true;
   var status=e.GetProperty("status").GetString();
   instance.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set(status);
   document.Regenerate();
   var box=instance.get_BoundingBox(v);
   TextNote.Create(document,v.Id,new XYZ(box.Min.X,box.Max.Y+1200/304.8,0),status,textType);
   results.Add(new {view=v.Name,id=v.Id.Value,imageId=instance.Id.Value,pinned=instance.Pinned,width_mm=instance.Width*304.8,height_mm=instance.Height*304.8,min_mm=new[]{box.Min.X*304.8,box.Min.Y*304.8},status});
  }
  tx.Commit();
 }
}
document.Save();
return new {created=results,remaining=manifest.RootElement.GetArrayLength()-names.Count(n=>n.StartsWith("REF_"))-results.Count};
