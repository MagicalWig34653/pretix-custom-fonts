from django.urls import reverse
from django.views.generic import ListView, CreateView, DeleteView, FormView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from pretix.control.views.organizer import OrganizerControlView
from pretix.control.views.event import EventViewMixin
from .models import CustomFont
from .forms import FontUploadForm, EventFontSettingsForm


class FontListView(OrganizerControlView, ListView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/list.html'
    context_object_name = 'fonts'
    permission = 'can_change_organizer_settings'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.request.organizer)


class FontCreateView(OrganizerControlView, CreateView):
    model = CustomFont
    form_class = FontUploadForm
    template_name = 'pretix_custom_fonts/form.html'
    permission = 'can_change_organizer_settings'

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.request.organizer.slug,
        })

    def form_valid(self, form):
        form.instance.organizer = self.request.organizer
        messages.success(self.request, _('The font has been uploaded.'))
        return super().form_valid(form)


class FontDeleteView(OrganizerControlView, DeleteView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/delete.html'
    permission = 'can_change_organizer_settings'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.request.organizer)

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.request.organizer.slug,
        })

    def post(self, request, *args, **kwargs):
        messages.success(self.request, _('The font has been deleted.'))
        return super().post(request, *args, **kwargs)


class EventFontSettingsView(EventViewMixin, FormView):
    model = CustomFont
    form_class = EventFontSettingsForm
    template_name = 'pretix_custom_fonts/event_settings.html'
    permission = 'can_change_event_settings'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.request.event
        return kwargs

    def form_valid(self, form):
        self.request.event.settings.set('custom_font_id', form.cleaned_data['default_font'].pk if form.cleaned_data['default_font'] else None)
        messages.success(self.request, _('Your settings have been saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:event_settings', kwargs={
            'organizer': self.request.organizer.slug,
            'event': self.request.event.slug,
        })
