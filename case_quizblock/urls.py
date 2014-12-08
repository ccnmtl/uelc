from django.conf.urls import patterns
from .views import (
    EditCaseQuizView, DeleteCaseQuestionView, DeleteCaseAnswerView,
    ReorderCaseAnswersView, ReorderCaseQuestionsView,
    AddQuestionToCaseQuizView, EditCaseQuestionView,
    AddAnswerToCaseQuestionView, EditCaseAnswerView,
)

urlpatterns = patterns(
    'case_quizblock.views',
    (r'^edit_casequiz/(?P<pk>\d+)/$', EditCaseQuizView.as_view(), {},
        'edit-casequiz'),
    (r'^edit_casequiz/(?P<pk>\d+)/add_question/$',
        AddQuestionToCaseQuizView.as_view(),
     {}, 'add-question-to-casequiz'),
    (r'^edit_casequestion/(?P<pk>\d+)/$', EditCaseQuestionView.as_view(), {},
     'edit-casequestion'),
    (r'^edit_casequestion/(?P<pk>\d+)/add_answer/$',
     AddAnswerToCaseQuestionView.as_view(), {}, 'add-answer-to-casequestion'),
    (r'^delete_casequestion/(?P<pk>\d+)/$',
        DeleteCaseQuestionView.as_view(), {},
     'delete-casequestion'),
    (r'^reorder_caseanswers/(?P<pk>\d+)/$',
        ReorderCaseAnswersView.as_view(), {},
     'reorder-caseanswer'),
    (r'^reorder_casequestions/(?P<pk>\d+)/$',
        ReorderCaseQuestionsView.as_view(), {},
     'reorder-casequestions'),
    (r'^delete_answer/(?P<pk>\d+)/$', DeleteCaseAnswerView.as_view(),
     {}, 'delete-caseanswer'),
    (r'^edit_caseanswer/(?P<pk>\d+)/$', EditCaseAnswerView.as_view(),
     {}, 'edit-caseanswer'),
)
