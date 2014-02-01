# flake8: noqa
from datetime import timedelta, date
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.utils import simplejson
from pagetree.models import Hierarchy
from tobaccocessation.activity_virtual_patient.models import DosageChoice, \
    ConcentrationChoice, Medication, Patient, TreatmentClassification, \
    TreatmentOptionReasoning, TreatmentOption, TreatmentFeedback, ActivityState


#@login_required
#def root(request, hierarchy):
#    first_patient = Patient.objects.get(display_order=1)
#    url = ('/pages/%s/assist/activity-virtual-patient/options/%s/' %
#           (hierarchy, first_patient.id))
#
#    return HttpResponseRedirect(url)
#
#
#@login_required
#def save(request, patient_id):
#    _save_user_state(request, patient_id)
#    doc = {'success': '1'}
#    return HttpResponse(simplejson.dumps(doc), 'application/json')
#
#
#@login_required
#def navigate(request, page_id, patient_id):
#    user_state = _save_user_state(request, patient_id)
#
#    next_url = _get_next_page(request.user.get_profile().role(),
#                              page_id, patient_id, user_state)
#
#    doc = {}
#    doc['redirect'] = next_url
#    return HttpResponse(simplejson.dumps(doc), 'application/json')
#
#
#@login_required
#def reset(request, patient_id):
#    hierarchy = request.user.get_profile().role()
#    user_state = _get_user_state(request)
#    user_state['patients'][patient_id] = {}
#    user_state['patients'][patient_id][
#        'available_treatments'] = _get_available_treatments(
#        request.user.get_profile().role(), True)
#    _save(request, user_state)
#
#    return HttpResponseRedirect(
#        reverse('options', args=[hierarchy, patient_id]))
#
#
#@login_required
#def options(request, hierarchy, patient_id):
#    role_name = request.user.get_profile().role()
#    hierarchy = Hierarchy.objects.get(name=role_name)
#    user_state = _get_user_state(request)
#    ctx = get_base_context(request, 'options',
#                           hierarchy, user_state, patient_id)
#
#    request.user.get_profile().set_has_visited([ctx['section']])
#
#    #setup new state object if the user is seeing this patient
#    #for the first time.
#    if (patient_id not in user_state['patients']):
#        user_state['patients'][patient_id] = {}
#        user_state['patients'][patient_id][
#            'available_treatments'] = _get_available_treatments(
#            request.user.get_profile().role(), True)
#        _save(request, user_state)
#
#    ctx['previous_url'] = _get_previous_page(hierarchy,
#                                             'options',
#                                             patient_id,
#                                             user_state)
#    ctx['patient_state'] = user_state['patients'][patient_id]
#    ctx['navigate'] = True
#    ctx['page_number'] = '1'
#
#    template = loader.get_template('activity_virtual_patient/options.html')
#    return HttpResponse(template.render(ctx))
#
#
#@login_required
#def selection(request, hierarchy, patient_id):
#    role_name = request.user.get_profile().role()
#    hierarchy = Hierarchy.objects.get(name=role_name)
#
#    user_state = _get_user_state(request)
#    ctx = get_base_context(request, 'selection',
#                           hierarchy, user_state, patient_id)
#    request.user.get_profile().set_has_visited([ctx['section']])
#
#    #do a quick check to verify everything is correct in the land of the
#    #patient state
#    if ('prescribe' in user_state['patients'][patient_id] and
#        user_state['patients'][patient_id]['prescribe'] not in
#            user_state['patients'][patient_id]['best_treatment']):
#        #clear the prescribe value out and save it.
#        user_state['patients'][patient_id]['prescribe'] = ''
#        user_state['patients'][patient_id]['combination'] = []
#        _save(request, user_state)
#
#    ctx['previous_url'] = _get_previous_page(
#        hierarchy, 'selection', patient_id, user_state)
#    ctx['medications'] = _get_available_treatments(
#        request.user.get_profile().role(), False)
#    ctx['patient_state'] = user_state['patients'][patient_id]
#    ctx['navigate'] = True
#    ctx['page_number'] = '2'
#    ctx['treatments_to_combine'] = 2
#
#    if 'combination' in user_state['patients'][patient_id]:
#        ctx['treatments_to_combine'] = 2 - len(
#            user_state['patients'][patient_id]['combination'])
#
#    template = loader.get_template('activity_virtual_patient/selection.html')
#    return HttpResponse(template.render(ctx))
#
#
#@login_required
#def prescription(request, hierarchy, patient_id, medication_idx='0'):
#    role_name = request.user.get_profile().role()
#    hierarchy = Hierarchy.objects.get(name=role_name)
#
#    user_state = _get_user_state(request)
#    ctx = get_base_context(request, 'prescription',
#                           hierarchy, user_state, patient_id)
#
#    request.user.get_profile().set_has_visited([ctx['section']])
#
#    idx = int(medication_idx)
#
#    previous_url = _get_previous_page(
#        hierarchy, 'prescription', patient_id, user_state, idx)
#
#    if (_is_combination(user_state, patient_id)):
#        tag = user_state['patients'][patient_id]['combination'][idx]
#    else:
#        tag = user_state['patients'][patient_id]['prescribe']
#
#    medication = Medication.objects.filter(tag=tag)
#
#    #this is an ugly little workaround due to the django template ifequaltag
#    #i was trying to compare a Model.id property with the stored json
#    #selection which is a string by default with no way to cast in the
#    #templates, I have to specifically send down ints to the template to
#    #get this to work. Django's templates may be a little too crippled formy
#    #tastes...
#    dosage_idx = -1
#    concentration_idx = -1
#    dosage2_idx = -1
#    concentration2_idx = -1
#    if (tag in user_state['patients'][patient_id]):
#        rx = user_state['patients'][patient_id][tag]
#        dosage_idx = int(rx['dosage'])
#        concentration_idx = int(rx['concentration'])
#
#        if (medication[0].rx_count > 1):
#            dosage2_idx = int(rx['dosage2'])
#            concentration2_idx = int(rx['concentration2'])
#
#    page_addendum = None
#    if len(medication) > 0:
#        page_addendum = "(%s)" % medication[0].name
#
#    ctx['medication'] = medication
#    ctx['medication_idx'] = medication_idx
#    ctx['previous_url'] = previous_url
#    ctx['dosage_idx'] = dosage_idx
#    ctx['concentration_idx'] = concentration_idx
#    ctx['dosage2_idx'] = dosage2_idx
#    ctx['concentration2_idx'] = concentration2_idx
#    ctx['navigate'] = True
#    ctx['page_number'] = 3
#    ctx['page_addendum'] = page_addendum
#    ctx['next_week'] = date.today() + timedelta(weeks=1)
#    template = loader.get_template(
#        'activity_virtual_patient/prescription.html')
#    return HttpResponse(template.render(ctx))
#
#
#@login_required
#def results(request, hierarchy, patient_id):
#    role_name = request.user.get_profile().role()
#    hierarchy = Hierarchy.objects.get(name=role_name)
#
#    user_state = _get_user_state(request)
#    ctx = get_base_context(request, 'results',
#                           hierarchy, user_state, patient_id)
#    request.user.get_profile().set_has_visited([ctx['section']])
#
#    patient_state = user_state['patients'][patient_id]
#
#    #pickup the feedback based on the user's answers
#    #query for the treatment option the user selected based
#    #on the prescribed drugs grade the user's rx(s)
#    to = None
#    correct_rx = False
#    combination = False
#    if (_is_combination(user_state, patient_id)):
#        combination = True
#        med_tag_one = patient_state['combination'][0]
#        med_tag_two = patient_state['combination'][1]
#
#        to = TreatmentOption.objects.get(
#            Q(medication_one__tag=med_tag_one) | Q(
#                medication_one__tag=med_tag_two),
#            Q(medication_two__tag=med_tag_one) | Q(
#                medication_two__tag=med_tag_two),
#            patient__id=patient_id)
#
#        cc1 = ConcentrationChoice.objects.get(
#            id=patient_state[med_tag_one]['concentration'])
#        cc2 = ConcentrationChoice.objects.get(
#            id=patient_state[med_tag_two]['concentration'])
#        dc1 = DosageChoice.objects.get(id=patient_state[med_tag_one]['dosage'])
#        dc2 = DosageChoice.objects.get(id=patient_state[med_tag_two]['dosage'])
#
#        correct_rx = cc1.correct and cc2.correct \
#            and dc1.correct and dc2.correct
#    else:
#        med_tag_one = patient_state['prescribe']
#        to = TreatmentOption.objects.get(patient__id=patient_id,
#                                         medication_one__tag=med_tag_one,
#                                         medication_two=None)
#        cc1 = ConcentrationChoice.objects.get(
#            id=patient_state[med_tag_one]['concentration'])
#        dc1 = DosageChoice.objects.get(id=patient_state[med_tag_one]['dosage'])
#
#        correct_rx = cc1.correct and dc1.correct
#
#    #todo - is there a better way to model this?
#    if to.classification == TreatmentClassification.objects.get(rank=1):
#        #for the best, factor in correct dosage
#        tf = TreatmentFeedback.objects.filter(patient__id=patient_id,
#                                              classification=to.classification,
#                                              correct_dosage=correct_rx)
#    elif to.classification == TreatmentClassification.objects.get(rank=3):
#        #for the worst, factor in combination
#        tf = TreatmentFeedback.objects.filter(patient__id=patient_id,
#                                              classification=to.classification,
#                                              combination_therapy=combination)
#    else:
#        tf = TreatmentFeedback.objects.filter(
#            patient__id=patient_id, classification=to.classification)
#
#    ctx['feedback'] = tf[0].feedback
#    ctx['best_treatment_options'] = TreatmentOptionReasoning.objects.filter(
#        patient__id=patient_id, classification__rank=1)
#    ctx['reasonable_treatment_options'] = \
#        TreatmentOptionReasoning.objects.filter(patient__id=patient_id,
#                                                classification__rank=2)
#    ctx['ineffective_treatment_options'] = \
#        TreatmentOptionReasoning.objects.filter(patient__id=patient_id,
#                                                classification__rank=3)
#    ctx['harmful_treatment_options'] = TreatmentOptionReasoning.objects.filter(
#        patient__id=patient_id, classification__rank=4)
#    ctx['previous_url'] = _get_previous_page(hierarchy, 'results',
#                                             patient_id, user_state)
#    ctx['next_url'] = _get_next_page(hierarchy, 'results',
#                                     patient_id, user_state)
#    ctx['prescription'] = "Prescription Summary Here"
#    ctx['page_number'] = 4
#
#    user_state['patients'][patient_id]['results'] = 'completed'
#    _save(request, user_state)
#
#    template = loader.get_template('activity_virtual_patient/results.html')
#    return HttpResponse(template.render(ctx))
#
###########################################################################
#
#
#
#def _save(request, user_state):
#    a = ActivityState.objects.filter(user=request.user).order_by('id')
#    stored_state = a[0]
#    stored_state.json = simplejson.dumps(user_state)
#    stored_state.save()
#
#
#def _is_combination(user_state, patient_id):
#    if ('patients' in user_state and
#        patient_id in user_state['patients'] and
#            'prescribe' in user_state['patients'][patient_id]):
#        return user_state['patients'][patient_id]['prescribe'] == 'combination'
#    else:
#        return False
#
###########################################################################
#
#
#def _get_next_page(hierarchy, page_id, patient_id, user_state):
#    next_url = None
#    if (page_id == "options"):
#        next_url = reverse('selection', args=[hierarchy, patient_id])
#    elif (page_id == "selection"):
#        next_url = reverse('prescription', args=[hierarchy, patient_id])
#    elif (page_id == "prescription"):
#        idx = int(user_state['patients'][patient_id]['medication_idx'])
#        if (_is_combination(user_state, patient_id) and idx == 0):
#            next_url = reverse('next_prescription',
#                               args=[hierarchy, patient_id, '1'])
#        else:
#            next_url = reverse('results', args=[hierarchy, patient_id])
#    elif (page_id == 'results'):
#        next_patient = _get_next_patient(patient_id)
#        if (next_patient):
#            next_url = reverse('options', args=[hierarchy, next_patient.id])
#
#    return next_url
#
#
#def _get_previous_page(hierarchy, page_id, patient_id, user_state, idx=-1):
#    previous_url = None
#    if (page_id == 'options'):
#        prev_patient = _get_previous_patient(patient_id)
#        if (prev_patient):
#            previous_url = reverse('results',
#                                   args=[hierarchy, prev_patient.id])
#    elif (page_id == 'selection'):
#        previous_url = reverse('options',
#                               args=[hierarchy, patient_id])
#    elif (page_id == 'prescription'):
#        if (idx == 0):
#            previous_url = reverse('selection',
#                                   args=[hierarchy, patient_id])
#        else:
#            previous_url = reverse('next_prescription',
#                                   args=[hierarchy, patient_id, '0'])
#    elif (page_id == 'results'):
#        if (_is_combination(user_state, patient_id)):
#            previous_url = reverse('next_prescription',
#                                   args=[hierarchy, patient_id, '1'])
#        else:
#            previous_url = reverse('next_prescription',
#                                   args=[hierarchy, patient_id, '0'])
#
#    return previous_url
#
#
#def _get_next_patient(patient_id):
#    try:
#        current_patient = Patient.objects.get(id=patient_id)
#        next_patient = Patient.objects.get(
#            display_order=current_patient.display_order + 1)
#        return next_patient
#    except Patient.DoesNotExist:
#        return None
#
#
#def _get_previous_patient(patient_id):
#    try:
#        current_patient = Patient.objects.get(id=patient_id)
#        next_patient = Patient.objects.get(
#            display_order=current_patient.display_order - 1)
#        return next_patient
#    except Patient.DoesNotExist:
#        return None
#
#
#def _get_available_treatments(role, combination):
#    if role in ['main']:
#        a = ['nicotinepatch', 'nicotinegum', 'nicotineinhaler',
#             'nicotinelozenge', 'nicotinenasalspray', 'varenicline',
#             'bupropion']
#    else:
#        a = ['nicotinepatch', 'nicotinelozenge',
#             'nicotinenasalspray', 'varenicline']
#
#    if (combination):
#        a.append('combination')
#    return a
#
#
#def _get_patients(user_state, patient_id):
#    lst = []
#    for p in Patient.objects.all().order_by('display_order'):
#        patient = {}
#        patient['display_order'] = p.display_order
#        patient['id'] = p.id
#        patient['completed'] = str(p.id) in user_state['patients']
#        patient['selected'] = str(p.id) == patient_id
#        lst.append(patient)
#    return lst
#
###########################################################################
#
#
#def get_base_context(request, page_id,
#                     hierarchy, user_state, patient_id):
#
#    section = hierarchy.get_section_from_path(
#        'assist/activity-virtual-patient')
#
#    ctx = Context({'user': request.user,
#                   'patient': Patient.objects.get(id=patient_id),
#                   'page_id': page_id,
#                   'section': section,
#                   'module': get_module(section),
#                   'root': hierarchy.get_root(),
#                   'request': request,
#                   'patients': _get_patients(user_state, patient_id)})
#
#    return ctx
#
#
#def get_hierarchy():
#    return Hierarchy.objects.get_or_create(name="main",
#                                           defaults=dict(base_url="/"))[0]
#
#
#def get_module(section):
#    """ get the top level module that the section is in"""
#    if section.is_root():
#        return None
#    return section.get_ancestors()[1]
