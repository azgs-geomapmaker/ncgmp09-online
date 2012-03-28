from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^geomap/$', 'ncgmp.geomap.uploads'),
    (r'^geomap/(?P<id>\d+)/$', 'ncgmp.geomap.resources'),
)