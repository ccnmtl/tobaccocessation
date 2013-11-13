from django.conf.urls.defaults import patterns
import os.path
import django.conf.urls

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    (r'^media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': media_root}),
    (r'^load/$',
     'tobaccocessation.activity_treatment_choice.views.loadstate'),
    (r'^save/$',
     'tobaccocessation.activity_treatment_choice.views.savestate')
)
