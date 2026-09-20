# Excluded skills against the verified Cowork capabilities

19 September 2026

The README says fourteen upstream skills do not ship because "Cowork has no filesystem, no shell, no
network fetch and no transcript access". That sentence has been fact-checked against Microsoft's
documentation and it does not survive. This is the re-examination the maintainer's own rule requires: if
the conclusions change, the exclusion list is revisited. It is a recommendation with reasons. The
maintainer decides.

The short answer: thirteen of the fourteen still stay out, but only three of them stay out for the reason
the README gives. One is a candidate for amber surgery today, and one is worth a tester probe before
the decision is settled. Six rows of the five-row exclusion table are wrong about which capability the
skill actually needs — two skills are filed under "host session transcripts" although their own text
forbids reading transcripts, two are filed under a local store they never touch, and the skill filed under
"scripts that fetch from the network" is the one whose text forbids using a host's fetch.

**Sources and citation convention.** Quote numbers come from the two dependency profiles and restart
within each skill. "Q3" in the read-redline section means read-redline's Q3 in
`excluded-skills-profiles-pipeline.md` (read-redline, sigpack, closing-bible, definition-check, conform,
diligence, docreview, regulatory); in the companion sections it means that skill's Q3 in
`excluded-skills-profiles-companion.md` (legalquants, lq-ask, lq-connect, lq-reflect, lq-apply,
my-lq-moment). Capability facts are the verified picture handed to this analysis and are not
re-researched here.

## How the corrected picture lands on the five hypotheses

The profiles were written against five hypotheses. Mapped onto what is now settled:

- **H1 — the host reads a public web page on request. True, with two qualifications.** Bing-backed web
  search applies to Cowork, with no user toggle but an admin option that disables "web search in
  Researcher and Cowork" by name; browser use is Edge automation on the user's device, web client only,
  off until an admin enables it. So a skill cannot *rely* on it, and what comes back is a rendering, not
  the publisher's bytes. No hashing, no receipt.
- **H2 — the host executes bundled Python. Documented, contested, and unspecified.** Microsoft's plugin
  development page calls `scripts/` "Executed, not loaded into context" and gives `scripts/extract-clauses.py`
  as the example; two other Microsoft pages call a skill "instructions to the AI" and "Prompt-based
  workflows". No Microsoft page names an interpreter, a language version, installed packages, external
  binaries, parallel workers or detached runs. Treat it as true pending a probe, with no binaries and an
  unverified package set.
- **H3 — a skill reads prior session history. Undocumented.** Skills "work within the current conversation
  context" and can "reference earlier messages"; past tasks are listed and resumable, but whether resuming
  restores prior messages into the model's context is undocumented, and nothing documents a tool by which
  a skill reads another session's log.
- **H4 — the OneDrive Cowork folder persists and a skill may read and write it. Half documented.** The
  write half is documented: outputs persist in the user's OneDrive Cowork folder. The read-it-back-in-a-
  later-session half is undocumented, not denied. Cowork cannot delete files, and the temporary
  environment a task runs in is removed when the task finishes.
- **H5 — a remote MCP connector. Documented and available.** Up to 10 `agentConnectors`, Streamable HTTP
  with OAuth or dynamic client registration (no API-key auth yet), real outbound requests. A skills-only
  package has no network channel of its own.

Two repository facts frame every recommendation below. `docs/CONTRACT.md` section 8 is that cards ship no
scripts and every step has a host-native path. And no shipped skill may link to an external site, sign-up,
assessment or product; the only URL a shipped skill may carry is the upstream repository in the licence
notice. Both are policy, not capability, and the maintainer can change either — but a recommendation that
ignores them is not useful.

## Summary

| Skill | README reason | Verified reason | Recommendation | Depends on probe |
| --- | --- | --- | --- | --- |
| read-redline | local Python pipelines that do the actual work | reading tracked changes and writing annotations back onto the page | CONDITIONAL ON PROBE | P3 (tracked changes), then P4 |
| sigpack | local Python pipelines that do the actual work | LibreOffice, Poppler and OCR, page-by-page visual inspection, and a ledger that must outlive the session | STAY OUT, REASON CORRECTED | P4 + P2 would justify revisiting, not re-admission |
| closing-bible | local Python pipelines that do the actual work | the same, unchanged: the script is the only thing that balances the receipt, and the skill forbids writing one by hand | STAY OUT (reason survives) | only a CONTRACT §8 policy change, then P1 |
| definition-check | local Python pipelines that do the actual work | the same, unchanged: the deterministic OOXML parser is the product | STAY OUT (reason survives) | only a CONTRACT §8 policy change, then P1 |
| conform | local Python pipelines that do the actual work | a hash-matched definition-check ledger and definition-check's own scripts, called across skill folders | STAY OUT, REASON CORRECTED | no — definition-check not shipping is decisive |
| diligence | local parallel worker runtimes plus fail-closed receipt gates | count-reconciled coverage of a whole data room, which its own fallback may not certify | STAY OUT, REASON CORRECTED | no |
| docreview | local parallel worker runtimes plus fail-closed receipt gates | the same, over a litigation production, with privilege holds across every lens | STAY OUT, REASON CORRECTED | no |
| regulatory | scripts that fetch from the network | the publisher's own bytes, hashed — the skill forbids quoting a rendered page | STAY OUT, REASON CORRECTED | no (P6 confirms the limit rather than lifting it) |
| legalquants | a local `~/.lq/` store and a community corpus behind a connector | a private store plus a scan of what is installed on the machine; lq-start already does the routing | STAY OUT, REASON CORRECTED | no |
| lq-ask | a local `~/.lq/` store and a community corpus behind a connector | a remote MCP connector to the LegalQuants corpus — it never touches the store | STAY OUT, REASON CORRECTED | no — a connector and an external-URL carve-out are product decisions |
| lq-connect | a local `~/.lq/` store and a community corpus behind a connector | live reading of the public LegalQuants member directory — it never touches the store | STAY OUT, REASON CORRECTED | no — the no-external-site rule decides it |
| lq-reflect | host session transcripts | the same, unchanged: reading the lawyer's own past sessions, selected by content hash | STAY OUT (reason survives) | no (P5 bounds the question; it cannot unlock the skill) |
| lq-apply | host session transcripts | the `~/.lq` journey store, and a destination a shipped skill may not name — its text forbids transcripts | STAY OUT, REASON CORRECTED | no |
| my-lq-moment | host session transcripts | a bundled renderer shelling out to local image binaries — its text forbids transcripts and reads only the current session | CANDIDATE FOR AMBER | P7 decides whether the cover keeps its template |

Counts: STAY OUT (reason survives) 3, STAY OUT with a corrected reason 9, candidate for amber 1,
conditional on a probe 1.

---

## 1. read-redline

