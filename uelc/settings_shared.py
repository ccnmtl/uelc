# Django settings for uelc project.
import os.path
from ccnmtlsettings.shared import common
from uelc.main.utils import clear_handler_cache

project = 'uelc'
base = os.path.dirname(__file__)
locals().update(common(project=project, base=base))

PROJECT_APPS = [
    'uelc.main',
    'gate_block',
    'curveball',
]

ALLOWED_HOSTS += ['eldex.org']  # noqa

USE_TZ = True
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'width': '100%',
        'removePlugins': 'stylesheetparser',
        'filebrowserBrowseUrl': '/admin/main/imageuploaditem/',
        'allowedContent': True,
        'autofocus': True,
        'toolbar_Custom': [
            {
                'name': 'document',
                'items': ['Source']
            },
            {
                'name': 'clipboard',
                'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord',
                          '-', 'Undo', 'Redo']
            },
            {
                'name': 'editing',
                'items': ['Find', '-', 'Scayt']
            },
            {
                'name': 'insert',
                'items': ['Image', 'Table', 'HorizontalRule',
                          'SpecialChar', 'PageBreak', 'Iframe']
            },
            '/',
            {
                'name': 'styles',
                'items': ['Styles', 'Format']
            },
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {
                'name': 'basicstyles',
                'items': ['Bold', 'Italic', 'Underline', 'Strike',
                          'Subscript', 'Superscript', '-', 'RemoveFormat']
            },
            {
                'name': 'paragraph',
                'items': ['NumberedList', 'BulletedList', '-',
                          'Outdent', 'Indent', '-', 'Blockquote']
            },
            {
                'name': 'links',
                'items': ['Link', 'Unlink', 'Anchor']
            },
        ]
    }
}

MIDDLEWARE_CLASSES += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'typogrify',
    'bootstrap3',
    'bootstrapform',
    'infranil',
    'django_extensions',
    'registration',
    'pagetree',
    'pageblocks',
    'quizblock',
    'uelc.main',
    'gate_block',
    'curveball',
    'ckeditor',
    'behave_django',
]

PAGEBLOCKS = [
    'gate_block.GateBlock',
    'main.TextBlockDT',
    'main.CaseQuiz',
    'curveball.CurveballBlock',
]


IMPERSONATE_REQUIRE_SUPERUSER = False

THUMBNAIL_SUBDIR = "thumbs"

LOGIN_REDIRECT_URL = "/"

ACCOUNT_ACTIVATION_DAYS = 7

WINDSOCK_BROKER_URL = "tcp://localhost:5555"
ZMQ_APPNAME = "uelc"
WINDSOCK_SECRET = "6f1d916c-7761-4874-8d5b-8f8f93d20bf2"
WINDSOCK_WEBSOCKETS_BASE = "ws://localhost:5050/socket/"

# Set this to True in local_settings.py
BEHAVE_DEBUG_ON_ERROR = False

PAGETREE_CUSTOM_CACHE_CLEAR = clear_handler_cache
