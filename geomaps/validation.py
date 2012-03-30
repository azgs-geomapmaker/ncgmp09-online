from django.db.models import get_models, get_model
from django.db.models.fields.related import ForeignKey
from ncgmp.utils import getLayerByName
from collections import Counter
import json

class GdbValidator():    
    requiredLayers = [ 'DescriptionOfMapUnits', 'DataSources', 'Glossary', 'ContactsAndFaults', 'MapUnitPolys' ]
    requiredFields = {
        'DescriptionOfMapUnits': ['Age', 'AreaFillPatternDescription', 'AreaFillRGB', 'Description', 'DescriptionOfMapUnits_ID', 'DescriptionSourceID', 'FullName', 'GeneralLithologyConfidence', 'GeneralLithologyTerm', 'HierarchyKey', 'Label', 'MapUnit', 'Name', 'ParagraphStyle'],
        'ExtendedAttributes': ['DataSourceID', 'ExtendedAttributes_ID', 'Notes', 'OwnerID', 'OwnerTable', 'Property', 'PropertyValue', 'Qualifier', 'ValueLinkID'],
        'RelatedDocuments': ['DataSourceID', 'DocumentName', 'DocumentPath', 'Notes', 'OwnerID', 'RelatedDocuments_ID', 'Type'],
        'StandardLithology': ['DataSourceID', 'Lithology', 'MapUnit', 'PartType', 'ProportionTerm', 'ProportionValue', 'ScientificConfidence', 'StandardLithology_ID'],
        'GeologicEvents': ['AgeDisplay', 'AgeOlderTerm', 'AgeOlderValue', 'AgeYoungerTerm', 'AgeYoungerValue', 'DataSourceID', 'Event', 'GeologicEvents_ID', 'Notes', 'TimeScale'],
        'DataSources': ['DataSources_ID', 'Notes', 'Source'],
        'Glossary': ['Definition', 'DefinitionSourceID', 'Glossary_ID', 'Term'],
        'Notes': ['DataSourceID', 'Notes', 'Notes_ID', 'OwnerID', 'Type'],
        'DataSourcePolys': ['DataSourceID', 'DataSourcePolys_ID', 'Notes'],
        'CartographicLines': ['CartographicLines_ID', 'DataSourceID', 'Label', 'Notes', 'Symbol', 'Type'],
        'SamplePoints': ['DataSourceID', 'FieldID', 'Label', 'LocationConfidenceMeters', 'Notes', 'PlotAtScale', 'SamplePoints_ID', 'StationID', 'Symbol'],
        'OrientationDataPoints': ['Azimuth', 'DataSourceID', 'IdentityConfidence', 'Inclination', 'Label', 'Notes', 'OrientationConfidenceDegrees', 'OrientationDataPoints_ID', 'Override', 'PlotAtScale', 'StationID', 'Symbol', 'SymbolRotation', 'Type'],
        'StationPoints': ['DataSourceID', 'FieldID', 'Label', 'Latitude', 'LocationConfidenceMeters', 'Longitude', 'PlotAtScale', 'StationPoints_ID', 'Symbol'],
        'ContactsAndFaults': ['ContactsAndFaults_ID', 'DataSourceID', 'ExistenceConfidence', 'IdentityConfidence', 'IsConcealed', 'Label', 'LocationConfidenceMeters', 'Notes', 'Override', 'Symbol', 'Type'],
        'OtherLines': ['DataSourceID', 'ExistenceConfidence', 'IdentityConfidence', 'Label', 'LocationConfidenceMeters', 'Notes', 'OtherLines_ID', 'Override', 'Symbol', 'Type'],
        'MapUnitPolys': ['DataSourceID', 'IdentityConfidence', 'Label', 'MapUnit', 'MapUnitPolys_ID', 'Notes', 'Symbol'],
        'OverlayPolys': ['DataSourceID', 'IdentityConfidence', 'Label', 'MapUnit', 'Notes', 'OverlayPolys_ID', 'Symbol']
    }
    
    def __init__(self, fgdb):
        self.logs = self.Logger()
        self.fgdb = fgdb
        excludedModels = ["GeoMap", "GeologicUnitView", "RepresentativeValue"]
        self.acceptedLayers = [ cls._meta.object_name for cls in get_models() if cls._meta.app_label == "ncgmp" and cls._meta.object_name not in excludedModels ]
        
    def isValid(self):
        if self.validateTables():
            if self.validateFields():
                if self.validateUniqueKeys():
                    if self.validateForeignKeys():
                        return True
        return False
    
    def validateTables(self):
        fgdbLayers = [layer.name for layer in self.fgdb]
        requiredLayerSet = set(self.requiredLayers)
        requiredLayersPresent = requiredLayerSet.intersection(fgdbLayers)
        if requiredLayersPresent == requiredLayerSet:
            return True
        else:
            missingLayers = list(requiredLayerSet.difference(requiredLayersPresent))
            self.logs.missingTables = missingLayers
            return False
        
    def validateFields(self):
        output = True
        for gdalLayer in [ layer for layer in self.fgdb if layer.name in self.acceptedLayers ]:
            requiredFields = set(self.requiredFields[gdalLayer.name])
            requiredFieldsPresent = requiredFields.intersection(gdalLayer.fields)
            if requiredFieldsPresent != requiredFields:
                missingFields = list(requiredFields.difference(requiredFieldsPresent))
                self.logs.addMissingFields(gdalLayer.name, missingFields)
                output = False            
        return output                            
    
    def validateUniqueKeys(self):
        output = True
        for gdalLayer in [ layer for layer in self.fgdb if layer.name in self.acceptedLayers ]:
            cls = get_model("ncgmp", gdalLayer.name)
            clsFields = cls._meta.fields
            uniqueFields = [ fld.name for fld in clsFields if fld.name != "id" and fld.unique ]            
            for uniqueField in uniqueFields:                  
                gdalField = gdalLayer.fields[ [field.upper() for field in gdalLayer.fields ].index(uniqueField.upper()) ]
                values = [ feature.get(gdalField) for feature in gdalLayer ]
                countedValues = Counter(values)
                repeats = [ i for i in countedValues if countedValues[i] > 1 ]
                
                if len(repeats) > 0:
                    self.logs.addRepeatedUniqueValues(gdalLayer.name, gdalField, repeats)
                    output = False
        return output
    
    def validateForeignKeys(self):
        output = True
        for gdalLayer in [ layer for layer in self.fgdb if layer.name in self.acceptedLayers ]:
            cls = get_model("ncgmp", gdalLayer.name)
            clsFields = cls._meta.fields
            fkFields = [ field for field in clsFields if isinstance(field, ForeignKey) and field.name != "owningmap" ]            
            for fkField in fkFields:
                relatedLayerName = fkField.rel.to._meta.object_name
                
                # ----------------------------------------------------------------------------------
                # Exception for mapunit relationship between MapUnitPolys and DescriptionOfMapUnits
                if fkField.name.upper() == "MAPUNIT" and gdalLayer.name == "MapUnitPolys":
                    relatedFieldName = "mapunit"
                else:
                    relatedFieldName = fkField.rel.field_name
                                
                relatedGdalLayer = getLayerByName(relatedLayerName, self.fgdb)
                # ----------------------------------------------------------------------------------
                                
                gdalField = gdalLayer.fields[ [ field.upper() for field in gdalLayer.fields ].index(fkField.name.upper()) ]
                relatedGdalField = relatedGdalLayer.fields[ [ field.upper() for field in relatedGdalLayer.fields ].index(relatedFieldName.upper()) ]
                
                fKeys = set([ feature.get(gdalField) for feature in gdalLayer ])
                relatedKeys = set([ feature.get(relatedGdalField) for feature in relatedGdalLayer ])
                
                missingKeys = fKeys.difference(relatedKeys)
                if len(missingKeys) > 0:
                    self.logs.addMissingForeignKeys(gdalLayer.name, relatedGdalField, relatedLayerName, list(missingKeys))
                    output = False                    
        return output
    
    def validationMessage(self):
        return self.logs.consoleMessage()
            
    class Logger():
        def __init__(self):
            self.missingTables = [] 
            self.missingFields = {}
            self.repeatedUniqueValues = {}
            self.missingForeignKeys = {}
            
        def addMissingFields(self, table, fields):        
            self.missingFields[table] = fields
            
        def addRepeatedUniqueValues(self, table, field, values):
            if table not in self.repeatedUniqueValues.keys():
                self.repeatedUniqueValues[table] = {}
            
            self.repeatedUniqueValues[table][field] = values
        
        def addMissingForeignKeys(self, table, field, relatedTable, values):
            if table not in self.missingForeignKeys.keys():
                self.missingForeignKeys[table] = {}
                
            self.missingForeignKeys[table][field + " >> " + relatedTable] = values
            
        def consoleMessage(self):
            tableMessage = "\n".join(self.missingTables)
            fieldMessage = "\n".join([tableName + ": " + ", ".join(self.missingFields[tableName]) for tableName in self.missingFields.keys()])
            repeatMessage = "\n".join([tableName + "\n\t" + "\n\t".join([fieldName + "\n\t\t" + "\n\t\t".join(self.repeatedUniqueValues[tableName][fieldName]) for fieldName in self.repeatedUniqueValues[tableName].keys()]) for tableName in self.repeatedUniqueValues.keys()])
            fkMessage = "\n".join([tableName + "\n\t" + "\n\t".join([relName + "\n\t\t" + "\n\t\t".join(self.missingForeignKeys[tableName][relName]) for relName in self.missingForeignKeys[tableName].keys()]) for tableName in self.missingForeignKeys.keys()])
            
            output = []
            if len(tableMessage) > 0:
                output.append(" ---- MISSING TABLES ---- ") 
                output.append(tableMessage)
            if len(fieldMessage) > 0:
                output.append(" ---- TABLES MISSING FIELDS ---- ") 
                output.append(fieldMessage)
            if len(repeatMessage) > 0:
                output.append(" ---- DUPLICATE VALUES IN UNIQUE FIELDS ---- ") 
                output.append(repeatMessage)
            if len(fkMessage) > 0:
                output.append(" ---- MISSING FOREIGN KEYS ---- ") 
                output.append(fkMessage)
            return "\n".join(output)
        
        def asJson(self):
            output= {}
            if len(self.missingTables) > 0: output["MissingTables"] = self.missingTables
            if len(self.missingFields.keys()) > 0: output["MissingFields"] = self.missingFields
            if len(self.repeatedUniqueValues.keys()) > 0: output["RepeatedUniqueValues"] = self.repeatedUniqueValues
            if len(self.missingForeignKeys.keys()) > 0: output["MissingForeignKeys"] = self.missingForeignKeys
            
            return json.dumps(output)
            