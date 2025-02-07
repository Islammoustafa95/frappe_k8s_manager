import frappe
from frappe.model.document import Document

class Subscription(Document):
    def before_save(self):
        # Ensure the next billing date is always after the start date
        if self.next_billing_date <= self.start_date:
            frappe.throw("Next billing date must be after the start date.")
