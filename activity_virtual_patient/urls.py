from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_root}),
                       (r'^$', 'tobaccocessation.activity_virtual_patient.views.root'),
                       
                       (r'^navigate/(?P<page_id>.*)/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.navigate'),
                       (r'^save/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.save'),
                       
                       url(r'^options/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.options', name='options'),
                       
                       url(r'^selection/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.selection', name='selection'),
                       
                       url(r'^prescription/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.prescription', name='prescription'),
                       url(r'^prescription/(?P<patient_id>\d+)/(?P<medication_idx>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.prescription', name='next_prescription'),
                       
                       url(r'^results/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.results', name='results'),
)
