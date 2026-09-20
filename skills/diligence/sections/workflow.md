## Workflow

1. **Inventory and identity.** Walk the tranche the lawyer supplied. For every
   file record, in the `Documents` sheet of the master register: a short stable
   label, the filename, the page count, the document's own date, the first line
   of page one, whether it reads as native text or as a scan, and whether it
   opened at all. Those four middle fields are the document's fingerprint;
   re-read and compare them at the start of every later session and report any
   mismatch, naming the row and both readings, before doing anything else. Mark
   a request list, schedule or instruction document as `instruction` only when
   the lawyer confirms it governs the run rather than being an agreement to
   review; it stays in the counts and the source table but never becomes a
   sample unit or a row in the issue grid. Encrypted files cannot be read: list
   them and park them. Files over 200 MB cannot be attached: name them and ask
   the lawyer how to supply them. Leave every source file untouched where it
   is. Then report the counts to the lawyer: files, instruction inputs,
   substantive files, how many read as text and how many as scans, and the gaps
   found so far.

2. **Read each document once.** Take the documents in register order, one at a
   time, holding only that document while you read it. Read the opening pages
   and the signature block and record the fields in
   [the one-document reading contract](references/shared/metadata-reader-prompt.md):
   type, title, parties, date, and the instruments it refers to. Every field
   carries the exact words it came from. Try a document at most twice, then
   park it as `metadata-incomplete` and move on; a parked document stays in the
   counts. Then go back over the recorded fields and find each quoted string
   again in its source. A quote you cannot find again does not get waved
   through: the field is blanked and the document is parked as
   `quote-unverified`.

3. **Relationships and families.** Group documents that plausibly belong
   together — shared parties once names are normalised, shared title words,
   a filename or index-number prefix, an explicit cross-reference — and only
   compare pairs inside a group. Where one document names another by title,
   date and parties, read the link straight off that reference. Where it is
   ambiguous, decide the pair under
   [the relationship contract](references/shared/edge-resolver-prompt.md),
   working only from the two recorded metadata blocks and never from the
   documents themselves. Every link carries the exact words that establish it,
   and a link you decided rather than read is shown to the lawyer as proposed.

4. **Compile the checklist.** Take the lawyer's checklist in whatever form it
   arrives and compile it into the framework shape in
   [references/framework-schema.md](references/framework-schema.md):
   conservative factual hit rules, an explicit empty exclusions list, and the
   rule for when an item is unresolved. Omit materiality entirely unless the
   lawyer supplied ranking rules; never invent or default a severity. Check the
   compiled framework against its own contract, and where it will not come
   right in two attempts ask the lawyer rather than looping. Then write the
   read-back: one plain-English row per issue, no field names. Every issue must
   trace to a named instruction input.

5. **Confirm the review setup (Gate 1).** Pick five representative substantive
   units, or every unit when there are five or fewer, and write down for each
   its label, a plain-language description and why it was picked. Build the
   review setup page per
   [references/review-ui.md](references/review-ui.md), carrying the read-back,
   the document counts, the family map with proposed links shown as proposed,
   the gaps, and the sample. Show that page — not an internal summary. It asks
   whether the questions, the collection and the scope are right. The lawyer
   confirms or regroups the families and confirms the exact setup statement in
   their reply; record that confirmation as a dated line in the register's
   `Counts` sheet and treat the family map as settled from then on. A bare
   "continue" does not carry this gate.

6. **Review the test results (Gate 2).** Run every confirmed issue against each
   sampled unit, one unit and one lens at a time, under
   [the issue-review contract](references/shared/finding-worker-prompt.md).
   Build the test-results page: factual matches, scoped negatives, items
   needing a decision, the quoted passage in full beside each finding, and the
   match definitions in plain language. Stable identifiers and framework
   versions stay in the collapsed technical area. The lawyer's feedback names
   the review question and says what should have counted differently; turn that
   into the corresponding framework fields, recompile as version N+1, check it,
   and rerun the sample whenever the test for an issue changed. Their sign-off
   freezes that version, and the frozen version number goes in the register.

7. **Scale, a tranche at a time.** Agree the scope of the run with the lawyer
   before starting it: which units, how many, and the boundary of this tranche.
   Then work the tranche one unit and one lens at a time, appending a
   `Findings` row for every issue against every unit — present, absent,
   unresolved or parked, never blank. A unit is the confirmed family where
   relationships exist, else the single agreement. A present row carries the
   verbatim quote and where it sits, and marks the current position only when
   the whole family including later amendments was read. Retry a rejected
   judgment at most twice, then park it visibly with its reason. Report, in the
   reply, the row count you read in and the row count you wrote out, and hand
   the register back. The next tranche begins with the lawyer attaching it.

8. **Locate the quotes, then check the findings again.** For every present
   finding, find its quoted words again in the source and record where they
   sit; a quote you cannot locate turns the finding to unresolved. Then make a
   second pass over every remaining present finding — every one of them, never
   only the ones ranked material, since an issue with no ranking rule must not
   escape checking — under
   [the checking contract](references/shared/finding-checker-prompt.md).
   That pass sees the finding, its quote, its governing framework item and the
   unit's text, and not the reasoning that produced it. A refuted or unresolved
   verdict turns the finding to unresolved and keeps the objection. Record in
   the register that this was a second pass by the same reader, and do not
   describe it as independent review.

9. **Gate 3 and delivery.** Reconcile in the register, not in a sentence: the
   `Counts` sheet holds units, issues, expected rows, filled rows and parked
   rows as live formulas, and the difference must be zero or explained by
   visible parked rows. If it does not come right, fix the run, never the
   numbers. State the read-in and written-out row counts in the reply. Then
   build the crosswalk page: an Issues view answering where each issue was
   found, an Agreements view reversing the same rows, a Scope and gaps view
   accounting for instruction inputs, substantive sources, families, parked
   items, unreadable items and missing materials, and an Audit view carrying
   the framework version, the fingerprints and the tranche boundaries. Say on
   the page which tranche it covers and what is outside it. The lawyer rules on
   everything marked **Needs a decision** and decides what to do with the
   factual output. Do not add recommendations, risk rankings, or any claim that
   the surface is legal advice unless separately instructed.
