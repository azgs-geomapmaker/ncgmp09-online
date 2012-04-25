from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields.related import ForeignKey
from django.contrib.gis.geos import Polygon
from ncgmp.models import GeoMap, DescriptionOfMapUnits
from ncgmp.utils import HttpGeoJsonResponse, SimpleJsonResponse, generate_color_dictionary
import json, mimeparse

@csrf_exempt
def byCollection(req, gmId):
    gm = get_object_or_404(GeoMap, pk=gmId)            
    
    if req.method == "GET":
        dmus = DescriptionOfMapUnits.objects.filter(owningmap=gm).exclude(paragraphstyle__iexact="heading")
        
        queryBox = req.GET.get("bbox", False)
        if queryBox:
            # input is lower-left x,lower-left y,upper-right x,upper-right y, in WGS84
            queryBox = queryBox.split(',')        
            bbox = Polygon.from_bbox((queryBox[0], queryBox[1], queryBox[2], queryBox[3]))
            dmus = dmus.filter(mapunitpolys__shape__intersects=bbox).distinct();
                
        return dmuContentNegotiation(req.META['HTTP_ACCEPT'].lower(), dmus, False)        
    
    elif req.method == "POST":
        raise NotImplementedError("POST DescriptionOfMapUnits Collection")
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

@csrf_exempt
def byResource(req, gmId, dmuId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    
    if req.method == "GET":
        dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
        if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
        return dmuContentNegotiation(req.META['HTTP_ACCEPT'].lower(), [dmu])
    
    elif req.method == "PUT":
        raise NotImplementedError("PUT DescriptionOfMapUnits Resource")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT"])

@csrf_exempt
def byAttribute(req, gmId, dmuId, dmuProp):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    if dmuProp not in [field.name for field in DescriptionOfMapUnits._meta.fields]: raise Http404("Property does not exist")
    fld = [field for field in DescriptionOfMapUnits._meta.fields if field.name == dmuProp][0]
    
    if req.method == "GET":        
        if isinstance(fld, ForeignKey): return HttpGeoJsonResponse([getattr(dmu, dmuProp)])
        return HttpResponse(json.dumps(getattr(dmu, dmuProp)), content_type="application/json")
    
    elif req.method == "PUT":
        data = req.body
        
        if isinstance(fld, ForeignKey): 
            try:
                criteria = { fld.rel.field_name: data }
                data = fld.rel.to.objects.get(**criteria)        
            except fld.rel.to.DoesNotExist:
                return HttpResponseBadRequest("Cannot resolve foreign key relationship for '" + fld.name + "' = '" +  data + "'")

        try: 
            setattr(dmu, dmuProp, data)
            dmu.save()            
        except Exception as ex: 
            return HttpResponseBadRequest(str(ex))
        else:
            return HttpResponse(json.dumps({ "success": True }), content_type="application/json")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT"])
    
def dmuContentNegotiation(accept, dmus, single=True):
    availableFormats = ["application/json", "text/html", "application/sld", "text/mss"]
    requestedFormat = mimeparse.best_match(availableFormats, accept)
    
    if requestedFormat == "application/json":
        return HttpGeoJsonResponse(dmus, single)
    elif requestedFormat == "text/html":
        return render_to_response("dmu/dmuHtml.html", {"dmu_list": dmus, 'colors': generate_color_dictionary(dmus)})
    elif requestedFormat == "application/sld":
        return render_to_response("dmu/dmuSld.xml", {"dmu_list": dmus, 'colors': generate_color_dictionary(dmus)}, mimetype="application/xml")
    elif requestedFormat == "text/mss":
        return render_to_response("dmu/dmuMss.mss", {"dmu_list": dmus, 'colors': generate_color_dictionary(dmus)}, mimetype="text/mss")
    else:
        return HttpResponse('Not Acceptable', status=406)