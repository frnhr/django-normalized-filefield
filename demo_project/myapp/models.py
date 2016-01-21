from math import log, ceil
from django.db import models


class MyModel(models.Model):
    description = models.CharField(max_length=254, blank=False, null=False)
    ac_required_file = models.FileField(upload_to='media/uploads/required', blank=False, null=False)
    ac_optional_file = models.FileField(upload_to='media/uploads/optional', blank=True, null=True)

    def __str__(self):
        return 'MM{{:0{}d}}'.format(
                ceil(log(MyModel.objects.count() + 1, 10)) + 1
        ).format(
                self.id if self.id else 0
        )
