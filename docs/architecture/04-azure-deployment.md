# Azure deployment view

The local runtime uses native processes. This view maps the same logical containers
to a production-oriented Azure topology. Terraform and Kubernetes definitions in
`infrastructure` encode this target; creating it is a manual, cost-bearing action.

```mermaid
flowchart TB
    internet["Bank workforce browser"]
    gitlab["GitLab CI/CD<br/>OIDC federation"]

    subgraph azure["Azure subscription"]
        frontdoor["Organization edge (planned)<br/>Application Gateway / WAF"]

        subgraph vnet["Private virtual network"]
            subgraph aks["Private AKS cluster"]
                ingress["Ingress controller"]
                web["Web UI pod"]
                api["Banking API pod<br/>Workload identity"]
                ai["AI service pod<br/>Workload identity"]
            end
            postgres[("Azure Database for PostgreSQL<br/>Flexible Server + vector")]
            ml["Azure ML<br/>Managed online endpoint"]
            openai["Azure OpenAI<br/>Private endpoint"]
            vault["Key Vault<br/>Secrets and certificates"]
        end

        acr["Azure Container Registry"]
        monitor["Azure Monitor + Log Analytics"]
        entra["Microsoft Entra ID"]
    end

    internet -->|"HTTPS"| frontdoor --> ingress --> web --> api --> ai
    api --> postgres
    ai --> postgres
    ai --> ml
    ai --> openai
    api --> entra
    api --> vault
    ai --> vault
    gitlab -->|"Build and sign"| acr
    gitlab -->|"Protected deployment"| aks
    acr --> aks
    aks --> monitor
    postgres --> monitor
    ml --> monitor

    classDef cluster fill:#e7efe9,stroke:#427456,color:#17211b
    classDef managed fill:#e8edf3,stroke:#65758a,color:#1d2835
    class web,api,ai,ingress cluster
    class postgres,ml,openai,vault,acr,monitor,entra managed
```

## Security posture

- AKS, PostgreSQL, Azure ML and Azure OpenAI use private networking.
- Pods use workload identity instead of embedded service-principal secrets.
- Key Vault CSI supplies only secrets that cannot use identity directly.
- GitLab deploys through workload identity federation and a protected environment.
- The public edge terminates TLS and applies WAF policy; application pods are not
  directly exposed.

The Terraform baseline implements the private platform and service endpoints. The
public edge remains an explicit integration point because certificates, DNS and a
shared ingress topology are organization-specific. The checked-in Kubernetes
ingress therefore uses a non-routable `.invalid` host and is not a claim of a
production-ready internet boundary.
