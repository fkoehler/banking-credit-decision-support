# Banking Credit Decision Support

An unofficial, synthetic reference application showing how a bank could combine
an explainable credit-risk model, retrieval-augmented generation (RAG), human
review, DevSecOps and an Azure/AKS target architecture.

> **Demo only:** This repository is not affiliated with any real bank. It uses
> generated data and fictional policies and must not be used for credit decisions.

## What the demo shows

- Java 21 and Spring Boot for the business workflow, security and audit trail.
- Python and scikit-learn for reproducible model training and inference.
- PostgreSQL plus pgvector for policy retrieval.
- A small React UI for advisor and reviewer workflows.
- Local AI adapters that work without cloud credentials, plus configurable Azure
  OpenAI and Azure Machine Learning adapters.
- Terraform, AKS manifests and a GitLab pipeline with explicit security gates.

## Start locally

The standard workflow is native and does not require Docker. It expects SDKMAN,
direnv, Python 3.12/uv, Node 22+/pnpm and PostgreSQL with the `vector` extension.

```bash
sdk env install
direnv allow
./dev doctor
./dev bootstrap
./dev up
```

Then open [http://localhost:5173](http://localhost:5173). Demo accounts:

| Role | User | Password |
|---|---|---|
| Advisor | `advisor` | `advisor-demo` |
| Risk reviewer | `reviewer` | `reviewer-demo` |

Seed fictional policies and a sample case with:

```bash
./dev seed
```

Stop only the processes started by this project:

```bash
./dev down
```

See [Local development](docs/local-development.md) for installation and
troubleshooting, [Configuration](docs/configuration.md) for every environment
variable, and [Architecture](docs/architecture/README.md) for the GitHub-rendered
C4 diagrams and design decisions.

## Repository map

```text
services/banking-api   Spring Boot public API and workflow
services/ai-service    Python model training, inference and RAG
services/web-ui        React/Vite demo interface
docs                   Architecture, ADRs, operations and demo script
infrastructure         Terraform, Kubernetes and Azure ML definitions
```

## Quality checks

```bash
./dev test
```

The same checks are split into test, security, build and infrastructure stages in
`.gitlab-ci.yml`.
