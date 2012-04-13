from geoserver.catalog import Catalog as gsconfigCatalog
from ncgmp.config import GeoServerConfig
from featuretype import SqlFeatureTypeDef

class Catalog(gsconfigCatalog):
    def create_postgis_sql_layer(self, geomap, workspace, layerClass):
        definition = SqlFeatureTypeDef(geomap, workspace, layerClass)
        
        if self.get_layer(definition.name) is None:
            featureType_url = GeoServerConfig.BaseGeoserverUrl + "rest/workspaces/" + workspace.name + "/datastores/" + GeoServerConfig.DataStoreName + "/featuretypes/"
            headers = { "Content-Type": "application/json" }
            
            headers, response = self.http.request(featureType_url, "POST", definition.serialize(), headers)
            assert 200 <= headers.status < 300, "Tried to create Geoserver layer but encountered a " + str(headers.status) + " error: " + response
            self._cache.clear()
            
            return self.get_layer(definition.name)