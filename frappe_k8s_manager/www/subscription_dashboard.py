import frappe
from frappe_k8s_manager.kubernetes.manage import manage_subscription

@frappe.whitelist()
def get_subscription(user_email):
    """Fetch user subscription details."""
    try:
        user = frappe.get_doc("User", {"email": user_email})
        subscription = frappe.get_doc("Subscription", {"user": user.name})

        return {
            "success": True,
            "plan": subscription.plan,
            "disk_space": subscription.disk_space,
            "apps": subscription.apps,
            "status": subscription.status
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "User or subscription not found"}
    except Exception as e:
        frappe.log_error(f"Error fetching subscription for {user_email}: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred"}

@frappe.whitelist()
def update_subscription(user_email, action, new_plan_id=None):
    """Upgrade, downgrade, or cancel the subscription."""
    try:
        # Validate input
        if action in ["upgrade", "downgrade"] and not new_plan_id:
            return {"success": False, "error": "New plan ID is required for this action"}

        result = manage_subscription(action, user_email, new_plan_id)

        return {"success": True, "message": "Subscription updated successfully", "details": result}
    except frappe.DoesNotExistError:
        return {"success": False, "error": "User or subscription not found"}
    except Exception as e:
        frappe.log_error(f"Error updating subscription for {user_email}: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred"}
