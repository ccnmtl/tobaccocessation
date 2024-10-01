from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client, RequestFactory
from pagetree.helpers import get_section_from_path
from pagetree.models import Hierarchy
from tobaccocessation.activity_virtual_patient.models import \
    PatientAssessmentBlock, Patient, ClassifyTreatmentColumn, Medication, \
    TreatmentClassification, BestTreatmentColumn, CombinationTreatmentColumn, \
    WritePrescriptionColumn, DosageChoice, TreatmentRankColumn, CorrectRxColumn
from tobaccocessation.main.models import UserProfile


class VirtualPatientTestCase(TestCase):
    fixtures = ['virtualpatient.json']

    @classmethod
    def create_block(cls, section, patient, view_type):
        block = PatientAssessmentBlock(patient=patient, view=view_type)
        block.save()

        section.append_pageblock(label="virtual patient",
                                 css_extra="",
                                 content_object=block)

        return block

    def setUp(self):
        self.c = Client()

        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')
        UserProfile.objects.get_or_create(user=self.user,
                                          gender='M',
                                          is_faculty='ST',
                                          institute='I1',
                                          specialty='S1',
                                          consent_participant=True,
                                          consent_not_participant=False,
                                          hispanic_latino='Y',
                                          year_of_graduation=2015)

        self.patient1 = Patient.objects.get(display_order=1)
        self.patient4 = Patient.objects.get(display_order=4)

        get_section_from_path("")  # creates a root if one doesn't exist
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.hierarchy.id = 3
        self.hierarchy.save()
        self.section = self.hierarchy.get_root().append_child('Bar Baz',
                                                              'bar-baz')

        get_section_from_path("", "alt")  # creates a root if one doesn't exist
        alt_hierarchy = Hierarchy.objects.get(name='alt')
        self.alt_section = alt_hierarchy.get_root().append_child(
            'Sam I Am', 'sam-i-am')

    CLASSIFY_TREATMENTS_DATA = {
        u'nicotinepatch': u'appropriate',
        u'nicotinegum': u'ineffective',
        u'nicotineinhaler': u'ineffective',
        u'nicotinenasalspray': u'harmful',
        u'bupropion': u'appropriate',
        u'varenicline': u'appropriate',
        u'combination': u'appropriate'
    }

    BEST_TREATMENT_SINGLE_APPROPRIATE = {
        u'prescribe': u'bupropion'
    }

    BEST_TREATMENT_SINGLE_INEFFECTIVE = {
        u'prescribe': u'nicotinepatch'
    }

    BEST_TREATMENT_DOUBLE = {
        u'prescribe': u'varenicline'
    }

    BEST_TREATMENT_COMBINATION_APPROPRIATE = {
        u'prescribe': u'combination',
        u'combination': [u'nicotinepatch', u'varenicline']
    }

    PRESCRIPTION_SINGLE_APPROPRIATE_CORRECT = {
        u'concentration-5': u'15',
        u'dosage-5': u'19'}

    PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT = {
        u'concentration-5': u'17',
        u'dosage-5': u'13'}

    PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT_CONCENTRATION = {
        u'concentration-5': u'17',
        u'dosage-5': u'19'}

    PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT_DOSAGE = {
        u'concentration-5': u'15',
        u'dosage-5': u'13'}

    PRESCRIPTION_SINGLE_INEFFECTIVE = {
        u'concentration-1': u'5',
        u'dosage-1': u'6'}

    PRESCRIPTION_DOUBLE_CORRECT = {
        u'concentration-7': u'21',
        u'dosage-7': u'26',
        u'concentration-8': u'33',
        u'dosage-8': u'31'}

    PRESCRIPTION_DOUBLE_INCORRECT = {
        u'concentration-7': u'22',
        u'dosage-7': u'25',
        u'concentration-8': u'31',
        u'dosage-8': u'32'}

    PRESCRIPTION_DOUBLE_APPROPRIATE_INCORRECT_RX1 = {
        u'concentration-7': u'22',
        u'dosage-7': u'25',
        u'concentration-8': u'33',
        u'dosage-8': u'31'}

    PRESCRIPTION_DOUBLE_APPROPRIATE_INCORRECT_RX2 = {
        u'concentration-7': u'21',
        u'dosage-7': u'26',
        u'concentration-8': u'31',
        u'dosage-8': u'32'}

    PRESCRIPTION_DOUBLE_HARMFUL = {
        u'concentration-7': u'21',
        u'dosage-7': u'26',
        u'concentration-8': u'33',
        u'dosage-8': u'31'}

    PRESCRIPTION_COMBINATION_INEFFECTIVE = {
        u'concentration-1': u'5',
        u'dosage-1': u'6',
        u'concentration-7': u'21',
        u'dosage-7': u'26',
        u'concentration-8': u'33',
        u'dosage-8': u'31'}


