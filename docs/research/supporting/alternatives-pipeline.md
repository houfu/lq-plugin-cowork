# Cowork-native alternatives and risk: document-pipeline skills

19 September 2026

Eight skills that were excluded from the Cowork bundles for depending on local Python, external
binaries, a private filesystem or a network fetch: read-redline, sigpack, closing-bible,
definition-check, conform, diligence, docreview, regulatory. This document designs the nearest
thing Cowork can do for each one, says what every step rests on, rates the risk it will not work,
names what the lawyer loses and names the probe that would settle the doubt. No skill is
recommended out.

Evidence letters on every substitute: **D** documented, **U** undocumented but not denied,
**C** contested or unspecified, **X** documented absent or forbidden by the skill's own text.
Capability risk is the worst letter on a load-bearing step: Low is all D, Medium has a U, High has
a C or an X. Quotes are verbatim from `docs/research/supporting/excluded-skills-profiles-pipeline.md`
and carry that document's Q numbers.

Probes P1 to P7 are as defined in `docs/research/excluded-skills-rebucket.md`. This document adds
three:

- **P8 — can Cowork build a PDF out of chosen pages of supplied PDFs?** Attach two synthetic
  four-page PDFs. Prompt: `Make me one new PDF containing page 3 of the first document and pages 1 and 2 of the second, in that order, and tell me how many pages it has.`
  Pass signal: a downloadable PDF in the Output folder with exactly those three pages in that order
  and their content intact. A reply that describes the pages instead of producing the file is a
  fail. Unlocks: sigpack's pack and compile halves, closing-bible's combined PDF.
- **P9 — does an Excel workbook survive a round trip?** Session 1: `Build me a tracker workbook with columns Document, Issue, Status, Quote, Locator and these six rows, and add a row at the bottom that counts how many rows are filled.`
  Then attach the returned workbook in a fresh session: `Add these four documents as new rows, fill the Status column for them, and give the workbook back to me unchanged apart from the new rows.`
  Pass signal: the returned file keeps the original six rows, the column order, the count formula and
  its recalculated value. Unlocks: the register pattern that carries state and coverage arithmetic
  for diligence, docreview, closing-bible and definition-check.
- **P10 — can Cowork produce a Word document carrying real tracked changes?** Prompt with a short
  supplied agreement: `Give me back this clause as a Word document with my three edits recorded as tracked changes attributed to "Review", not as plain edited text.`
  Pass signal: opening the file in Word shows insertions and deletions in the review pane. Unlocks:
  read-redline's annotated Word copy and the conform alternative's redline.

Whether a scheduled Cowork run can take placed files and write outputs is being read separately;
every step below that leans on it is marked U and no design depends on it.

---

## 1. read-redline

### 1. The alternative, step by step

A redline reviewer whose primary path is the Word path and whose PDF path degrades in the open. The
lawyer attaches the redline; the skill reads the changes, rates them, groups them into themes and
delivers an issues list and a themed reading, with an HTML marked-passage view in the preview pane
in place of the annotated PDF.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Inspect the file; `pdfinfo` for page count, producer, title; find the compare-tool summary page | Model reads the attached file; page count and the summary page's printed totals read as text | D (text and totals); U (PDF producer metadata) |
| 2 | Calibrate what the marks mean, always, before extracting | The skill states what it can see — strikethrough, underline, coloured text, balloons — and asks the lawyer to confirm in one line before it reads anything | D |
| 2b | Record the gate as `calibration.confirmed.json` beside `extract.json` | A `redline-calibration.md` block written into the Output folder manifest, plus the confirmation line in the conversation; the "refuse to build without it" rule becomes a rule the skill applies to itself | write D; enforcement D but self-applied |
| 3 | Extract changed pairs (Word path: tracked insertions and deletions with authors) | Host-native reading of tracked changes in DOCX | **U, probe P3** |
| 4 | Render every changed page at 110 dpi and look; quarantine every mark with no pair | Model reads the pages, including markup and scans (PDF path only; the Word path says "There are no pages to render") | **U, probe P4** — PDF path only |
| 5 | Reconcile the pair count against the summary-page totals | The skill states both numbers and explains the gap in one sentence; the numbers go in the receipt | D, self-counted |
| 6 | Rate and write rows against `significance_rubric.md` | Same, unchanged — legal judgment on text the model has read | D |
| 7 | Group rows into themes in two passes | Same, unchanged | D |
| 8 | Annotate the same PDF and re-open it to check the page count survived | Not attempted. In its place: an HTML marked-passage view for the preview pane showing each pair old-beside-new with its theme and tier, and, on request, a Word issues list through the built-in Word skill | HTML D; Word output D; **annotating a supplied PDF X in practice** |
| 8b | Word path only: annotated copy on request | A new Word document with the changes recorded as tracked changes | **U, probe P10**; the plain-text fallback is D |
| 9 | Present themes, the receipt line, two artifacts | Chat summary plus the HTML view plus the issues list, all named by filename in the Output folder | D |
| — | Keep intermediates under `tmp/redline/` and delete them after step 9 | Named files in the Output folder, disclosed, never deleted | D |

### 2. Capability risk

**Medium.** The worst letter on a load-bearing step is U: P3 for the Word path, P4 for the PDF path.
Nothing here is C or X except the annotated PDF, which is not load-bearing because the skill's own
text already treats it as a losable artifact.

### 3. Fidelity

**Same deliverable with a disclosed weaker guarantee.** The issues list and the themed reading are
the same. Three guarantees weaken: the visual-reconciliation completeness receipt if P4 fails, the
annotated PDF, and the calibration gate as an enforced artifact. All three are degradations the
skill's own text already tells it to disclose rather than refuse over: "If the host cannot render
pages, say plainly that visual reconciliation did not run and the completeness receipt is
unavailable. If it cannot write PDF annotations, deliver the grounded issues list and state that the
annotated-PDF artifact could not be produced; do not silently claim the normal output contract was
completed" (read-redline Q6).

### 4. Failure modes

- **Step 3 (U, P3): Silent, and the worst in this set.** If Cowork reads a DOCX as though the
  tracked changes had been accepted, the skill reports no changes — which is indistinguishable from
  the legitimate stop the skill already has: "If the report says **no tracked changes found**, stop:
  the changes were accepted before saving or the file is a clean draft, and there is nothing to
  review" (Q10). Mitigation that turns it loud: the skill may not say "no tracked changes found"
  unless it first quotes one inserted string and one deleted string with its author from somewhere
  in the file, or states in terms that it could not determine whether the file carries tracked
  changes and asks the lawyer to confirm in Word. A nil return must name which of the two it is.
