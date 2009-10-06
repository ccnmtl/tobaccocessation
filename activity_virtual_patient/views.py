from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from tobaccocessation.activity_virtual_patient.models import *
from django.utils import simplejson

@login_required
def root(request):
    # dump the user back where they were when they left
    user_state = get_user_state(request)
    
    url = '/activity/virtualpatient/%s/%s' % (user_state['current_page'], user_state['current_patient'])
    
    return HttpResponseRedirect(url)

@login_required
def save(request):
    json = request.POST['json']
    obj = simplejson.loads(json)
    try:
        state = PageState.objects.get(path=obj['url'])
    except PageState.DoesNotExist:
        state = PageState.objects.create(path=obj['url'])

    state.json = json
    state.save()
    
    response = {}
    response['success'] = True
    return HttpResponse(simplejson.dumps(response), 'application/json')

@login_required        
def load(request, url):
    doc = {}
    try:
        state = PageState.objects.get(path=request.GET['url'])
        doc = state.json
    except PageState.DoesNotExist:
        doc['url'] = request.GET['url']

    return HttpResponse(doc, 'application/json')

@login_required
def page(request, page_id, patient_id):
    page = int(page_id)
    if (page == 1):
        return options(request, patient_id)
    elif (page == 2):
        return selection(request, patient_id) 
    elif (page == 3):
        return prescription(request, patient_id)
    else:
        return results(request, patient_id) 

def options(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'medications': Medication.objects.all().order_by('display_order')
    })
        
    template = loader.get_template('activity_virtual_patient/options.html')
    return HttpResponse(template.render(ctx))

def selection(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
    })
        
    template = loader.get_template('activity_virtual_patient/treatment_options.html')
    return HttpResponse(template.render(ctx))
    
def prescription(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
    })
        
    template = loader.get_template('activity_virtual_patient/treatment_options.html')
    return HttpResponse(template.render(ctx))
    
def results(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
    })
        
    template = loader.get_template('activity_virtual_patient/treatment_options.html')
    return HttpResponse(template.render(ctx))
    
def get_user_state(request):
    try:    
        stored_state = ActivityState.objects.get(user=request.user)
    except ActivityState.DoesNotExist:
        patients = Patient.objects.all().order_by('display_order')
        state = {}
        state['version'] = 1
        state['current_patient'] = patients[0].id
        state['current_page'] = 1
        
        blank_patient_state = {}
        for p in patients:
            blank_patient_state[str(patients[0].id)] = {}
        state['patients'] = blank_patient_state
        
        stored_state = ActivityState.objects.create(user=request.user, json=simplejson.dumps(state))

    return simplejson.loads(stored_state.json)

    