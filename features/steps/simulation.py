from behave import then

from curveball.models import CurveballSubmission


@then(u'there are no curveball submissions')
def there_are_no_curveball_submissions(context):
    assert not CurveballSubmission.objects.exists()


@then(u'a curveball submission exists')
def a_curveball_submission_exists(context):
    assert CurveballSubmission.objects.exists()
