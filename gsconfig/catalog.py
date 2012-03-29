from geoserver.catalog import Catalog as gsconfigCatalog
from ncgmp.config import GeoServerConfig
from featuretype import SqlFeatureTypeDef

class Catalog(gsconfigCatalog):
    def create_postgis_sql_layer(self, geomap, layerClass):
        definition = SqlFeatureTypeDef(geomap, layerClass)
        
        featureType_url = GeoServerConfig.BaseGeoserverUrl + "rest/workspaces/ncgmp/datastores/django/featuretypes/"
        headers = { "Content-Type": "application/json" }
        
        headers, response = self.http.request(featureType_url, "POST", definition.serialize(), headers)
        assert 200 <= headers.status < 300, "Tried to create layer but got " + str(headers.status) + ": " + response
        self._cache.clear()