from django import forms

from .models import MyModel

from normalized_filefield.form_field import NormalizedFileField


class MyModelForm(forms.ModelForm):

    # required_file = NormalizedFileField(required=True)
    # optional_file = NormalizedFileField(required=False)

    class Meta:
        model = MyModel
        exclude = ()
        widgets = {
            # 'required_file': NormalizedFileInput(),
            # 'optional_file': NormalizedFileInput(),
        }
