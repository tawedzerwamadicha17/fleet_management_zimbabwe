"""Zimbabwe-specific identifier validation for the fleet module.

Format checks only. They catch typos; they do not prove a number is registered
with ZIMRA, ZINARA or the Registrar. Strict checks block saving; soft checks warn.
"""
import re

import frappe
from frappe import _

PLATE_RE = re.compile(r"^[A-Z]{3}\s?\d{3,4}$")  # e.g. AEX 1234
NATIONAL_ID_RE = re.compile(r"^\d{2}-?\d{6,7}\s?-?[A-Z]\s?-?\d{2}$")  # e.g. 63-123456 A 42
DIGITS_RE = re.compile(r"^\d+$")


def clean(value):
    return re.sub(r"[\s\-]", "", (value or "")).upper()


def validate_plate(plate, strict=False):
    plate = (plate or "").strip().upper()
    if plate and not PLATE_RE.match(plate):
        msg = _("Number plate {0} does not look like a Zimbabwean plate (e.g. AEX 1234).").format(plate)
        frappe.throw(msg) if strict else frappe.msgprint(msg, indicator="orange", alert=True)


def validate_national_id(value):
    if value and not NATIONAL_ID_RE.match(value.strip().upper()):
        frappe.msgprint(
            _("National ID {0} does not match the Zimbabwean format (e.g. 63-123456 A 42).").format(value),
            indicator="orange",
            alert=True,
        )


def validate_tin(tin, label="TIN"):
    """ZIMRA TIN / BP number: 10 digits."""
    v = clean(tin)
    if v and not (DIGITS_RE.match(v) and len(v) == 10):
        frappe.throw(_("{0} must be 10 digits (got {1}).").format(label, tin))
    return v


def validate_vat_number(vat):
    """ZIMRA VAT registration number: 9 digits."""
    v = clean(vat)
    if v and not (DIGITS_RE.match(v) and len(v) == 9):
        frappe.throw(_("VAT number must be 9 digits (got {0}).").format(vat))
    return v
