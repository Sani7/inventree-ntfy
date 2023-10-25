"""Plugin to send notifications from InvenTree via Ntfy."""
import requests
from django.utils.translation import gettext_lazy as _
from plugin import InvenTreePlugin, registry
from plugin.mixins import BulkNotificationMethod, SettingsMixin


class PlgMixin:
    """Mixin to access plugin easier.

    This needs to be spit out to reference the class. Perks of python.
    """

    def get_plugin(self):
        """Return plugin reference."""
        return NtfyPlugin


class NtfyPlugin(SettingsMixin, InvenTreePlugin):
    """Send notifications from InvenTree via Ntfy."""

    NAME = 'NtfyPlugin'
    SLUG = 'ntfy'
    TITLE = "Ntfy Notifications"
    SETTINGS = {
        'ENABLE_NOTIFICATION_NTFY': {
            'name': _('Enable ntfy notifications'),
            'description': _('Allow sending of event notifications via ntfy'),
            'default': False,
            'validator': bool,
        },
        'NOTIFICATION_NTFY_URL': {
            'name': _('Ntfy URLs'),
            'description': _('URLs for notification enppoints, seperated by semicolons'),
            'protected': True,
        },
    }

    class NtfyNotification(PlgMixin, BulkNotificationMethod):
        """Notificationmethod for delivery via ntfy."""

        METHOD_NAME = 'ntfy'
        GLOBAL_SETTING = 'ENABLE_NOTIFICATION_NTFY'

        def get_targets(self):
            """Not used by this method."""
            return self.targets

        def send_bulk(self):
            """Send the notifications out via Ntfy."""
            instance = registry.plugins.get(self.get_plugin().SLUG.lower())
            url = instance.get_setting('NOTIFICATION_NTFY_URL')

            if not url:
                return False
            
            # Add all of the notification services
            ret = True
            for notifiy_url in url.split(';'):
                r = requests.post(notifiy_url,
                                  data=str(self.context['message']),
                                  headers={
                                      "Title": str(self.context['name']),
                                  })
                
                if (r.status_code != 200):
                    ret = False

            return bool(ret)
