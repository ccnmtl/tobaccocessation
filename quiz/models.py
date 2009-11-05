from django.db import models
from pagetree.models import PageBlock
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django import forms
from datetime import datetime
from django.core.urlresolvers import reverse


class Quiz(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    description = models.TextField(blank=True)
    rhetorical = models.BooleanField(default=False)
    template_file = "quiz/quizblock.html"

    display_name = "Quiz"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return not self.rhetorical

    def submit(self,user,data):
        """ a big open question here is whether we should
        be validating submitted answers here, on submission, 
        or let them submit whatever garbage they want and only
        worry about it when we show the admins the results """
        s = Submission.objects.create(quiz=self,user=user)
        for k in data.keys():
            if k.startswith('question'):
                qid = int(k[len('question'):])
                question = Question.objects.get(id=qid)
                response = Response.objects.create(
                    submission=s,
                    question=question,
                    value=data[k])

    def unlocked(self,user):
        # meaning that the user can proceed *past* this one,
        # not that they can access this one. careful.
        if (self.rhetorical):
            return True
        
        return Submission.objects.filter(quiz=self,user=user).count() > 0
    
    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea(),
                                          initial=self.description)
            rhetorical = forms.BooleanField(initial=self.rhetorical)
            alt_text = "<a href=\"" + reverse("edit-quiz",args=[self.id]) + "\">manage questions/answers</a>" 
        return EditForm()

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
            rhetorical = forms.BooleanField()
        return AddForm()

    @classmethod
    def create(self,request):
        return Quiz.objects.create(description=request.POST.get('description',''),
                                   rhetorical=request.POST.get('rhetorical',''))

    def edit(self,vals,files):
        self.description = vals.get('description','')
        self.rhetorical = vals.get('rhetorical','')
        self.save()

    def add_question_form(self,request=None):
        class AddQuestionForm(forms.ModelForm):
            class Meta:
                model = Question
                exclude = ("quiz","ordinality")
        return AddQuestionForm(request)

    def update_questions_order(self,question_ids):
        for i,qid in enumerate(question_ids):
            question = Question.objects.get(id=qid)
            question.ordinality = i + 1
            question.save()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz)
    text = models.TextField()
    question_type = models.CharField(max_length=256,
                                     choices=(("multiple choice","Multiple Choice: Multiple answers"),
                                              ("single choice","Multiple Choice: Single answer"),
                                              ("short text","Short Text"),
                                              ("long text","Long Text"),
                                              ))
    ordinality = models.IntegerField(default=1)
    explanation = models.TextField(blank=True)
    intro_text = models.TextField(blank=True)

    class Meta:
        ordering = ('quiz','ordinality')

    def __unicode__(self):
        return self.text

    def add_answer_form(self,request=None):
        class AddAnswerForm(forms.ModelForm):
            class Meta:
                model = Answer
                exclude = ("question","ordinality")
        return AddAnswerForm(request)

    def correct_answer_number(self):
        if self.question_type != "single choice":
            return None
        return self.answer_set.filter(correct=True)[0].ordinality

    def correct_answer_letter(self):
        if self.question_type != "single choice" or self.answer_set.count() == 0:
            return None
        return chr(ord('A') + self.correct_answer_number() - 1)

    def update_answers_order(self,answer_ids):
        for i,aid in enumerate(answer_ids):
            answer = Answer.objects.get(id=aid)
            answer.ordinality = i + 1
            answer.save()

class Answer(models.Model):
    question = models.ForeignKey(Question)
    ordinality = models.IntegerField(default=1)
    value = models.CharField(max_length=256,blank=True)
    label = models.TextField(blank=True)
    correct = models.BooleanField(default=False)

    class Meta:
        ordering = ('question','ordinality')

    def __unicode__(self):
        return self.label

class Submission(models.Model):
    quiz = models.ForeignKey(Quiz)
    user = models.ForeignKey(User)
    submitted = models.DateTimeField(default=datetime.now)

class Response(models.Model):
    question = models.ForeignKey(Question)
    submission = models.ForeignKey(Submission)
    value = models.TextField(blank=True)

    def __unicode__(self):
        return "response to %s by %s at %s" % (unicode(self.question),unicode(self.user),self.submitted)

