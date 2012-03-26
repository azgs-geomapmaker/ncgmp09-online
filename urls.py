from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^test', 'ncgmp.views.test'),
)