# Azure Terraform baseline

This baseline creates the network, private AKS cluster, ACR, PostgreSQL Flexible
Server with the `vector` extension allowed, Key Vault, Azure OpenAI deployments,
Azure ML workspace, private endpoints and DNS, workload identities, and monitoring
dependencies shown in the
[Azure deployment view](../../docs/architecture/04-azure-deployment.md).

The public WAF/ingress edge shown in the target view is deliberately outside this
baseline. Its design depends on the organization's DNS, certificate, connectivity
and shared-ingress standards; the repository ingress uses an invalid placeholder
host until those decisions are made.

It does not run automatically: applying creates billable resources and model
availability varies by subscription and region.

```bash
az login
cp terraform.tfvars.example terraform.tfvars
export TF_VAR_postgres_admin_password='use-a-secret-source'
terraform init
terraform plan
terraform apply
```

After apply, replace the two workload identity placeholders in the Kubernetes
overlay with Terraform outputs, configure a private CI runner or deployment agent,
create the narrow application database role, and supply runtime secrets through Key
Vault CSI or an approved external-secrets controller.

The bootstrap database password is present in Terraform state. Store remote state
in a locked, encrypted Azure Storage backend and rotate the bootstrap credential
after creating narrower runtime identities. A production bank environment should
prefer PostgreSQL Entra authentication after validating driver and operational
requirements.
