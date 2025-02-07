import frappe
from frappe.model.document import Document

class UserSubscription(Document):
    def before_insert(self):
        """Ensure there is no duplicate active subscription"""
        existing_subscription = frappe.get_all(
            "User Subscription",
            filters={"user": self.user, "status": "Active"},
            fields=["name"]
        )
        if existing_subscription:
            frappe.throw("User already has an active subscription.")
