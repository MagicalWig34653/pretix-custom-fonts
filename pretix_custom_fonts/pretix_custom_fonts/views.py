from django.urls import path, reverse
from django.views.generic import ListView, CreateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect
from pretix.control.views.organizer import OrganizerDetailViewMixin
from .models import CustomFont
from .forms import FontUploadForm


class FontListView(OrganizerDetailViewMixin, ListView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/font_list.html'
    context_object_name = 'fonts'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.request.organizer)


class FontCreateView(OrganizerDetailViewMixin, CreateView):
    model = CustomFont
    form_class = FontUploadForm
    template_name = 'pretix_custom_fonts/font_form.html'

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.request.organizer.slug,
        })

    def form_valid(self, form):
        form.instance.organizer = self.request.organizer
        messages.success(self.request, _('The font has been uploaded.'))
        return super().form_valid(form)


class FontDeleteView(OrganizerDetailViewMixin, DeleteView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/font_delete.html'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.request.organizer)

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.request.organizer.slug,
        })

    def post(self, request, *args, **kwargs):
        messages.success(self.request, _('The font has been deleted.'))
        return super().post(request, *args, **kwargs)
