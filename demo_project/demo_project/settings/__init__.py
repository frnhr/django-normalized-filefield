"""
These are the setting of the project demo_project. It's continuing mission to import
strange new versions, to seek out matching settings files. To boldly go where no
file field has gone before.

Other files in this package (`django_1_7.py`, etc.) are unchanged default settings files,
as made by `manage.py startproject` command.

The necessary settings are added at the end of this file.
"""

from distutils.version import LooseVersion
from django import VERSION, get_version

V_this = LooseVersion(get_version(VERSION))
V1_10 = LooseVersion("1.10")
V1_9 = LooseVersion("1.9")
V1_8 = LooseVersion("1.8")
V1_7 = LooseVersion("1.7")
V1_6 = LooseVersion("1.6")

if V_this >= V1_10:
    raise NotImplementedError('Unsupported new version of Django.')
elif V_this >= V1_9:
    from .django_1_9 import *
elif V_this >= V1_8:
    from .django_1_8 import *
elif V_this >= V1_7:
    from .django_1_7 import *
else:
    raise NotImplementedError('Unsupported old version of Django.')


# ~~~ Settings specific to this project ~~~ #


# Correcting `BASE_DIR` for the "settings" module structure:

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Actual settings for normalized filefield:

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'myapp',
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    "normalized_filefield": {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        "LOCATION": os.path.join(BASE_DIR, 'tmp/normalized_filefield')
    },
}
