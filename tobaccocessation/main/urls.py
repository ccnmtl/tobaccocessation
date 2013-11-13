from django.conf.urls.defaults import patterns
import os.path
import django.conf.urls

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$',
                        'django.views.static.serve',
                        {'document_root': media_root}),
                       )

urlpatterns += patterns(
    'tobaccocessation.main.views',

    (r'^accessible/(?P<section_slug>.*)/$',
     'is_accessible',
     {},
     'is-accessible'),

    (r'^clear/$', 'clear_state', {}, 'clear-state'),
)
