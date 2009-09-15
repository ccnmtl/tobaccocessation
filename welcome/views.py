from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

@login_required
def root(request):
    return render_to_response("welcome/index.html", dict(user=request.user))