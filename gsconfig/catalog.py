from geoserver.catalog import FailedRequestError, Catalog as gsconfigCatalog
from ncgmp.config import GeoServerConfig
from featuretype import SqlFeatureTypeDef
from datastore import PostGISDatastoreDef

class Catalog(gsconfigCatalog):
    def create_postgis_sql_layer(self, geomap, workspace, layerClass):
        definition = SqlFeatureTypeDef(geomap, workspace, layerClass)
        
        if self.get_layer(definition.name) is None:
            featureType_url = GeoServerConfig.BaseGeoserverUrl + "rest/workspaces/" + workspace.name + "/datastores/django/featuretypes/"
            headers = { "Content-Type": "application/json" }
            
            headers, response = self.http.request(featureType_url, "POST", definition.serialize(), headers)
            assert 200 <= headers.status < 300, "Tried to create Geoserver layer but encountered a " + str(headers.status) + " error: " + response
            self._cache.clear()
            
            return self.get_layer(definition.name)
        
    def create_postgis_datastore(self, workspace):
        definition = PostGISDatastoreDef(workspace)
        
        try:
            self.get_store("django", workspace)
        except FailedRequestError:
            store_url = GeoServerConfig.BaseGeoserverUrl + "rest/workspaces/" + workspace.name + "/datastores/"
            headers = { "Content-Type": "application/json" }
            
            headers, response = self.http.request(store_url, "POST", definition.serialize(), headers)
            assert 200 <= headers.status < 300, "Tried to create Geoserver datastore but encountered a " + str(headers.status) + " error: " + response
            self._cache.clear()
            
            return self.get_store("django")