- **Step 4 (U, P4): Loud.** The skill either reports what is on a page or says it could not, and Q6
  already prescribes the sentence.
- **Step 8b (U, P10): Loud.** Either the returned document opens with tracked changes or it does
  not, and the lawyer sees that immediately.
- **Step 2b (self-applied gate): Silent.** A calibration that was never confirmed can still produce
  a confident report. Mitigation: the calibration line and the lawyer's confirmation are reproduced
  verbatim at the head of the deliverable, so an unconfirmed run is visible on the artifact.

### 5. Tier

**Tier 2.** Ship after P3 passes; or ship now with the announced degrade — a banner saying the skill
could not confirm it can see tracked changes and that a nil result must be checked in Word. P4
decides whether the PDF path travels with it.

### 6. Probes

P3 decides it. P4 decides whether the PDF path comes. P10 decides whether the annotated Word copy
survives as marks or only as description.

### 7. Effort and companions

`exclude: scripts/**` removes 7 files, leaving **1 companion** (`references/significance_rubric.md`,
2.4 KB) against a cap of 20. Layers: a `replace` on the two Output-conventions sentences (Q1, Q2);
section overlays on "Capability fallback" (host-native becomes the only path), on workflow step 4
(rendering becomes reading), on step 8 (annotation becomes the HTML view), on "The Word path" step 5,
and on "Final checks" (Q11's re-open-and-verify becomes a self-check, the way cite-check's colour
rule was restated). Moderate: comparable to playbook-review, lighter than cite-check.

### 8. Bundle and routing

Transactional, which carries 8 skills today against a cap of 20. The collision is playbook-review,
whose trigger list already includes "re-review the revised draft they sent back" and whose
description disclaims a tracked-changes redline. Both descriptions need a hand-off line: read-redline
reads a redline against its own previous version with no playbook in the room; playbook-review
measures a draft against approved positions.

### 9. The honest counter

The skill's text forbids nothing here. It is the only one of the eight with no forbidden fallback:
"If the scripts cannot run, use host-native PDF reading, rendering, and annotation capabilities to
preserve the same calibration, extraction, visual reconciliation, quarantine, rating, and coverage
rules" (Q5). Two things bend. Q1 says keep the intermediates "under `tmp/redline/` and delete them
after step 9" — Cowork cannot delete, so the alternative keeps them in the Output folder and names
them, which serves the intent (nothing hidden) while breaking the letter. Q7 and Q8 make the
calibration an enforced artifact — "A confirmed calibration is an artifact, not a memory" — and the
alternative can only make it a self-applied rule, which must be said in the body rather than glossed.
No changed promise is needed.

### 10. What the lawyer actually gets

They attach the redline the other side sent back and say "tell me what moved". A minute later they
get a short read: three or four themes with a line each on what the other side is doing, then the
housekeeping line, then the individual points that did not cluster. There is an issues list they can
send to the client or the partner, and a page in the preview pane showing each change old-beside-new
with a materiality tier. What they do not get is their own PDF handed back with marks on it, and if
the skill could not see inside the file properly it says so at the top rather than telling them there
was nothing to review.

---

## 2. sigpack

Two alternatives at different tiers. Build the first.

### 2A. A re-scoped drafting and chasing skill (recommended first)

#### 1. The alternative, step by step

Name it `signature-pages`. Its promise is the half of sigpack that is document reading and drafting:
work out who signs what and how, draft the pages, write the instructions and the cover note, and
keep the chase list. It never compiles an executed set.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Extract the signing matrix from each execution version's parties clause and execution language | Model reads the attached execution versions and proposes capacity chain, signatory, required marks, copies | D |
| 2 | Gate: show the lawyer the matrix table and confirm before drafting | Same, in the conversation | D |
| 3 | Load the firm's template and draft the pages | The lawyer attaches their own template DOCX; the pages are produced through the built-in Word skill | D |
| 4 | Open the ledger and settle the build options | An Excel or Markdown ledger the lawyer attaches at the start of each session and gets back updated in the Output folder | D bring-your-own; read-back without attaching U, probe P2; Excel round trip U, probe P9 |
| 5 | Build the packs as PDFs | Not attempted. The pages go out as documents per party, named per the lawyer's pattern | changed promise |
| 6 | Instructions table and cover note, including the escrow line | Same, unchanged | D |
| 7 | Present the headline, the instructions, the cover note, the receipt line | Same, minus the executed-set counts | D |
| — | Chasers: per-party facts for the lawyer to send themselves | Same, unchanged; the skill never sends | D |

#### 2. Capability risk

**Low.** Every load-bearing step is D. The ledger is carried by the lawyer, so nothing rests on P2.

#### 3. Fidelity

**Different deliverable.** It is the planning, drafting and chasing half. There is no scan-and-classify
pass, no page-by-page verdict, no compile, no executed PDF and no completeness receipt.

#### 4. Failure modes

Step 4 is the only U and it is Loud: either the lawyer's ledger comes back with the new batch in it or
it does not, and they can see the file. The silent risk is a matrix that misreads an execution block
— mitigated by the gate at step 2, which is upstream's own: "**Gate: show the lawyer the matrix table
and confirm before drafting**" (sigpack Q9).

#### 5. Tier

**Tier 3** — a re-scoped skill with a changed promise and a changed name. Worth having: the signing
matrix, the drafted pages, the instructions table and the cover note are real work, and the shipped
closing-checklist description already reserves the ground with "Do not use ... for assembling
signature pages", so the hand-off only needs its direction filled in.

#### 6. Probes

None gate it. P9 would make the Excel ledger cleaner; P2 would let the ledger stop travelling by hand.

#### 7. Effort and companions

After the global strip and `scripts/**`: **2 companions** (`ledger_schema.md`,
`signature_page_rules.md`, 22.7 KB), and `signature_page_rules.md` gets shorter because the
classification rules it exists for are out of scope. Layers: a full-file overlay is likely, because
the three-mode structure and the `/sigpack [mode] [flags]` grammar (Q16) both have to go; the card
must also drop the `argument-hint` frontmatter, which the build already strips.

#### 8. Bundle and routing

Transactional. No contest to invent; closing-checklist points here already.

#### 9. The honest counter

The skill's text is emphatic that the half being dropped is the half that matters: "A user who wants
'just merge them' is asking for a different, less safe tool; say so once, then do it properly" (Q8).
The re-scope respects that by refusing to be the less safe tool — it does not merge at all, and it
says so in the description rather than offering a degraded compile. "Compile refuses to run while any
page is `unknown`. Never guess" (Q10) is honoured by never compiling.

#### 10. What the lawyer actually gets

