document.addEventListener("DOMContentLoaded", function() {
    fetchPlans();

    document.getElementById("subscribe-button").addEventListener("click", function() {
        let selectedPlan = document.querySelector('input[name="plan"]:checked');
        if (!selectedPlan) {
            alert("Please select a subscription plan.");
            return;
        }

        let planId = selectedPlan.value;

        fetch('/api/method/frappe_k8s_manager.www.subscription.process_subscription', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ plan_id: planId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                window.location.href = data.checkout_url;
            } else {
                alert("Subscription failed: " + data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});

function fetchPlans() {
    fetch('/api/method/frappe_k8s_manager.www.subscription.get_plans')
    .then(response => response.json())
    .then(data => {
        let plansContainer = document.getElementById("plans-container");
        plansContainer.innerHTML = "";

        data.plans.forEach(plan => {
            let planElement = `
                <div class="plan">
                    <input type="radio" name="plan" value="${plan.name}">
                    <label>${plan.plan_name} - $${plan.price}/month</label>
                </div>
            `;
            plansContainer.innerHTML += planElement;
        });
    })
    .catch(error => console.error("Error:", error));
}
