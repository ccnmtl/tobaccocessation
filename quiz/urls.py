from django.conf.urls.defaults import patterns
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_root}),
                       (r'^edit_quiz/(?P<id>\d+)/$','quiz.views.edit_quiz',{},'edit-quiz'),
                       (r'^edit_quiz/(?P<id>\d+)/add_question/$','quiz.views.add_question_to_quiz',{},'add-question-to-quiz'),
                       (r'^edit_question/(?P<id>\d+)/$','quiz.views.edit_question',{},'edit-question'),
                       (r'^edit_question/(?P<id>\d+)/add_answer/$','quiz.views.add_answer_to_question',{},'add-answer-to-question'),
                       (r'^delete_question/(?P<id>\d+)/$','quiz.views.delete_question',{},'delete-question'),
                       (r'^reorder_answers/(?P<id>\d+)/$','quiz.views.reorder_answers',{},'reorder-answer'),
                       (r'^reorder_questions/(?P<id>\d+)/$','quiz.views.reorder_questions',{},'reorder-questions'),
                       (r'^delete_answer/(?P<id>\d+)/$','quiz.views.delete_answer',{},'delete-answer'),
                       (r'^edit_answer/(?P<id>\d+)/$','quiz.views.edit_answer',{},'edit-answer'),
)