**a. Stated reason.** "local Python pipelines that do the actual work". It survives in outline but not in
substance. read-redline is the only one of the eight that genuinely needs third-party packages — "The
bundled scripts require `pdfplumber`, `pypdf`, `python-docx`, and Poppler" (Q3) — so the row's wording is
literally true here. What it hides is that the skill's own text blesses a host-native path: "If the scripts
cannot run, use host-native PDF reading, rendering, and annotation capabilities to preserve the same
calibration, extraction, visual reconciliation, quarantine, rating, and coverage rules" (Q5), with the two
degradations named as things to disclose rather than reasons to refuse (Q6). No fallback is forbidden
anywhere in this skill. Under the corrected picture the question is not whether Python runs; it is whether
Cowork can see a tracked change and put a mark back on a page.

**b. What the value rests on.** Filesystem and shell, in that order. The intermediates live in a working
directory — "Keep them under `tmp/redline/` and delete them after step 9" (Q1) — and the deliverables go
"beside the input as `<name> - Annotated.pdf` (or `.docx`) / `<name> - Issues List.docx`" (Q2). Both are
survivable: the Output folder is a real writable place, and the only real loss is the instruction to delete,
which Cowork cannot do anyway. The load-bearing dependency is the read: the method is visual — "Prefer
visual review. Run `pdftoppm -png -r 110` on every page that has changed pairs plus a sample of the rest"
(Q4) — and the Word path turns on a tracked-changes report that can say "no tracked changes found" and
stop (Q10). Network and transcript: none, confirmed both in prose and by grep of `scripts/`. Findings that
touch it: finding 2 (Poppler has no documented path even if scripts run; pdfplumber, pypdf and python-docx
are unverified) and finding 1 (the Output folder persists, so "beside the input" restates cleanly as "in
the Output folder").

**c. Recommendation: CONDITIONAL ON PROBE.** Everything in the surgery is ordinary except the one thing
nobody has tested. The probe is P3: attach a synthetic DOCX carrying tracked insertions and deletions from
two authors, and ask Cowork to list every tracked change with its author and its text. Pass signal: it
enumerates insertions and deletions separately, names the authors, and does not read the document as if
the changes had been accepted. A pass makes read-redline an amber candidate on the Word path. P4 (can
Cowork report what a page looks like, including strikethrough markup and a scanned page) decides whether
the PDF path comes with it; a fail there costs the visual-reconciliation receipt, which Q6 already tells
the skill to disclose.

If P3 passes, the surgery in this repository's layers is: `exclude: scripts/**`; a `replace` on the Output
conventions to send intermediates and deliverables to the session's Output folder and to drop the deletion
instruction, which CONTRACT §8 forbids claiming; a section overlay on "Capability fallback" making the
host-native path the only path; a section overlay on workflow step 4 replacing `pdftoppm` with "read the
changed pages"; and step 8's re-open-and-verify check (Q11) restated as a self-check the way cite-check's
colour rule was. The issues list goes out through the built-in Word skill, exactly as playbook-review's
matrix does. Losses to state in `notes`: the annotated PDF, because nothing suggests Cowork can write
annotations onto a supplied PDF and preserve its page count; the visual-reconciliation completeness
receipt if P4 fails; and the calibration gate as an enforced artifact — "A confirmed calibration is an
artifact, not a memory" (Q7) and the annotators "refuse to build without a valid artifact that matches the
current extract" (Q8) becomes a rule the model applies to itself, which is weaker and should be said so in
the body.

**d. File arithmetic.** 11 files today: SKILL.md, 7 scripts, 1 reference, LICENSE, `agents/openai.yaml`.
The build strips LICENSE and `agents/**` globally; `exclude: scripts/**` removes 7. That leaves **1
companion file** (`references/significance_rubric.md`, 2.4 KB) against a cap of 20 and 10 MB. The cap was
never this skill's problem.

**e. Bundle and routing.** Transactional. The collision is playbook-review, whose trigger list already
includes "They've sent back a revised draft - re-review it against the same playbook and tell me what
moved" and whose description says not to "expect a tracked-changes redline of the source document". Both
descriptions would need a hand-off line: read-redline reviews a redline against its own previous version
with no playbook in the room; playbook-review measures a draft against approved positions. Without that
line the two will fight over "review this markup".

---

## 2. sigpack

**a. Stated reason.** "local Python pipelines that do the actual work" — too broad, and pointed at the
wrong thing. The profile is explicit that `scripts/sigpack.py` imports "stdlib only ... no third-party
Python packages imported by the script itself". What the script needs is other programs: "Scanned-page
processing and rendering use Poppler and `tesseract` when available; Word conversion uses LibreOffice"
(Q3). None of those has a documented path in Cowork even on the reading of H2 most favourable to scripts,
and finding 2 says so in terms.

**b. What the value rests on.** Three things, none of them Python. First, page-by-page visual inspection,
which the skill treats as a gate rather than a nicety: "Without a way to render every candidate and
returned page, say plainly that the visual-review gate cannot run and do not compile an executed set"
(Q7). Second, a store that outlives the session: "Ledger: `sigpack.ledger.json` in the closing folder, next
to the execution versions. It stays with the matter" (Q1), and "The pack half opens it, every batch of
returns settles into it, and its receipt must balance. It is the memory across sessions" (Q5). Third, file
conversion: "If `soffice` is missing the command stops and says so; ask for PDFs rather than proceeding as
if converted" (Q12). Findings that touch it: finding 2 (no documented binaries), finding 1 (the Output
folder persists, but reading it back in a later session is undocumented — which is exactly the half sigpack
needs), and finding 1 again on deletion, which sigpack does not need.

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency for the table: *page-by-
page visual inspection of every signature page, Word-to-PDF conversion and OCR, and a ledger that has to be
read back in a later session.* The decision stands on the skill's own words. Its refusal is not a
fallback it dislikes; it is the product: "Compile refuses to run while any page is `unknown`. Never guess"
(Q10), and "A user who wants 'just merge them' is asking for a different, less safe tool; say so once, then
do it properly" (Q8). A Cowork sigpack that could not see the pages would be precisely the less safe tool
its own text tells it to refuse. P4 and P2 together would justify looking again — not re-admitting — and
even then the compile half needs page extraction and reassembly from supplied PDFs, which nothing
documents.

**d. File arithmetic.** 6 files today. After the global strip and `scripts/**`: **2 companion files**
(`ledger_schema.md`, `signature_page_rules.md`, 22.7 KB). Comfortably inside the cap.

**e. Bundle and routing.** Transactional, if it ever returns. No collision to invent: the shipped
closing-checklist description already says "Do not use ... for assembling signature pages", so the space is
reserved and the hand-off sentence would only need its direction filled in.

---

## 3. closing-bible

**a. Stated reason.** "local Python pipelines that do the actual work". It survives as written, and this is
one of the three skills where it does. The frontmatter says so itself: "Requires local command execution
and Python 3.12 or newer" (Q1).

**b. What the value rests on.** Shell, and uniquely a shell the skill refuses to do without: "The script is
the only thing that validates inspection records and balances the receipt. If it cannot run (no Python
3.12 or newer), stop: tell the lawyer the audit cannot be completed here and why, and produce no index,
receipt or exceptions list by hand. A receipt written without the script is not a receipt" (Q7, repeated at
Q14). The receipt is the deliverable — "The receipt is written only when it balances; if the counts do not
reconcile the script stops and says so, and that is the finding, not a bug to work around" (Q8). Network is
ruled out in frontmatter (Q4) and the filesystem need is ordinary output placement (Q2). Findings that
touch it: finding 2 twice over — no Microsoft page names a language version, so "Python 3.12 or newer"
cannot be established even by a probe that shows *something* executes, and the combined-PDF step needs
`pypdf`, an unverified package (Q6).

