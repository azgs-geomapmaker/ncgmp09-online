from django.db.models import get_model
from django.db import transaction

class GeologicUnitViewGenerator:
    GeologicUnitView = get_model("ncgmp", "GeologicUnitView")
    
    def __init__(self, geomap):
        self.gm = geomap
        
        MapUnitPolys = get_model("ncgmp", "MapUnitPolys")
        self.mapunitpolys = MapUnitPolys.objects.filter(owningmap=geomap)
        
    def createGeologicUnitView(self, mapunitpoly):
        dmu = mapunitpoly.mapunit
        repValue = dmu.representativeValue()
        ds = mapunitpoly.datasourceid
        
        kwargs = {
            "owningmap": self.gm,
            "identifier": mapunitpoly.mapunitpolys_id,
            "name": dmu.name,
            "description": dmu.description,
            "geologicUnitType": "missing",
            "rank": dmu.hierarchykey,
            "lithology": dmu.generallithologyterm,
            "geologicHistory": dmu.age,
            "observationMethod": self.gm.map_type,
            "positionalAccuracy": "missing",
            "source": ds.source,
            "geologicUnitType_uri": "http://resource.geosciml.org/classifier/cgi/geologicunittype/geologic_unit",
            "representativeLithology_uri": repvalue.representativelithology_uri, 
            "representativeAge_uri": repvalue.representativeage_uri,
            "representativeOlderAge_uri": repvalue.representativeolderage_uri,     
            "representativeYoungerAge_uri": repvalue.representativeyoungerage_uri,
            "specification_uri": "/ncgmp/gm/" + str(gm.id) + "/dmu/" + str(dmu.id) + "/",                    
            "metadata_uri": self.gm.metadata_url,
            "genericSymbolizer": dmu.mapunit,
            "shape": mapunitpoly.shape
        }
                    
        return self.GeologicUnitView(**kwargs)
    
    def buildGeologicUnitViews(self):
        newFeatures = [ self.createGeologicUnitView(poly) for poly in self.mapunitpolys ]
        self.GeologicUnitView.objects.bulk_create(newFeatures)  