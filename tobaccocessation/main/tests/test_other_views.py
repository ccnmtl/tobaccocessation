from django.contrib.auth.models import User
import json
import simplejson as json
from django.test import TestCase, RequestFactory
from django.test.client import Client
from tobaccocessation.activity_prescription_writing.views import loadstate, savestate
from django.contrib.auth.models import User
from pagetree.models import Hierarchy, Section


class TestOtherSimpleViews(TestCase):
    '''Made this extra class to avoid name space collisions with treatment choice loadstate and savestate.'''
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')
        self.user.save()

        self.hierarchy = Hierarchy(name="main", base_url="/")
        self.hierarchy.save()

        root = Section.add_root(label="Root", slug="",
                                hierarchy=self.hierarchy)

        root.append_child("Section 1", "section-1")
        root.append_child("Section 2", "section-2")

        self.section1 = Section.objects.get(slug="section-1")
        self.section2 = Section.objects.get(slug="section-2")

        self.staff = User.objects.create_user('test_staff',
                                             'test@ccnmtl.com',
                                             'staffpassword')
        self.staff.save()


    def tearDown(self):
        self.user.delete()

    def test_perscription_writing_load_state(self):
        request = self.factory.get('/activity/perscription/load/')
        request.user = self.user
        response = loadstate(request)
        self.assertEqual(response.status_code, 200)




    # def test_perscription_writing_save_state(self):
    #     json_data = json.dumps(['json', {'need json': ('garbage', None, 1.0, 2)}]) #\'json\'
    #     request = self.factory.post('/activity/perscription/save/', {"\json":'need json'}, content_type="application/json")
    #     request.user = self.user
    #     response = savestate(request)
    #     self.assertEqual(response.status_code, 200)


