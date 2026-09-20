# Deciding whether a usage is leakage

A checklist for precedent-leakage mode. Each queued item is a usage in the **core** document, not a concept from the source. The question is whether the core document's own current definitions already cover it, or whether its wording and context instead trace back to the named source document.

## The decisions

- **Covered** — the core document's own definitions fully cover this usage. It is not leakage. Use this to clear a usage, not to describe a source-to-core mapping.
- **Leakage** — the usage's wording, scope or context plausibly originates in the named source document's vocabulary and is not covered by anything the core document itself defines. This is the finding this mode exists to produce, and it always goes to the lawyer.
- **False friend** — the label coincides with a source-document term, but on inspection the core document is using it as its own distinct, self-contained concept. Do not flag a usage as leakage merely because a similarly spelled term also appears in the source document; that coincidence alone is not evidence of anything.
- **Narrowed or broadened** — the usage tracks the source concept, but the core document's own surrounding language has already narrowed or broadened it. Worth putting in front of the lawyer rather than silently clearing or silently flagging.
- **Needs review** — more of the documents might settle it.
- **Not enough evidence** — what the two documents say cannot support a decision.

One-to-many, many-to-one and no-mapping are not decisions in this mode.

## What a leakage finding must carry

A leakage finding cites, quoted exactly, the source-document wording the concept appears to have come from, and — where the core document has anything to say on the point — the core-document wording that fails to cover it. Name the specific source concept the flagged usage appears to carry. A finding without both halves is not a finding; report it as needs review instead.

## Rules

A leakage check always names its source document. Never run it as an open sweep across everything the lawyer has ever drafted.

Be slower to flag than to clear when the only evidence is a shared label, and faster to flag when the wording matches a whole limb of the source definition that the core document's own definitions never mention.

Every flagged usage escalates. None of them is corrected in the core document by this skill.
