from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from tobaccocessation.activity_virtual_patient.urls import *
from tobaccocessation.activity_treatment_choice.urls import *
from tobaccocessation.activity_prescription_writing.urls import *
from tobaccocessation.quiz.urls import *
from pagetree.urls import *
import djangowind.urls
import survey.urls
import os.path
admin.autodiscover()


site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^$','tobaccocessation_main.views.index'),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logged_out.html'}),
                       (r'^pagetree/',include('pagetree.urls')),
                       (r'^activity/treatment/', include('tobaccocessation.activity_treatment_choice.urls')),
                       (r'^activity/prescription/', include('tobaccocessation.activity_prescription_writing.urls')),
                       (r'^activity/virtualpatient/', include('tobaccocessation.activity_virtual_patient.urls')),
                       (r'^quiz/', include('tobaccocessation.quiz.urls')),
                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
		               (r'^survey/',include('survey.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
                       
                       url(r'^welcome/$', 'tobaccocessation_main.views.welcome', name='welcome'),
                       url(r'^resources/$', 'tobaccocessation_main.views.resources', name='resources'),
                       
                       

                       # completely override pagetree for virtual patient. it's too much to fit it into the structure                       
                       url(r'^assist/activity-virtual-patient/$', 'tobaccocessation.activity_virtual_patient.views.root', name='root'),
                       url(r'^assist/activity-virtual-patient/options/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.options', name='options'),
                       url(r'^assist/activity-virtual-patient/selection/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.selection', name='selection'),
                       url(r'^assist/activity-virtual-patient/prescription/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.prescription', name='prescription'),
                       url(r'^assist/activity-virtual-patient/prescription/(?P<patient_id>\d+)/(?P<medication_idx>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.prescription', name='next_prescription'),
                       url(r'^assist/activity-virtual-patient/results/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.results', name='results'),

                       # very important that these two stay last and in this order
                       (r'^edit/(?P<path>.*)$','tobaccocessation_main.views.edit_page'),
                       (r'^(?P<path>.*)$','tobaccocessation_main.views.page'),
)
