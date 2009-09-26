from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^$','siteeditor.views.index'),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logged_out.html'}),
                       (r'^activity/treatment/', include('tobaccocessation.activity_treatment_choice.urls')),
                       (r'^activity/prescription/', include('tobaccocessation.activity_prescription_writing.urls')),
                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
		               (r'^survey/',include('survey.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
                       (r'^pagetree/',include('pagetree.urls')),
                       
                       (r'^edit/(?P<path>.*)add_child_section/$','siteeditor.views.add_child_section'),
                       (r'^edit/(?P<path>.*)add_textblock/$','siteeditor.views.add_textblock'),
                       (r'^edit/(?P<path>.*)add_imageblock/$','siteeditor.views.add_imageblock'),
                       (r'^edit/(?P<path>.*)add_imagepullquoteblock/$','siteeditor.views.add_imagepullquoteblock'),
                       (r'^edit/(?P<path>.*)add_htmlblock/$','siteeditor.views.add_htmlblock'),
                       (r'^edit/(?P<path>.*)add_pullquoteblock/$','siteeditor.views.add_pullquoteblock'),
                       
                       # very important that these two stay last and in this order
                       (r'^edit/(?P<path>.*)$','siteeditor.views.edit_page'),
                       (r'^(?P<path>.*)$','siteeditor.views.page'),        
)
