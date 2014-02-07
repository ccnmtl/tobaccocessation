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


@login_required
def results(request, hierarchy, patient_id):
    role_name = request.user.get_profile().role()
    hierarchy = Hierarchy.objects.get(name=role_name)

    user_state = _get_user_state(request)
    ctx = get_base_context(request, 'results',
                           hierarchy, user_state, patient_id)
    request.user.get_profile().set_has_visited([ctx['section']])

    patient_state = user_state['patients'][patient_id]

    #pickup the feedback based on the user's answers
    #query for the treatment option the user selected based
    #on the prescribed drugs grade the user's rx(s)
    to = None
    correct_rx = False
    combination = False
    if (_is_combination(user_state, patient_id)):
        combination = True
        med_tag_one = patient_state['combination'][0]
        med_tag_two = patient_state['combination'][1]

        to = TreatmentOption.objects.get(
            Q(medication_one__tag=med_tag_one) | Q(
                medication_one__tag=med_tag_two),
            Q(medication_two__tag=med_tag_one) | Q(
                medication_two__tag=med_tag_two),
            patient__id=patient_id)

        cc1 = ConcentrationChoice.objects.get(
            id=patient_state[med_tag_one]['concentration'])
        cc2 = ConcentrationChoice.objects.get(
            id=patient_state[med_tag_two]['concentration'])
        dc1 = DosageChoice.objects.get(id=patient_state[med_tag_one]['dosage'])
        dc2 = DosageChoice.objects.get(id=patient_state[med_tag_two]['dosage'])

        correct_rx = cc1.correct and cc2.correct \
            and dc1.correct and dc2.correct
    else:
        med_tag_one = patient_state['prescribe']
        to = TreatmentOption.objects.get(patient__id=patient_id,
                                         medication_one__tag=med_tag_one,
                                         medication_two=None)
        cc1 = ConcentrationChoice.objects.get(
            id=patient_state[med_tag_one]['concentration'])
        dc1 = DosageChoice.objects.get(id=patient_state[med_tag_one]['dosage'])

        correct_rx = cc1.correct and dc1.correct

    #todo - is there a better way to model this?
    if to.classification == TreatmentClassification.objects.get(rank=1):
        #for the best, factor in correct dosage
        tf = TreatmentFeedback.objects.filter(patient__id=patient_id,
                                              classification=to.classification,
                                              correct_dosage=correct_rx)
    elif to.classification == TreatmentClassification.objects.get(rank=3):
        #for the worst, factor in combination
        tf = TreatmentFeedback.objects.filter(patient__id=patient_id,
                                              classification=to.classification,
                                              combination_therapy=combination)
    else:
        tf = TreatmentFeedback.objects.filter(
            patient__id=patient_id, classification=to.classification)

    ctx['feedback'] = tf[0].feedback
    ctx['best_treatment_options'] = TreatmentOptionReasoning.objects.filter(
        patient__id=patient_id, classification__rank=1)
    ctx['reasonable_treatment_options'] = \
        TreatmentOptionReasoning.objects.filter(patient__id=patient_id,
                                                classification__rank=2)
    ctx['ineffective_treatment_options'] = \
        TreatmentOptionReasoning.objects.filter(patient__id=patient_id,
                                                classification__rank=3)
    ctx['harmful_treatment_options'] = TreatmentOptionReasoning.objects.filter(
        patient__id=patient_id, classification__rank=4)
    ctx['previous_url'] = _get_previous_page(hierarchy, 'results',
                                             patient_id, user_state)
    ctx['next_url'] = _get_next_page(hierarchy, 'results',
                                     patient_id, user_state)
    ctx['prescription'] = "Prescription Summary Here"
    ctx['page_number'] = 4

    user_state['patients'][patient_id]['results'] = 'completed'
    _save(request, user_state)

    template = loader.get_template('activity_virtual_patient/results.html')
    return HttpResponse(template.render(ctx))


