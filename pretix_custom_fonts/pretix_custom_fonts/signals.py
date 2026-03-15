from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.signals import register_payment_providers, register_ticket_outputs
from pretix.control.signals import nav_organizer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

logger = logging.getLogger(__name__)

@receiver(nav_organizer, dispatch_uid="pretix_custom_fonts_nav")
def control_nav_organizer(sender, request, organizer, **kwargs):
    url = reverse('plugins:pretix_custom_fonts:list', kwargs={
        'organizer': organizer.slug,
    })
    if not request.user.has_organizer_permission(request.organizer, 'can_change_organizer_settings'):
        return []

    return [
        {
            'label': _('Custom Fonts'),
            'url': url,
            'active': (request.resolver_match.url_name.startswith('plugins:pretix_custom_fonts:')),
            'icon': 'font',
        }
    ]

# Integration in PDF-Rendering
# Pretix nutzt ReportLab. Um Fonts verfügbar zu machen, müssen sie in pdfmetrics registriert werden.
# Wir können dies tun, wenn ein Ticket-Output generiert wird oder über einen allgemeineren Hook.

def register_custom_fonts(event):
    from .models import CustomFont
    fonts = CustomFont.objects.filter(organizer=event.organizer)
    for font in fonts:
        try:
            # Wir registrieren die Schriftart unter ihrem Namen
            # Hinweis: In der Produktion sollte dies gecached werden, da pdfmetrics global ist.
            # ReportLab wirft einen Fehler, wenn die Schriftart bereits registriert ist.
            if font.name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font.name, font.font_file.path))
                logger.info(f"Registered custom font: {font.name}")
        except Exception as e:
            logger.error(f"Could not register font {font.name}: {e}")

# Dieser Hook wird aufgerufen, bevor ein Ticket generiert wird (falls das Ticket-Plugin dies unterstützt)
# Da es keinen direkten "pre_render_pdf" Hook in pretix-base gibt, der universell ist,
# nutzen wir einen Hook, der oft vor der PDF-Erstellung ausgeführt wird.

@receiver(register_ticket_outputs, dispatch_uid="pretix_custom_fonts_register_fonts")
def register_fonts_on_ticket_output(sender, **kwargs):
    # sender ist hier das Event
    register_custom_fonts(sender)
    return []
