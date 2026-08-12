# ADR-003: Keep a deterministic local generation mode

**Status:** Accepted

The default local profile performs real ML inference and vector retrieval but uses
a deterministic template for the narrative. A cloud key is not required for the
demo, provider failures are visible, and tests remain reproducible. The Azure
profile can replace embeddings and generation through the same interfaces.

