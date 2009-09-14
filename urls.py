from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       # Example:
                       # (r'^tobaccocessation/', include('tobaccocessation.foo.urls')),
                       ('^$','django.views.generic.simple.redirect_to', {'url':'/welcome/'}),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logged_out.html'}),
                       (r'^resources/', include('tobaccocessation.resources.urls')),
                       (r'^welcome/', include('tobaccocessation.welcome.urls')),
                       (r'^assist/', include('tobaccocessation.assist.urls')),
                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
		               (r'^survey/',include('survey.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
        
)
