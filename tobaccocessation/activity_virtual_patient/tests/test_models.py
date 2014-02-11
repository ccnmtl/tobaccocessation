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


class TestPatientAssessmentBlock(TestCase):
    def setUp(self):
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
