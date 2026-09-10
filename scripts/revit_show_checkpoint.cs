var ui=new Autodesk.Revit.UI.UIApplication(document.Application);
var view=new FilteredElementCollector(document).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().Single(v=>v.Name=="02 Proposed - Ground Coordination");
ui.ActiveUIDocument.ActiveView=view;
ui.ActiveUIDocument.RefreshActiveView();
var uv=ui.ActiveUIDocument.GetOpenUIViews().First(v=>v.ViewId==view.Id);
uv.ZoomAndCenterRectangle(new XYZ(-7000/304.8,-7500/304.8,0),new XYZ(34000/304.8,17000/304.8,0));
return uv.GetZoomCorners().Select(p=>new{x=p.X*304.8,y=p.Y*304.8}).ToArray();
