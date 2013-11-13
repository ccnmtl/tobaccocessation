from django.conf.urls.defaults import patterns, url
import os.path
import django.conf.urls

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    (r'^media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': media_root}),

    (r'^navigate/(?P<page_id>.*)/(?P<patient_id>\d+)/$',
     'tobaccocessation.activity_virtual_patient.views.navigate'),
    (r'^save/(?P<patient_id>\d+)/$',
     'tobaccocessation.activity_virtual_patient.views.save'),
    url(r'^reset/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.reset', name='reset'),
)
