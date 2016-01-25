# -*- coding: utf-8 -*-
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from django.core.cache import caches
from django.core.files.uploadedfile import InMemoryUploadedFile


class FileCache(object):
    def __init__(self):
        self.backend = self.get_backend()

    def get_backend(self):
        return caches['normalized_filefield']

    def set(self, key, field_name, state, upload, clear, initial_url, initial_name):
        # Note: `InMemoryUploadedFile` cannot be pickled, so we save raw values under key `upload`
        #       Same is true for `FieldFile`, but only two values are needed, so it is saves
        #       in a simpler way (`initial_url` and `initial_name`).
        data = {
            "state": state,
            "upload": None if not upload else {
                "content": upload.file.read(),
                "field_name": field_name,
                "name": upload.name,
                "content_type": upload.content_type,
                "size": upload.size,
                "charset": upload.charset,
            },
            "clear": clear,
            "initial_url": initial_url,
            "initial_name": initial_name,
        }
        if upload:
            upload.file.seek(0)
        self.backend.set(key, data)

    def get(self, key):
        data = None
        cached_data = self.backend.get(key)
        if cached_data:
            if cached_data["upload"]:
                f = BytesIO()
                f.write(cached_data["upload"]["content"])
                upload = InMemoryUploadedFile(
                    file=f,
                    field_name=cached_data["upload"]["field_name"],
                    name=cached_data["upload"]["name"],
                    content_type=cached_data["upload"]["content_type"],
                    size=cached_data["upload"]["size"],
                    charset=cached_data["upload"]["charset"],
                )
                upload.file.seek(0)
            else:
                upload = None
            data = {
                "state": cached_data["state"],
                "upload": upload,
                "clear": cached_data["clear"],
                "initial_url": cached_data["initial_url"],
                "initial_name": cached_data["initial_name"],
            }

        return data

    def delete(self, key):
        self.backend.delete(key)