from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields.related import ForeignKey
from ncgmp.models import GeoMap, DescriptionOfMapUnits, RepresentativeValue
from ncgmp.utils import HttpGeoJsonResponse
import json

@csrf_exempt
def byCollection(req, gmId, dmuId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    
    if req.method == "GET":
        return HttpGeoJsonResponse(RepresentativeValue.objects.filter(mapunit=dmu))
    
    elif req.method == "POST":
        dmu.generateRepresentativeValues()
        return HttpGeoJsonResponse([dmu.representativeValue()])
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

@csrf_exempt
def byResource(req, gmId, dmuId, repId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    
    if req.method == "GET":
        rep = get_object_or_404(RepresentativeValue, pk=repId)
        if rep.mapunit != dmu: return HttpResponseBadRequest("Invalid lithology resource")
        return HttpGeoJsonResponse([rep])
    
    elif req.method == "PUT":
        raise NotImplementedError("PUT RepresentativeValue Resource")
    
    elif req.method == "DELETE":
        raise NotImplementedError("DELETE RepresentativeValue Attribute")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])

@csrf_exempt
def byAttribute(req, gmId, dmuId, repId, repProp):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    rep = get_object_or_404(RepresentativeValue, pk=repId)
    if rep.mapunit != dmu: return HttpResponseBadRequest("Invalid rep value resource")
    if repProp not in [field.name for field in RepresentativeValue._meta.fields]: raise Http404("Property does not exist")
    fld = [field for field in RepresentativeValue._meta.fields if field.name == repProp][0]
    
    if req.method == "GET":
        if isinstance(fld, ForeignKey): return HttpGeoJsonResponse([getattr(rep, repProp)])
        return HttpResponse(json.dumps(getattr(rep, repProp)), content_type="application/json")
    
    elif req.method == "PUT":
        if isinstance(fld, ForeignKey): raise NotImplementedError("Cannot update ForeignKey fields")
        
        data = req.body                
        response = { "success": True }
        try: 
            setattr(rep, repProp, data)
            rep.save()            
        except Exception (ex): 
            response["success"] = False
            response["message"] = str(ex)
        
        return HttpResponse(json.dumps(response), content_type="application/json")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT"])