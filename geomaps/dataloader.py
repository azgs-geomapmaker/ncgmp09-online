from django.contrib.gis.gdal import DataSource
from django.db.models.fields.related import ForeignKey
from django.db.models import get_models, get_model

class GdbLoader():
    loadOrder = [
        "DataSources",
        "Glossary",
        "DescriptionOfMapUnits",
        "MapUnitPolys",
        "ContactsAndFaults"                     
    ]
    
    def __init__(self, geomap):
        self.geomap = geomap
        self.fgdb = DataSource(geomap.fgdb_path)
        self.acceptedLayers = [ cls._meta.object_name for cls in get_models() if cls._meta.app_label == "ncgmp" and cls._meta.object_name != "GeoMap" ]
                
    def load(self):
        for layerName in self.loadOrder:
            gdalLayer = [ layer for layer in self.fgdb if layer.name == layerName ][0]
            self.loadLayer(gdalLayer)
                    
    def loadLayer(self, gdalLayer):
        cls = get_model("ncgmp", gdalLayer.name)
        clsFields = [ clsField for clsField in cls._meta.fields if clsField.name != "id" and clsField.name != "owningmap" ]
        for feature in gdalLayer:
            newFeatureArgs = { "owningmap": self.geomap }                                                                           # New features are always related to the GeoMap being loaded
            for clsField in clsFields:                                                                                              # For each field in the destination table....
                if clsField.name == "shape":                                                                                        # Field is the Shape / Geometry Field
                    newFeatureArgs[clsField.name] = feature.geom.geos                                                               # feature.geom.geos is a GEOSGeometry object, which can be passed as directly to the model                    
                else:                                    
                    gdalField = gdalLayer.fields[ [ field.upper() for field in gdalLayer.fields ].index(clsField.name.upper()) ]    # Find the appropriate field in the GDAL Layer                    
                    if isinstance(clsField, ForeignKey):                                                                            # If the field is a Foreign Key
                        relatedCls = clsField.rel.to                                                                                # Find the related Class                    
                        relatedFieldName = clsField.rel.field_name                                                                  # Find the field name in the related Class
                        relatedCriteria = { relatedFieldName: feature.get(gdalField) }                                              # Sets up the filter criteria to find the correct instance of the related Class
                        newFeatureArgs[clsField.name] = relatedCls.objects.get(**relatedCriteria)                                   # Get the related instance, add it to kwargs for the new feature
                    elif clsField.name != "shape":                                                                                  # Field is not a Foreign Key, and is not a Shape field
                        newFeatureArgs[clsField.name] = feature.get(gdalField)                                                 
                
            newFeature = cls(**newFeatureArgs)
            newFeature.save()
                