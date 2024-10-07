from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import smart_str
from pagetree.helpers import get_section_from_path
from pagetree.models import Hierarchy, Section
from quizblock.models import Quiz, Question, Answer
from tobaccocessation.main.models import QuestionColumn, UserProfile, \
    clean_header


class UserProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("test_student",
                                             "test@ccnmtl.com",
                                             "testpassword")
        UserProfile.objects.get_or_create(user=self.user,
                                          gender="M",
                                          is_faculty="ST",
                                          institute="I1",
                                          specialty="S2",
                                          hispanic_latino="Y",
                                          year_of_graduation=2015)

        self.hierarchy = Hierarchy(name="main", base_url="/")
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
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)

        self.assertFalse(profile.get_has_visited(self.section1))
        self.assertFalse(profile.get_has_visited(self.section2))

        profile.set_has_visited([self.section1, self.section2])

        self.assertTrue(profile.get_has_visited(self.section1))
        self.assertTrue(profile.get_has_visited(self.section2))

    def test_last_location(self):
        user = User.objects.get(username="test_student")

        # By default, the 1st leaf is returned if there are no visits
        self.assertEqual(user.profile.last_location(), self.section1)

        user.profile.set_has_visited([self.section1])
        self.assertEqual(user.profile.last_location(), self.section1)

        user.profile.set_has_visited([self.section2])
        self.assertEqual(user.profile.last_location(), self.section2)

        user.profile.set_has_visited([self.section1])
        self.assertEqual(user.profile.last_location(), self.section1)

    def test_user_unicode(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)
        uni_name = smart_str(profile)
        self.assertEqual(uni_name, "test_student")

    def test_user_display_name(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)
        display_name = UserProfile.display_name(profile)
        self.assertEqual(display_name, "test_student")

    def test_percent_complete(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)

        self.assertEqual(0, profile.percent_complete())

        profile.set_has_visited([self.root, self.section1])
        self.assertEqual(66, profile.percent_complete())
        profile.set_has_visited([self.section2])
        self.assertEqual(100, profile.percent_complete())

    def test_percent_complete_null_hierarchy(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)
        profile.speciality = "pediatrics"

        self.assertEqual(0, profile.percent_complete())

    def test_is_role_student(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)

        profile.is_faculty = "FA"
        profile.save()
        self.assertFalse(profile.is_role_student())
        self.assertTrue(profile.is_role_faculty())

        profile.is_faculty = "OT"
        profile.save()
        self.assertFalse(profile.is_role_student())
        self.assertFalse(profile.is_role_faculty())

        profile.is_faculty = "ST"
        profile.save()
        self.assertTrue(profile.is_role_student())
        self.assertFalse(profile.is_role_faculty())

    def test_default_role(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)

        self.assertEqual("main", profile.role())

    def test_role(self):
        user = User.objects.get(username="test_student")
        profile = UserProfile.objects.get(user=user)

        # pre-doctoral
        self.assertEqual(profile.role(), "main")

        # verify being a faculty doesn't change this selection
        profile.is_faculty = "FA"
        profile.save()
        self.assertEqual(profile.role(), "main")

        profile.specialty = "S1"
        profile.save()
        self.assertEqual(profile.role(), "general")

        profile.specialty = "S2"  # Pre-Doctoral Student"
        profile.save()
        self.assertEqual(profile.role(), "main")

        profile.specialty = "S3"  # Endodontics
        profile.save()
        self.assertEqual(profile.role(), "endodontics")

        profile.specialty = "S4"  # Oral and Maxillofacial Surgery"
        profile.save()
        self.assertEqual(profile.role(), "surgery")

        profile.specialty = "S5"  # Pediatric Dentistry
        profile.save()
        self.assertEqual(profile.role(), "pediatrics")

        profile.specialty = "S6"  # Periodontics
        profile.save()
        self.assertEqual(profile.role(), "perio")

        profile.specialty = "S7"  # Prosthodontics
        profile.save()
        self.assertEqual(profile.role(), "general")

        profile.specialty = "S8"  # Orthodontics
        profile.save()
        self.assertEqual(profile.role(), "orthodontics")

        profile.specialty = "S9"  # Other
        profile.save()
        self.assertEqual(profile.role(), "main")

        profile.specialty = "S10"  # Dental Public Health
        profile.save()
        self.assertEqual(profile.role(), "main")