**c. Recommendation: STAY OUT (reason survives).** No corrected line is needed for the table; the existing
row describes this skill accurately. Under CONTRACT §8 as it stands there is nothing to discuss: a card
that ships no script cannot produce a receipt this skill would accept, and the skill forbids producing one
any other way. Only a policy change, backed by P1 showing a named interpreter of version 3.12 or newer with
`pypdf` importable, would put it back on the table — and a card whose only path is a script is one tenant
setting away from being broken, which is the argument for leaving the policy where it is.

**d. File arithmetic.** 23 files today. After the global strip and `scripts/**`: 12 companions, of which 9
are `.schema.json` contracts only the script reads. Dropping those leaves **3 companion files**
(`assembly-rules.md`, `sigpack-ledger-consumption.md`, `status-taxonomy.md`, together well under 100 KB).
The 20-file cap is not why this skill is out.

**e. Bundle and routing.** Transactional. Again the shipped closing-checklist description already reserves
the ground — "Do not use ... for auditing the signed closing folder" — and closing-bible's own routing
already hands signature-page work to sigpack (Q16) and pre-signing rooms to diligence (Q17), neither of
which ships, so those two sentences would have to be rewritten as scope statements rather than hand-offs.

---

## 4. definition-check

**a. Stated reason.** "local Python pipelines that do the actual work". Survives as written. The
deterministic OOXML parser is the product, and the skill says what the no-parser mode costs: analyse "only
content actually exposed by the host. Request pasted/exported text if the DOCX body is inaccessible. Never
claim deterministic parity" (Q6).

