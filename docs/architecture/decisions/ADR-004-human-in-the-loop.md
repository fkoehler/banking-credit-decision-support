# ADR-004: Require human credit decisions

**Status:** Accepted

The model estimates risk; it does not approve, reject or recommend a decision.
Every assessed case enters `PENDING_REVIEW`. Only the reviewer role can record an
allowed outcome and an independent comment. Assessment provenance and the human
decision are persisted as separate records.