class TestQuestionColumn(TestCase):

    def setUp(self):
        self.c = Client()

        self.user = User.objects.create_user("test_student",
                                             "test@ccnmtl.com",
                                             "testpassword")

        get_section_from_path("")  # creates a root if one doesn't exist
        self.hierarchy = Hierarchy.objects.get(name="main")
        self.section = self.hierarchy.get_root().append_child("Foo", "foo")

    def create_quizblock(self, section):
        quiz = Quiz()
        quiz.save()

        self.section.append_pageblock(label="quiz",
                                      css_extra="",
                                      content_object=quiz)
        return quiz

    def test_text_question(self):
        quiz = self.create_quizblock(self.section)

        question = Question.objects.create(
            quiz=quiz, text="foo", question_type="long text")

        column = QuestionColumn(self.hierarchy, question)

        idt = "%s_%s" % (self.hierarchy.id, question.id)
        self.assertEqual(column.identifier(), idt)

        key_row = [idt, "main", "Quiz", "long text", b"foo"]
        self.assertEqual(column.key_row(), key_row)

        # no data
        self.assertEqual(column.user_value(self.user), "")

        data_id = "question%s" % question.id
        data = {data_id: "here is my long text"}
        quiz.submit(self.user, data)
        self.assertEqual(column.user_value(self.user), "here is my long text")

    def test_single_choice_question(self):
        choice_quiz = self.create_quizblock(self.section)

        question = Question.objects.create(
            quiz=choice_quiz, text="foo", question_type="single choice")
        answer = Answer.objects.create(question=question,
                                       value="1", label="one")

        column = QuestionColumn(self.hierarchy, question, answer)

        question_id = "%s_%s" % (self.hierarchy.id, question.id)
        answer_id = "%s_%s_%s" % (self.hierarchy.id, question.id, answer.id)
        self.assertEqual(column.identifier(), answer_id)

        key_row = [question_id, "main", "Quiz", "single choice",
                   b"foo", answer.id, b"one"]
        self.assertEqual(column.key_row(), key_row)

        # no data
        self.assertEqual(column.user_value(self.user), "")

        data_id = "question%s" % question.id
        data = {data_id: "1"}
        choice_quiz.submit(self.user, data)
        self.assertEqual(column.user_value(self.user), answer.id)

    def test_multiple_choice_question(self):
        choice_quiz = self.create_quizblock(self.section)

        question = Question.objects.create(
            quiz=choice_quiz, text="foo", question_type="multiple choice")
        answer1 = Answer.objects.create(question=question,
                                        value="1", label="one")
        answer2 = Answer.objects.create(question=question,
                                        value="2", label="two")
        answer3 = Answer.objects.create(question=question,
                                        value="3", label="three")

        column = QuestionColumn(self.hierarchy, question, answer1)
        column2 = QuestionColumn(self.hierarchy, question, answer2)
        column3 = QuestionColumn(self.hierarchy, question, answer3)

        question_id = "%s_%s" % (self.hierarchy.id, question.id)
        answer_id = "%s_%s_%s" % (self.hierarchy.id, question.id, answer1.id)
        self.assertEqual(column.identifier(), answer_id)

        key_row = [question_id, "main", "Quiz", "multiple choice",
                   b"foo", answer1.id, b"one"]
        self.assertEqual(column.key_row(), key_row)

        # no data
        self.assertEqual(column.user_value(self.user), "")

        data_id = "question%s" % question.id
        data = {data_id: ["2", "1"]}
        choice_quiz.submit(self.user, data)
        self.assertEqual(column.user_value(self.user), answer1.id)
        self.assertEqual(column2.user_value(self.user), answer2.id)
        self.assertEqual(column3.user_value(self.user), "")

    def test_all(self):
        choice_quiz = self.create_quizblock(self.section)
        quest1 = Question.objects.create(
            quiz=choice_quiz, text="foo", question_type="single choice")
        a1 = Answer.objects.create(question=quest1,
                                   value="1", label="one", correct=True)
        a2 = Answer.objects.create(question=quest1,
                                   value="2", label="two")

        text_quiz = self.create_quizblock(self.section)
        quest2 = Question.objects.create(
            quiz=text_quiz, text="foo", question_type="long text")

        columns = QuestionColumn.all(self.hierarchy, self.section, True)
        self.assertEqual(len(columns), 3)
        self.assertEqual(columns[0].question, quest1)
        self.assertEqual(columns[0].answer, a1)
        self.assertEqual(columns[1].question, quest1)
        self.assertEqual(columns[1].answer, a2)
        self.assertEqual(columns[2].question, quest2)
        self.assertEqual(columns[2].answer, None)

        columns = QuestionColumn.all(self.hierarchy, self.section, False)
        self.assertEqual(len(columns), 2)
        self.assertEqual(columns[0].question, quest1)
        self.assertEqual(columns[0].answer, None)
        self.assertEqual(columns[1].question, quest2)
        self.assertEqual(columns[1].answer, None)

    def test_clean_header(self):
        s = "<p></p></div>\n\r<>'\"foobar,"
        self.assertEqual(clean_header(s), b'foobar')
