var f=document.Application.NewFamilyDocument(@"C:\ProgramData\Autodesk\RVT 2027\Family Templates\English\Metric Structural Framing - Beams and Braces.rft");var step="start";
try{
 using(var tx=new Transaction(f,"Parametric timber section")){
 tx.Start();var fm=f.FamilyManager;fm.NewType("90x35 MGP10");
 var b=fm.AddParameter("b",GroupTypeId.Geometry,SpecTypeId.Length,false);var h=fm.AddParameter("h",GroupTypeId.Geometry,SpecTypeId.Length,false);
 var hb=fm.AddParameter("Half Width",GroupTypeId.Constraints,SpecTypeId.Length,false);var hh=fm.AddParameter("Half Depth",GroupTypeId.Constraints,SpecTypeId.Length,false);
 fm.Set(b,200/304.8);fm.Set(h,300/304.8);fm.SetFormula(hb,"b / 2");fm.SetFormula(hh,"h / 2");
 var v=(View)f.GetElement(new ElementId(39L));
 Action<long,long,XYZ,XYZ,FamilyParameter> dim=(a,c,p,q,fp)=>{var ra=new ReferenceArray();ra.Append(((ReferencePlane)f.GetElement(new ElementId(a))).GetReference());ra.Append(((ReferencePlane)f.GetElement(new ElementId(c))).GetReference());f.FamilyCreate.NewLinearDimension(v,Line.CreateBound(p,q),ra).FamilyLabel=fp;};
 dim(1014,46,new XYZ(0,1,1),new XYZ(0,0,1),hb);dim(46,1029,new XYZ(0,0,1),new XYZ(0,-1,1),hb);
 dim(1056,47,new XYZ(0,1,1),new XYZ(0,1,0),hh);dim(47,1076,new XYZ(0,1,0),new XYZ(0,1,-1),hh);
 step="width";fm.Set(b,35/304.8);f.Regenerate();step="height";fm.Set(h,90/304.8);f.Regenerate();
 var mat=Material.Create(f,"LC Timber - MGP10");((Material)f.GetElement(mat)).Color=new Color(201,159,92);
 var ex=new FilteredElementCollector(f).OfClass(typeof(Extrusion)).Cast<Extrusion>().Single();
 step="material";var material=fm.Parameters.Cast<FamilyParameter>().Single(p=>p.Definition.Name=="Structural Material");fm.Set(material,mat);
 var sizes=new[]{new[]{90,45},new[]{140,45},new[]{190,45},new[]{240,45},new[]{300,45},new[]{90,90}};
 foreach(var s in sizes){fm.NewType(s[0]+"x"+s[1]+(s[0]>=240?" LVL13":" timber"));fm.Set(b,s[1]/304.8);fm.Set(h,s[0]/304.8);}
 tx.Commit();}
 var path=@"C:\Users\Stormtrooper\Git\EVOLVE - Frame\output\revit\families\LC Rectangular Timber.rfa";System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path));f.SaveAs(path,new SaveAsOptions{OverwriteExistingFile=true});var loaded=f.LoadFamily(document);return new{family=loaded.Name,types=loaded.GetFamilySymbolIds().Count};
}catch(Exception ex){return new{step,failure=ex.ToString()};}finally{f.Close(false);}

