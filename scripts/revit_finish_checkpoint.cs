var ui=new Autodesk.Revit.UI.UIApplication(document.Application);
var views=new FilteredElementCollector(document).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().Where(v=>v.Name.StartsWith("02 Proposed - ")).ToList();
using(var tx=new Transaction(document,"Leichhardt - full reference sheet previews")){
 tx.Start();
 foreach(var v in views){
  var image=new FilteredElementCollector(document,v.Id).OfClass(typeof(ImageInstance)).Cast<ImageInstance>().Single();var b=image.get_BoundingBox(v);
  var box=new BoundingBoxXYZ{Min=new XYZ(b.Min.X-500/304.8,b.Min.Y-500/304.8,-10),Max=new XYZ(b.Max.X+500/304.8,b.Max.Y+500/304.8,40)};
  v.CropBox=box;
 }
 tx.Commit();
}
var export=new ImageExportOptions{ExportRange=ExportRange.SetOfViews,FilePath=@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\checkpoint",HLRandWFViewsFileType=ImageFileType.PNG,ShadowViewsFileType=ImageFileType.PNG,ZoomType=ZoomFitType.FitToPage,PixelSize=2600,ImageResolution=ImageResolution.DPI_150};
export.SetViewsAndSheets(views.Select(v=>v.Id).ToList());document.ExportImage(export);document.Save();
return new{saved=document.PathName,warnings=document.GetWarnings().Count,view=ui.ActiveUIDocument.ActiveView.Name};
