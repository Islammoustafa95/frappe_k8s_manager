import frappe
import stripe

STRIPE_API_KEY = frappe.conf.get("stripe_secret_key")
stripe.api_key = STRIPE_API_KEY

def send_monthly_invoices():
    """Automatically send invoices to all active customers."""
    users = frappe.get_all("Stripe Customer", fields=["user", "stripe_id"])

    for user in users:
        invoices = stripe.Invoice.list(customer=user["stripe_id"], limit=1)
        
        if invoices.data:
            invoice = invoices.data[0]
            frappe.sendmail(
                recipients=[user["user"]],
                subject="Your Monthly Invoice",
                message=frappe.render_template("frappe_k8s_manager/email_templates/invoice_email.html", {"invoice_url": invoice.invoice_pdf}),
            )
