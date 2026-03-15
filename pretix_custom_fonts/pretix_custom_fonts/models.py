import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from pretix.base.models import Organizer


def font_path(instance, filename):
    return f'pub/{instance.organizer.slug}/fonts/{filename}'


class CustomFont(models.Model):
    organizer = models.ForeignKey(
        Organizer,
        related_name='custom_fonts',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Family name'),
        help_text=_('A name for the font family, e.g. "Roboto".')
    )
    STYLE_CHOICES = (
        ('regular', _('Regular')),
        ('bold', _('Bold')),
        ('italic', _('Italic')),
        ('bolditalic', _('Bold Italic')),
    )
    style = models.CharField(
        max_length=20,
        choices=STYLE_CHOICES,
        default='regular',
        verbose_name=_('Font style')
    )
    font_file = models.FileField(
        upload_to=font_path,
        verbose_name=_('Font file'),
        help_text=_('Only TTF and OTF files are supported.')
    )

    def __str__(self):
        return f"{self.name} ({self.get_style_display()})"

    @property
    def extension(self):
        return os.path.splitext(self.font_file.name)[1].lower()
