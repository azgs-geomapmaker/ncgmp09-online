from django.db.models import get_model
from ncgmp.config import GeoServerConfig
from catalog import Catalog

class LayerGenerator:
    ncgmpModelNames = ["MapUnitPolys", "ContactsAndFaults"]
    gsmlpModelNames = [] # At this point, we're thinking there is only going to be one GeologicUnitView... 
    
    def __init__(self, geomap):
        self.ncgmpModelsToLoad = [ get_model("ncgmp", modelName) for modelName in self.ncgmpModelNames ]
        self.gsmlpModelsToLoad = [ get_model("ncgmp", modelName) for modelName in self.gsmlpModelNames ]     
        self.gm = geomap
        self.cat = Catalog(GeoServerConfig.BaseGeoserverUrl + "rest", GeoServerConfig.GeoserverAdminUser, GeoServerConfig.GeoserverAdminSecret)
        self.gsmlpWs = self.cat.get_workspace("gsmlp")
        self.ncgmpWs = self.cat.get_workspace("ncgmp")
        
    def createNewLayers(self):
        newLayers = []
        
        for model in self.ncgmpModelsToLoad:
            newLayers.append(self.cat.create_postgis_sql_layer(self.gm, self.ncgmpWs, model))
            
        for model in self.gsmlpModelsToLoad:
            newLayers.append(self.cat.create_postgis_sql_layer(self.gm, self.gsmlpWs, model))
            
        return newLayers