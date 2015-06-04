from behave_django import environment
from splinter import Browser

from uelc.main.tests.factories import UELCCaseQuizModuleFactory


def before_all(context):
    context.browser = Browser('firefox')
    UELCCaseQuizModuleFactory()


def before_scenario(context, scenario):
    environment.before_scenario(context, scenario)


def after_scenario(context, scenario):
    environment.after_scenario(context, scenario)
