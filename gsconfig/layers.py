from django.db.models import get_model
from ncgmp.config import GeoServerConfig
from catalog import Catalog

class LayerGenerator:
    gsmlpModelNames = ["GeologicUnitView"]
    
    def __init__(self, geomap):
        self.gsmlpModelsToLoad = [ get_model("ncgmp", modelName) for modelName in self.gsmlpModelNames ]     
        self.gm = geomap
        self.cat = Catalog(GeoServerConfig.BaseGeoserverUrl + "rest", GeoServerConfig.GeoserverAdminUser, GeoServerConfig.GeoserverAdminSecret)
        self.gsmlpWs = self.cat.get_workspace("gsmlp")
        if self.gsmlpWs is None: self.cat.create_workspace("gsmlp", "http://xmlns.geosciml.org/geosciml-portrayal/1.0")
        
    def createNewLayers(self):
        newLayers = []
            
        for model in self.gsmlpModelsToLoad:
            newLayers.append(self.cat.create_postgis_sql_layer(self.gm, self.gsmlpWs, model))
            
        return newLayers