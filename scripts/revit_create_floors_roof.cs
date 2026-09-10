try {
if(new FilteredElementCollector(document).OfClass(typeof(Floor)).GetElementCount()!=0)throw new Exception("Existing floors require review");
var ground=new FilteredElementCollector(document).OfClass(typeof(Level)).Cast<Level>().Single(l=>l.Name.StartsWith("00 Ground FFL"));
var results=new List<object>();
Func<double,ElementId,CompoundStructure> structure=(d,m)=>{var c=CompoundStructure.CreateSimpleCompoundStructure(new List<CompoundStructureLayer>{new CompoundStructureLayer(d/304.8,MaterialFunctionAssignment.Structure,m)});c.EndCap=EndCapCondition.NoEndCap;return c;};
using(var tx=new Transaction(document,"Leichhardt - slab surfaces, floor opening and roof")){
 tx.Start();
 var partition=new FilteredElementCollector(document).OfClass(typeof(Wall)).Cast<Wall>().Single(w=>w.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString()=="GF-GAR-P");
 WallUtils.DisallowWallJoinAtEnd(partition,1);((LocationCurve)partition.Location).Curve=Line.CreateBound(new XYZ(6275/304.8,2760/304.8,0),new XYZ(6275/304.8,7940/304.8,0));
 var baseFloor=new FilteredElementCollector(document).OfClass(typeof(FloorType)).Cast<FloorType>().First(t=>t.Name=="Concrete 100mm");
 var concrete=Material.Create(document,"LC Concrete - S04 slab");((Material)document.GetElement(concrete)).Color=new Color(158,158,154);
 var wood=Material.Create(document,"LC Particleboard - 19mm");((Material)document.GetElement(wood)).Color=new Color(184,151,98);
 var slabType=(FloorType)baseFloor.Duplicate("LC S04 - 125mm concrete slab");slabType.SetCompoundStructure(structure(125,concrete));
 var deckType=(FloorType)baseFloor.Duplicate("LC Supplier - 19mm particleboard deck");deckType.SetCompoundStructure(structure(19,wood));
 Func<double[][],CurveLoop> loop=pts=>{var l=new CurveLoop();for(int i=0;i<pts.Length;i++){var a=pts[i];var b=pts[(i+1)%pts.Length];l.Append(Line.CreateBound(new XYZ(a[0]/304.8,a[1]/304.8,0),new XYZ(b[0]/304.8,b[1]/304.8,0)));}return l;};
 Action<string,double[][],double,bool,double[][]> floor=(name,pts,z,deck,hole)=>{var loops=new List<CurveLoop>{loop(pts)};if(hole!=null)loops.Add(loop(hole));var f=Floor.Create(document,loops,deck?deckType.Id:slabType.Id,ground.Id);f.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).Set(z/304.8);f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(name);f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(deck?"Supplier p47 19mm; A08 stair/void cutout; architectural FFL retained D01. Joists separate.":"A06 footprint; S04 125mm slab surface. Beams/piers modelled separately. Porch uses written RL D02.");results.Add(new{name,id=f.Id.Value});};
 floor("SLAB-GF",new[]{new[]{6230.0,2520},new[]{8510.0,2520},new[]{8510.0,3620},new[]{12480.0,3620},new[]{12480.0,0},new[]{26990.0,0},new[]{26990.0,8180},new[]{6230.0,8180}},0,false,null);
 floor("SLAB-GARAGE",new[]{new[]{0.0,2520},new[]{6230.0,2520},new[]{6230.0,8180},new[]{6470.0,8180},new[]{6470.0,9500},new[]{0.0,9500}},-86,false,null);
 floor("SLAB-ALFRESCO",new[]{new[]{6130.0,0},new[]{12480.0,0},new[]{12480.0,3620},new[]{8510.0,3620},new[]{8510.0,2520},new[]{6130.0,2520}},-86,false,null);
 floor("SLAB-PORCH-D02",new[]{new[]{26990.0,4500},new[]{28430.0,4500},new[]{28430.0,8180},new[]{26990.0,8180}},-172,false,null);
 floor("FF-DECK",new[]{new[]{6230.0,150},new[]{26840.0,150},new[]{26840.0,8030},new[]{6230.0,8030}},3140,true,new[]{new[]{20750.0,6840},new[]{24200.0,6840},new[]{24200.0,4830},new[]{26750.0,4830},new[]{26750.0,7940},new[]{20750.0,7940}});
 var baseRoof=new FilteredElementCollector(document).OfClass(typeof(RoofType)).Cast<RoofType>().First(t=>t.Name=="Generic - 225mm");var roofType=(RoofType)baseRoof.Duplicate("LC Metal roof - 25mm coordination skin");var metal=Material.Create(document,"LC Roof - Charcoal");((Material)document.GetElement(metal)).Color=new Color(65,73,78);roofType.SetCompoundStructure(structure(25,metal));
 var points=new[]{new[]{5680.0,-400},new[]{27390.0,-400},new[]{27390.0,8580},new[]{5680.0,8580}};
 var ca=new CurveArray();foreach(var c in loop(points))ca.Append(c);ModelCurveArray mapping=new ModelCurveArray();document.Regenerate();
 var roof=document.Create.NewFootPrintRoof(ca,ground,roofType,out mapping);foreach(ModelCurve c in mapping){roof.set_DefinesSlope(c,true);roof.set_SlopeAngle(c,Math.Tan(25*Math.PI/180));}
 roof.get_Parameter(BuiltInParameter.ROOF_LEVEL_OFFSET_PARAM).Set((5740+106-550*Math.Tan(25*Math.PI/180))/304.8);
 roof.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("ROOF-MAIN");roof.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("A03/A12 25deg hip; supplier7880 span,550 overhang, T1 heel106. 25mm skin is coordination thickness; battens/finish build-up pending. Architectural ceiling retained.");
 results.Add(new{name="ROOF-MAIN",id=roof.Id.Value});
 tx.Commit();
}
document.Save();return new{elements=results,warnings=document.GetWarnings().Select(w=>w.GetDescriptionText()).ToArray()};
}catch(Exception ex){return new{failure=ex.ToString()};}
