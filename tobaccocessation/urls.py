from django.conf import settings
import django.conf.urls
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView
from django.contrib import admin
import os.path
admin.autodiscover()
from registration.backends.default.views import RegistrationView
from tobaccocessation.main.views import CreateAccountForm

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

login_page = (r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'WIND_BASE'):
    login_page = (r'^accounts/', include('djangowind.urls'))
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (
        r'^accounts/logout/$',
        'djangowind.views.logout',
        {'next_page': '/'})
redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
#auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))



urlpatterns = patterns('',#'django.views.generic.simple',
                      (r'^about/', TemplateView.as_view(template_name="flatpages/about.html")),
                      (r'^help/', TemplateView.as_view(template_name="flatpages/help.html")),
                      (r'^contact/', TemplateView.as_view(template_name="flatpages/contact.html")),
                      )

urlpatterns += patterns(
    '',
    (r'^crossdomain.xml$',
     'django.views.static.serve',
     {'document_root': os.path.abspath(os.path.dirname(__file__)),
      'path': 'crossdomain.xml'}),
    (r'^$', 'tobaccocessation.main.views.index'),
    (r'^accounts/logout/$',
     'django.contrib.auth.views.logout',
     {'next_page': redirect_after_logout}),
    login_page,  # see above
    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm),
        name='registration_register'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^smoketest/', include('smoketest.urls')),
    (r'^main/', include('tobaccocessation.main.urls')),
    (r'^activity/treatment/', include(
        'tobaccocessation.activity_treatment_choice.urls')),
    (r'^activity/prescription/',
     include('tobaccocessation.activity_prescription_writing.urls')),
    (r'^activity/virtualpatient/',
     include('tobaccocessation.activity_virtual_patient.urls')),
    (r'^activity/quiz/', include('quizblock.urls')),
    (r'^quizblock/',
     include('quizblock.urls')),
    #('^accounts/', include('djangowind.urls')),

    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),

    # completely override pagetree for virtual patient. it's
    # too much to fit it into the structure
    url(r'^assist/activity-virtual-patient/$',
        'tobaccocessation.activity_virtual_patient.views.root', name='root'),
    url(r'^assist/activity-virtual-patient/options/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.options',
        name='options'),
    url(r'^assist/activity-virtual-patient/selection/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.selection',
        name='selection'),
    url(r'^assist/activity-virtual-patient/prescription/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.prescription',
        name='prescription'),
    url(r'^assist/activity-virtual-patient/prescription/'
        '(?P<patient_id>\d+)/(?P<medication_idx>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.prescription',
        name='next_prescription'),
    url(r'^assist/activity-virtual-patient/results/(?P<patient_id>\d+)/$',
        'tobaccocessation.activity_virtual_patient.views.results',
        name='results'),

    (r'^pagetree/', include('pagetree.urls')),

    # resources path -- content that's open by default
    (r'^edit/resources/(?P<path>.*)$',
     'tobaccocessation.main.views.edit_resources'),
    (r'^resources/(?P<path>.*)$',
     'tobaccocessation.main.views.resources'),

    # very important that this stays last and in this order
    (r'^edit/(?P<path>.*)$', 'tobaccocessation.main.views.edit_page'),
    (r'^(?P<path>.*)$', 'tobaccocessation.main.views.page'),
)
