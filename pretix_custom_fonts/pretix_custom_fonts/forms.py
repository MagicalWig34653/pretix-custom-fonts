import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomFont


class FontUploadForm(forms.ModelForm):
    class Meta:
        model = CustomFont
        fields = ['name', 'font_file']

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
        label=_("Custom Font"),
        help_text=_("Choose a custom font to be used in PDF outputs for this event.")
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop('event')
        super().__init__(*args, **kwargs)
        self.fields['default_font'].queryset = CustomFont.objects.filter(organizer=event.organizer)
        self.fields['default_font'].initial = event.settings.get('custom_font_id')
