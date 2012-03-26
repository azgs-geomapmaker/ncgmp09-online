from django.contrib.gis.gdal import DataSource

# Function to find a layer within a GDAL DataSource given its name
def getLayerByName(layername, datasource):
    index = 0
    output = None
    if layername is None or not isinstance(datasource, DataSource): return None
    while index < len(datasource):
        if datasource[index].name.upper() == layername.upper():
            output = datasource[index]
            break
        index = index + 1
        
    return output