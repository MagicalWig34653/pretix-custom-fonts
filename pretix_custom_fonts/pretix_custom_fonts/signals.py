from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from pretix.base.signals import register_payment_providers, register_ticket_outputs, layout_text_render, invoice_render
from pretix.control.signals import nav_organizer, nav_event
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
import os

logger = logging.getLogger(__name__)


def register_custom_fonts(event):
    from .models import CustomFont
    fonts = CustomFont.objects.filter(organizer=event.organizer)
    for font in fonts:
        try:
            if font.name not in pdfmetrics.getRegisteredFontNames():
                # Ensure the file exists on disk
                if os.path.exists(font.font_file.path):
                    pdfmetrics.registerFont(TTFont(font.name, font.font_file.path))
                    logger.info(f"Registered custom font: {font.name}")
                else:
                    logger.error(f"Font file not found: {font.font_file.path}")
        except Exception as e:
            logger.error(f"Could not register font {font.name}: {e}")


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


@receiver(nav_event, dispatch_uid="pretix_custom_fonts_nav_event")
def control_nav_event(sender, request, **kwargs):
    organizer = request.organizer
    event = request.event
    url = reverse('plugins:pretix_custom_fonts:event_settings', kwargs={
        'organizer': organizer.slug,
        'event': event.slug,
    })
    if not request.user.has_event_permission(organizer, event, 'can_change_event_settings', request=request):
        return []

    return [
        {
            'label': _('Custom Font'),
            'url': url,
            'active': (request.resolver_match.url_name == 'plugins:pretix_custom_fonts:event_settings'),
            'icon': 'font',
            'group': _('Settings'),
        }
    ]

@receiver(layout_text_render, dispatch_uid="pretix_custom_fonts_layout_text_render")
def on_layout_text_render(sender, request, **kwargs):
    # sender is the event
    register_custom_fonts(sender)

    font_id = sender.settings.get('custom_font_id')
    if font_id:
        from .models import CustomFont
        try:
            font = CustomFont.objects.get(pk=font_id)
            # Registering the font is already done by register_custom_fonts(sender)
            # We don't need to return anything here, but the font is now available in ReportLab
            pass
        except CustomFont.DoesNotExist:
            pass
    return []


@receiver(invoice_render, dispatch_uid="pretix_custom_fonts_invoice_render")
def on_invoice_render(sender, **kwargs):
    # sender is the event
    register_custom_fonts(sender)

    font_id = sender.settings.get('custom_font_invoice_id')
    if font_id:
        from .models import CustomFont
        try:
            font = CustomFont.objects.get(pk=font_id)
            # We set the font family for invoices
            sender.settings.set('invoice_renderer_pdf_fontfamily', font.name)
            logger.info(f"Set invoice font family to: {font.name}")
        except CustomFont.DoesNotExist:
            pass
    return []


@receiver(register_ticket_outputs, dispatch_uid="pretix_custom_fonts_register_fonts")
def register_fonts_on_ticket_output(sender, **kwargs):
    # sender ist hier das Event
    register_custom_fonts(sender)

    # Wir setzen die gewählte Schriftart in den Settings für das Ticket-Rendering,
    # falls eine ausgewählt wurde.
    font_id = sender.settings.get('custom_font_id')
    if font_id:
        from .models import CustomFont
        try:
            font = CustomFont.objects.get(pk=font_id)
            # Wir setzen die Font-Family für Ticket-Outputs, die dieses Setting respektieren
            sender.settings.set('ticket_output_pdf_font_family', font.name)
            logger.info(f"Set ticket font family to: {font.name}")
        except CustomFont.DoesNotExist:
            pass

    return []
