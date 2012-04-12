from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, get_object_or_404
from ncgmp.models import GeologicUnitView, DescriptionOfMapUnits, GeoMap
from ncgmp.utils import HttpGeoJsonResponse
import json

@csrf_exempt
def byCollection(req, gmId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    
    if req.method == "GET":
        return HttpGeoJsonResponse(GeologicUnitView.objects.filter(owningmap=gm), False)
    
    elif req.method == "POST":        
        response = { "success": True }
        try: 
            gm.populateRepresentativeValues()
            gm.createGsmlp()
            return HttpResponse(json.dumps(response), content_type="application/json")
        except Exception as ex: 
            response["success"] = False
            response["message"] = str(ex)
            return HttpResponse(json.dumps(response), content_type="application/json", status=500)          
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])