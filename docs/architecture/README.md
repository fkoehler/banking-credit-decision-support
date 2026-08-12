# Architecture documentation

## What is C4?

C4 explains software architecture by zooming in, similar to an online map:

1. **System context** shows people and external systems around the product.
2. **Containers** shows the independently running applications and data stores.
3. **Components** shows the main responsibilities inside those applications.
4. **Code** can show individual classes, but is intentionally omitted here because
   code diagrams become stale quickly and the source is clearer at that level.

This documentation adds a deployment view for the Azure runtime. All diagrams use
standard Mermaid flowcharts inside Markdown, so GitHub renders them directly in the
repository without a documentation server or exported image.

## Views

| View | Question answered |
|---|---|
| [1. System context](01-system-context.md) | Who uses the system and what surrounds it? |
| [2. Containers](02-containers.md) | Which applications and stores run? |
| [3. Components](03-components.md) | How is an assessment implemented? |
| [4. Azure deployment](04-azure-deployment.md) | Where do those parts run in Azure? |
| [5. Runtime sequences](05-runtime-sequences.md) | What happens during ingestion and assessment? |

## Principles

- Spring Boot owns the public API, authorization, workflow and audit trail.
- Python owns model and retrieval concerns behind an internal interface.
- Generated text is evidence-linked assistance, never an autonomous decision.
- The local and Azure provider profiles share the same business contracts.
- Secrets enter through local ignored overrides or managed Azure identities.

Architecture decisions are recorded in [`decisions`](decisions/README.md).

