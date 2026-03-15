from django.urls import reverse
from django.views.generic import ListView, CreateView, DeleteView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from pretix.base.models import Organizer
from .models import CustomFont
from .forms import FontUploadForm


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
        resp = super().form_valid(form)
        if not self.object.is_pdf_compatible:
            messages.warning(self.request, _('This font was uploaded successfully for web usage, but it cannot be used for PDF rendering (PostScript outlines detected). It will be available for CSS themes but not for invoices.'))
        else:
            messages.success(self.request, _('The font has been uploaded.'))
        return resp


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