**b. What the value rests on.** Shell for the deterministic path (Q4), a workspace for the marked run
(Q2), and — for the full-capability path — a specific vendor's worker runtime, flagged in the source with a
waiver: "the requested packaged runner is intentionally specific to the local Codex host and worker
runtime" (Q17), "On OpenAI Codex, use the resumable one-command runner as the default full-review path"
(Q18). Network is "optional ... enhancements" in the skill's own words (Q5). Transcript: none. Findings
that touch it: finding 2 (the runtime is unspecified and no Microsoft page names parallel workers, which is
exactly what this skill's default path farms out), and the repository's own vendor-word transform, which
strips the named runtime rather than replacing it.

**c. Recommendation: STAY OUT (reason survives).** Two independent blockers, only one of which a probe
could ever touch. Even granting H2 in full, the skill's own coverage audit is what gates its deliverable —
"a missing accepted-label usage or a non-label mention marked as a definition blocks completed HTML" (Q10)
— and the degraded mode is expressly not the same product. The second blocker is that the full path is
written for a named vendor runtime this package must not mention at all. What would be shipped is the C0
mode, and the assessment's line about it still holds: the fallback path removes the reason to install it.
Q7 is the sentence to respect: "Never translate a missing parser, partial input, failed command, or skipped
method into 'no issues found.'"

**d. File arithmetic.** 67 files today, the largest of the fourteen. After the global strip and
`scripts/**`: 23 companions — 3 over the cap. Dropping the 11 `.schema.json` contracts the script enforces
brings it to **12**, including the five `prompts/` files. So the cap is survivable; it is not the reason.

**e. Bundle and routing.** Transactional. It would collide with nothing shipped today, which is itself the
point: nothing in the current bundle does defined-term review, and a C0-mode definition-check would be the
only skill in either package that opens by telling the lawyer it cannot do the thing it is named for.

---

## 5. conform

**a. Stated reason.** "local Python pipelines that do the actual work" — true but not the operative
reason, and it hides a dependency no probe can cure. conform's scripts are pure stdlib with no
`subprocess` at all. Its blocker is that it cannot start without another skill.

**b. What the value rests on.** A hard stop it applies to itself: "`/conform` never runs against a missing,
stale, mismatched, or incomplete `/definition-check` ledger. Run the packaged preflight before any mapping
work" (Q3), and in the capability table, "`/conform` cannot run: it requires the packaged preflight to
recompute and compare document hashes against ledger records, which needs local file access" (Q4). The
fallback is forbidden in terms: "Cannot run the packaged preflight or mapping engine. Stop; do not attempt
a Python-free reimplementation of hash comparison or ledger validation" (Q6), and for pasted text, "State
that `/conform` requires local command execution and cannot verify ledger freshness from pasted text
alone" (Q8). On top of that it runs a script that lives in another skill's folder —
`python <definition-check-skill-dir>/scripts/normalize_terms.py ...` — and reads that skill's references by
the relative path `../../definition-check/references/capability-routing.md`. Findings that touch it:
finding 2 (nothing documents cross-skill file access inside a Cowork package, where each skill is its own
folder), and the plain fact that definition-check is not in either bundle.

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *a current, hash-matched
definition-check ledger and definition-check's own scripts, reached across skill folders — and
definition-check does not ship.* The hard stop is not a bug to design around: "A hard stop is normal,
expected behavior, not a bug to work around" (Q10). No probe changes this while definition-check is out.

**d. File arithmetic.** 24 files today. After the global strip and `scripts/**`: 10 companions; dropping
the 3 `.json` schemas leaves **7**. Inside the cap and irrelevant to the decision.

**e. Bundle and routing.** Transactional. It would need playbook-review beside it to avoid confusion
between "conform this precedent clause into our vocabulary" and "review this draft against our playbook",
which are adjacent asks with very different outputs.

---

## 6. diligence

**a. Stated reason.** "local parallel worker runtimes plus fail-closed receipt gates". The first half does
not survive: diligence's own text says parallelism is optional — "process isolated assignments sequentially
when parallel workers are unavailable" (Q6). The second half survives and is the real reason.

**b. What the value rests on.** A count-reconciled cross-product over an entire data room, with the receipt
as the deliverable: "`reconcile_counts.py` exits 0: every approved issue has exactly one result for every
reviewable substantive unit, or that unit is visibly parked" (Q12), and "Run `reconcile_counts.py` first.
It must prove the complete issue × substantive-unit cross-product, with parked units visible; if it fails,
fix the run, never the numbers" (Q13). Underneath that sits stable file identity and a temp master dataset
(Q1, Q2) plus Poppler and LibreOffice review copies (Q4). This is the one of the eight with the richest
portable fallback, and that fallback sets its own ceiling: "The fallback is method-compatible, not
assurance-equivalent. State exactly which checks were unavailable" (Q9), and "If stable file identity and
complete count reconciliation cannot be established, the run may deliver a clearly labeled review and
unresolved queue, but it may not call the result coverage-certified" (Q10). It also forbids the obvious
shortcut: "Continue inside the same skill. Do not replace the workflow with an informal whole-room review"
(Q8). Findings that touch it: finding 2 (no documented binaries, no parallel workers, no detached runs) and
finding 1 (the temporary environment is removed when the task finishes, so "one temp master dataset
directory for this run" has no home that survives a multi-day review).

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *stable file identity and
a reconciled issue-by-document count across a whole data room; without them its own rules forbid calling
the result coverage-certified.* What could be built host-natively is a labelled, uncertified review of a
handful of documents — which is a different skill, not an adaptation of this one, and this repository
adapts rather than rewrites. Worth saying plainly to the maintainer: a Cowork diligence would be a skill
whose every delivery carries a disclaimer that the coverage claim is unavailable, which is the "promises
receipts it cannot produce" failure in a politer form.

**d. File arithmetic.** 72 files today, the largest tree of the fourteen. After the global strip and
`scripts/**`: 22 companions — 2 over the cap. Dropping the 8 `.schema.json` files leaves **14**, of which
most are the `references/shared/` tree that is byte-identical to docreview's. Inside the cap; not the
reason.

**e. Bundle and routing.** Transactional, with a litigation echo. Two shipped descriptions currently
declare its territory closed: organize-case-docs ends with "document-by-document responsiveness and
privilege review, which is out of scope" and document-discovery with "reviewing an incoming production
document by document, which is out of scope". Re-admitting diligence or docreview means rewriting both of
those clauses from "out of scope" into a named hand-off, in both bundles.

---

## 7. docreview

**a. Stated reason.** Same row as diligence, and the same correction: "Prefer the bundled Python path.
Every bundled Python script uses the standard library only" (Q3), and if they cannot run, "follow the
portable fallback in `execution-modes.md`, using isolated workers when available and the same jobs
sequentially otherwise" (Q4). Parallelism is not the blocker.

**b. What the value rests on.** The same reconciliation gate, plus a privilege discipline that is the
reason the skill exists: "Only `not-privileged` releases a unit. Pending, `privileged`, and `needs-review`
records remain held across every lens" (Q7); "It must prove the complete issue-by-unit count equation and
exact lawyer confirmation of every image-review bundle. Fix the run, never the numbers" (Q8); "Delivery
requires exit 0. Exit 1 leaves a visible rendering blocker; exit 2 means integrity failure. Neither state
is lawyer-reviewed, client-ready, or coverage-certified" (Q9). Its `references/shared/` tree, including the
fallback text quoted under diligence, is byte-identical to diligence's, so every word of Q8–Q10 there
applies here too. It also runs a local review page that "works from `file://`, loads no remote resource"
(Q5) — an HTML application, not a document, and the closest Cowork equivalent is a preview-pane page with
no local file protocol behind it. Findings that touch it: finding 2 and finding 1, as for diligence, plus
the settled fact that Cowork cannot read sensitivity-labelled files, which lands hardest on exactly this
kind of production.

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *count-reconciled,
privilege-held review of a whole production, where a held unit may not be released and an unreconciled run
may not be delivered.* Carrying privilege holds across lenses without the run state that holds them is the
part that would fail quietly, which is the worst way for a privilege mechanism to fail.

**d. File arithmetic.** 62 files today. After the global strip and `scripts/**`: 21 companions — 1 over the
cap. Dropping the 10 `.json` schemas leaves **11**. Inside the cap; not the reason.

**e. Bundle and routing.** Litigation. Same collision as diligence, against the same two shipped
descriptions, and one more: document-discovery already owns "privilege-log queues", which is the tail end
of docreview's own workflow.

---

## 8. regulatory

**a. Stated reason.** "scripts that fetch from the network". This one no longer holds, and it is backwards.
The host now has a documented way to read the web; the skill is the thing that forbids using it. Its
central rule: "Nothing is quoted that did not come from the publisher's own bytes. Not from a search
result, not from a law firm note, not from a tracker, not from a database, not from memory, and not from a
web-fetch tool's rendering of a page — that is a model's summary of the text, not the text" (Q6), under
the heading sentence "Secondary sources tell you an instrument exists. Only the official publisher tells
you what it says" (Q5).

**b. What the value rests on.** Network fetch of a very particular kind, plus file retention. `fetch_source.py`
is the only script across all eight that makes a real network call, and the receipt it produces is the
point: "The script refuses to save anything that redirects off that host. If it refuses, report that — do
not fall back to a secondary source" (Q14). Everything downstream reads saved bytes twice: "Every script
reads saved files and nothing else — a pipe, a device or a directory is refused on sight, because the whole
chain depends on being able to read the same bytes twice and hash them. Save the text and pass the path"
(Q2). Quote verification is hard-edged — "If a quote fails, fix it or cut it. Never ship it with a caveat"
(Q12) — and `refresh` needs an earlier run still on disk from a previous session (profile §8, H4). Shell
is, unusually, optional in the skill's own words: "Scripts are optional host capabilities" (Q3). Findings
that touch it: finding 3 in full (Bing-backed search applies to Cowork, admin-disableable by name, and
yields renderings, not bytes; no skill-level fetch of an arbitrary URL, no raw response bytes, no hashing),
and finding 4's irrelevance here, and finding 1's undocumented read-back half, which `refresh` needs.

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *the publisher's own
bytes with a hash and a redirect refusal — the skill's central rule forbids quoting a host's rendering of a
page.* The provisional route exists (Q9) but the skill itself describes what is left: an answer headed
"Your answer — provisional and unverified" with the unproved points named. That is the assessment's
original judgment restated with better evidence, and P6 will confirm the limit rather than lift it. H5 is
the honest route and the profile says why it would work: a connector that returned raw bytes with URL,
retrieval time and sha256, and refused off-publisher redirects, would satisfy Q6 where a rendering cannot.

**d. File arithmetic.** 23 files today. After the global strip and `scripts/**`: **12 companion files**
(5 top-level references plus the 7 jurisdiction registries, 91 KB). Inside the cap — the assessment's
"22, over" counted LICENSE, `agents/openai.yaml` and the scripts this build already removes. Its
description at 1,014 characters is also moot, because the card replaces the description wholesale.

**e. Bundle and routing.** Both bundles, if it ever returned, as a core-group skill. Two collisions. The
shipped cite-check description ends by disclaiming "whether an authority is still good law, which this
skill does not determine" and its adapted body now routes existence checks to the Deep Research and
Enterprise Search built-ins — regulatory is the skill that was meant to receive that handoff upstream
("For a statutory citation unit referred by another workflow, read `references/citation-handoff.md`", Q17).
And "look up what the current regulation says" is the archetypal prompt a tenant's own research built-in
will take, which makes the routing contest one this skill would often lose.

---

## 9. legalquants

**a. Stated reason.** "a local `~/.lq/` store and a community corpus behind a connector". Half right. The
store half is exactly right for this skill; the corpus half belongs to lq-ask, not here. And the reason
omits the blocker that no capability finding can cure.

**b. What the value rests on.** Shell and filesystem together, with no documented way down. Every
invocation begins with three script calls: "The orientation marker: `scripts/onboarding.py offer` — if it
says show, §2 runs exactly once. Then `~/.lq/profile.json` — if it exists: `practice.sentence`,
`fluency.level`" (Q1); "run `scripts/onboarding.py offer` (no `--root`, so `~/.lq`)" (Q3); and counters via
"`../lq-reflect/scripts/profile_store.py status`" (Q6). Writes are delegated and gated: "Anything that
changes their profile — a stage note, a declined offer — is written only through the store script, shown
verbatim, on their explicit yes" (Q8), and "Never edit `~/.lq/` files directly" (Q2). The profile records
that no chat-only fallback is documented anywhere in this skill. The uncurable part is Q4: it runs "the
catalog script that ships with the `lq-start` skill (`../lq-start/scripts/catalog.py --all-plugins --format
json` ...)" to enumerate what is installed on the machine — and CONTRACT §8 says a shipped skill must not
"claim a skill can see which other skills or bundles are installed". Network and transcripts: none, and the
"no transcripts" is a design choice, not a gap: "Read nothing else. No transcripts, no documents, no matter
names" (Q5).

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *a private `~/.lq` store
written through a script, and a scan of which plugins are installed on the machine — and lq-start already
does the routing job from a static map.* Note for the maintainer: the three cross-skill script paths in Q1,
Q4 and Q6 all reach into sibling skill folders, which is a second structural problem in a Cowork package
even if every capability question went the right way.

**d. File arithmetic.** 6 files today. After the global strip and `scripts/**`: **1 companion**
(`references/endings.md`) — and that file is the table of external doors (assess.legalquants.com, the
Substack, the community site), so under CONTRACT §8 it goes too, leaving **0**.

**e. Bundle and routing.** Both bundles, and a head-on collision with lq-start, which ships in both and
answers the same sentence ("where am I and what do I do next"). A secondary collision with lq-mirror on
"assess me". There is no room for this skill in either package as they stand.

---

## 10. lq-ask

**a. Stated reason.** "a local `~/.lq/` store and a community corpus behind a connector". The store half is
simply wrong for this skill: the profile records that lq-ask never reads or writes `~/.lq/profile.json` or
`journey.jsonl`, and the string `~/.lq` does not appear anywhere in its SKILL.md. Its only store contact is
the shared first-run marker (Q1). The connector half is right, and it has become the most interesting row
in the table because H5 is now documented and available.

**b. What the value rests on.** Network fetch, of three different kinds. The live corpus behind the
connector, with its own documented degrade — "If it is **not available**: say so in one plain line ('the
live corpus isn't reachable from here') and work from the public surfaces instead" (Q5). Public code: "'Does
the community have a tool for this?' is answered from github.com/LegalQuants — public repositories, fetched
live (the org page, a repo's README) and cited by repo name" (Q4). And a live builds search through a
sibling's script: "`../legalquants/scripts/evidence.py search-builds` — every member's submitted project,
title and description, searched live" (Q3), which the profile notes parses data embedded in a Next.js chunk
rather than a documented API, so a rendered-page read would probably not recover those fields. Shell is
needed for `source_access.py` (Q2) and for the sibling's `evidence.py`. Transcripts: none. Findings that
touch it: finding 5 in full (agentConnectors, Streamable HTTP, OAuth or DCR, API-key auth not yet
available, and "Connectors are only needed when your skill requires live data from an external system"),
and finding 3 (H1 would cover the essays and READMEs but not the builds directory).

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *live query of the
LegalQuants corpus through a remote MCP connector; it never touches the local store.* Two things keep it
out, and neither is a Cowork capability. The first is this repository's scope: the packages are
skills-only, and the README already says porting a connector is not a contribution it wants. The second is
CONTRACT §8's rule that no shipped skill links to an external site or product — lq-ask's entire ending is
the paid Substack (Q8) and its sources are legalquants.com surfaces. Strip those and the skill has nothing
to cite. Worth flagging clearly: this is the one excluded skill whose route is now documented and
buildable, and what stands in the way is a product decision — stand up an authenticated Streamable-HTTP MCP
server and carve out the external-URL rule — not a missing capability.

**d. File arithmetic.** 6 files today. After the global strip and `scripts/**`: **2 companions**
(`service-contract.md`, `sources.md`, 4.9 KB). A connector version would also need an
`mcpToolDescription` file and an `agentConnectors` entry in the manifest, which is packaging, not a
companion.

**e. Bundle and routing.** Both bundles. Collides with the tenant's own research and search built-ins on
almost every phrasing a lawyer would use, and with the shipped wiki card, which explicitly sends "research
into outside material" to the research built-in. A skill whose answer is "what does this community think"
is distinguishable in principle, but only if its description says so in the first clause.

---

## 11. lq-connect

**a. Stated reason.** "a local `~/.lq/` store and a community corpus behind a connector". Wrong on the
store, and misleading on the connector. The profile is unambiguous: lq-connect has no `scripts/` folder at
all, never calls `profile_store.py`, and `~/.lq` does not appear in its text. Its only store contact is the
shared first-run marker (Q1). And it needs no connector: what it needs is to read public web pages.

**b. What the value rests on.** Network fetch, as plain prose rather than as a script: "Read the public
directory (`legalquants.com/community`, profiles at `/profile/<slug>`). Match on the taxonomy in
`references/taxonomy.md`" (Q3). Its evidence-deepening steps do go through a sibling's script — "`../legalquants/scripts/evidence.py
code --repo <owner/repo> --path <file>` for one bounded, cited excerpt" (Q2) and "`evidence.py page --url
<url>`" (Q9) — but those are conditional, not the load-bearing step. It sets its own boundary on what a
citation is: "LinkedIn is named if listed, never fetched — an unauthenticated fetch there returns a login
wall, not content ... a citation is something you fetched and can quote, or it is not a citation" (Q4). On
transcripts it is stricter than the exclusion table imagines: "no client names, no matter details, no
document content, and nothing raw from the current session unless they paste it themselves" (Q5). Findings
that touch it: finding 3 — under H1 the load-bearing step is newly plausible, tenant permitting, because a
rendered directory page is exactly what the skill wants to quote.

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *live reading of the
public LegalQuants member directory.* On capability alone this is the closest of the six companions to
buildable today, and that should be recorded honestly. What keeps it out is CONTRACT §8: the skill's whole
output is a name plus a link on an external site, and no shipped skill may carry such a URL. There is also
a fit problem the capability picture does not touch — a Cowork tenant that installs a legal-skills plugin
is not thereby a LegalQuants member, and the skill's two documented misses both end by handing over the
public directory link (Q7, Q8), which is the one thing it may not do here.

**d. File arithmetic.** 4 files today. After the global strip: **1 companion** (`references/taxonomy.md`,
1.9 KB). The smallest of the fourteen.

**e. Bundle and routing.** Both bundles. Collides with the tenant's people-search surfaces and with
Enterprise Search on "who knows about X"; nothing in either shipped bundle competes, because nothing in
either bundle is about people.

---

## 12. lq-reflect

**a. Stated reason.** "host session transcripts". Survives, and this is the only one of the three skills in
that row for which it is true. One precision is owed: transcript access is undocumented rather than
documented-absent, and what lq-reflect needs is not the documented within-conversation context but reading
*other* sessions, across a window, by exact file.

**b. What the value rests on.** Transcript access of a specific shape, and the shape is the consent
architecture. Scope comes from a metadata-only scan — "run `scripts/debrief_scan.py --list` with the window
and `--state ~/.lq` for candidates (metadata only, no content)" (Q3) — and only then the content: "retrieve
its complete messages and surrounding responses through `session_reader.py --session <exact filename>
--manifest <file> --confirmed --lines <start> <end>`, within that same confirmed selection" (Q4). The
window is days or weeks: "Default: since the last debrief, or the last seven days on a first run. `24h`,
`3d`, `7d`, `30d` when asked" (Q6), against hardcoded on-disk stores (Q7). The store is the second
dependency — "`~/.lq/` holds the store. Every write goes through one `scripts/profile_store.py` call per
run" (Q1) — and the skill has already anticipated a restrictive host: "If the sandbox refuses a write, say
so and give the exact command for the lawyer to run" (Q2). Crucially, it forbids improvising the read:
"Avoid custom transcript searches, ad hoc Python extraction, database content reads, `cat`, `rg` or subagent
reads that bypass the selection" (Q13). Findings that touch it: finding 4 in full — Cowork documents the
current conversation, lists and resumes past tasks, and retains transcripts for eDiscovery and audit, which
is an admin surface, not a skill's.

**c. Recommendation: STAY OUT (reason survives).** No corrected line needed for the table. P5 is worth
running because the answer is interesting for other reasons, but it cannot unlock this skill: even a pass
would show that a *resumed* task remembers its own earlier messages, which is one thread, not the lawyer's
last seven days across every session. The chat-only branch exists — "If they decline, work only from what
they tell you — that is often enough" (Q9) — but it is a consent-decline path inside Live mode, not a
substitute for the debrief, and shipping it as the whole skill would be shipping lq-mirror with extra
steps.

**d. File arithmetic.** 12 files today. After the global strip and `scripts/**`: 5 companions; dropping
`store-contract.md` and `reading.md`, which describe the scripts and the reading contract, leaves **3**
(`bottlenecks.md`, `mining.md`, `technique-ladder.md`, under 20 KB). Not the reason.

**e. Bundle and routing.** Both bundles. Two collisions. lq-mirror, which ships in both and takes "assess
me" and "where am I with AI". And timenarratives, which takes "write up what I did today" — "go through my
sessions from the last week" is one paraphrase away from that, and timenarratives' own description ends
with a scope statement precisely because that boundary is thin.

---

## 13. lq-apply

**a. Stated reason.** "host session transcripts". Flatly wrong: lq-apply's own list of sources ends "Never
used: raw transcripts, unconfirmed or proposed items, anything that looks like a client, a matter, or
document content" (Q5). It reads no session logs at all.

**b. What the value rests on.** The store, read through a sibling's script: "Read `~/.lq/profile.json` and
`~/.lq/journey.jsonl` through the store contract's read paths (`../lq-reflect/references/store-contract.md`;
script at `../lq-reflect/scripts/profile_store.py` ...)" (Q1), with writes confined to one door (Q8). A
local output — "Where it goes. Local file, saved where they say" (Q2). And an optional fetch with a
graceful degrade: "Fetch the form's current fields when reachable (the wording is the site's, never from
memory); when unreachable, say the draft is provisional" (Q4). Notably it also documents a complete no-store
mode: "Empty or missing store: say so honestly and start one now ... then compile from what they give you
in this session. Never send them away to wait" (Q9). Findings that touch it: finding 1 (an Output-folder
draft is exactly what H4's documented half provides) and finding 3 (H1 covers Q4's form-wording fetch,
tenant permitting).

