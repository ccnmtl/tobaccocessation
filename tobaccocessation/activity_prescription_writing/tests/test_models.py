from django.contrib.auth.models import User
from django.test import TestCase
from tobaccocessation.activity_prescription_writing.models import Block, \
    Medication


class TestBlock(TestCase):
    fixtures = ['prescriptionwriting.json']

    def test_default_settings(self):
        block = Block(medication_name='Nicotine Patch')
        block.save()

        self.assertTrue(block.needs_submit())
        self.assertTrue(block.redirect_to_self_on_submit())

    def test_single_prescription(self):
        user = User.objects.create(username="test")
        block = Block(medication_name='Nicotine Patch')
        block.save()

        self.assertFalse(block.unlocked(user))

        meds = block.medication()
        self.assertEquals(len(meds), 1)
        self.assertEquals(meds[0],
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
        self.assertEquals(len(meds), 2)
        self.assertEquals(meds[0].refills, 0)
        self.assertEquals(meds[0].dispensing, '11 tablets')

        self.assertEquals(meds[0].refills, 0)
        self.assertEquals(meds[0].dispensing, '11 tablets')
        self.assertEquals(meds[0].dosage, '0.5mg')

        self.assertEquals(meds[1].refills, 2)
        self.assertEquals(meds[1].dispensing, '56 tablets')
        self.assertEquals(meds[1].dosage, '1.0mg')

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
