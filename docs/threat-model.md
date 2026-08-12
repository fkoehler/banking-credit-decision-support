# Threat model

This lightweight threat model identifies the most important trust boundaries for
the reference implementation. It is not a production security assessment.

| Threat | Example | Control in this repository | Remaining work |
|---|---|---|---|
| Broken access control | Advisor records a decision | Spring role check and separate decision endpoint | Map and test real Entra group claims |
| Prompt injection | Policy text tells the model to ignore rules | Retrieved text is supplied as untrusted context; system instruction restricts use | Add adversarial RAG evaluation and content quarantine |
| Unsupported generated claim | Narrative invents a policy | Citations and template fallback remain visible | Enforce structured claim-to-source validation |
| Secret exposure | Cloud key committed or logged | `.envrc.local`, GitLab secret scan, workload identity design | Central rotation and incident runbook |
| Model supply-chain attack | Artifact is replaced | Version and metrics travel with the result | Sign artifacts, SBOM and verify provenance before load |
| Malicious document | Oversized or crafted upload | API size constraints and idempotent checksum design | MIME inspection, antivirus and isolated PDF extraction |
| Data leakage | Full case appears in logs or LLM request | Synthetic-only boundary and no payload logging | Field-level redaction and approved data classification |
| Dependency vulnerability | Compromised package or image | Lockfiles, SCA and Trivy pipeline jobs | SLA-driven patch and exception process |

## Trust boundaries

1. Browser to public Spring API.
2. Spring API to internal Python API.
3. Application workloads to PostgreSQL and model artifacts.
4. AI service to Azure OpenAI and Azure ML.
5. CI/CD to registry and AKS.

Every boundary needs authenticated transport in an Azure deployment. The local
profile optimizes inspectability and uses conspicuous demo credentials instead.
