from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def root(request):
    template = loader.get_template('activity_prescription_writing/index.html')
    return HttpResponse(template.render(ctx))