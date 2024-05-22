from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.utils.encoding import smart_str
from pagetree.helpers import get_section_from_path
from pagetree.models import Hierarchy
from tobaccocessation.activity_prescription_writing.models import Block, \
    Medication, PrescriptionColumn


class TestBlock(TestCase):
    fixtures = ['prescriptionwriting.json']

    def test_medication(self):
        med = Medication.objects.create(name="something",
                                        dosage="dosage",
                                        dispensing="dispensing",
                                        signature="signature",
                                        refills=1,
                                        sort_order=10)

        self.assertEqual(smart_str(med), "something")
        self.assertEqual(med.rx_count, 1)

    def test_default(self):
        block = Block(medication_name='Nicotine Patch')
        block.save()

        self.assertEqual(block.medication_name, 'Nicotine Patch')
        self.assertTrue(block.allow_redo)
        self.assertTrue(block.needs_submit())
        self.assertTrue(block.redirect_to_self_on_submit())

    def test_add_form(self):
        form = Block.add_form()
        self.assertIsNotNone(form)
        self.assertTrue('medication_name' in form.fields)
        self.assertTrue('allow_redo' in form.fields)

    def test_edit_form(self):
        block = Block(medication_name='Nicotine Patch')
        block.save()

        form = block.edit_form()
        self.assertIsNotNone(form)
        self.assertTrue('medication_name' in form.fields)
        self.assertTrue('allow_redo' in form.fields)
        self.assertEqual(form.initial['medication_name'], 'Nicotine Patch')
        self.assertTrue(form.initial['allow_redo'])

    def test_create(self):
        rf = RequestFactory()
        post_request = rf.post('/',
                               {'medication_name': 'Nicotine Patch',
                                'allow_redo': False})
        block = Block.create(post_request)
        self.assertEqual(block.medication_name, 'Nicotine Patch')
        self.assertFalse(block.allow_redo)

    def test_edit(self):
        block = Block(medication_name='Nicotine Patch')
        block.save()
        self.assertEqual(block.medication_name, 'Nicotine Patch')
        self.assertTrue(block.allow_redo)

        rf = RequestFactory()
        post_request = rf.post('/',
                               {'medication_name': 'Nicotine Gum',
                                'allow_redo': False})

        block.edit(post_request.POST, None)
        self.assertEqual(block.medication_name, 'Nicotine Gum')
        self.assertFalse(block.allow_redo)

    def test_single_prescription(self):
        user = User.objects.create(username="test")
        block = Block(medication_name='Nicotine Patch')
        block.save()

        self.assertFalse(block.unlocked(user))

        # clear with no data
        block.clear_user_submissions(user)
        self.assertFalse(block.unlocked(user))

        meds = block.medication()
        self.assertEqual(len(meds), 1)
        self.assertEqual(meds[0],
                         Medication.objects.get(name='Nicotine Patch'))

        data = {
            'dosage': '1.0mg',
            'disp': '5 tablets',
            'sig': 'instructions go here',
            'refills': '2'
        }
        block.submit(user, data)
        self.assertTrue(block.unlocked(user))

        block.clear_user_submissions(user)
        self.assertFalse(block.unlocked(user))

    def test_double_prescription(self):
        user = User.objects.create(username="test")
        block = Block(medication_name='Varenicline')
        block.save()

        self.assertFalse(block.unlocked(user))

        meds = block.medication()
        self.assertEqual(len(meds), 2)
        self.assertEqual(meds[0].refills, 0)
        self.assertEqual(meds[0].dispensing, '11 tablets')

        self.assertEqual(meds[0].refills, 0)
        self.assertEqual(meds[0].dispensing, '11 tablets')
        self.assertEqual(meds[0].dosage, '0.5mg')

        self.assertEqual(meds[1].refills, 2)
        self.assertEqual(meds[1].dispensing, '56 tablets')
        self.assertEqual(meds[1].dosage, '1.0mg')

        data = {
            'dosage': '0.5mg',
            'disp': '5 tablets',
            'sig': 'instructions go here',
            'refills': '0',
            'dosage_2': '1.0mg',
            'disp_2': '56 tablets',
            'sig_2': 'more instructions go here',
            'refills_2': '2'
        }
        block.submit(user, data)
        self.assertTrue(block.unlocked(user))

        block.clear_user_submissions(user)
        self.assertFalse(block.unlocked(user))

    def test_interaction(self):
        user = User.objects.create(username="test")
        varenicline1 = Block(medication_name='Varenicline')
        varenicline1.save()

        varenicline2 = Block(medication_name='Varenicline')
        varenicline2.save()

        patch = Block(medication_name='Nicotine Patch')
        patch.save()

        self.assertFalse(varenicline1.unlocked(user))
        self.assertFalse(varenicline2.unlocked(user))
        self.assertFalse(patch.unlocked(user))

        data = {
            'dosage': '0.5mg',
            'disp': '5 tablets',
            'sig': 'instructions go here',
            'refills': '0',
            'dosage_2': '1.0mg',
            'disp_2': '56 tablets',
            'sig_2': 'more instructions go here',
            'refills_2': '2'
        }
        varenicline1.submit(user, data)
        varenicline2.submit(user, data)
        patch.submit(user, data)

        self.assertTrue(varenicline1.unlocked(user))
        self.assertTrue(varenicline2.unlocked(user))
        self.assertTrue(patch.unlocked(user))

        varenicline1.clear_user_submissions(user)
        self.assertFalse(varenicline1.unlocked(user))
        self.assertTrue(varenicline2.unlocked(user))
        self.assertTrue(patch.unlocked(user))

        patch.clear_user_submissions(user)
        self.assertFalse(varenicline1.unlocked(user))
        self.assertTrue(varenicline2.unlocked(user))
        self.assertFalse(patch.unlocked(user))


