from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.views.generic import TemplateView
from registration.backends.default.views import RegistrationView
from tobaccocessation.main.models import CreateAccountForm
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'WIND_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))

urlpatterns = patterns(
    '',
    (r'^crossdomain.xml$',
     'django.views.static.serve',
     {'document_root': os.path.abspath(os.path.dirname(__file__)),
      'path': 'crossdomain.xml'}),
    (r'^about/',
     TemplateView.as_view(template_name="flatpages/about.html")),
    (r'^help/',
     TemplateView.as_view(template_name="flatpages/help.html")),
    (r'^contact/',
     TemplateView.as_view(template_name="flatpages/contact.html")),
    url(r'^$', 'tobaccocessation.main.views.index', name="index"),

    auth_urls,

    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm),
        name='registration_register'),

    (r'^accounts/', include('registration.backends.default.urls')),

    (r'^admin/', include(admin.site.urls)),
    (r'^smoketest/', include('smoketest.urls')),
    (r'^main/', include('tobaccocessation.main.urls')),

    url(r'^create_profile/',
        'tobaccocessation.main.views.create_profile',
        name="create_profile"),

    (r'^activity/prescription/',
     include('tobaccocessation.activity_prescription_writing.urls')),
    (r'^activity/virtualpatient/',
     include('tobaccocessation.activity_virtual_patient.urls')),
    (r'^activity/quiz/', include('quizblock.urls')),
    (r'^quizblock/',
     include('quizblock.urls')),

    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),

    (r'^pagetree/', include('pagetree.urls')),

    (r'^pages/(?P<hierarchy>\w+)/edit/(?P<path>.*)$',
     'tobaccocessation.main.views.edit_page'),
    (r'^pages/(?P<hierarchy>\w+)/(?P<path>.*)$',
     'tobaccocessation.main.views.page'),
)