**c. Recommendation: STAY OUT, REASON CORRECTED.** Corrected one-line dependency: *the `~/.lq` journey
store, and a destination — an external application and assessment site — that a shipped skill may not name.*
On capability this skill is close to portable: a conversation-driven draft written to the Output folder is
squarely inside what Cowork does, and Q9 makes the storeless mode a first-class path rather than a
degradation. What ends it is purpose. The artifact exists to be submitted at an external assessment site
(Q10, Q11), and CONTRACT §8 forbids a shipped skill from naming it. Remove the destination and what is left
is a generic CV drafter with no evidence behind it, which is not this skill and not something either bundle
needs.

**d. File arithmetic.** 4 files today, no scripts of its own. After the global strip: **1 companion**
(`references/formats.md`, 2.9 KB).

**e. Bundle and routing.** Both bundles. Collides with lq-mirror on self-assessment and with writing on
"draft my CV"; neither collision is severe, because the collisions are not what keeps it out.

---

## 14. my-lq-moment

**a. Stated reason.** "host session transcripts". Wrong, and in the opposite direction from lq-apply: this
skill reads only the current session, by rule, and says so twice. "Scope is the **current session only**: no
history, no transcripts of other sessions, no `~/.lq/`, no profile or playbook reads" (Q2). What it reads
is "this session's conversation, the tool and skill events, the workspace artifacts (files edited or
created, tests and validation results)" (Q8) — which is close to what Cowork documents that a skill has.

