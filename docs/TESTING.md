# Acceptance testing: the tester programme

Nothing in this repository has been run in a live Microsoft 365 Copilot Cowork
tenant. The packages build, validate and ship reproducibly; the skill content has
been read line by line against what Cowork can do. Whether any of it *works* —
whether the right skill activates from an ordinary sentence, and whether it then
does what its description promises — is unknown, and the maintainer has no
Copilot capacity to find out.

That is what this programme is for. It has two halves:

- **Part A — routing.** Does the right skill activate? Run from the generated
  `dist/<bundle>-trigger-tests.md` (attached to every
  [release](https://github.com/houfu/lq-plugin-cowork/releases/latest)).
- **Part B — behaviour.** Does the skill then produce what it says it produces?
  One smoke test per shipped skill, below.

Both are recorded the same way: one
[UAT report](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml)
per result, and one open
[help wanted issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
per skill to claim.

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
| `legalquants-litigation-cowork` | 15 | You work in disputes, or you want the widest coverage: nine skills are litigation-only. |
| `legalquants-transactional-cowork` | 8 | You work on deals, or you want the shorter run: playbooks and closing checklists. |

Six skills ship in **both** bundles (`lq-start`, `legaldesign`,
`timenarratives`, `wiki`, `closing-checklist`, `lq-mirror`). Test each of them
once, in whichever bundle you installed, and say which bundle in the report.

If you install both at once, say so in every report: two enabled plugins
contributing six identically-named skills is untested ground, and how Cowork
handles it is itself a finding.

## Part A — routing tests

Cowork picks a skill from its `description` and nothing else. The routing tests
are generated from each card's `triggers`: four prompts that must activate the
skill, and four adjacent prompts that must not, each naming the skill that
should take it instead.

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
- **The closing line.** `lq-start` and `lq-mirror` — and only those two — are
  instructed to end every reply with, exactly: *"LegalQuants skills are a
  workflow aid, not legal advice. The judgement stays yours."* If you see that
  line, one of those two ran. Its **absence proves nothing** about the other
  fifteen: they carry no such instruction.
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

A note on the colour: **green** skills needed little adaptation and are close to
upstream. **Amber** skills lost machinery — scripts, schemas, validators,
local applications — and had that machinery replaced with instructions. Amber is
where the risk is. Eleven of the seventeen are amber.

Start a fresh conversation for each test. Put prepared files in the session's
Input folder or attach them; either is fine, but say which you did.

### lq-start

*amber · both bundles · no files needed*

**Prompt:** `What can you actually do here? Give me the map.`

**Pass:**

- It renders the whole map of **both** bundles, with every entry labelled with
  the bundle it belongs to — not just the one you installed.
- Exactly one neutral sentence says that a skill responds only if its bundle is
  available in the tenant, and that plugin availability is managed by the
  Microsoft 365 administrator.
- It routes and does not do the work: asked to draft something, it declines in a
  line and names the skill instead.
- The reply ends with the fixed closing line, unchanged.

**Watch for:** this is a full-file overlay — every word is this repository's, not
upstream's. It must not claim to know which bundle is installed, must not claim
a typed `/` skill menu (deliberate choice is the conversation's Sources picker),
and must not name any skill outside the map — `docreview`, `lq-ask`,
`diligence` and the other eleven left-out skills do not exist here.

### lq-mirror

*amber · both bundles · no files needed*

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

*amber · both bundles*

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

*amber · both bundles*

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

*amber · both bundles*

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

### closing-checklist

*green · both bundles*

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

*green · litigation*

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

*green · litigation*

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

*green · litigation*

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

*green · litigation*

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

*green · litigation*

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

*green · litigation*

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

*amber · litigation*

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

*amber · litigation*

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

*amber · litigation*

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

### playbook-builder

*amber · transactional*

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

*amber · transactional*

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
`version` field of `manifest.json` inside the zip. For v0.1.0 it is `0.1.0`.

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

## Status board

Updated from closed UAT issues; the pinned [status board](https://github.com/houfu/lq-plugin-cowork/issues/18) links every skill issue. Every cell starts at **not tested**, and that is
an honest description of where this project is.

| Bundle | Skill | Routing | Behaviour |
| --- | --- | --- | --- |
| litigation | `lq-start` | not tested | not tested |
| litigation | `writing` | not tested | not tested |
| litigation | `correspondence` | not tested | not tested |
| litigation | `client-update` | not tested | not tested |
| litigation | `depositions` | not tested | not tested |
| litigation | `new-matter` | not tested | not tested |
| litigation | `organize-case-docs` | not tested | not tested |
| litigation | `cite-check` | not tested | not tested |
| litigation | `pressuretest` | not tested | not tested |
| litigation | `document-discovery` | not tested | not tested |
| litigation | `legaldesign` | not tested | not tested |
| litigation | `timenarratives` | not tested | not tested |
| litigation | `wiki` | not tested | not tested |
| litigation | `closing-checklist` | not tested | not tested |
| litigation | `lq-mirror` | not tested | not tested |
| transactional | `lq-start` | not tested | not tested |
| transactional | `closing-checklist` | not tested | not tested |
| transactional | `playbook-builder` | not tested | not tested |
| transactional | `playbook-review` | not tested | not tested |
| transactional | `legaldesign` | not tested | not tested |
| transactional | `timenarratives` | not tested | not tested |
| transactional | `wiki` | not tested | not tested |
| transactional | `lq-mirror` | not tested | not tested |

A skill is marked **passed** for routing when all eight of its trigger-test rows
have been run and recorded in one tenant, and **passed** for behaviour when its
smoke test above has been run with a result of pass. Anything else — partial
runs, mixed results, a pass in one tenant and a misfire in another — stays open
with the detail in the issue, because "it worked for me" is not a status.
