import subprocess
import frappe

def update_k8s_cluster(user, new_plan):
    """Upgrade or downgrade Kubernetes cluster based on new plan."""
    namespace = f"erpnext-{user.name.lower()}"

    try:
        # Update Helm deployment
        helm_cmd = [
            "helm", "upgrade", namespace, "frappe/erpnext",
            "--namespace", namespace,
            "--set", f"persistence.size={new_plan.disk_space}Gi",
            "--set", f"extraApps={new_plan.extra_apps}"
        ]
        subprocess.run(helm_cmd, check=True)

        # Notify User
        frappe.sendmail(
            recipients=[user.email],
            subject="Your ERPNext Subscription Has Been Updated",
            message=f"Your ERPNext instance has been updated to the {new_plan.name} plan."
        )

        return {"status": "success"}
    
    except subprocess.CalledProcessError as e:
        frappe.log_error(f"Upgrade/Downgrade Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def delete_k8s_cluster(user):
    """Delete the user's Kubernetes namespace when they cancel their subscription."""
    namespace = f"erpnext-{user.name.lower()}"

    try:
        # Delete Helm release
        subprocess.run(["helm", "uninstall", namespace, "--namespace", namespace], check=True)

        # Delete Namespace
        subprocess.run(["kubectl", "delete", "namespace", namespace], check=True)

        # Notify User
        frappe.sendmail(
            recipients=[user.email],
            subject="Your ERPNext Subscription Has Been Cancelled",
            message="Your ERPNext instance has been successfully deleted."
        )

        return {"status": "success"}

    except subprocess.CalledProcessError as e:
        frappe.log_error(f"Deletion Failed: {str(e)}")
        return {"status": "error", "message": str(e)}
