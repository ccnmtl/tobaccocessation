import django.views.static
import os.path

from django.conf.urls import url
from tobaccocessation.main.views import (
    is_accessible, clear_state, report,
)

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = [
    url(r'^media/(?P<path>.*)$', django.views.static.serve,
        {'document_root': media_root}),
]

urlpatterns += [
    url(r'^accessible/(?P<section_slug>.*)/$', is_accessible, {},
        'is-accessible'),
    url(r'^clear/$', clear_state, {}, 'clear-state'),
    url(r'^report/$', report, {}, 'report'),
]
