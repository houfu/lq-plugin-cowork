# The playbook format

One Markdown file is the playbook. Both skills read and write this shape: the
builder produces it, the review applies it. Nothing else is canonical, and there
is no database, registry or receipt file behind it.

## The file

`playbook.md`, in the folder the lawyer chose. Its front section is the header,
then one section per issue, then the lenses, then the sources.

```markdown
# <Playbook title>

- Playbook ID: <kebab-case-slug>
- Version: <x.y.z>
- Status: draft | approved | retired
- Agreement family: <e.g. Master Services Agreement>
- Perspective: <represented party, e.g. Supplier>
- Governing law: <jurisdiction, or "not established">
- Built: <date, month spelled in full>
- Sources: S1 … Sn (listed at the end)
```

`Status: approved` is the only status a review may operate on. A `draft`
playbook, or one whose issues are all candidates, is for inspection only.

## An issue

```markdown
### General liability cap (liab-general-cap)

- Status: approved | candidate | conflicted
- Priority: high | medium | low | none
- Preferred: <the house position, in one or two sentences>
- Approved wording: <exact clause text, or "none">
- Fallback 1: <position> — Condition: <when it may be used>
- Fallback 2: …
- Red line: <the position that may not be crossed, or "none">
- Depends on: <other issue IDs, or "none">
- Source: S2, clause 11.2 — "<exact quoted text from that source>"
```

Rules that hold whatever the formatting:

- The heading is the legal topic first, then the kebab-case issue ID in
  brackets. Never lead with a raw identifier.
- Every operative position carries at least one source line with an exact quote
  from a listed source, or an explicit record of the lawyer's own decision.
- Preferred position, ranked fallbacks with their conditions, red line and
  priority are distinct fields. An absent one is written `none`, never inferred.
- `Approved wording` is operative clause text the lawyer approved. A position
  summary is not wording. Where there is none, say `none`.
- `Status: candidate` means visible and non-operative. Only the lawyer's explicit
  approval moves an issue, a wording item or a lens to `approved`.

## Matter Lenses

```markdown
## Matter Lens: Regulated Financial Services (lens-regulated-fs)

- Status: approved | candidate
- Applies when: <the policy trigger, stated as a rule or threshold>
- Adjusts liab-general-cap: Preferred -> 150% of fees; Condition: partner sign-off
- Adjusts payment-terms: Preferred -> 60 days
- Source: S3, clause 9.1 — "<exact quoted text>"
```

A lens is a named, reusable set of adjustments to named issues. It never
activates itself and never rewrites the baseline. Standard Baseline is the
default posture for every review; a lens applies only when the lawyer says so in
their own words, in that review.

Two active lenses that set different values for the same field of the same issue
block the stance. Say which lenses, which issue, which field and which values,
and stop. Never resolve it by frequency, recency, score or hidden precedence.
An explicit matter instruction from the lawyer applies last and stays visible in
the trace; conflicting matter instructions also block the stance.

## Sources

```markdown
## Sources

- S1 — MSA_Standard_Template.docx — approved-template — read in full
- S2 — Halcyon_Executed_2026.docx — negotiated-final — read in full
- S3 — KM note on regulated clients.md — km-guidance — read in full
- S4 — Vendor_MSA_scan.pdf — unannotated-precedent — pages 4-6 unreadable
```

Source roles are `approved-template`, `negotiated-final`, `unannotated-precedent`
and `km-guidance`. The evidence hierarchy is, strongest first: explicit lawyer
confirmation or approved KM guidance; approved house template; negotiated final
agreement; unannotated precedent. Frequency is evidence of recurrence, not
approval.

Record what you could not read as plainly as what you could. A document with
unresolved tracked changes, an encrypted file, or a page you cannot read is not
settled evidence: keep it visible and resolve or exclude it at the gate.

## Defined terms

List the house defined terms that approved wording depends on, with their exact
definitions, at the end of the playbook. A review maps each of them into the
contract under review before proposing any drafting that uses them, and records
one of:

- `exact` — same label, same definition text.
- `equivalent` — different drafting, substantially the same legal scope; cite
  both definitions and say why.
- `undefined` — the contract has no counterpart; a separate proposed definition
  insertion is required before the term may be used.
- `defined-differently` — the scopes differ; a hard stop for any drafting that
  uses the term. Show both definitions to the lawyer rather than guessing.
- `unresolved` — no safe answer yet; non-operative until assessed.

A wording difference alone is never a deviation. Approved house wording is a
provenance source, not a style template to impose: suggested drafting passes
through the mapped terms and makes only the minimum change needed.

## Drafting provenance and coverage

Every suggested change records its provenance as one of `approved-playbook`,
`candidate-drafting`, `mixed` or `none`. A playbook gap is never presented as
approved policy.

Coverage reconciles in three independent counts, and all three are shown:

- documents: completed + parked + unreadable = expected;
- contract sections or elements: completed + parked + unreadable = expected;
- operative rules: evaluated + not applicable + blocked = expected.

Reconciled means all three balance. It proves accounting, not the correctness of
any legal judgment.
