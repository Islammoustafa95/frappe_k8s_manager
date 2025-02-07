import frappe
import stripe
from frappe.utils import now_datetime, add_days, format_datetime

STRIPE_API_KEY = frappe.conf.get("stripe_secret_key")
stripe.api_key = STRIPE_API_KEY

def send_in_app_notifications():
    """Send in-app notifications for upcoming renewals and failed payments."""
    try:
        # Get subscriptions expiring in 7 days
        reminder_date = add_days(now_datetime(), 7)
        expiring_subscriptions = frappe.get_all("Subscription", 
                                                filters={"next_billing_date": reminder_date}, 
                                                fields=["name", "user", "plan", "next_billing_date"])
        
        for sub in expiring_subscriptions:
            user = frappe.get_doc("User", sub.user)
            
            # Create a Frappe notification
            notification = frappe.get_doc({
                "doctype": "Notification Log",
                "subject": "Your Subscription is Renewing Soon!",
                "content": f"Your {sub.plan} subscription will renew on {format_datetime(sub.next_billing_date, 'YYYY-MM-DD')}.",
                "for_user": user.name,
                "type": "Alert"
            })
            notification.insert(ignore_permissions=True)
            
        # Handle failed payments
        failed_invoices = stripe.Invoice.list(status="open", due_date={"lt": now_datetime().timestamp()})
        for invoice in failed_invoices.auto_paging_iter():
            customer_id = invoice.customer
            customer = frappe.get_value("Stripe Customer", {"stripe_id": customer_id}, "user")
            if customer:
                user = frappe.get_doc("User", customer)
                
                # Send in-app notification for failed payment
                failed_notification = frappe.get_doc({
                    "doctype": "Notification Log",
                    "subject": "Payment Failed!",
                    "content": "Your last payment failed. Please update your billing information.",
                    "for_user": user.name,
                    "type": "Danger"
                })
                failed_notification.insert(ignore_permissions=True)

                # Send email alert
                email_content = frappe.render_template("frappe_k8s_manager/templates/emails/failed_payment.html", {
                    "user_name": user.full_name
                })
                frappe.sendmail(
                    recipients=[user.email],
                    subject="Your Payment Failed!",
                    message=email_content
                )

        frappe.logger().info(f"Sent {len(expiring_subscriptions)} renewal and {len(failed_invoices)} payment failure notifications.")

    except Exception as e:
        frappe.log_error(f"Error in subscription notifications: {str(e)}", "Subscription Notification Error")
