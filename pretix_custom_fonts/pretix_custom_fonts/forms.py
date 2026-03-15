import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomFont


class FontUploadForm(forms.ModelForm):
    class Meta:
        model = CustomFont
        fields = ['name', 'style', 'font_file']

    def __init__(self, *args, **kwargs):
        self.organizer = kwargs.pop('organizer', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['font_file'].required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        style = cleaned_data.get('style')

        if name and style and self.organizer:
            qs = CustomFont.objects.filter(organizer=self.organizer, name=name, style=style)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_("A font with this family name and style already exists for this organizer."))
        return cleaned_data

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
