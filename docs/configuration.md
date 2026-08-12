# Configuration reference

All runtime differences are controlled through environment variables. Values below
are safe local defaults unless marked optional. Secrets belong in `.envrc.local`,
GitLab protected variables or Azure Key Vault—never in the repository.

## Runtime and network

| Variable | Default | Meaning |
|---|---|---|
| `APP_ENV` | `local` | Runtime profile label |
| `API_HOST` / `API_PORT` | `127.0.0.1` / `8080` | Spring API listener |
| `AI_HOST` / `AI_PORT` | `127.0.0.1` / `8081` | Internal FastAPI listener |
| `WEB_HOST` / `WEB_PORT` | `127.0.0.1` / `5173` | Vite listener |
| `AI_SERVICE_URL` | `http://127.0.0.1:8081` | Spring-to-Python base URL |
| `VITE_API_URL` | `http://127.0.0.1:8080` | Browser-to-Spring base URL |
| `WEB_ORIGIN` | `http://127.0.0.1:5173` | Allowed browser origin |

## PostgreSQL

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_NAME` | `bank_credit_support` | Dedicated local database |
| `DATABASE_HOST` / `DATABASE_PORT` | `127.0.0.1` / `5432` | Database listener |
| `DATABASE_USER` | current OS user | Database role |
| `DATABASE_PASSWORD` | empty | Local password if required |
| `DATABASE_URL` | derived | Python psycopg URL |
| `JDBC_DATABASE_URL` | derived | Spring JDBC URL |

## Identity

| Variable | Default | Meaning |
|---|---|---|
| `AUTH_MODE` | `local` | `local` or `oidc` |
| `LOCAL_ADVISOR_USERNAME` / `LOCAL_ADVISOR_PASSWORD` | demo credentials | Local advisor login |
| `LOCAL_REVIEWER_USERNAME` / `LOCAL_REVIEWER_PASSWORD` | demo credentials | Local reviewer login |
| `OIDC_ISSUER_URI` | empty | Entra issuer for `oidc` mode |
| `AZURE_TENANT_ID` / `AZURE_CLIENT_ID` | empty | Azure identity metadata |

## AI and retrieval

| Variable | Default | Meaning |
|---|---|---|
| `AI_MODEL_PATH` | repository artifact path | Local risk model bundle |
| `AI_MODEL_METADATA_PATH` | repository metrics path | Model evaluation metadata |
| `AI_INFERENCE_PROVIDER` | `local` | `local` or `azure-ml` |
| `AI_EMBEDDING_PROVIDER` | `local` | `local` or `azure-openai` |
| `AI_GENERATION_PROVIDER` | `template` | `template` or `azure-openai` |
| `AI_VECTOR_STORE` | `postgres` | Vector-store adapter |
| `AI_LOCAL_EMBEDDING_MODEL` | `intfloat/multilingual-e5-small` | FastEmbed model id |
| `AI_EMBEDDING_DIMENSIONS` | `384` | pgvector column dimension |
| `AI_CHUNK_SIZE` / `AI_CHUNK_OVERLAP` | `700` / `100` | Approximate word chunking |
| `AI_RAG_TOP_K` | `5` | Retrieved passages per assessment |

Changing embedding provider, model or dimension requires a fresh vector index.

## Azure providers

All are optional in the default local profile:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_ML_ENDPOINT`
- `AZURE_ML_API_KEY`

AKS should use workload identity instead of API keys where the selected SDK and
service support it. Key variables exist for explicit demo environments only.

