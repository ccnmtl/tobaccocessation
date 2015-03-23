from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test.client import Client
from pagetree.models import Hierarchy, Section
from tobaccocessation.main.models import UserProfile


class TestViews(TestCase):
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

    def test_accessible(self):
        pass
        # Need better test...

    def test_is_accessible(self):
        pass

    def test_clear_state(self):
        pass

    def test_consent_no_profile(self):
        self.c = Client()
        self.c.login(username='test_student', password='testpassword')
        self.response = self.c.get('/', follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertEquals(self.response.redirect_chain[0][1], 302)
        self.assertEquals(self.response.templates[0].name,
                          "main/create_profile.html")

    def test_consent_incomplete_profile(self):
        # User has a profile, but does not have "consent" or other
        # special fields filled out. Redirect to create profile
        UserProfile.objects.create(user=self.user,
                                   gender='M',
                                   is_faculty='ST',
                                   institute='I1',
                                   specialty='S1',
                                   hispanic_latino='Y',
                                   year_of_graduation=2015,
                                   consent_participant=False,
                                   consent_not_participant=False)

        self.c = Client()
        self.c.login(username='test_student', password='testpassword')
        self.response = self.c.get('/', follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertEquals(self.response.templates[0].name,
                          "main/create_profile.html")
        self.assertEquals(self.response.redirect_chain[0][1], 302)

    def test_consent_complete_profile(self):
        # User has a complete profile
        profile = UserProfile.objects.create(user=self.user,
                                             gender='M',
                                             is_faculty='ST',
                                             institute='I1',
                                             specialty='S1',
                                             hispanic_latino='Y',
                                             year_of_graduation=2015,
                                             consent_participant=True,
                                             consent_not_participant=False)
        profile.gender = 'F'
        profile.is_faculty = 'ST'
        profile.specialty = 'S10'
        profile.year_of_graduation = 2014
        profile.consent_participant = True
        profile.consent_not_participant = False
        profile.save()

        self.c = Client()
        self.c.login(username='test_student', password='testpassword')
        self.response = self.c.get('/', follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertEquals(self.response.templates[0].name,
                          "main/index.html")
        self.assertEquals(len(self.response.redirect_chain), 0)