class TestPrescriptionColumn(TestCase):
    fixtures = ['prescriptionwriting.json']

    def setUp(self):
        self.c = Client()

        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')

        get_section_from_path("")  # creates a root if one doesn't exist
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().append_child('Foo', 'foo')

    def create_block(self, section, medication_name):
        block = Block(medication_name=medication_name)
        block.save()

        self.section.append_pageblock(label="prescription writing",
                                      css_extra="",
                                      content_object=block)
        return block

    def test_instance(self):
        medication_name = 'Nicotine Patch'
        medication = Medication.objects.get(name=medication_name)
        block = self.create_block(self.section, medication_name)

        column = PrescriptionColumn(self.hierarchy, block, medication, "sig")

        idt = "%s_%s_sig" % (self.hierarchy.id, medication.id)
        self.assertEqual(column.identifier(), idt)

        key_row = [idt, "main", 'Prescription Writing Exercise',
                   'short text', 'Nicotine Patch sig']
        self.assertEqual(column.key_row(), key_row)

    def test_user_value_none(self):
        medication_name = 'Varenicline'
        med = Medication.objects.get(name=medication_name,
                                     rx_count__gt=0)
        block = self.create_block(self.section, medication_name)

        column = PrescriptionColumn(self.hierarchy, block, med, "dosage_2")
        # no data
        self.assertEqual(column.user_value(self.user), '')

    def test_user_value_single(self):
        medication_name = 'Nicotine Patch'
        med = Medication.objects.get(name=medication_name)
        block = self.create_block(self.section, medication_name)
        column = PrescriptionColumn(self.hierarchy, block, med, "sig")

        data = {
            'dosage': '1.0mg',
            'disp': '5 tablets',
            'sig': 'instructions go here',
            'refills': '2'
        }
        block.submit(self.user, data)
        self.assertEqual(column.user_value(self.user), 'instructions go here')

    def test_user_value_double(self):
        medication_name = 'Varenicline'
        med = Medication.objects.get(name=medication_name, rx_count__gt=0)
        block = self.create_block(self.section, medication_name)
        column = PrescriptionColumn(self.hierarchy, block, med, "dosage_2")

        data = {
            'dosage': '0.5mg',
            'disp': '5 tablets',
            'sig': 'instructions go here',
            'refills': '0',
            'dosage_2': '1.0mg',
            'disp_2': '56 tablets',
            'sig_2': 'more instructions go here',
            'refills_2': '2'
        }
        block.submit(self.user, data)
        self.assertEqual(column.user_value(self.user), '1.0mg')

    def test_all_single(self):
        self.create_block(self.section, "Bupropion")
        columns = PrescriptionColumn.all(self.hierarchy, self.section, True)
        self.assertEqual(len(columns), 4)
        self.assertEqual(columns[0].field, "dosage")
        self.assertEqual(columns[0].medication.name, "Bupropion")
        self.assertEqual(columns[0].hierarchy.name, "main")

        self.assertEqual(columns[1].field, "disp")
        self.assertEqual(columns[2].field, "sig")
        self.assertEqual(columns[3].field, "refills")

    def test_all_double(self):
        self.create_block(self.section, "Varenicline")
        columns = PrescriptionColumn.all(self.hierarchy, self.section, True)
        self.assertEqual(len(columns), 8)
        self.assertEqual(columns[0].field, "dosage")
        self.assertEqual(columns[0].medication.name, "Varenicline")
        self.assertEqual(columns[0].hierarchy.name, "main")

        self.assertEqual(columns[1].field, "disp")
        self.assertEqual(columns[2].field, "sig")
        self.assertEqual(columns[3].field, "refills")

        self.assertEqual(columns[4].field, "dosage_2")
        self.assertEqual(columns[5].field, "disp_2")
        self.assertEqual(columns[6].field, "sig_2")
        self.assertEqual(columns[7].field, "refills_2")
