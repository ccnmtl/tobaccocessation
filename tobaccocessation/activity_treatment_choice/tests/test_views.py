from tobaccocessation.activity_treatment_choice.views import *
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory


from django.test.client import Client



class ViewTest(TestCase):  # unittest.


    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user('test_student', 'test@ccnmtl.com', 'testpassword')

    def tearDown(self):
        self.user.delete()

    def test_index(self):
        # it should redirect us somewhere.
        self.c = Client()
        response = self.c.get("/")
        self.assertEquals(response.status_code, 302)
        
    def setUp(self):
        '''Set up method for testing views.'''
        self.factory = RequestFactory()
        self.user = User.objects.create_user('somestudent', 'email@email.com', 'somestudent')
        self.user.save()

