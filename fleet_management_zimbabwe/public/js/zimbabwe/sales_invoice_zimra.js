frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        if (frm.doc.docstatus !== 1) return;
        const st = frm.doc.zimra_fiscal_status;
        if (st === "Fiscalised" && frm.doc.zimra_qr_url) {
            frm.dashboard.add_comment(
                __("Fiscalised. Verify on FDMS: {0}", [`<a href="${frm.doc.zimra_qr_url}" target="_blank">${frm.doc.zimra_receipt_id}</a>`]),
                "green", true
            );
        } else if (st === "Pending" || st === "Failed") {
            frm.add_custom_button(__("Fiscalise with ZIMRA"), () => {
                frappe.call({
                    method: "fleet_management_zimbabwe.fleet_management.zimbabwe.fiscal.fiscalise_invoice",
                    args: { invoice: frm.doc.name },
                    freeze: true,
                    freeze_message: __("Submitting to ZIMRA FDMS..."),
                    callback: () => frm.reload_doc(),
                    error: () => frm.reload_doc(),
                });
            }, __("ZIMRA"));
        }
    },
});
