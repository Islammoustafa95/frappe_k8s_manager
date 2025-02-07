import frappe
import stripe

STRIPE_API_KEY = frappe.conf.get("stripe_secret_key")
stripe.api_key = STRIPE_API_KEY

@frappe.whitelist()
def get_invoice_history():
    """Fetch invoice history from Stripe."""
    user = frappe.session.user
    stripe_customer = frappe.get_value("Stripe Customer", {"user": user}, "stripe_id")

    if not stripe_customer:
        return {"error": "No Stripe account found"}

    invoices = stripe.Invoice.list(customer=stripe_customer, limit=5)
    
    invoice_data = [
        {
            "date": frappe.utils.formatdate(frappe.utils.get_datetime(invoice.created)),
            "amount": f"${invoice.total / 100:.2f}",
            "url": invoice.invoice_pdf
        }
        for invoice in invoices.auto_paging_iter()
    ]

    return invoice_data

@frappe.whitelist()
def send_invoice(invoice_id):
    """Send an invoice to the user via email."""
    user_email = frappe.session.user
    invoice = stripe.Invoice.retrieve(invoice_id)

    if not invoice.invoice_pdf:
        return {"error": "Invoice not found."}

    frappe.sendmail(
        recipients=[user_email],
        subject="Your Invoice from Frappe K8s Manager",
        message=frappe.render_template("frappe_k8s_manager/email_templates/invoice_email.html", {"invoice_url": invoice.invoice_pdf}),
    )

    return {"message": "Invoice sent successfully!"}
