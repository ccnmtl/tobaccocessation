from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_root}),
                       (r'^$', 'tobaccocessation.activity_virtual_patient.views.root'),
                       url(r'^(?P<page_id>\d+)/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.page', name='virtual_patient_page'),
                       (r'^post/(?P<page_id>\d+)/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.post'),
                       (r'^save/(?P<page_id>\d+)/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.save'),
                       (r'^load/(?P<page_id>\d+)/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.load')
)
