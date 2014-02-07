from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.query_utils import Q
from django.db.models.signals import pre_save, post_init
from django.dispatch.dispatcher import receiver
from django.utils import simplejson
from operator import itemgetter
from pagetree.models import PageBlock


class Medication(models.Model):
    name = models.CharField(max_length=25)
    instructions = models.TextField()
    display_order = models.IntegerField()
    tag = models.CharField(max_length=25)
    rx_count = models.IntegerField(default=1)

    class Meta:
        ordering = ['display_order']

    def __unicode__(self):
        return "%s" % (self.name)


class ConcentrationChoice(models.Model):
    medication = models.ForeignKey(Medication)
    concentration = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()


class DosageChoice(models.Model):
    medication = models.ForeignKey(Medication)
    dosage = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()


class RefillChoice(models.Model):
    medication = models.ForeignKey(Medication)
    refill = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()


class Patient(models.Model):
    GENDER_CHOICES = (
        ('F', 'Female'),
        ('M', 'Male')
    )

    name = models.CharField(max_length=25)
    description = models.TextField()
    history = models.TextField()
    display_order = models.IntegerField()
    gender = models.CharField(max_length=1,
                              default='F',
                              choices=GENDER_CHOICES)

    def __unicode__(self):
        return "%s. %s" % (self.display_order, self.name)

    def treatments(self):
        qs = Medication.objects.filter(
            Q(medication_one__patient__id=self.id) |
            Q(medication_two__patient__id=self.id) |
            Q(tag="combination")).distinct().order_by("display_order")
        return qs


class TreatmentClassification(models.Model):
    rank = models.IntegerField()
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s. %s" % (self.rank, self.description)


class TreatmentOption(models.Model):
    patient = models.ForeignKey(Patient)
    classification = models.ForeignKey(TreatmentClassification)
    medication_one = models.ForeignKey(
        Medication, related_name="medication_one")
    medication_two = models.ForeignKey(
        Medication, related_name="medication_two", blank=True, null=True)

    def __unicode__(self):
        return "Option: %s [%s, %s]" % (self.classification.description,
                                        self.medication_one,
                                        self.medication_two)


class TreatmentOptionReasoning(models.Model):
    patient = models.ForeignKey(Patient)
    classification = models.ForeignKey(TreatmentClassification)
    medication = models.ForeignKey(Medication, blank=True, null=True)
    combination = models.BooleanField(blank=True)
    reasoning = models.TextField()
    display_order = models.IntegerField(default=0)

    def __unicode__(self):
        return "OptionReasoning: %s [%s, %s]" % \
            (self.classification.description, self.medication, self.reasoning)


class TreatmentFeedback(models.Model):
    patient = models.ForeignKey(Patient)
    classification = models.ForeignKey(TreatmentClassification)
    correct_dosage = models.BooleanField(blank=True)
    combination_therapy = models.BooleanField(blank=True)
    feedback = models.TextField()

    def __unicode__(self):
        return "Feedback: %s %s" % \
            (self.patient, self.classification.description)


class ActivityState (models.Model):
    user = models.ForeignKey(User, unique=True,
                             related_name="virtual_patient_user")
    json = models.TextField()

    @classmethod
    def get_for_user(cls, user):
        try:
            stored_state = ActivityState.objects.get(user=user)
        except ActivityState.DoesNotExist:
            # setup the template
            state = {}
            state['version'] = 1
            state['patients'] = {}

            stored_state = ActivityState.objects.create(
                user=user, json=simplejson.dumps(state))
        except ActivityState.MultipleObjectsReturned:
            a = ActivityState.objects.filter(user=user).order_by('id')
            stored_state = a[0]

        return stored_state


@receiver(post_init, sender=ActivityState)
def post_init_activity_state(sender, instance, *args, **kwargs):
    instance.data = simplejson.loads(instance.json)


@receiver(pre_save, sender=ActivityState)
def pre_save_activity_state(sender, instance, *args, **kwargs):
    instance.json = simplejson.dumps(instance.data)


