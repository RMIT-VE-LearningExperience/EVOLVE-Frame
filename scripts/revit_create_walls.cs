var data=System.Text.Json.JsonDocument.Parse(System.IO.File.ReadAllText(@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\build_manifest.json"));
if(new FilteredElementCollector(document).OfClass(typeof(Wall)).GetElementCount()!=0)throw new Exception("Walls already exist; inspect before rebuilding");
var levels=new FilteredElementCollector(document).OfClass(typeof(Level)).Cast<Level>().ToList();
var ground=levels.Single(l=>l.Name.StartsWith("00 Ground FFL"));var first=levels.Single(l=>l.Name.StartsWith("01 First FFL"));
Func<double,double> ft=x=>x/304.8;
var created=new List<object>();
using(var tx=new Transaction(document,"Leichhardt - dimensioned architectural walls and openings")){
 tx.Start();
 var types=new Dictionary<int,WallType>();
 var baseType=new FilteredElementCollector(document).OfClass(typeof(WallType)).Cast<WallType>().First(t=>t.Name=="Generic - 200mm");
 foreach(var width in new[]{90,190,230,240}){
  var t=(WallType)baseType.Duplicate("LC - "+width+"mm "+(width==90?"Partition":"Enclosure")+" - coordination envelope");
  var mat=Material.Create(document,"LC "+width+"mm enclosure");var m=(Material)document.GetElement(mat);m.Color=width==190?new Color(225,224,215):width==90?new Color(214,202,175):new Color(170,121,94);
  t.SetCompoundStructure(CompoundStructure.CreateSimpleCompoundStructure(new List<CompoundStructureLayer>{new CompoundStructureLayer(ft(width),MaterialFunctionAssignment.Structure,mat)}));
  t.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_COMMENTS)?.Set("Dimensioned wall envelope. Detailed timber model is separate; cavity and finish layer breakdown not asserted.");types[width]=t;
 }
 foreach(var e in data.RootElement.GetProperty("walls").EnumerateArray()){
  var mark=e.GetProperty("mark").GetString();var a=e.GetProperty("a");var b=e.GetProperty("b");double z=e.GetProperty("z").GetDouble();
  var level=z>3000?first:ground;
  var p=new XYZ(ft(a[0].GetDouble()),ft(a[1].GetDouble()),level.Elevation);var q=new XYZ(ft(b[0].GetDouble()),ft(b[1].GetDouble()),level.Elevation);
  var wall=Wall.Create(document,Line.CreateBound(p,q),types[e.GetProperty("width").GetInt32()].Id,level.Id,ft(e.GetProperty("height").GetDouble()),ft(z)-level.Elevation,false,false);
  wall.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(mark);wall.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(e.GetProperty("source").GetString()+". Coordination WIP; see discrepancy log.");
  document.Regenerate();var ids=new List<long>();bool horizontal=Math.Abs(p.Y-q.Y)<1e-6;
  foreach(var o in e.GetProperty("openings").EnumerateArray()){
   double c=o.GetProperty("centre").GetDouble(),w=o.GetProperty("width").GetDouble(),lo=z+o.GetProperty("sill").GetDouble(),hi=lo+o.GetProperty("height").GetDouble();
   var op=document.Create.NewOpening(wall,horizontal?new XYZ(ft(c-w/2),p.Y,ft(lo)):new XYZ(p.X,ft(c-w/2),ft(lo)),horizontal?new XYZ(ft(c+w/2),p.Y,ft(hi)):new XYZ(p.X,ft(c+w/2),ft(hi)));
   op.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.Set(o.GetProperty("mark").GetString());op.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set("A07/A08 calibrated jamb centre; A11 nominal opening size. Frame/leaf detailing to follow; rough-opening allowances not asserted.");ids.Add(op.Id.Value);
  }
  created.Add(new{mark,id=wall.Id.Value,openings=ids});
 }
 tx.Commit();
}
document.Save();
var ui=new Autodesk.Revit.UI.UIApplication(document.Application);var view=new FilteredElementCollector(document).OfClass(typeof(View3D)).Cast<View3D>().First(v=>!v.IsTemplate&&!v.IsPerspective);ui.ActiveUIDocument.ActiveView=view;ui.ActiveUIDocument.Selection.SetElementIds(new List<ElementId>());ui.ActiveUIDocument.RefreshActiveView();ui.ActiveUIDocument.GetOpenUIViews().First(v=>v.ViewId==view.Id).ZoomToFit();
return new{walls=created,warnings=document.GetWarnings().Select(w=>w.GetDescriptionText()).ToArray()};
