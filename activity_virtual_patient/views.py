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
    user_state = get_user_state(request)
    
    url = '/activity/virtualpatient/%s/%s' % (user_state['current_page'], user_state['current_patient'])
    
    return HttpResponseRedirect(url)

@login_required        
def load(request, page_id, patient_id):
    user_state = get_user_state(request)
    
    doc = {}
    if patient_id in user_state['patients']:
        doc = user_state['patients'][patient_id]

    print simplejson.dumps(doc)
    return HttpResponse(simplejson.dumps(doc), 'application/json')

@login_required
def post(request, page_id, patient_id):
    page = int(page_id)
    next_page = page + 1
    
    user_state = get_user_state(request)

    # add the posted information to the user_state
    updated_state = simplejson.loads(request.POST['json'])
    for item in updated_state:
        user_state['patients'][patient_id][item] = updated_state[item]
    
    user_state['current_page'] = next_page
    
    save_user_state(request, user_state)
    
    doc = {}
    doc['redirect'] = reverse('virtual_patient_page', args=[str(next_page), patient_id])
    return HttpResponse(simplejson.dumps(doc), 'application/json')

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
       'medications': Medication.objects.all().order_by('display_order'),
       'page_id': "1",
    })
        
    template = loader.get_template('activity_virtual_patient/options.html')
    return HttpResponse(template.render(ctx))

def selection(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'medications': Medication.objects.all().order_by('display_order'),
       'page_id': "2",
    })
        
    template = loader.get_template('activity_virtual_patient/selection.html')
    return HttpResponse(template.render(ctx))
    
def prescription(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'page_id': 3,
    })
        
    template = loader.get_template('activity_virtual_patient/prescription.html')
    return HttpResponse(template.render(ctx))
    
def results(request, patient_id):
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'medications': Medication.objects.all().order_by('display_order'),
       'page_id': 4,
    })
        
    template = loader.get_template('activity_virtual_patient/results.html')
    return HttpResponse(template.render(ctx))
    
def get_user_state(request):
    try:    
        stored_state = ActivityState.objects.get(user=request.user)
    except ActivityState.DoesNotExist:
        # setup the template
        patients = Patient.objects.all().order_by('display_order')
        state = {}
        state['version'] = 1
        state['current_patient'] = patients[0].id
        state['current_page'] = 1
        
        blank_patient_state = {}
        for p in patients:
            blank_patient_state[str(p.id)] = {}
        state['patients'] = blank_patient_state
        
        stored_state = ActivityState.objects.create(user=request.user, json=simplejson.dumps(state))

    return simplejson.loads(stored_state.json)

def save_user_state(request, new_user_state):
    stored_state = ActivityState.objects.get(user=request.user)
    stored_state.json = simplejson.dumps(new_user_state)
    stored_state.save()
    