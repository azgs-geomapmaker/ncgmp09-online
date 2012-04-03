from django.db.models import get_model
from django.db import transaction

class GeologicUnitViewGenerator:
    def __init__(self, geomap):
        self.gm = geomap
        
        MapUnitPolys = get_model("ncgmp", "MapUnitPolys")
        self.mapunitpolys = MapUnitPolys.objects.filter(owningmap=geomap)
        
    def createGeologicUnitView(self, mapunitpoly):
        dmu = mapunitpoly.mapunit
        repValues = dmu.representativevalue_set.all()
        ds = mapunitpoly.datasourceid
        
        kwargs = {
            "owningmap": self.gm,
            "identifier": mapunitpoly.mapunitpolys_id,
            "name": dmu.name,
            "description": dmu.description,
            "geologicUnitType": "missing",
            "rank": dmu.hierarchykey,
            "lithology": dmu.generallithologyterm,
            "geologicHistory": dmu.age,                      # OR compile from geologicevents
            "observationMethod": self.gm.map_type,
            "positionalAccuracy": "missing",
            "source": ds.source,
            "geologicUnitType_uri": "http://resource.geosciml.org/classifier/cgi/geologicunittype/geologic_unit",
            "representativeLithology_uri": "none",            
            "representativeAge_uri": "none",
            "representativeLowerAge_uri": "none",           # From a related GeologicEvent. Can there be more than one?
            "representativeUpperAge_uri": "none",           # From a related GeologicEvent. Can there be more than one?
            "specification_uri": "none",                    # What should this be?
            "metadata_uri": self.gm.metadata_url,           
            "genericSymbolizer": dmu.mapunit,
            "shape": mapunitpoly.shape
        }
        
        if len(repValues) > 0: 
            kwargs["representativeLithology_uri"] = repvalues[0].representativelithology_uri
            kwargs["representativeAge_uri"] = repvalues[0].representativeage_uri
        
        GeologicUnitView = get_model("ncgmp", "GeologicUnitView")
        return GeologicUnitView(**kwargs)
    
    @transaction.commit_manually
    def buildGeologicUnitViews(self):
        for poly in self.mapunitpolys:
            self.createGeologicUnitView(poly).save()
        transaction.commit()   