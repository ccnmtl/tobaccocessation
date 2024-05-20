from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.db.models.query_utils import Q
from django.db.models.signals import pre_save, post_init
from django.dispatch.dispatcher import receiver
import json
from operator import itemgetter
from pagetree.models import PageBlock, Hierarchy


class Medication(models.Model):
    name = models.CharField(max_length=25)
    instructions = models.TextField()
    display_order = models.IntegerField()
    tag = models.CharField(max_length=25)
    rx_count = models.IntegerField(default=1)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return "%s" % (self.name)


class ConcentrationChoice(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    concentration = models.CharField(max_length=50)
    correct = models.BooleanField(default=False)
    display_order = models.IntegerField()


class DosageChoice(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=50)
    correct = models.BooleanField(default=False)
    display_order = models.IntegerField()


class RefillChoice(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    refill = models.CharField(max_length=50)
    correct = models.BooleanField(default=False)
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

    def __str__(self):
        return "%s. %s" % (self.display_order, self.name)

    def treatments(self):
        qs = Medication.objects.filter(
            Q(medication_one__patient__id=self.id) |
            Q(medication_two__patient__id=self.id) |
            Q(tag="combination")).distinct().order_by("display_order")
        return qs

    def appropriate_treatment_options(self):
        return self.treatmentoptionreasoning_set.filter(classification__rank=1)

    def less_appropriate_treatment_options(self):
        opts = self.treatmentoptionreasoning_set.filter(classification__rank=2)
        return opts

    def harmful_treatment_options(self):
        return self.treatmentoptionreasoning_set.filter(classification__rank=3)


class TreatmentClassification(models.Model):
    rank = models.IntegerField()
    description = models.CharField(max_length=50)

    def __str__(self):
        return "%s. %s" % (self.rank, self.description)

    @classmethod
    def value_to_rank(cls, value):
        if value == 'appropriate':
            return 1
        if value == 'ineffective':
            return 2
        if value == 'harmful':
            return 3


class TreatmentOption(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    classification = models.ForeignKey(TreatmentClassification,
                                       on_delete=models.CASCADE)
    medication_one = models.ForeignKey(
        Medication, related_name="medication_one",
        on_delete=models.CASCADE)
    medication_two = models.ForeignKey(
        Medication, related_name="medication_two", blank=True, null=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return "Option: %s [%s, %s]" % (self.classification.description,
                                        self.medication_one,
                                        self.medication_two)


class TreatmentOptionReasoning(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    classification = models.ForeignKey(TreatmentClassification,
                                       on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, blank=True, null=True,
                                   on_delete=models.CASCADE)
    combination = models.BooleanField(blank=True, default=False)
    reasoning = models.TextField()
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return "OptionReasoning: %s [%s, %s]" % \
            (self.classification.description, self.medication, self.reasoning)

    class Meta:
        ordering = ['display_order', 'id']


class TreatmentFeedback(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    classification = models.ForeignKey(TreatmentClassification,
                                       on_delete=models.CASCADE)
    correct_dosage = models.BooleanField(blank=True, default=False)
    combination_therapy = models.BooleanField(blank=True, default=False)
    feedback = models.TextField()

    def __str__(self):
        return "Feedback: %s %s" % \
            (self.patient, self.classification.description)


class ActivityState (models.Model):
    user = models.ForeignKey(User,
                             related_name="virtual_patient_user",
                             on_delete=models.CASCADE)
    hierarchy = models.ForeignKey(Hierarchy, on_delete=models.CASCADE)
    json = models.TextField()

    class Meta:
        unique_together = (("user", "hierarchy"),)

    @classmethod
    def get_for_user(cls, user, hierarchy):
        try:
            stored_state = ActivityState.objects.get(user=user,
                                                     hierarchy=hierarchy)
        except ActivityState.DoesNotExist:
            # setup the template
            state = {}
            state['patients'] = {}

            stored_state = ActivityState.objects.create(
                user=user, hierarchy=hierarchy, json=json.dumps(state))

        return stored_state

    @classmethod
    def clear_for_user(cls, user, hierarchy, patient_id):
        state = ActivityState.objects.get(user=user, hierarchy=hierarchy)
        state.data['patients'][patient_id] = {}
        state.save()

    def patient_state(self, patient):
        patient_id = str(patient.id)
        if patient_id not in self.data["patients"]:
            self.data["patients"][patient_id] = {}
        return self.data["patients"][patient_id]

    def save_patient_state(self, patient, data):
        self.data["patients"][str(patient.id)] = data
        self.save()


@receiver(post_init, sender=ActivityState)
def post_init_activity_state(sender, instance, *args, **kwargs):
    instance.data = json.loads(instance.json)


@receiver(pre_save, sender=ActivityState)
def pre_save_activity_state(sender, instance, *args, **kwargs):
    instance.json = json.dumps(instance.data)


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

    pageblocks = GenericRelation(PageBlock)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    view = models.IntegerField(choices=VIEW_CHOICES)

    template_file = "activity_virtual_patient/patient.html"
    css_template_file = "activity_virtual_patient/patient_css.html"
    js_template_file = "activity_virtual_patient/patient_js.html"
    display_name = "Virtual Patient"

    def __str__(self):
        return smart_str(self.pageblock())

    def pageblock(self):
        return self.pageblocks.all()[0]

    def get_hierarchy(self):
        return self.pageblock().section.hierarchy

    def needs_submit(self):
        return self.view != self.VIEW_RESULTS

    def submit_classify_treatments(self, data, patient_state):
        patient_state = {}
        for k in data.keys():
            patient_state[k] = {}
            patient_state[k]['classification'] = data[k]
        return patient_state

    def submit_best_treatment_option(self, data, patient_state):
        patient_state[data['prescribe']]['prescribe'] = 'true'
        for k in data.keys():
            if k == 'prescribe':
                patient_state[data[k]][k] = 'true'
            elif k == 'combination':
                for m in data[k]:
                    if m in patient_state:
                        patient_state[m][k] = 'true'
        return patient_state

    def submit_write_prescription(self, data, patient_state):
        for key, value in data.items():
            field, med_id = key.split('-')  # fieldname-medicine_id
            medicine = Medication.objects.get(id=med_id)
            if 'rx' not in patient_state[medicine.tag]:
                patient_state[medicine.tag]['rx'] = {}
            if med_id not in patient_state[medicine.tag]['rx']:
                patient_state[medicine.tag]['rx'][med_id] = {}
            patient_state[medicine.tag]['rx'][med_id][field] = value
        return patient_state

    def submit(self, user, data):
        state = ActivityState.get_for_user(user, self.get_hierarchy())
        patient_state = state.patient_state(self.patient)

        if self.view == self.CLASSIFY_TREATMENTS:
            patient_state = self.submit_classify_treatments(
                data, patient_state)
        elif self.view == self.BEST_TREATMENT_OPTION:
            patient_state = self.submit_best_treatment_option(
                data, patient_state)
        elif self.view == self.WRITE_PRESCRIPTION:
            patient_state = self.submit_write_prescription(
                data, patient_state)

        state.save_patient_state(self.patient, patient_state)
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
        state = ActivityState.get_for_user(user, self.get_hierarchy())
        patient_state = state.patient_state(self.patient)

        if self.view == self.CLASSIFY_TREATMENTS:
            return (len(self.patient.treatments()) ==
                    len(patient_state.keys()))
        elif self.view == self.BEST_TREATMENT_OPTION:
            return self.unlocked_best_treatment_option(patient_state)
        elif self.view == self.WRITE_PRESCRIPTION:
            return self.unlocked_write_prescription(user)
        elif self.view == self.VIEW_RESULTS:
            medications = self.medications(user)
            return len(medications) > 0
        return False

    def unlocked_best_treatment_option(self, patient_state):
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

    def unlocked_write_prescription(self, user):
        medications = self.medications(user)
        for med in medications:
            if len(med['choices']) != med['rx_count']:
                return False
            for choice in med['choices']:
                if (not hasattr(choice, 'selected_dosage') or
                        not hasattr(choice, 'selected_concentration')):
                    return False
        return True

    def available_treatments(self, user):
        state = ActivityState.get_for_user(user, self.get_hierarchy())
        patient_state = state.patient_state(self.patient)
        qst = self.patient.treatments()

        lst = list(qst)
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
        state = ActivityState.get_for_user(user, self.get_hierarchy())
        patient_state = state.patient_state(self.patient)

        medications = []
        for key, value in patient_state.items():
            if (key != 'combination' and
                    ('combination' in value or 'prescribe' in value)):
                qst = Medication.objects.filter(
                    tag=key).order_by("display_order")
                context = {'rx_count': len(qst),
                           'name': qst[0].name,
                           'tag': qst[0].tag,
                           'display_order': qst[0].display_order,
                           'choices': []}
                for med in qst:
                    if 'rx' in value:
                        setattr(med, "selected_concentration",
                                int(value['rx'][str(med.id)]['concentration']))
                        setattr(med, "selected_dosage",
                                int(value['rx'][str(med.id)]['dosage']))

                        cnc = ConcentrationChoice.objects.get(
                            id=int(value['rx'][str(med.id)]['concentration']))
                        dsc = DosageChoice.objects.get(
                            id=int(value['rx'][str(med.id)]['dosage']))

                        setattr(med,
                                "selected_concentration_label",
                                cnc.concentration)
                        setattr(med,
                                "selected_dosage_label",
                                dsc.dosage)
                    context['choices'].append(med)
                medications.append(context)

        return sorted(medications, key=itemgetter('display_order'))

    def complete_rx(self, medications):
        for medicine in medications:
            for choice in medicine['choices']:
                if not hasattr(choice, 'selected_concentration'):
                    return False
                if not hasattr(choice, 'selected_dosage'):
                    return False
        return True

    def correct_rx(self, medications):
        # "Correct" the concentration & dosage choices
        correct_rx = True
        medication_ids = []
        for medicine in medications:
            for choice in medicine['choices']:
                cnc = choice.concentrationchoice_set.get(correct=True)
                dsc = choice.dosagechoice_set.get(correct=True)

                if (choice.selected_concentration != cnc.id or
                        choice.selected_dosage != dsc.id):
                    correct_rx = False

                medication_ids.append(choice.id)
        return correct_rx, medication_ids

    def feedback(self, user):
        if not self.unlocked(user):
            return None

        medications = self.medications(user)
        if not self.complete_rx(medications):
            return None

        correct_rx, medication_ids = self.correct_rx(medications)

        # Find the treatment option associated with the prescribed medications
        topt = TreatmentOption.objects.filter(patient__id=self.patient.id)

        combination = len(medications) == 2
        if combination:
            topt = topt.get(medication_one__id__in=medication_ids,
                            medication_two__id__in=medication_ids)
        else:
            topt = topt.get(medication_one__id__in=medication_ids,
                            medication_two__isnull=True)

        tfd = TreatmentFeedback.objects.filter(
            patient__id=self.patient.id, classification=topt.classification)

        if topt.classification.rank == 1:
            # For the best, factor in correct dosage
            tfd = tfd.get(correct_dosage=correct_rx)
        else:  # for ineffective + harmful factor in combination
            tfd = tfd.get(combination_therapy=combination)

        return tfd


class PatientAssessmentForm(forms.ModelForm):
    class Meta:
        model = PatientAssessmentBlock
        exclude = []


class VirtualPatientColumn(object):
    def identifier(self):
        raise NotImplementedError

    def key_row(self):
        raise NotImplementedError

    def user_value(self, user):
        raise NotImplementedError

    @classmethod
    def all(cls, hrchy, section, key=True):
        columns = []
        ctype = ContentType.objects.get(name='patient assessment block')

        for activity in section.pageblock_set.filter(content_type=ctype):
            block = activity.block()
            patient = activity.block().patient

            if block.view == PatientAssessmentBlock.CLASSIFY_TREATMENTS:
                columns += ClassifyTreatmentColumn.all(hrchy, patient, key)
            elif block.view == PatientAssessmentBlock.BEST_TREATMENT_OPTION:
                columns += BestTreatmentColumn.all(hrchy, patient, key)
                columns += CombinationTreatmentColumn.all(hrchy, patient, key)
            elif block.view == PatientAssessmentBlock.WRITE_PRESCRIPTION:
                columns += WritePrescriptionColumn.all(hrchy, patient, key)
            elif block.view == PatientAssessmentBlock.VIEW_RESULTS:
                columns += TreatmentRankColumn.all(hrchy, block, key)
                columns += CorrectRxColumn.all(hrchy, block, key)

        return columns


class ClassifyTreatmentColumn(VirtualPatientColumn):

    def __init__(self, hierarchy, patient, treatment, classification=None):
        self.hierarchy = hierarchy
        self.patient = patient
        self.treatment = treatment
        self.classification = classification

    def description(self):
        return "Step 1 - Classify Treatments for %s - %s" % \
            (self.patient.name, self.treatment.name)

    def identifier(self):
        return "vp_%s_%s_1_%s" % (self.hierarchy.id,
                                  self.patient.id,
                                  # virtual patient page
                                  self.treatment.id)

    def key_row(self):
        return [self.identifier(), self.hierarchy.name, "Virtual Patient",
                "single choice", self.description(),
                self.classification.rank, self.classification.description]

    def user_value(self, user):
        state = ActivityState.get_for_user(user, self.hierarchy)
        patient_state = state.patient_state(self.patient)

        try:
            clss = patient_state[self.treatment.tag]['classification']
            return TreatmentClassification.value_to_rank(clss)
        except KeyError:
            return ''

    @classmethod
    def all(cls, hierarchy, patient, key):
        columns = []

        for treat in patient.treatments():
            if key:
                classifications = TreatmentClassification.objects.all()
                for classification in classifications.order_by('rank'):
                    columns.append(ClassifyTreatmentColumn(
                        hierarchy, patient, treat, classification))
            else:
                columns.append(ClassifyTreatmentColumn(
                    hierarchy, patient, treat))
        return columns


class BestTreatmentColumn(VirtualPatientColumn):

    def __init__(self, hierarchy, patient, treatment=None):
        self.hierarchy = hierarchy
        self.patient = patient
        self.treatment = treatment

    def description(self):
        return "Step 2 - Best Treatment for %s" % self.patient.name

    def identifier(self):
        return "vp_%s_%s_2" % (self.hierarchy.id, self.patient.id)

    def key_row(self):
        return [self.identifier(), self.hierarchy.name, "Virtual Patient",
                "single choice", self.description(),
                self.treatment.id, self.treatment.name]

    def user_value(self, user):
        state = ActivityState.get_for_user(user, self.hierarchy)
        patient_state = state.patient_state(self.patient)

        for treatment in self.patient.treatments():
            if (treatment.tag in patient_state and
                    'prescribe' in patient_state[treatment.tag]):
                return treatment.id

        return ''

    @classmethod
    def all(cls, hierarchy, patient, key):
        columns = []

        # One single choice question -- "best" treatment
        if key:
            for trt in patient.treatments():
                columns.append(BestTreatmentColumn(hierarchy, patient, trt))
        else:
            columns.append(BestTreatmentColumn(hierarchy, patient))

        return columns


class CombinationTreatmentColumn(VirtualPatientColumn):

    def __init__(self, hierarchy, patient, treatment):
        self.hierarchy = hierarchy
        self.patient = patient
        self.treatment = treatment

    def description(self):
        return "Step 3 - Combination Therapy for %s" % self.patient.name

    def patient_id(self):
        return "vp_%s_%s_3" % (self.hierarchy.id, self.patient.id)

    def patient_treatment_id(self, treat):
        return "vp_%s_%s_3_%s" % (self.hierarchy.id, self.patient.id, treat.id)

    def identifier(self):
        return self.patient_treatment_id(self.treatment)

    def key_row(self):
        return [self.patient_id(), self.hierarchy.name, "Virtual Patient",
                "multiple choice", self.description(), self.treatment.id,
                self.treatment.name]

    def user_value(self, user):
        state = ActivityState.get_for_user(user, self.hierarchy)
        patient_state = state.patient_state(self.patient)

        try:
            if 'combination' in patient_state[self.treatment.tag]:
                return self.treatment.id
        except KeyError:
            pass  # that's okay

        return ''

    @classmethod
    def all(cls, hierarchy, patient, key):
        columns = []

        # One multichoice question -- 2 combination treatments
        for trt in patient.treatments():
            if trt.name != "combination":
                columns.append(CombinationTreatmentColumn(hierarchy,
                                                          patient, trt))
        return columns


class WritePrescriptionColumn(VirtualPatientColumn):

    def __init__(self, hierarchy, patient, field, medication, choice=None):
        self.hierarchy = hierarchy
        self.patient = patient
        self.field = field
        self.medication = medication
        self.choice = choice

    def identifier(self):
        return "vp_%s_%s_4_%s_%s" % (self.hierarchy.id, self.patient.id,
                                     self.medication.id, self.field)

    def description(self):
        return "Step 4 - Prescribe %s for %s - %s" % (self.medication.name,
                                                      self.patient.name,
                                                      self.field)

    def key_row(self):
        return [self.identifier(), self.hierarchy.name, "Virtual Patient",
                "single choice", self.description(), self.choice.id,
                getattr(self.choice, self.field)]

    def user_value(self, user):
        state = ActivityState.get_for_user(user, self.hierarchy)
        patient_state = state.patient_state(self.patient)

        try:
            rx = patient_state[self.medication.tag]['rx']
            return rx[str(self.medication.id)][self.field]
        except KeyError:
            return ''

    @classmethod
    def all(cls, hierarchy, patient, key):
        columns = []

        # rows for each medication / dosage / choice value
        for trt in patient.treatments():
            medications = Medication.objects.filter(
                tag=trt.tag).exclude(tag='combination')
            for med in medications:
                if key:
                    for dosage in med.dosagechoice_set.all():
                        columns.append(WritePrescriptionColumn(hierarchy,
                                                               patient,
                                                               "dosage",
                                                               med,
                                                               dosage))
                    for conc in med.concentrationchoice_set.all():
                        columns.append(WritePrescriptionColumn(hierarchy,
                                                               patient,
                                                               "concentration",
                                                               med,
                                                               conc))
                else:
                    columns.append(WritePrescriptionColumn(hierarchy, patient,
                                                           "dosage", med))
                    columns.append(WritePrescriptionColumn(hierarchy, patient,
                                                           "concentration",
                                                           med))

        return columns


class TreatmentRankColumn(VirtualPatientColumn):
    def __init__(self, hierarchy, block, classification=None):
        self.hierarchy = hierarchy
        self.patient = block.patient
        self.block = block
        self.classification = classification

    def identifier(self):
        return "vp_%s_%s_5" % (self.hierarchy.id, self.patient.id)

    def description(self):
        return "Selected Treatment Rank for %s" % (self.patient.name)

    def key_row(self):
        return [self.identifier(),
                self.hierarchy.name,
                "Virtual Patient",
                "single choice",
                self.description(),
                self.classification.rank,
                self.classification.description]

    def user_value(self, user):
        feedback = self.block.feedback(user)
        if feedback is not None:
            return feedback.classification.rank
        else:
            return ''

    @classmethod
    def all(cls, hierarchy, block, key):
        columns = []
        if key:
            for classification in TreatmentClassification.objects.all():
                columns.append(TreatmentRankColumn(hierarchy,
                                                   block,
                                                   classification))
        else:
            columns.append(TreatmentRankColumn(hierarchy, block))

        return columns


class CorrectRxColumn(VirtualPatientColumn):
    def __init__(self, hierarchy, block):
        self.hierarchy = hierarchy
        self.patient = block.patient
        self.block = block

    def identifier(self):
        return "vp_%s_%s_6" % (self.hierarchy.id, self.patient.id)

    def description(self):
        return "Is Selected Prescription Correct for %s" % (self.patient.name)

    def key_row(self):
        return [self.identifier(),
                self.hierarchy.name,
                "Virtual Patient",
                "boolean",
                self.description()]

    def user_value(self, user):
        medications = self.block.medications(user)

        if not self.block.complete_rx(medications):
            return ''

        correct_rx, a = self.block.correct_rx(medications)
        return correct_rx

    @classmethod
    def all(cls, hierarchy, block, key):
        return [CorrectRxColumn(hierarchy, block)]
