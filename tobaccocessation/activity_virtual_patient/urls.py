from django.conf.urls import url
from django.conf.urls import patterns
import os.path

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    (r'^media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': media_root}),
    url(r'^reset/(?P<section_id>\d+)/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.reset', name='reset'),
)
