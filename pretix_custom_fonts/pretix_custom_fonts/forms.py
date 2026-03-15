import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomFont


class FontUploadForm(forms.ModelForm):
    class Meta:
        model = CustomFont
        fields = ['name', 'font_file']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # ReportLab fonts often have issues with spaces or special chars if not careful,
            # but usually it's fine. However, we should ensure it's a valid identifier-like string
            # to be safe for PDF font names.
            import re
            if not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
                raise ValidationError(_("The font name contains invalid characters. Use only letters, numbers, spaces, underscores, and hyphens."))
        return name

    def clean_font_file(self):
        f = self.cleaned_data.get('font_file')
        if f:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ('.ttf', '.otf'):
                raise ValidationError(_("Only .ttf and .otf files are allowed."))
        return f


class EventFontSettingsForm(forms.Form):
    default_font = forms.ModelChoiceField(
        queryset=CustomFont.objects.none(),
        required=False,
        label=_("Custom Font for Tickets"),
        help_text=_("Choose a custom font to be used in PDF ticket generation for this event. Note: This will override the default font setting in the ticket layout if the layout uses the default font.")
    )
    invoice_font = forms.ModelChoiceField(
        queryset=CustomFont.objects.none(),
        required=False,
        label=_("Custom Font for Invoices"),
        help_text=_("Choose a custom font to be used for invoices of this event.")
    )
    shop_font = forms.ModelChoiceField(
        queryset=CustomFont.objects.none(),
        required=False,
        label=_("Custom Font for Shop (Alternative)"),
        help_text=_("If selecting the font in the 'Shop Design' section does not work, you can select it here as an alternative.")
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super().__init__(*args, **kwargs)
        self.fields['default_font'].queryset = CustomFont.objects.filter(organizer=event.organizer)
        self.fields['default_font'].initial = event.settings.get('custom_font_id')
        self.fields['invoice_font'].queryset = CustomFont.objects.filter(organizer=event.organizer)
        self.fields['invoice_font'].initial = event.settings.get('custom_font_invoice_id')
        self.fields['shop_font'].queryset = CustomFont.objects.filter(organizer=event.organizer)
        self.fields['shop_font'].initial = event.settings.get('custom_font_shop_id')