They drop the execution versions in and get a table: for each document, who signs, in what capacity,
how many originals, and whether a witness is needed. They confirm it, and they get drafted signature
pages on their own template, a per-party instruction table, and a cover note with the escrow wording.
When pages come back, the skill helps them keep the ledger straight and drafts the chaser facts. It
never tells them the set is complete, because it cannot look at the returned pages.

### 2B. Full sigpack (deferred)

#### 1. Step deltas

Everything above plus: scan for candidates across the folder (D for text, **U P4** for deciding from
the look of a page whether it is a real signature page or an exhibit's form page); read every
candidate page and every returned page and record a verdict (**U, P4**); convert Word inputs to PDF
(**U**); build pack PDFs from chosen pages and insert returned pages into the execution versions
(**U, probe P8**); render and look before delivering (**U, P4**).

#### 2 to 4. Risk, fidelity, failure

Capability risk **Medium** by the letter of the rubric — four stacked U steps, no C or X — but four
stacked Us is not the same bet as one. Fidelity: **Core promise not deliverable** if P4 fails,
because the skill says so itself: "Without a way to render every candidate and returned page, say
plainly that the visual-review gate cannot run and do not compile an executed set" (Q7). The failure
mode on P4 is Silent in the way that matters: a model that believes it has looked at a scanned
signature page and has not will report a signed block that is blank. The mitigation is upstream's own
and it is a refusal, not a label.

#### 5 to 6. Tier and probes

**Tier 2**, conditional on P4 *and* P8 both passing, plus P2 or P9 for the ledger. Three probes for
one skill is the signal to build 2A first.

#### 9. The honest counter

Q12 — "If `soffice` is missing the command stops and says so; ask for PDFs rather than proceeding as
if converted" — is directly satisfiable: the alternative asks for PDFs. Q10's refusal on any
`unknown` page is what P4 decides.

---

## 3. closing-bible

### 1. The alternative, step by step

Name it `closing-index`. Its promise is the index and the exceptions list, and it says on every
delivery that it is a reading of the folder, not a balanced receipt.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Take the census: every file, page counts, text, hashes | Model lists every attached file with apparent title, parties, date and whether it looks executed; page counts from reading | D for the list; **X for hashes** |
| 2 | Group into families | Same, unchanged — this is reading and judgment | D |
| 3 | Show the family table and confirm the grouping before going on | Same, in the conversation | D |
| 4 | Inspect each family and write `inspection.json`: which member is final, what state it is in | Model reads the execution pages; a scanned execution page needs page inspection | D for text-layer documents; **U, probe P4** for scans |
| 5 | Reconcile against the checklist and balance the receipt | An Excel status register: one row per expected item, with status, selected source, qualification, and a counted total row whose arithmetic the lawyer can see. Labelled "a reading, not a certified receipt" | produce D; update in place **U, probe P9**; **the balanced receipt X** |
| 6 | Present Gate 1: index, census summary, missing and unexpected, version conflicts | Same, as chat plus a Markdown or HTML index in the preview pane plus a Word index on request | D |
| — | Build: combined PDF with bookmarks and volumes | Not attempted | **U at best, probe P8; bookmarks undocumented** |
| — | Outputs beside the closing folder, never inside it | The Output folder, named and disclosed, never deleted | D |

### 2. Capability risk

**High.** The receipt is an X: there is no hashing, and more decisively the skill forbids a receipt
produced any other way.

### 3. Fidelity

**Core promise not deliverable.** The skill's own words: "The script is the only thing that validates
inspection records and balances the receipt. If it cannot run (no Python 3.12 or newer), stop: tell
the lawyer the audit cannot be completed here and why, and produce no index, receipt or exceptions
list by hand. A receipt written without the script is not a receipt" (closing-bible Q7, repeated at
Q14). That sentence forbids the index and the exceptions list too, not only the receipt. So the
alternative cannot be an adaptation of closing-bible. It has to be a different skill with a different
name and a promise that never uses the word receipt.

### 4. Failure modes

- Step 4 (U, P4): **Loud** — the upstream taxonomy already has `not-inspected` with a reason, and Q5
  prescribes carrying it through as not ready.
- Step 5 (the count): **Silent** in the model, **Loud in the workbook**. This is the design move for
  this skill. A model that says "all 43 items are accounted for" cannot be checked; an Excel register
  with 43 rows, a status column and a visible count formula can be checked in ten seconds. The
  workbook is the substitute for the receipt, and its honesty comes from being inspectable rather
  than from being computed correctly.
- Step 1 (no hashes): **Loud** — the skill says it does not fingerprint files and cannot tell the
  lawyer that a source has not changed since the census.

### 5. Tier

**Tier 3.** A re-scoped skill with a changed promise, and it is worth shipping: building the index
and the exceptions list from two hundred closing documents is the bulk of the labour, and the lawyer
signs the completeness question off themselves — which, on a closing, they do anyway. A **Tier 4**
variant exists: a connector the firm operates that reads the closing folder, hashes it and balances
the receipt would restore the promise in full, but it means running a server against a live deal
folder.

### 6. Probes

P4 for scanned execution pages, P9 for the register, P8 if anyone wants the combined PDF back. P1
would reopen the original skill, and only if it showed a named interpreter of version 3.12 or newer,
which no Microsoft page comes close to naming today.

### 7. Effort and companions

23 files today; after the global strip and `scripts/**`, 12 companions of which 9 are schema
contracts only the script reads. Dropping those leaves 3, and the re-scope drops two more
(`assembly-rules.md` is about the combined PDF, `sigpack-ledger-consumption.md` consumes a ledger
from a skill that does not ship): **1 companion** (`status-taxonomy.md`), plus a new register-format
reference. The effort is a full-file overlay — the body is organised around a script and two approval
gates that guard script outputs.

### 8. Bundle and routing

Transactional. The shipped closing-checklist description currently says "Do not use ... for auditing
the signed closing folder", which reserves the ground and must be rewritten into a named hand-off to
whatever this skill is called. Closing-bible's own routing sentences hand signature-page work to
sigpack (Q16) and pre-signing rooms to diligence (Q17); if signature-pages ships the first survives
as a hand-off, and the second becomes a scope statement.

### 9. The honest counter

Q7 and Q14 are the sharpest forbidden-fallback sentences in the whole set, and they do not only
forbid a hand-built receipt — they tell the skill to stop and produce nothing. Any Cowork closing
work therefore has to be a new skill, not an adaptation, and it must never present its status table
as a receipt. Q8 — "The receipt is written only when it balances; if the counts do not reconcile the
script stops and says so, and that is the finding, not a bug to work around" — is the guarantee being
given up, and the Excel register is offered as a visible substitute, not an equivalent. Q12's
boundary survives untouched: the skill still "never decides that completion has occurred, never
certifies due execution, authority, delivery or enforceability, and never changes a source file".

