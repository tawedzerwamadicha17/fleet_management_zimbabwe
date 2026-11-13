"""ZIMRA FDMS fiscalisation scaffold for fleet (transport) invoices.

What this does:
  * checks the buyer details ZIMRA requires on a fiscal tax invoice
  * builds a submitReceipt-style payload from a Sales Invoice
  * posts it to the configured FDMS gateway using the device certificate (mTLS)
  * stores the fiscal result and verification QR link on the invoice

What it does NOT do: sign receipts. The device signature (SHA-256 hash chain plus
private-key signature) must follow ZIMRA's current Fiscal Device Gateway spec for your
device. Register a signer through the `zimra_receipt_signer` hook; until one is
registered, submission is refused and the invoice is marked Failed. Validate the
payload against ZIMRA's spec and test environment before going live.
"""
import json

import frappe
import requests
from frappe import _
from frappe.utils import flt, get_datetime, get_site_path

from fleet_management_zimbabwe.fleet_management.zimbabwe.validators import validate_tin, validate_vat_number


def get_settings():
    return frappe.get_cached_doc("ZIMRA Fleet Settings")


def fdms_active():
    try:
        return bool(get_settings().fdms_enabled)
    except Exception:
        return False


# ---------------------------------------------------------------- validation
def validate_buyer(si, method=None):
    """Hook: Sales Invoice.validate. Buyer details are mandatory on fiscal invoices."""
    if not fdms_active() or si.is_return and not si.return_against:
        return
    cust = frappe.get_cached_doc("Customer", si.customer)
    problems = []
    if not (si.customer_name or cust.customer_name):
        problems.append(_("buyer registered name"))
    tin = cust.tax_id
    if tin:
        validate_tin(tin, _("Customer TIN"))
    else:
        problems.append(_("buyer TIN (Tax ID on Customer)"))
    if cust.get("zimra_vat_number"):
        validate_vat_number(cust.zimra_vat_number)
    if not (si.customer_address or si.address_display):
        problems.append(_("buyer address"))
    if not (si.contact_mobile or si.contact_email or cust.get("mobile_no")):
        problems.append(_("buyer contact (phone or email)"))
    if problems:
        frappe.throw(
            _("ZIMRA fiscal invoices require buyer details. Missing: {0}").format(", ".join(problems)),
            title=_("Buyer details required"),
        )
    if si.currency not in ("ZWG", "USD"):
        frappe.msgprint(
            _("Currency {0} is not ZWG or USD. Confirm the device is configured for it.").format(si.currency),
            indicator="orange",
        )


# ------------------------------------------------------------------- payload
def _tax_for_line(item_row, si, s):
    rate = 0.0
    for t in si.taxes:
        if t.rate:
            rate = flt(t.rate)
            break
    if item_row.get("item_tax_rate"):
        try:
            rates = json.loads(item_row.item_tax_rate)
            if rates:
                rate = flt(next(iter(rates.values())))
        except Exception:
            pass
    if rate > 0:
        return "A", rate, s.tax_id_standard
    return "B", 0.0, s.tax_id_zero


def build_receipt(si, counter, global_no, previous_hash=None):
    s = get_settings()
    cust = frappe.get_cached_doc("Customer", si.customer)
    sign = -1 if si.is_return else 1
    lines, taxes = [], {}
    for i, row in enumerate(si.items, 1):
        code, pct, tax_id = _tax_for_line(row, si, s)
        net = flt(row.net_amount)
        tax_amt = round(net * pct / 100, 2)
        gross = round(net + tax_amt, 2) * sign
        lines.append(
            {
                "receiptLineType": "Sale",
                "receiptLineNo": i,
                "receiptLineHSCode": row.get("customs_tariff_number") or "",
                "receiptLineName": (row.item_name or row.item_code)[:200],
                "receiptLineQuantity": flt(row.qty),
                "receiptLinePrice": flt(row.rate),
                "receiptLineTotal": gross,
                "taxCode": code,
                "taxPercent": pct,
                "taxID": tax_id,
            }
        )
        g = taxes.setdefault((code, pct, tax_id), {"taxAmount": 0.0, "salesAmountWithTax": 0.0})
        g["taxAmount"] += tax_amt * sign
        g["salesAmountWithTax"] += gross
    receipt = {
        "deviceID": s.device_id,
        "receiptType": "CreditNote" if si.is_return else "FiscalInvoice",
        "receiptCurrency": si.currency,
        "receiptCounter": counter,
        "receiptGlobalNo": global_no,
        "invoiceNo": si.name,
        "buyerData": {
            "buyerRegisterName": si.customer_name or cust.customer_name,
            "buyerTradeName": cust.customer_name,
            "vatNumber": cust.get("zimra_vat_number") or "",
            "buyerTIN": cust.tax_id,
            "buyerContacts": {
                "phoneNo": si.contact_mobile or cust.get("mobile_no") or "",
                "email": si.contact_email or "",
            },
            "buyerAddress": {"street": (si.address_display or "").replace("<br>", ", ")[:200]},
        },
        "receiptDate": get_datetime(f"{si.posting_date} {si.posting_time or '00:00:00'}").strftime("%Y-%m-%dT%H:%M:%S"),
        "receiptLinesTaxInclusive": True,
        "receiptLines": lines,
        "receiptTaxes": [
            {
                "taxCode": c,
                "taxPercent": p,
                "taxID": tid,
                "taxAmount": round(v["taxAmount"], 2),
                "salesAmountWithTax": round(v["salesAmountWithTax"], 2),
            }
            for (c, p, tid), v in taxes.items()
        ],
        "receiptPayments": [
            {"moneyTypeCode": "Other" if flt(si.outstanding_amount) <= 0 else "Credit",
             "paymentAmount": round(flt(si.grand_total) * sign, 2)}
        ],
        "receiptTotal": round(flt(si.grand_total) * sign, 2),
    }
    if si.is_return and si.return_against:
        receipt["creditDebitNote"] = {"receiptID": frappe.db.get_value("Sales Invoice", si.return_against, "zimra_receipt_id")}
    return receipt


