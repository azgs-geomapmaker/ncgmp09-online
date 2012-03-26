from django.contrib.gis.gdal import DataSource, OGRException
from django.db.models.fields.related import ForeignKey
from django.db.models import get_model

class Logger(list):
    pass

# Variable to define where to get fields from the source database to ingest into the destination database
#    primarily handles lowercasing that is a consequence of postgresql, but also provides info about Foreign Key relationships
fld_maps = {
    'DataSources': {'datasources_id': 'DataSources_ID', 'source': 'Source', 'notes': 'Notes'},   
    'Glossary': {'definition': 'Definition', 'term': 'Term', 'glossary_id': 'Glossary_ID', 'definitionsourceid': {'datasources_id': 'DefinitionSourceID'}},
    'DescriptionOfMapUnits': {'generallithologyconfidence': 'GeneralLithologyConfidence', 'hierarchykey': 'HierarchyKey', 'name': 'Name', 'areafillrgb': 'AreaFillRGB', 'generallithologyterm': 'GeneralLithologyTerm', 'age': 'Age', 'descriptionsourceid': {'datasources_id': 'DescriptionSourceID'}, 'label': 'Label', 'areafillpatterndescription': 'AreaFillPatternDescription', 'mapunit': 'MapUnit', 'fullname': 'FullName', 'paragraphstyle': 'ParagraphStyle', 'descriptionofmapunits_id': 'DescriptionOfMapUnits_ID', 'description': 'Description'}, 
}

# Function to build a simple mapping of required relationships for a table
def relationship_mapping(table_name):
    # Get the model class corresponding to this table
    cls = get_model("ncgmp", table_name)
    if cls is None: return None
    
    opts = cls._meta
    relationships = {}
    for fld in opts.fields:
        if isinstance(fld, ForeignKey):
            relationships[fld.name] = { # fld.name = The name of the field in this table that relates to another
              "table": fld.rel.to._meta.object_name, # = The name of the related table
              "field": fld.rel.field_name } # = The name of the field in the related table    
                
    if relationships == {}: return None
    else: return relationships
    
# Function to find a layer within a GDAL DataSource given its name
def get_layer_by_name(layername, datasource):
    index = 0
    output = None
    if layername is None or not isinstance(datasource, DataSource): return None, 0
    while index < len(datasource):
        if datasource[index].name.upper() == layername.upper():
            output = datasource[index]
            break
        index = index + 1
        
    return output, index

# Function to check Tables in an NCGMP File Geodatabase
def table_validator(fgdb):
    required_layers = [ 'DescriptionOfMapUnits', 'DataSources', 'Glossary', 'ContactsAndFaults', 'MapUnitPolys' ]
    if not set(required_layers).intersection([layer.name for layer in fgdb]) == set(required_layers):
        missing_tables = list(set(required_layers).difference(set(required_layers).intersection([layer.name for layer in fgdb])))
        return False, "Database is missing required tables: " + ", ".join(missing_tables)
    else: return True, "Tables are valid"

