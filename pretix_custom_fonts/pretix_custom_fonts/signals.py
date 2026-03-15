from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django import forms
from pretix.base.signals import register_ticket_outputs, event_copy_data
from pretix.control.signals import nav_organizer, nav_event, event_settings_widget_kwargs
from pretix.presale.signals import html_head, sass_variables
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

@receiver(register_ticket_outputs, dispatch_uid="pretix_custom_fonts_register_fonts")
def register_fonts_on_ticket_output(sender, **kwargs):
    # sender is the event
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

    # Inkompatible Hooks dokumentieren:
    # layout_text_render existiert in dieser Pretix-Version nicht.
    # Wir verlassen uns stattdessen auf die Registrierung via register_ticket_outputs.

    # Invoice Font Handling
    invoice_font_id = sender.settings.get('custom_font_invoice_id')
    if invoice_font_id:
        from .models import CustomFont
        try:
            font = CustomFont.objects.get(pk=invoice_font_id)
            sender.settings.set('invoice_renderer_pdf_fontfamily', font.name)
            logger.info(f"Set invoice font family to: {font.name}")
        except CustomFont.DoesNotExist:
            pass

    # Shop Design Font Handling
    shop_font_id = sender.settings.get('custom_font_shop_id')
    if shop_font_id:
        from .models import CustomFont
        try:
            font = CustomFont.objects.get(pk=shop_font_id)
            # Wir setzen die 'font_family' Einstellung von Pretix auf den Namen unserer Schrift
            # Das sorgt dafür, dass Pretix im SASS die Variable $font-family auf diesen Namen setzt.
            sender.settings.set('font_family', font.name)
        except CustomFont.DoesNotExist:
            pass

    return []


@receiver(event_settings_widget_kwargs, dispatch_uid="pretix_custom_fonts_settings_widget_kwargs")
def event_settings_widget_kwargs_handler(sender, field, request, **kwargs):
    if field.name == 'font_family':
        from .models import CustomFont
        custom_fonts = CustomFont.objects.filter(organizer=sender.organizer)
        if custom_fonts.exists():
            # Wir erweitern die Choices des bestehenden font_family Feldes
            if not isinstance(field.widget, forms.Select):
                return {}

            new_choices = list(field.choices)
            for font in custom_fonts:
                new_choices.append((font.name, font.name))

            return {'choices': new_choices}
    return {}


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
        }}
        """
    css += "</style>"
    return css


@receiver(sass_variables, dispatch_uid="pretix_custom_fonts_sass_variables")
def sass_variables_handler(sender, **kwargs):
    # Falls eine Custom Font für den Shop gewählt wurde, stellen wir sicher, dass sie im SASS ankommt.
    # Das ist redundant, wenn 'font_family' bereits gesetzt ist, aber sicherer.
    font_id = sender.settings.get('custom_font_shop_id')
    if font_id:
        from .models import CustomFont
        try:
            font = CustomFont.objects.get(pk=font_id)
            return {
                'font-family': f"'{font.name}'"
            }
        except CustomFont.DoesNotExist:
            pass
    return {}
