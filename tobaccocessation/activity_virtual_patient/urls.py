from django.urls import re_path

from tobaccocessation.activity_virtual_patient.views import reset


urlpatterns = [
    re_path(r'^reset/(?P<section_id>\d+)/(?P<patient_id>\d+)/$',
            reset, name='reset'),
]
