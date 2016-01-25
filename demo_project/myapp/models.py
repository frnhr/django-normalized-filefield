from math import log, ceil
from django.db import models

from normalized_filefield.model_field import NormalizedFileField


class MyModel(models.Model):
    description = models.CharField(max_length=254, blank=False, null=False)
    required_text = models.CharField(max_length=254, blank=False, null=False)
    required_file = NormalizedFileField(upload_to='media/uploads/required', blank=False, null=False)
    optional_text = models.CharField(max_length=254, blank=True, null=True)
    optional_file = NormalizedFileField(upload_to='media/uploads/optional', blank=True, null=True)

    def __str__(self):
        return 'MM{{:0{}d}}'.format(
                int(ceil(log(MyModel.objects.count() + 1, 10)) + 1)
        ).format(
                self.id if self.id else 0
        )
