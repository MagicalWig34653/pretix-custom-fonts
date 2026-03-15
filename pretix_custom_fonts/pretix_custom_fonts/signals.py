from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pretix.control.signals import nav_organizer
from pretix.plugins.ticketoutputpdf.signals import register_fonts
import os


@receiver(nav_organizer, dispatch_uid="pretix_custom_fonts_nav")
def control_nav_organizer(sender, request, **kwargs):
    organizer = request.organizer
    url = reverse('plugins:pretix_custom_fonts:list', kwargs={
        'organizer': organizer.slug,
    })
    if not request.user.has_organizer_permission(organizer, 'can_change_organizer_settings'):
        return []

    return [
        {
            'label': _('Custom Fonts'),
            'url': url,
            'active': (request.resolver_match.url_name.startswith('plugins:pretix_custom_fonts:')),
            'icon': 'font',
        }
    ]


@receiver(register_fonts, dispatch_uid="pretix_custom_fonts_register_fonts")
def handle_register_fonts(sender, **kwargs):
    from .models import CustomFont

    # We return all fonts to ensure they are visible in the settings.
    # If we wanted to isolate them by organizer, we would need to check sender (Event or Organizer).
    fonts = CustomFont.objects.all()
    
    ret = {}
    for font in fonts:
        if font.name not in ret:
            ret[font.name] = {}

        try:
            # We need the absolute path on the filesystem for the PDF generation
            path = font.font_file.path
            if not os.path.exists(path):
                continue
        except (AttributeError, NotImplementedError):
            continue
        except Exception:
            continue

        # Each font family can have variants: regular, bold, italic, bolditalic
        font_data = {
            'truetype': path,
        }
        
        # Add woff/woff2 as a bridge for web visibility
        try:
            url = font.font_file.url
            font_data['woff'] = url
            font_data['woff2'] = url
        except:
            pass
            
        ret[font.name][font.style] = font_data

    # Finalize the dictionary by adding 'sample' and filtering incomplete families
    final_ret = {}
    for font_name, variants in ret.items():
        # Pretix requires at least the 'regular' variant
        if 'regular' in variants:
            final_ret[font_name] = variants
            final_ret[font_name]['sample'] = mark_safe(
                'The quick brown fox jumps over the lazy dog.<br>'
                'Franz jagt im komplett verwahrlosten Taxi quer durch Bayern.'
            )

    return final_ret
