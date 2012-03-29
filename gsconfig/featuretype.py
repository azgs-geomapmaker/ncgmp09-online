from ncgmp.config import GeoServerConfig
from django.contrib.gis.gdal import DataSource
from django.conf import settings
from collections import OrderedDict
import json

class SqlFeatureTypeDef:
    def __init__(self, geomap, workspace, layerClass):
        self.name = "-".join([geomap.name, layerClass._meta.db_table])
        self.title = " for ".join([layerClass._meta.object_name, geomap.title])
        self.fieldNames = [ "\"%s\"" % fld.name for fld in layerClass._meta.fields if fld.name not in ["id", "owningmap"] ]
        
        dbSettings = settings.DATABASES['default']
        connectionString = "PG:dbname='" + dbSettings['NAME'] + "' user='" + dbSettings['USER'] + "' password='" + dbSettings['PASSWORD'] + "'"
        ds = DataSource(connectionString)
        
        if layerClass._meta.db_table in [ layer.name for layer in ds ]:
            layer = [ layer for layer in ds if layer.name == layerClass._meta.db_table ][0]
        else: raise Exception
        
        self.namespace = {
            "name": workspace.name,
            "href": GeoServerConfig.BaseGeoserverUrl + "rest/namespaces/" + workspace.name + ".json"                  
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
        self.virtualTable["sql"] = "select " + ", ".join(self.fieldNames) + " from " + layerClass._meta.db_table + " where owningmap_id = " + str(geomap.id)
        self.virtualTable["geometry"] = self.geometry
        
        self.store = {
            "@class": "dataStore",
            "name": "django",
            "href": GeoServerConfig.BaseGeoserverUrl + "rest/workspaces/" + workspace.name + "/datastores/" + GeoServerConfig.DataStoreName + ".json"              
        }
        
    def serialize(self):
        return json.dumps({
            "featureType": {
                "name": self.name,
                "title": self.title,
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