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
- GitHub Actions for the repository's public test signal.

## How the application works

The application supports a bank employee while reviewing a fictional
practice-financing case. It deliberately separates four responsibilities:

1. **Classical ML estimates risk.** Training creates 8,000 deterministic,
   synthetic cases and compares logistic regression with gradient boosting. The
   candidate with the lower validation Brier score is selected; the checked-in
   model is gradient boosting. It learns statistical associations in this
   generated dataset, not real-world lending rules or causal relationships.
2. **RAG finds relevant policy evidence.** Fictional policies are split into
   sections, converted to embeddings and stored in PostgreSQL with pgvector. A
   vector search retrieves the passages that are semantically closest to the
   current case.
3. **A generator explains the evidence.** The local default uses a deterministic
   template. When Azure OpenAI is configured, an LLM receives the already
   calculated risk score, visible input factors and retrieved passages and turns
   them into a readable, source-linked explanation. It neither calculates the
   score nor makes the decision.
4. **A human reviewer decides.** The reviewer checks the original inputs, model
   output and cited policy passages, then records an independent decision and
   comment in the audit trail.

### Concrete example

The prepared demo case describes a dentist with EUR 185,000 annual income,
EUR 620,000 practice revenue, four years of operating history, EUR 80,000
existing debt, a requested credit of EUR 450,000, EUR 100,000 equity and no late
payments. From these values, the application derives an equity ratio of 22.2%
and a debt-to-income ratio of 0.43. With the currently checked-in model artifact,
the ML service estimates a probability of default of about 3.3%; retraining or a
different model version may change that value.

RAG then retrieves passages such as the fictional equity-contribution and
capacity-review sections. The template or configured LLM combines the score,
the visible factors and those cited passages into an explanation for the
reviewer. A low score therefore does not approve the credit: only the human
reviewer records the final outcome.

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
`.gitlab-ci.yml`; `.github/workflows/ci.yml` runs the portable test and platform
validation subset on GitHub.