class PatientAssessmentBlock(models.Model):
    CLASSIFY_TREATMENTS = 0
    BEST_TREATMENT_OPTION = 1
    WRITE_PRESCRIPTION = 2
    VIEW_RESULTS = 3

    VIEW_CHOICES = (
        (CLASSIFY_TREATMENTS, 'Treatment Options'),
        (BEST_TREATMENT_OPTION, 'Best Treatment Option'),
        (WRITE_PRESCRIPTION, 'Prescription'),
        (VIEW_RESULTS, 'Results')
    )

    pageblocks = generic.GenericRelation(PageBlock)
    patient = models.ForeignKey(Patient)
    view = models.IntegerField(choices=VIEW_CHOICES)

    template_file = "activity_virtual_patient/patient.html"
    css_template_file = "activity_virtual_patient/patient_css.html"
    js_template_file = "activity_virtual_patient/patient_js.html"
    display_name = "Virtual Patient"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return self.view != 'RS'

    def clear_user_submissions(self, user):
        state = ActivityState.get_for_user(user)
        state.data['patients'][self.patient.id] = {}
        state.save()

    def submit(self, user, data):
        state = ActivityState.get_for_user(user)

        if self.view == self.CLASSIFY_TREATMENTS:
            state.data['patients'][self.patient.id] = {}
            for k in data.keys():
                state.data['patients'][self.patient.id][k] = {}
                state.data['patients'][self.patient.id][k][
                    'classification'] = data[k]
        elif self.view == self.BEST_TREATMENT_OPTION:
            patient_state = state.data["patients"][str(self.patient.id)]
            patient_state[data['prescribe']]['prescribe'] = 'true'
            for k in data.keys():
                if k == 'prescribe':
                    patient_state[data[k]][k] = 'true'
                elif k == 'combination':
                    for m in data[k]:
                        patient_state[m][k] = 'true'
        elif self.view == self.WRITE_PRESCRIPTION:
            patient_state = state.data["patients"][str(self.patient.id)]
            for key, value in data.items():
                field, med_id = key.split('-')  # fieldname-medicine_id
                medicine = Medication.objects.get(id=med_id)
                if 'rx' not in patient_state[medicine.tag]:
                    patient_state[medicine.tag]['rx'] = {}
                if med_id not in patient_state[medicine.tag]['rx']:
                    patient_state[medicine.tag]['rx'][med_id] = {}
                patient_state[medicine.tag]['rx'][med_id][field] = value

        state.save()

        return True

    def redirect_to_self_on_submit(self):
        return False

    @classmethod
    def add_form(self):
        return PatientAssessmentForm()

    def edit_form(self):
        return PatientAssessmentForm(instance=self)

    @classmethod
    def create(self, request):
        form = PatientAssessmentForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = PatientAssessmentForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def _patient_state(self, state):
        patient_id = str(self.patient.id)
        if patient_id not in state.data["patients"]:
            state.data["patients"][patient_id] = {}
        return state.data["patients"][patient_id]

    def unlocked(self, user):
        state = ActivityState.get_for_user(user)
        patient_state = self._patient_state(state)

        if self.view == self.CLASSIFY_TREATMENTS:
            return (len(self.patient.treatments()) ==
                    len(patient_state.keys()))
        elif self.view == self.BEST_TREATMENT_OPTION:
            prescribe = None
            combination = 0
            for key in patient_state.keys():
                if 'prescribe' in patient_state[key]:
                    prescribe = key
                if 'combination' in patient_state[key]:
                    combination += 1

            return (prescribe is not None and
                    (prescribe != 'combination' or
                     combination == 2))
        elif self.view == self.WRITE_PRESCRIPTION:
            medications = self.medications(user)
            for med in medications:
                if len(med['choices']) != med['rx_count']:
                    return False
                for choice in med['choices']:
                    if (not hasattr(choice, 'selected_dosage') or
                            not hasattr(choice, 'selected_concentration')):
                        return False
            return True
        else:
            return True

    def available_treatments(self, user):
        state = ActivityState.get_for_user(user)
        patient_state = self._patient_state(state)
        qs = self.patient.treatments()

        lst = list(qs)
        for med in lst:
            if med.tag in patient_state:
                setattr(med, "classification",
                        patient_state[med.tag]["classification"])
                if "prescribe" in patient_state[med.tag]:
                    setattr(med, "prescribe", "true")
                if "combination" in patient_state[med.tag]:
                    setattr(med, "combination", "true")
        return lst

    def medications(self, user):
        state = ActivityState.get_for_user(user)
        patient_state = self._patient_state(state)

        medications = []
        for key, value in patient_state.items():
            if (key != 'combination' and
                    ('combination' in value or 'prescribe' in value)):
                qs = Medication.objects.filter(
                    tag=key).order_by("display_order")
                context = {'rx_count': len(qs),
                           'name': qs[0].name,
                           'tag': qs[0].tag,
                           'display_order': qs[0].display_order,
                           'choices': []}
                for med in qs:
                    if 'rx' in value:
                        setattr(med, "selected_concentration",
                                int(value['rx'][str(med.id)]['concentration']))
                        setattr(med, "selected_dosage",
                                int(value['rx'][str(med.id)]['dosage']))
                    context['choices'].append(med)
                medications.append(context)

        return sorted(medications, key=itemgetter('display_order'))

    def feedback(self, user):
        medications = self.medications(user)
        combination = len(medications) == 2

        # "Correct" the concentration & dosage choices
        correct_rx = True
        medication_ids = []
        for medicine in medications:
            for choice in medicine['choices']:
                cc = choice.concentrationchoice_set.get(correct=True)
                dosage = choice.dosagechoice_set.get(correct=True)

                if (choice.selected_concentration != cc.id or
                        choice.selected_dosage != dosage.id):
                    correct_rx = False

                medication_ids.append(choice.id)

        # Find the treatment option associated with the prescribed medications
        to = TreatmentOption.objects.filter(patient__id=self.patient.id)
        if combination:
            to = to.get(medication_one__id__in=medication_ids,
                        medication_two__id__in=medication_ids)
        else:
            to = to.get(medication_one__id__in=medication_ids,
                        medication_two__isnull=True)

        tf = TreatmentFeedback.objects.filter(patient__id=self.patient.id,
                                              classification=to.classification)

        if to.classification.rank == 1:
            # For the best, factor in correct dosage
            tf = tf.get(correct_dosage=correct_rx)
        else:  # for ineffective + harmful factor in combination
            tf = tf.get(combination_therapy=combination)

        return tf


class PatientAssessmentForm(forms.ModelForm):
    class Meta:
        model = PatientAssessmentBlock
