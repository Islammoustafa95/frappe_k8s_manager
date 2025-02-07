import frappe
import stripe

# Fetch Stripe API Key from Frappe Config
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

@frappe.whitelist()
def update_billing_settings(stripe_api_key, billing_email):
    """Update Stripe API key and billing email."""
    settings = frappe.get_single("Billing Settings")
    settings.stripe_api_key = stripe_api_key
    settings.billing_email = billing_email
    settings.save()
    frappe.db.commit()
    return {"message": "Billing settings updated successfully."}

@frappe.whitelist()
def get_stripe_billing_portal():
    """Retrieve Stripe billing portal URL for customer."""
    user = frappe.session.user
    stripe_customer = frappe.get_value("Stripe Customer", {"user": user}, "stripe_id")

    if not stripe_customer:
        return {"error": "No Stripe account found"}

    session = stripe.billing_portal.Session.create(
        customer=stripe_customer,
        return_url=frappe.utils.get_url("/billing-settings")
    )

    return {"url": session.url}

@frappe.whitelist()
def change_subscription_plan(plan_id):
    """Change the user's subscription plan on Stripe."""
    user = frappe.session.user
    stripe_customer = frappe.get_value("Stripe Customer", {"user": user}, "stripe_id")

    if not stripe_customer:
        return {"error": "No Stripe account found"}

    subscriptions = stripe.Subscription.list(customer=stripe_customer, status="active")

    if not subscriptions.data:
        return {"error": "No active subscription found"}

    subscription_id = subscriptions.data[0].id
    stripe.Subscription.modify(
        subscription_id,
        items=[{"id": subscriptions.data[0].items.data[0].id, "price": plan_id}],
        proration_behavior="create_prorations",
    )

    return {"success": True, "message": "Subscription plan updated successfully."}

@frappe.whitelist()
def cancel_subscription():
    """Cancel the user's active subscription on Stripe."""
    user = frappe.session.user
    stripe_customer = frappe.get_value("Stripe Customer", {"user": user}, "stripe_id")

    if not stripe_customer:
        return {"error": "No Stripe account found"}

    subscriptions = stripe.Subscription.list(customer=stripe_customer, status="active")

    if not subscriptions.data:
        return {"error": "No active subscription found"}

    subscription_id = subscriptions.data[0].id
    stripe.Subscription.delete(subscription_id)

    return {"success": True, "message": "Subscription cancelled successfully."}
