from django.conf.urls.defaults import patterns

urlpatterns = patterns('',    
    (r'^terminology-mapping/(?P<geomapId>\d+)/$', 'ncgmp.ui.views.termMapping'),
    (r'^gm/(?P<gmId>\d+)/js/(?P<fileName>.+)$', 'ncgmp.ui.views.javascript'),
    
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/lith/$', 'ncgmp.dmu.lith.byCollection'),    
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/lith/(?P<lithId>\d+)/$', 'ncgmp.dmu.lith.byResource'),
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/lith/(?P<lithId>\d+)/(?P<lithProp>.+)/$', 'ncgmp.dmu.lith.byAttribute'),
    
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/rep/$', 'ncgmp.dmu.rep.byCollection'),    
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/rep/(?P<repId>\d+)/$', 'ncgmp.dmu.rep.byResource'),
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/rep/(?P<repId>\d+)/(?P<repProp>.+)/$', 'ncgmp.dmu.rep.byAttribute'),
    
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/(?P<qualifier>age|preferredage)/$', 'ncgmp.dmu.age.byCollection'),
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/(?P<qualifier>age|preferredage)/(?P<ageId>\d+)/$', 'ncgmp.dmu.age.byResource'),
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/(?P<qualifier>age|preferredage)/(?P<ageId>\d+)/(?P<ageProp>.+)/$', 'ncgmp.dmu.age.byAttribute'),
    
    (r'^gm/(?P<gmId>\d+)/dmu/$', 'ncgmp.dmu.dmu.byCollection'),
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/$', 'ncgmp.dmu.dmu.byResource'),
    (r'^gm/(?P<gmId>\d+)/dmu/(?P<dmuId>\d+)/(?P<dmuProp>.+)/$', 'ncgmp.dmu.dmu.byAttribute'),
    
    (r'^gm/(?P<gmId>\d+)/geounitview/$', 'ncgmp.gsmlp.geounitview.byCollection'),
    
    (r'^gm/$', 'ncgmp.geomaps.views.byCollection'),
    (r'^gm/(?P<id>\d+)/$', 'ncgmp.geomaps.views.byResource'),
    (r'^gm/(?P<id>\d+)/(?P<attribute>.+)/$', 'ncgmp.geomaps.views.byAttribute'),
    
    (r'^vocab/$', 'ncgmp.vocab.views.vocabCollection'),
    (r'^vocab/(?P<vocabId>\d+)/$', 'ncgmp.vocab.views.vocabResource'),
    (r'^vocab/(?P<vocabId>\d+)/term/$', 'ncgmp.vocab.views.termCollection'),
    (r'^vocab/(?P<vocabId>\d+)/term/(?P<termId>\d+)/$', 'ncgmp.vocab.views.termResource'),
    (r'^vocab/(?P<vocabId>\d+)/update/$', 'ncgmp.vocab.views.updateVocabulary'),
)