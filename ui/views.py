from django.shortcuts import render_to_response

def termMapping(req, geomapId):
    return render_to_response("term-mapping.jade", { "geomapId": geomapId })