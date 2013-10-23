from django.test import TestCase
from django.test.client import Client
from tobaccocessation.activity_prescription_writing.models import Medication, Block

class TestModelsNoUser(TestCase):
    def setUp(self):
        self.medication = Medication(name="medication name", refills=2, sort_order=2, rx_count=1)
        self.medication.save()
        self.block = Block(medication_name="block medication")
        self.block.save()

    def test_medication(self):
       	self.assertEquals("medication name", unicode(self.medication))

    def test_block_submit_false(self):
        self.assertEquals(self.block.needs_submit(), False)

    # def test_block_create(self):
    #     c = Client()
    #     self.request = c.post('/some_page/', {'medication_name': 'medication name', 'show_correct': False})
    #     self.block_create = self.block.create(self.request)
    #     self.assertIsNotNone(self.block_create)

    def test_block_edit_form(self):
        self.form_test = self.block.edit_form()
        self.assertIsNotNone(self.form_test)

    def test_block_add_form(self):
        self.add_form_test = self.block.add_form()
        self.assertIsNotNone(self.add_form_test)


    def test_block_medication_method(self):
        self.test_medication = self.block.medication()
        self.assertIsNotNone(self.test_medication)
