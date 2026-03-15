from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pretix.presale.signals import html_head as html_head_presale
from pretix.control.signals import html_head as html_head_control, nav_organizer
from pretix.base.models import Organizer, Event
import logging
import os

# Robustere Importe für das register_fonts Signal
try:
    from pretix.base.signals import register_fonts as register_fonts_base
except ImportError:
    register_fonts_base = None

try:
    from pretix.plugins.ticketoutputpdf.signals import register_fonts as register_fonts_pdf
except ImportError:
    register_fonts_pdf = None

logger = logging.getLogger(__name__)


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


@receiver(html_head_presale, dispatch_uid="pretix_custom_fonts_html_head_presale")
@receiver(html_head_control, dispatch_uid="pretix_custom_fonts_html_head_control")
def html_head_handler(sender, request, **kwargs):
    # Wir binden die @font-face Definitionen ein, damit die Custom Fonts gerendert werden
    from .models import CustomFont
    
    organizer = None
    if hasattr(sender, 'organizer'):
        organizer = sender.organizer
    elif hasattr(request, 'event') and request.event:
        organizer = request.event.organizer
    elif hasattr(request, 'organizer') and request.organizer:
        organizer = request.organizer
        
    if not organizer:
        return ""
        
    fonts = CustomFont.objects.filter(organizer=organizer)
    if not fonts.exists():
        return ""

    css = "<style>"
    for font in fonts:
        font_url = font.font_file.url
        css += f"""
        @font-face {{
            font-family: '{font.name}';
            src: url('{font_url}');
            font-weight: {'bold' if 'bold' in font.style else 'normal'};
            font-style: {'italic' if 'italic' in font.style else 'normal'};
            font-display: swap;
        }}
        """

    css += "</style>"
    return css


def handle_register_fonts(sender, **kwargs):
    from .models import CustomFont
    
    # Ermittlung des Organizers basierend auf dem Sender
    organizer = None
    if isinstance(sender, Organizer):
        organizer = sender
    elif isinstance(sender, Event):
        organizer = sender.organizer
    elif hasattr(sender, 'organizer'):
        organizer = sender.organizer
    
    if not organizer:
        return {}

    fonts = CustomFont.objects.filter(organizer=organizer)
    ret = {}
    for font in fonts:
        if font.name not in ret:
            ret[font.name] = {}
        
        try:
            path = font.font_file.path
            if not os.path.exists(path):
                continue
        except Exception:
            continue
            
        # Wir verwenden das Format, das sowohl vom PDF-Plugin als auch
        # vom globalen Font-System (ab Pretix 4.9) verstanden wird.
        ret[font.name][font.style] = {
            'truetype': path,
        }
        # Web-URLs als Fallback für das Shop-Design hinzufügen
        try:
            url = font.font_file.url
            ret[font.name][font.style]['woff'] = url
            ret[font.name][font.style]['woff2'] = url
        except:
            pass

    # Wir filtern Fonts heraus, die kein 'regular' haben
    final_ret = {}
    for font_name, variants in ret.items():
        if 'regular' in variants:
            final_ret[font_name] = variants
            # 'sample' wird für die Vorschau in der UI benötigt
            final_ret[font_name]['sample'] = mark_safe(
                'The quick brown fox jumps over the lazy dog.<br>'
                'Franz jagt im komplett verwahrlosten Taxi quer durch Bayern.'
            )

    return final_ret


if register_fonts_base:
    register_fonts_base_handler = receiver(
        register_fonts_base, 
        dispatch_uid="pretix_custom_fonts_register_fonts_base"
    )(handle_register_fonts)

if register_fonts_pdf:
    register_fonts_pdf_handler = receiver(
        register_fonts_pdf, 
        dispatch_uid="pretix_custom_fonts_register_fonts_pdf"
    )(handle_register_fonts)
