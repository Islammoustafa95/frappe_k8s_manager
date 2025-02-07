import frappe
from frappe_k8s_manager.kubernetes.manage import manage_subscription

@frappe.whitelist()
def get_subscription(user_email):
    """Fetch user subscription details."""
    user = frappe.get_doc("User", {"email": user_email})
    subscription = frappe.get_doc("Subscription", {"user": user.name})
    return {
        "plan": subscription.plan,
        "disk_space": subscription.disk_space,
        "apps": subscription.apps,
        "status": subscription.status
    }

@frappe.whitelist()
def update_subscription(user_email, action, new_plan_id=None):
    """Upgrade, downgrade, or cancel the subscription."""
    return manage_subscription(action, user_email, new_plan_id)
