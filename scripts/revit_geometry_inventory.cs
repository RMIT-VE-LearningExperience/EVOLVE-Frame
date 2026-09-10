return new{
 title=document.Title,
 walls=new FilteredElementCollector(document).OfClass(typeof(Wall)).GetElementCount(),
 wallTypes=new FilteredElementCollector(document).OfClass(typeof(WallType)).Cast<WallType>().Where(t=>t.Kind==WallKind.Basic).Select(t=>new{id=t.Id.Value,name=t.Name,width=t.Width*304.8}).ToArray(),
 floorTypes=new FilteredElementCollector(document).OfClass(typeof(FloorType)).Cast<FloorType>().Select(t=>new{id=t.Id.Value,name=t.Name}).ToArray(),
 roofTypes=new FilteredElementCollector(document).OfClass(typeof(RoofType)).Cast<RoofType>().Select(t=>new{id=t.Id.Value,name=t.Name}).ToArray(),
 framing=new FilteredElementCollector(document).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(t=>t.Category!=null&&(t.Category.Id.Value==(long)BuiltInCategory.OST_StructuralFraming||t.Category.Id.Value==(long)BuiltInCategory.OST_StructuralColumns)).Select(t=>new{id=t.Id.Value,family=t.FamilyName,name=t.Name,parameters=t.Parameters.Cast<Parameter>().Select(p=>new{name=p.Definition.Name,type=p.StorageType.ToString(),value=p.AsValueString()}).ToArray()}).ToArray()
};
