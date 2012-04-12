from django.shortcuts import render_to_response

def termMapping(req, geomapId):
    return render_to_response("terminology/term-mapping.jade", { "geomapId": geomapId })