**b. What the value rests on.** Shell, and specifically shelling out to image binaries. "The cover is
rendered by the skill's own script, never by an image model: draft the two sentences short (eight to ten
words each; the script refuses more than twelve), get the lawyer's yes on them, then run
`scripts/render_cover.py --before '…' --after '…' --out-dir outputs`" (Q3). The script rasterises through
whichever of `rsvg-convert`, `magick`, `inkscape`, `qlmanage` or a headless browser exists. The body
already anticipates a restrictive host: "on a sandboxed host the renderers may be present but blocked, so
ask for permission to re-run the same command with the host's elevated execution capability" (Q4). Its
degrade path is documented and its forbidden alternative is named: "Only if that also fails, say so, hand
over the SVG and the approved text, and give the one-line conversion ... Do not draw anything yourself, ask
an image model, or claim a PNG exists" (Q9). The one write to the store is optional, consent-gated and
single-line (Q6, Q7). Findings that touch it: finding 2 (no documented external binaries, so even a
passing script probe would not deliver a rasteriser) and finding 1 (the Output folder is exactly where Q1's
cover files are described as landing).

**c. Recommendation: CANDIDATE FOR AMBER.** This is the one of the fourteen where a host-native adaptation
is plausible today under the no-scripts policy, and the repository has already performed the same surgery
once on lq-mirror. In the repo's layers: `exclude: scripts/**`; a section overlay on step 3 replacing the
render command with "fill the supplied cover template with the two approved sentences and save it as an
HTML page for the preview pane", which is the pattern cite-check now uses with `report-template.html` and
playbook-review with the Word skill; a section overlay or `replace` deleting step 5's store write
(`profile_store.py` is another skill's script and the store does not exist here); and a `replace` on the
ending, which currently routes to lq-apply, a skill that does not ship — a scope statement takes its place.
What it loses, and what the card's `notes` must say: the PNG artifact, since Cowork's documented outputs do
not include a rasterised image and Q9 forbids drawing one or claiming one exists; the saved line, so a
moment is a reading, not a record; and — pending P7 — possibly the fixed template image itself, if a skill's
output cannot embed a bundled companion asset. What must be respected: Q9's prohibition survives the
surgery unchanged, and the body must keep saying it. The honest counter-argument for the maintainer: an
"LQ Moment" is a LegalQuants-programme construct, the rubric judges the session against that programme's
standard, and lq-mirror already occupies the one reflective slot in both bundles. The surgery is easy; the
question is whether a second reflective skill earns its place.

**d. File arithmetic.** 10 files today. After the global strip and `scripts/**`: **6 companions** — four
references (`copy.md`, `cover.md`, `examples.md`, `rubric.md`), `assets/README.md` and
`assets/cover-template.png` at 583 KB. Against the caps: 6 of 20 files, largest 583 KB of 5 MB, total
602 KB of 10 MB. It is the only one of the fourteen with a binary asset, and the 15-second companion
download timeout is worth remembering for that file, though 583 KB is not a plausible cause of failure.

**e. Bundle and routing.** Both bundles, as a core-adjacent reflective skill. Collisions: lq-mirror, whose
description already claims "assess me", "what's my archetype" and "where am I with AI" — my-lq-moment's ask
is narrower ("was this session the good kind?") and the two descriptions would need an explicit hand-off in
both directions; and legaldesign, which owns "make me a polished page for the preview pane" and would
otherwise take the cover request.

---

# Across all fourteen

## The corrected exclusion table

The current table has five rows for fourteen skills, and three of those rows now group skills whose
reasons differ. One row per skill, with a Status column, is what the corrected picture supports:

| Skill | Depends on | Status |
| --- | --- | --- |
| read-redline | reading tracked changes in a Word document, and putting marks back on a page | Out pending a tester result |
| sigpack | page-by-page inspection of every signature page, document conversion and OCR, and a ledger that has to be read back in a later session | Out |
| closing-bible | a local Python pipeline that does the actual work: it is the only thing that balances the receipt, and the skill forbids writing one by hand | Out |
| definition-check | a local Python pipeline that does the actual work: the deterministic document parser is the product | Out |
| conform | a current, hash-matched definition-check ledger, and definition-check's own scripts — and definition-check does not ship | Out |
| diligence | stable file identity and a reconciled issue-by-document count over a whole data room; its own rules forbid certifying coverage without them | Out |
| docreview | the same over a litigation production, with privilege holds that must survive every lens | Out |
| regulatory | the publisher's own bytes, hashed: its central rule forbids quoting a host's rendering of a page | Out |
| legalquants | a private local store written through a script, and a scan of which plugins are installed; the lq-start skill already does the routing | Out |
| lq-ask | live query of the LegalQuants corpus through a remote connector, and links to material outside the tenant | Out — the connector route is real but out of scope here |
| lq-connect | live reading of the public LegalQuants member directory, and a link out to it | Out — no shipped skill carries an external link |
| lq-reflect | reading the lawyer's own past sessions, selected by exact file | Out |
| lq-apply | the private journey store, and a destination outside the tenant that a shipped skill may not name | Out |
| my-lq-moment | a bundled renderer that shells out to local image programs | Candidate for a future release |

## The paragraph that replaces "Cowork has no filesystem"

Two sentences, to sit under the table where the current paragraph does:

> Cowork works on files in OneDrive and SharePoint rather than a disk you can address, runs no
> interpreter, external program or page renderer that any Microsoft page names, reaches the web only
> through a tenant-controlled search that returns a rendering rather than the publisher's bytes, and
> exposes no session history beyond the conversation in front of it. Each of these skills puts its value
> in exactly what is missing — a hashed byte, a mark on a page, a receipt a program balanced, a ledger
> that outlives the session — so shipping one as prose would ship the instructions without the machinery,
> and a skill that promises receipts it cannot produce is worse than no skill.

The sentence after it, about a remote MCP connector being the honest long-term route, should stay and is
now better supported: connectors are documented, up to ten per package, Streamable HTTP with OAuth or
dynamic client registration.

## docs/CONTRACT.md section 8: keep the policy, fix the premise

**Keep "Cards assume no script runs" as a deliberate policy. Change the sentence above it, which is now
factually wrong.** Section 8 currently says "Whether bundled scripts execute is undocumented." It is
documented: Microsoft's plugin development page (updated 17 September 2026) lists a skill's `scripts/`
folder as "Executed, not loaded into context", labels it "Executable utilities", and gives
`scripts/extract-clauses.py` as the example; the Use Cowork page names script execution as a background
operation and says "Code is never executed during static checks". Suggested replacement:

> Microsoft's plugin development page says a skill's `scripts/` folder is executed rather than loaded into
> context; two other Microsoft pages describe a skill as instructions to the model and as a prompt-based
> workflow. No Microsoft page names an interpreter, a language version, installed packages, external
> programs, parallel workers or detached runs, and the code-interpreter documentation covers declarative
> agents without mentioning Cowork. Cards therefore assume **no script runs**: every step must have a
> host-native path.

The policy itself should not move, for three reasons. The runtime is unspecified, so a card that depended
on a script would be depending on an unnamed interpreter with an unknown package set. Nothing documents
external programs at all, and five of the eight pipeline skills need programs rather than packages —
LibreOffice, Poppler, Tesseract, an SVG rasteriser — so even a perfect Python probe would not reach them.
And a script path is a second way for a skill to fail that the lawyer cannot see, in a product whose own
static checks never execute code.

**What would have to be shown to change it.** Not "a script ran once". The bar should be: probe P1 returns
a fingerprint naming an interpreter and version, with an explicit list of importable packages, reproduced
by two testers in two different tenants; and, for any specific card, the exact packages that card needs
appear in that list. Even then the right change is per-card and conservative — a script as an optional
accelerator with the host-native path retained and authoritative, never a card whose only path is a script.
Nothing about external programs should change without a probe that names them, and there is currently no
documentation to hang such a probe on.

## Tester probes, for docs/TESTING.md and the `uat` issues

These are capability probes rather than skill tests: they belong in a short Part E, and each maps to a
re-admission decision above. Synthetic files only, one fresh conversation each, and the report should say
which Cowork client and whether the tenant has web search enabled.

**P1 — Does a bundled script actually run, and in what?**
*This one cannot be run from the released bundles, because no shipped skill contains a script.* It needs a
throwaway single-skill probe package containing `scripts/probe.py`, which prints one line naming
`sys.version`, `platform.platform()`, whether `pypdf`, `pdfplumber`, `docx`, `openpyxl` and `PIL` import,
and whether `soffice`, `pdftoppm` and `tesseract` are on the path; the SKILL.md says to run it and report
its output verbatim.
Prompt: `Run the environment probe and show me its output exactly as printed.`
Pass signal: the reply contains the fingerprint line, with a real Python version string. A reply that
paraphrases the script, describes what it would print, or reports the script as instructions is a fail and
should be recorded as such — it is the most informative outcome the programme can produce.
Unlocks: nothing directly, under the policy recommended above. It is the input to the policy decision, and
to closing-bible, definition-check and read-redline's primary paths.

**P2 — Does a file written in one session come back in the next?**
Prompt, session 1: `Create a file called probe-ledger.json in my Cowork Output folder containing exactly {"probe":"lqc","n":1} and tell me where you put it.`
Prompt, a new session on a later day, with nothing attached: `Open probe-ledger.json from my Cowork folder, tell me what n is, then save it back with n increased by one.`
Pass signal: it finds the file without the tester attaching it, reports `n` as 1, and writes 2 — and a
third session reads 2.
Unlocks: the cross-session half of sigpack's ledger and regulatory's `refresh`; more broadly it is the
answer to H4's undocumented half, which several future adaptations would rest on.

**P3 — Does Cowork report tracked changes in a Word document?**
Prepare a two-page synthetic DOCX with tracked insertions and deletions by two named authors and one
comment.
Prompt: `List every tracked change in this agreement: the exact inserted and deleted text, who made it, and where it sits. Tell me if there are none.`
Pass signal: insertions and deletions listed separately with authors, and the comment noted; and, on a
clean copy of the same file, it says there are none rather than inventing some.
Unlocks: read-redline's Word path — the condition for moving it to amber. Also strengthens playbook-review,
which ships and disclaims tracked-changes output today.

**P4 — Can Cowork tell what is on a page?**
Prepare a four-page synthetic PDF: page 2 carries redline markup (strikethrough and underline), page 3 is a
scanned image of a signature block signed over a printed name, page 4 is clean.
Prompt: `Go through this PDF page by page. For each page tell me whether anything is struck through or underlined, whether there is handwriting or a signature, and whether the page is scanned rather than typed.`
Pass signal: correct per-page answers, including that page 3 is an image and is signed, without being told.
Unlocks: read-redline's PDF path; and it is the first of the two things sigpack would need before anyone
reopens that decision.

**P5 — What does a resumed task remember?**
Prompt, session 1: `Remember this reference for later: ALDERNEY-7. Draft me two lines about anything.`
Then, from the task list, resume that task the next day: `What was the reference I gave you?`
Then, in a brand-new task: `What did I ask you in my previous Cowork task?`
Pass signal: the resumed task returns ALDERNEY-7 unprompted; the new task does not know. The second half
answering is a bigger finding than the first half failing and should be reported loudly.
Unlocks: nothing — lq-reflect needs the lawyer's last seven days across every session, not one thread. It
bounds H3 and it tells any future multi-session design what it may assume.

**P6 — Is web search on in this tenant, and what comes back?**
Prompt: `Search the web and quote me, word for word, the opening sentence of the official text you find at legislation.gov.uk for the Bribery Act 2010 section 1, and give me the address of the page you read.`
Pass signal: a URL and a quotation, plus whatever the client says about web search; a refusal naming a
disabled web-search setting is an equally useful result and should be reported with the tenant's admin
posture if known.
Unlocks: nothing — it confirms the limit rather than lifting it. It matters because cite-check ships today
and its existence check assumes a research surface, and because it is the evidence for regulatory's
corrected row.

**P7 — Can a skill's output carry a file that shipped with the skill?**
Run against the shipped legaldesign skill, which carries HTML templates as companions.
Prompt: `Turn the attached advice note into a one-pager using your supplied template, and tell me which of your template files you used.`
Pass signal: the produced HTML visibly uses the packaged template's structure and any image it carries, and
the reply names the companion file.
Unlocks: my-lq-moment's cover — whether the card keeps the fixed template image or produces a plain styled
card. It is also a useful check on cite-check's report template, which ships today and is assumed to work
this way.

## What the exclusion table gets wrong today

Six things, in the order they matter:

1. **Two skills are filed under transcripts although their own text forbids transcripts.** lq-apply: "Never
   used: raw transcripts, unconfirmed or proposed items, anything that looks like a client, a matter, or
   document content" (lq-apply Q5). my-lq-moment: "Scope is the **current session only**: no history, no
   transcripts of other sessions, no `~/.lq/`, no profile or playbook reads" (my-lq-moment Q2). Only
   lq-reflect in that row reads session logs.
2. **Two skills are filed under a local store they never touch.** The profiles record that neither lq-ask
   nor lq-connect reads or writes `~/.lq/profile.json` or `journey.jsonl`, and that `~/.lq` does not appear
   in either SKILL.md; lq-connect has no `scripts/` folder at all. Their only contact with the store is the
   shared first-run marker they call in a sibling's folder.
3. **The skill filed under "scripts that fetch from the network" is the one that forbids using a host's
   fetch.** regulatory's rule is "not from a web-fetch tool's rendering of a page — that is a model's
   summary of the text, not the text" (regulatory Q6). The host now has web search; the dependency is
   bytes and a hash, not fetch.
4. **"Local Python pipelines" implies third-party packages, and only one of the five needs any.**
   read-redline needs pdfplumber, pypdf and python-docx (read-redline Q3). sigpack's script imports stdlib
   only and shells out to LibreOffice, Poppler and Tesseract (sigpack Q3). closing-bible declares
   "stdlib-only" in its own frontmatter metadata and needs pypdf only for the optional combined PDF
   (closing-bible Q1, Q6). conform's scripts are pure stdlib with no `subprocess` at all. definition-check
   is stdlib-only and its real second blocker is a named vendor's worker runtime (definition-check Q17,
   Q18). If the row is going to name a dependency, it should name the one that bites.
