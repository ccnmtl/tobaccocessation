from django.contrib.auth.models import User
from django.test import TestCase
from pagetree.models import Hierarchy, Section
from tobaccocessation.main.models import UserProfile, FlashVideoBlock
import time


class UserProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test_student',
                                             'test@ccnmtl.com',
                                             'testpassword')
        UserProfile.objects.get_or_create(user=self.user)[0]
        self.hierarchy = Hierarchy(name="student", base_url="/")
        self.hierarchy.save()

        self.root = Section.add_root(label="Root", slug="",
                                     hierarchy=self.hierarchy)

        self.root.append_child("Section 1", "section-1")
        self.root.append_child("Section 2", "section-2")

        self.section1 = Section.objects.get(slug="section-1")
        self.section2 = Section.objects.get(slug="section-2")

    def tearDown(self):
        self.user.delete()
        self.hierarchy.delete()

    def test_set_has_visited(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)

        self.assertFalse(profile.get_has_visited(self.section1))
        self.assertFalse(profile.get_has_visited(self.section2))

        profile.set_has_visited([self.section1, self.section2])

        self.assertTrue(profile.get_has_visited(self.section1))
        self.assertTrue(profile.get_has_visited(self.section2))

    def test_last_location(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)

        # By default, the 1st leaf is returned if there are no visits
        self.assertEquals(profile.last_location(), self.section1)

        profile.set_has_visited([self.section1])
        time.sleep(5)
        profile.set_has_visited([self.section2])

        self.assertEquals(profile.last_location(), self.section2)

        profile.set_has_visited([self.section1])
        self.assertEquals(profile.last_location(), self.section1)

    def test_user_unicode(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)
        uni_name = UserProfile.__unicode__(profile)
        self.assertEqual(uni_name, 'test_student')

    def test_user_display_name(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)
        display_name = UserProfile.display_name(profile)
        self.assertEqual(display_name, 'test_student')

    def test_default_role(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)

        self.assertEquals("student", profile.role())

    def test_percent_complete(self):
        user = User.objects.get(username='test_student')
        profile = UserProfile.objects.get(user=user)

        self.assertEquals(0, profile.percent_complete())

        profile.set_has_visited([self.root, self.section1])
        self.assertEquals(66, profile.percent_complete())
        profile.set_has_visited([self.section2])
        self.assertEquals(100, profile.percent_complete())


class FlashVideoBlockTest(TestCase):
    def test_edit_flash_form(self):
        self.flash = FlashVideoBlock(width=4, height=3)
        self.flash.save()
        self.form_test = self.flash.edit_form()
        self.assertIsNotNone(self.form_test)

    def test_block_add_form(self):
        self.flash = FlashVideoBlock(width=4, height=3)
        self.flash.save()
        self.add_form_test = self.flash.add_form()
        self.assertIsNotNone(self.add_form_test)

    # def test_create_flash_pageblock(self):
    #     self.c = Client()
    #     self.response = self.c.post("/")
    #     self.create_flash_block = FlashVideoBlock.create(self.response)
    #     self.assertIsNotNone(self.create_flash_block)
