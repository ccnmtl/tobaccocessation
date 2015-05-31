import os.path

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from registration.backends.default.views import RegistrationView

from tobaccocessation.main.models import CreateAccountForm


admin.autodiscover()

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))

logout_page = (r'^accounts/logout/$',
               'django.contrib.auth.views.logout',
               {'next_page': redirect_after_logout})
admin_logout_page = (r'^accounts/logout/$',
                     'django.contrib.auth.views.logout',
                     {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (r'^accounts/logout/$',
                   'djangowind.views.logout',
                   {'next_page': redirect_after_logout})
    admin_logout_page = (r'^admin/logout/$',
                         'djangowind.views.logout',
                         {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    logout_page,
    admin_logout_page,
    auth_urls,
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

    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm),
        name='registration_register'),

    # override the default urls for pasword
    url(r'^password/change/$',
        auth_views.password_change,
        name='password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        name='password_reset'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),

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

    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),

    (r'^pagetree/', include('pagetree.urls')),

    (r'^pages/(?P<hierarchy>\w+)/edit/(?P<path>.*)$',
     'tobaccocessation.main.views.edit_page'),
    (r'^pages/(?P<hierarchy>\w+)/(?P<path>.*)$',
     'tobaccocessation.main.views.page'),
)
