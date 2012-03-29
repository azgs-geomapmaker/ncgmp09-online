from django.db.models import get_model
from ncgmp.config import GeoServerConfig
from catalog import Catalog

class LayerGenerator:
    modelNames = [ "MapUnitPolys", "ContactsAndFaults" ]
    
    def __init__(self, geomap):
        self.modelsToLoad = [ get_model("ncgmp", modelName) for modelName in self.modelNames ]          
        self.gm = geomap
        self.cat = Catalog(GeoServerConfig.BaseGeoserverUrl + "rest", GeoServerConfig.GeoserverAdminUser, GeoServerConfig.GeoserverAdminSecret)
        
    def createNewLayers(self):
        newLayers = []
        
        for model in self.modelsToLoad:
            newLayers.append(self.cat.create_postgis_sql_layer(self.gm, model))
            
        return newLayers