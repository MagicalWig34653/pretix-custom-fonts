from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.control.signals import nav_organizer
from pretix.presale.signals import html_head
from pretix.base.signals import register_fonts as register_fonts_base
from pretix.base.models import Organizer, Event
import logging
import os

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


@receiver(html_head, dispatch_uid="pretix_custom_fonts_html_head")
def html_head_handler(sender, request, **kwargs):
    # Wir binden die @font-face Definitionen im Frontend ein, damit die Custom Fonts gerendert werden
    # Dies ist ergänzend zur Registrierung, falls der Benutzer die Fonts direkt via CSS ansprechen möchte.
    from .models import CustomFont
    
    if not hasattr(sender, 'organizer'):
        return ""
        
    fonts = CustomFont.objects.filter(organizer=sender.organizer)
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
        
        # Für pretix müssen wir den Pfad zur Datei im Dateisystem angeben
        # Dies funktioniert sowohl für ReportLab (PDF) als auch für die SASS-Kompilierung (Shop)
        try:
            path = font.font_file.path
            if not os.path.exists(path):
                continue
        except Exception:
            continue
            
        ret[font.name][font.style] = path

    # Wir filtern Fonts heraus, die kein 'regular' haben, da pretix das meist voraussetzt
    # Außerdem stellen wir sicher, dass das Format den Erwartungen entspricht
    final_ret = {}
    for font_name, variants in ret.items():
        if 'regular' in variants:
            # pretix erwartet Varianten-Keys wie 'regular', 'bold', 'italic', 'bolditalic'
            # direkt mit dem Pfad als Wert (oder ein Dict mit 'truetype' bei PDF-Plugin)
            final_ret[font_name] = variants

    return final_ret


@receiver(register_fonts_base, dispatch_uid="pretix_custom_fonts_register_fonts_base")
def register_fonts_base_handler(sender, **kwargs):
    return handle_register_fonts(sender, **kwargs)


# Wir versuchen den Import des PDF-Signals. Falls das Plugin nicht aktiv ist,
# wird das Signal nicht gefunden.
try:
    from pretix.plugins.ticketoutputpdf.signals import register_fonts as register_fonts_signal
    
    @receiver(register_fonts_signal, dispatch_uid="pretix_custom_fonts_register_fonts_pdf")
    def register_fonts_pdf_handler(sender, **kwargs):
        # Das PDF-Plugin erwartet ggf. ein leicht anderes Format (mit 'truetype' key)
        # aber meistens funktioniert auch das flache Format. 
        # Zur Sicherheit geben wir hier das Format zurück, das pretix-fontpack-free nutzt.
        res = handle_register_fonts(sender, **kwargs)
        pdf_res = {}
        for font_name, variants in res.items():
            pdf_res[font_name] = {}
            for style, path in variants.items():
                pdf_res[font_name][style] = {
                    'truetype': path
                }
            # 'sample' wird vom PDF-Plugin für die Vorschau genutzt
            if 'regular' in variants:
                pdf_res[font_name]['sample'] = variants['regular']
        return pdf_res
except ImportError:
    pass
