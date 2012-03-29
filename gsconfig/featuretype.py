from ncgmp.config import GeoServerConfig
from django.contrib.gis.gdal import DataSource
from django.conf import settings
from collections import OrderedDict
import json

class SqlFeatureTypeDef:
    def __init__(self, geomap, layerClass):
        self.name = geomap.name.replace(" ", "-")
        
        dbSettings = settings.DATABASES['default']
        connectionString = "PG:dbname='" + dbSettings['NAME'] + "' user='" + dbSettings['USER'] + "' password='" + dbSettings['PASSWORD'] + "'"
        ds = DataSource(connectionString)
        
        if layerClass._meta.db_table in [ layer.name for layer in ds ]:
            layer = [ layer for layer in ds if layer.name == layerClass._meta.db_table ][0]
        else: raise Exception
        
        self.namespace = {
            "name": "ncgmp",
            "href": GeoServerConfig.BaseGeoserverUrl + "rest/namespaces/ncgmp.json"                  
        }
        
        self.nativeCRS = layer.srs.wkt
        
        self.nativeBoundingBox = {
            "minx": layer.extent.min_x,
            "maxx": layer.extent.max_x,
            "miny": layer.extent.min_y,
            "maxy": layer.extent.max_y,
            "crs": "EPSG:" + str(layer.srs.srid)                          
        }
        
        self.geometry = OrderedDict()
        self.geometry["name"] = "shape"
        self.geometry["type"] = layer.geom_type.name
        self.geometry["srid"] = layer.srs.srid
        
        self.virtualTable = OrderedDict()
        self.virtualTable["name"] = self.name
        self.virtualTable["sql"] = "select * from " + layerClass._meta.db_table + " where owningmap_id = " + str(geomap.id)
        self.virtualTable["geometry"] = self.geometry
        
        self.store = {
            "@class": "dataStore",
            "name": "django",
            "href": GeoServerConfig.BaseGeoserverUrl + "rest/workspaces/ncgmp/datastores/django.json"              
        }
        
    def serialize(self):
        return json.dumps({
            "featureType": {
                "name": self.name,
                "namespace": self.namespace,
                "nativeCRS": self.nativeCRS,
                "nativeBoundingBox": self.nativeBoundingBox,
                "metadata": {
                    "entry": {
                        "@key": "JDBC_VIRTUAL_TABLE",
                        "virtualTable": self.virtualTable          
                    }             
                },
                "store": self.store                
            }              
        })