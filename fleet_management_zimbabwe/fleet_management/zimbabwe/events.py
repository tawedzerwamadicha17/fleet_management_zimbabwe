import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

from fleet_management_zimbabwe.fleet_management.zimbabwe.validators import validate_plate


def _lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def _expired_documents(parenttype, parent, required):
    if not (parent and required):
        return []
    rows = frappe.get_all(
        "Vehicle Documents",
        filters={"parenttype": parenttype, "parent": parent, "description": ["in", required]},
        fields=["description", "expire_date"],
    )
    have = {r.description: r.expire_date for r in rows}
    today = getdate(nowdate())
    out = []
    for doc_type in required:
        exp = have.get(doc_type)
        if not exp:
            out.append(_("{0}: not on file").format(doc_type))
        elif getdate(exp) < today:
            out.append(_("{0}: expired {1}").format(doc_type, exp))
    return out


def validate_vehicle_trip(doc, method=None):
    """Hook: Vehicle Trip.validate."""
    validate_plate(doc.get("vehicle_plate_number"))
    validate_plate(doc.get("trailer_plate_number"))
    s = frappe.get_cached_doc("ZIMRA Fleet Settings")
    if not s.block_trip_on_expired_documents or not doc.get("vehicle"):
        return
    required = _lines(s.mandatory_document_types)
    if doc.get("is_international_trip"):
        required += _lines(s.international_document_types)
        missing = [
            label for field, label in (
                ("zimra_transit_declaration_no", _("transit declaration no.")),
                ("cross_border_permit_no", _("cross-border permit no.")),
            ) if not doc.get(field)
        ]
        if missing:
            frappe.msgprint(_("International trip: still missing {0}.").format(", ".join(missing)),
                            indicator="orange", alert=True)
    problems = _expired_documents("Vehicle", doc.vehicle, required)
    if doc.get("trailer"):
        problems += [f"{_('Trailer')}: {p}" for p in _expired_documents("Trailer", doc.trailer, required)]
    if problems:
        frappe.throw("<br>".join(problems), title=_("Vehicle documents not compliant"))


def send_expiry_alerts():
    """Daily scheduler: email documents expiring within the configured window."""
    s = frappe.get_cached_doc("ZIMRA Fleet Settings")
    recipients = [e.strip() for e in (s.alert_recipients or "").split(",") if e.strip()]
    if not recipients:
        return
    horizon = add_days(nowdate(), int(s.expiry_alert_days or 30))
    rows = frappe.db.sql(
        """select tvd.parenttype, tvd.parent, tvd.description, tvd.reference_no, tvd.expire_date
           from `tabVehicle Documents` tvd
           where tvd.expire_date is not null and tvd.expire_date <= %s
           order by tvd.expire_date""",
        horizon, as_dict=True,
    )
    if not rows:
        return
    body = "<table border='1' cellpadding='4'><tr><th>Asset</th><th>Document</th><th>Ref</th><th>Expires</th></tr>"
    for r in rows:
        status = "EXPIRED" if getdate(r.expire_date) < getdate(nowdate()) else str(r.expire_date)
        body += f"<tr><td>{r.parenttype} {r.parent}</td><td>{r.description}</td><td>{r.reference_no or ''}</td><td>{status}</td></tr>"
    frappe.sendmail(recipients=recipients, subject=_("Fleet documents expired or expiring soon"), message=body + "</table>")