### 10. What the lawyer actually gets

They point the skill at the closing folder and get back a proposed index in their own order, a list
of the files that group into one document under three names, a list of what the checklist expects and
the folder does not contain, and a list of families where two candidates both look final. It comes as
a workbook they can sort and a page they can read. What they do not get is the sentence that says the
set is complete, and they do not get the combined bible PDF. The skill says both of those things in
its first reply, not its last.

---

## 4. definition-check

### 1. The alternative, step by step

The skill's own degraded mode, made the only mode, with the coverage claim replaced by a visible
count the lawyer can spot-check.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | State the boundary and inspect the tool inventory before running | An opening line saying what this run can and cannot establish; no capability probing | D |
| 2 | Deterministic DOCX path: parse the OOXML, enumerate defined terms and every mention | Model reads the document body and enumerates the terms | D for reading; **the exhaustiveness guarantee X** |
| 2b | — | New step: enumerate the document's own units first — clauses, schedules, annexes — state the count, then work through them one at a time, the way cite-check's adaptation works through prepared units | D |
| 3 | Full-capability agentic path: fan out packets to workers | Sequential passes in one session, execution shape recorded | D |
| 4 | `mention-coverage.json` audit that independently rescans accepted labels | An Excel definitions register: one row per term, with clause of definition, definition text, count of mentions found, the locators, and a disposition. Plus the unit list from step 2b, so the lawyer can compare it against the contract's own numbering | produce D; update in place **U, probe P9** |
| 5 | Review path: confirm candidates before displaying them as defined terms | Same, unchanged | D |
| 6 | Outputs: `definition-check.html` generated only after term and occurrence review are complete | The same HTML artifact in the preview pane, carrying a mandatory line saying the coverage is a self-declared count, not a parse | D |
| 7 | Term normalization for downstream consumers (`/conform`) | Kept as a section the conform alternative reads, not as a script run across folders | D |
| — | Workspace, `--work-dir`/`--output-dir` disjoint, fail-closed cleanup | The Output folder, named, disclosed, never deleted | D |

### 2. Capability risk

**Medium.** Reading the body is D throughout. The register's in-place update is the only U, and the
lawyer can carry the file instead. The X sits on the guarantee, not on a step, which is why this is
a fidelity problem rather than a capability problem.

### 3. Fidelity

**Same deliverable with a disclosed weaker guarantee.** The artifact is the same HTML review. What
weakens is the audit behind it: "a missing accepted-label usage or a non-label mention marked as a
definition blocks completed HTML" (definition-check Q10) cannot fire for a usage the model did not
notice, so the block is gone. The skill's own text provides for exactly this mode — "Analyze only
content actually exposed by the host. Request pasted/exported text if the DOCX body is inaccessible.
Never claim deterministic parity" (Q6) — so the alternative is a mode the skill already names, not a
fallback it forbids.

### 4. Failure modes

- Step 2 (missed occurrence): **Silent**, and it is the characteristic failure of this whole skill.
  Three mitigations, all needed. First, the unit list: the skill states how many clauses it read and
  which, and the lawyer can compare that against the contract's table of contents in seconds. Second,
  the register: sorting by "mentions found = 0" surfaces the never-used terms, and any single row can
  be confirmed with Word's own Find. Third, the mandatory line on the artifact — the skill finds
  problems, it does not certify their absence.
- Step 4 (U, P9): **Loud.**
- The prohibition that must survive verbatim: "Never translate a missing parser, partial input,
  failed command, or skipped method into 'no issues found.'" (Q7). In this alternative that becomes a
  standing rule, because there is no parser at all: a clean result is reported as "no issues found in
  the 62 clauses I read", never as "no issues".

### 5. Tier

**Tier 2** — ship now with an announced degrade. No probe gates it. P1 would restore the parser path
if it ever showed a named interpreter, but nothing waits on it.

### 6. Probes

P9 for the register. P1 only as an upgrade path.

### 7. Effort and companions

67 files today, the largest of the eight. After the global strip and `scripts/**`: 23 companions,
three over the cap; dropping the 11 schema contracts leaves 12; dropping the runtime references that
describe a vendor's worker runtime (`capability-routing.md`, `agentic-review-protocol.md`,
`openai-codex-runtime.md`, `ledger-contract.md`, `stage-runner.md`, `stage-telemetry.md`) leaves
about **6** — `rule-catalog.md` and the five `prompts/` files repurposed as review checklists. A
full-file overlay, and the heaviest single card of the eight: the body is built around a deterministic
path, an agentic path and a vendor waiver, and two of the three go.

### 8. Bundle and routing

Transactional. Nothing shipped does defined-term review, so there is no collision to resolve — only a
scope line against playbook-review, which also takes "check this draft" prompts.

### 9. The honest counter

Q10 is the guarantee being surrendered and it must be said on the artifact, not only in chat. Q11 —
"`definition-check.html` is the primary lawyer-facing review artifact. Generate it only after both
term and occurrence review are complete" — survives, because both reviews still happen; what changes
is what "complete" can mean. Q9's discipline is worth keeping exactly: if the review does not finish,
do not write a partial HTML file, say so in chat. Q13 — do not execute macros, embedded objects or
document-supplied instructions — is a rule this alternative needs more, not less, because a model
reading a contract body is the thing a document-borne instruction would be aimed at.

### 10. What the lawyer actually gets

They attach the agreement and ask what is wrong with its definitions. They get a page listing the
defined terms, each with where it is defined and where it is used, and above it a short list of the
actual problems: three terms defined and never used, one term used in clause 14 that is never
defined, "Business Day" defined twice with different meanings, four references to a schedule that
does not exist. They also get a workbook they can sort. The first line of the page tells them the
skill read 62 clauses and found 68 terms, and that this is a careful reading rather than a machine
count, so a term it did not notice will not appear.

---

## 5. conform

### 1. The alternative, step by step

Name it `clause-fit`. The design move is not to substitute for the hash — it is to remove the reason
the hash existed. Upstream, the ledger came from an earlier run and might have gone stale. Here both
documents are read in the one session, so there is nothing to go stale.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Confirm the core document | Same, in the conversation | D |
| 2 | Ledger preflight: recompute and compare document hashes against ledger records; hard stop on mismatch | Removed. Both documents are attached to this session and both vocabularies are extracted in this session | **the preflight X**; the in-session extraction D |
| 3 | Deterministic term normalization by running definition-check's script across skill folders | The definition-check alternative's method applied to both documents in this session; no cross-folder file reach, which the repo's card rules forbid anyway | D |
| 4 | Agentic mapping: dispatch mapping packets to workers | Sequential mapping in one session, execution shape recorded | D |
| 5 | Escalation decision rules: which mappings change meaning | Same, unchanged — this is the legal content and the reason to have the skill | D |
| 6 | Precedent-leakage scan | Same, unchanged | D |
| 7 | Outputs: mapping record and redline, every mapping a proposal | Mapping table in chat plus a Word document carrying the proposed clause; tracked changes in that document if P10 passes, otherwise old-beside-new | D for the document; **U, probe P10** for tracked changes |
| — | Temporary marked run workspace, disjoint from the output directory | The Output folder, named, disclosed | D |

