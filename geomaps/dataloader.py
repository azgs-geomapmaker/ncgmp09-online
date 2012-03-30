from django.contrib.gis.gdal import DataSource
from django.db.models.fields.related import ForeignKey
from django.db.models import get_models, get_model
from django.db import transaction

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
                
    def load(self):
        for layerName in self.loadOrder:
            gdalMatch = [ layer for layer in self.fgdb if layer.name == layerName ]
            if len(gdalMatch) == 1: self.loadLayer(gdalMatch[0])
    
    @transaction.commit_manually                
    def loadLayer(self, gdalLayer):
        cls = get_model("ncgmp", gdalLayer.name)
        clsFields = [ clsField for clsField in cls._meta.fields if clsField.name not in ["id", "owningmap"] ]
        upperFields = [ field.upper() for field in gdalLayer.fields ]
        for feature in gdalLayer:
            newFeatureArgs = { "owningmap": self.geomap }                                                                           # New features are always related to the GeoMap being loaded
            for clsField in clsFields:                                                                                              # For each field in the destination table....
                if clsField.name == "shape":                                                                                        # Field is the Shape / Geometry Field
                    newFeatureArgs[clsField.name] = feature.geom.geos                                                               # feature.geom.geos is a GEOSGeometry object, which can be passed as directly to the model                    
                else:                                    
                    gdalField = gdalLayer.fields[ upperFields.index(clsField.name.upper()) ]                                        # Find the appropriate field in the GDAL Layer                    
                    if isinstance(clsField, ForeignKey):                                                                            # If the field is a Foreign Key
                        relatedCls = clsField.rel.to                                                                                # Find the related Class
                        
                        # ----------------------------------------------------------------------------------
                        # Exception for mapunit relationship between MapUnitPolys and DescriptionOfMapUnits
                        if clsField.name == "mapunit" and gdalLayer.name == "MapUnitPolys":
                            relatedFieldName = "mapunit"
                        else:
                            relatedFieldName = clsField.rel.field_name                                                              # Find the field name in the related Class
                        # ----------------------------------------------------------------------------------
                                            
                                                                                    
                        relatedCriteria = { relatedFieldName: feature.get(gdalField) }                                              # Sets up the filter criteria to find the correct instance of the related Class
                        newFeatureArgs[clsField.name] = relatedCls.objects.get(**relatedCriteria)                                   # Get the related instance, add it to kwargs for the new feature
                    else:                                                                                                           # Field is not a Foreign Key, and is not a Shape field
                        newFeatureArgs[clsField.name] = feature.get(gdalField)                                                 
                
            newFeature = cls(**newFeatureArgs)
            newFeature.save()                    
        transaction.commit()