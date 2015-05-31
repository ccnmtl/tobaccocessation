from django.conf.urls import url
from django.conf.urls import patterns


urlpatterns = patterns(
    '',
    url(r'^reset/(?P<section_id>\d+)/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.reset', name='reset'),
)