def _sign(receipt, previous_hash):
    hooks = frappe.get_hooks("zimra_receipt_signer")
    if not hooks:
        frappe.throw(
            _("No ZIMRA receipt signer registered (hook: zimra_receipt_signer). Signing must be implemented to ZIMRA's spec for your device."),
            title=_("Signer missing"),
        )
    return frappe.get_attr(hooks[-1])(receipt, previous_hash)


def _cert():
    s = get_settings()
    def path(url):
        rel = url.lstrip("/")
        return get_site_path("private", "files", rel.split("/files/")[-1]) if "/private/" in url else get_site_path("public", "files", rel.split("/files/")[-1])
    return path(s.client_certificate), path(s.client_private_key)


# ---------------------------------------------------------------- submission
@frappe.whitelist()
def fiscalise_invoice(invoice):
    si = frappe.get_doc("Sales Invoice", invoice)
    if si.docstatus != 1:
        frappe.throw(_("Submit the invoice before fiscalising."))
    if si.get("zimra_fiscal_status") == "Fiscalised":
        frappe.throw(_("Invoice is already fiscalised."))
    s = get_settings()
    if not s.fdms_enabled:
        frappe.throw(_("FDMS fiscalisation is disabled in ZIMRA Fleet Settings."))
    try:
        last = frappe.db.sql(
            "select max(zimra_receipt_counter), max(zimra_receipt_global_no) from `tabSales Invoice` where zimra_fiscal_status='Fiscalised' and zimra_device_id=%s",
            s.device_id,
        )[0]
        counter, global_no = int(last[0] or 0) + 1, int(last[1] or 0) + 1
        prev_hash = frappe.db.get_value(
            "Sales Invoice", {"zimra_receipt_global_no": global_no - 1, "zimra_device_id": s.device_id}, "zimra_receipt_hash"
        )
        receipt = build_receipt(si, counter, global_no, prev_hash)
        receipt["receiptDeviceSignature"] = _sign(receipt, prev_hash)
        r = requests.post(
            f"{s.fdms_base_url.rstrip('/')}/SubmitReceipt",
            json={"Receipt": receipt},
            headers={"DeviceModelName": s.device_model or "", "DeviceModelVersion": s.device_model or ""},
            cert=_cert(),
            timeout=30,
        )
        r.raise_for_status()
        res = r.json()
        if res.get("validationErrors"):
            raise frappe.ValidationError(json.dumps(res["validationErrors"]))
        si.db_set(
            {
                "zimra_fiscal_status": "Fiscalised",
                "zimra_receipt_id": res.get("receiptID"),
                "zimra_receipt_counter": counter,
                "zimra_receipt_global_no": global_no,
                "zimra_device_id": s.device_id,
                "zimra_receipt_hash": (receipt["receiptDeviceSignature"] or {}).get("hash"),
                "zimra_qr_url": f"{s.verification_url.rstrip('/')}/{res.get('receiptID', '')}",
                "zimra_error": "",
            }
        )
        return res
    except Exception as e:
        si.db_set({"zimra_fiscal_status": "Failed", "zimra_error": str(e)[:1000]})
        frappe.log_error(title="ZIMRA fiscalisation failed", message=frappe.get_traceback())
        raise


def fiscalise_on_submit(si, method=None):
    """Hook: Sales Invoice.on_submit. Queued so a gateway outage does not block billing."""
    if fdms_active():
        si.db_set("zimra_fiscal_status", "Pending")
        frappe.enqueue(
            "fleet_management_zimbabwe.fleet_management.zimbabwe.fiscal._fiscalise_job",
            invoice=si.name, queue="short", enqueue_after_commit=True,
        )


def _fiscalise_job(invoice):
    try:
        fiscalise_invoice(invoice)
    except Exception:
        pass  # status and error already stored on the invoice
