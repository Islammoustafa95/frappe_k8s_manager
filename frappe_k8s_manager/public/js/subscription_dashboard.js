frappe.pages['subscription-dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Subscription Dashboard',
        single_column: true
    });

    frappe.call({
        method: 'frappe_k8s_manager.www.subscription_dashboard.get_subscription',
        args: { user_email: frappe.session.user },
        callback: function(response) {
            let data = response.message;
            $(wrapper).html(`
                <div class="subscription-info">
                    <h3>Current Plan: ${data.plan}</h3>
                    <p>Disk Space: ${data.disk_space} GB</p>
                    <p>Installed Apps: ${data.apps}</p>
                    <p>Status: ${data.status}</p>
                    <button class="btn btn-primary" id="upgrade-plan">Upgrade</button>
                    <button class="btn btn-warning" id="downgrade-plan">Downgrade</button>
                    <button class="btn btn-danger" id="cancel-subscription">Cancel</button>
                </div>
            `);

            $('#upgrade-plan').click(() => updateSubscription('upgrade'));
            $('#downgrade-plan').click(() => updateSubscription('downgrade'));
            $('#cancel-subscription').click(() => updateSubscription('cancel'));
        }
    });

    function updateSubscription(action) {
        let new_plan = action !== "cancel" ? prompt("Enter New Plan ID") : null;
        frappe.call({
            method: 'frappe_k8s_manager.www.subscription_dashboard.update_subscription',
            args: { user_email: frappe.session.user, action: action, new_plan_id: new_plan },
            callback: function(response) {
                frappe.msgprint(response.message);
            }
        });
    }
};
