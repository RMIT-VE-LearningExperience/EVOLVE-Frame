using(var tx=new Transaction(document,"Leichhardt - garage junction and model display")){
 tx.Start();
 var wall=new FilteredElementCollector(document).OfClass(typeof(Wall)).Cast<Wall>().Single(w=>w.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()=="GF-GAR-P");
 ((LocationCurve)wall.Location).Curve=Line.CreateBound(new XYZ(6275/304.8,2760/304.8,-86/304.8),new XYZ(6275/304.8,8060/304.8,-86/304.8));
 var type=new FilteredElementCollector(document).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(t=>t.ViewFamily==ViewFamily.ThreeDimensional);
 var v=View3D.CreateIsometric(document,type.Id);v.Name="03 Building Geometry - Coordination WIP";v.DetailLevel=ViewDetailLevel.Fine;v.DisplayStyle=DisplayStyle.FlatColors;
 foreach(Category c in document.Settings.Categories){if((c.CategoryType==CategoryType.Annotation||c.Name=="Scope Boxes"||c.Name=="Reference Planes")&&v.CanCategoryBeHidden(c.Id))v.SetCategoryHidden(c.Id,true);}
 v.SetSectionBox(new BoundingBoxXYZ{Min=new XYZ(-1000/304.8,-1200/304.8,-3500/304.8),Max=new XYZ(30000/304.8,11000/304.8,10000/304.8)});v.IsSectionBoxActive=true;
 var forward=new XYZ(-1,1,-0.75).Normalize();var right=forward.CrossProduct(XYZ.BasisZ).Normalize();var up=right.CrossProduct(forward).Normalize();v.SetOrientation(new ViewOrientation3D(new XYZ(120, -65, 65),up,forward));
 tx.Commit();
}
document.Save();var ui=new Autodesk.Revit.UI.UIApplication(document.Application);var view=new FilteredElementCollector(document).OfClass(typeof(View3D)).Cast<View3D>().Single(v=>v.Name=="03 Building Geometry - Coordination WIP");ui.ActiveUIDocument.ActiveView=view;ui.ActiveUIDocument.RefreshActiveView();
return new{walls=new FilteredElementCollector(document).OfClass(typeof(Wall)).GetElementCount(),warnings=document.GetWarnings().Select(w=>w.GetDescriptionText()).ToArray()};
