# Project context

Banking Credit Decision Support is an unofficial reference implementation for a
fictional practice-financing workflow. It demonstrates application development,
classical machine learning, RAG, human review and a secure Azure platform without
using real bank or customer data.

## User journey

1. An advisor enters a synthetic financing case.
2. The application requests a probability-of-default estimate from a versioned
   model trained on generated data.
3. The AI service retrieves relevant passages from fictional policies in pgvector.
4. A template or Azure OpenAI explains the result and cites those passages.
5. A risk reviewer considers the evidence and records a human decision.

The model is an input to the workflow, never the decision maker. Input factors are
associations and must not be presented as causal explanations.

## Current scope

The repository contains one end-to-end MVP, a native local runtime, provider
interfaces for Azure, GitHub-readable architecture documentation, and deployable
infrastructure definitions. Real customer data, production certification, LLM
fine-tuning and fraud detection are explicitly out of scope.

## Source map

- `services/banking-api`: public Spring Boot boundary, workflow, RBAC and audit.
- `services/ai-service`: synthetic training, inference, embeddings and retrieval.
- `services/web-ui`: compact React interface for the demonstration.
- `infrastructure`: Azure, AKS and Azure ML deployment definitions.
- `docs`: architecture, decisions, configuration and operating instructions.

