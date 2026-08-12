# ADR-002: Use RAG instead of fine-tuning for policy knowledge

**Status:** Accepted

Policies change and answers must expose their sources. The system chunks and embeds
documents, retrieves relevant passages and supplies them at inference time. It does
not fine-tune a language model to memorize policy content. Updating knowledge is
therefore auditable and does not require changing model weights.

