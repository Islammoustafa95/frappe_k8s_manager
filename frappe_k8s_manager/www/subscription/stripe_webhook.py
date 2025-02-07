import frappe
import stripe
import json
from frappe_k8s_manager.kubernetes.deploy import create_k8s_cluster

stripe.api_key = "your_stripe_secret_key"

@frappe.whitelist(allow_guest=True)
def stripe_webhook():
    """Handles Stripe webhook for successful payments"""
    payload = frappe.request.get_data(as_text=True)
    event = None

    try:
        event = json.loads(payload)
    except json.JSONDecodeError as e:
        frappe.log_error("Webhook error while parsing request", str(e))
        return "Invalid payload", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_email = session["customer_email"]
        plan_id = session["metadata"]["plan_id"]

        # Deploy Kubernetes cluster
        deployment_status = create_k8s_cluster(user_email, plan_id)

        if deployment_status["status"] == "success":
            return {"status": "success", "message": "Kubernetes cluster created"}
        else:
            return {"status": "error", "message": deployment_status["error"]}

    return {"status": "ignored"}
