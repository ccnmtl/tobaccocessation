from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import password_change, password_change_done, \
    password_reset, password_reset_done, password_reset_complete, \
    password_reset_confirm
import django.contrib.auth.views
from django.views.generic import TemplateView
from django.views.static import serve
import djangowind.views
from registration.backends.default.views import RegistrationView

from tobaccocessation.main.forms import CreateAccountForm
from tobaccocessation.main.views import (
    index, edit_page, page, create_profile,
)


admin.autodiscover()

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)

auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))

logout_page = url(r'^accounts/logout/$', django.contrib.auth.views.logout,
                  {'next_page': redirect_after_logout})
admin_logout_page = url(r'^accounts/logout/$',
                        django.contrib.auth.views.logout,
                        {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))
    logout_page = url(r'^accounts/logout/$',
                      djangowind.views.logout,
                      {'next_page': redirect_after_logout})
    admin_logout_page = url(r'^admin/logout/$',
                            djangowind.views.logout,
                            {'next_page': redirect_after_logout})


urlpatterns = [
    logout_page,
    admin_logout_page,
    auth_urls,
    url(r'^about/', TemplateView.as_view(
        template_name="flatpages/about.html")),
    url(r'^help/', TemplateView.as_view(
        template_name="flatpages/help.html")),
    url(r'^contact/', TemplateView.as_view(
        template_name="flatpages/contact.html")),
    url(r'^$', index, name="index"),

    # override the default urls for password
    url(r'^password/change/$', password_change,
        name='password_change'),
    url(r'^password/change/done/$', password_change_done,
        name='password_change_done'),
    url(r'^password/reset/$', password_reset,
        name='password_reset'),
    url(r'^password/reset/done/$', password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/complete/$', password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm, name='password_reset_confirm'),

    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm), name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^smoketest/', include('smoketest.urls')),
    url(r'^main/', include('tobaccocessation.main.urls')),

    url(r'^create_profile/', create_profile, name="create_profile"),

    url(r'^activity/virtualpatient/',
        include('tobaccocessation.activity_virtual_patient.urls')),
    url(r'^activity/quiz/', include('quizblock.urls')),
    url(r'^quizblock/', include('quizblock.urls')),

    url(r'^uploads/(?P<path>.*)$',
        serve, {'document_root': settings.MEDIA_ROOT}),

    url(r'^pagetree/', include('pagetree.urls')),

    url(r'^pages/(?P<hierarchy>\w+)/edit/(?P<path>.*)$', edit_page),
    url(r'^pages/(?P<hierarchy>\w+)/(?P<path>.*)$', page),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
