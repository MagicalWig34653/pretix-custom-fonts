import os
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomFont


class FontUploadForm(forms.ModelForm):
    class Meta:
        model = CustomFont
        fields = ['name', 'style', 'font_file']

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
