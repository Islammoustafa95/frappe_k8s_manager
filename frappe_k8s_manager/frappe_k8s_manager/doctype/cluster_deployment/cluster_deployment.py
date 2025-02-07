import frappe
import subprocess
import json

class ClusterDeployment(frappe.model.document.Document):
    """Handles Kubernetes cluster deployments."""
    
    def before_insert(self):
        """Ensure cluster name uniqueness before inserting a new record."""
        existing = frappe.db.exists("Cluster Deployment", {"cluster_name": self.cluster_name})
        if existing:
            frappe.throw(f"Cluster with name '{self.cluster_name}' already exists!")

    def deploy_cluster(self):
        """Deploys the Kubernetes cluster based on stored kubeconfig."""
        self.status = "Deploying"
        self.save()
        frappe.db.commit()

        try:
            # Save kubeconfig to a temporary file
            kubeconfig_path = "/tmp/kubeconfig.yaml"
            with open(kubeconfig_path, "w") as f:
                f.write(self.kubeconfig)

            # Example: Check cluster nodes using kubectl
            cmd = f"KUBECONFIG={kubeconfig_path} kubectl get nodes -o json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                nodes_info = json.loads(result.stdout)
                self.status = "Active"
                self.deployment_logs = json.dumps(nodes_info, indent=2)
            else:
                self.status = "Failed"
                self.deployment_logs = result.stderr

        except Exception as e:
            self.status = "Failed"
            self.deployment_logs = str(e)

        self.save()
        frappe.db.commit()

    def on_trash(self):
        """Prevent deletion if the cluster is active."""
        if self.status == "Active":
            frappe.throw("Cannot delete an active cluster.")
