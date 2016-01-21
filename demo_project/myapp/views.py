from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages

from .forms import MyModelForm
from .models import MyModel


class ListMyModel(ListView):
    model = MyModel


class CreateMyModel(CreateView):
    template_name = 'myapp/mymodel_create.html'
    model = MyModel
    form_class = MyModelForm

    def form_valid(self, form):
        response = super(CreateMyModel, self).form_valid(form)
        messages.success(self.request, 'Created {}'.format(form.instance))
        return response

    def get_success_url(self):
        return reverse('mymodel_update', args=(self.object.id, ))


class UpdateMyModel(UpdateView):
    template_name = 'myapp/mymodel_update.html'
    model = MyModel
    form_class = MyModelForm

    def get_success_url(self):
        messages.success(self.request, 'Updated {}'.format(self.object))
        return reverse('mymodel_update', args=[self.object.id])


class DeleteMyModel(DeleteView):
    template_name = 'myapp/mymodel_delete.html'
    model = MyModel

    def get_success_url(self):
        messages.success(self.request, 'Deleted {}'.format(self.object))
        return reverse('mymodel_list')
