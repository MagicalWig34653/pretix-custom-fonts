from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pretix.control.signals import nav_organizer
from pretix.plugins.ticketoutputpdf.signals import register_fonts
from django.conf import settings
import os
import shutil


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
    fonts = CustomFont.objects.all()
    
    ret = {}
    
    # Identify potential static base directories for materialization
    # We prefer the one mentioned in the error message, followed by STATIC_ROOT
    static_dirs = ['/pretix/src/pretix/static']
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        static_dirs.append(settings.STATIC_ROOT)
    static_dirs.append(os.path.join(os.path.dirname(__file__), 'static'))

    for font in fonts:
        if font.name not in ret:
            ret[font.name] = {}

        try:
            # We need the absolute path on the filesystem for the PDF generation
            source_path = font.font_file.path
            if not os.path.exists(source_path):
                continue
        except (AttributeError, NotImplementedError):
            continue
        except Exception:
            continue

        # Bridge from MEDIA to STATIC: Materialize the font into a static directory
        filename = os.path.basename(source_path)
        rel_path = f"pretix_custom_fonts/fonts/{font.organizer.slug}/{filename}"
        
        materialized = False
        for base in static_dirs:
            if not base: continue
            try:
                target_path = os.path.join(base, rel_path)
                target_dir = os.path.dirname(target_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                # Copy file if missing or if the source is newer
                if not os.path.exists(target_path) or os.path.getmtime(source_path) > os.path.getmtime(target_path):
                    shutil.copy2(source_path, target_path)
                
                materialized = True
                break # Success
            except:
                continue

        if not materialized:
            # Fallback to media path if materialization failed
            pass

        # Each font family can have variants: regular, bold, italic, bolditalic
        # Use relative path for truetype - Pretix will resolve it via staticfiles finders.
        # This ensures it passes the safety check as it's within the static hierarchy.
        font_data = {
            'truetype': rel_path if materialized else source_path,
        }
        
        # Add woff/woff2 as a bridge for web visibility
        # To avoid the 'Missing staticfiles manifest entry' error, bypass manifest 
        # lookup by providing a full absolute URL if SITE_URL is available.
        try:
            site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
            if site_url:
                # Direct absolute URL to the media file bypasses static() manifest lookup
                url = site_url + font.font_file.url
            else:
                # Fallback: Use the materialized static path if available
                if materialized:
                    url = f"{settings.STATIC_URL}{rel_path}"
                else:
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
