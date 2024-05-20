import django.views.static
import os.path

from django.urls import re_path
from tobaccocessation.main.views import (
    is_accessible, clear_state, report,
)

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', django.views.static.serve,
            {'document_root': media_root}),
]

urlpatterns += [
    re_path(r'^accessible/(?P<section_slug>.*)/$', is_accessible, {},
            'is-accessible'),
    re_path(r'^clear/$', clear_state, {}, 'clear-state'),
    re_path(r'^report/$', report, {}, 'report'),
]
