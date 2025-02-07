import subprocess
import frappe
import requests

CLOUDFLARE_API_TOKEN = "your_cloudflare_api_token"
KUBERNETES_SERVER = "your_kubernetes_server"

def create_k8s_cluster(user_email, plan_id):
    """Deploy ERPNext on Kubernetes for a new customer"""
    user = frappe.get_doc("User", {"email": user_email})
    plan = frappe.get_doc("Subscription Plan", plan_id)

    namespace = f"erpnext-{user.name.lower()}"
    subdomain = f"{user.name.lower()}.yourdomain.com"

    try:
        # Step 1: Create Namespace
        subprocess.run(["kubectl", "create", "namespace", namespace], check=True)

        # Step 2: Deploy ERPNext using Helm
        helm_cmd = [
            "helm", "install", namespace,
            "frappe/erpnext",
            "--namespace", namespace,
            "--set", f"ingress.hostname={subdomain}",
            "--set", f"persistence.size={plan.disk_space}Gi",
            "--set", f"extraApps={plan.extra_apps}"
        ]
        subprocess.run(helm_cmd, check=True)

        # Step 3: Update Cloudflare DNS
        update_dns_record(subdomain)

        # Step 4: Notify User
        frappe.sendmail(
            recipients=[user_email],
            subject="Your ERPNext Instance is Ready!",
            message=f"Your ERPNext site is live at: https://{subdomain}. \nLogin with your email and password."
        )

        return {"status": "success"}

    except subprocess.CalledProcessError as e:
        frappe.log_error(f"Kubernetes Deployment Failed: {str(e)}")
        return {"status": "error", "error": str(e)}

def update_dns_record(subdomain):
    """Automatically updates Cloudflare DNS for the new subdomain"""
    url = f"https://api.cloudflare.com/client/v4/zones/your_zone_id/dns_records"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "CNAME",
        "name": subdomain,
        "content": KUBERNETES_SERVER,
        "ttl": 120,
        "proxied": True
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
