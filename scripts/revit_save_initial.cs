if (document.Title != "Project1") throw new Exception("Expected the inspected Project1 model");
if (new FilteredElementCollector(document).OfClass(typeof(Wall)).GetElementCount()!=0) throw new Exception("Model changed since preflight");
var target=@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\Leichhardt_Coordination_Model.rvt";
if (System.IO.File.Exists(target)) throw new Exception("Coordination file already exists; inspect before replacing");
document.SaveAs(target,new SaveAsOptions {OverwriteExistingFile=false,MaximumBackups=5});
return new {saved=document.PathName};
