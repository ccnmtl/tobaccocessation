from django.conf.urls import url

from tobaccocessation.activity_virtual_patient.views import reset


urlpatterns = [
    url(r'^reset/(?P<section_id>\d+)/(?P<patient_id>\d+)/$',
        reset, name='reset'),
]
