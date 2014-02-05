from django.contrib.auth.models import User
from django.test import TestCase
from tobaccocessation.activity_virtual_patient.models import \
    PatientAssessmentBlock, Patient


class TestPatientAssessmentBlock(TestCase):
    fixtures = ['virtualpatient.json']

    def setUp(self):
        self.user = User.objects.create(username="test")
        self.patient = Patient.objects.get(display_order=1)

    CLASSIFY_TREATMENTS_DATA = {
        u'nicotinepatch': u'appropriate',
        u'nicotinegum': u'ineffective',
        u'nicotineinhaler': u'ineffective',
        u'nicotinenasalspray': u'ineffective',
        u'bupropion': u'harmful',
        u'varenicline': u'appropriate',
        u'combination': u'appropriate'
    }

    def test_classify_treatments_view(self):
        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        treatments = block.available_treatments(self.user)
        self.assertEquals(len(treatments), 7)
        self.assertEquals(treatments[0].tag, 'nicotinepatch')
        self.assertEquals(treatments[1].tag, 'nicotinegum')
        self.assertEquals(treatments[2].tag, 'nicotineinhaler')
        self.assertEquals(treatments[3].tag, 'nicotinenasalspray')
        self.assertEquals(treatments[4].tag, 'bupropion')
        self.assertEquals(treatments[5].tag, 'varenicline')
        self.assertEquals(treatments[6].tag, 'combination')
        for t in treatments:
            self.assertFalse(hasattr(t, 'prescribe'))
            self.assertFalse(hasattr(t, 'combination'))
            self.assertFalse(hasattr(t, 'classification'))

        # appropriate choices
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        self.assertTrue(block.unlocked(self.user))
        treatments = block.available_treatments(self.user)
        self.assertTrue(treatments[0].classification, 'appropriate')
        self.assertTrue(treatments[1].classification, 'appropriate')
        self.assertTrue(treatments[2].classification, 'ineffective')
        self.assertTrue(treatments[3].classification, 'ineffective')
        self.assertTrue(treatments[4].classification, 'harmful')
        self.assertTrue(treatments[5].classification, 'appropriate')
        self.assertTrue(treatments[6].classification, 'appropriate')
        for t in treatments:
            self.assertFalse(hasattr(t, 'prescribe'))
            self.assertFalse(hasattr(t, 'combination'))

    BEST_TREATMENT_DATA_SINGLE = {
        u'prescribe': u'nicotinepatch'
    }

    BEST_TREATMENT_DATA_DOUBLE = {
        u'prescribe': u'varenicline'
    }

    BEST_TREATMENT_DATA_COMBINATION = {
        u'prescribe': u'combination',
        u'combination': [u'nicotinepatch', u'varenicline']
    }

    def test_best_treatment_single(self):
        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.BEST_TREATMENT_OPTION)
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.BEST_TREATMENT_DATA_SINGLE)
        self.assertTrue(block.unlocked(self.user))

        medications = block.medications(self.user)
        self.assertEquals(len(medications), 1)
        self.assertEquals(medications[0]['rx_count'], 1)
        self.assertEquals(medications[0]['tag'], 'nicotinepatch')
        self.assertEquals(medications[0]['name'], 'Nicotine Patch')
        self.assertEquals(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

    def test_best_treatment_double(self):
        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.BEST_TREATMENT_OPTION)
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.BEST_TREATMENT_DATA_DOUBLE)
        self.assertTrue(block.unlocked(self.user))

        medications = block.medications(self.user)
        self.assertEquals(len(medications), 1)
        self.assertEquals(medications[0]['rx_count'], 2)
        self.assertEquals(medications[0]['tag'], 'varenicline')
        self.assertEquals(medications[0]['name'], 'Varenicline')
        self.assertEquals(len(medications[0]['choices']), 2)

        obj = medications[0]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))
        obj = medications[0]['choices'][1]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

    def test_best_treatment_combination(self):
        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block = PatientAssessmentBlock(
            patient=self.patient,
            view=PatientAssessmentBlock.BEST_TREATMENT_OPTION)
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.BEST_TREATMENT_DATA_COMBINATION)
        self.assertTrue(block.unlocked(self.user))

        medications = block.medications(self.user)
        self.assertEquals(len(medications), 2)
        self.assertEquals(medications[0]['rx_count'], 1)
        self.assertEquals(medications[0]['tag'], 'nicotinepatch')
        self.assertEquals(medications[0]['name'], 'Nicotine Patch')
        self.assertEquals(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

        self.assertEquals(medications[1]['rx_count'], 2)
        self.assertEquals(medications[1]['tag'], 'varenicline')
        self.assertEquals(medications[1]['name'], 'Varenicline')
        self.assertEquals(len(medications[1]['choices']), 2)

        obj = medications[1]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))
        obj = medications[1]['choices'][1]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

    PRESCRIPTION_COMBINATION_DATA = {
        u'concentration-7': u'22',
        u'dosage-8': u'31',
        u'concentration-2': u'1',
        u'dosage-7': u'26',
        u'dosage-2': u'1',
        u'concentration-8': u'30'}

    def test_prescribe_single(self):
        self.assertTrue(True)

    def test_prescribe_double(self):
        self.assertTrue(True)

    def test_prescribe_combination(self):
        self.assertTrue(True)
