import frappe
import stripe

stripe.api_key = "your_stripe_secret_key"

@frappe.whitelist()
def get_plans():
    """Fetch all available subscription plans"""
    plans = frappe.get_all("Subscription Plan", fields=["name", "plan_name", "price"])
    return {"plans": plans}

@frappe.whitelist()
def process_subscription(plan_id):
    """Process subscription payment and create Kubernetes cluster"""
    user = frappe.session.user

    # Fetch plan details
    plan = frappe.get_doc("Subscription Plan", plan_id)
    if not plan:
        return {"status": "error", "message": "Invalid plan selected."}

    # Create Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user,
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": plan.plan_name,
                    },
                    "unit_amount": int(plan.price * 100),
                },
                "quantity": 1,
            }],
            mode="subscription",
            success_url=frappe.utils.get_url() + "/success",
            cancel_url=frappe.utils.get_url() + "/subscription",
        )
        return {"status": "success", "checkout_url": checkout_session.url}

    except stripe.error.StripeError as e:
        return {"status": "error", "message": str(e)}