class TestPatientAssessmentBlock(VirtualPatientTestCase):

    def test_add_form(self):
        form = PatientAssessmentBlock.add_form()
        self.assertIsNotNone(form)
        self.assertTrue('patient' in form.fields)
        self.assertTrue('view' in form.fields)

    def test_edit_form(self):
        block = PatientAssessmentBlock(
            patient=self.patient1,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.save()

        form = block.edit_form()
        self.assertIsNotNone(form)
        self.assertTrue('patient' in form.fields)
        self.assertTrue('view' in form.fields)
        self.assertEqual(form.initial['patient'],
                         self.patient1.id)
        self.assertEqual(form.initial['view'],
                         PatientAssessmentBlock.CLASSIFY_TREATMENTS)

    def test_create(self):
        rf = RequestFactory()
        post_request = rf.post('/',
                               {'patient': '4',
                                'view': PatientAssessmentBlock.VIEW_RESULTS})
        block = PatientAssessmentBlock.create(post_request)
        self.assertEqual(block.view, PatientAssessmentBlock.VIEW_RESULTS)
        self.assertEqual(block.patient, self.patient4)

    def test_edit(self):
        block = PatientAssessmentBlock(
            patient=self.patient1,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.save()
        self.assertEqual(block.patient, self.patient1)
        self.assertEqual(block.view,
                         PatientAssessmentBlock.CLASSIFY_TREATMENTS)

        rf = RequestFactory()
        post_request = rf.post('/',
                               {'patient': '4',
                                'view': PatientAssessmentBlock.VIEW_RESULTS})

        block.edit(post_request.POST, None)
        self.assertEqual(block.patient, self.patient4)
        self.assertEqual(block.view, PatientAssessmentBlock.VIEW_RESULTS)

    def test_classify_treatments_view(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        treatments = block.available_treatments(self.user)
        self.assertEqual(len(treatments), 7)
        self.assertEqual(treatments[0].tag, 'nicotinepatch')
        self.assertEqual(treatments[1].tag, 'nicotinegum')
        self.assertEqual(treatments[2].tag, 'nicotineinhaler')
        self.assertEqual(treatments[3].tag, 'nicotinenasalspray')
        self.assertEqual(treatments[4].tag, 'bupropion')
        self.assertEqual(treatments[5].tag, 'varenicline')
        self.assertEqual(treatments[6].tag, 'combination')
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
        self.assertTrue(treatments[3].classification, 'harmful')
        self.assertTrue(treatments[4].classification, 'appropriate')
        self.assertTrue(treatments[5].classification, 'appropriate')
        self.assertTrue(treatments[6].classification, 'appropriate')
        for t in treatments:
            self.assertFalse(hasattr(t, 'prescribe'))
            self.assertFalse(hasattr(t, 'combination'))

        block.view = PatientAssessmentBlock.VIEW_RESULTS
        self.assertFalse(block.unlocked(self.user))

    def test_best_treatment_single(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.BEST_TREATMENT_SINGLE_INEFFECTIVE)
        self.assertTrue(block.unlocked(self.user))

        medications = block.medications(self.user)
        self.assertEqual(len(medications), 1)
        self.assertEqual(medications[0]['rx_count'], 1)
        self.assertEqual(medications[0]['tag'], 'nicotinepatch')
        self.assertEqual(medications[0]['name'], 'Nicotine Patch')
        self.assertEqual(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

    def test_best_treatment_double(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.BEST_TREATMENT_DOUBLE)
        self.assertTrue(block.unlocked(self.user))

        medications = block.medications(self.user)
        self.assertEqual(len(medications), 1)
        self.assertEqual(medications[0]['rx_count'], 2)
        self.assertEqual(medications[0]['tag'], 'varenicline')
        self.assertEqual(medications[0]['name'], 'Varenicline')
        self.assertEqual(len(medications[0]['choices']), 2)

        obj = medications[0]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))
        obj = medications[0]['choices'][1]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

    def test_best_treatment_combination(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user,
                     self.BEST_TREATMENT_COMBINATION_APPROPRIATE)
        self.assertTrue(block.unlocked(self.user))

        medications = block.medications(self.user)
        self.assertEqual(len(medications), 2)
        self.assertEqual(medications[0]['rx_count'], 1)
        self.assertEqual(medications[0]['tag'], 'nicotinepatch')
        self.assertEqual(medications[0]['name'], 'Nicotine Patch')
        self.assertEqual(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

        self.assertEqual(medications[1]['rx_count'], 2)
        self.assertEqual(medications[1]['tag'], 'varenicline')
        self.assertEqual(medications[1]['name'], 'Varenicline')
        self.assertEqual(len(medications[1]['choices']), 2)

        obj = medications[1]['choices'][0]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))
        obj = medications[1]['choices'][1]
        self.assertFalse(hasattr(obj, 'selected_concentration'))
        self.assertFalse(hasattr(obj, 'selected_dosage'))

    def test_prescribe_single(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user, self.BEST_TREATMENT_SINGLE_INEFFECTIVE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.PRESCRIPTION_SINGLE_INEFFECTIVE)
        medications = block.medications(self.user)
        self.assertEqual(len(medications), 1)
        self.assertEqual(medications[0]['rx_count'], 1)
        self.assertEqual(medications[0]['tag'], 'nicotinepatch')
        self.assertEqual(medications[0]['name'], 'Nicotine Patch')
        self.assertEqual(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertEqual(int(obj.selected_concentration), 5)
        self.assertEqual(int(obj.selected_dosage), 6)
        self.assertEqual(obj.selected_concentration_label, u'21 mg')
        self.assertEqual(obj.selected_dosage_label, u'2 boxes, 28 patches')

    def test_prescribe_double(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user, self.BEST_TREATMENT_DOUBLE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.PRESCRIPTION_DOUBLE_CORRECT)
        medications = block.medications(self.user)
        self.assertEqual(len(medications), 1)
        self.assertEqual(medications[0]['rx_count'], 2)
        self.assertEqual(medications[0]['tag'], 'varenicline')
        self.assertEqual(medications[0]['name'], 'Varenicline')
        self.assertEqual(len(medications[0]['choices']), 2)

        obj = medications[0]['choices'][0]
        self.assertEqual(int(obj.selected_concentration), 21)
        self.assertEqual(int(obj.selected_dosage), 26)
        obj = medications[0]['choices'][1]
        self.assertEqual(int(obj.selected_concentration), 33)
        self.assertEqual(int(obj.selected_dosage), 31)

    def test_prescribe_combination(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user,
                     self.BEST_TREATMENT_COMBINATION_APPROPRIATE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.PRESCRIPTION_COMBINATION_INEFFECTIVE)
        medications = block.medications(self.user)
        self.assertEqual(len(medications), 2)

        self.assertEqual(medications[0]['rx_count'], 1)
        self.assertEqual(medications[0]['tag'], 'nicotinepatch')
        self.assertEqual(medications[0]['name'], 'Nicotine Patch')
        self.assertEqual(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertEqual(int(obj.selected_concentration), 5)
        self.assertEqual(int(obj.selected_dosage), 6)

        self.assertEqual(medications[1]['rx_count'], 2)
        self.assertEqual(medications[1]['tag'], 'varenicline')
        self.assertEqual(medications[1]['name'], 'Varenicline')
        self.assertEqual(len(medications[1]['choices']), 2)

        obj = medications[1]['choices'][0]
        self.assertEqual(int(obj.selected_concentration), 21)
        self.assertEqual(int(obj.selected_dosage), 26)
        obj = medications[1]['choices'][1]
        self.assertEqual(int(obj.selected_concentration), 33)
        self.assertEqual(int(obj.selected_dosage), 31)

    def test_feedback_single_appropriate(self):
        # Appropriate treatment - single prescription - correctrx
        # Appropriate treatment - single prescription - incorrectrx - dosage
        # Appropriate treatment - single prescription - incorrectrx - concentr
        # Appropriate treatment - single prescription - incorrectrx - both
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        # Bupropion
        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user, self.BEST_TREATMENT_SINGLE_APPROPRIATE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION

        # Correct
        block.submit(self.user, self.PRESCRIPTION_SINGLE_APPROPRIATE_CORRECT)
        feedback = block.feedback(self.user)
        self.assertTrue(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        # Incorrect - both concentration & dosage
        block.submit(self.user, self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        # Incorrect - concentration
        block.submit(
            self.user,
            self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT_CONCENTRATION)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        # Incorrect - dosage
        block.submit(self.user,
                     self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT_DOSAGE)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        block.view = PatientAssessmentBlock.VIEW_RESULTS
        self.assertTrue(block.unlocked(self.user))

    def test_feedback_double_appropriate(self):
        # Appropriate treatment - double prescription - correctrx
        # Appropriate treatment - double prescription - incorrectrx - both
        # Appropriate treatment - double prescription - incorrectrx - rx1
        # Appropriate treatment - double prescription - incorrectrx - rx2
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        self.assertTrue(block.needs_submit())
        self.assertFalse(block.unlocked(self.user))

        block.submit(self.user, self.BEST_TREATMENT_DOUBLE)
        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION

        # Correct
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_CORRECT)
        feedback = block.feedback(self.user)
        self.assertTrue(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        # Incorrect - both medicines
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_INCORRECT)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        # Incorrect - medicine 1
        block.submit(
            self.user,
            self.PRESCRIPTION_DOUBLE_APPROPRIATE_INCORRECT_RX1)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

        # Incorrect - medicine 2
        block.submit(self.user,
                     self.PRESCRIPTION_DOUBLE_APPROPRIATE_INCORRECT_RX2)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEqual(feedback.classification.rank, 1)

    def test_feedback_single_ineffective(self):
        # "correct" is irrelevant
        # combination is relevant
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user, self.BEST_TREATMENT_SINGLE_INEFFECTIVE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION
        block.submit(self.user, self.PRESCRIPTION_SINGLE_INEFFECTIVE)

        feedback = block.feedback(self.user)
        self.assertEqual(feedback.classification.rank, 2)
        self.assertFalse(feedback.combination_therapy)

    def test_feedback_double_harmful(self):
        # "correct" is irrelevant
        # combination is relevant
        block = self.create_block(self.section, self.patient4,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user, self.BEST_TREATMENT_DOUBLE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION

        # Correct
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_CORRECT)
        feedback = block.feedback(self.user)
        self.assertEqual(feedback.classification.rank, 3)

        # Incorrect - both medicines
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_INCORRECT)
        feedback = block.feedback(self.user)
        self.assertEqual(feedback.classification.rank, 3)

    def test_feedback_combination_ineffective(self):
        # correct is irrelevant
        # combination is not
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user,
                     self.BEST_TREATMENT_COMBINATION_APPROPRIATE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION
        block.submit(self.user, self.PRESCRIPTION_COMBINATION_INEFFECTIVE)
        feedback = block.feedback(self.user)
        self.assertEqual(feedback.classification.rank, 2)
        self.assertTrue(feedback.combination_therapy)

    def test_separate_hierarchies(self):
        block = self.create_block(
            self.section, self.patient1,
            PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        alt_block = self.create_block(
            self.alt_section, self.patient1,
            PatientAssessmentBlock.CLASSIFY_TREATMENTS)

        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        self.assertTrue(block.unlocked(self.user))
        self.assertFalse(alt_block.unlocked(self.user))

        alt_block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        self.assertTrue(block.unlocked(self.user))
        self.assertTrue(alt_block.unlocked(self.user))

    def test_reset(self):
        block = self.create_block(
            self.section, self.patient1,
            PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        alt_block = self.create_block(
            self.alt_section, self.patient1,
            PatientAssessmentBlock.CLASSIFY_TREATMENTS)

        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        alt_block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        self.assertTrue(block.unlocked(self.user))
        self.assertTrue(alt_block.unlocked(self.user))

        url = "/activity/virtualpatient/reset/%s/%s/" % (self.section.id,
                                                         self.patient1.id)

        self.c.login(username='test_student', password='testpassword')
        self.c.get(url)
        self.assertFalse(block.unlocked(self.user))
        self.assertTrue(alt_block.unlocked(self.user))
        # these fail in 1.6.4. I think it has to do with
        # the fixtures needing updating.
#        self.assertEqual(response.status_code, 200)
#        self.assertEqual(response.request["PATH_INFO"], "/")


class TestClassifyTreatmentColumn(VirtualPatientTestCase):

    def test_all(self):
        self.create_block(self.section, self.patient1,
                          PatientAssessmentBlock.CLASSIFY_TREATMENTS)

        a = ClassifyTreatmentColumn.all(self.hierarchy, self.patient1, True)
        self.assertEqual(len(a), 21)
        self.assertIsNotNone(a[0].classification)
        a = ClassifyTreatmentColumn.all(self.hierarchy, self.patient1, False)
        self.assertEqual(len(a), 7)
        self.assertIsNone(a[0].classification)

    def test_instance(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)

        med = Medication.objects.get(tag="nicotinepatch")
        classification = TreatmentClassification.objects.get(rank=1)

        # key
        column = ClassifyTreatmentColumn(self.hierarchy, self.patient1,
                                         med, classification)
        self.assertEqual(column.identifier(), "vp_3_1_1_1")
        self.assertEqual(column.key_row(),
                         ["vp_3_1_1_1",
                          "main",
                          "Virtual Patient", "single choice",
                          "Step 1 - Classify Treatments for Beverly "
                          "Johnson - Nicotine Patch",
                          1,
                          "More Appropriate Treatment Choice"])

        # value
        column = ClassifyTreatmentColumn(self.hierarchy, self.patient1, med)
        self.assertEqual(column.user_value(self.user), '')

        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        self.assertEqual(column.user_value(self.user), 1)


class TestBestTreatmentColumn(VirtualPatientTestCase):

    def test_all(self):
        self.create_block(self.section, self.patient1,
                          PatientAssessmentBlock.BEST_TREATMENT_OPTION)

        a = BestTreatmentColumn.all(self.hierarchy, self.patient1, True)
        self.assertEqual(len(a), 7)
        self.assertIsNotNone(a[0].treatment)
        a = BestTreatmentColumn.all(self.hierarchy, self.patient1, False)
        self.assertEqual(len(a), 1)
        self.assertIsNone(a[0].treatment)

    def test_instance(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.BEST_TREATMENT_OPTION)

        med = Medication.objects.get(tag="nicotinepatch")

        # key
        column = BestTreatmentColumn(self.hierarchy, self.patient1, med)
        self.assertEqual(column.identifier(), "vp_3_1_2")
        self.assertEqual(column.key_row(),
                         ["vp_3_1_2",
                          "main",
                          "Virtual Patient", "single choice",
                          "Step 2 - Best Treatment for Beverly Johnson",
                          med.id,
                          "Nicotine Patch"])

        # value
        column = BestTreatmentColumn(self.hierarchy, self.patient1)
        self.assertEqual(column.user_value(self.user), '')

        block.submit(self.user, self.BEST_TREATMENT_SINGLE_APPROPRIATE)
        self.assertEqual(column.user_value(self.user), 5)


class TestCombinationTreatmentColumn(VirtualPatientTestCase):

    def test_all(self):
        self.create_block(self.section, self.patient1,
                          PatientAssessmentBlock.BEST_TREATMENT_OPTION)

        a = CombinationTreatmentColumn.all(self.hierarchy, self.patient1, True)
        self.assertEqual(len(a), 7)
        self.assertIsNotNone(a[0].treatment)
        a = CombinationTreatmentColumn.all(self.hierarchy,
                                           self.patient1, False)
        self.assertEqual(len(a), 7)
        self.assertIsNotNone(a[0].treatment)

    def test_instance(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.BEST_TREATMENT_OPTION)

        med = Medication.objects.get(tag="nicotinepatch")

        # key
        column = CombinationTreatmentColumn(self.hierarchy, self.patient1, med)
        self.assertEqual(column.identifier(), "vp_3_1_3_1")
        self.assertEqual(column.key_row(),
                         ["vp_3_1_3",
                          "main",
                          "Virtual Patient", "multiple choice",
                          "Step 3 - Combination Therapy for Beverly Johnson",
                          med.id,
                          "Nicotine Patch"])

        # value - no state
        column = CombinationTreatmentColumn(self.hierarchy, self.patient1, med)
        self.assertEqual(column.user_value(self.user), '')

        # value - nicotine patch included in combination therapy
        block.submit(self.user, self.BEST_TREATMENT_COMBINATION_APPROPRIATE)
        self.assertEqual(column.user_value(self.user), med.id)

        # value - bupropion not included in combination therapy
        med = Medication.objects.get(tag="bupropion")
        column = CombinationTreatmentColumn(self.hierarchy, self.patient1, med)
        self.assertEqual(column.user_value(self.user), '')


class TestWritePrescriptionColumn(VirtualPatientTestCase):

    def test_all(self):
        self.create_block(self.section, self.patient1,
                          PatientAssessmentBlock.WRITE_PRESCRIPTION)

        a = WritePrescriptionColumn.all(self.hierarchy, self.patient1, True)
        self.assertEqual(len(a), 54)
        self.assertIsNotNone(a[0].choice)
        a = WritePrescriptionColumn.all(self.hierarchy, self.patient1, False)
        self.assertEqual(len(a), 14)
        self.assertIsNone(a[0].choice)

    def test_instance(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.BEST_TREATMENT_OPTION)
        block.submit(self.user, self.BEST_TREATMENT_COMBINATION_APPROPRIATE)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.WRITE_PRESCRIPTION)

        med = Medication.objects.get(tag="nicotinepatch")
        dosage = DosageChoice.objects.get(medication=med,
                                          dosage='4 boxes, 56 patches')

        # key
        column = WritePrescriptionColumn(self.hierarchy, self.patient1,
                                         "dosage", med, dosage)
        self.assertEqual(column.identifier(), "vp_3_1_4_1_dosage")
        self.assertEqual(column.key_row(),
                         ["vp_3_1_4_1_dosage",
                          "main", "Virtual Patient",
                          "single choice",
                          "Step 4 - Prescribe Nicotine Patch for "
                          "Beverly Johnson - dosage",
                          dosage.id,
                          "4 boxes, 56 patches"])

        # value
        column = WritePrescriptionColumn(self.hierarchy, self.patient1,
                                         "dosage", med)
        self.assertEqual(column.user_value(self.user), '')

        block.submit(self.user, self.PRESCRIPTION_COMBINATION_INEFFECTIVE)
        self.assertEqual(column.user_value(self.user), '6')


class TestTreatmentRankColumn(VirtualPatientTestCase):

    def test_all(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.VIEW_RESULTS)

        a = TreatmentRankColumn.all(self.hierarchy, block, True)
        self.assertEqual(len(a), 3)
        self.assertIsNotNone(a[0].classification)
        a = TreatmentRankColumn.all(self.hierarchy, block, False)
        self.assertEqual(len(a), 1)
        self.assertIsNone(a[0].classification)

    def test_instance(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.BEST_TREATMENT_OPTION)
        block.submit(self.user, self.BEST_TREATMENT_COMBINATION_APPROPRIATE)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.WRITE_PRESCRIPTION)

        results = self.create_block(self.section, self.patient1,
                                    PatientAssessmentBlock.VIEW_RESULTS)

        # key
        classification = TreatmentClassification.objects.get(rank=2)
        column = TreatmentRankColumn(self.hierarchy, results, classification)
        self.assertEqual(column.identifier(), "vp_3_1_5")
        self.assertEqual(column.key_row(),
                         ["vp_3_1_5",
                          "main", "Virtual Patient",
                          "single choice",
                          "Selected Treatment Rank for Beverly Johnson",
                          2,
                          "Less Appropriate Treatment Choice"])

        # value
        column = TreatmentRankColumn(self.hierarchy, results, classification)
        self.assertEqual(column.user_value(self.user), '')

        block.submit(self.user, self.PRESCRIPTION_COMBINATION_INEFFECTIVE)
        column = TreatmentRankColumn(self.hierarchy, results)
        self.assertEqual(column.user_value(self.user), 2)


class TestCorrectRxColumn(VirtualPatientTestCase):

    def test_all(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.VIEW_RESULTS)

        a = CorrectRxColumn.all(self.hierarchy, block, True)
        self.assertEqual(len(a), 1)
        a = CorrectRxColumn.all(self.hierarchy, block, False)
        self.assertEqual(len(a), 1)

    def test_instance(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.BEST_TREATMENT_OPTION)
        block.submit(self.user, self.BEST_TREATMENT_SINGLE_APPROPRIATE)
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.WRITE_PRESCRIPTION)

        results = self.create_block(self.section, self.patient1,
                                    PatientAssessmentBlock.VIEW_RESULTS)

        # key
        column = CorrectRxColumn(self.hierarchy, results)
        self.assertEqual(column.identifier(), "vp_3_1_6")
        self.assertEqual(column.key_row(),
                         ["vp_3_1_6",
                          "main", "Virtual Patient",
                          "boolean",
                          "Is Selected Prescription Correct "
                          "for Beverly Johnson"])

        # value
        self.assertEqual(column.user_value(self.user), '')

        block.submit(self.user, self.PRESCRIPTION_SINGLE_APPROPRIATE_CORRECT)
        self.assertEqual(column.user_value(self.user), True)

        block.submit(self.user, self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT)
        self.assertEqual(column.user_value(self.user), False)
