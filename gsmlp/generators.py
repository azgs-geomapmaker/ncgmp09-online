from django.db.models import get_model
from django.db import transaction

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
            "geologicUnitType": "none",
            "rank": dmu.hierarchykey,
            "lithology": dmu.generallithologyterm,
            "geologicHistory": "none",
            "observationMethod": "none",
            "positionalAccuracy": "none",
            "source": ds.source,
            "geologicUnitType_uri": "none",
            "representativeLithology_uri": "none",
            "representativeAge_uri": "none",
            "representativeLowerAge_uri": "none",
            "representativeUpperAge_uri": "none",
            "specification_uri": "none",
            "metadata_uri": "none",
            "genericSymbolizer": "none",
            "shape": mapunitpoly.shape
        }
        
        GeologicUnitView = get_model("ncgmp", "GeologicUnitView")
        return GeologicUnitView(**kwargs)
    
    @transaction.commit_manually
    def buildGeologicUnitViews(self):
        for poly in self.mapunitpolys:
            self.createGeologicUnitView(poly).save()
        transaction.commit()   