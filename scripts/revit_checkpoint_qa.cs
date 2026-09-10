var ui=new Autodesk.Revit.UI.UIApplication(document.Application);
var views=new FilteredElementCollector(document).OfClass(typeof(View)).Cast<View>().ToList();
var ground=views.Single(v=>v.Name=="02 Proposed - Ground Coordination");
var first=views.Single(v=>v.Name=="02 Proposed - First Coordination");
using(var tx=new Transaction(document,"Leichhardt - reference checkpoint status")){
 tx.Start();
 foreach(var v in new[]{ground,first}){
  var image=new FilteredElementCollector(document,v.Id).OfClass(typeof(ImageInstance)).Cast<ImageInstance>().Single();
  image.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set("Calibrated "+(v.Id==ground.Id?"A07":"A08")+" underlay. Local drawing coordinates; view reference only.");
 }
 var statusView=views.Single(v=>v.Name=="00 Coordination - Model Status");
 var note=new FilteredElementCollector(document,statusView.Id).OfClass(typeof(TextNote)).Cast<TextNote>().Single();
 note.Text="LEICHHARDT - REFERENCE CHECKPOINT 01\nScope: proposed architecture, primary structure, detailed timber and truss members.\nFive architectural reference levels, seven external-face coordination control grids, sixteen linked source views.\nA03/A06/A07/A08/A12 and supplier layouts calibrated in two directions. Five structural underlays registered to architectural dimensions.\nLocal origin: west garage external/boundary X=0; main GF south external face Y=0; GF FFL Z=0 = drawing RL10.906.\nTrue north checked against A03 05deg24min40sec bearing and north arrow. Shared XY are local, not georeferenced. Default template map location is not verified.\nD01: floor zone400 (A12), joists300 or equivalent (S10), joists413/360 +19 flooring +10 ceiling (supplier).\nD02: porch RL10.734 implies172mm step, but A06/A07 label226mm.\nD03: engineer bracingN1 vs supplierN2. Engineering S09/S11 explicitly require supplier-truss validation.\nD04: W14/W15/W17/W19 plan2300 width vs schedule2230.\nDetailed logs and calibration evidence: output/revit.\nNo building geometry has been created at this reference checkpoint. NOT A COMPLETED CONSTRUCTION MODEL.";
 tx.Commit();
}
ui.ActiveUIDocument.ActiveView=ground;
ui.ActiveUIDocument.RefreshActiveView();
var open=ui.ActiveUIDocument.GetOpenUIViews().First(v=>v.ViewId==ground.Id);
open.ZoomAndCenterRectangle(new XYZ(-2000/304.8,-2500/304.8,0),new XYZ(30500/304.8,11500/304.8,0));
var images=new FilteredElementCollector(document).OfClass(typeof(ImageInstance)).Cast<ImageInstance>().ToList();
var export=new ImageExportOptions{ExportRange=ExportRange.SetOfViews,FilePath=@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\checkpoint",HLRandWFViewsFileType=ImageFileType.PNG,ShadowViewsFileType=ImageFileType.PNG,ZoomType=ZoomFitType.FitToPage,PixelSize=2600,ImageResolution=ImageResolution.DPI_150};
export.SetViewsAndSheets(new List<ElementId>{ground.Id,first.Id});document.ExportImage(export);
document.Save();
return new{path=document.PathName,view=ground.Name,levels=new FilteredElementCollector(document).OfClass(typeof(Level)).GetElementCount(),grids=new FilteredElementCollector(document).OfClass(typeof(Grid)).GetElementCount(),referenceViews=views.Count(v=>v.Name.StartsWith("REF_")),images=images.Count,allImagesPinned=images.All(i=>i.Pinned),walls=new FilteredElementCollector(document).OfClass(typeof(Wall)).GetElementCount(),warnings=document.GetWarnings().Select(w=>w.GetDescriptionText()).ToArray(),exports=System.IO.Directory.GetFiles(@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit","checkpoint*.png")};
