import frappe
import stripe

# Set your Stripe API key
STRIPE_API_KEY = frappe.conf.get("stripe_secret_key")
stripe.api_key = STRIPE_API_KEY

@frappe.whitelist()
def get_billing_history(user_email):
    """Fetch user billing history from Stripe."""
    try:
        user = frappe.get_doc("User", {"email": user_email})
        customer = frappe.get_doc("Stripe Customer", {"user": user.name})
        
        invoices = stripe.Invoice.list(customer=customer.stripe_id, limit=10)
        
        billing_data = []
        for invoice in invoices.auto_paging_iter():
            billing_data.append({
                "date": frappe.utils.format_datetime(invoice.created, "YYYY-MM-DD"),
                "amount": invoice.total / 100,  # Convert cents to dollars
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "invoice_url": invoice.hosted_invoice_url
            })
        
        return billing_data
    
    except Exception as e:
        frappe.log_error(f"Error fetching billing history: {str(e)}", "Billing History Error")
        return {"error": str(e)}
