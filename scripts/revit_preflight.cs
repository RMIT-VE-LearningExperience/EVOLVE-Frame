var doc = document;
var mm = UnitTypeId.Millimeters;
Func<XYZ, object> point = p => new { x_mm = UnitUtils.ConvertFromInternalUnits(p.X, mm), y_mm = UnitUtils.ConvertFromInternalUnits(p.Y, mm), z_mm = UnitUtils.ConvertFromInternalUnits(p.Z, mm) };
return new {
  title = doc.Title, path = doc.PathName, version = doc.Application.VersionNumber, build = doc.Application.VersionBuild,
  workshared = doc.IsWorkshared, isModifiable = doc.IsModifiable,
  lengthUnits = doc.GetUnits().GetFormatOptions(SpecTypeId.Length).GetUnitTypeId().TypeId,
  levels = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().Select(l => new { id=l.Id.Value, name=l.Name, elevation_mm=UnitUtils.ConvertFromInternalUnits(l.Elevation,mm) }).ToArray(),
  grids = new FilteredElementCollector(doc).OfClass(typeof(Grid)).Cast<Grid>().Select(g => new {id=g.Id.Value,name=g.Name}).ToArray(),
  phases = doc.Phases.Cast<Phase>().Select(p=>new {id=p.Id.Value,name=p.Name}).ToArray(),
  projectBasePoint = point(BasePoint.GetProjectBasePoint(doc).Position), surveyPoint = point(BasePoint.GetSurveyPoint(doc).Position),
  activeSite = doc.ActiveProjectLocation.Name,
  northAngle = doc.ActiveProjectLocation.GetProjectPosition(XYZ.Zero).Angle,
  warnings = doc.GetWarnings().Select(w=>w.GetDescriptionText()).ToArray(),
  wallCount = new FilteredElementCollector(doc).OfClass(typeof(Wall)).GetElementCount(),
  floorCount = new FilteredElementCollector(doc).OfClass(typeof(Floor)).GetElementCount(),
  roofCount = new FilteredElementCollector(doc).OfClass(typeof(RoofBase)).GetElementCount()
};