5. **"Local parallel worker runtimes" is not what blocks diligence or docreview.** Both say sequential
   processing is a supported shape: "process isolated assignments sequentially when parallel workers are
   unavailable" (diligence Q6); "using isolated workers when available and the same jobs sequentially
   otherwise" (docreview Q4). What blocks them is stable file identity and count reconciliation, which
   their shared fallback text says must not be called coverage-certified without (diligence Q10).
6. **The 20-companion-file cap is not a reason to exclude any of the fourteen.** After this build's global
   strip of LICENSE and `agents/**` and a card `exclude: scripts/**`, every one of the fourteen fits:
   read-redline 1, sigpack 2, closing-bible 12 (3 after dropping script-only schemas), definition-check 23
   (12 after), conform 10 (7 after), diligence 22 (14 after), docreview 21 (11 after), regulatory 12,
   legalquants 1, lq-ask 2, lq-connect 1, lq-reflect 5 (3 after), lq-apply 1, my-lq-moment 6. The September
   assessment's "over the cap" counts included LICENSE, `agents/openai.yaml` and `scripts/`, all of which
   this build already removes. Nothing in the README claims the cap as a reason, and nothing should.

**One adjacent finding, not about the exclusion table.** The settled picture records that the Deep Research
built-in has been retired in favour of Researcher (support page updated 9 September 2026). Five shipped
places still name it: `docs/CONTRACT.md` section 8's list of built-ins, and the cards for lq-start, wiki,
pressuretest and cite-check, the last of which tells the model that "the Deep Research skill reaches the
public web". Those are live hand-offs to a built-in that no longer exists, in skills that ship today. It is
outside this analysis's scope but it is the same fact-check that produced everything above, and it is
cheaper to fix now than to learn from a misfire report.
