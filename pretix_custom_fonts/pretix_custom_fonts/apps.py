from django.utils.translation import gettext_lazy as _

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    class PluginConfig:
        pass


class PluginApp(PluginConfig):
    name = 'pretix_custom_fonts'
    verbose_name = _('Custom Fonts for pretix')

    class PretixPluginMeta:
        name = _('Custom Fonts')
        author = 'Junie'
        description = _('Manage custom fonts (TTF/OTF) for your event PDFs.')
        visible = True
        version = '1.0.0'
        category = 'FEATURE'
        compatibility = "pretix>=4.0.0"

    def ready(self):
        from . import signals  # NOQA
