scheduler_events = {
    "daily": [
        "frappe_k8s_manager.tasks.subscription_reminders.send_subscription_reminders"
    ],
    "hourly": [
        "frappe_k8s_manager.tasks.subscription_notifications.send_in_app_notifications"
    ]
}

web_routes = [
    {"from_route": "/billing_settings", "to_route": "billing_settings"}
]