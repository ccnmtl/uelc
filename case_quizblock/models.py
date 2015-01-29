from django import forms
from django.core.urlresolvers import reverse
from quizblock.models import Quiz, Question, Submission
from quizblock.models import Response
from gate_block.models import GateSubmission
from uelc.main.models import CaseMap
from pagetree.models import Section
from pagetree.reports import ReportableInterface
from django.core.exceptions import ObjectDoesNotExist


class CaseQuiz(Quiz):
    display_name = "Case Quiz"
    template_file = "case_quizblock/quizblock.html"

    def submit(self, user, data):
        """ a big open question here is whether we should
        be validating submitted answers here, on submission,
        or let them submit whatever garbage they want and only
        worry about it when we show the admins the results """
        s = Submission.objects.create(quiz=self, user=user)
        # create a CaseMap for the user
        # get Case the user is currently on
        quiz = self
        for k in data.keys():
            if k.startswith('case'):
                case_id = data[k]
                try:
                    casemap = CaseMap.objects.get(
                        user=user,
                        case_id=case_id)

                except ObjectDoesNotExist:
                    casemap = CaseMap.objects.create(
                        user=user,
                        case_id=case_id,
                        value=str(0))

                casemap.set_value(quiz, data)

            if k.startswith('question'):
                qid = int(k[len('question'):])
                question = CaseQuestion.objects.get(id=qid)
                # it might make more sense to just accept a QueryDict
                # instead of a dict so we can use getlist()
                if isinstance(data[k], list):
                    for v in data[k]:
                        Response.objects.create(
                            submission=s,
                            question=question,
                            value=v)
                else:
                    Response.objects.create(
                        submission=s,
                        question=question,
                        value=data[k])

    def is_submitted(self, quiz, user):
        return Submission.objects.filter(
            quiz=self,
            user=user).count() > 0

    def unlocked(self, user, section):
        # meaning that the user can proceed *past* this one,
        # not that they can access this one. careful.
        unlocked = False
        submissions = GateSubmission.objects.filter(gate_user_id=user.id)
        if len(submissions) > 0:
            for sub in submissions:
                section_id = sub.gateblock.pageblock().section_id
                section = Section.objects.get(id=section_id)
                upv = section.get_uservisit(user)
                blocks = section.pageblock_set.all()
                for block in blocks:
                    obj = block.content_object
                    if obj.display_name == "Gate Block":
                        unlocked = obj.unlocked(user, section)
            is_quiz_submitted = self.is_submitted(self, user)
            if not (unlocked and is_quiz_submitted):
                unlocked = False
                upv.status = 'complete'
                upv.save()
            else:
                upv.status = 'complete'
                upv.save()
                unlocked = True
        return unlocked

    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea(),
                                          initial=self.description)
            rhetorical = forms.BooleanField(initial=self.rhetorical)
            allow_redo = forms.BooleanField(initial=self.allow_redo)
            show_submit_state = forms.BooleanField(
                initial=self.show_submit_state)
            alt_text = ("<a href=\"" + reverse("edit-casequiz", args=[self.id])
                        + "\">manage questions/answers</a>")
        return EditForm()

    @classmethod
    def create(self, request):
        return CaseQuiz.objects.create(
            description=request.POST.get('description', ''),
            rhetorical=request.POST.get('rhetorical', ''),
            allow_redo=request.POST.get('allow_redo', ''),
            show_submit_state=request.POST.get('show_submit_state', False))


ReportableInterface.register(CaseQuiz)


class CaseQuestion(Question):
    display_name = "Case Question"

    def __init__(self, *args, **kwargs):
        if 'question_type' not in kwargs:
            kwargs['question_type'] = "single choice"
            super(CaseQuestion, self).__init__(*args, **kwargs)

    def edit_form(self, request=None):
        return QuestionForm(request, instance=self)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = CaseQuestion
        exclude = ("quiz",)
        fields = ('intro_text', 'text', 'explanation')
