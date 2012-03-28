from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.core.context_processors import csrf
from ncgmp.models import GeoMap
from upload import UploadGeoMapForm

def uploads(req):
    
    if req.method == 'GET':
        form = UploadGeoMapForm()
        context = {
            "title": "New Geologic Map",
            "form": form
        }
        context.update(csrf(req))
        
        return render_to_response('geomap.jade', context)
    
    
    elif req.method == 'POST':
        form = UploadGeoMapForm(req.POST, req.FILES)
        if form.is_valid():                   
            return HttpResponseRedirect(str(form.fgdbHandler.newGeoMap.id))
        PUT
        context = {
            "title": "New Geologic Map",
            "form": form,
            "error": form.fgdbHandler.errJson
        }
        context.update(csrf(req))
        
        return render_to_response('geomap.jade', context)
    
    
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    
def resources(req, id):
    
    if req.method == 'GET':
        gm = get_object_or_404(GeoMap, pk=id)
        context = {
            "title": gm.name,
            "geomap": gm           
        }
        context.update(csrf(req))
        return render_to_response('geomap-resource.jade', context)
    
    elif req.method == 'POST':
        return HttpResponse("Not implemented yet")
    
    elif req.method == 'PUT':
        return HttpResponse("Not implemented yet")
    
    elif req.method == 'DELETE':
        return HttpResponse("Not implemented yet")
    
def resourceAttributes(req, id, attribute):
    gm = get_object_or_404(GeoMap, pk=id)
    if attribute not in [ field.name for field in GeoMap._meta.fields ]: raise Http404
        
    if req.method == 'GET':
        return HttpResponse("Not implemented yet")
    
    elif req.method == 'POST':
        return HttpResponse("Not implemented yet")
    
    elif req.method == 'PUT':                
        data = [ param for param in req.body.split("&") if param.startswith("value=") ][0]
        data = data.split("=")[1]
        
        if attribute == "is_loaded" and gm.is_loaded == False and data == "true":
            gm.load()
        elif attribute == "fgdb_path":
            return HttpResponseBadRequest("fgdb_path cannot be updated")
        else:
            setattr(gm, attribute, data)
            gm.save()
        
        return HttpResponse('{ "success": true }', content_type="application/json")
    
    elif req.method == 'DELETE':
        return HttpResponse("Not implemented yet")