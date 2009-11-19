from models import Quiz, Question, Answer, ActivityState
from django.contrib.auth.decorators import permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from pagetree.models import Hierarchy
from django.core.urlresolvers import reverse
from django.utils import simplejson

class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            if type(items) == type({}):
                return render_to_response(self.template_name, items, context_instance=RequestContext(request))
            else:
                return items

        return rendered_func

def get_hierarchy():
    return Hierarchy.objects.get_or_create(name="main",defaults=dict(base_url="/"))[0]

@rendered_with('quiz/edit_quiz.html')
def edit_quiz(request,id):
    quiz = get_object_or_404(Quiz,id=id)
    section = quiz.pageblock().section
    h = get_hierarchy()
    return dict(quiz=quiz,section=section,
                root=h.get_root())

def delete_question(request,id):
    question = get_object_or_404(Question,id=id)
    if request.method == "POST":
        quiz = question.quiz
        question.delete()
        return HttpResponseRedirect(reverse("edit-quiz",args=[quiz.id]))
    return HttpResponse("""
<html><body><form action="." method="post">Are you Sure?
<input type="submit" value="Yes, delete it" /></form></body></html>
""")

def delete_answer(request,id):
    answer = get_object_or_404(Answer,id=id)
    if request.method == "POST":
        question = answer.question
        answer.delete()
        return HttpResponseRedirect(reverse("edit-question",args=[question.id]))
    return HttpResponse("""
<html><body><form action="." method="post">Are you Sure?
<input type="submit" value="Yes, delete it" /></form></body></html>
""")


def reorder_answers(request,id):
    if request.method != "POST":
        return HttpResponse("only use POST for this")
    question = get_object_or_404(Question,id=id)
    keys = request.GET.keys()
    keys.sort()
    answers = [int(request.GET[k]) for k in keys if k.startswith('answer_')]
    question.update_answers_order(answers)
    return HttpResponse("ok")

def reorder_questions(request,id):
    if request.method != "POST":
        return HttpResponse("only use POST for this")
    quiz = get_object_or_404(Quiz,id=id)
    keys = request.GET.keys()
    keys.sort()
    questions = [int(request.GET[k]) for k in keys if k.startswith('question_')]
    quiz.update_questions_order(questions)
    return HttpResponse("ok")

def add_question_to_quiz(request,id):
    quiz = get_object_or_404(Quiz,id=id)
    form = quiz.add_question_form(request.POST)
    if form.is_valid():
        question = form.save(commit=False)
        question.quiz = quiz
        question.ordinality = quiz.question_set.count() + 1
        question.save()
    return HttpResponseRedirect(reverse("edit-quiz",args=[quiz.id]))

@rendered_with('quiz/edit_question.html')
def edit_question(request,id):
    question = get_object_or_404(Question,id=id)
    return dict(question=question)

def add_answer_to_question(request,id):
    question = get_object_or_404(Question,id=id)
    form = question.add_answer_form(request.POST)
    if form.is_valid():
        answer = form.save(commit=False)
        answer.question = question
        answer.ordinality = question.answer_set.count() + 1
        answer.save()
    return HttpResponseRedirect(reverse("edit-question",args=[question.id]))

@rendered_with('quiz/edit_answer.html')
def edit_answer(request,id):
    answer = get_object_or_404(Answer,id=id)
    return dict(answer=answer)

@login_required
def loadstate(request):
    try: 
        state = ActivityState.objects.get(user=request.user)
        if (len(state.json) > 0):
            doc = state.json
    except ActivityState.DoesNotExist:
        doc = "{}"

    response = HttpResponse(doc, 'application/json')
    response['Cache-Control']='max-age=0,no-cache,no-store'
    return response
    
@login_required
def savestate(request):
    json = request.POST['json']
    
    try: 
        state = ActivityState.objects.get(user=request.user)
        state.json = json
        state.save()
    except ActivityState.DoesNotExist:
        state = ActivityState.objects.create(user=request.user, json=json)
        
    response = {}
    response['success'] = 1
        
    return HttpResponse(simplejson.dumps(response), 'application/json')
