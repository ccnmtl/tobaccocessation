from django.contrib.auth.models import User
from django.test import TestCase
from tobaccocessation.activity_prescription_writing.models import Block
from tobaccocessation.activity_prescription_writing.\
    templatetags.prescription_state import GetPrescription


class FakeRequest(object):
    pass


class GetPrescriptionNodeTest(TestCase):
    fixtures = ['prescriptionwriting.json']

    def setUp(self):
        self.block = Block(medication_name='Nicotine Patch')
        self.block.save()

        self.user = User.objects.create(username="test")

    def test_render_nostate(self):
        request = FakeRequest()
        request.user = self.user

        node = GetPrescription('block', 'state')
        context = dict(request=request, block=self.block)
        result = node.render(context)
        self.assertEqual(result, '')
        self.assertTrue('state' in context)

        keys = context['state'].keys()
        self.assertFalse('dosage' in keys)
        self.assertFalse('sig' in keys)
        self.assertFalse('disp' in keys)
        self.assertFalse('refills' in keys)

        self.assertTrue('complete' in keys)
        self.assertFalse(context['state']['complete'])

    def test_render_state(self):
        data = {
            'dosage': '1.0mg',
            'disp': '5 tablets',
            'sig': 'instructions go here',
            'refills': '2'
        }
        self.block.submit(self.user, data)

        request = FakeRequest()
        request.user = self.user

        node = GetPrescription('block', 'state')
        context = dict(request=request, block=self.block)
        result = node.render(context)
        self.assertEqual(result, '')
        self.assertTrue('state' in context)

        state = context['state']
        self.assertEquals(state['dosage'], '1.0mg')
        self.assertEquals(state['disp'], '5 tablets')
        self.assertEquals(state['sig'], 'instructions go here')
        self.assertEquals(state['refills'], '2')
        self.assertTrue(state['complete'])
