from django.urls import reverse
from django.views.generic import ListView, CreateView, DeleteView, FormView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from pretix.base.models import Organizer, Event
from .models import CustomFont
from .forms import FontUploadForm, EventFontSettingsForm


class OrganizerPermissionMixin(LoginRequiredMixin):
    permission = None

    def dispatch(self, request, *args, **kwargs):
        self.organizer = get_object_or_404(Organizer, slug=self.kwargs['organizer'])
        if not request.user.has_organizer_permission(self.organizer, self.permission):
            raise PermissionDenied(_('You do not have permission to access this page.'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizer'] = self.organizer
        return context


class EventPermissionMixin(LoginRequiredMixin):
    permission = None

    def dispatch(self, request, *args, **kwargs):
        self.organizer = get_object_or_404(Organizer, slug=self.kwargs['organizer'])
        self.event = get_object_or_404(Event, slug=self.kwargs['event'], organizer=self.organizer)
        if not request.user.has_event_permission(self.organizer, self.event, self.permission, request=request):
            raise PermissionDenied(_('You do not have permission to access this page.'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizer'] = self.organizer
        context['event'] = self.event
        return context


class FontListView(OrganizerPermissionMixin, ListView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/list.html'
    context_object_name = 'fonts'
    permission = 'can_change_organizer_settings'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.organizer)


class FontCreateView(OrganizerPermissionMixin, CreateView):
    model = CustomFont
    form_class = FontUploadForm
    template_name = 'pretix_custom_fonts/form.html'
    permission = 'can_change_organizer_settings'

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.organizer.slug,
        })

    def form_valid(self, form):
        form.instance.organizer = self.organizer
        messages.success(self.request, _('The font has been uploaded.'))
        return super().form_valid(form)


class FontDeleteView(OrganizerPermissionMixin, DeleteView):
    model = CustomFont
    template_name = 'pretix_custom_fonts/delete.html'
    permission = 'can_change_organizer_settings'

    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.organizer)

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.organizer.slug,
        })

    def post(self, request, *args, **kwargs):
        messages.success(self.request, _('The font has been deleted.'))
        return super().post(request, *args, **kwargs)


class EventFontSettingsView(EventPermissionMixin, FormView):
    model = CustomFont
    form_class = EventFontSettingsForm
    template_name = 'pretix_custom_fonts/event_settings.html'
    permission = 'can_change_event_settings'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.event
        return kwargs

    def form_valid(self, form):
        self.event.settings.set('custom_font_id', form.cleaned_data['default_font'].pk if form.cleaned_data['default_font'] else None)
        self.event.settings.set('custom_font_invoice_id', form.cleaned_data['invoice_font'].pk if form.cleaned_data['invoice_font'] else None)
        self.event.settings.set('custom_font_shop_id', form.cleaned_data['shop_font'].pk if form.cleaned_data['shop_font'] else None)
        messages.success(self.request, _('Your settings have been saved.'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:event_settings', kwargs={
            'organizer': self.organizer.slug,
            'event': self.event.slug,
        })