### 2. Capability risk

**Low** for the re-scoped skill. Every load-bearing step is D; the only U is cosmetic, on how the
redline is presented. Note that the *unchanged* skill is High — the preflight is an X, since Cowork
has no hashing and the ledger cannot exist.

### 3. Fidelity

**Different deliverable.** The mapping, the escalations and the proposed clause are the same. What
goes is the two-run structure: no ledger, no freshness guarantee carried from an earlier session, no
hash identity between the document reviewed and the document conformed, and the unit of work is a
clause or a section rather than two fully ledgered documents.

### 4. Failure modes

- Step 2 removed: **Loud by construction.** The skill cannot claim a freshness guarantee it no longer
  offers; the description says both documents are read here and now.
- Step 3 (vocabulary extraction): **Silent**, inherited from the definition-check alternative — a
  defined term the model did not notice is a mapping that never gets proposed. Mitigation: the
  mapping table lists every term it mapped and every term it found no equivalent for, so the lawyer
  sees the universe it worked from; and the proposed clause is a proposal they read anyway.
- Step 7 (U, P10): **Loud.**

### 5. Tier

**Tier 3.** Re-scoped, changed name, changed promise. Worth having: "take this indemnity from the
precedent and make it fit our agreement's defined terms" is a daily transactional ask, and the
escalation rubric — which substitutions change meaning and which do not — is the valuable part and
survives whole.

### 6. Probes

None gate it. P10 improves the redline.

### 7. Effort and companions

24 files today; after the global strip and `scripts/**`, 10 companions; dropping the 3 schemas and the
two routing and protocol references leaves about **4** (the escalation rules, the mapping and
leakage-scan prompts rewritten as checklists). A full-file overlay, and the card must delete the
literal cross-folder path `../../definition-check/references/capability-routing.md`, which the repo's
card rules already forbid ("Cards must not reference ... files outside the skill folder").

### 8. Bundle and routing

Transactional. It needs a hand-off line against playbook-review, since "conform this precedent clause
into our vocabulary" and "review this draft against our playbook" are adjacent asks with very
different outputs.

### 9. The honest counter

Three sentences forbid the adaptation as written and none forbids the re-scope. "`/conform` never runs
against a missing, stale, mismatched, or incomplete `/definition-check` ledger" (conform Q3) —
the alternative has no ledger, which is "missing", so this must go and the changed promise must say
why. "Cannot run the packaged preflight or mapping engine. Stop; do not attempt a Python-free
reimplementation of hash comparison or ledger validation" (Q6) — respected: the alternative does not
reimplement hash comparison, it removes the two-run structure that needed it. "A hard stop is normal,
expected behavior, not a bug to work around" (Q10) — the hard stop is retired along with the thing it
guarded, which is a changed promise and not a worked-around stop. Two boundaries survive intact and
should be quoted in the new body: "'Safe to propose' never means silent application. Every mapping —
escalated or not — is a proposal in the redline and mapping record for the lawyer to accept, edit, or
reject" (Q11), and "No silent document modification" (Q14), which Cowork enforces anyway by writing a
new file.

### 10. What the lawyer actually gets

They attach their agreement and the precedent, point at a clause, and say "make this fit". They get a
table: the precedent says "Permitted Encumbrances", we say "Permitted Liens", same meaning, mapped;
the precedent's "Material Adverse Effect" carries a carve-out ours does not, escalated, here is why
it matters; the precedent refers to a schedule we have no equivalent of, flagged. Then the rewritten
clause as a Word document, as a proposal. What they do not get is any assurance that the definitions
in either document were checked in a prior run — the skill reads both in front of them, every time.

---

## 6. diligence

### 1. The alternative, step by step

The skill's own portable fallback made the only path, with the coverage certification retired
permanently and the master register carrying the state the run directory used to hold.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Inventory and review copies; hash-bound sidecar; stable file identity | The register records an identity fingerprint per document — filename, page count, document date, the first line of page one — re-read and compared at the start of every session. Sources stay untouched in the Input folder, which Cowork cannot modify or delete | fingerprint D; **hash-bound review copies X** |
| 2 | Metadata pass: one fresh worker per document, every field carrying a verbatim quote | Sequential passes, one document at a time, same schema, same quote rule, execution shape recorded | D |
| 3 | Relationships and families | Same, unchanged | D |
| 4 | Compile the lawyer's checklist into a framework and read it back | Same, as a Markdown framework and a read-back table | D |
| 5 | Gate 1: confirm the review setup on five representative documents | Same, in the conversation | D |
| 6 | Gate 2: review the test results before scaling | Same | D |
| 7 | Scale: the full or targeted plan | Tranches of documents per session, each tranche's rows appended to the register, which the lawyer attaches at the start of the next session | bring-your-own D; read-back without attaching **U, probe P2**; workbook round trip **U, probe P9**; scheduled batches **U** |
| 8 | Verify: quote check, then an independent checker without the maker's reasoning | The model re-locates every quote in the source and records the locator; a second pass sees only the finding, the quote and the framework item. The skill records that this is a second pass, not an independent reviewer | D, with the disclosure Q7's analogue already requires |
| 9 | Gate 3: reconcile the complete issue × substantive-unit cross-product, then render the crosswalk | The register is the reconciliation: rows are documents × issues, a visible count row says how many are filled and how many are parked, and the arithmetic is formulas the lawyer can see. The crosswalk renders as HTML for the preview pane | reconciliation as visible arithmetic D; **the certification X** |
| — | Delete the temp master dataset at completion | The register and the artifacts stay in the Output folder, named; nothing is deleted | D |
| — | Scanned or image-only documents | Parked as unreadable and listed, which the upstream taxonomy already provides for | **U, probe P4**, failing loud |

### 2. Capability risk

**Medium.** P4 on scanned documents and P9 on the workbook; the state question is answered by the
lawyer carrying the register, which is D.

### 3. Fidelity

