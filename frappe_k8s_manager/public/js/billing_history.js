frappe.pages['billing-history'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Billing History',
        single_column: true
    });

    frappe.call({
        method: 'frappe_k8s_manager.www.billing_history.get_billing_history',
        args: { user_email: frappe.session.user },
        callback: function(response) {
            let data = response.message;
            if (data.error) {
                $(wrapper).html(`<p class="text-danger">${data.error}</p>`);
                return;
            }

            let table_html = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Amount</th>
                            <th>Currency</th>
                            <th>Status</th>
                            <th>Invoice</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.forEach(invoice => {
                table_html += `
                    <tr>
                        <td>${invoice.date}</td>
                        <td>${invoice.amount}</td>
                        <td>${invoice.currency}</td>
                        <td>${invoice.status}</td>
                        <td><a href="${invoice.invoice_url}" target="_blank" class="btn btn-info">View Invoice</a></td>
                    </tr>
                `;
            });

            table_html += `</tbody></table>`;
            $(wrapper).html(table_html);
        }
    });
};
