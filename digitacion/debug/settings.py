# Settings import
from ..settings import *

DEBUG = True

INSTALLED_APPS += [
    'debug_toolbar',
    'autofixture',
]

MIDDLEWARE_CLASSES += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS=('127.0.0.1', )