**Same deliverable with a disclosed weaker guarantee.** The crosswalk, the quote-anchored findings,
the parked queue and the scope-and-gaps account are the same artifacts. The guarantee that goes is
the certification, and the skill's own shared fallback text sets exactly this ceiling: "If stable file
identity and complete count reconciliation cannot be established, the run may deliver a clearly
labeled review and unresolved queue, but it may not call the result coverage-certified" (diligence
Q10). Note that it *permits* the labelled review — this is a ceilinged mode, not a forbidden one.

### 4. Failure modes

- Step 1 (no hashes): **Loud** — the fingerprint either matches on re-read or it does not, and a
  swapped document is reported.
- Step 7 (state across sessions): **Loud** — no register attached, no continuation; the skill says
  which tranches are recorded and which are not.
- Step 9 (the count): **Silent in the model, Loud in the workbook.** Same move as closing-bible: the
  arithmetic has to be somewhere the lawyer can see it. A model that says "every document was
  reviewed against every issue" is not checkable; 24 rows by 13 columns with 312 filled cells and a
  count formula is.
- Step 8 (second pass called independent): **Silent** unless disclosed. The mitigation is upstream's
  own wording for the sequential case, applied here as a standing sentence: record the execution
  shape and do not claim independent review.
- Step 4 and the framework: "The framework is the only instruction channel to workers. If a
  calibration is not a framework field, it does not exist" (Q16) survives and should, because a
  single-session model is more prone to absorbing an instruction from a document than a script is.

### 5. Tier

**Tier 2** — ship now with an announced degrade: no coverage certification ever, scanned documents
parked as unreadable, and the tranche boundary stated on every delivery. P4 would remove the second
of those.

### 6. Probes

P4 for scans, P9 for the register, P2 only if anyone wants the register to stop travelling by hand.

### 7. Effort and companions

72 files today. After the global strip and `scripts/**`: 22 companions, two over the cap; dropping the
8 schema contracts leaves 14; dropping the runtime references (`openai-codex-runtime.md`,
`review-ui.md`, and the parts of `references/shared/` that are script contracts) brings it to about
**8**. The heaviest surgery of the eight after definition-check, and the shared tree is dense with
words the build flags — run directory, parallel workers, exit code, sidecar — so `execution-modes.md`
needs rewriting rather than patching. It is also shared byte-for-byte with docreview, so the rewrite
is done once and used twice, which is the argument for treating these two as one piece of work.

### 8. Bundle and routing

Transactional, which has room. The two "out of scope" clauses that currently reserve this ground —
organize-case-docs' "document-by-document responsiveness and privilege review, which is out of scope"
and document-discovery's "reviewing an incoming production document by document, which is out of
scope" — sit in the litigation bundle. Because a skill may hand off by name only to skills present in
every bundle it ships in, a transactional diligence cannot name them; those two need a scope statement
rather than a hand-off, and diligence needs one against playbook-review.

### 9. The honest counter

"Continue inside the same skill. Do not replace the workflow with an informal whole-room review" (Q8)
is the sentence the alternative most has to honour, and the tranche design is how: the method stays,
the assurance drops, and nothing becomes "read the room and tell me what you think". "The fallback is
method-compatible, not assurance-equivalent. State exactly which checks were unavailable" (Q9) is the
required disclosure and belongs on the artifact. "A claim without a verified verbatim quote does not
enter any artifact" (Q11) survives in form — every row carries its quote and locator — and weakens in
verification, because the check is self-performed. "Never transmit anything anywhere" (Q5) is
satisfied: a skills-only package has no network channel of its own.

### 10. What the lawyer actually gets

They give the skill their issues list and the first tranche of the data room. They approve the
framework, look at five sample documents' findings and say what is wrong with them, and then the
skill works through the tranche, one document at a time, filling a workbook: document, issue, finding,
the verbatim words it relies on, where they are. Next session they attach the workbook and the next
tranche. At the end they have a crosswalk they can read and a workbook they can sort, with a visible
count of what was covered and a visible list of what was parked. What they never get is the sentence
saying the review is coverage-certified, and the skill says so at the start, not at the end.

---

## 7. docreview

### 1. The alternative, step by step

The same design as diligence, over a litigation production, with one addition that carries all the
weight.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Inventory the production and build review copies | As diligence step 1; sensitivity-labelled or encrypted files cannot be read and are listed | fingerprint D; **labelled files X, failing loud** |
| 2 | Map the production and plan reads | Same, unchanged | D |
| 3 | Compile and read back the review questions | Same | D |
| 4 | Plain-language setup approval | Same | D |
| 5 | Run and merge the test sample | Sequential, one unit at a time | D |
| 6 | Obtain lawyer privilege rulings; only `not-privileged` releases a unit | The register's first column is the privilege state. The skill re-reads it at the start of every session and states the held count before doing anything else. **No register attached, no findings output at all.** No quoted text from a held unit is written into any artifact, or into the register itself | D, but self-applied |
| 7 | Verify findings independently | Second pass, disclosed as a second pass | D |
| 8 | Review findings in a page that works from `file://` and loads no remote resource | An HTML page in the preview pane with the findings inline, no local file protocol and no remote resource | D |
| 9 | Scale only after calibration | Tranches, as diligence | bring-your-own D; **U** for anything leaning on a scheduled run |
| 10 | Reconcile and deliver; delivery requires a clean reconciliation | The register's visible arithmetic, with the certification retired | **the certification X** |

### 2. Capability risk

**Medium** on the letters — the same Us as diligence, plus an X on labelled files that fails loudly.
The risk that matters here is not capability, it is the privilege mechanism.

### 3. Fidelity

**Same deliverable with a disclosed weaker guarantee**, with one caveat that should be put to the
maintainer rather than buried. The crosswalk and the findings are the same. The certification goes,
as with diligence. But the privilege hold goes from an enforced record — "Only `not-privileged`
releases a unit. Pending, `privileged`, and `needs-review` records remain held across every lens"
(docreview Q7) — to a rule a model applies to itself with the production in its context. That is the
one guarantee in these eight skills where "weaker" may simply be unacceptable, and the honest thing is
to say so and let a litigator decide.

### 4. Failure modes

- Step 6 (privilege): **Silent, and the most costly silent failure in the set** — a privileged
  document's words in a deliverable look exactly like a correct finding. Four mitigations, and the
  design needs all four. The privilege state is the first column of the register. The skill states
  the held count and lists the held ids before it produces anything. It writes no quoted text from a
  held unit anywhere, including into the register, so even the state file cannot leak. And if the
  register is not attached it refuses to produce findings at all, which converts the state dependency
  from a silent omission into a loud hard stop. Even with all four, this is a rule and not a lock.
- Step 10 (the count): **Silent in the model, Loud in the workbook**, as diligence.
- Step 1 (labelled files): **Loud** — unreadable, listed, parked.

