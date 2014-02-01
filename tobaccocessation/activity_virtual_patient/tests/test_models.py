from django.test import TestCase
from tobaccocessation.activity_virtual_patient.models import Medication
from tobaccocessation.activity_virtual_patient.models import Patient
from tobaccocessation.activity_virtual_patient.models \
    import TreatmentClassification
from tobaccocessation.activity_virtual_patient.models import TreatmentOption
from tobaccocessation.activity_virtual_patient.models \
    import TreatmentOptionReasoning
from tobaccocessation.activity_virtual_patient.models import TreatmentFeedback


class TestMedication(TestCase):
    def test_unicode(self):
        m = Medication.objects.create(
            name="foo",
            instructions="instructions",
            display_order=1,
            tag="none")
        self.assertEqual(str(m), "foo")


class TestPatient(TestCase):
    def test_unicode(self):
        p = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        self.assertEqual(str(p), "1. foo")


class TestTreatmentClassification(TestCase):
    def test_unicode(self):
        tc = TreatmentClassification.objects.create(rank=1, description="foo")
        self.assertEqual(str(tc), "1. foo")


class TestTreatmentOption(TestCase):
    def test_unicode(self):
        p = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        m1 = Medication.objects.create(
            name="m1",
            instructions="instructions",
            display_order=1,
            tag="none")
        m2 = Medication.objects.create(
            name="m2",
            instructions="instructions",
            display_order=2,
            tag="none")
        tc = TreatmentClassification.objects.create(rank=1, description="foo")
        to = TreatmentOption.objects.create(
            patient=p, classification=tc, medication_one=m1, medication_two=m2)
        self.assertEqual(str(to), "Option: foo [m1, m2]")


class TestTreatmentOptionReasoning(TestCase):
    def test_unicode(self):
        p = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        m1 = Medication.objects.create(
            name="m1",
            instructions="instructions",
            display_order=1,
            tag="none")
        tc = TreatmentClassification.objects.create(rank=1, description="foo")
        tor = TreatmentOptionReasoning.objects.create(
            patient=p, classification=tc, medication=m1,
            combination=True, reasoning="i don't know")
        self.assertEqual(str(tor), "OptionReasoning: foo [m1, i don't know]")


class TestTreatmentFeedback(TestCase):
    def test_unicode(self):
        p = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        tc = TreatmentClassification.objects.create(
            rank=1, description="foo")
        tf = TreatmentFeedback.objects.create(
            patient=p, classification=tc, feedback="ok")
        self.assertEqual(str(tf), "Feedback: 1. foo foo")
