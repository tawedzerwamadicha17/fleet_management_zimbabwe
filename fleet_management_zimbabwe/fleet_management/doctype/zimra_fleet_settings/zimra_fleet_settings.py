import frappe
from frappe import _
from frappe.model.document import Document

from fleet_management_zimbabwe.fleet_management.zimbabwe.validators import validate_tin, validate_vat_number


class ZIMRAFleetSettings(Document):
    def validate(self):
        self.bp_number = validate_tin(self.bp_number, "Company TIN / BP Number")
        self.vat_number = validate_vat_number(self.vat_number)
        if self.fdms_enabled:
            for fld in ("fdms_base_url", "device_id", "device_serial_no", "client_certificate", "client_private_key"):
                if not self.get(fld):
                    frappe.throw(_("{0} is required when FDMS fiscalisation is enabled.").format(self.meta.get_label(fld)))
