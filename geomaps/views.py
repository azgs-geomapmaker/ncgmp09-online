from django.shortcuts import render_to_response
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.core.context_processors import csrf
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
            return HttpResponseRedirect("/ncgmp/geomap/" + form.fgdbHandler.newGeoMap.id)
        
        context = {
            "title": "New Geologic Map",
            "form": form,
            "error": form.fgdbHandler.errJson
        }
        context.update(csrf(req))
        
        return render_to_response('geomap.jade', context)
    
    
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])