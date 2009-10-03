from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from tobaccocessation.activity_virtual_patient.models import *

@login_required
def treatment_options(request):
    ctx = Context({
       'user': request.user
    })
    
    template = loader.get_template('activity_virtual_patient/treatment_options.html')
    return HttpResponse(template.render(ctx))