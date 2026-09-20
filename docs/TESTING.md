# Acceptance testing: the tester programme

Nothing in this repository has been run in a live Microsoft 365 Copilot Cowork
tenant. The packages build, validate and ship reproducibly; the skill content has
been read line by line against what Cowork can do. Whether any of it *works* —
whether the right skill activates from an ordinary sentence, and whether it then
does what its description promises — is unknown, and the maintainer has no
Copilot capacity to find out.

That is what this programme is for. It has three halves, which is one more than
a half allows, and they are worth running in this order:

- **Part A — routing.** Does the right skill activate? Run from the generated
  `dist/<bundle>-trigger-tests.md` (attached to every
  [release](https://github.com/houfu/lq-plugin-cowork/releases/latest)).
- **Part B — behaviour.** Does the skill then produce what it says it produces?
  One smoke test per shipped skill, below.
- **Part E — capability probes.** Fourteen questions about what Cowork itself
  can do that nobody has answered, each one a single prompt. These are the
  highest-value thing a tester can run: several skills move a risk tier on one
  result, and one of them, P7a, costs nothing because it runs against a skill
  that already ships.

All three are recorded the same way: one
[UAT report](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml)
per result, one open
[help wanted issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
per skill to claim, and one issue per probe labelled `probe`.

## What testers need

- **A Microsoft 365 Copilot tenant with Cowork**, on desktop or web. Custom
  plugins are not supported in Cowork on mobile.
- **A bundle installed** — see [docs/INSTALL.md](INSTALL.md). Personal scope,
  shared with **Only you**, is enough.
- **The release assets**: the bundle zip, its `<bundle>-trigger-tests.md`, and
  `build-report.md` (which tells you the package version and, per skill, what
  the adaptation changed).
- **Synthetic documents only.** Every test below says what to prepare. Invent the
  parties, the numbers and the facts. Never use a real matter, a real client
  name or anything you would not publish. This is not a caution about the
  plugin; it is a caution about issue trackers.
- **About ten minutes per skill**, and the patience to start a fresh
  conversation for every prompt.

You do not need to clone this repository, install Python, or know what a section
overlay is.

## Choosing a bundle

| Bundle | Skills | Test it if |
| --- | --- | --- |
| `legalquants-litigation-cowork` | 15 | You work in disputes: drafting, cite-checking, depositions, discovery, document review, case organisation, client reporting. Ten skills are litigation-only. |
| `legalquants-transactional-cowork` | 14 | You work on deals: playbooks, redlines, defined terms, diligence, closing checklists and closing indexes. Nine skills are transactional-only. |
| `legalquants-companion-cowork` | 8 | You want to test the reflective half — where you stand with AI, what to do next, a review of a piece of work — rather than any particular matter. Nothing in it needs a synthetic deal or case. |

Five skills ship in **both practice bundles** (`lq-start`, `legaldesign`,
`regulatory`, `timenarratives`, `wiki`), and `lq-start` ships in the companion
bundle too. Test each of them once, in whichever bundle you installed, and say
which bundle in the report.

If you install more than one at once, say so in every report: two enabled
plugins contributing identically-named skills is untested ground, and how
Cowork handles it is itself a finding.

A tester can also skip the bundle:
[docs/INSTALL.md](INSTALL.md#0-upload-one-skill-on-its-own)'s Route 0 uploads a
single `.skill` archive on its own to test one skill without installing
anything else. Say so in the report — with only that skill installed, Part A's
routing tests only cover that one skill against Cowork's own built-in skills,
not against the sibling skills a bundle would install beside it.

## Part A — routing tests

Cowork picks a skill from its `description` and nothing else. The routing tests
are generated from each card's `triggers`: four or five prompts that must
activate the skill, and four or five adjacent prompts that must not, each
naming the skill that should take it instead.

### How to run them

1. Open `dist/<bundle>-trigger-tests.md` from the release. It is a table per
   skill: `Prompt | Expected | Result`.
2. **One fresh conversation per prompt.** This matters more than anything else
   here. A skill that has already activated colours everything that follows, and
   a second prompt in the same session tests memory, not routing.
3. **Attach nothing** unless the prompt itself implies a file ("this brief",
   "these documents", "the letter attached here"). Where it does, attach one
   short synthetic document so the prompt is not obviously empty — the routing
   decision is made on your words, but a prompt that references a document with
   no document present invites a clarifying question instead of an activation.
4. Type the prompt **exactly as written**, in a single message.
5. Record what actually activated in the Result column, then move on. Do not
   continue the conversation: you are testing the first hop.

### How to tell which skill activated

Cowork's own documentation says a skill notification appears in the chat when a
plugin skill activates, and that the session side panel has a **Skills** section
listing the skills Cowork loaded during the session, shown as chips. That panel
is the primary signal: read the chip, not the prose.

**Unverified:** what that notification looks like, whether the chip names the
skill exactly as the package does (`cite-check`), and whether a skill that was
loaded but contributed nothing still appears. None of that is documented in
detail. If the panel does not give you a clean answer, fall back to inferring it
from the reply itself:

- **Shape.** Each skill has a distinctive opening move. `pressuretest` posts a
  map headed "Untested — questions I am about to test, not findings".
  `correspondence` returns a route, a reviewer note, a ledger, a draft and a
  no-send gate. `new-matter` shows a record and asks for approval before saving.
  Part B below tells you what each one should look like.
- **The closing line.** `lq-start` and `lq-mirror` are instructed to end every
  reply with, exactly: *"LegalQuants skills are a workflow aid, not legal
  advice. The judgement stays yours."* Some companion skills carry it too,
  where upstream did — the per-skill entries in `build-report.md` say which. If
  you see that line, a skill instructed to carry it ran. Its **absence proves
  nothing**: most of the thirty-one carry no such instruction.
- **Vocabulary.** A reply that uses the skill's own terms — "Unvalidated
  preview", "no-send gate", "Gate 1", "source manifest", "archetype" — is strong
  evidence. Generic competent prose with none of those markers usually means
  base Cowork answered and no skill activated at all, which is a routing result
  worth recording in exactly those words.

Record what you observed and how you concluded it. "Skills panel showed
`client-update`" and "no panel entry; reply had the no-send gate so probably
`correspondence`" are both useful, and they are not the same claim.

### What counts as a failure

- A positive prompt where the named skill did not activate.
- A negative prompt where it did.
- A prompt where **two** skills appear to be fighting over the work.
- A prompt where nothing activated and Cowork answered by itself.

All four are description problems, not bugs. See [Part D](#part-d--what-happens-to-your-report).

## Part B — behaviour smoke tests

One per shipped skill. Each gives the synthetic inputs to prepare, the exact
prompt, what a pass looks like, and what to watch for given what the adaptation
changed. "Watch for" is drawn from each card's `notes` — the record of what was
cut from upstream and therefore what is most likely to misbehave here.

A note on the colour and the tier. **Green** skills needed little adaptation and
are close to upstream. **Amber** skills lost machinery — scripts, schemas,
validators, local applications — and had that machinery replaced with
instructions. **Red** skills are the fourteen whose upstream version leaned on
machinery a Cowork package cannot carry at all, and which were re-designed
rather than ported. Seven of the thirty-one are green, ten amber and fourteen
red.

The **tier** on each entry below says how far the skill's promise moved: **0**
ships as written apart from mechanics; **1** stands only on documented
capabilities and fails where you can see it; **2** waits on one named probe, or
ships now with a degrade it announces in the reply; **3** is re-scoped, so the
promise itself changed and the description says so. Tiers 2 and 3 are where a
tester's attention is worth most, and every tier 2 and 3 entry below says what
its characteristic failure looks like. One skill, `read-redline`, ships
**probe-gated**: it works now, with a degrade announced in the reply, until
probe P3 comes back.

Start a fresh conversation for each test. Put prepared files in the session's
Input folder or attach them; either is fine, but say which you did.

### lq-start

*amber · tier 1 · all three bundles · no files needed*

**Prompt:** `What can you actually do here? Give me the map.`

**Pass:**

- It renders the whole map of **all three** bundles — all thirty-one skills,
  grouped as upstream groups them — with every entry labelled with the bundle
  or bundles it ships in, not just the one you installed.
- Exactly one neutral sentence says that a skill responds only if its bundle is
  available in the tenant, and that plugin availability is managed by the
  Microsoft 365 administrator.
- It routes and does not do the work: asked to draft something, it declines in a
  line and names the skill instead.
- The reply ends with the fixed closing line, unchanged.

**Watch for:** this is a full-file overlay — every word is this repository's, not
upstream's. It must not claim to know which bundle is installed, must not claim
a typed `/` skill menu (deliberate choice is the conversation's Sources picker),
and must not name a skill the map does not carry or invent one. Every
upstream skill is now in the map, so the failure to watch for is the opposite
of 0.1.0's: a skill named without its bundle label, or an entry recited from
memory rather than in the map's own words.

### lq-mirror

*amber · tier 1 · companion · no files needed*

**Prompt:** `Where am I with AI as a lawyer? Am I behind?`

**Pass:**

- Twelve questions, asked conversationally, one or two at a time — never dumped
  as a form or a numbered list of twelve.
- The reading names an archetype (with "The"), gives a one-liner, a paragraph
  said to *you*, and one concrete move for this week.
- It ends by naming one skill to try, chosen from what is actually available in
  the session, or falling back to `lq-start`.
- The reply ends with the fixed closing line, unchanged.

**Watch for:** this skill **stores nothing** and **gives no score**. A number, a
level, a grade, a percentile, a claim that it saved or will remember anything, a
link to an external assessment or a members-only offer are all defects — the
external link, the pitch and the save-through-a-store path were removed in the
adaptation. The summary should be offered as text you copy yourself.

### wiki

*amber · tier 1 · both practice bundles*

**Prepare:** nothing. Have a two-minute exchange first about some general point
of law or method (invented), so there is something reusable to save.

**Prompt:** `Save the reusable lessons from this conversation to my wiki.`

**Pass:**

- It asks where the wiki lives before writing anything, suggesting
  `Documents/Cowork/wiki` as a default, and never silently invents or scans for
  a folder.
- It runs the confidentiality gate before saving, and keeps matter facts out:
  reusable law and method only.
- It writes Markdown notes into the folder you named, records the change in
  `log.md`, regenerates the browsable Wiki Home, and tells you the file names.
- Asked whether it can save or retrieve on its own, it says plainly that there
  is nothing to switch on.

**Watch for:** the bundled wiki tooling is gone, so there is no hash chain, no
lock, no versions directory, no dry run and no rollback — any mention of them is
a defect. Cowork cannot delete files: a note must be **withdrawn**, never
described as deleted or cleaned up. A confidentiality problem is reported for
you to clear, not described as remediated.

### legaldesign

*amber · tier 1 · both practice bundles*

**Prepare:** one short advice note (a page is plenty) about an invented company
and an invented dispute or deal. Markdown, Word or PDF.

**Prompt:** `Turn this advice into a one-page explainer I can send the client.`

**Pass:**

- One **self-contained** HTML file: no remote code, fonts or images.
- It opens in the preview pane and the reply names the file.
- Content comes from your note — it lays out work already done rather than
  writing new substance or new facts.
- It names the checks it could not run (browser and device checks) instead of
  passing over them.
- It names any intermediate files left in the Output folder.

**Watch for:** the two builders, the JSON schemas and the clip tool were dropped,
so nothing is executed here — the model writes the specification and the HTML
itself. A claim that it "ran the builder", "validated against the schema" or
"captured" an image is a defect. Images must be genuine only where you supplied
one; the default is an exact quoted excerpt.

### timenarratives

*amber · tier 2 · both practice bundles*

**Prepare:** have a real working exchange first — ask Cowork to summarise a
short synthetic document, then ask a follow-up — so there is work to narrate.

**Prompt:**
`Do my time entries for the work we just did on the Bellweather matter for Priya Raman.`

**Pass:**

- The output is headed **Unvalidated preview**, in exactly those words.
- One concise narrative per supported workstream, each traceable to something
  actually said or supplied, with short source labels.
- **No durations, clock values, rates, fees, amounts, billing codes or
  billability decisions anywhere** — not in the narratives, not in the reply.
- The draft is shown in the reply first; a file is written only if you ask, and
  carries the **Unvalidated preview** label into the file.

**Watch for:** the forty-module script layer and the packet/anchoring machinery
are gone, and the skill is scoped to this conversation plus what you supply. Any
claim to have retrieved other chats, compiled a packet, anchored or validated
anything is a defect.

### regulatory

*red · tier 1 · both practice bundles*

**Prepare:** one short synthetic "regulation" as a PDF — three or four numbered
provisions, a title, an invented instrument number and regulator, and somewhere
on the front page a line reading "current as at 1 March 2026".

**Prompt:** `What does regulation 4 require us to do about record-keeping?`

**Pass:**

- Before reading anything it names the instrument and the publisher, tells you
  exactly which document to download and from whom, and waits.
- Attach the PDF and confirm in one line where you got it and when. The note
  comes back with the provision quoted verbatim, the clause it sits in, the
  version and "as at" date read off the document itself, and what it means for
  your question.
- The source filename and your own provenance line are printed at the bottom.
- Skip the download and confirm nothing, and the note comes back headed
  **"provisional and unverified"**, naming the points that lack proof and what
  document and date would resolve them. That is the skill working, not failing.

**Watch for:** the fetch-and-hash script is gone, so provenance is something you
attest to rather than something the skill proved. A claim to have retrieved the
document, verified a source, refused a redirect or hashed anything is a defect.
So is a quotation sourced from a web search or a browser rendering rather than
from the file you attached — the skill's own rule forbids that by name. The
jurisdiction registries that say where official text lives are a dated snapshot
and must carry an "as at" line. A scanned or image-only official PDF should stop
the run, not produce a note.

### closing-checklist

*green · tier 0 · transactional*

**Prepare:** a two- or three-page extract of an invented share purchase
agreement: parties, a couple of conditions precedent, a signing mechanic and a
completion mechanic.

**Prompt:** `Draft a closing checklist from this share purchase agreement.`

**Pass:**

- A checklist with the columns No., Source reference, Item, Responsibility,
  Timing, Status, Notes, and merged phase rows (pre-signing, signing, interim,
  closing, post-closing).
- A parties legend and a status key using only the values the table uses;
  unknown status reads "Not confirmed".
- Every item carries a source reference back to the agreement; an unknown
  adviser appears as a bracketed placeholder, never an invented name.
- The editable Word document is produced **through the built-in Word skill**.
- Any working file left behind is named.

**Watch for:** the Word helper scripts were dropped, so nothing "runs". If a Word
document cannot be produced, the skill must say so plainly and must never
present a Markdown file as a Word file.

### writing

*green · tier 0 · litigation*

**Prepare:** half a page of invented facts and one invented contract clause.

**Prompt:**
`Write me a neutral memo on whether the client can terminate under clause 12.`

**Pass:**

- It classifies the deliverable as neutral analysis rather than advocacy, and
  says so.
- Every material proposition is tied to the supplied record; gaps are named
  rather than filled.
- Inconvenient facts and reasonable alternatives stay in.
- It offers the `cite-check` and `pressuretest` hand-offs where they apply, and
  is explicit that neither authorises filing, service or sending.

**Watch for:** a green skill, close to upstream. The risk is invented authority:
if it cites cases or statutes you did not supply, record the exact citations.

### correspondence

*green · tier 0 · litigation*

**Prepare:** a one-page letter from invented opposing counsel, complaining about
invented discovery responses and demanding something by a date.

**Prompt:**
`Here's the letter opposing counsel sent this morning — triage it and tell me what it wants and by when.`

**Pass:**

- The reply comes back in the contracted order: recommended route and status;
  internal reviewer note; fact and source ledger; draft outbox; no-send gate;
  optional agenda.
- The no-send gate is explicit and lists what still needs approval.
- Where the source set is incomplete it returns a partial triage and says what
  cannot be concluded, rather than a polished fiction.

**Watch for:** the packaged exemplars are teaching material only. A reply that
reproduces a filed document wholesale, or imitates a named real lawyer, is a
defect worth reporting verbatim.

### client-update

*green · tier 0 · litigation*

**Prepare:** two short synthetic documents — an invented court order and a
five-line budget table.

**Prompt:**
`Draft this quarter's status update to the client on the Henderson litigation.`

**Pass:**

- Verified developments, analysis, recommendations and decisions stay in
  **separate layers** — no analysis smuggled in as fact.
- Deadlines, budget, exposure, risks and owners are explicit.
- The closing sections appear: `Needs confirmation`, `Sources and limitations`,
  `Distribution`, `Next trigger`, and a `No-send note`.
- It drafts and does not send, and says so.

**Watch for:** raw file paths, credentials or hidden metadata in the output, and
any statement that the report was sent, filed or uploaded.

### depositions

*green · tier 0 · litigation*

**Prepare:** a one-page invented witness summary and two short invented exhibits
(an email and a memo) that bear on when someone knew something.

**Prompt:**
`Plan the deposition of their finance director — I need to lock in when they knew about the defect.`

**Pass:**

- Objectives map to claims, defences and elements, not just topics.
- A source-backed chronology and witness map, anchored to your exhibits.
- An exhibit sequence with foundation questions, and an examination outline.
- Witness-preparation guidance stays on the right side of the ethics line
  (process, truthfulness, "I do not recall" is acceptable).

**Watch for:** invented procedural rules. It should name the federal baseline and
say that local, state or judge-specific practice may control, rather than
asserting a rule for your forum.

### new-matter

*green · tier 0 · litigation*

**Prepare:** a one-page invented complaint or demand letter, with parties, a
date and a court or agency.

**Prompt:** `We were served with a complaint this morning — open a matter for it.`

**Pass:**

- It runs a human-confirmed intake and shows the **whole record plus its save
  destination** for approval before writing anything.
- It states plainly that no conflicts search, legal hold, calendar entry,
  contact, filing, service or upload has occurred.
- Conflicts posture is recorded as *your* assertion, never as a check it ran.
- It writes only after unambiguous approval, names where it wrote, and offers an
  explicit hand-off to `organize-case-docs`.

**Watch for:** any claim to have run a conflicts search, diarised a date or
issued a hold. Also watch what it does when you say something vague like "looks
good" — praise is not approval to save.

### organize-case-docs

*green · tier 0 · litigation*

**Prepare:** three or four short synthetic documents with dates that form a
sequence — an email, a notice, an invoice, a memo.

**Prompt:**
`Organize the documents in the Alvarez matter and build a chronology with sources.`

**Pass:**

- A source manifest covering **every** file examined, including any it could not
  read.
- Chronology entries carry exact locators (page, Bates or line), not just file
  names.
- A claim-and-defence proof chart and an issue-and-evidence matrix that show
  gaps rather than filling them.
- Unreadable material is preserved and marked, never guessed at.

**Watch for:** it should decline document-by-document responsiveness and
privilege review as out of scope, and hand off rather than improvise.

### cite-check

*amber · tier 2 · litigation*

**Prepare:** this one needs a little setup, and it is worth it.

1. Write two or three short "authority" files yourself — a paragraph or two
   each, clearly invented (`Kowalski v. Reese`, a made-up statute section).
2. Write a one-page "brief" citing them, containing deliberately: one accurate
   quotation with a correct pincite; one quotation that misstates what the
   source says; one pincite pointing at a page the source does not have; and one
   citation to an authority you do **not** supply.

**Prompt:**
`Cite-check this brief against the cases in the folder before I file it on Friday.`

**Pass:**

- It works through the brief one prepared unit at a time — paragraph, footnote,
  table cell — rather than summarising the whole thing at once.
- It produces the **colour-coded HTML report** from the packaged template, saved
  as a file you can open in the preview pane, and names that file in the reply.
- The citation whose authority you did not supply is **amber — claimed but
  unverified — never green**, and the misquotation and the bad pincite are
  flagged.
- The report and the final message both carry the scope note that this checks
  citations against the sources supplied for this run and does not check later
  case history.
- The appendix accounts for every prepared unit, including units with no
  citations.

**Watch for:** the packaged runner, the JSON schemas and the validator were all
dropped — the model now applies the colour rule itself, which is exactly the
thing most likely to slip. A green row with no source excerpt or locator is a
defect. So is treating a public search hit as verification: finding that a case
exists never verifies the quotation, pincite or proposition, and it must say so
in those terms. It must not opine on whether an authority is still good law.

### pressuretest

*amber · tier 1 · litigation*

**Prepare:** three short synthetic documents that disagree with each other —
say, an agreement dated 3 March, a letter that refers to it as dated 3 May, and
a schedule whose figures do not add up to the total asserted elsewhere.

**Prompt:**
`Pressure-test our position that the termination was lawful, against these documents.`

**Pass:**

- An early **Transmission 1** map in chat, headed "Untested — questions I am
  about to test, not findings", including a "Read so far:" line, with every
  planned attack phrased as a question and no verdict.
- Attacks adjudicated one at a time, each anchored to a quoted passage.
- A verdict **derived** from the adjudications, not announced up front.
- Final delivery is a short chat summary **plus** an HTML report built from the
  packaged template, saved for the preview pane and named.
- The date contradiction and the arithmetic contradiction are both found, with
  the count shown for any period it calculates.

**Watch for:** this is the longest body in the bundle at about 5,000 words —
over Microsoft's ~3,000-word guidance, and the one warning the build reports. If
the model loses steps, skips a transmission, abbreviates findings or never
produces the report, that is precisely the evidence needed to justify cutting
the body. Also watch for leftovers of the removed machinery: exit codes, a
request to change a reasoning-effort setting, or an instruction to run a helper.

### document-discovery

*amber · tier 1 · litigation*

**Prepare:** an invented set of six requests for production, numbered, a couple
of them deliberately overbroad ("all documents concerning the company").

**Prompt:**
`Go through their requests and draft our objections and responses request by request.`

**Pass:**

- Each served request is preserved **exactly** as served, and answered
  individually.
- Combined responses are split into individual grounds; equivalent objections
  are consolidated; scope variants are kept.
- Objection candidates you did not choose are surfaced with their conditions,
  and supplying precedent wording is not treated as your approval of it.
- The editable response document is routed to the built-in **Word** skill.

**Watch for:** the two local HTML applications (objection library, objection
review), their schemas and the three references that drove them were dropped. Any
instruction to open an application, run a script or load an objection library is
a defect. Reviewing an incoming production document by document should be
declined as out of scope — `docreview` does not exist in this bundle.

### docreview

*red · tier 2 · litigation*

**Prepare:** six short synthetic production documents, numbered — two emails, a
memo, a contract extract, a meeting note, and one that plainly reads as advice
from a lawyer — plus a three-line list of what you are looking for.

**Prompt:** `Review this production against these requests, a tranche at a time.`

**Pass:**

- It maps the production, reads the review questions back to you, and asks you
  to approve the setup in plain language before reviewing anything.
- It runs a test sample first and shows you those results before scaling.
- It produces an Excel register whose **first column is privilege state**, and
  it states the held count and the held document ids before producing anything
  else.
- Findings carry the verbatim words they rest on and where those words are; the
  crosswalk renders as an HTML page for the preview pane.
- Come back in a fresh session **without** attaching the register: it refuses to
  produce findings at all, and says why.
- Nothing from a held document appears anywhere — not in the findings, not in
  the register.

**Watch for:** upstream, only a lawyer's `not-privileged` ruling released a
document and the record enforced it. Here the hold is a rule the model applies
to itself with the production in its context. Four mitigations are built in and
it is still a rule and not a lock — that is `KI-docreview-1`, and its failure
mode is silent, because a privileged document's words in a deliverable look
exactly like a correct finding. Report any instance immediately. The parallel
worker runtime and the coverage certification are gone: "coverage-certified",
"complete" and "proved" are defects, and so is calling the second pass an
independent review. Encrypted documents cannot be read and should be listed and
parked; a sensitivity-labelled one should be attempted and the result reported,
not parked on an assumption.

### playbook-builder

*amber · tier 1 · transactional*

**Prepare:** two short invented agreements of the same type (a services
agreement, say) with different liability caps and different indemnity wording.

**Prompt:**
`Build a contract playbook from our standard MSA and this negotiated agreement.`

**Pass:**

- It freezes a source census first and tells you what it is working from.
- Two gates: curate positions and lenses, then approve and seal — neither
  skipped.
- Every preferred position, fallback, red line and approved wording is linked to
  the exact source text behind it.
- It writes `playbook.md` and `coherence-report.md` as **Markdown** in the folder
  you chose, and tells you the path.
- A matter lens is proposed but not activated without your say-so.

**Watch for:** the deterministic builder, its runtime and the JSON schema are
gone. There is no `playbook.json`, no `source-manifest.json`, no
`build-receipt.json`, no hashes and no registry — the "seal" is a read-through
check the model performs and reports. Any claim of a hash, receipt or registry
entry is a defect, as is producing HTML: the Markdown files are the deliverable.

### playbook-review

*amber · tier 2 · transactional*

**Prepare:** the `playbook.md` from the previous test (or a short invented one
in the same shape), plus an invented counterparty draft that breaches two of its
positions.

**Prompt:** `Review this MSA the supplier sent against our playbook.`

**Pass:**

- **Gate 1** makes the lens decision an active choice and records it in your own
  words.
- The reply carries the triage table — Clause Ref, Topic, Risk, Status,
  Deviation & Commercial Context, Action / External Comment — sorted by risk,
  with any structural warnings **above** it.
- Then issue by issue: visible markup, a clean copy-paste drafting block, and a
  separate external negotiation comment.
- It writes `issues-list.md`, and distinguishes the **internal** cut (candid
  guidance, marked privileged) from the **external** cut (no internal guidance,
  no risk ratings), naming each.
- A coverage account reconciles every playbook rule and every document.

**Watch for:** this is a full-file overlay — over half the upstream body was
script mechanics. It returns an **issues list, not a tracked-changes redline**:
a claim to have redlined the source document, or to produce one, is a defect
(that is the Word skill's job). Verification is by reading and quoting, so any
mention of hashes, validators or a registry picker is a leftover worth
reporting.

### read-redline

*red · tier 2 · transactional · probe-gated on P3*

**Prepare:** a two-page synthetic agreement in Word carrying tracked insertions
and deletions by two named authors and one comment; plus a clean copy of the
same file with the changes accepted.

**Prompt:** `Tell me what moved in this redline the other side sent back.`

**Pass:**

- Before reading anything it says what it can see — strikethrough, underline,
  coloured text, balloons — and asks you to confirm in one line.
- Three or four themes with a line each on what the other side is doing, then
  the housekeeping, then the individual points that did not cluster.
- An issues list you could send to a partner or a client, and an HTML page in
  the preview pane showing each change old-beside-new with a materiality tier.
- On the **clean copy**: it either quotes one inserted and one deleted string
  with its author before saying there are none, or it says plainly that it could
  not determine whether the file carries tracked changes and asks you to check
  in Word. A bare "no tracked changes found" is a defect.
- The calibration line and your confirmation appear at the head of the
  deliverable.

**Watch for:** this is the one skill shipping probe-gated, and the reply should
say so — until probe **P3** comes back, it cannot confirm it can see tracked
changes at all, and a nil result has to be checked in Word. That failure is
silent and is the worst in the transactional set: a file whose changes Cowork
cannot see reads exactly like a clean draft. You do not get your own PDF handed
back with marks on it; a claim to have annotated a PDF, rendered pages at a
resolution, or quarantined a mark is a defect.

### sigpack

*red · tier 3 · transactional*

**Prepare:** two short synthetic execution versions with parties clauses and
execution blocks — one company signing by two directors, one individual signing
with a witness — and a one-page signature-page template of your own.

**Prompt:**
`Work out who signs what on these two agreements and draft the signature pages.`

**Pass:**

- A matrix table first: per document, who signs, in what capacity, how many
  originals, whether a witness is needed — shown for your confirmation **before**
  anything is drafted.
- Then the pages drafted on your own template through the built-in Word skill, a
  per-party instruction table, and a cover note carrying the escrow wording.
- A ledger you attach comes back updated in the Output folder, with the row count
  it read and the row count it wrote both stated in the reply.
- Chaser facts drafted for you to send yourself. It never sends anything.

**Watch for:** the promise has changed and the first reply should say so. This
drafts and chases; it never compiles an executed set. It does not scan a folder
for candidate pages, does not read returned pages, does not build pack PDFs, and
never tells you the set is complete — because it cannot look at what came back.
Any of those is a defect, and so is a "just merge them" compile offered as a
lesser service.

### closing-bible

*red · tier 3 · transactional*

**Prepare:** eight to twelve short synthetic closing documents with deliberate
traps — one document present under three filenames, two candidates that both look
final, and one scanned-looking execution page — plus a checklist that expects one
item you do not supply.

**Prompt:** `Build me a closing index from these documents and tell me what is missing.`

**Pass:**

- It states how many files it actually received, at the top, before anything
  else.
- A family table shown for your confirmation before it goes on.
- A proposed index in your own order; the files that group into one document
  under three names; what the checklist expects and the folder does not contain;
  and the families where two candidates both look final.
- An Excel status register — one row per expected item, with status, selected
  source, qualification, and a counted total row whose arithmetic you can see —
  labelled as a reading rather than a certified receipt.
- The scanned page reported as not inspected, with a reason.
- It says in its **first** reply, not its last, that it does not produce the
  combined bible PDF and does not certify completeness.

**Watch for:** upstream a script hashed every file and balanced a receipt, and
refused to produce anything by hand if it could not run. This is a different
skill with a different promise: no hashes, so it cannot tell you a source has
not changed since the census, and no receipt ever. The count is something you
check in the workbook, not something the skill proved — "all 43 items accounted
for" with no visible arithmetic is a defect, and so is a scanned execution page
described as signed.

### definition-check

*red · tier 2 · transactional*

**Prepare:** a synthetic agreement of a dozen clauses with deliberate faults:
three terms defined and never used, one term used in clause 14 and never
defined, "Business Day" defined twice with different meanings, and a reference
to a schedule that does not exist.

**Prompt:** `What is wrong with the definitions in this agreement?`

**Pass:**

- An opening line saying what this run can and cannot establish.
- It enumerates the document's own units — clauses, schedules, annexes — states
  the count, and works through them one at a time.
- The real problems on top: the unused terms, the undefined term, the double
  definition, the missing schedule reference.
- An Excel definitions register underneath: one row per term, clause of
  definition, definition text, count of mentions found, the locators, a
  disposition.
- An HTML review page for the preview pane carrying a line saying the coverage
  is a self-declared count, not a parse.
- The first line of the page says how many clauses it read and how many terms it
  found.

**Watch for:** the OOXML parser, its exhaustiveness guarantee and the audit that
blocked the HTML when a usage was missed are all gone. The characteristic
failure is silent: an occurrence the model did not notice simply never appears,
and the review looks clean. A clean result must read "no issues found in the 62
clauses I read", never "no issues found" — and upstream's prohibition has to
survive verbatim: a missing parser, partial input or skipped method is never
translated into "no issues found".

### conform

*red · tier 3 · transactional*

**Prepare:** a short synthetic agreement with its own defined terms ("Permitted
Liens", a Material Adverse Effect definition with no carve-out), and a precedent
clause using different vocabulary for the same ideas ("Permitted Encumbrances",
an MAE carrying a carve-out) and referring to a schedule your agreement has no
equivalent of.

**Prompt:**
`Take this indemnity from the precedent and make it fit our agreement's defined terms.`

**Pass:**

- Both documents are read in this session, and it confirms which is the core
  document.
- A mapping table: same-meaning substitutions mapped, meaning-changing ones
  escalated with a line on why it matters, the schedule with no equivalent
  flagged.
- Every term it mapped **and** every term it found no equivalent for, so you can
  see the universe it worked from.
- The rewritten clause as a Word document, offered as a proposal.
- A precedent-leakage scan.

**Watch for:** the two-run structure is gone with the ledger and the hash
preflight. There is no freshness guarantee carried from an earlier run and no
hash identity between the document reviewed and the document conformed: a claim
of either is a defect, and the skill should say plainly that it reads both
documents here and now. The vocabulary extraction inherits definition-check's
silent failure — a defined term the model never noticed is a mapping never
proposed — which is why the table has to list what it found no equivalent for.

### diligence

*red · tier 2 · transactional*

**Prepare:** your issues list, four or five lines, and a first tranche of six
short synthetic data-room documents: a lease extract, two contracts with
change-of-control clauses, a board minute, an invoice, and one scanned-looking
page. Keep a second tranche of four for the follow-up session.

**Prompt:** `Review this first tranche of the data room against my issues list.`

**Pass:**

- It compiles your list into a framework and reads it back before reviewing
  anything.
- It reviews five sample documents first and asks what is wrong with those
  findings before scaling.
- Then, one document at a time, an Excel master register: document, issue,
  finding, the verbatim words it relies on, where they are.
- An identity fingerprint per document — filename, page count, document date,
  the first line of page one — recorded, and re-read at the start of the next
  session.
- In a fresh session, attach the register and the second tranche: the new rows
  are appended, and it states the row count it read and the row count it wrote.
- A visible count of what was covered and a visible list of what was parked, and
  the tranche boundary stated on every delivery.

**Watch for:** the parallel worker runtime, the hash-bound review copies and the
coverage certification are gone. "Coverage-certified", "complete" and "proved"
are defects, and so is calling the verification pass an independent review — it
is a second pass and must say so. Scanned or image-only documents are parked as
unreadable and listed, never described. If you do not attach the register, the
run continues on reduced scope and says which tranches are recorded — that is
the rule here, and it is deliberately different from `docreview`, which stops.

### legalquants

*red · tier 3 · companion · no files needed*

**Prepare:** nothing. Optionally, a two-line `lqplaybook.md` carrying a confirmed
`[lq-start]` entry, and a dated note from an earlier review.

**Prompt:** `Where am I with all this, and what should I do next?`

**Pass:**

- One or two sentences on where you are, grounded only in what you just said and
  in whatever you attached — and it names the file it looked for when you
  attached nothing.
- **One** concrete next move, two at most, with the sentence to type for it.
- It offers skills from a static map and says plainly that it cannot see what
  your administrator installed.
- Nothing is saved. A preference worth keeping is handed to you as one exact line
  to paste into your own file.
- Bring nothing and it asks one question rather than guessing.
- The reply ends with the fixed closing line, unchanged.

**Watch for:** upstream this read the lawyer's own machine — a profile, a
journey, counters, a scan of installed plugins. None of that exists here, and
the silent failure is that it carries on from an empty journey sounding exactly
as sure. A claim to know what you have done before, to have saved anything, or
to know which plugins are installed is a defect. So is a menu: this offers one
move. Watch the boundary with `lq-start`, which routes work to a skill, and
`lq-mirror`, which reads where you stand with AI.

### lq-ask

*red · tier 3 · companion · no files needed*

**Prompt:**
`Has anyone worked out a good way to use AI for document review in litigation?`

**Pass:**

- A first line naming the date the library is current to.
- A practitioner's answer with two or three specific citations — an essay title,
  a date, a named piece of work — and no URLs.
- It names the rooms it searched and the ones it could not: the live corpus, the
  builds directory and the code are named as unavailable in plain words, not
  implied.
- When the library has nothing, it says so in one sentence and offers general
  knowledge clearly labelled as such.
- A closing scope statement: this answered from a library dated *X*, and that is
  not the whole community.

**Watch for:** upstream fetched its citations at answer time, and a citation was
"something you fetched and can quote, or it is not a citation". Here the library
is a dated snapshot shipped with the skill, and the failure is silent — a
six-month-old answer reads exactly like a current one. The words *currently*,
*now*, *the latest* and *the community now thinks* are defects. So is a citation
presented as a live query result, and so is anything newer offered without being
labelled as a search rendering from outside the library.

### lq-connect

*red · tier 3 · companion*

**Prepare:** nothing for the main path, but your tenant needs real internal
material behind whatever topic you ask about — pick one you know is covered. For
the second path, a short invented directory or contact list.

**Prompt:**
`I need to talk to someone who has actually done a data-room review with AI before I commit to this approach.`

**Pass:**

- It asks what the need is, writes it back as two sanitized sentences with no
  client or matter in them, and waits for an explicit yes.
- It hands off to the **Enterprise Search** built-in by name to find people
  inside your organisation.
- Two or three people, each with one line on why — **grounded in a document it
  names and quotes** — and one line on what to say when you reach out.
- If nobody fits, it says so rather than padding to three.
- Attach a directory of your own and it matches that too, with the same
  discipline.
- It never messages anyone, never books anything, and never claims someone is
  good at this — only that this is what the record shows.

**Watch for:** the pool has changed from the LegalQuants community directory to
the people your tenant can already see. The silent failure is three plausible
colleagues padded to three because you asked for three: a person with no
quotable document behind them is a defect. What Enterprise Search actually
returns for a "who here has worked on X" question is probe **P14** and it is
unrun — a tenant with thin indexing may return nothing useful, and saying so
plainly is the correct outcome, not a failure.

### lq-reflect

*red · tier 3 · companion*

**Prepare:** do a real piece of work first, in the same conversation — ask Cowork
to draft or analyse something synthetic and go back and forth a few times.
Optionally, a dated review note from a previous run.

**Prompt:** `That was harder than it should have been. What would you do differently?`

**Pass:**

- It says what this review is before anything else, and lists what it is about to
  read, by name, before any finding.
- Three short items: one thing you did well, one concrete change to try, and why
  that change helps your actual work — **each anchored in something you actually
  typed**.
- Where it can quote you it quotes you; where it is reconstructing, it says "as I
  understand it, you asked…" and uses no quotation marks. A moment with no quote
  is dropped rather than padded.
- One change to keep, written out with a countable signature, saved as a short
  dated note in the Output folder and named — and it tells you to bring that note
  back next time so it can check whether the change held.
- Ask for "the last seven days" and it tells you in one line that it reviews the
  work in front of you, and what to attach if you want more.

**Watch for:** upstream this read your own past sessions across a window, with a
consent architecture built on hashes and previews. None of that exists here, and
the failure is the worst in the set: asked "how did that go?", a model will
produce a fluent account of a session with quotes that read like quotes whether
or not it can see anything. Probe **P11** is what settles it. Treat any
verbatim-looking quote you did not type as a defect and report it with the exact
wording. It must not claim a window, a scan, a manifest or a hash, and it must
stay on the piece of work rather than drifting into `lq-mirror`'s ground.

### lq-apply

*red · tier 3 · companion*

**Prepare:** nothing required. Optionally, a short invented note listing two or
three things you have built or run with AI.

**Prompt:** `Help me write up what I've actually done with AI.`

**Pass:**

- The first line says it is not connected to any application or assessment.
- It asks what to draw on, in order, starting with anything you have kept and
  ending with just talking to it — and it asks for files, never offering to take
  a folder.
- An **inventory of what it read**, shown before it writes anything.
- One or two questions about work it suspects is missing.
- A one-page legal-AI CV or a profile in which every line traces to something you
  confirmed, with declared kept apart from inferred, and attribution separated:
  built, co-built, forked, tested, deployed.
- The gaps as a short list in plain words — and it refuses to fill them however
  you ask, including when you say everyone exaggerates.
- The draft saved as a named file, the private evidence notes in a second one,
  and nothing submitted anywhere.

**Watch for:** upstream's artifact existed to be submitted, and the destination
is gone: there is no application format here, only a CV and a profile. A public
handle is reported as you gave it, never verified — a claim to have read or
checked a profile is a defect. The silent failure is a thin draft that looks
complete because an evidence file was not found, which is why it names the file
it looked for. Watch the boundary with `writing`, which drafts documents, and
`lq-mirror`, which gives a reading rather than an artifact.

### my-lq-moment

*red · tier 2 · companion*

**Prepare:** do a real piece of work first, in the same conversation — something
with a before, a move and a result you can check.

**Prompt:** `Was that actually impressive, or am I flattering myself?`

**Pass:**

- It explains what it is about to do and states the training exclusion up front.
- An explicit consent gate: may it inspect and assess only the work evidence in
  this current session?
- Then either a plain **insufficient evidence** outcome ending in refusal — never
  a lower bar — or a private write-up in five parts: Before, Move, Result, Check,
  Takeaway, with every claim tied to something in the session.
- Only if you want it: a LinkedIn post in your own voice, and a cover card that
  opens in the preview pane with two short sentences on it, which you export as
  an image yourself.
- Where it shortens a sentence to fit, it shows you the shortened sentence and
  says it did.
- A practice example is labelled as one everywhere.
- Nothing is posted and nothing is kept. If one line is worth keeping, it hands
  you the exact line for your own file.

**Watch for:** the cover used to be rendered by a bundled script over a packaged
template image. Here it is an HTML card, and until probe **P7b** comes back it
may arrive as a plain styled card with no template image — the skill should say
which form it produced. It must never draw the image itself, ask an image model,
or claim a PNG exists. What decides whether this skill is useful at all is what
it can see of its own session (probe **P11**): if Cowork exposes little, the
honest answer is *insufficient evidence* every time, which is loudly useless
rather than quietly wrong. A moment awarded on a session it could not actually
see is the defect to report.

## Part C — how to report

**One report per result.** Use the
[UAT report form](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml):
it asks for the report type (routing pass, routing misfire, behaviour pass,
behaviour defect), the bundle, the skill, the package version, the date, your
Cowork client if you know it, the prompt you typed, the files you attached, what
you expected, what happened, and an excerpt of the reply.

Passes are worth reporting too. A skill with four routing passes and a clean
behaviour run is a skill that can come off the status board, and that is the
whole point of the exercise.

If you claimed a
[help wanted issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22),
you can tick its checklist in a comment instead of filing separate reports —
whichever is less work. Just make sure a misfire ends up somewhere with the
exact prompt attached.

**Sanitise everything.**

- Never paste client material, matter names, party names, file names from a real
  matter, or anything from a live system. Not in an issue, not in a screenshot,
  not in an attached file.
- The tests above are built entirely on invented documents for this reason. If
  you tested with something real because it was to hand, **retype the finding
  with invented facts** before filing it, or describe the shape of the problem
  without the content.
- Trim reply excerpts to what shows the problem — a few lines. Do not paste an
  entire generated report.
- Screenshots: check the side panel, the file list, the tenant name and the
  window title before attaching. Crop hard.
- If you are unsure whether something is safe to post, describe it instead of
  pasting it, and say that is what you did.

The package version is in the release name, in `build-report.md`, and in the
`version` field of `manifest.json` inside the zip. For v0.2.0 it is `0.2.0`.

## Part D — what happens to your report

**A misfire is a description problem.** Cowork routes on a skill's
`description` and nothing else — no invocation grammar, no keywords, no
routing table. So when the wrong skill answers, the fix is not code:

1. The report is triaged against the card, `skills/<name>/skill.yaml`.
2. The fix is an edit to that card: sharpen the trigger phrases in
   `description`, add the missing hand-off sentence ("Do not use for X (use the
   Y skill)"), or adjust the neighbouring skill that took the work instead.
3. Your prompt is added to that card's `triggers`, so the regression is recorded
   and shows up in the generated trigger tests from then on.
4. A pull request runs `make package`; the change appears in
   `dist/<bundle>-trigger-tests.md` and the build report.
5. It ships in the next release, and the issue closes referencing it.

**A behaviour defect** is triaged the same way but usually lands one layer
deeper: a section overlay or a patch in `skills/<name>/`, with the card's
`notes` updated to record what changed and why. Where the defect turns out to be
upstream's rather than the adaptation's, it is recorded in the card's `notes` and
reported upstream instead — this repository does not edit `upstream/`.

Either way you will see the fix: the issue links the commit, the release notes
name the skill, and the status board below moves.

## Part E — capability probes

Parts A and B ask whether a skill works. These ask what **Cowork** can do, and
they are the most valuable thing in this document. Fourteen questions sit
behind the thirty-one cards, each one a thing a card would like to rely on and
cannot, because Microsoft's documentation does not answer it. A single result
moves a skill's risk tier: P3 releases `read-redline` from the degrade it ships
with, P9 settles the workbook pattern that four skills carry their state in,
P11 decides whether `lq-reflect` and `my-lq-moment` can do their central step at
all, and P14 decides whether `lq-connect` has a pool to search.

`probes.yaml` at the repository root is the source for everything below — the
same file the build report, the site and the issue renderer read — so if this
page and that file ever disagree, the file wins. The
[site](https://houfu.github.io/lq-plugin-cowork/probes.html) renders the same
fourteen. Each probe has, or will have, its own issue labelled `uat` and
`probe`; claim one in a comment the way you would claim a skill.

**How to run one.**

1. **One fresh conversation per probe**, synthetic files only. Where a probe
   needs two sessions on different days, that is part of the probe and not an
   inconvenience to work around.
2. **Type the prompt exactly as written.** These are worded to make a fake
   answer visible, and a paraphrase can lose that.
3. **Record the tenant's posture** with every report: which Cowork client you
   used, whether web search is on, and — for browser use — whether an admin had
   to enable it first, since it is disabled by default. A tenant where the
   admin declines is a reportable result, not a failed run.
4. **Read "worst outcome" before you run it.** For most of these the dangerous
   result is not a refusal but a confident answer with nothing behind it. If
   you get one, say so in those words and paste what it said.
5. Two probes need a throwaway probe package rather than a shipped bundle (P1
   and the P7b arm). P7a needs nothing: it runs against the `legaldesign` skill
   that ships today, which is why it is the one to run first.

**One standing check that is not a probe.** On any run, note **the exact names
of the built-in skills your tenant actually offers**, as they appear in the side
panel and the Sources picker, and report the list verbatim. That settles by
observation something this repository cannot settle by argument: Microsoft's
Cowork pages name "Deep Research" as a built-in while a consumer-plan support
page announces its retirement in favour of "Researcher", and those appear to be
two features sharing a name. Nothing here gets renamed on the strength of a
page about a different plan — only on a tester seeing a different name in a
real tenant.

### P1 — Does a bundled script actually run, and in what?

**Settles:** Whether a script packaged inside a skill is executed at all, and
what interpreter and libraries it would run under. Nothing ships with a script
under the no-scripts policy, so a result changes no tier; it is the input to
the maintainer's decision about that policy and to the original, not
re-scoped, paths of closing-bible, definition-check and read-redline.

**Setup:** Cannot be run from the released bundles, because no shipped skill
contains a script. Needs a throwaway single-skill probe package containing
scripts/probe.py, which prints one line naming sys.version,
platform.platform(), whether pypdf, pdfplumber, docx, openpyxl and PIL import,
and whether soffice, pdftoppm and tesseract are on the path. The SKILL.md says
to run it and report its output verbatim.

**Prompt:**

> Run the environment probe and show me its output exactly as printed.

**Pass:** The reply contains the fingerprint line with a real Python version
string.

**Fail:** A reply that paraphrases the script, describes what it would print,
or reports the script's contents as instructions.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** no tier directly. It settles a question the cards are written
around rather than one they wait on, and a result still changes what they can
offer.

### P2 — Does a file written in one session come back in the next?

**Settles:** Whether state written to the Cowork folder is reachable from a
later session without the lawyer attaching it. No tier turns on it, by design:
every cross-session design brings its own state instead. It is an ergonomics
upgrade for sigpack's ledger, regulatory's refresh baseline, legalquants step
3b, lq-reflect step 8b and lq-apply step 2b.

**Setup:** None beyond two sessions on different days.

**Prompts:**

- Session 1: Create a file called probe-ledger.json in my Cowork Output folder
  containing exactly {"probe":"lqc","n":1} and tell me where you put it.
- A new session on a later day, with nothing attached: Open probe-ledger.json
  from my Cowork folder, tell me what n is, then save it back with n increased
  by one.

**Pass:** It finds the file without the tester attaching it, reports n as 1,
writes 2 — and a third session reads 2.

**Fail:** It cannot find the file, or asks the tester to attach it.

**Worst outcome:** a **refusal**, which is the safe shape. Record it plainly,
and watch for the dangerous variant where it answers without having read
anything.

**Unlocks:** no tier directly. It settles a question the cards are written
around rather than one they wait on, and a result still changes what they can
offer.

### P3 — Does Cowork report tracked changes in a Word document?

**Settles:** Whether Cowork can see tracked insertions, deletions and comments
in a Word document at all, and whether it returns an honest nil on a clean
copy. Word tracked changes are nowhere mentioned in Microsoft's pages.

**Setup:** A two-page synthetic DOCX with tracked insertions and deletions by
two named authors and one comment; plus a clean copy of the same file with the
changes accepted.

**Prompt:**

> List every tracked change in this agreement: the exact inserted and deleted
> text, who made it, and where it sits. Tell me if there are none.

**Pass:** Insertions and deletions listed separately with authors, and the
comment noted; and, on the clean copy, it says there are none rather than
inventing some.

**Fail:** It reads the document as though the changes had been accepted and
reports no changes.

**Worst outcome:** **silent** — a wrong result that looks exactly like a right
one. Check the artifact, not the reply.

**Unlocks:** `read-redline`, `playbook-review`.

### P4 — Can Cowork tell what is on a page?

**Settles:** Whether Cowork can say, page by page, what a PDF carries —
strikethrough and underline, handwriting and signatures, and whether a page is
scanned rather than typed. OCR, scanned PDFs and handwriting are nowhere
mentioned.

**Setup:** A four-page synthetic PDF: page 2 carries redline markup
(strikethrough and underline), page 3 is a scanned image of a signature block
signed over a printed name, page 4 is clean.

**Prompt:**

> Go through this PDF page by page. For each page tell me whether anything is
> struck through or underlined, whether there is handwriting or a signature,
> and whether the page is scanned rather than typed.

**Pass:** Correct per-page answers, including that page 3 is an image and is
signed, without being told.

**Fail:** It describes pages it cannot see, or reports the scanned page as
blank or as text.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** `read-redline`, `diligence`, `docreview`, `closing-bible`,
`regulatory`, `sigpack`.

### P5 — What does a resumed task remember?

**Settles:** What re-enters the model's context when a task is resumed, and
whether a brand-new task can see the previous one. The mechanism of
continuation is documented; what it carries is not. No tier turns on it: it
bounds lq-reflect's week-wide alternative.

**Setup:** Two sessions plus one resumption, over two days.

**Prompts:**

- Session 1: Remember this reference for later: ALDERNEY-7. Draft me two lines
  about anything.
- Resuming that task from the task list the next day: What was the reference I
  gave you?
- Then, in a brand-new task: What did I ask you in my previous Cowork task?

**Pass:** The resumed task returns ALDERNEY-7 unprompted; the new task does
not know.

**Fail:** The resumed task does not have it, or — the bigger finding — the new
task does.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** no tier directly. It settles a question the cards are written
around rather than one they wait on, and a result still changes what they can
offer.

### P6 — Is web search on in this tenant, and what comes back?

**Settles:** Whether web search is enabled here, and whether what comes back
is a page address the lawyer can check or a rendering they cannot. It confirms
a limit rather than lifting one, and informs lq-ask's optional step and
regulatory's locator-only use of search.

**Prompt:**

> Search the web and quote me, word for word, the opening sentence of the
> official text you find at legislation.gov.uk for the Bribery Act 2010
> section 1, and give me the address of the page you read.

**Pass:** A URL and a quotation, plus whatever the client says about web
search.

**Fail:** A refusal naming a disabled web-search setting — which is an equally
useful result and should be reported with the tenant's admin posture if known.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** no tier directly. It settles a question the cards are written
around rather than one they wait on, and a result still changes what they can
offer.

### P7 — Can a skill's output carry a file that shipped with the skill?

**Settles:** Whether a companion file packaged inside a skill reaches
something the lawyer receives. Carrying the asset is documented; reaching an
output is not. Two arms, one probe: P7a a text or HTML template, P7b a bundled
binary image. P7a is free today and should be the first probe the programme
runs.

**Setup:** P7a: none; run it against the shipped legaldesign skill, which
carries HTML templates as companions. P7b: package a probe skill carrying a
small PNG and an HTML template that references it.

**Prompts:**

- P7a: Turn the attached advice note into a one-pager using your supplied
  template, and tell me which of your template files you used.
- P7b: Build the card from your supplied template and tell me which of your
  packaged files it used.

**Pass:** P7a: the produced HTML visibly uses the packaged template's
structure and the reply names the companion file. P7b: the rendered page shows
the image and the reply names the file.

**Fail:** P7a: generic HTML, or a named file that was not used. P7b, recorded
separately: the page renders without the image, or the reply claims an image
that is not there.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** `my-lq-moment`, `read-redline`, `docreview`, `definition-check`.

### P8 — Can Cowork build a PDF out of chosen pages of supplied PDFs?

**Settles:** Whether Cowork can assemble a new PDF from chosen pages of
supplied ones. Merging or splitting PDFs is nowhere mentioned, and the PDF
built-in's entire description is the single line "Work with PDF documents".

**Setup:** Two synthetic four-page PDFs with distinguishable page content.

**Prompt:**

> Make me one new PDF containing page 3 of the first document and pages 1 and
> 2 of the second, in that order, and tell me how many pages it has.

**Pass:** A downloadable PDF in the Output folder with exactly those three
pages in that order and their content intact.

**Fail:** A reply that describes the pages instead of producing the file, or a
PDF with the wrong pages or order.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** `sigpack`, `closing-bible`.

### P9 — Does an Excel workbook survive a round trip with its arithmetic intact?

**Settles:** Whether a workbook's structure and formulas survive being handed
back and forth. The round trip itself is documented; whether the arithmetic
survives is not. After P3, the probe with the widest reach in the
document-pipeline half.

**Setup:** None; two sessions.

**Prompts:**

- Session 1: Build me a tracker workbook with columns Document, Issue, Status,
  Quote, Locator and these six rows, and add a row at the bottom that counts
  how many rows are filled.
- A fresh session with the returned workbook attached: Add these four
  documents as new rows, fill the Status column for them, and give the
  workbook back to me unchanged apart from the new rows.

**Pass:** The returned file keeps the original six rows, the column order, the
count formula as a formula, and its recalculated value.

**Fail:** Rows dropped or reordered, columns renamed, or the count arriving as
a hard-coded number rather than a live formula.

**Worst outcome:** **silent** — a wrong result that looks exactly like a right
one. Check the artifact, not the reply.

**Unlocks:** `diligence`, `docreview`, `closing-bible`, `definition-check`,
`sigpack`.

### P10 — Can Cowork produce a Word document carrying real tracked changes?

**Settles:** Whether Cowork can write a Word file whose edits are recorded as
tracked changes rather than applied as plain text. Producing a Word document
with tracked changes or comments is nowhere stated. Neither dependent step is
load-bearing; both improve.

**Setup:** A short supplied agreement clause.

**Prompt:**

> Give me back this clause as a Word document with my three edits recorded as
> tracked changes attributed to "Review", not as plain edited text.

**Pass:** Opening the file in Word shows insertions and deletions in the
review pane.

**Fail:** A document with the edits applied as plain text, or coloured text
that is not a tracked change.

**Worst outcome:** **loud** — you will see it fail, which makes this the
comfortable kind of probe.

**Unlocks:** `read-redline`, `conform`.

### P11 — What can a skill see and quote of its own session?

**Settles:** Whether a skill can quote the lawyer's own words back verbatim,
list the files created and list the skills and tools used, and whether it says
honestly which of those it is reading and which it is reconstructing. A
refusal blocks nothing: it forces every quote to come from an attached file.

**Setup:** In one conversation, do some work first: type a distinctive
sentence, have a file created, invoke a second skill.

**Prompt:**

> Quote back, word for word, the sentence I typed at the start of this
> session; list the files created in this session; and list the skills and
> tools used. Say for each whether you are reading it or reconstructing it.

**Pass:** A verbatim quote, the correct file list, the correct skill and tool
list, each with honest attribution.

**Fail:** Two distinguishable ways: a refusal (usable — the cards adapt around
it) or a fluent paraphrase presented as a quote.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** `lq-reflect`, `my-lq-moment`.

### P12 — Browser use: does what it reads reach the skill?

**Settles:** Two things. (a) Availability: is browser use enabled in this
tenant, and what did it take to enable it — it needs Edge, runs only in Cowork
on the web, and is disabled by default until an admin turns it on. (b)
Quotability: does page content or a downloaded file become something the
session, and therefore a skill, can quote. No design depends on it.

**Setup:** Cowork on the web in Microsoft Edge, on a device where Edge is
installed, in a tenant where an admin has performed the enable steps. Record
what the posture was before the tester asked, who had to act, and the tenant's
DLP and site-blocking posture. A tenant where the admin declines is a
reportable result, not a failed run.

**Prompt:**

> Open the page at <public URL> and quote its first heading and the first
> sentence under it. Tell me how you retrieved it, and tell me whether that
> page is now one of my session files.

**Pass:** The quote comes back, Cowork names the route, and it states plainly
whether the content is now a session file.

**Fail:** The content comes back as a summary rather than quotable text; or a
refusal citing a blocked site (still a useful result — record it with the
posture).

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** `lq-connect`, `lq-apply`, `lq-ask`.

### P13 — Can a scheduled run work over files placed earlier?

**Settles:** Whether an automated run can read files the lawyer placed
earlier, write outputs, and load a custom skill. The scheduling machinery is
documented; what a run can reach is not. No card is built on it; any of them
may offer a cadence as a closing line, and must name the twenty-five
scheduled-prompt cap when they do.

**Setup:** A file already sitting in the Cowork folder, and a custom skill
installed.

**Prompt:**

> Every Monday at 9am, use the <name> skill on closing-register.xlsx in my
> Cowork folder and save the updated register back.

**Pass:** The Runs tab shows it ran; an output file appears; the output
reflects the placed file; and the run history shows the custom skill was
loaded.

**Fail:** The schedule exists but the skill is not invoked, or nothing is
written, or the run reports success with no output.

**Worst outcome:** **silent** — a wrong result that looks exactly like a right
one. Check the artifact, not the reply.

**Unlocks:** no tier directly. It settles a question the cards are written
around rather than one they wait on, and a result still changes what they can
offer.

### P14 — Enterprise Search as a people finder

**Settles:** Whether Enterprise Search can answer who in the organisation has
worked on a topic, with a quotable document behind each name. Microsoft's
whole statement about it is the line "Enterprise Search Search across your
organization".

**Setup:** A tenant with real internal material behind the chosen topic.

**Prompt:**

> Who in my organisation has worked on <a topic with real internal material
> behind it>? Name up to three people and, for each, quote the document that
> shows it.

**Pass:** Named people, each with a quotable document.

**Fail:** Documents with no people attached, or names with nothing behind
them.

**Worst outcome:** a **fluent fake** — a confident answer with nothing behind
it. That is worse than a refusal, and it is a separate result: record it with
the exact wording.

**Unlocks:** `lq-connect`.

## Status board

Updated from closed UAT issues; the pinned [status board](https://github.com/houfu/lq-plugin-cowork/issues/18) links every skill issue, and the probe issues — labelled `uat` and `probe` — sit beside them. Every cell starts at **not tested**, and that is
an honest description of where this project is.

| Bundle | Skill | Routing | Behaviour |
| --- | --- | --- | --- |
| litigation | `legaldesign` | not tested | not tested |
| litigation | `lq-start` | not tested | not tested |
| litigation | `regulatory` | not tested | not tested |
| litigation | `timenarratives` | not tested | not tested |
| litigation | `wiki` | not tested | not tested |
| litigation | `cite-check` | not tested | not tested |
| litigation | `client-update` | not tested | not tested |
| litigation | `correspondence` | not tested | not tested |
| litigation | `depositions` | not tested | not tested |
| litigation | `docreview` | not tested | not tested |
| litigation | `document-discovery` | not tested | not tested |
| litigation | `new-matter` | not tested | not tested |
| litigation | `organize-case-docs` | not tested | not tested |
| litigation | `pressuretest` | not tested | not tested |
| litigation | `writing` | not tested | not tested |
| transactional | `legaldesign` | not tested | not tested |
| transactional | `lq-start` | not tested | not tested |
| transactional | `regulatory` | not tested | not tested |
| transactional | `timenarratives` | not tested | not tested |
| transactional | `wiki` | not tested | not tested |
| transactional | `closing-bible` | not tested | not tested |
| transactional | `closing-checklist` | not tested | not tested |
| transactional | `conform` | not tested | not tested |
| transactional | `definition-check` | not tested | not tested |
| transactional | `diligence` | not tested | not tested |
| transactional | `playbook-builder` | not tested | not tested |
| transactional | `playbook-review` | not tested | not tested |
| transactional | `read-redline` | not tested | not tested |
| transactional | `sigpack` | not tested | not tested |
| companion | `legalquants` | not tested | not tested |
| companion | `lq-apply` | not tested | not tested |
| companion | `lq-ask` | not tested | not tested |
| companion | `lq-connect` | not tested | not tested |
| companion | `lq-mirror` | not tested | not tested |
| companion | `lq-reflect` | not tested | not tested |
| companion | `my-lq-moment` | not tested | not tested |
| companion | `lq-start` | not tested | not tested |

A skill is marked **passed** for routing when all of its trigger-test rows
have been run and recorded in one tenant, and **passed** for behaviour when its
smoke test above has been run with a result of pass. Anything else — partial
runs, mixed results, a pass in one tenant and a misfire in another — stays open
with the detail in the issue, because "it worked for me" is not a status.

The fourteen capability probes have their own board, and a probe is the only
thing here that can move a skill's tier. One result, in one tenant, recorded
honestly, is enough to change what this repository ships.

| Probe | Result |
| --- | --- |
| `P1` | not run |
| `P2` | not run |
| `P3` | not run |
| `P4` | not run |
| `P5` | not run |
| `P6` | not run |
| `P7` | not run |
| `P8` | not run |
| `P9` | not run |
| `P10` | not run |
| `P11` | not run |
| `P12` | not run |
| `P13` | not run |
| `P14` | not run |

A probe is marked **run** when its result has been recorded in one tenant with
the tenant's posture stated — client, web search, browser use. Two tenants
disagreeing is a finding in itself and both stay on the board.
