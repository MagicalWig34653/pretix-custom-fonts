from django.urls import path, reverse
from django.views.generic import ListView, CreateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from pretix.base.models import Organizer
from .models import CustomFont
from .forms import FontUploadForm


class OrganizerViewMixin:
    def dispatch(self, request, *args, **kwargs):
        self.organizer = get_object_or_404(Organizer, slug=self.kwargs['organizer'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizer'] = self.organizer
        return context


class FontListView(OrganizerViewMixin, ListView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/font_list.html'
    context_object_name = 'fonts'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.organizer)


class FontCreateView(OrganizerViewMixin, CreateView):
    model = CustomFont
    form_class = FontUploadForm
    template_name = 'pretix_custom_fonts/font_form.html'

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.organizer.slug,
        })

    def form_valid(self, form):
        form.instance.organizer = self.organizer
        messages.success(self.request, _('The font has been uploaded.'))
        return super().form_valid(form)


class FontDeleteView(OrganizerViewMixin, DeleteView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/font_delete.html'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.organizer)

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.organizer.slug,
        })

    def post(self, request, *args, **kwargs):
        messages.success(self.request, _('The font has been deleted.'))
        return super().post(request, *args, **kwargs)
