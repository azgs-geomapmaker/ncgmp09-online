from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields.related import ForeignKey
from ncgmp.models import GeoMap, DescriptionOfMapUnits, StandardLithology
from ncgmp.utils import HttpGeoJsonResponse, geoJsonToKwargs
import json

@csrf_exempt
def byCollection(req, gmId, dmuId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    
    if req.method == "GET":
        return HttpGeoJsonResponse(StandardLithology.objects.filter(mapunit=dmu))
    
    elif req.method == "POST":
        success, response = geoJsonToKwargs(StandardLithology, req.raw_post_data, ["owningmap", "mapunit"])
        if not success: return HttpResponseBadRequest(response)
        
        response["owningmap"] = gm
        response["mapunit"] = dmu
        
        try:
            newSl = StandardLithology(**response)
            newSl.save()
            return HttpGeoJsonResponse(newSl)
        except Exception (ex):
            return HttpResponseBadRequest(str(ex))
        
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

@csrf_exempt    
def byResource(req, gmId, dmuId, lithId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    
    if req.method == "GET":
        sl = get_object_or_404(StandardLithology, pk=lithId)
        if sl.mapunit != dmu: return HttpResponseBadRequest("Invalid lithology resource")
        return HttpGeoJsonResponse([sl])
    
    elif req.method == "PUT":
        success, response = geoJsonToKwargs(StandardLithology, req.raw_post_data, ["owningmap", "mapunit"])
        if not success: return HttpResponseBadRequest(response)
        
        response["owningmap"] = gm
        response["mapunit"] = dmu
        response["id"] = lithId
        
        try:
            newSl = StandardLithology(**response)
            newSl.save()
            return HttpGeoJsonResponse(newSl)
        except Exception (ex):
            return HttpResponseBadRequest(str(ex))
        
    elif req.method == "DELETE":
        sl = get_object_or_404(StandardLithology, pk=lithId)
        if sl.mapunit != dmu: return HttpResponseBadRequest("Invalid lithology resource")
        try: sl.delete()
        except Exception (ex):
            return HttpResponseBadRequest(str(ex))
        else:
            return HttpResponse(json.dumps({ "success": True }), content_type="application/json")
        
    else:
        return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])

@csrf_exempt
def byAttribute(req, gmId, dmuId, lithId, lithProp):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    sl = get_object_or_404(StandardLithology, pk=lithId)
    if sl.mapunit != dmu: return HttpResponseBadRequest("Invalid lithology resource")
    if lithProp not in [field.name for field in StandardLithology._meta.fields]: raise Http404("Property does not exist")
    fld = [field for field in StandardLithology._meta.fields if field.name == lithProp][0]
    
    if req.method == "GET":        
        if isinstance(fld, ForeignKey): return HttpGeoJsonResponse([getattr(sl, lithProp)])
        return HttpResponse(json.dumps(getattr(sl, lithProp)), content_type="application/json")
    
    elif req.method == "PUT":
        data = req.body
        
        if isinstance(fld, ForeignKey): 
            try:
                criteria = { fld.rel.field_name: data }
                data = fld.rel.to.objects.get(**criteria)        
            except fld.rel.to.DoesNotExist:
                return HttpResponseBadRequest("Cannot resolve foreign key relationship for '" + fld.name + "' = '" +  data + "'")
            
        try: 
            setattr(sl, lithProp, data)
            sl.save()
        except Exception (ex): 
            return HttpResponseBadRequest(str(ex))
        else:
            return HttpResponse(json.dumps({ "success": True }), content_type="application/json")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT"])