from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from tobaccocessation.activity_treatment_choice.models import * 

@login_required
def root(request):
    treatments = [ 'patch', 'gum', 'inhaler', 'lozenge', 'nasalspray', 'chantix', 'bupropion', 'combination'  ]
    
    ctx = Context({
       'user': request.user,
       'treatments': treatments,
    })
    
    template = loader.get_template('activity_treatment_choice/treatment.html')
    return HttpResponse(template.render(ctx))

@login_required
def loadstate(request):
    print("loadstate: " + request.user.username)
    
    try: 
        state = ActivityState.objects.get(user=request.user)
        print state
        if (len(state.json) > 0):
            doc = state.json
    except ActivityState.DoesNotExist:
        doc = "{}"
        
    return HttpResponse(doc, 'application/json')
    
@login_required
def savestate(request):
    print("savestate: " + request.user.username)
    
    json = request.POST['json']
    
    try: 
        state = ActivityState.objects.get(user=request.user)
        state.json = json
        state.save()
    except ActivityState.DoesNotExist:
        state = ActivityState.objects.create(user=request.user, json=json)
        
    response = {}
    response['success'] = 1
    print("savestate response: " + simplejson.dumps(response))
        
    return HttpResponse(simplejson.dumps(response), 'application/json')
