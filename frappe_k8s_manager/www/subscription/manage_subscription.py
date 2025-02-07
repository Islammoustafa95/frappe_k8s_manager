import frappe
from frappe_k8s_manager.kubernetes.manage import update_k8s_cluster, delete_k8s_cluster

@frappe.whitelist()
def manage_subscription(action, user_email, new_plan_id=None):
    """Handles subscription upgrades, downgrades, and cancellations."""
    user = frappe.get_doc("User", {"email": user_email})
    
    if action == "upgrade" or action == "downgrade":
        new_plan = frappe.get_doc("Subscription Plan", new_plan_id)
        status = update_k8s_cluster(user, new_plan)
    elif action == "cancel":
        status = delete_k8s_cluster(user)
    else:
        return {"status": "error", "message": "Invalid action"}

    return status
