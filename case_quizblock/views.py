from models import CaseQuiz, CaseQuestion
from quizblock.models import Answer
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView


class EditCaseQuizView(DetailView):
    model = CaseQuiz


class DeleteCaseQuestionView(DeleteView):
    model = CaseQuestion

    def get_success_url(self):
        quiz = self.object.quiz
        return reverse("edit-casequiz", args=[quiz.id])


class DeleteCaseAnswerView(DeleteView):
    model = Answer

    def get_success_url(self):
        question = self.object.question
        return reverse("edit-casequestion", args=[question.id])


class ReorderItemsView(View):
    def post(self, request, pk):
        parent = get_object_or_404(self.parent_model, pk=pk)
        keys = [k
                for k in request.GET.keys()
                if k.startswith(self.prefix)]
        keys.sort(key=lambda x: int(x.split("_")[1]))
        items = [int(request.GET[k])
                 for k in keys if k.startswith(self.prefix)]
        self.update_order(parent, items)
        return HttpResponse("ok")


class ReorderCaseAnswersView(ReorderItemsView):
    parent_model = CaseQuestion
    prefix = "answer_"

    def update_order(self, parent, items):
        parent.update_answers_order(items)


class ReorderCaseQuestionsView(ReorderItemsView):
    parent_model = CaseQuiz
    prefix = "question_"

    def update_order(self, parent, items):
        parent.update_questions_order(items)


class AddQuestionToCaseQuizView(View):
    def post(self, request, pk):
        quiz = get_object_or_404(CaseQuiz, pk=pk)
        form = quiz.add_question_form(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
        return HttpResponseRedirect(reverse("edit-casequiz", args=[quiz.id]))


class EditCaseQuestionView(View):
    template_name = "case_quizblock/edit_question.html"

    def get(self, request, pk):
        question = get_object_or_404(CaseQuestion, pk=pk)
        return render(
            request,
            self.template_name,
            dict(question=question, answer_form=question.add_answer_form()))

    def post(self, request, pk):
        question = get_object_or_404(CaseQuestion, pk=pk)
        form = question.edit_form(request.POST)
        question = form.save(commit=False)
        question.save()
        return HttpResponseRedirect(reverse("edit-casequestion",
                                            args=[question.id]))


class AddAnswerToCaseQuestionView(View):
    template_name = 'case_quizblock/edit_question.html'

    def get(self, request, pk):
        casequestion = get_object_or_404(CaseQuestion, pk=pk)
        form = casequestion.add_answer_form()
        return render(
            request,
            self.template_name,
            dict(question=casequestion, answer_form=form))

    def post(self, request, pk):
        casequestion = get_object_or_404(CaseQuestion, pk=pk)
        form = casequestion.add_answer_form(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = casequestion
            if answer.label == '':
                answer.label = answer.value
            answer.save()
            return HttpResponseRedirect(reverse("edit-casequestion",
                                                args=[casequestion.id]))
        return render(
            request,
            self.template_name,
            dict(question=casequestion, answer_form=form))


class EditCaseAnswerView(View):
    template_name = 'case_quizblock/edit_answer.html'

    def get(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        form = answer.edit_form()
        return render(
            request,
            self.template_name,
            dict(answer_form=form, answer=answer))

    def post(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        form = answer.edit_form(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.save()
            return HttpResponseRedirect(reverse("edit-caseanswer",
                                                args=[answer.id]))
        return render(
            request,
            self.template_name,
            dict(answer_form=form, answer=answer))
