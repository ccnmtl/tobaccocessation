from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from tobaccocessation.activity_virtual_patient.models import *
from django.utils import simplejson
from django.core.urlresolvers import reverse

@login_required
def root(request):
    # dump the user back where they were when they left
    user_state = _get_user_state(request)
    
    url = '/activity/virtualpatient/%s/%s' % (user_state['current_page'], user_state['current_patient'])
    
    return HttpResponseRedirect(url)

@login_required        
def load(request, page_id, patient_id):
    user_state = _get_user_state(request)
    
    doc = {}
    if patient_id in user_state['patients']:
        doc = user_state['patients'][patient_id]

    # reloading a page, resets the current page state
    user_state['current_page'] = page_id

    stored_state = ActivityState.objects.get(user=request.user)
    stored_state.json = simplejson.dumps(user_state)
    stored_state.save()
    
    return HttpResponse(simplejson.dumps(doc), 'application/json')

@login_required
def save(request, page_id, patient_id):
    _save_user_state(request, page_id, patient_id)
    doc = { 'success': '1' }
    return HttpResponse(simplejson.dumps(doc), 'application/json')
    

@login_required
def navigate(request, page_id, patient_id):
    _save_user_state(request, page_id, patient_id)
    
    next_page = _get_next_page(page_id)
    
    doc = {}
    doc['redirect'] = reverse(next_page, args=[patient_id])
    return HttpResponse(simplejson.dumps(doc), 'application/json')

@login_required
def options(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'medications': Medication.objects.all().order_by('display_order'),
       'page_id': "options",
    })
        
    template = loader.get_template('activity_virtual_patient/options.html')
    return HttpResponse(template.render(ctx))

@login_required
def selection(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'medications': Medication.objects.all().order_by('display_order'),
       'page_id': "selection",
    })
        
    template = loader.get_template('activity_virtual_patient/selection.html')
    return HttpResponse(template.render(ctx))
    
@login_required
def prescription(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'page_id': "prescription",
    })
        
    template = loader.get_template('activity_virtual_patient/prescription.html')
    return HttpResponse(template.render(ctx))

@login_required
def prescription_post(request):
    print "prescription_post" 
    
@login_required
def results(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'medications': Medication.objects.all().order_by('display_order'),
       'page_id': "results",
    })
        
    template = loader.get_template('activity_virtual_patient/results.html')
    return HttpResponse(template.render(ctx))
    
###################################################################################
def _get_user_state(request):
    try:    
        stored_state = ActivityState.objects.get(user=request.user)
    except ActivityState.DoesNotExist:
        # setup the template
        patients = Patient.objects.all().order_by('display_order')
        state = {}
        state['version'] = 1
        state['current_patient'] = patients[0].id
        state['current_page'] = 'options'
        
        blank_patient_state = {}
        for p in patients:
            blank_patient_state[str(p.id)] = {}
        state['patients'] = blank_patient_state
        
        stored_state = ActivityState.objects.create(user=request.user, json=simplejson.dumps(state))

    return simplejson.loads(stored_state.json)

def _save_user_state(request, current_page, patient_id):
    if (len(request.POST['json']) < 1):
        return
    
    user_state = _get_user_state(request)

    # add the posted information to the user_state
    updated_state = simplejson.loads(request.POST['json'])
    for item in updated_state:
        user_state['patients'][patient_id][item] = updated_state[item]
    
    user_state['current_page'] = current_page
    
    stored_state = ActivityState.objects.get(user=request.user)
    stored_state.json = simplejson.dumps(user_state)
    stored_state.save()
    
###################################################################################

def _get_next_page(page_id):
    next_page = ""
    if (page_id == "options"):
        next_page = "selection"
    elif (page_id == "selection"):
        next_page = "prescription"
    elif (page_id == "prescription"):
        next_page = "results"
    return next_page
    