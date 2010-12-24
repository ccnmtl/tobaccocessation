from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from tobaccocessation.activity_virtual_patient.urls import *
from tobaccocessation.activity_treatment_choice.urls import *
from tobaccocessation.activity_prescription_writing.urls import *
from quizblock.urls import *
from main.urls import *
from pagetree.urls import *
import djangowind.urls
import survey.urls
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")

login_page = (r'^accounts/',include('django.contrib.auth.urls'))
if hasattr(settings,'WIND_BASE'):
    login_page = (r'^accounts/',include('djangowind.urls'))
redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

urlpatterns = patterns('django.views.generic.simple',
                        (r'^about', 'direct_to_template',{'template':'flatpages/about.html'}),
                        (r'^help', 'direct_to_template',{'template':'flatpages/help.html'}),
                        (r'^contact', 'direct_to_template',{'template':'flatpages/contact.html'}),
                        )

urlpatterns += patterns('',
                       (r'^crossdomain.xml$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.dirname(__file__)), 'path': 'crossdomain.xml'}),
                       (r'^$','main.views.index'),
                       (r'^accounts/logout/$','django.contrib.auth.views.logout', {'next_page': redirect_after_logout}),
                       login_page, #see above
                       
                       (r'^admin/pagetree/',include('pagetree.urls')),
                       (r'^admin/quiz/',include('quizblock.urls')),
                       (r'^admin/(.*)', admin.site.root),
                       
                       (r'^main/', include('main.urls')),
                       (r'^activity/treatment/', include('tobaccocessation.activity_treatment_choice.urls')),
                       (r'^activity/prescription/', include('tobaccocessation.activity_prescription_writing.urls')),
                       (r'^activity/virtualpatient/', include('tobaccocessation.activity_virtual_patient.urls')),
                       (r'^activity/quiz/', include('quizblock.urls')),
                       ('^accounts/',include('djangowind.urls')),
                       
                       (r'^survey/',include('survey.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
                       
                       # completely override pagetree for virtual patient. it's too much to fit it into the structure                       
                       url(r'^assist/activity-virtual-patient/$', 'tobaccocessation.activity_virtual_patient.views.root', name='root'),
                       url(r'^assist/activity-virtual-patient/options/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.options', name='options'),
                       url(r'^assist/activity-virtual-patient/selection/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.selection', name='selection'),
                       url(r'^assist/activity-virtual-patient/prescription/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.prescription', name='prescription'),
                       url(r'^assist/activity-virtual-patient/prescription/(?P<patient_id>\d+)/(?P<medication_idx>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.prescription', name='next_prescription'),
                       url(r'^assist/activity-virtual-patient/results/(?P<patient_id>\d+)/$', 'tobaccocessation.activity_virtual_patient.views.results', name='results'),

                       (r'^pagetree/',include('pagetree.urls')),
                       
                       # very important that this stays last and in this order
                       (r'^edit/(?P<path>.*)$','main.views.edit_page'),
                       (r'^(?P<path>.*)$','main.views.page'),
)