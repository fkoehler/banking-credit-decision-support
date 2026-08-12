# ADR-001: Separate business and AI services

**Status:** Accepted

Spring Boot owns public contracts, security, workflow and audit. Python owns model
training, inference and retrieval behind an internal API. This keeps enterprise
business rules independent from the faster-moving AI toolchain, at the cost of one
additional runtime and a contract that needs testing.

