# Kubernetes deployment contract

`base` contains provider-neutral workloads and policies. `overlays/azure` adds the
AKS workload-identity annotations and Azure Container Registry image locations.

Render both variants without contacting a cluster:

```bash
kubectl kustomize infrastructure/kubernetes/base
kubectl kustomize infrastructure/kubernetes/overlays/azure
```

Before applying the Azure overlay:

1. Replace the example ACR hostname and immutable image tags.
2. Replace both workload-identity client-id placeholders with Terraform outputs.
3. Replace `credit-support.example.invalid` with an approved private or public host.
4. Create `app-secrets` through Key Vault CSI or the organization's approved
   external-secrets controller. It must provide `JDBC_DATABASE_URL`,
   `DATABASE_URL`, `DATABASE_USER`, `DATABASE_PASSWORD`, `OIDC_ISSUER_URI`,
   `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`,
   `AZURE_OPENAI_CHAT_DEPLOYMENT`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, and
   `AZURE_ML_ENDPOINT`.
5. Ensure the ingress controller and private DNS/network path exist. They are not
   installed by this application overlay.

Never commit a rendered Secret. Workload identity is the default for Azure OpenAI
and Azure ML; API-key variables exist only for explicit demo environments.
