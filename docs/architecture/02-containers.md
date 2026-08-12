# C4 level 2 — Containers

In C4, a container is an independently running application or data store, not
necessarily a Docker container.

```mermaid
flowchart TB
    user["Advisor / risk reviewer"]

    subgraph product["Banking Credit Decision Support"]
        ui["Web UI<br/>React + TypeScript<br/>Case entry and review"]
        api["Banking API<br/>Java 21 + Spring Boot<br/>Public API, RBAC, workflow, audit"]
        ai["AI service<br/>Python + FastAPI<br/>Training, inference, RAG, explanations"]
        db[("PostgreSQL + pgvector<br/>Cases, decisions, documents, vectors")]
        artifacts["Versioned model artifacts<br/>Model, schema, metrics, model card"]
    end

    llm["Azure OpenAI<br/>Optional cloud generation and embeddings"]
    ml["Azure ML managed endpoint<br/>Optional cloud risk inference"]
    identity["Microsoft Entra ID<br/>Optional cloud authentication"]

    user -->|"HTTPS"| ui
    ui -->|"JSON/HTTPS"| api
    api -->|"Internal JSON/HTTP"| ai
    api -->|"JDBC"| db
    ai -->|"SQL + vector queries"| db
    ai --> artifacts
    ai -.->|"Azure profile"| llm
    ai -.->|"Azure profile"| ml
    api -.->|"OIDC profile"| identity

    classDef public fill:#1f5738,stroke:#123c26,color:#fff
    classDef internal fill:#e7efe9,stroke:#427456,color:#17211b
    classDef data fill:#f3ead7,stroke:#9a7236,color:#2b2519
    class ui,api public
    class ai internal
    class db,artifacts data
```

## Dependency rule

The UI only calls the Banking API. The API may degrade when the AI service is
unavailable, but the AI service never becomes a second public business API.

