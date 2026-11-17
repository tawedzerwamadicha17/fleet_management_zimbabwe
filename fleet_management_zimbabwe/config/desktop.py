from frappe import _


def get_data():
    """Desktop icon (legacy desk / v14). In v15 the app is shown through add_to_apps_screen."""
    return [
        {
            "module_name": "Fleet Management",
            "type": "module",
            "label": _("Fleet Management"),
            "color": "#2E7D32",
            "icon": "octicon octicon-package",
            "description": _("Fleet, trips, border processing and ZIMRA compliance"),
        }
    ]
