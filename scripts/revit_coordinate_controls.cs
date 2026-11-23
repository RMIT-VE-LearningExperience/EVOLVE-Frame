var mm=UnitTypeId.Millimeters;
Func<double,double> ft=x=>UnitUtils.ConvertToInternalUnits(x,mm);
var results=new List<object>();
using(var tx=new Transaction(document,"Leichhardt - local drawing coordinates and control grids")){
 tx.Start();
 var loc=document.ActiveProjectLocation.Duplicate("A03 Local Site Grid - Drawing RL - XY not georeferenced");
 document.ActiveProjectLocation=loc;
 double bearing=(5+24.0/60+40.0/3600)*Math.PI/180;
 double desiredEast=-Math.Sin(bearing),desiredNorth=-Math.Cos(bearing);
 bool verified=false;
 foreach(var angle in new[]{Math.PI/2+bearing,-Math.PI/2-bearing}){
  loc.SetProjectPosition(XYZ.Zero,new ProjectPosition(0,0,ft(10906),angle));
  var a=loc.GetProjectPosition(XYZ.Zero);var b=loc.GetProjectPosition(XYZ.BasisX);
  if(Math.Abs(b.EastWest-a.EastWest-desiredEast)<1e-8 && Math.Abs(b.NorthSouth-a.NorthSouth-desiredNorth)<1e-8){verified=true;break;}
 }
 if(!verified)throw new Exception("True north transform did not match A03 bearing and north arrow");
 if(new FilteredElementCollector(document).OfClass(typeof(Grid)).GetElementCount()!=0)throw new Exception("Existing grids require review");
 var xs=new[]{("CX0",0.0),("CX1",6130.0),("CX2",26990.0),("CX3",28430.0)};
 var ys=new[]{("CY0",0.0),("CY1",8180.0),("CY2",9500.0)};
 foreach(var def in xs){var g=Grid.Create(document,Line.CreateBound(new XYZ(ft(def.Item2),ft(-1500),0),new XYZ(ft(def.Item2),ft(11000),0)));g.Name=def.Item1;g.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set("Coordination control only, A06/A07 external face dimension; not an engineer-issued structural grid.");g.Pinned=true;}
 foreach(var def in ys){var g=Grid.Create(document,Line.CreateBound(new XYZ(ft(-1500),ft(def.Item2),0),new XYZ(ft(30000),ft(def.Item2),0)));g.Name=def.Item1;g.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set("Coordination control only, A06/A07 external face dimension; not an engineer-issued structural grid.");g.Pinned=true;}
 var views=new FilteredElementCollector(document).OfClass(typeof(View)).Cast<View>().ToDictionary(v=>v.Id.Value);
 foreach(var pair in new[]{("REF_A07_Floor_1","02 Proposed - Ground Coordination"),("REF_A08_Floor_2","02 Proposed - First Coordination")}){
  var source=views.Values.Single(v=>v.Name==pair.Item1);var target=views.Values.Single(v=>v.Name==pair.Item2);
  var image=new FilteredElementCollector(document,source.Id).OfClass(typeof(ImageInstance)).Cast<ImageInstance>().Single();
  var box=image.get_BoundingBox(source);
  var underlay=ImageInstance.Create(document,target,image.GetTypeId(),new ImagePlacementOptions(new XYZ(box.Min.X,box.Min.Y,0),BoxPlacement.BottomLeft));
  underlay.LockProportions=true;underlay.Width=image.Width;underlay.SetLocation(new XYZ(box.Min.X,box.Min.Y,0),BoxPlacement.BottomLeft);underlay.Pinned=true;
  underlay.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set("Calibrated A06/A07 local drawing grid. Reference underlay; remove/hide from production sheets.");
  var bb=new BoundingBoxXYZ();bb.Min=new XYZ(ft(-2500),ft(-2500),ft(-1000));bb.Max=new XYZ(ft(31000),ft(12000),ft(10000));target.CropBox=bb;target.CropBoxActive=true;target.CropBoxVisible=false;
  results.Add(new {view=target.Name,image=underlay.Id.Value});
 }
 tx.Commit();
}
document.Save();
var ui=new Autodesk.Revit.UI.UIApplication(document.Application);var view=new FilteredElementCollector(document).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().Single(v=>v.Name=="02 Proposed - Ground Coordination");
ui.ActiveUIDocument.ActiveView=view;
ui.ActiveUIDocument.GetOpenUIViews().First(v=>v.ViewId==view.Id).ZoomAndCenterRectangle(new XYZ(ft(-2000),ft(-2500),0),new XYZ(ft(30500),ft(11500),0));
var position=document.ActiveProjectLocation.GetProjectPosition(XYZ.Zero);
return new{references=results,angleDegrees=position.Angle*180/Math.PI,drawingRL_mm=position.Elevation*304.8,site=document.ActiveProjectLocation.Name,grids=7};
