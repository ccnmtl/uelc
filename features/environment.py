from behave_django import environment
from django.conf import settings
from splinter import Browser

from uelc.main.tests.factories import UELCModuleFactory


BEHAVE_DEBUG_ON_ERROR = False


def before_all(context):
    settings.DEBUG = True
    context.browser = Browser('firefox')
    UELCModuleFactory()


def before_scenario(context, scenario):
    environment.before_scenario(context, scenario)


def after_scenario(context, scenario):
    environment.after_scenario(context, scenario)


def after_all(context):
    context.browser.quit()
    context.browser = None


def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        import ipdb
        ipdb.post_mortem(step.exc_traceback)
