from django.db import models

from . import form_field


class NormalizedFileField(models.FileField):

    def formfield(self, **kwargs):
        defaults = {'form_class': form_field.NormalizedFileField}
        defaults.update(kwargs)
        return super(NormalizedFileField, self).formfield(**defaults)
