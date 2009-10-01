from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django import forms
from tobaccocessation.activity_prescription_writing.models import * 
from django.utils import simplejson
    
@login_required
def rx(request, ordinal=None):

    try:    
        user_state = ActivityState.objects.get(user=request.user)
    except ActivityState.DoesNotExist:
        state = {}
        state['current_medication_ordinal'] = 1
        user_state = ActivityState.objects.create(user=request.user, json=simplejson.dumps(state))
        
    json_state_object = simplejson.loads(user_state.json)
        
    if (ordinal==None):
        # figure out what medicine they're currently on
        ordinal = json_state_object['current_medication_ordinal']
        
    try:
        current_medication = Medication.objects.filter(sort_order=ordinal).order_by('id')
    except Medication.DoesNotExist:
        current_medication = None
    
    try:
        prev_ordinal = int(ordinal) - 1
        prev = Medication.objects.filter(sort_order=prev_ordinal).order_by('id')
    except Medication.DoesNotExist:
        prev = None
    
    try:
        next_ordinal = int(ordinal) + 1
        next = Medication.objects.filter(sort_order=next_ordinal).order_by('id')
    except Medication.DoesNotExist:
        next = None
        
    ctx = Context({
       'user': request.user,
       'current_medication': current_medication, # at least one, sometimes two
       'multiple': current_medication.count > 1,
       'next': next,
       'prev': prev
    })
    
    template = 'activity_prescription_writing/blank_prescription.html'
    medication_state = None
        
    if request.method == 'POST':
        # store the medication_state given, then redisplay the form with the correct answers.
        template = 'activity_prescription_writing/prescription.html'
        if current_medication[0].name in json_state_object:
            medication_state = json_state_object[current_medication[0].name]
        else:
            medication_state = {}
        
        medication_state['dosage'] = request.POST.get('dosage')
        medication_state['disp'] = request.POST.get('disp')
        medication_state['sig'] = request.POST.get('sig')
        medication_state['refills'] = request.POST.get('refills')
        medication_state['dosage_2'] = request.POST.get('dosage_2')
        medication_state['disp_2'] = request.POST.get('disp_2')
        medication_state['sig_2'] = request.POST.get('sig_2')
        medication_state['refills_2'] = request.POST.get('refills_2')
             
        json_state_object[current_medication[0].name] = medication_state
        json_state_object['current_medication_ordinal'] = current_medication[0].sort_order
        
        user_state.json = simplejson.dumps(json_state_object)
        user_state.save()
    elif current_medication[0].name in json_state_object:
        template = 'activity_prescription_writing/prescription.html'
        medication_state = json_state_object[current_medication[0].name]
        
    if medication_state:
        ctx['dosage'] = medication_state['dosage']
        ctx['disp'] = medication_state['disp']
        ctx['sig'] = medication_state['sig']
        ctx['refills'] = medication_state['refills']
        ctx['dosage_2'] = medication_state['dosage_2']
        ctx['disp_2'] = medication_state['disp_2']
        ctx['sig_2'] = medication_state['sig_2']
        ctx['refills_2'] = medication_state['refills_2']
        
    template = loader.get_template(template)
    return HttpResponse(template.render(ctx))