### 5. Tier

**Tier 2** with the same announced degrade as diligence, and last in build order of all eight. If
only one of the pair is built, build diligence: a mis-scoped transactional finding is a commercial
problem, and a leaked privileged document is a professional-conduct problem.

### 6. Probes

P4 and P9 as diligence. Nothing probes the privilege risk, because it is not a capability question.

### 7. Effort and companions

62 files today. After the global strip and `scripts/**`: 21 companions; dropping the 10 schema
contracts leaves 11; dropping the runtime references brings it to about **7**. The `references/shared/`
rewrite is shared with diligence, so the marginal cost of the second card is small once the first is
done.

### 8. Bundle and routing

Litigation, which carries 15 skills against a cap of 20. Two shipped descriptions currently declare
this territory closed — organize-case-docs and document-discovery, the latter of which also owns
"privilege-log queues", the tail end of this skill's own workflow. Both are in the same bundle, so
both clauses can become named hand-offs rather than scope statements.

### 9. The honest counter

Q7 is the sentence the alternative cannot fully honour and must quote in its own body, so a lawyer
reading the skill knows what kind of hold they are getting. "A privilege signal always creates a hold
until the lawyer rules" (Q10) survives as a rule. "It must prove the complete issue-by-unit count
equation and exact lawyer confirmation of every image-review bundle. Fix the run, never the numbers"
(Q8) becomes visible arithmetic in a workbook rather than a proof, and the skill must not use the word
prove. "This skill proposes and verifies; it does not produce, serve, file, or transmit documents"
(Q11) survives untouched and is easier to honour in Cowork than anywhere.

### 10. What the lawyer actually gets

They give the skill the production and their requests, approve the questions and the sample, and it
works through the documents a tranche at a time, filling a workbook: document, request, finding, the
words it relies on, where they are, and a privilege column. Anything that smells privileged stops
there and waits for their ruling, and nothing about a held document goes into any output. They get a
findings page they can read and a workbook they can sort. The skill will not produce anything at all
if they have not given it the workbook back, because without it, it does not know what is held.

---

## 8. regulatory

Two alternatives at different tiers. Build the first.

### 8A. regulatory, source supplied by the lawyer (recommended first)

#### 1. The alternative, step by step

The lawyer goes to the official publisher and puts the file in the Input folder. The skill works from
those bytes — literally the publisher's own document, placed by a human — and the provenance that
`fetch_source.py` used to prove becomes a short block the lawyer completes and the skill prints.

| # | Upstream step | Cowork substitute | Evidence |
| --- | --- | --- | --- |
| 1 | Identify the instrument | Same, unchanged; `references/jurisdictions/` tells the lawyer which publisher to go to | D; the registries are a dated static snapshot and go stale |
| 2 | Confirm with the user before fetching | Becomes: name the publisher and the exact document to download, and ask them to place it | D |
| 3 | Fetch from the official publisher, refusing any off-host redirect, and hash the bytes | The lawyer downloads it. The skill records a provenance block — publisher, address, date retrieved, and the lawyer's own statement that they took it from there — and prints it with the note | bring-your-own bytes D; **the retrieval receipt and the hash X**; host web search as a locator only, availability **U, probe P6** |
| 4 | Check the version | The document's own "current as at" or amendment statement, read off the page and quoted | D |
| 5 | Extract the provisions | Model reads the document; a scanned or image-only official PDF is a stop | D for text-layer; **U, probe P4** for scans |
| 6 | Construe, and quote | Same, unchanged — this is the legal method and the reason for the skill | D |
| 7 | Check the quotes before the note goes out | The skill re-locates each quote in the supplied file and records the provision label and locator; the note ends with the source filename and the provenance block, so any quote is checkable against the attached file in seconds | D, self-performed |
| — | `refresh`: compare against an earlier saved run | The lawyer attaches the earlier note and its extraction file and the skill diffs them | D bring-your-own; read-back without attaching **U, probe P2** |
| — | `compare` across markets, `check` against a plan | Same, one supplied source per jurisdiction | D |
| — | Run folder per instrument, new dated folder never over the old one | Dated files in the Output folder, named, never deleted | D |

#### 2. Capability risk

**Low.** Every load-bearing step is D. The one U — a scanned official PDF — fails loudly at step 5,
and the skill already owns the sentence for it.

#### 3. Fidelity

**Same deliverable with a disclosed weaker guarantee.** The note is the same and the central rule
survives: nothing is quoted that did not come from the publisher's own document. What weakens is the
proof of provenance — attested by the lawyer rather than established by a retrieval receipt, a
redirect refusal and a hash.

#### 4. Failure modes

- Step 3 (attested rather than proved provenance): **Loud, and the skill already has the mechanism.**
  If the provenance block is not completed, the skill falls to its own provisional route: "Begin
  **Your answer — provisional and unverified**, identify exactly which points lack proof, and state
  what document/date/check would resolve them" (regulatory Q9). That is a loud failure written by the
  skill's own author.
- Step 4 (wrong version supplied): **Loud** — the skill reads the version statement off the document
  and says what it is, so a lawyer who supplied last year's consolidation is told.
- Step 5 (U, P4): **Loud.**
- Step 7 (self-performed quote check): **Silent**, but the mitigation is unusually strong here: the
  source file is sitting in the lawyer's own Input folder, every quote carries its provision label,
  and checking one takes ten seconds. Q12 stays absolute: "If a quote fails, fix it or cut it. Never
  ship it with a caveat."

#### 5. Tier

**Tier 1.** It ships on documented capabilities and its failures are loud, because the skill's own
provisional route is the failure mode.

#### 6. Probes

None gate it. P6 tells the programme whether web search is even on in a tenant, which matters only
for locating the right document, never for quoting it. P4 for scanned official PDFs. P2 would let
`refresh` stop carrying files by hand.

#### 7. Effort and companions

23 files today; after the global strip and `scripts/**`, **12 companions** (5 top-level references
plus the 7 jurisdiction registries, 91 KB) — inside the cap. Layers: section overlays on "Fetch from
the official publisher", "Scripts reference" and "Source failure and delivery gate", a rewrite of the
`refresh` workflow's run-folder mechanics, and a `replace` pass on the script invocations in the four
workflows. The jurisdiction registries need a dated "as at" line, because they are a snapshot of where
official text lives and that moves.

#### 8. Bundle and routing

