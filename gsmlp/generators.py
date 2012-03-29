from django.db.models import get_model

class GeologicUnitViewGenerator:
    def __init__(self, geomap):
        self.gm = geomap
        
        MapUnitPolys = get_model("ncgmp", "MapUnitPolys")
        self.mapunitpolys = MapUnitPolys.objects.filter(owningmap=geomap)
        
    def createGeologicUnitView(self, mapunitpoly):
        dmu = mapunitpoly.mapunit
        ds = mapunitpoly.datasourceid
        
        kwargs = {
            "owningmap": self.gm,
            "identifier": mapunitpoly.mapunitpolys_id,
            "name": dmu.name,
            "description": dmu.description,
            "rank": dmu.hierarchykey,
            "lithology": dmu.generallithologyterm,
            "source": ds.source,
            "geologicUnitType_uri": "",
            "representativeLithology_uri": "",
            "representativeAge_uri": "",
            "representativeLowerAge_uri": "",
            "representativeUpperAge_uri": "",
            "specification_uri": "",
            "metadata_uri": "",
            "shape": mapunitpoly.shape
        }
        
        GeologicUnitView = get_model("ncgmp", "GeologicUnitView")
        newGeologicUnitView = GeologicUnitView(**kwargs)
        newGeologicUnitView.save()
        
    def buildGeologiUnitViews(self):
        for poly in self.mapunitpolys:
            self.createGeologicUnitView(poly)
    