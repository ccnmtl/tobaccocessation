from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client, RequestFactory
from pagetree.helpers import get_section_from_path
from pagetree.models import Hierarchy
from tobaccocessation.activity_virtual_patient.models import \
    PatientAssessmentBlock, Patient
from tobaccocessation.main.models import UserProfile


class TestPatientAssessmentBlock(TestCase):
    fixtures = ['virtualpatient.json']

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
                                          hispanic_latino='Y',
                                          year_of_graduation=2015,
                                          consent=True)

        self.patient1 = Patient.objects.get(display_order=1)
        self.patient4 = Patient.objects.get(display_order=4)

        get_section_from_path("")  # creates a root if one doesn't exist
        hierarchy = Hierarchy.objects.get(name='main')
        self.section = hierarchy.get_root().append_child('Bar Baz', 'bar-baz')

        get_section_from_path("", "alt")  # creates a root if one doesn't exist
        alt_hierarchy = Hierarchy.objects.get(name='alt')
        self.alt_section = alt_hierarchy.get_root().append_child(
            'Sam I Am', 'sam-i-am')

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
        self.assertEquals(form.initial['patient'],
                          self.patient1.id)
        self.assertEquals(form.initial['view'],
                          PatientAssessmentBlock.CLASSIFY_TREATMENTS)

    def test_create(self):
        rf = RequestFactory()
        post_request = rf.post('/',
                               {'patient': '4',
                                'view': PatientAssessmentBlock.VIEW_RESULTS})
        block = PatientAssessmentBlock.create(post_request)
        self.assertEquals(block.view, PatientAssessmentBlock.VIEW_RESULTS)
        self.assertEquals(block.patient, self.patient4)

    def test_edit(self):
        block = PatientAssessmentBlock(
            patient=self.patient1,
            view=PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.save()
        self.assertEquals(block.patient, self.patient1)
        self.assertEquals(block.view,
                          PatientAssessmentBlock.CLASSIFY_TREATMENTS)

        rf = RequestFactory()
        post_request = rf.post('/',
                               {'patient': '4',
                                'view': PatientAssessmentBlock.VIEW_RESULTS})

        block.edit(post_request.POST, None)
        self.assertEquals(block.patient, self.patient4)
        self.assertEquals(block.view, PatientAssessmentBlock.VIEW_RESULTS)

    CLASSIFY_TREATMENTS_DATA = {
        u'nicotinepatch': u'appropriate',
        u'nicotinegum': u'ineffective',
        u'nicotineinhaler': u'ineffective',
        u'nicotinenasalspray': u'harmful',
        u'bupropion': u'appropriate',
        u'varenicline': u'appropriate',
        u'combination': u'appropriate'
    }

    def create_block(self, section, patient, view_type):
        block = PatientAssessmentBlock(patient=patient, view=view_type)
        block.save()

        section.append_pageblock(label="virtual patient",
                                 css_extra="",
                                 content_object=block)

        return block

    def test_classify_treatments_view(self):
        block = self.create_block(self.section, self.patient1,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
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
        self.assertTrue(treatments[3].classification, 'harmful')
        self.assertTrue(treatments[4].classification, 'appropriate')
        self.assertTrue(treatments[5].classification, 'appropriate')
        self.assertTrue(treatments[6].classification, 'appropriate')
        for t in treatments:
            self.assertFalse(hasattr(t, 'prescribe'))
            self.assertFalse(hasattr(t, 'combination'))

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
        self.assertEquals(len(medications), 1)
        self.assertEquals(medications[0]['rx_count'], 1)
        self.assertEquals(medications[0]['tag'], 'nicotinepatch')
        self.assertEquals(medications[0]['name'], 'Nicotine Patch')
        self.assertEquals(len(medications[0]['choices']), 1)

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
        self.assertEquals(len(medications), 1)
        self.assertEquals(medications[0]['rx_count'], 1)
        self.assertEquals(medications[0]['tag'], 'nicotinepatch')
        self.assertEquals(medications[0]['name'], 'Nicotine Patch')
        self.assertEquals(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertEquals(int(obj.selected_concentration), 5)
        self.assertEquals(int(obj.selected_dosage), 6)
        self.assertEquals(obj.selected_concentration_label, u'21 mg')
        self.assertEquals(obj.selected_dosage_label, u'2 boxes, 28 patches')

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
        self.assertEquals(len(medications), 1)
        self.assertEquals(medications[0]['rx_count'], 2)
        self.assertEquals(medications[0]['tag'], 'varenicline')
        self.assertEquals(medications[0]['name'], 'Varenicline')
        self.assertEquals(len(medications[0]['choices']), 2)

        obj = medications[0]['choices'][0]
        self.assertEquals(int(obj.selected_concentration), 21)
        self.assertEquals(int(obj.selected_dosage), 26)
        obj = medications[0]['choices'][1]
        self.assertEquals(int(obj.selected_concentration), 33)
        self.assertEquals(int(obj.selected_dosage), 31)

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
        self.assertEquals(len(medications), 2)

        self.assertEquals(medications[0]['rx_count'], 1)
        self.assertEquals(medications[0]['tag'], 'nicotinepatch')
        self.assertEquals(medications[0]['name'], 'Nicotine Patch')
        self.assertEquals(len(medications[0]['choices']), 1)

        obj = medications[0]['choices'][0]
        self.assertEquals(int(obj.selected_concentration), 5)
        self.assertEquals(int(obj.selected_dosage), 6)

        self.assertEquals(medications[1]['rx_count'], 2)
        self.assertEquals(medications[1]['tag'], 'varenicline')
        self.assertEquals(medications[1]['name'], 'Varenicline')
        self.assertEquals(len(medications[1]['choices']), 2)

        obj = medications[1]['choices'][0]
        self.assertEquals(int(obj.selected_concentration), 21)
        self.assertEquals(int(obj.selected_dosage), 26)
        obj = medications[1]['choices'][1]
        self.assertEquals(int(obj.selected_concentration), 33)
        self.assertEquals(int(obj.selected_dosage), 31)

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
        self.assertEquals(feedback.classification.rank, 1)

        # Incorrect - both concentration & dosage
        block.submit(self.user, self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEquals(feedback.classification.rank, 1)

        # Incorrect - concentration
        block.submit(
            self.user,
            self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT_CONCENTRATION)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEquals(feedback.classification.rank, 1)

        # Incorrect - dosage
        block.submit(self.user,
                     self.PRESCRIPTION_SINGLE_APPROPRIATE_INCORRECT_DOSAGE)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEquals(feedback.classification.rank, 1)

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
        self.assertEquals(feedback.classification.rank, 1)

        # Incorrect - both medicines
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_INCORRECT)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEquals(feedback.classification.rank, 1)

        # Incorrect - medicine 1
        block.submit(
            self.user,
            self.PRESCRIPTION_DOUBLE_APPROPRIATE_INCORRECT_RX1)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEquals(feedback.classification.rank, 1)

        # Incorrect - medicine 2
        block.submit(self.user,
                     self.PRESCRIPTION_DOUBLE_APPROPRIATE_INCORRECT_RX2)
        feedback = block.feedback(self.user)
        self.assertFalse(feedback.correct_dosage)
        self.assertEquals(feedback.classification.rank, 1)

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
        self.assertEquals(feedback.classification.rank, 2)
        self.assertFalse(feedback.combination_therapy)

    def test_feedback_double_harmful(self):
        # "correct" is irrelevant
        # combination is relevant
        block = self.create_block(self.section,
                                  self.patient4,
                                  PatientAssessmentBlock.CLASSIFY_TREATMENTS)
        block.submit(self.user, self.CLASSIFY_TREATMENTS_DATA)

        block.view = PatientAssessmentBlock.BEST_TREATMENT_OPTION
        block.submit(self.user, self.BEST_TREATMENT_DOUBLE)

        block.view = PatientAssessmentBlock.WRITE_PRESCRIPTION

        # Correct
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_CORRECT)
        feedback = block.feedback(self.user)
        self.assertEquals(feedback.classification.rank, 3)

        # Incorrect - both medicines
        block.submit(self.user, self.PRESCRIPTION_DOUBLE_INCORRECT)
        feedback = block.feedback(self.user)
        self.assertEquals(feedback.classification.rank, 3)

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
        self.assertEquals(feedback.classification.rank, 2)
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
        response = self.c.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.request["PATH_INFO"], "/")
        self.assertFalse(block.unlocked(self.user))
        self.assertTrue(alt_block.unlocked(self.user))
