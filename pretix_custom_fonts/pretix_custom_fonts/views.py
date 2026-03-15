from django.urls import reverse
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
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
        return CustomFont.objects.filter(organizer=self.organizer).order_by('name', 'style')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fonts = context['fonts']
        families = {}
        for font in fonts:
            if font.name not in families:
                families[font.name] = []
            families[font.name].append(font)
        
        families_data = []
        for name, family_fonts in families.items():
            mapping = {}
            found_styles = {f.style: f for f in family_fonts}
            for pretix_slot, style_list in CustomFont.PRETIX_STYLE_MAP.items():
                for style in style_list:
                    if style in found_styles:
                        mapping[pretix_slot] = found_styles[style]
                        break
            families_data.append({
                'name': name,
                'fonts': family_fonts,
                'mapping': mapping
            })
            
        context['families_data'] = families_data
        return context


class FontCreateUpdateMixin:
    model = CustomFont
    form_class = FontUploadForm
    template_name = 'pretix_custom_fonts/form.html'
    permission = 'can_change_organizer_settings'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organizer'] = self.organizer
        return kwargs

    def get_success_url(self):
        return reverse('plugins:pretix_custom_fonts:list', kwargs={
            'organizer': self.organizer.slug,
        })


class FontCreateView(OrganizerPermissionMixin, FontCreateUpdateMixin, CreateView):
    def form_valid(self, form):
        form.instance.organizer = self.organizer
        resp = super().form_valid(form)
        if not self.object.is_pdf_compatible:
            messages.warning(self.request, _('This font was uploaded successfully for web usage, but it cannot be used for PDF rendering (PostScript outlines detected). It will be available for CSS themes but not for invoices.'))
        else:
            messages.success(self.request, _('The font has been uploaded.'))
        return resp


class FontUpdateView(OrganizerPermissionMixin, FontCreateUpdateMixin, UpdateView):
    def get_queryset(self):
        return CustomFont.objects.filter(organizer=self.organizer)

    def form_valid(self, form):
        resp = super().form_valid(form)
        if not self.object.is_pdf_compatible:
            messages.warning(self.request, _('This font was updated successfully for web usage, but it cannot be used for PDF rendering (PostScript outlines detected). It will be available for CSS themes but not for invoices.'))
        else:
            messages.success(self.request, _('The font style has been updated.'))
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
