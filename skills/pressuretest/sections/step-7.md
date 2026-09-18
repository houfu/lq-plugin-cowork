## Step 7 — Deliver in three transmissions

Delivery is staged so the lawyer sees the shape of the fight within the
opening minutes and the checked result at the end. The map and updates live in
chat. The final delivery is a short chat summary and a complete offline HTML
report, both generated from one compact structured record.

**Transmission 1 — the map, checked with the lawyer (chat only, within the
opening minutes).** Read first the documents that state the position
under test — the draft, pleading, advice or instrument the instruction
points at, and anything the instruction names — build the map from those,
and post it. Do not wait to read the rest of the bundle or to finish
enumerating attacks: route links that rest on documents not yet read are
marked "to be checked" in the map, and late-arriving attacks join
Transmission 2 rather than delaying Transmission 1. Target: in the
lawyer's hands inside two minutes on most bundles. The map states what has
been read so far ("Read so far: D1, D2, C4") — that line is required, and the
receipt discloses it. In plain English it
states: each
position under test and what it claims, part by part; the strongest route
through the documents in two or three quoted, anchored lines; and the
planned lines of attack, every one phrased strictly as a question ("does
the pleaded reliance date precede the assurance? D2 ¶19 against D4 ¶12 — I
will test this"). It is headed `Untested — questions I am about to test,
not findings`, states no verdict, asserts nothing, and uses no impact
vocabulary. It is never written into the brief, never exported as a
standalone document, and never a citable result.

Then, in an interactive run — one where the host presents a live user who
has replied or can reply in this session — stop and ask: **"Is this the
position you want tested, and are these the right questions? Correct or
add anything before I run the attacks."** Wait for the reply, but not
idly: read the rest of the selected set while the lawyer considers the
map, and complete the inventory (Step 2) in the same stretch. Treat
corrections as boundary amendments and record them; an unqualified "go"
suffices to proceed. This checkpoint is the cheapest moment to fix a
mis-scoped run — adjudication only starts once the lawyer has confirmed
the target *and* every selected document has been read. If the full read
changes the confirmed map — a position or limb restated, the strongest
route rerouted, a document the map relied on superseded — open
Transmission 2 with a one-sentence map update, record it in the companion
(`checkpoint.map_changed_after_full_read` true, with `change_note`), and
in an interactive run let the lawyer object before the first adjudication
is posted. Record which documents had been read when the map was posted
in `checkpoint.map_read`; the receipt states it. In an interactive run, an unanswered checkpoint is not consent: finish safe
reading, record `checkpoint.status: unanswered`, then return control and wait
for the lawyer. Do not start adjudication, invent a reply, or switch to batch
mode because time has passed. Record `confirmed` after an unqualified go or
`amended` after the lawyer's corrections have been incorporated. A material
change after the full read requires renewed confirmation before adjudication.
Use `non_interactive` only where the actual host cannot receive a reply or the
user explicitly requested a batch run; an assistant-authored test prompt does
not supply user consent. In that branch, write the map to transient `docket.md`,
including "Read so far", and proceed with the absence of a lawyer check disclosed.
Never claim an automated fixture validated the real interactive exchange.

**Transmission 2 — adjudication updates (chat only, optional).** As attacks
resolve, post short updates in plain language ("The side letter expressly
overrides the agreement; I am still checking when the waiver expired").
Confirmed Pressure Points may be stated as soon
as they are adjudicated and anchored — the flip statement travels with the
first mention. Skip this transmission entirely on small bundles where the
final brief will land inside a few minutes anyway.

**Transmission 3 — the checked result (HTML report and short chat summary).**

Build one compact record of the run — tested positions, strongest route,
coverage, every attack and its adjudication, and the checkpoint state — and
generate both outputs from it. Do not analyse twice, and do not author the
summary and the report independently.

1. **Summary.** Two to four short sentences: the main problem and its
   consequence (or why the position remains supported), what still holds, and
   what to do next. Name the affected party and the actual transaction, claim
   or relief; do not say a whole case fails when one part does. For an
   incomplete review, lead with what remains untested and qualify the answer.
   Write for a lawyer without this chat's context, in ordinary language,
   distinguishing a substantive problem from a correction or an evidence
   question. Scope-confirmation wording follows the recorded checkpoint status
   and is never authored as a claim of consent in free prose.
2. **Sources and anchors.** List every selected document with a readable name
   and date, matching the coverage partition exactly, including unreadable,
   excluded and parked items. Each anchor carries the selected filename, the
   verbatim quote and a visible locator — "clause 4.4, PDF p.2", not "D2".
   Write "the buyer's firm offer dated 3 September 2026 (correspondence item
   C13), PDF p.6" and keep the readable name on later mentions; never make the
   reader decode a trailing key. Take titles and dates from the supplied
   source. Do not invent item names, and do not invent missing pinpoints:
   state "pinpoint unavailable" and disclose the limit.
3. **Findings.** Every finding has a title and a statement. Every Pressure
   Point also carries the party and limb it hits, the test applied, the next
   step, whether the position survives, and its flip or defect statement;
   optionally the smallest change that would fix it. Defeated and
   route-weakening attacks retain their dispositive anchor note; watch items
   may add what would close them. Titles state the practical finding in plain
   language — "The guarantee does not make the deferred price unconditional" —
   with no methodology label. Group findings as problems, contradictions,
   evidence questions and practical points, and include corrections and
   qualifications there without presenting them as further reasons the
   position fails. Render every adjudicated finding, including on an
   incomplete run, completely and once; never abbreviate away a sixth point, a
   supporting passage, a consequence, a survival statement or an action.
4. **Report.** Fill the supplied [report template](assets/report-template.html)
   from that record and save it as an HTML file the lawyer opens in the preview
   pane. The template fixes the layout: do not write replacement HTML, repeat
   the analysis or invent display fields. The file must read completely on its
   own; a link to a source is optional navigation, never a substitute for the
   readable name and pinpoint beside the quote. After the summary, include the
   short **How to read this review** explanation — potential issues have been
   tested; some need attention, while answered objections explain supported
   parts of the argument, not further defects or assurance about the whole
   position — even if the user saw the Step 0 orientation, and without being
   asked. Order: summary, reading explanation and issues requiring attention →
   problems with the position → contradictions to correct → evidence still
   needed → practical points and qualifications → strongest supporting
   argument → objections the documents answer → arguments that fail without
   changing the conclusion → review limits and sources. Omit empty groups.
   Each finding appears in full once; the opening highlights reuse titles, not
   a second analysis. A sound result includes its strongest route.
5. **Delivery.** Post the short summary in chat, then the report file, saying
   where it was saved and what the Step 8 checks found. Do not paste the full
   report into chat as well unless asked. If a file cannot be produced or
   delivered, give the complete checked reading view in chat instead, in
   consecutive parts if necessary, and disclose which outputs and checks were
   unavailable. The chat reading view carries the same findings, quotes and
   locators: a different delivery route, never a shorter analysis.

**Export on request.** Produce the same record as a standalone document with a
title, date and context added; findings, sources, quotes and outcomes are
unchanged. Do not re-analyse or rewrite the findings to export them. Use the
Word skill when the lawyer wants a Word file, then check that every finding and
visible pinpoint survived the conversion and disclose anything that did not.
Name the actual location of anything saved.

All reader-facing prose, including progress updates, is plain English.
Keep **Pressure Point**, **attack answered**, **defeated attack**, **flip
statement**, **operative limb** and **route** as internal method terms.
Use **problem with the position**, **objection the documents answer**,
**consequence**, **part of the claim/conclusion**, and **argument** as appropriate.
An answered objection is not a defect found: the reviewer considered it and the
documents answer it. A failed argument with another independent supporting
argument is different and gets its own group. Do not use a glossary to preserve
unnecessary jargon. Source terminology remains verbatim inside quotations.
Structural labels such as `pressure_points`,
`position_holds`, `breaks_position`, `internal_defect`, `weakens_route`,
`proof_gap` and `machine_proposed` belong in machine fields, not lawyer-facing
prose. Do not display process telemetry such as "answered 'go'", "active mode"
or "interactive checkpoint". Source terminology remains quoted and attributed.
Keep `context` and other non-Pressure-Point findings free of impact vocabulary:
"load-bearing", "material defect/finding/pressure point/inconsistency", "fatal",
"dispositive", "defect", "materially/fundamentally/critically undermine".
A source's own term may be quoted; the author's classification supplies impact.
