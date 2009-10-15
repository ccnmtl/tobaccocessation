from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from tobaccocessation.activity_virtual_patient.models import *
from django.utils import simplejson
from django.core.urlresolvers import reverse
from StdSuites.Type_Names_Suite import null

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
def prescription(request, patient_id, medication_idx='0'):
    user_state = _get_user_state(request)
    idx = int(medication_idx)
    
    if (idx == 0):
        previous_url = reverse('selection', args=[patient_id])
    else:
        previous_url = reverse('next_prescription', args=[patient_id, '0'])
        
    if (_is_combination(user_state, patient_id)):
        tag = user_state['patients'][patient_id]['combination'][idx]
    else:
        tag = user_state['patients'][patient_id]['prescribe']
        
    medication = Medication.objects.get(tag=tag)
    
    # this is an ugly little workaround due to the django template ifequal tag
    # i was trying to compare a Model.id property with the stored json selection which is a string by default
    # with no way to cast in the templates, I have to specifically send down ints to the template to 
    # get this to work. Django's templates may be a little too crippled for my tastes...
    dosage_idx = -1
    concentration_idx = -1
    refill_idx = -1
    if (user_state['patients'][patient_id].has_key(tag)):
        rx = user_state['patients'][patient_id][tag]
        dosage_idx = int(rx['dosage'])
        concentration_idx = int(rx['concentration'])
        if (rx.has_key('refill')):
            refill_idx = int(rx['refill'])
    
    ctx = Context({
       'user': request.user,
       'patient': Patient.objects.get(id=patient_id),
       'page_id': "prescription",
       'medication': medication,
       'medication_idx': medication_idx,
       'previous_url': previous_url,
       'dosage_idx': dosage_idx,
       'concentration_idx': concentration_idx,
       'refill_idx': refill_idx,
    })
        
    template = loader.get_template('activity_virtual_patient/prescription.html')
    return HttpResponse(template.render(ctx))


@login_required
def prescription_post(request):
    user_state = _get_user_state(request)
    update = simplejson.loads(request.POST['json'])
    patient_id = update['patient_id']
    
    # save the data out
    medication_tag = update['medication_tag']
    user_state['patients'][patient_id][medication_tag] = update[medication_tag]
    _save(request, user_state)
    
    # navigate to the next view
    idx = int(update['medication_idx'])
    if (_is_combination(user_state, patient_id) and idx == 0):
        next_url = reverse('next_prescription', args=[patient_id, '1'])
    else:
        next_url = reverse('results', args=[patient_id])
            
    doc = {}
    doc['redirect'] = next_url
    return HttpResponse(simplejson.dumps(doc), 'application/json')
    
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
    _save(request, user_state)
    
def _save(request, user_state):
    stored_state = ActivityState.objects.get(user=request.user)
    stored_state.json = simplejson.dumps(user_state)
    stored_state.save()
    
def _is_combination(user_state, patient_id):
    return user_state['patients'][patient_id]['prescribe'] == 'combination'
    
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
    