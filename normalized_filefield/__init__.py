# coding: utf-8
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

VERSION = '0.1.1'


if 'normalized_filefield' not in settings.CACHES:
    raise ImproperlyConfigured(
        "CACHES['normalized_filefield'] is not defined in settings.py")
