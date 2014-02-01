from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models.query_utils import Q
from django.db.models.signals import pre_save, post_init
from django.dispatch.dispatcher import receiver
from django.utils import simplejson
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
    name = models.CharField(max_length=25)
    description = models.TextField()
    history = models.TextField()
    display_order = models.IntegerField()

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
    CHOOSE_TREATMENT_OPTION = 0
    BEST_TREATMENT_OPTION = 1
    WRITE_PRESCRIPTION = 2
    VIEW_RESULTS = 3

    VIEW_CHOICES = (
        (CHOOSE_TREATMENT_OPTION, 'Treatment Options'),
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

        if self.view == self.CHOOSE_TREATMENT_OPTION:
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
            1 == 0

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

    def unlocked(self, user):
        state = ActivityState.get_for_user(user)
        patient_state = state.data["patients"][str(self.patient.id)]

        if self.view == self.CHOOSE_TREATMENT_OPTION:
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
            return False
        else:
            return True

    def available_treatments(self, user):
        state = ActivityState.get_for_user(user)
        patient_state = state.data["patients"][str(self.patient.id)]
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


class PatientAssessmentForm(forms.ModelForm):
    class Meta:
        model = PatientAssessmentBlock
