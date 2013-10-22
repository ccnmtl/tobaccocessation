from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from tobaccocessation.activity_treatment_choice.views import loadstate, savestate
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

class SimpleViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.c.get("/")
        self.assertEquals(response.status_code, 302)
        # for now, we don't care where. really, we
        # are just making sure it's not a 500 error
        # at this point

    def test_smoke(self):
        # run the smoketests. we don't care if they pass
        # or fail, we just want to make sure that the
        # smoketests themselves don't have an error
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)

    def test_load_state(self):
        request = self.factory.get('/load/')
        request.user = self.user
        response = loadstate(request)
        self.assertEqual(response.status_code, 200)

    def test_save_state(self):
        request = self.factory.post('/save/', {'json':'need json'})
        request.user = self.user
        response = savestate(request)
        self.assertEqual(response.status_code, 200)
