from django import forms

from .widget import NormalizedFileInput


# noinspection PyUnresolvedReferences
class NormalizedFileField(forms.fields.FileField):
    widget = NormalizedFileInput

    def clean(self, data, initial=None):
        # `False` means "clear". End of story.
        if data is False:
            return False
        # The rest of the jazz is fine:
        return super(NormalizedFileField, self).clean(data, initial)
