frappe.pages['dashboard'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Dashboard',
        single_column: true
    });

    frappe.call({
        method: 'frappe.desk.notifications.get_notification_info_for_user',
        callback: function(response) {
            let notifications = response.message.notifications;
            let notification_html = '<ul class="list-group">';

            notifications.forEach(noti => {
                notification_html += `
                    <li class="list-group-item ${noti.type === 'Danger' ? 'list-group-item-danger' : 'list-group-item-info'}">
                        <strong>${noti.subject}</strong> - ${noti.content}
                    </li>`;
            });

            notification_html += '</ul>';
            $(wrapper).html(notification_html);
        }
    });
};
