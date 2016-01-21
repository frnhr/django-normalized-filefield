from django import forms

from .models import MyModel


class MyModelForm(forms.ModelForm):

    #ac_required_file = ResubmittableAlwaysClearableFileFormField(required=True)
    #ac_optional_file = ResubmittableAlwaysClearableFileFormField(required=False)

    class Meta:
        model = MyModel
        exclude = ()
        widgets = {
            #'required_file': DownloadableInMemoryFileInput(),
        }
