from django.test import TestCase
from tobaccocessation.activity_treatment_choice.models import Block


class TestModelsOther(TestCase):
    def setUp(self):
        self.block = Block()
        self.block.save()

    def test_block_submit_false(self):
        self.assertEquals(self.block.needs_submit(), False)

    def test_block_edit_form(self):
        self.form_test = self.block.edit_form()
        self.assertIsNotNone(self.form_test)

    def test_block_add_form(self):
        self.add_form_test = self.block.add_form()
        self.assertIsNotNone(self.add_form_test)


    # def test_block_create(self):
    #     c = Client()
    #     self.request = c.post('/some_page/', {
    #         'medication_name': 'medication name', 'show_correct': False})
    #     self.block_create = self.block.create(self.request)
    #     self.assertIsNotNone(self.block_create)
