import frappe
import stripe
from frappe.utils import now_datetime, add_days, format_datetime

STRIPE_API_KEY = frappe.conf.get("stripe_secret_key")
stripe.api_key = STRIPE_API_KEY

def send_subscription_reminders():
    """Send automated email reminders for upcoming subscription renewals."""
    try:
        # Get subscriptions expiring in 7 days
        reminder_date = add_days(now_datetime(), 7)
        expiring_subscriptions = frappe.get_all("Subscription", 
                                                filters={"next_billing_date": reminder_date}, 
                                                fields=["name", "user", "plan", "next_billing_date"])
        
        for sub in expiring_subscriptions:
            user = frappe.get_doc("User", sub.user)
            email_content = frappe.render_template("frappe_k8s_manager/templates/emails/subscription_reminder.html", {
                "user_name": user.full_name,
                "plan": sub.plan,
                "billing_date": format_datetime(sub.next_billing_date, "YYYY-MM-DD")
            })
            
            frappe.sendmail(
                recipients=[user.email],
                subject="Your Subscription is Renewing Soon!",
                message=email_content
            )
            
        frappe.logger().info(f"Sent {len(expiring_subscriptions)} subscription reminders.")
    
    except Exception as e:
        frappe.log_error(f"Error in subscription reminders: {str(e)}", "Subscription Reminder Error")
