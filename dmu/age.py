from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models.fields.related import ForeignKey
from ncgmp.models import GeoMap, DescriptionOfMapUnits, GeologicEvents, ExtendedAttributes
from ncgmp.utils import HttpGeoJsonResponse, geoJsonToKwargs
import json, uuid

@csrf_exempt
def byCollection(req, gmId, dmuId, qualifier):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid mapunit resource")
    
    if req.method == "GET":
        if qualifier == "age": response = dmu.geologicHistory()
        else: response = dmu.preferredAge()
        return HttpGeoJsonResponse(response, False)
    
    elif req.method == "POST":
        success, response = geoJsonToKwargs(GeologicEvents, req.raw_post_data, ["owningmap"])
        if not success: return HttpResponseBadRequest(response)
        response["owningmap"] = gm
        return createGeologicEvent(response, qualifier, gm, dmu)
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

@csrf_exempt  
def byResource(req, gmId, dmuId, qualifier, ageId):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid age resource")
    
    if req.method == "GET":
        ge = get_object_or_404(GeologicEvents, pk=ageId)
        if dmu not in ge.mapunits(): return HttpResponseBadRequest("Invalid age resource")
        if (qualifier.lower() == "age" and ge.inGeologicHistory(dmu)) or (qualifier.lower() == "preferredage" and ge.isPreferredAge(dmu)):
            return HttpGeoJsonResponse([ge])
        else:
            return HttpResponseBadRequest("Invalid age resource")
    
    elif req.method == "PUT":
        success, response = geoJsonToKwargs(GeologicEvents, req.raw_post_data, ["owningmap"])
        if not success: return HttpResponseBadRequest(response)
        response["owningmap"] = gm
        response["id"] = ageId
        return createGeologicEvent(response, qualifier, gm, dmu)
    
    elif req.method == "DELETE":
        ge = get_object_or_404(GeologicEvents, pk=ageId)
        if dmu not in ge.mapunits(): return HttpResponseBadRequest("Invalid age resource")
        if qualifier.lower() == "age" and ge.inGeologicHistory(dmu):
            extAttrs = ExtendedAttributes.objects.filter(valuelinkid=ge.geologicevents_id, ownerid=dmu.descriptionofmapunits_id).exclude(property="preferredAge")
        elif qualifier.lower() == "preferredage" and  ge.isPreferredAge(dmu): 
            extAttrs = ExtendedAttributes.objects.filter(valuelinkid=ge.geologicevents_id, ownerid=dmu.descriptionofmapunits_id, property="preferredAge")
        else: return HttpResponseBadRequest("Invalid age resource")
        
        extAttrs.delete()
        if ExtendedAttributes.objects.filter(valuelinkid=ge.geologicevents_id).count() == 0:
            ge.delete()
            
        return HttpResponse(json.dumps({"success": True}), content_type="application/json")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])

@csrf_exempt
def byAttribute(req, gmId, dmuId, qualifier, ageId, ageProp):
    gm = get_object_or_404(GeoMap, pk=gmId)
    dmu = get_object_or_404(DescriptionOfMapUnits, pk=dmuId)
    if dmu.owningmap != gm: return HttpResponseBadRequest("Invalid age resource")
    ge = get_object_or_404(GeologicEvents, pk=ageId)
    if dmu not in ge.mapunits(): return HttpResponseBadRequest("Invalid age resource")
    if (qualifier.lower() == "age" and not ge.inGeologicHistory(dmu)) or (qualifier.lower() == "preferredage" and not ge.isPreferredAge(dmu)): return HttpResponseBadRequest("Invalid age resource")
    if ageProp not in [field.name for field in GeologicEvents._meta.fields]: raise Http404("Property does not exist")
    
    if req.method == "GET":
        fld = [field for field in GeologicEvents._meta.fields if field.name == ageProp][0]
        if isinstance(fld, ForeignKey): return HttpGeoJsonResponse([getattr(ge, ageProp)])
        return HttpResponse(json.dumps(getattr(ge, ageProp)), content_type="application/json")
    
    elif req.method == "PUT":
        data = req.body 
        
        if isinstance(fld, ForeignKey):
            try:
                criteria = { fld.rel.field_name: data }
                data = fld.rel.to.objects.get(**criteria)        
            except fld.rel.to.DoesNotExist:
                return HttpResponseBadRequest("Cannot resolve foreign key relationship for '" + fld.name + "' = '" +  data + "'")
                            
        try: 
            setattr(ge, ageProp, data)
            ge.save()            
        except Exception as ex:
            return HttpResponseBadRequest(str(ex))
        else:
            return HttpResponse(json.dumps({ "success": True }), content_type="application/json")
    
    else:
        return HttpResponseNotAllowed(["GET", "PUT"])
    
def createGeologicEvent(kwargs, qualifier, gm, dmu):
    try:
        newGe = GeologicEvents(**kwargs)
        newGe.save()          
    except Exception as ex:
        return HttpResponseBadRequest(str(ex))
    
    if (qualifier.lower() == "age" and not newGe.inGeologicHistory(dmu)) or (qualifier.lower() == "preferredage" and not newGe.isPreferredAge(dmu)):
        properties = { "age": "GeologicHistory", "preferredage": "preferredAge"}
        extKwargs = {
            "owningmap": gm,
            "extendedattributes_id": uuid.uuid4(),
            "ownertable": "DescriptionOfMapUnits",
            "ownerid": dmu.descriptionofmapunits_id,
            "property": properties[qualifier.lower()],
            "propertyvalue": "",
            "valuelinkid": newGe.geologicevents_id,
            "qualifier": "",
            "notes": "",
            "datasourceid": newGe.datasourceid
        }
        newExt = ExtendedAttributes.objects.create(**extKwargs)
    
    return HttpGeoJsonResponse([newGe])