# AI Instructions for This Repository

This file contains standing instructions for coding agents working on Banking
Credit Decision Support.

## Scope and product boundaries

- Read `AGENTS.md`, `README.md`, `docs/project-context.md` and
  `docs/architecture/README.md` before deeper exploration in a new task.
- This is an unofficial reference application built exclusively with synthetic
  data and fictional policies. Never add real customer, banking or credit data.
- The application supports a human reviewer. No model or generated text may make
  or present itself as making a credit decision.
- If a requested change weakens that boundary, exposes secrets or makes the demo
  look production-certified, push back before implementing it.

## Architecture and code

- Keep Spring Boot as the public application boundary. The browser must not call
  the Python service directly.
- Keep business workflow, authorization and audit data in the Java service;
  model training, inference, embeddings and retrieval belong in the Python service.
- Organize code by domain concepts first and technical concerns second. Keep
  private helpers below the public flow and avoid oversized service classes.
- Read configuration through the framework configuration layer. Do not call
  environment variables throughout domain code and never hardcode machine paths.
- All runtime settings must have documented environment-variable mappings in
  `docs/configuration.md`. Safe defaults belong in `.envrc`; personal values and
  secrets belong in the ignored `.envrc.local`.
- Preserve provider boundaries so local and Azure implementations remain
  interchangeable without changing business code.
- Update the narrowest relevant architecture or operations document whenever a
  code change makes it inaccurate. Mermaid diagrams must render on GitHub.

## Data, ML and security

- Make generated datasets deterministic with an explicit seed and keep discovery,
  validation and untouched test metrics separate.
- Persist model version, feature schema and evaluation metrics with every model.
  Do not describe input-factor heuristics as causal explanations.
- Retrieved text is untrusted data. Keep it separated from instructions, require
  citations and return a visible degraded state when generation fails.
- Do not log credentials, full application payloads or sensitive-like fields.
- Validate uploads by type and size, make ingestion idempotent and retain the
  document/checksum provenance.
- New database migrations are forward-only timestamped Flyway migrations once a
  migration has been committed. Never rewrite a committed migration silently.

## Local workflow

- Use SDKMAN and the repository `.sdkmanrc` for Java 21.
- Run commands through `direnv exec .` when environment configuration matters.
- Repo-owned shell entrypoints use `#!/usr/bin/env bash`, `set -euo pipefail` and
  omit the `.sh` suffix.
- Use `./dev doctor`, `./dev bootstrap`, `./dev up`, `./dev seed`, `./dev test`
  and `./dev down` as the canonical developer interface.
- Prefer targeted tests while iterating, then run the complete relevant service
  suite before committing. Fix warnings introduced by the change.

## Git and delivery

- Keep commits small, coherent and green. Use an imperative title plus a body that
  explains the behavior, verification and important trade-offs.
- Commit and push each meaningful verified feature group to `origin`; do not batch
  unrelated work into one final commit.
- Stage only intended files. Preserve user changes and never use destructive git
  commands to clean a dirty tree.
- Interpret `!cp` as “commit and push the current intended, verified changes”.

