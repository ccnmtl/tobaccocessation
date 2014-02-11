from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from django import forms


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

    def __unicode__(self):
        return "%s" % (self.name)


class Block(models.Model):
    pageblocks = generic.GenericRelation(
        PageBlock, related_name="prescription_writing_pageblocks")
    medication_name = models.CharField(max_length=25)
    allow_redo = models.BooleanField(default=True)
    template_file = "activity_prescription_writing/prescription.html"
    js_template_file = "activity_prescription_writing/prescription_js.html"
    css_template_file = "activity_prescription_writing/prescription_css.html"
    display_name = "Activity: Prescription Writing"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

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
            obj = simplejson.loads(state.json)
            obj[self.medication_name] = {}
            state.json = simplejson.dumps(obj)
            state.save()
        except ActivityState.DoesNotExist:
            pass  # calling reset before they've done anything

    def submit(self, user, data):
        state = ActivityState.get_for_user(self, user)
        obj = simplejson.loads(state.json)
        obj[self.medication_name] = {}

        for key, value in data.items():
            obj[self.medication_name][key] = value
        state.json = simplejson.dumps(obj)
        state.save()

    def unlocked(self, user):
        unlock = False
        state = ActivityState.get_for_user(self, user)
        obj = simplejson.loads(state.json)

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


class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="prescription_writing_user")
    block = models.ForeignKey(Block)
    json = models.TextField(blank=True)

    class Meta:
        unique_together = (("user", "block"),)

    def loads(self):
        return simplejson.loads(self.json)

    @classmethod
    def get_for_user(cls, block, user):
        try:
            state = ActivityState.objects.get(user=user, block=block)
        except ActivityState.DoesNotExist:
            state = ActivityState.objects.create(user=user, block=block)

            obj = {}
            for m in Medication.objects.all():
                obj[m.name] = {}

            state.json = simplejson.dumps(obj)
            state.save()

        return state