# Function to check Field Names in an NCGMP File Geodatabase
def field_validator(fgdb):
    field_checks = {
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
    
    passed_field_validation = True
    message = []
    for layer in fgdb:
        if layer.name in field_checks.keys() and not set(field_checks[layer.name]).intersection(layer.fields) == set(field_checks[layer.name]):
            passed_field_validation = False
            missing_fields = list(set(field_checks[layer.name]).difference(set(field_checks[layer.name]).intersection(layer.fields)))
            message.append(layer.name + " is missing required fields: " + ", ".join(missing_fields))
            
    if not passed_field_validation: return False, "\n".join(message)
    else: return True, "Fields are valid"

# Function to check Foreign Key validity in an NCGMP File Geodatabase
def fk_validator(fgdb):
    output = {}
    # For each layer in the File Geodatabase...
    for layer in fgdb:
        lyr_output = {}
        rels = relationship_mapping(layer.name)
        if rels:
            # For each relationship in the layer....
            for fk in rels.keys():
                rel_lyr = get_layer_by_name(rels[fk]["table"], fgdb)[0]
                if rel_lyr is None: continue
                
                # Get fk and pk names with the proper case-sensitivity
                corr_fk = layer.fields[[fld.upper() for fld in layer.fields].index(fk.upper())]
                corr_pk = rel_lyr.fields[[fld.upper() for fld in rel_lyr.fields].index(rels[fk]["field"].upper())]
                
                # Build an array of all the keys that need to be found
                find_these = []
                
                # For each feature in this layer...
                for f in layer:
                    # Get the key value into the array
                    key_val = f.get(corr_fk) # Get the value of the fk
                    if key_val not in find_these: find_these.append(key_val)
                    
                # For each feature in the related layer...
                for rel_f in rel_lyr:
                    this_rel_key = rel_f.get(corr_pk)
                    if this_rel_key in find_these: # If the pk matches a fk, remove it from the array
                        find_these.remove(this_rel_key)
                
                # If, after looking at all related features we didn't find a match, fill out the logging helper obj
                if len(find_these) > 0 and rel_lyr.name not in lyr_output.keys():
                    lyr_output[rel_lyr.name] = find_these
                if len(find_these) > 0 and rel_lyr.name in lyr_output.keys():
                    lyr_output[rel_lyr.name] = list(set(lyr_output[rel_lyr.name]).union(find_these))
                    
            # If there were any unmatched in this layer, add the info to the final output logging obj            
            if len(lyr_output.keys()) > 0: output[layer.name] = lyr_output
        
    if len(output.keys()) > 0:
        message = ""
        for lyr_name in output.keys():
            message = message + lyr_name.upper() + ":\n"
            for rel_lyr_name in output[lyr_name]:
                message = message + "\t" + rel_lyr_name + ":\n"
                message = message + "\t\t" + "\n\t\t".join(output[lyr_name][rel_lyr_name]) + "\n\n"
                
        return False, message
    else: return True, "Foreign Key relationships are valid"

# Function to validate that unique key fields are in fact unique
def unique_validator(fgdb):
    output = {}
    for lyr_name in fld_maps:
        this_layer_output = {}
        layer, index = get_layer_by_name(lyr_name, fgdb)
        
        opts = get_model("ncgmp", lyr_name)._meta
        for fld in opts.fields:
            if fld.name == "id": continue # id field doesn't exist in the data layer yet, doesn't need to be checked
            if fld.unique:
                this_fld_output = []
                corr_fld_name = fld_maps[lyr_name][fld.name]
                the_keys = []
                for f in layer:
                    this_key = f.get(corr_fld_name)
                    if this_key not in the_keys: the_keys.append(this_key)
                    else: this_fld_output.append(this_key)
                if len(this_fld_output) > 0 :
                    this_layer_output[fld.name] = this_fld_output
        if len(this_layer_output.keys()) > 0:
            output[lyr_name] = this_layer_output
        
    if len(output.keys()) > 0:
        message = ""
        for lyr_name in output.keys():
            message = message +lyr_name.upper() + " has duplicate values in unique key fields:\n"
            for fld_name in output[lyr_name]:
                message = message + "\t" + fld_name + ":\n"
                message = message + "\t\t" + "\n\t\t".join(output[lyr_name][fld_name]) + "\n\n"
                
        return False, message
    else:
        return True, "Unique Key fields are valid"
        

# Function to validate an NCGMP File Geodatabase
def validate_fgdb(geomap):
    # First step in validation: GDAL has to be able to open it
    try:
        fgdb = DataSource(geomap.fgdb_path)
    except OGRException as ex:
        return False, ex.message
    
    # Next step in validation: Must contain the minimum set of tables
    valid, message = table_validator(fgdb)
    if not valid: return valid, message
    
    # Next step in validation: Check that field names are correct
    valid, message = field_validator(fgdb)
    if not valid: return valid, message
    
    # Next step in validation: Check that unique keys are in fact unique
    valid, message = unique_validator(fgdb)
    if not valid: return False, message
    
    # Next step in validation: Check that Foreign Key relationships are observed
    #    This is really, really slow. Perhaps this can be replaced by catching errors during load_data??
    valid, message = fk_validator(fgdb)
    if not valid: return False, message
    
    # If we got here, then we validated
    return True, "Database passed validation"
      
def load_data(geomap):
    # Get the DataSource
    ds = DataSource(geomap.fgdb_path)
    
    for lyr_name in fld_maps.keys():
        lyr = get_layer_by_name(lyr_name, ds)[0]
        cls = get_model("ncgmp", lyr_name)
        
        # Generate field-mapping dictionary
        fld_map = fld_maps[lyr_name]
        
        # Loop through the features in the layer
        for f in lyr:
            # Build the arguments to create a new instance of the appropriate model
            kwargs = {'owningmap': geomap}                                              # New features are always related to the GeoMap being loaded
            for dest_fld in fld_map:                                                    # For each field in the destination table....
                if isinstance(fld_map[dest_fld], dict):                                 # Dict in field map indicates that this field is a Foreign Key
                    related_cls = cls._meta.get_field_by_name(dest_fld)[0].rel.to       # Gets the related Class
                    related_fld = fld_map[dest_fld].keys()[0]                           # Gets the lookup field in the related Class
                    criteria = {related_fld: f.get(fld_map[dest_fld][related_fld])}     # Sets up the filter criteria to find the correct instance of the related Class
                    kwargs[dest_fld] = related_cls.objects.get(**criteria)              # Gets the instance of the related Class, adds it to the args for the new feature
                elif dest_fld not in ['shape']:                                         # Field is not a Foreign Key, and is not a Shape field
                    kwargs[dest_fld] = f.get(fld_map[dest_fld])                         # Simply add the field value to the arguments for the new feature
                elif dest_fld == 'shape':                                               # Field is a Shape Field
                    pass
            
            # Build, save the new thing
            new_inst = cls(**kwargs)
            new_inst.save()
                
    # Getting out here means that loading completed successfully
    return True, "Data loaded successfully"
            