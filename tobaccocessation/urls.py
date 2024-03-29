from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.views.static import serve
from django_cas_ng import views as cas_views
from registration.backends.default.views import RegistrationView
from tobaccocessation.main.forms import CreateAccountForm
from tobaccocessation.main.views import (
    index, edit_page, page, create_profile,
)


admin.autodiscover()

urlpatterns = [
    url(r'^about/', TemplateView.as_view(
        template_name="flatpages/about.html")),
    url(r'^help/', TemplateView.as_view(
        template_name="flatpages/help.html")),
    url(r'^contact/', TemplateView.as_view(
        template_name="flatpages/contact.html")),
    url(r'^$', index, name="index"),

    url(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm), name='registration_register'),
    path('accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    url(r'^admin/', admin.site.urls),
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
