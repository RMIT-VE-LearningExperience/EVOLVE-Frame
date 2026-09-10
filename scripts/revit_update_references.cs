var manifest=System.Text.Json.JsonDocument.Parse(System.IO.File.ReadAllText(@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\reference_manifest.json"));
var views=new FilteredElementCollector(document).OfClass(typeof(View)).Cast<View>().Where(v=>v.Name.StartsWith("REF_")).ToDictionary(v=>v.Name);
var results=new List<object>();
using(var tx=new Transaction(document,"Leichhardt - verified PDF calibration")){
 tx.Start();
 foreach(var e in manifest.RootElement.EnumerateArray().Where(e=>e.GetProperty("controls").ValueKind!=System.Text.Json.JsonValueKind.Null)){
  var v=views[e.GetProperty("name").GetString()];
  var instance=new FilteredElementCollector(document,v.Id).OfClass(typeof(ImageInstance)).Cast<ImageInstance>().Single();
  instance.Pinned=false; instance.Width=e.GetProperty("width_mm").GetDouble()/304.8;
  instance.SetLocation(new XYZ(e.GetProperty("x_mm").GetDouble()/304.8,e.GetProperty("y_mm").GetDouble()/304.8,0),BoxPlacement.BottomLeft);instance.Pinned=true;
  var status=e.GetProperty("status").GetString();instance.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set(status);
  var text=new FilteredElementCollector(document,v.Id).OfClass(typeof(TextNote)).Cast<TextNote>().Single();text.Text=status;
  document.Regenerate();var box=instance.get_BoundingBox(v);text.Coord=new XYZ(box.Min.X,box.Max.Y+1200/304.8,0);
  results.Add(new {view=v.Name,width=instance.Width*304.8,status});
 }
 tx.Commit();
}
document.Save();return results;
