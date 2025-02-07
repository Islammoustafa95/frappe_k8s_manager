$(document).ready(function() {
    // Fetch Billing Info
    frappe.call({
        method: "frappe_k8s_manager.www.billing_settings.get_billing_info",
        callback: function(response) {
            if (response.message.error) {
                $("#billing-info").html(`<p>${response.message.error}</p>`);
            } else {
                $("#plan_name").text(response.message.plan_name);
                $("#billing_date").text(response.message.billing_date);
            }
        }
    });

    // Update Payment Method
    $("#update-payment-btn").click(function() {
        frappe.call({
            method: "frappe_k8s_manager.www.billing_settings.update_payment_method",
            callback: function(response) {
                if (response.message.error) {
                    frappe.msgprint(response.message.error);
                } else {
                    window.location.href = response.message.url;
                }
            }
        });
    });

    // Change Subscription Plan
    $("#change-plan-btn").click(function() {
        let selectedPlan = $("#plan-selection").val();

        frappe.call({
            method: "frappe_k8s_manager.www.billing_settings.change_subscription",
            args: { new_plan: selectedPlan },
            callback: function(response) {
                frappe.msgprint(response.message.message || response.message.error);
                location.reload();
            }
        });
    });

    // Cancel Subscription
    $("#cancel-subscription-btn").click(function() {
        if (confirm("Are you sure you want to cancel your subscription?")) {
            frappe.call({
                method: "frappe_k8s_manager.www.billing_settings.cancel_subscription",
                callback: function(response) {
                    frappe.msgprint(response.message.message);
                    location.reload();
                }
            });
        }
    });
});


$(document).ready(function() {
    // Fetch Invoice History
    frappe.call({
        method: "frappe_k8s_manager.www.billing_settings.get_invoice_history",
        callback: function(response) {
            let invoiceList = $("#invoice-list");
            invoiceList.empty();

            if (response.message.error) {
                invoiceList.append(`<tr><td colspan="3">${response.message.error}</td></tr>`);
            } else {
                response.message.forEach(invoice => {
                    invoiceList.append(`
                        <tr>
                            <td>${invoice.date}</td>
                            <td>${invoice.amount}</td>
                            <td><a href="${invoice.url}" target="_blank" class="btn btn-sm btn-primary">Download</a></td>
                        </tr>
                    `);
                });
            }
        }
    });
});
