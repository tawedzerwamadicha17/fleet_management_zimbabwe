"""Server-side helpers for the Fleet Management dashboard (custom Number Cards)."""
import frappe
from frappe import _
from frappe.utils import add_days, nowdate


def _alert_days():
    try:
        return int(frappe.db.get_single_value("ZIMRA Fleet Settings", "expiry_alert_days") or 30)
    except Exception:
        return 30


def _count(condition, values):
    return frappe.db.sql(
        f"select count(*) from `tabVehicle Documents` where expire_date is not null and {condition}",
        values,
    )[0][0]


@frappe.whitelist()
def expired_documents_count():
    """Vehicle/Trailer documents whose expiry date is already past."""
    frappe.has_permission("Vehicle", throw=True)
    return {
        "value": _count("expire_date < %s", nowdate()),
        "fieldtype": "Int",
        "route": ["query-report", "Truck Document Expiration Report"],
        "route_options": {},
    }


@frappe.whitelist()
def expiring_documents_count():
    """Documents expiring within the alert window set in ZIMRA Fleet Settings."""
    frappe.has_permission("Vehicle", throw=True)
    return {
        "value": _count("expire_date >= %s and expire_date <= %s", (nowdate(), add_days(nowdate(), _alert_days()))),
        "fieldtype": "Int",
        "route": ["query-report", "Truck Document Expiration Report"],
        "route_options": {},
    }
