import json

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from pagetree.models import PageBlock


class Medication(models.Model):
    name = models.CharField(max_length=25)
    dosage = models.CharField(max_length=25)
    dispensing = models.CharField(max_length=50)
    signature = models.TextField()
    refills = models.IntegerField()
    sort_order = models.IntegerField()
    dosage_callout = models.TextField(blank=True, null=True)
    dispensing_callout = models.TextField(blank=True, null=True)
    signature_callout = models.TextField(blank=True, null=True)
    refills_callout = models.TextField(blank=True, null=True)
    rx_count = models.IntegerField(default=1)

    def __str__(self):
        return "%s" % (self.name)


class Block(models.Model):
    pageblocks = GenericRelation(
        PageBlock, related_query_name="prescription_writing_pageblocks")
    medication_name = models.CharField(max_length=25)
    allow_redo = models.BooleanField(default=True)
    template_file = "activity_prescription_writing/prescription.html"
    js_template_file = "activity_prescription_writing/prescription_js.html"
    css_template_file = "activity_prescription_writing/prescription_css.html"
    display_name = "Activity: Prescription Writing"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return "%s -- %s" % (
            smart_str(self.pageblock()), self.medication_name)

    @classmethod
    def add_form(self):
        return PrescriptionBlockForm()

    def edit_form(self):
        return PrescriptionBlockForm(instance=self)

    @classmethod
    def create(self, request):
        form = PrescriptionBlockForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = PrescriptionBlockForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def medication(self):
        meds = Medication.objects.filter(name=self.medication_name)
        return meds.order_by('id')

    def redirect_to_self_on_submit(self):
        return True

    def needs_submit(self):
        return True

    def clear_user_submissions(self, user):
        try:
            state = ActivityState.objects.get(user=user, block=self)
            obj = json.loads(state.json)
            obj[self.medication_name] = {}
            state.json = json.dumps(obj)
            state.save()
        except ActivityState.DoesNotExist:
            pass  # calling reset before they've done anything

    def submit(self, user, data):
        state = ActivityState.get_for_user(self, user)
        obj = json.loads(state.json)
        obj[self.medication_name] = {}

        for key, value in data.items():
            obj[self.medication_name][key] = value
        state.json = json.dumps(obj)
        state.save()

    def unlocked(self, user):
        unlock = False
        state = ActivityState.get_for_user(self, user)
        obj = json.loads(state.json)

        if self.medication_name in obj:
            d = obj[self.medication_name]
            if self.medication()[0].rx_count == 1:
                unlock = 'dosage' in d and len(d['dosage']) > 0 and \
                    'disp' in d and len(d['disp']) > 0 and \
                    'sig' in d and len(d['sig']) > 0 and \
                    'refills' in d and len(d['refills']) > 0
            else:
                unlock = 'dosage' in d and len(d['dosage']) > 0 and \
                    'disp' in d and len(d['disp']) > 0 and \
                    'sig' in d and len(d['sig']) > 0 and \
                    'refills' in d and len(d['refills']) > 0 and \
                    'dosage_2' in d and len(d['dosage_2']) > 0 and \
                    'disp_2' in d and len(d['disp_2']) > 0 and \
                    'sig_2' in d and len(d['sig_2']) > 0 and \
                    'refills_2' in d and len(d['refills_2']) > 0

        return unlock


class PrescriptionBlockForm(forms.ModelForm):
    class Meta:
        model = Block
        exclude = []


class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="prescription_writing_user",
                             on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    json = models.TextField(blank=True)

    class Meta:
        unique_together = (("user", "block"),)

    def loads(self):
        return json.loads(self.json)

    @classmethod
    def get_for_user(cls, block, user):
        state, created = ActivityState.objects.get_or_create(user=user,
                                                             block=block)
        if created:
            obj = {}
            for m in Medication.objects.all():
                obj[m.name] = {}

            state.json = json.dumps(obj)
            state.save()

        return state


class PrescriptionColumn(object):
    def __init__(self, hierarchy, block, medication, field):
        self.hierarchy = hierarchy
        self.block = block
        self.medication = medication
        self.field = field

    def key_row(self):
        return [self.identifier(),
                self.hierarchy.name,
                'Prescription Writing Exercise',
                'short text',  # item type
                '%s %s' % (self.medication.name, self.field)]  # item descript

    def identifier(self):
        return "%s_%s_%s" % (
            self.hierarchy.id, self.medication.id, self.field)

    def user_value(self, user):
        try:
            state = ActivityState.objects.get(
                block=self.block,
                user=user).loads()
            if (self.medication.name in state and
                    self.field in state[self.medication.name]):
                return state[self.medication.name][self.field]
            state[self.medication.name]
        except ActivityState.DoesNotExist:
            pass

        return ''

    @classmethod
    def all(cls, hrchy, section, key_only=True):
        columns = []
        ctype = ContentType.objects.get(
            app_label="activity_prescription_writing", model='block')

        for activity in section.pageblock_set.filter(content_type=ctype):
            medications = Medication.objects.filter(
                name=activity.block().medication_name, rx_count__gt=0)
            for med in medications:
                columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                  block=activity.block(),
                                                  medication=med,
                                                  field='dosage'))
                columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                  block=activity.block(),
                                                  medication=med,
                                                  field='disp'))
                columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                  block=activity.block(),
                                                  medication=med,
                                                  field='sig'))
                columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                  block=activity.block(),
                                                  medication=med,
                                                  field='refills'))

                if med.rx_count > 1:
                    columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                      block=activity.block(),
                                                      medication=med,
                                                      field='dosage_2'))
                    columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                      block=activity.block(),
                                                      medication=med,
                                                      field='disp_2'))
                    columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                      block=activity.block(),
                                                      medication=med,
                                                      field='sig_2'))
                    columns.append(PrescriptionColumn(hierarchy=hrchy,
                                                      block=activity.block(),
                                                      medication=med,
                                                      field='refills_2'))
        return columns
