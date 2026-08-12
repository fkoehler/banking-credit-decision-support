# C4 level 3 — Components

This view zooms into the two backend containers. Arrows show runtime dependency
direction, not package imports.

```mermaid
flowchart LR
    ui["Web UI"]

    subgraph java["Banking API — Spring Boot"]
        controllers["REST controllers<br/>Validation and transport"]
        security["Security configuration<br/>Local RBAC / OIDC profile"]
        workflow["Credit case service<br/>Workflow and human decisions"]
        aiclient["AI client<br/>Internal contract adapter"]
        repos["JPA repositories<br/>Business persistence"]
    end

    subgraph python["AI service — FastAPI"]
        endpoint["Assessment endpoint<br/>Orchestration"]
        risk["Risk model<br/>Feature schema and inference"]
        retrieval["RAG engine<br/>Chunking and retrieval"]
        providers["Provider adapters<br/>Local / Azure"]
        generator["Explanation generator<br/>Template / Azure OpenAI"]
        training["Training workflow<br/>Synthetic data and evaluation"]
    end

    database[("PostgreSQL + pgvector")]
    model["Model artifact + metrics"]

    ui --> controllers
    security --> controllers
    controllers --> workflow
    workflow --> aiclient
    workflow --> repos
    aiclient --> endpoint
    endpoint --> risk
    endpoint --> retrieval
    endpoint --> generator
    retrieval --> providers
    generator --> providers
    repos --> database
    retrieval --> database
    training --> model
    risk --> model

    classDef boundary fill:#1f5738,stroke:#123c26,color:#fff
    classDef component fill:#edf2ed,stroke:#5e7b68,color:#17211b
    class controllers,endpoint boundary
    class security,workflow,aiclient,repos,risk,retrieval,providers,generator,training component
```

## Important contracts

- The public API uses versioned `/api/v1` resources.
- The Python API is explicitly internal under `/internal/v1`.
- Every assessment returns model version, generation mode and source citations.
- The persisted decision is separate from the assessment and requires reviewer role.

