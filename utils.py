from django.contrib.gis.gdal import DataSource
from django.core.serializers import serialize
from django.contrib.gis.geos import GEOSGeometry
from django.db.models.fields.related import ForeignKey
from django.http import HttpResponse
import json

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

def HttpGeoJsonResponse(querySet, single=True):
    input = json.loads(serialize("json", querySet))
    output = { "type": "FeatureCollection", "features": [] }
    for inputObj in input:
        feature = {
            "type": "Feature",
            "id": inputObj["pk"],
            "properties": {},
            "geometry": None       
        }
        
        for fld in inputObj["fields"].keys():
            if fld == "shape":
                geom = GEOSGeometry(inputObj["fields"][fld])
                feature["geometry"] = geom.json
            else:
                feature["properties"][fld] = inputObj["fields"][fld]
        output["features"].append(feature)
    
    if single: output = feature
    return HttpResponse(json.dumps(output), content_type="application/json")

def SimpleJsonResponse(querySet, single=True):
    input = json.loads(serialize("json", querySet))
    output = []
    for inputObj in input:
        feature = { "id": inputObj["pk"] }
        for fld in inputObj["fields"].keys():
            if fld == "shape":
                geom = GEOSGeometry(inputObj["fields"][fld])
                feature["geometry"] = geom.json
            else:
                feature[fld] = inputObj["fields"][fld]
        output.append(feature)
        
    if single: output = feature
    return HttpResponse(json.dumps(output), content_type="application/json")
            
def geoJsonToKwargs(model, geoJson, ignore=[]):
    input = json.loads(geoJson)
    output = dict()
    
    if "id" in input.keys(): output["id"] = input["id"]
    if "geometry" in input.keys() and "shape" in [field.name for field in model._meta.fields]:
        output["shape"] = GEOSGeometry(input["geometry"])
    
    for prop in [p for p in input["properties"].keys() if p not in ignore]:
        fld = [field for field in model._meta.fields if field.name == prop]
        if len(fld) == 1:
            fld = fld[0]
            inputVal = input["properties"][prop]
            if isinstance(fld, ForeignKey):
                try:
                    criteria = { fld.rel.field_name: inputVal }
                    relatedResource = fld.rel.to.objects.get(**criteria)
                    output[prop] = relatedResource                    
                except fld.rel.to.DoesNotExist:
                    return False, "Cannot resolve foreign key relationship for '" + prop + "' = '" +  inputVal + "'"
            else:
                output[prop] = inputVal
            
    return True, output

def tohex(r,g,b):
    hexchars = "0123456789ABCDEF"
    return "#" + hexchars[r / 16] + hexchars[r % 16] + hexchars[g / 16] + hexchars[g % 16] + hexchars[b / 16] + hexchars[b % 16]
      
def generate_color_dictionary(dmu_queryset):
    color_dict = dict()
    for description in dmu_queryset:
        r = int(description.areafillrgb.split(';')[0])
        g = int(description.areafillrgb.split(';')[1])
        b = int(description.areafillrgb.split(';')[2])
        color_dict[description.pk] = tohex(r,g,b)
    
    return color_dict