Core group, so both bundles; litigation goes to 16 and transactional to 9, both inside the cap of 20.
Two collisions. The shipped cite-check description disclaims "whether an authority is still good law,
which this skill does not determine", and regulatory is the skill upstream meant to receive that
hand-off: "For a statutory citation unit referred by another workflow, read
`references/citation-handoff.md`" (Q17), which can now be a live hand-off in both bundles. The harder
contest is that "look up what the current regulation says" is the archetypal prompt a tenant's own
research built-in will take, so the description has to lean on the supplied-source premise — this
skill works from the official text you give it — to win the right requests and lose the wrong ones.

#### 9. The honest counter

The central rule is the thing to test the design against: "Nothing is quoted that did not come from
the publisher's own bytes. Not from a search result, not from a law firm note, not from a tracker, not
from a database, not from memory, and not from a web-fetch tool's rendering of a page — that is a
model's summary of the text, not the text" (regulatory Q6). A publisher PDF the lawyer downloaded is
none of the things on that list, so the alternative respects the rule where a search-backed version
would break it. What it cannot honour is Q2 — "the whole chain depends on being able to read the same
bytes twice and hash them" — because there is no hashing; the purpose of that sentence, a source that
does not shift between steps, is met by the file sitting unchanged in the Input folder for the
session, and the difference must be stated. Q14's redirect refusal has no analogue and no longer
needs one, because the skill no longer fetches. Q10 stays: "A failed quote is removed or corrected;
the provisional label does not license unchecked quotations."

#### 10. What the lawyer actually gets

They ask what a regulation requires. The skill names the instrument and tells them exactly which
document to download and from which publisher, and waits. They drop the PDF in, confirm in one line
where they got it and when, and get back a note: what the provision says, quoted verbatim with the
clause it lives in, what version of the instrument that is and as at what date, and what it means for
their question — with the source filename and their own provenance line printed at the bottom. If
they skip the download step, the note comes back headed "provisional and unverified" with the
unproved points named, which is the skill working correctly rather than failing.

### 8B. regulatory behind a connector (deferred)

#### 1 to 3. Design, risk, fidelity

A remote MCP `agentConnector` the firm operates: it fetches from the publisher, refuses anything that
redirects off that host, and returns the bytes with a SHA-256 and a retrieval timestamp. Up to 10
connectors per package, Streamable HTTP over HTTPS, JSON-RPC 2.0 [D route]. That restores Q14 and Q2
in full. Capability risk **Low** on the capability and high on the precondition, which is
organisational rather than technical: somebody has to run and maintain the server, and the package
has to declare it. Fidelity: **Same deliverable, full guarantee** — the only one of these sixteen
designs that gives a guarantee back rather than taking one away.

#### 5. Tier

**Tier 4.** Build 8A first and build this only if testers say the download-and-attest step is the
friction. The evidence from 8A will say whether it is.

---

## Summary

| Skill | Alternative in one line | Capability risk | Fidelity | Worst failure mode | Tier | Probes | Companions after surgery |
| --- | --- | --- | --- | --- | --- | --- | --- |
| read-redline | Word path primary, issues list and an HTML marked-passage view; no annotated PDF | Medium | Same deliverable, disclosed weaker guarantee | Silent: a file whose tracked changes Cowork cannot see reads as "no changes" | 2 | P3 decides; P4 for the PDF path; P10 for the Word copy | 1 |
| sigpack (A) | `signature-pages`: matrix, drafted pages, instructions, cover note, chasers; never compiles | Low | Different deliverable | Loud: the lawyer's ledger either comes back updated or does not | 3 | none gating; P9, P2 improve | 2 |
| sigpack (B) | Full sigpack including scan, verdicts and compile | Medium (four stacked U) | Core promise not deliverable if P4 fails | Silent: a blank block reported as signed | 2 | P4 and P8 both, plus P2 or P9 | 2 |
| closing-bible | `closing-index`: index, exceptions list and an Excel status register; never a receipt | High | Core promise not deliverable (Q7, Q14) | Silent count, made loud by visible workbook arithmetic | 3 | P4, P9; P8 for the combined PDF | 1 plus a register reference |
| definition-check | The skill's own C0 mode as the only mode, with a unit list and an Excel definitions register | Medium | Same deliverable, disclosed weaker guarantee | Silent: an occurrence the model did not notice | 2 | none gating; P9 for the register | ~6 |
| conform | `clause-fit`: both documents read in one session, so no ledger and no hash are needed | Low | Different deliverable | Silent: a defined term never noticed is never mapped | 3 | none gating; P10 for the redline | ~4 |
| diligence | Portable fallback as the only path, tranches, Excel master register as state and receipt | Medium | Same deliverable, disclosed weaker guarantee | Silent count, made loud by visible workbook arithmetic | 2 | P4, P9 | ~8 |
| docreview | The same, plus privilege state as column one and no register means no output | Medium | Same deliverable, disclosed weaker guarantee | Silent: a held document's words in a deliverable | 2 | P4, P9 | ~7 |
| regulatory (A) | Lawyer supplies the publisher's own document and attests where it came from | Low | Same deliverable, disclosed weaker guarantee | Loud: no provenance block means the provisional heading | 1 | none gating; P6, P4, P2 inform | 12 |
| regulatory (B) | A firm-operated connector that fetches, refuses redirects, hashes and returns bytes | Low (capability), organisational precondition | Same deliverable, full guarantee | Loud: the connector is up or it is not | 4 | none | 12 |

### Build order

1. **regulatory (A)** — Tier 1, no probe, and the only one of the eight whose failure mode was
   written by its own author.
2. **definition-check** — Tier 2, no probe, fills a gap nothing in either bundle covers.
3. **read-redline** — Tier 2, gated on P3, which is the single most valuable probe in this set.
4. **signature-pages** and **clause-fit** — Tier 3, no probes, both small and both useful.
5. **closing-index** — Tier 3, needs the register pattern proved by P9 first.
6. **diligence**, then **docreview** — Tier 2 each, shared surgery, and the privilege question in
   docreview is a decision for a litigator rather than a probe.

### The three things this whole set turns on

The **Excel register** does the work that a private filesystem and a receipt script used to do, in
four of the eight designs. It is state the lawyer carries, it is the reconciliation, and its arithmetic
is inspectable — which is the only honest substitute for a count the skill cannot prove. P9 is
therefore the probe with the widest reach after P3.

**Bring-your-own beats read-back** everywhere it was tried. Every design above that needs state across
sessions has the lawyer attach the file, which is D today, rather than waiting on P2. P2 remains worth
running because it would remove a step the lawyer finds tedious, but no design should be built on it.

**Silent counts are the recurring danger**, not missing capabilities. Six of the eight skills promise
a coverage claim that a script used to compute. In every case the answer is the same shape: make the
count visible in an artifact the lawyer can check, state the method that produced it, and never use a
word — receipt, certified, proved, complete — that claims more than a careful reading.
