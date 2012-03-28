from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^geomap/$', 'ncgmp.geomaps.views.uploads'),
    (r'^geomap/(?P<id>\d+)/$', 'ncgmp.geomaps.views.resources'),
)