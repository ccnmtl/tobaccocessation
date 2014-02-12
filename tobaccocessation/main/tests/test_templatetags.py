from django.contrib.auth.models import User
from django.test import TestCase
from quizblock.models import Quiz, Question, Answer, Submission, Response
from tobaccocessation.main.templatetags.quizcorrect import IfQuizCorrectNode, \
    IfQuizCompleteNode


class FakeRequest(object):
    pass


class MockNodeList(object):
    def __init__(self):
        self.rendered = False

    def render(self, c):
        self.rendered = True


class IfQuizCompleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create()
        self.request = FakeRequest()

    def assert_render_true(self):
        nl1 = MockNodeList()
        nl2 = MockNodeList()

        node = IfQuizCompleteNode('quiz', nl1, nl2)
        self.request.user = self.user
        context = dict(request=self.request, quiz=self.quiz)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nl1.rendered)
        self.assertFalse(nl2.rendered)

    def assert_render_false(self):
        nl1 = MockNodeList()
        nl2 = MockNodeList()
        node = IfQuizCompleteNode('quiz', nl1, nl2)
        self.request.user = self.user
        context = dict(request=self.request, quiz=self.quiz)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertFalse(nl1.rendered)
        self.assertTrue(nl2.rendered)

    def test_quiz_complete(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        # No submission
        self.assert_render_false()

        # Empty submission
        s = Submission.objects.create(quiz=self.quiz, user=self.user)
        self.assert_render_false()

        # ques1 response (single choice)
        Response.objects.create(question=ques1, submission=s, value="a")
        self.assert_render_false()

        # ques2 response - 1 answer
        Response.objects.create(question=ques2, submission=s, value="a")
        self.assert_render_true()

        # ques2 response - 2 answers
        Response.objects.create(question=ques2, submission=s, value="b")
        self.assert_render_true()

        # ques2 response - 3 answers
        Response.objects.create(question=ques2, submission=s, value="b")
        self.assert_render_true()


class IfQuizCorrectTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create()
        self.request = FakeRequest()

    def assert_render_true(self):
        nl1 = MockNodeList()
        nl2 = MockNodeList()
        node = IfQuizCorrectNode('quiz', nl1, nl2)
        self.request.user = self.user
        context = dict(request=self.request, quiz=self.quiz)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nl1.rendered)
        self.assertFalse(nl2.rendered)

    def assert_render_false(self):
        nl1 = MockNodeList()
        nl2 = MockNodeList()
        node = IfQuizCorrectNode('quiz', nl1, nl2)
        self.request.user = self.user
        context = dict(request=self.request, quiz=self.quiz)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertFalse(nl1.rendered)
        self.assertTrue(nl2.rendered)

    def test_choice_single_answer_noresponse(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        self.assert_render_false()
        Submission.objects.create(quiz=self.quiz, user=self.user)
        self.assert_render_false()

    def test_choice_single_answer_correct(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="a")
        self.assert_render_true()

    def test_choice_single_answer_incorrect(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="b")
        self.assert_render_false()

    def test_choice_multiple_answer_noresponse(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")
        Answer.objects.create(question=ques1, label="c",
                              value="c", correct=True)

        self.assert_render_false()

        Submission.objects.create(quiz=self.quiz, user=self.user)
        self.assert_render_false()

    def test_choice_multiple_answer_incomplete(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")
        Answer.objects.create(question=ques1, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="b")
        self.assert_render_false()
        Response.objects.create(question=ques1, submission=sub, value="a")
        self.assert_render_false()
        Response.objects.create(question=ques1, submission=sub, value="c")
        self.assert_render_false()

    def test_choice_multiple_answer_correct(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")
        Answer.objects.create(question=ques1, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="a")
        Response.objects.create(question=ques1, submission=sub, value="c")
        self.assert_render_true()

    def test_choice_multiple_answer_incorrect(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")
        Answer.objects.create(question=ques1, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="a")
        Response.objects.create(question=ques1, submission=sub, value="b")

        self.assert_render_false()

    def test_quiz_noresponse(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        self.assert_render_false()

        Submission.objects.create(quiz=self.quiz, user=self.user)
        self.assert_render_false()

    def test_quiz_incomplete_response(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="a")

        self.assert_render_false()

    def test_quiz_incomplete_response2(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques2, submission=sub, value="b")

        self.assert_render_false()

    def test_quiz_correct(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="a")
        Response.objects.create(question=ques2, submission=sub, value="a")
        Response.objects.create(question=ques2, submission=sub, value="c")

        self.assert_render_true()

    def test_quiz_incorrect(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="a")
        Response.objects.create(question=ques2, submission=sub, value="b")
        Response.objects.create(question=ques2, submission=sub, value="c")

        self.assert_render_false()

    def test_quiz_incorrect2(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="b")
        Response.objects.create(question=ques2, submission=sub, value="a")
        Response.objects.create(question=ques2, submission=sub, value="c")

        self.assert_render_false()

    def test_quiz_incorrect3(self):
        ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
                                        question_type="single choice")
        Answer.objects.create(question=ques1, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques1, label="b", value="b")

        ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
                                        question_type="multiple choice")
        Answer.objects.create(question=ques2, label="a",
                              value="a", correct=True)
        Answer.objects.create(question=ques2, label="b", value="b")
        Answer.objects.create(question=ques2, label="c",
                              value="c", correct=True)

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=ques1, submission=sub, value="b")
        Response.objects.create(question=ques2, submission=sub, value="b")
        Response.objects.create(question=ques2, submission=sub, value="c")

        self.assert_render_false()
