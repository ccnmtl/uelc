from django.conf import settings
from splinter import Browser

from uelc.main.tests.factories import AdminUpFactory, UELCModuleFactory


def before_all(context):
    context.browser = Browser('firefox', wait_time=4)


def before_scenario(context, scenario):
    AdminUpFactory()
    UELCModuleFactory()


def after_step(context, step):
    if settings.BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        import ipdb
        ipdb.post_mortem(step.exc_traceback)


def after_all(context):
    context.browser.quit()
    del context.browser
