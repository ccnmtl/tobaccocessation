from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client


class ViewTest(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')

    def tearDown(self):
        self.user.delete()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.c.get("/")
        self.assertEquals(response.status_code, 302)
