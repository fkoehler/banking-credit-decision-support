# C4 level 1 — System context

This is the widest view. It deliberately avoids implementation details and shows
the people and managed platforms that interact with the decision-support system.

```mermaid
flowchart LR
    advisor["Advisor<br/>Creates a fictional financing case"]
    reviewer["Risk reviewer<br/>Examines evidence and decides"]
    system["Banking Credit Decision Support<br/>Produces model evidence, policy passages<br/>and an assisted explanation"]
    entra["Microsoft Entra ID<br/>Workforce identity and roles"]
    azureai["Azure AI services<br/>OpenAI inference and ML endpoint"]

    advisor -->|"Submits case data"| system
    system -->|"Assessment and sources"| advisor
    reviewer -->|"Records accountable decision"| system
    system -->|"Decision history"| reviewer
    system <-->|"OIDC in Azure profile"| entra
    system <-->|"Model and language inference"| azureai

    classDef person fill:#f4e7c7,stroke:#9a7236,color:#2b2519
    classDef product fill:#1f5738,stroke:#123c26,color:#fff
    classDef external fill:#e8edf3,stroke:#65758a,color:#1d2835
    class advisor,reviewer person
    class system product
    class entra,azureai external
```

## Trust boundary

The system treats identity assertions, uploaded policy text, model artifacts and
generated language as separate trust domains. A valid reviewer identity is still
required after the AI steps complete.

