from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
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
    re_path(r'^about/', TemplateView.as_view(
        template_name="flatpages/about.html")),
    re_path(r'^help/', TemplateView.as_view(
        template_name="flatpages/help.html")),
    re_path(r'^contact/', TemplateView.as_view(
        template_name="flatpages/contact.html")),
    re_path(r'^$', index, name="index"),

    re_path(r'^accounts/register/$', RegistrationView.as_view(
        form_class=CreateAccountForm), name='registration_register'),
    path('accounts/', include('registration.backends.default.urls')),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    re_path(r'^admin/', admin.site.urls),
    re_path(r'^smoketest/', include('smoketest.urls')),
    re_path(r'^main/', include('tobaccocessation.main.urls')),

    re_path(r'^create_profile/', create_profile, name="create_profile"),

    re_path(r'^activity/virtualpatient/',
            include('tobaccocessation.activity_virtual_patient.urls')),
    re_path(r'^activity/quiz/', include('quizblock.urls')),
    re_path(r'^quizblock/', include('quizblock.urls')),

    re_path(r'^uploads/(?P<path>.*)$',
            serve, {'document_root': settings.MEDIA_ROOT}),

    re_path(r'^pagetree/', include('pagetree.urls')),

    re_path(r'^pages/(?P<hierarchy>\w+)/edit/(?P<path>.*)$', edit_page),
    re_path(r'^pages/(?P<hierarchy>\w+)/(?P<path>.*)$', page),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
