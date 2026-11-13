import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from fleet_management_zimbabwe.fleet_management.zimbabwe.constants import BORDER_POSTS, CURRENCIES, VEHICLE_DOCUMENT_TYPES

CUSTOM_FIELDS = {
    "Vehicle": [
        dict(fieldname="fleet_section", label="Fleet", fieldtype="Section Break", insert_after="amended_from"),
        dict(fieldname="number_plate", label="Number Plate", fieldtype="Data", in_list_view=1, in_standard_filter=1),
        dict(fieldname="fuel_consumption", label="Fuel Consumption (L/km)", fieldtype="Float"),
        dict(fieldname="status", label="Status", fieldtype="Select", default="Available", in_standard_filter=1,
             options="Available\nEn Route\nEn Route - Returning\nUnder Maintenance\nOut of Service"),
        dict(fieldname="hidden_status", label="Hidden Status", fieldtype="Int", hidden=1, read_only=1),
        dict(fieldname="current_trip", label="Current Trip", fieldtype="Link", options="Vehicle Trip", read_only=1),
        dict(fieldname="vehicle_documents", label="Vehicle Documents", fieldtype="Table", options="Vehicle Documents"),
    ],
    "Customer": [
        dict(fieldname="zimra_vat_number", label="VAT Registration Number (ZIMRA)", fieldtype="Data",
             insert_after="tax_id", description="9 digits. TIN goes in Tax ID"),
    ],
    "Sales Invoice": [
        dict(fieldname="zimra_section", label="ZIMRA Fiscalisation", fieldtype="Section Break",
             insert_after="amended_from", collapsible=1),
        dict(fieldname="zimra_fiscal_status", label="Fiscal Status", fieldtype="Select",
             options="\nNot Required\nPending\nFiscalised\nFailed", read_only=1, no_copy=1, in_list_view=0,
             in_standard_filter=1),
        dict(fieldname="zimra_receipt_id", label="FDMS Receipt ID", fieldtype="Data", read_only=1, no_copy=1),
        dict(fieldname="zimra_qr_url", label="Verification Link", fieldtype="Data", options="URL", read_only=1, no_copy=1),
        dict(fieldname="zimra_col", fieldtype="Column Break"),
        dict(fieldname="zimra_device_id", label="Fiscal Device ID", fieldtype="Int", read_only=1, no_copy=1),
        dict(fieldname="zimra_receipt_counter", label="Receipt Counter", fieldtype="Int", read_only=1, no_copy=1),
        dict(fieldname="zimra_receipt_global_no", label="Receipt Global No", fieldtype="Int", read_only=1, no_copy=1),
        dict(fieldname="zimra_receipt_hash", label="Receipt Hash", fieldtype="Data", read_only=1, no_copy=1, hidden=1),
        dict(fieldname="zimra_error", label="Fiscalisation Error", fieldtype="Small Text", read_only=1, no_copy=1),
    ],
    "Vehicle Trip": [
        dict(fieldname="zimra_customs_section", label="Zimbabwe Cross-Border / ZIMRA Customs", fieldtype="Section Break",
             insert_after="main_status", collapsible=1),
        dict(fieldname="is_international_trip", label="International / Cross-Border Trip", fieldtype="Check"),
        dict(fieldname="zimra_transit_declaration_no", label="ZIMRA Transit Declaration No (ASYCUDA)", fieldtype="Data",
             depends_on="is_international_trip"),
        dict(fieldname="zimra_bill_of_entry_no", label="Bill of Entry / Export Entry No", fieldtype="Data",
             depends_on="is_international_trip"),
        dict(fieldname="zimra_customs_col", fieldtype="Column Break"),
        dict(fieldname="zimra_carbon_tax_cert_no", label="Carbon Tax Certificate No", fieldtype="Data",
             depends_on="is_international_trip"),
        dict(fieldname="comesa_yellow_card_no", label="COMESA Yellow Card No", fieldtype="Data",
             depends_on="is_international_trip"),
        dict(fieldname="cross_border_permit_no", label="Cross-Border Permit No", fieldtype="Data",
             depends_on="is_international_trip"),
    ],
}


def _seed(doctype, key, values):
    for v in values:
        if not frappe.db.exists(doctype, v):
            frappe.get_doc({"doctype": doctype, key: v}).insert(ignore_permissions=True)


def execute():
    """after_migrate: idempotent Zimbabwe fleet setup."""
    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
    if frappe.db.exists("DocType", "Vehicle Documents Type"):
        _seed("Vehicle Documents Type", "description", VEHICLE_DOCUMENT_TYPES)
    if frappe.db.exists("DocType", "Trip Location"):
        for name, local, intl in BORDER_POSTS:
            if not frappe.db.exists("Trip Location", name):
                frappe.get_doc({"doctype": "Trip Location", "description": name, "location": name,
                                "is_local_border": local, "is_international_border": intl}).insert(ignore_permissions=True)
    for c in CURRENCIES:
        if frappe.db.exists("Currency", c) and not frappe.db.get_value("Currency", c, "enabled"):
            frappe.db.set_value("Currency", c, "enabled", 1)
    frappe.db.commit()
