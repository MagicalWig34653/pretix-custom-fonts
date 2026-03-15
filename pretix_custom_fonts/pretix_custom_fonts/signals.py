from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.control.signals import nav_organizer
from pretix.presale.signals import html_head
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
    from .models import CustomFont
    fonts = CustomFont.objects.filter(organizer=sender.organizer)
    if not fonts.exists():
        return ""

    css = "<style>"
    for font in fonts:
        # Wir müssen sicherstellen, dass die URL absolut oder relativ zum Root ist und korrekt funktioniert
        font_url = font.font_file.url
        css += f"""
        @font-face {{
            font-family: '{font.name}';
            src: url('{font_url}');
            font-weight: {'bold' if 'bold' in font.style else 'normal'};
            font-style: {'italic' if 'italic' in font.style else 'normal'};
        }}
        """

    css += "</style>"
    return css


def register_fonts(sender, **kwargs):
    # Dieser Receiver registriert Fonts für pretix.plugins.ticketoutputpdf
    from .models import CustomFont
    # Wir laden hier alle Fonts des Organizers für das Event
    # Hinweis: Da dieser Signal-Receiver global für das Event aufgerufen wird,
    # geben wir die für diesen Organizer verfügbaren Fonts zurück.
    if not hasattr(sender, 'organizer'):
        return {}

    fonts = CustomFont.objects.filter(organizer=sender.organizer)
    ret = {}
    for font in fonts:
        if font.name not in ret:
            ret[font.name] = {}
        
        path = font.font_file.path
        # Pretix erwartet ein Mapping von Font-Namen auf Varianten.
        # Ein Font kann Varianten wie 'regular', 'bold', 'italic', 'bolditalic' haben.
        ret[font.name][font.style] = {
            'truetype': path,
            # 'woff', 'woff2' könnten hier ebenfalls stehen, falls vorhanden.
            # Pretix nutzt 'truetype' für PDF-Generierung (ReportLab).
        }
        # 'sample' sollte auf der Ebene des Font-Namens liegen, nicht pro Variante
        # Wir nehmen einfach die Datei der ersten Variante als Sample.
        if 'sample' not in ret[font.name]:
            ret[font.name]['sample'] = path

    # Wir filtern Fonts heraus, die kein 'regular' haben, da Pretix das meist voraussetzt
    return {k: v for k, v in ret.items() if 'regular' in v}


# Wir versuchen den Import des Signals. Falls das Ticket-Output-Plugin nicht aktiv ist,
# wird das Signal nicht gefunden.
try:
    from pretix.plugins.ticketoutputpdf.signals import register_fonts as register_fonts_signal
    register_fonts = receiver(register_fonts_signal, dispatch_uid="pretix_custom_fonts_register_fonts")(register_fonts)
except ImportError:
    # Falls das Plugin nicht installiert ist, machen wir nichts.
    pass
