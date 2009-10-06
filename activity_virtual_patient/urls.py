from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_root}),
                       (r'^$', 'tobaccocessation.activity_virtual_patient.views.root'),
                       (r'^(?P<page_id>\d+)/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.page'),
                       (r'^save/$', 'tobaccocessation.activity_virtual_patient.views.save'),
                       (r'^load/(?P<url>.*)$', 'tobaccocessation.activity_virtual_patient.views.load')
)
