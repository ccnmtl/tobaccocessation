from django.test import TestCase
from pagetree.models import Hierarchy
from pagetree.tests.factories import ModuleFactory, UserFactory

from tobaccocessation.main.tests.factories import UserProfileFactory


class TestViews(TestCase):
    def setUp(self):
        self.user = UserFactory()

        ModuleFactory("main", "/pages/main/")
        hierarchy = Hierarchy.objects.get(name='main')
        self.section = hierarchy.get_root().get_first_leaf()

    def test_index(self):
        # it should redirect us somewhere.
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        # for now, we don't care where. really, we
        # are just making sure it's not a 500 error
        # at this point

    def test_smoke(self):
        self.client.get("/smoketest/")

    def test_page_no_profile(self):
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.templates[0].name,
                         "main/create_profile.html")

    def test_page_profile(self):
        UserProfileFactory(user=self.user)

        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.section.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name,
                         "main/page.html")
