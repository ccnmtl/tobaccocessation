from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django import forms
from tobaccocessation.activity_prescription_writing.models import * 
from django.utils import simplejson

@login_required
def loadstate(request):
    try: 
        state = ActivityState.objects.get(user=request.user)
        if (len(state.json) > 0):
            doc = state.json
    except ActivityState.DoesNotExist:
        doc = "{}"

    response = HttpResponse(doc, 'application/json')
    response['Cache-Control']='max-age=0,no-cache,no-store'        
    return response
    
@login_required
def savestate(request):
    json = request.POST['json']
    update = simplejson.loads(json)
    
    try: 
        state = ActivityState.objects.get(user=request.user)
        
        obj = simplejson.loads(state.json)
        for item in update:
            obj[item] = update[item]
        
        state.json = simplejson.dumps(obj)
        state.save()
    except ActivityState.DoesNotExist:
        state = ActivityState.objects.create(user=request.user, json=json)
        
    response = {}
    response['success'] = 1
        
    return HttpResponse(simplejson.dumps(response), 'application/json')
