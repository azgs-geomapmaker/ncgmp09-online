import urllib2, urllib, urlparse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotAllowed

def proxy_response_cors_headers(response, methods):
    # Give it CORS headers
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = ','.join(methods)
    response['Access-Control-Allow-Headers'] = 'content-type,x-requested-with'
    
    return response

@csrf_exempt
def proxy(request):        
    method = request.META['REQUEST_METHOD']
    
    if method in ["POST", "GET"]:
        url = request.GET.get('url', "http://catalog.usgin.org")
        if request.GET.__len__ > 1:
            for param in request.GET:
                if param != 'url':
                    url += "&" + param + "=" + request.GET.get(param)
    elif method in ["OPTIONS"]:
        response = HttpResponse("OK", status=200, mimetype="text/plain")
        return proxy_response_cors_headers(response, ['GET','POST', 'OPTIONS'])
    else:
        return HttpResponseNotAllowed(['GET','POST', 'OPTIONS'])
    
    try:
        if method == "POST":                        
            headers = {'CONTENT-LENGTH': request.META['CONTENT_LENGTH'],
                       'CONTENT-TYPE': request.META.get('CONTENT_TYPE', 'text/plain')}
            
            body = request.raw_post_data
            r = urllib2.Request(url, body, headers)
            y = urllib2.urlopen(r)
        else:
            parsedUrl = urlparse.urlparse(url)
            urlBase = urlparse.urlunparse((parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path, None, None, None))
            query = urlparse.parse_qsl(parsedUrl.query)
            encodedQuery = urllib.urlencode(query)
            
            y = urllib2.urlopen(urlBase, encodedQuery)
        
        # print content type header
        response = HttpResponse(y.read())
        i = y.info()
        if i.has_key("Content-Type"):
            response['Content-Type'] = i["Content-Type"]
        else:
            response['Content-Type'] = "text/plain"
        
        y.close()
        
        return proxy_response_cors_headers(response, ['GET','POST', 'OPTIONS'])

    except Exception, E:
        return HttpResponse("Some unexpected error occurred. Error text was:" + str(E), status=500)      
