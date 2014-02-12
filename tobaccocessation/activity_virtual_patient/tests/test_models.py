from django.test import TestCase
from tobaccocessation.activity_virtual_patient.models import \
    TreatmentClassification, TreatmentOptionReasoning, Medication, Patient, \
    TreatmentFeedback, TreatmentOption


class TestMedication(TestCase):
    def test_unicode(self):
        med = Medication.objects.create(
            name="foo",
            instructions="instructions",
            display_order=1,
            tag="none")
        self.assertEqual(str(med), "foo")


class TestPatient(TestCase):
    fixtures = ['virtualpatient.json']

    def test_unicode(self):
        patient = Patient.objects.get(display_order=1)
        self.assertEqual(str(patient), "1. Beverly Johnson")

    def test_treatments(self):
        patient = Patient.objects.get(display_order=1)
        treatments = patient.treatments()
        self.assertEquals(len(treatments), 7)

        patient = Patient.objects.get(display_order=2)
        treatments = patient.treatments()
        self.assertEquals(len(treatments), 8)


class TestTreatmentClassification(TestCase):
    def test_unicode(self):
        choice = TreatmentClassification.objects.create(rank=1,
                                                        description="foo")
        self.assertEqual(str(choice), "1. foo")


class TestTreatmentOption(TestCase):
    def test_unicode(self):
        patient = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        med1 = Medication.objects.create(
            name="med1",
            instructions="instructions",
            display_order=1,
            tag="none")
        med2 = Medication.objects.create(
            name="med2",
            instructions="instructions",
            display_order=2,
            tag="none")
        choice = TreatmentClassification.objects.create(rank=1,
                                                        description="foo")
        option = TreatmentOption.objects.create(
            patient=patient, classification=choice,
            medication_one=med1, medication_two=med2)
        self.assertEqual(str(option), "Option: foo [med1, med2]")


class TestTreatmentOptionReasoning(TestCase):
    def test_unicode(self):
        patient = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        med1 = Medication.objects.create(
            name="med1",
            instructions="instructions",
            display_order=1,
            tag="none")
        tcl = TreatmentClassification.objects.create(rank=1, description="foo")
        tor = TreatmentOptionReasoning.objects.create(
            patient=patient, classification=tcl, medication=med1,
            combination=True, reasoning="i don't know")
        self.assertEqual(str(tor), "OptionReasoning: foo [med1, i don't know]")


class TestTreatmentFeedback(TestCase):
    def test_unicode(self):
        patient = Patient.objects.create(
            name="foo",
            description="bar",
            history="history",
            display_order=1)
        tcl = TreatmentClassification.objects.create(
            rank=1, description="foo")
        tfd = TreatmentFeedback.objects.create(
            patient=patient, classification=tcl, feedback="ok")
        self.assertEqual(str(tfd), "Feedback: 1. foo foo")
