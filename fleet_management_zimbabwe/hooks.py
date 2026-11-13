from . import __version__ as app_version

app_name = "fleet_management_zimbabwe"
app_title = "Fleet Management Zimbabwe"
app_publisher = "Murozvi"
app_description = "Fleet and transport management localised for Zimbabwe: ZWG/USD, ZIMRA fiscalisation (FDMS), ZINARA/VID/cross-border compliance"
app_email = "info@example.com"
app_license = "GNU General Public License (v3)"
app_icon = "octicon octicon-package"
app_color = "green"
app_logo_url = "/assets/fleet_management_zimbabwe/images/fleet_logo.svg"

# Shows the app on the desktop "Apps" screen (v15) and opens the Fleet Management workspace
add_to_apps_screen = [
    {
        "name": "fleet_management_zimbabwe",
        "logo": "/assets/fleet_management_zimbabwe/images/fleet_logo.svg",
        "title": "Fleet Management",
        "route": "/app/fleet-management",
    }
]

required_apps = ["frappe/erpnext", "frappe/hrms"]

doctype_js = {
    "Sales Invoice": "public/js/zimbabwe/sales_invoice_zimra.js",
}

doc_events = {
    "Vehicle Trip": {
        "validate": "fleet_management_zimbabwe.fleet_management.zimbabwe.events.validate_vehicle_trip",
    },
    "Sales Invoice": {
        "validate": "fleet_management_zimbabwe.fleet_management.zimbabwe.fiscal.validate_buyer",
        "on_submit": "fleet_management_zimbabwe.fleet_management.zimbabwe.fiscal.fiscalise_on_submit",
    },
}

scheduler_events = {
    "daily": [
        "fleet_management_zimbabwe.fleet_management.zimbabwe.events.send_expiry_alerts",
    ],
}

after_install = "fleet_management_zimbabwe.fleet_management.zimbabwe.setup.execute"
after_migrate = "fleet_management_zimbabwe.fleet_management.zimbabwe.setup.execute"
