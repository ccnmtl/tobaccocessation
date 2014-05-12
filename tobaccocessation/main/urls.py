from django.conf.urls import patterns
import os.path

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$',
                        'django.views.static.serve',
                        {'document_root': media_root}),
                       )

urlpatterns += patterns(
    'tobaccocessation.main.views',
    #(r'^profile/$', 'create_profile'),
    (r'^accessible/(?P<section_slug>.*)/$',
     'is_accessible', {}, 'is-accessible'),

    (r'^clear/$', 'clear_state', {}, 'clear-state'),

    (r'^report/$', 'report', {}, 'report'),
)
