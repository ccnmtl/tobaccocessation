from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
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
                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
		               (r'^survey/',include('survey.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
                       
                       
                       # very important that these two stay last and in this order
                       (r'^edit/(?P<path>.*)$','tobaccocessation_main.views.edit_page'),
                       (r'^(?P<path>.*)$','tobaccocessation_main.views.page'),        
)
