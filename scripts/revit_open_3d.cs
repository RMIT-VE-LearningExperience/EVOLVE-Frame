var ui=new Autodesk.Revit.UI.UIApplication(document.Application);
var views=new FilteredElementCollector(document).OfClass(typeof(View3D)).Cast<View3D>().Where(v=>!v.IsTemplate&&!v.IsPerspective).ToList();
var view=views.FirstOrDefault(v=>v.Name=="{3D}")??views.FirstOrDefault();
if(view==null){
 using(var tx=new Transaction(document,"Open coordination 3D view")){
  tx.Start();
  var type=new FilteredElementCollector(document).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(t=>t.ViewFamily==ViewFamily.ThreeDimensional);
  view=View3D.CreateIsometric(document,type.Id);view.Name="00 Coordination - 3D";
  tx.Commit();
 }
}
ui.ActiveUIDocument.ActiveView=view;
ui.ActiveUIDocument.RefreshActiveView();
var uv=ui.ActiveUIDocument.GetOpenUIViews().FirstOrDefault(v=>v.ViewId==view.Id);
uv?.ZoomToFit();
return new{document=document.Title,activeView=ui.ActiveUIDocument.ActiveView.Name,type=ui.ActiveUIDocument.ActiveView.ViewType.ToString(),walls=new FilteredElementCollector(document).OfClass(typeof(Wall)).GetElementCount()};
