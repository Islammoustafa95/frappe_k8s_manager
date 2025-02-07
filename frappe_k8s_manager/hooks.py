app_name = "frappe_k8s_manager"
app_title = "Frappe K8s Manager"
app_publisher = "Your Name"
app_description = "A Frappe app for Kubernetes-based SaaS management"
app_email = "your-email@example.com"
app_license = "MIT"

# Includes in `<head>`
app_include_css = [
    "/assets/frappe_k8s_manager/css/style.css"
]
app_include_js = [
    "/assets/frappe_k8s_manager/js/billing_settings.js",
    "/assets/frappe_k8s_manager/js/subscription_dashboard.js",
    "/assets/frappe_k8s_manager/js/notifications.js"
]

# Website Route Rule
website_route_rules = [
    {"from_route": "/subscription-dashboard", "to_route": "subscription_dashboard"},
    {"from_route": "/billing-settings", "to_route": "billing_settings"}
]

# Doctype JavaScript Events (Client-Side Logic)
doctype_js = {
    "Subscription": "public/js/subscription.js",
    "Billing Settings": "public/js/billing_settings.js"
}

# Fixtures (for Doctype Custom Fields & Permissions)
fixtures = ["Custom Field", "Property Setter"]

# API Whitelist (Public Methods)
api_whitelist = [
    "frappe_k8s_manager.www.subscription_dashboard.get_subscription",
    "frappe_k8s_manager.www.subscription_dashboard.update_subscription",
    "frappe_k8s_manager.billing.billing_settings.get_invoice_history",
    "frappe_k8s_manager.billing.billing_settings.send_invoice"
]

# Doctype Event Hooks
doc_events = {
    "Subscription": {
        "on_update": "frappe_k8s_manager.kubernetes.manage.handle_subscription_update",
        "on_cancel": "frappe_k8s_manager.kubernetes.manage.handle_subscription_cancel"
    },
    "Invoice": {
        "on_submit": "frappe_k8s_manager.billing.billing_settings.send_invoice"
    }
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "frappe_k8s_manager.billing.subscription_reminders.send_reminders"
    ],
    "weekly": [
        "frappe_k8s_manager.billing.cleanup_expired_subscriptions"
    ]
}

# User Data Protection (GDPR Compliance)
user_data_fields = [
    {
        "doctype": "Subscription",
        "filter_by": "user",
        "redact_fields": ["user_email", "billing_info"],
        "partial": 1
    }
]

# Permissions
permission_query_conditions = {
    "Subscription": "frappe_k8s_manager.kubernetes.manage.get_subscription_conditions"
}

# Authentication and Authorization
auth_hooks = [
    "frappe_k8s_manager.auth.validate"
]
