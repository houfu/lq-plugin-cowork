# Cowork-native alternatives and risk: companion skills

19 September 2026

Six companion skills were excluded from the Cowork bundles: `legalquants`, `lq-ask`, `lq-connect`,
`lq-reflect`, `lq-apply`, `my-lq-moment`. This paper does not ask whether they should stay out. It
asks, for each one, what the nearest thing Cowork can actually do looks like, what every step of that
thing rests on, how likely it is not to work, how it would fail, what the lawyer loses, and which
probe would settle the remaining doubt. Every skill gets a recommended tier and the conditions
attached to it. None gets "stay out".

The seventh companion skill, `lq-mirror`, already shipped. It is the worked example: the same surgery
this paper designs five more times was performed on it once, in public, and the card is in the tree at
`skills/lq-mirror/skill.yaml`. Its moves are set out below before the catalogue, because every
alternative here is built out of them.

## How to read this

**Evidence letters.** Every substitute step carries one.

- **D** — documented. Microsoft documents the capability, or the repo already ships a skill that does
  exactly this.
- **U** — undocumented but not denied. Nothing in the record says Cowork can; nothing says it cannot.
  A probe settles it.
- **C** — contested or unspecified. Microsoft's own pages disagree, or the capability exists but
  nothing says a skill can address it, or what comes back is unspecified.
- **X** — documented absent, or forbidden by the skill's own text.

**Capability risk** is the worst letter on a load-bearing step: Low (all D), Medium (a U), High (a C
or X). A step is load-bearing if the alternative is not worth shipping when that step fails.

**Fidelity** is one of: Same deliverable / Same deliverable with a disclosed weaker guarantee /
Different deliverable / Core promise not deliverable. The last one is reserved for cases where the
skill's own text says a version without the missing thing is unacceptable, and it forces a re-scoped
skill with a changed promise and preferably a changed name.

**Failure mode** is Loud or Silent, per U or C step. Loud means the lawyer sees it fail. Silent means
they get a plausible answer that is not backed by what it claims. Every silent mode is given the
mitigation that turns it loud, because a silent failure in a legal skill is the thing this repository
exists to avoid.

**Tiers.** Tier 1: ship on documented capabilities only, with loud failures. Tier 2: ship after one
named probe passes, or ship now with an announced degrade. Tier 3: a re-scoped skill with a changed
promise — worth shipping only if that promise is worth having. Tier 4: needs a remote MCP connector
for a load-bearing step.

**Probes.** P1 script runtime fingerprint. P2 write then read back across sessions. P3 tracked changes
in DOCX. P4 page inspection including scans. P5 resumed-session memory. P6 web search availability and
provenance. P7 companion asset in output. This paper adds five, defined where they first bite and
collected at the end: P8 bundled binary asset in an output file; P9 what a skill can see and quote of
its own session; P10 browser use, tenant posture and skill-initiated navigation; P11 a scheduled task
running a custom skill over placed files; P12 Enterprise Search as a people finder.

**Citation convention.** "lq-reflect Q4" means quote 4 in that skill's section of
`docs/research/supporting/excluded-skills-profiles-companion.md`; numbering restarts per skill. Where
a line matters and the profile did not number it, it is quoted and attributed to its heading in the
upstream `SKILL.md`. "LM1" etc. are the lq-mirror quotes reproduced in that document.

**Policy and capability are kept apart.** Where an alternative is blocked by `docs/CONTRACT.md`
section 8 rather than by Cowork, it is said so in its own sentence. The maintainer can change policy;
nobody in this repository can change capability. One precision that matters for four of the six
skills: the build's own external-URL rule, `LQC-W010`, is a **warning**, not an error, and it exempts
"a URL that occurs anywhere in the upstream skill folder, in any file". Every LegalQuants URL in these
six skills is upstream-authored, so the validator would let them through. What blocks them is the
section 8 sentence "No shipped skill links to an external site, sign-up, assessment or product" —
policy alone, changeable by the maintainer without touching the build.

---

## The lq-mirror surgery, as the template

Four moves, all visible in `skills/lq-mirror/skill.yaml`. They recur in every alternative below.

1. **Delete the first-run marker section outright.** `sections: - match: '## First run? One marker,
   once ever'  delete: true`. All six of the excluded skills open with that section and all six call
   `../legalquants/scripts/onboarding.py`. It goes the same way each time.
2. **Replace the store write with "show it; they keep it".** The upstream step offered to save through
   `profile_store.py`; the card replaced it with "Show the summary in the reply itself, as a few short
   paragraphs they can copy; do not put it in a file and do not save anything on their behalf", and
   then said the quiet part in the skill's own voice: "This skill stores nothing itself; the
   conversation persists like any other Cowork session."
3. **Replace the external door with a one-line, once, honest refusal.** The assessment link became
   "say in one line, once, that there is a formal observed one and that it is not this, and that you
   cannot take them to it from here".
4. **Replace the catalogue call with what is visibly in the room.** The ending now says: "Choose it
   from the LegalQuants skills actually offered in this session — never from memory. If you cannot
   tell what is available, or nothing fits what they described, say so plainly and point them at the
   lq-start skill."

Plus the two mechanical ones: the `/name` title line was rewritten to a plain English heading, and the
"CODEX for Legal" sign-off became "LegalQuants skills are a workflow aid, not legal advice. The
judgement stays yours."

What lq-mirror did **not** have to solve is the thing the other six turn on: it needs no evidence it
cannot see. "Everything here is self-report. You read no transcripts, no sessions, no files" (LM1),
and "The reading is complete even if saving is declined" (LM2). The surgery was cheap because the
skill was already complete without the machinery. The five surgeries below are expensive in exactly
the proportion that their skills are not.

---

## Substitution pattern catalogue

Fourteen patterns. Each says what it is, what it substitutes for, its evidence letter, the probe that
settles it, its failure mode, and which of the fourteen excluded skills use it. Pipeline skills are
named where the use is obvious; the pipeline half of this analysis is a separate paper.

### S1. The private store, four ways

**Substitutes for:** `~/.lq/profile.json`, `journey.jsonl`, `scan_state.json`, `state.json`, the
`onboarding.json` marker — everything upstream keeps on the lawyer's own disk between runs.

- **S1a — a named file in the Output folder.** The skill writes `lq-journey-2026-09-19.md` (or
  `.json`) and says where it is. **Write: D** — "You can also access files that Cowork creates
  directly in your OneDrive Cowork folder at any time." **Read it back next session without the
  lawyer attaching it: U** — nothing documents it, nothing denies it. **Probe: P2.** **Failure mode:
  Silent** if a card assumes the read-back and the file quietly is not there, because the model will
  carry on from an empty state and sound exactly as confident. **Mitigation:** the card must state
  the file it expected and what it did not find, in the reply, before it does anything else. **Used
  by:** lq-reflect (the debrief note), lq-apply (the evidence file), legalquants (the journey note),
  my-lq-moment (assets only). Pipeline: sigpack's ledger, regulatory's refresh baseline, conform's
  hash-matched ledger, closing-bible's receipt.
- **S1b — bring your own state.** The lawyer attaches the state file at the start of each session.
  **D**, and not theoretical: `playbook-review` ships this today — "Require an approved playbook: the
  `playbook.md` a build produced, or one the lawyer supplies in the same shape... There is no library
  to search and no registry to discover; if the lawyer does not know where theirs is, ask them to
  point at the folder." Paired with S1a it gives a genuine cross-session loop with no undocumented
  step in it: one skill writes the file, the lawyer keeps it, the next session they attach it.
  **Failure mode: Loud** — a missing attachment is visible to both parties. **Used by:** lq-reflect,
  lq-apply, legalquants, and every pipeline skill that wanted a ledger.
- **S1c — `lqplaybook.md` as the carrier for confirmed preferences.** Per CONTRACT section 8 and the
  fourteen shipped cards that already do it (every skill in both bundles except `lq-start`, `lq-mirror`
  and `wiki`): read only confirmed `[skill-name]` entries from a playbook the lawyer attached or
  placed in the Input folder, never write it, and offer a discovered preference as one exact line they
  can add. **D.** It carries settled preferences well and a journey badly — it is a preferences file,
  not an event log, and widening its tag space to a new skill name is a contract edit, not a
  capability question. **Failure mode: Loud.** **Used by:** legalquants (the quoting posture, the
  declined move), lq-apply (format preference), lq-reflect (the one change in play, at a stretch),
  my-lq-moment (nothing kept, or one line offered).
- **S1d — an Excel workbook as the journey, via the Excel built-in.** **Produce: D.** **Update in
  place across sessions: U** (same question as S1a, plus whether an existing workbook can be edited
  rather than re-emitted). **Probe: P2.** **Failure mode: Silent** — a re-emitted workbook that drops
  earlier rows looks like a workbook. **Mitigation:** the skill prints the row count it read and the
  row count it wrote. **Used by:** lq-reflect, lq-apply. Pipeline: diligence and docreview's
  issue-by-document grid.

### S2. The Output folder as the working directory

**Substitutes for:** run directories, scratch paths, intermediates that upstream deletes.
**Evidence: D**, with one documented constraint — "Cowork can't delete files or folders in OneDrive or
SharePoint" — so nothing may be described as cleaned up. **Probe:** none needed. **Failure mode:
Loud** (the files are visibly there). **Used by:** all fourteen. Shipped precedent in cite-check,
legaldesign, closing-checklist, playbook-review, client-update, document-discovery and pressuretest,
each of which now says which working files remain and names them.

### S3. The script re-expressed as prose

**Substitutes for:** every bundled script whose job was deterministic bookkeeping or formatting rather
than computation the model cannot do. **Evidence: D** for the prose path itself; **C** for keeping the
script as an optional accelerator, because Microsoft's pages disagree about whether `scripts/` runs and
no page names an interpreter (**probe: P1**). Repo policy is that cards ship no scripts, revisited per
card only if P1 returns a named interpreter and package set reproduced in two tenants. **Failure mode
of the prose path: Silent** where the script enforced a rule the prose merely states — a refusal, a
length cap, a check. **Mitigation:** write the rule as a step with a visible output ("I shortened this
to nine words; here it is"), not as a background guarantee. **Used by:** all fourteen. Shipped
precedent: `wiki` (`wiki.py` became "read the delimited block out of the note itself and quote it
exactly"), `lq-start` (`catalog.py` became a static map), `legaldesign` (`scaffold.py` became "Build it
yourself, in this order, and do not skip a step because the next one looks close"), `playbook-builder`
("What replaces validation is reading").

### S4. Renderers

**Substitutes for:** PNG output from an SVG rasteriser shelling out to local binaries.

- An HTML page for the preview pane, built from a bundled template: **D** for HTML rendering; **U**
  for whether a bundled image asset actually appears in the output (**P7** for an HTML template,
  **P8** for a binary image).
- A slide via the PowerPoint built-in: **D**.
- The lawyer converts: **D**, and blessed by the skill's own text in the one case that needs it
  (my-lq-moment Q9).

**Failure mode: Silent and severe if the model draws the image itself or claims a PNG exists** —
my-lq-moment Q9 forbids both by name. **Mitigation:** carry Q9's prohibition into the adapted body
verbatim. **Used by:** my-lq-moment (the cover). Pipeline: sigpack (page images), read-redline (marks
on a page).

### S5. Network reach

**Substitutes for:** live fetches of a corpus, a member directory, a public site, a repository.

- A declared `agentConnectors` remote MCP server: **D** as a route (Streamable HTTP, JSON-RPC 2.0,
  OAuth or dynamic client registration, up to 10 per package, `copilot-cowork/1.0` on outbound
  requests). It is Tier 4 because somebody has to operate the server.
- A dated static snapshot shipped as companions: **D**, and stale by construction.
- Browser use reading a public page: **U in any given tenant** — Edge automation on the user's device,
  web client only, "disabled by default" until an admin enables it (**probe: P10**).
- Bing-backed web search: **C** — the article says it applies to Cowork, Cowork has no user toggle, an
  admin can disable it by name, and no page describes a web tool a skill can invoke (**probe: P6**).
- Bring your own page — the lawyer pastes or attaches it: **D**.

**Failure mode of the snapshot: Silent staleness.** **Mitigation:** the date is in the first line of
every answer and in the description, and the card is forbidden from claiming currency. **Failure mode
of search and browser use: mixed** — a refusal is loud, a confident answer sourced from a rendering
the lawyer cannot check is silent. **Mitigation:** name the route used and the fact that it is a
rendering, never bytes. **Used by:** lq-ask, lq-connect, lq-apply (the form fields), legalquants (the
Residency line). Pipeline: regulatory (which refuses a rendering by rule), cite-check (which ships
today and assumes a research surface).

### S6. Session transcripts across sessions

**Substitutes for:** reading the lawyer's own past AI sessions off disk over a window.

- The lawyer attaches previous sessions' Output files, or a running journey file they keep: **D**.
- A resumed task, where the current conversation is itself a past session: **U** — every Microsoft
  page describes resumption in UI terms and none says what re-enters the model's context (**probe:
  P5**, with **P7** on the same question).
- Current-session-only mode: **D** — "Plugin skills work within the current conversation context. They
  can read files you attached, reference earlier messages."
- The lawyer pastes what they remember: **D**.

**Failure mode: Silent** — a model asked about last week will produce a plausible account of last week
from the conversation it is in. This is the single most dangerous substitution in the set, because the
output looks identical whether the evidence existed or not. **Mitigation:** the card states the
evidence it actually read, by name, before any finding, and lq-reflect's own coverage discipline
("Coverage is always stated: the files read, their dates, messages omitted or shortened") is kept
verbatim rather than adapted. **Used by:** lq-reflect above all; my-lq-moment (current session only, by
design, not by degrade); legalquants (the counters).

### S7. The first-run marker and consent

**Substitutes for:** `onboarding.py offer` / `shown --token` / `preview`, the lockfile-protected
once-ever marker under the store root.

An in-conversation consent line each session: **D**. A line in `lqplaybook.md` recording that the
introduction was seen: **D**, and it makes "once ever" into "once per file the lawyer keeps", which is
weaker but honest. **Failure mode: Loud** — a repeated introduction is visible and mildly annoying, not
dangerous. This is the cheapest substitution in the catalogue and the one every one of the six needs:
all six open with the same marker section (legalquants Q3, lq-ask Q1, lq-connect Q1, lq-reflect's "First
run? One marker, once ever", lq-apply's same, my-lq-moment's same). **Precedent:** lq-mirror deleted
the section outright.

### S8. The installed-plugin scan

**Substitutes for:** `catalog.py --all-plugins --format json`, upstream's way of knowing what it is
allowed to offer. A static map inside the skill: **D**, and already shipped — `lq-start` carries
`files/references/map.md` with both bundles, every entry labelled with its bundle, plus one neutral
sentence that a skill responds only if its bundle is available in the tenant and that plugin
availability is managed by the Microsoft 365 administrator. **This substitution is also a policy
requirement**, not just a capability workaround: CONTRACT section 8 says a card may not "claim a skill
can see which other skills or bundles are installed". **Failure mode: Silent** — the skill names a
skill the tenant does not have. **Mitigation:** lq-start's neutral availability sentence, plus
lq-mirror's stronger form where it fits ("Choose it from the LegalQuants skills actually offered in
this session — never from memory"). **Used by:** legalquants (its whole §1 step 3), lq-reflect ("Where
did they do by hand what a tool would do?"), my-lq-moment and lq-apply (their endings).

### S9. The argument grammar

**Substitutes for:** `argument-hint` and `/skill 7d`-style invocation. Natural-language inference:
**D** — "Users invoke skills in natural language; Cowork routes on `description`. There is no `$name`
or `/name` argument grammar; modes must be inferred from what the user says." The build strips
`argument-hint` and `disable-model-invocation` mechanically. **Failure mode: Loud-ish** — the wrong
mode is usually visible in the first paragraph of the answer. **Mitigation:** state the inferred mode
in one line before working ("I'll review the last thing we did here, not your whole week"). **Used by:**
lq-reflect (`[24h|3d|7d|30d] | session <file> | <what went wrong>`, the sharpest example in the set),
lq-apply (`[application|cv|profile]`), lq-ask, lq-connect. Pipeline: every skill with modes;
`pressuretest` ships `sections/modes.md` doing exactly this.

### S10. External links, sign-ups, assessments

**Not a capability substitution.** Cowork can render a link; the repository forbids one. The only URL
a shipped skill may carry is the upstream repository in the licence notice. Two precisions worth
having: the validator's rule (`LQC-W010`) is a warning and exempts upstream-authored URLs, so the
block is section 8's policy sentence alone; and the rule is about URLs **in the skill's own files**,
not about a link the lawyer supplied in the conversation and asked the skill to work with. **Used by:**
lq-ask (the Substack, Q8), lq-connect (the directory, Q3/Q7/Q8), lq-apply (the assessment, Q10/Q11),
legalquants (the Residency, Q11). my-lq-moment is clean — it carries no URL at all.

### S11. Promote the skill's own documented degrade to the whole skill

**Substitutes for:** inventing a new fallback. Five of the six already contain a written, first-class
path for the case where the machinery is absent, and in every case it is closer to Cowork than
anything an adapter would invent:

- lq-ask Q5: "If it is **not available**: say so in one plain line ('the live corpus isn't reachable
  from here') and work from the public surfaces instead".
- lq-apply Q9: "**Empty or missing store:** say so honestly and start one now... then compile from what
  they give you in this session. Never send them away to wait."
- lq-reflect Q9: "If they decline, work only from what they tell you — that is often enough."
- my-lq-moment Q9: hand over the file and the approved text and give the one-line conversion; and its
  insufficient-evidence rule, "If the host cannot supply real evidence (some hosts expose little), say
  so plainly: that is an automatic *insufficient evidence* outcome, and it ends in refusal, not in a
  lower bar."
- lq-reflect step 8: "Without workers, skip this and say so in one line; the debrief is complete
  without it."

**Evidence: D** — it is the skill's own text, so it introduces no new capability claim and no new
promise. **Failure mode: Loud by construction**, because each of these lines is a statement to the
lawyer. **Caveat:** a degrade written as one branch of two becomes a different skill when it is the
only branch, which is why several sections below end at Tier 3 rather than Tier 1.

### S12. Say the gap out loud

**Substitutes for:** nothing — it is the mitigation that converts S1a, S5 and S6's silent failures into
loud ones, and it is the reason several alternatives here are shippable at all. The shape is upstream's
own: lq-reflect's "Coverage is always stated: the files read, their dates, messages omitted or
shortened, parse errors"; lq-connect's "Unavailable is said, not implied" (lq-ask §1);
playbook-builder's "A source you cannot read, or can read only partly, stays visible as such." **D.**
**Used by:** all fourteen; it is the house style already.

### S13. Hand off to a built-in instead of to a bundled program

**Substitutes for:** a local program the package would have shipped. Cowork's built-ins are addressable
by exact name: Word, Excel, PowerPoint, PDF, Email, Scheduling, Calendar Management, Meetings, Daily
Briefing, Enterprise Search, Communications, Adaptive Cards, App. **D** for the hand-off; **U or C** for
what any given built-in returns on a use it was not described for. Do not hand off to "Deep Research":
it has been retired in favour of Researcher, and five shipped places still name it. **Failure mode:
Loud** normally, **Silent** where the built-in returns something adjacent to what was asked.
**Mitigation:** name the built-in in the reply and say what came back. **Used by:** my-lq-moment
(PowerPoint, for the cover), lq-apply (Word, for the CV), lq-connect (Enterprise Search, for people),
lq-reflect (Excel, for a journey grid). Pipeline: read-redline (Word), sigpack (PDF).

### S14. A scheduled task as the cadence

**Substitutes for:** "run this every week", which upstream got from the lawyer's own habit and a
watermark in the store. Cowork has a Schedule feature and scheduled tasks with run history; whether a
scheduled run can take placed files and write outputs is **U** and is being read separately. **Probe:
P11.** **Failure mode: Silent** — a schedule that runs and produces nothing looks like a schedule that
has not run yet. **Mitigation:** do not build a card whose value depends on it; offer it as a closing
line the lawyer can act on. **Used by:** lq-reflect (the weekly debrief), potentially legalquants (the
check-in). Pipeline: regulatory's refresh.

---

## 1. legalquants

The conductor. It reads where the lawyer is from three script calls, then offers one move — never a
menu. "Everything you know comes from their own machine" (`SKILL.md` §1). On Cowork there is no such
machine, and there is already a shipped skill doing the routing half.

### The alternative, step by step

The nearest thing Cowork can do is a **returning-lawyer conversation** — where you are, and the one
next step — that remembers only what the lawyer hands it. I would build it as a second mode of the
shipped `lq-start` card rather than as a seventh companion skill; the standalone version is costed
below as the alternative.

| # | Upstream step | Cowork-native substitute | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `onboarding.py offer` decides whether the cold open runs (Q3) | The orientation is offered when the lawyer sounds new, once per conversation, and never gates the task | S7 | D |
| 2 | Read `~/.lq/profile.json` for `practice.sentence`, `fluency.level` (Q1) | Read confirmed `[lq-start]` lines from an `lqplaybook.md` the lawyer attached or placed in the Input folder; otherwise ask one question | S1c | D |
| 3 | Counters via `profile_store.py status` — debriefs run, moments kept, lessons in play (Q6) | Read the dated note a previous review or draft wrote to the Output folder, if the lawyer attached it; otherwise ask, in one sentence | S1b | D |
| 3b | (as above, without the lawyer attaching) | Read the same note back from the OneDrive Cowork folder unprompted | S1a | **U** (P2) |
| 4 | `catalog.py --all-plugins` enumerates what is installed (Q4) | The static bundle map `lq-start` already ships, with its neutral tenant-availability sentence | S8 | D |
| 5 | The cold open: what this is, the live map, one taste, one next step | The same four beats, with the map from step 4 | S3 | D |
| 6 | Returning: name where they are in one or two sentences | Same, grounded only in steps 2–3 and what they just said | S3 | D |
| 7 | Offer **one** move, two at most | Unchanged | — | D |
| 8 | Transitions noticed and celebrated from the counters | Compare what the note says with what they say now; one warm sentence | S1b | D |
| 9 | Writes go through the store, on explicit yes (Q8) | Nothing is written. A preference worth keeping is offered as one exact line for their own file | S1c, lq-mirror move 2 | D |
| 10 | The Residency door (Q11) | Removed | S10 | policy |
| 11 | "CODEX for Legal is a workflow aid…" (Q12) | "LegalQuants skills are a workflow aid, not legal advice. The judgement stays yours." | — | D |

### Capability risk

**Low.** Every load-bearing step is D. Step 3b is the only U and it is an upgrade, not a dependency:
if P2 fails, the lawyer attaches the note and nothing else changes.

### Fidelity

**Different deliverable** — a routing-and-next-step conversation that remembers only what the lawyer
brings, rather than a companion that reads their machine quietly. One sub-promise is **not
deliverable** at all: "You may only offer skills that appear in its output. A verb that is not
installed is not an option" (Q4's step, `SKILL.md` §1). Cowork gives no such output and CONTRACT
section 8 forbids claiming otherwise, so the alternative must offer from a static map and say so. The
skill's quietness survives intact — Q5's "Read nothing else. No transcripts, no documents, no matter
names" is easier to honour here than upstream, not harder.

### Failure modes

- Step 3b (U): **Silent** — the model carries on from an empty journey and sounds exactly as sure.
  **Mitigation:** the card names the file it looked for and says it did not find it, before the
  reading.
- Step 4 (D, but policy-shaped): **Silent** if the map drifts from the tenant's actual install — the
  lawyer is pointed at a skill they do not have. **Mitigation:** `lq-start`'s availability sentence,
  already written and shipping.

### Tier and conditions

**Tier 3.** The promise changes: it can no longer read them, so it asks or reads what they brought.
Conditions: (a) it ships as a mode of `lq-start`, not as a second skill, unless the maintainer wants a
distinct "where am I on the journey" ask; (b) it never claims to see the install; (c) the memory is
explicitly the lawyer's file, in the lq-mirror form — "This skill stores nothing itself"; (d) the
Residency line goes. A standalone version needs a changed name (`lq-next` reads right) and a
description whose first clause distinguishes it from `lq-start`'s "which skill for this work" and
`lq-mirror`'s "where do I stand with AI" — which is a thin gap, and the honest reason to merge.

### Probes

P2 upgrades step 3b from "attach it" to "it is just there" and is worth running for four of these six
skills at once. P11 matters only if the maintainer wants a scheduled check-in. No probe can unlock
step 4 — that one is policy, and only the maintainer can move it.

### Effort and companion count

If merged into `lq-start`: one `sections` overlay adding the returning-lawyer beats to the existing
full-file overlay, plus two or three lines in `files/references/map.md`. **0 new companions.** If
standalone: a full-file `SKILL.md` overlay (the upstream body is 1,311 words and almost every
paragraph names a script), `exclude: scripts/**`, and a copy of the map — **1 companion**, which then
drifts against `lq-start`'s copy at every release. Today's arithmetic for reference: 6 files, 1
companion after the global strip and `scripts/**` (`references/endings.md`), and 0 once the endings
table goes with the external doors.

### Bundle and routing collisions

Both bundles. A head-on collision with `lq-start`, which ships in both and answers the same sentence,
and a secondary one with `lq-mirror` on "where am I". There is no room for a third skill in that
space; there is room for a second mode inside `lq-start`.

### The honest counter

Q1, Q3, Q4 and Q6 describe the entire "read where they are" mechanism as script calls against a
private store, and the skill documents no chat-only path anywhere. Q2 — "Never edit `~/.lq/` files
directly" — is a rule the alternative respects trivially, by writing nothing at all. Q5's "no
transcripts" is honoured. What the alternative cannot honour is Q4's rule about only offering what is
installed, and it must say so in the body rather than pretend.

**Policy block:** yes, but small — the Residency URL (Q11) under section 8, and the installed-skills
claim under section 8's Sources-picker bullet. Neither is a capability limit.

### What the lawyer actually gets

They say "where am I with all this, what should I do next?" and get a short, warm answer that is
honest about where it came from: one or two sentences about where they are, based on what they just
said and on a note or playbook file they attached if they have one, then one concrete move and the
sentence to type for it. If they have brought nothing, it asks one question rather than guessing. It
names skills from a map that says plainly it cannot see what their administrator installed. Nothing
is saved; if something is worth remembering it hands them one line to paste into their own file. It
is quieter and less magical than upstream, and a lawyer who has never seen upstream will not notice
anything missing — except that it asks them a question the first time.

---

## 2. lq-ask

"What does the community actually know about this", answered with citations fetched at answer time.
Its promise is receipts: "A citation is something you fetched and can quote, or it is not a citation"
(`SKILL.md` §1).

Two alternatives at different tiers. Build the first.

### Alternative A — the dated library reader (Tier 2)

lq-ask already contains this skill. Q5 is its documented degrade: "If it is **not available**: say so
in one plain line ('the live corpus isn't reachable from here') and work from the public surfaces
instead". The adaptation is to make that branch the whole skill and ship the library with it.

| # | Upstream step | Cowork-native substitute | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `onboarding.py offer` (Q1) | Deleted | S7 | D |
| 2 | Query the lq-mcp connector; check authority with `source_access.py` (Q2) | Not available; say so in Q5's own words, once, up front | S11 | D |
| 3 | Public surfaces from `references/sources.md` (Q5) | A dated digest shipped as companions: the community's published positions, written out, each with its title and date | S5 (snapshot) | D |
| 4 | "Code is a room too" — github.com/LegalQuants fetched live (Q4) | Not available. Named as unavailable, never guessed | S12 | X for the fetch; D for saying so |
| 5 | The builds directory searched live (Q3) | Not available; the same | S12 | X / D |
| 6 | Name the rooms searched and the ones that were not | Unchanged — "Unavailable is said, not implied" | S12 | D |
| 7 | Answer like a practitioner, cite like a lawyer | Unchanged, but every citation is a title and a date, never a URL, and never described as live | S5, S10 | D |
| 8 | Corpus silent → the honest miss (Q6) | Unchanged | S11 | D |
| 9 | Optional: check whether something newer exists | Offer once, only if the lawyer asks; label the provenance as a search rendering, never as the corpus | S5 (search) | **C** (P6) |
| 10 | The ending — the Substack (Q8) | A scope statement: this answered from a library dated *X*, and it is not the whole community | S10 | policy |

**Capability risk: Low.** Steps 1–8 are all D. Step 9 is C and deliberately not load-bearing.

**Fidelity: Different deliverable** — a dated library reader, not a live corpus query. The skill's own
words for what it is losing are Q3 ("searched live") and Q4 ("fetched live"). What matters is that the
alternative does not violate anything the text forbids: §1 says "Never pretend a citation from that
file is a live query result; name it as what it is", which is exactly the discipline the alternative
runs on.

**Failure modes.** Step 3's staleness is **Silent**: a lawyer cannot tell that a confident answer is
six months old. **Mitigation:** the library's date appears in the description, in the first line of
every answer, and in the closing scope statement, and the card is forbidden from saying "currently" or
"the community now thinks". Step 9 is **Silent** in the worse direction — a search rendering quoted as
though it were the corpus. **Mitigation:** if it is offered at all, it is offered in a separate
paragraph under its own heading, labelled as outside the library.

**Tier 2** — ship now with an announced degrade. The announcement is the date.

**Probes.** P6 for step 9 only. Nothing load-bearing waits on a probe.

**Effort and companion count.** 6 files today, 2 companions after the strip (`service-contract.md`,
`sources.md`). `service-contract.md` describes the LQ Brain connection and goes; `sources.md` is a list
of links and is replaced. The real cost is not the card, it is the content: **somebody has to write the
digest**. A useful one is an index plus four to eight topic files, well inside the 20-file / 5 MB /
10 MB budget — call it **5 companions** — and it is new work, not a transformation of upstream text.
That is the honest reason this is not the first thing to build, and it should be said to the maintainer
plainly.

**Bundle and routing collisions.** Both bundles. It collides with the tenant's own research and search
built-ins on almost any phrasing, and with the shipped `wiki` card, which explicitly sends "research
into outside material" to the research built-in. The description has to say "what other lawyers have
published about working this way" in the first clause, or it will lose every routing contest it should
win and win several it should lose.

**The honest counter.** Q3 and Q4 are unambiguous that two of the four rooms are live-only, and the
profile's note that the builds directory embeds its data in a framework chunk rather than an API means
even a page read would probably not recover it. The alternative does not pretend otherwise: those two
rooms are named as unavailable in every answer that would have used them.

**Policy block: yes** — the Substack (Q8), `legalquants.com`, `github.com/LegalQuants`. Note the narrow
carve that needs no policy change: citing an essay by **title and date without a URL** is not a link.
That is enough for the skill to function. A second, non-capability question sits underneath: the digest
is LegalQuants content being bundled into an independent adaptation, which is a licensing decision for
the maintainer.

### Alternative B — the connector (Tier 4)

Declare an `agentConnectors` entry for an authenticated Streamable-HTTP MCP server exposing the
corpus; the body's step 2 becomes a real connector query and Q5 stays as the degrade it already is.
**Capability risk: Low on the route** (connectors are documented, up to 10 per package, OAuth or
dynamic client registration; API-key auth is declared in the schema but stated as not yet available in
Cowork) **and High on everything else**, because it needs a server somebody operates, an auth story
for a tenant that is not a LegalQuants member, and the same external-URL carve-out. **Fidelity: Same
deliverable.** **Tier 4.**

### Which to build first

**A.** It needs no infrastructure, no auth, no external URL and no capability nobody has tested. It
also upgrades into B without changing the card's promise to the lawyer: the description stays "what
the community has published on this", and one day the sources get fresher. The only thing standing in
A's way is that somebody has to write the library — which is a real cost, and a better one to pay than
a connector nobody has stood up.

### What the lawyer actually gets

They ask "has anyone worked out a good way to do X with AI?" and get a practitioner's answer with two
or three specific citations — an essay title, a date, a named piece of work — and a line at the top
saying this comes from a library current to a stated date, and a line at the bottom saying what it
could not look at. When the library has nothing, they are told so in one sentence and offered general
knowledge clearly labelled as such. What they do not get is anything that happened since the library
was written, and they will know that every time.

---

## 3. lq-connect

Find two or three people whose public profiles fit a sanitized need, hand over the links, stop. Its
load-bearing step is a page read: "Read the public directory (`legalquants.com/community`, profiles at
`/profile/<slug>`)" (Q3). Of the six it is the one whose capability gap is smallest and whose policy
gap is largest.

Two alternatives, plus a third named for completeness. Build the first, with the second as a mode
inside it.

### Alternative A — the colleague finder (Tier 3)

Keep the entire discipline — the sanitized need, the taxonomy, two or three with a specific why, the
honest miss, no brokering — and change the pool from the LegalQuants directory to the people the
tenant can already see.

| # | Upstream step | Cowork-native substitute | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `onboarding.py offer` (Q1) | Deleted | S7 | D |
| 2 | Derive the need summary, shape never substance (Q5) | Unchanged | — | D |
| 3 | Show it verbatim, explicit yes (Q6) | Unchanged | — | D |
| 4 | Warn that a good match takes a minute; progress beats | Unchanged | — | D |
| 5 | Read the public directory and profiles (Q3) | Hand off to the Enterprise Search built-in by name to surface people inside the tenant and the work that names them | S13 | D by name; **U** on what it returns (P12) |
| 6 | Match on `references/taxonomy.md` | Unchanged — the taxonomy is the intellectual content and it ports intact | — | D |
| 7 | Deepen the why with a fetched excerpt (Q2, Q9) | Quote the tenant document that grounds the match — which is a stronger citation than upstream's, because it was genuinely retrieved | S12 | D |
| 8 | LinkedIn named, never fetched (Q4) | Unchanged, and now redundant | — | D |
| 9 | Hand over profile links | Hand over the person, the document that shows the fit, and one line on what to say | — | D |
| 10 | Nobody fits → the directory link and a suggested search (Q7, Q8) | Say so plainly and suggest the search the lawyer could run themselves | S10 | policy |

**Capability risk: Medium.** Step 5 is the only U: Enterprise Search is documented as a built-in by
exact name, but nothing says what a "who here has worked on X" request returns, and a tenant with thin
indexing returns nothing useful. P12 settles it.

**Fidelity: Different deliverable** — a colleague finder, not a LegalQuants member finder. Q3 is the
promise that changes, and the change is not cosmetic: the value of upstream's answer is that these are
people who chose to be findable for exactly this.

**Failure modes.** Step 5 (U): **Silent** in the worst way — a confident list of three colleagues who
are adjacent rather than apposite, padded because the skill wanted three. **Mitigation:** the skill's
own rule already handles it if kept verbatim — "Pick **two or three** — fewer when that is what the
evidence supports, never pad" and "A forced match is worse than an honest miss" (Q8) — plus a
requirement to quote, for each person, the document that put them on the list.

**Tier 3**, conditions: (a) the description opens with "inside your organisation" so the routing
contest with Enterprise Search is a hand-off rather than a fight; (b) no external link anywhere;
(c) the sanitization gate is kept even though the summary no longer leaves the tenant, because it is
cheap and it is what makes the skill safe to use on a live matter; (d) P12 run before it ships, or the
card ships with an announced degrade ("if I cannot find people here, I will say so and stop").

### Alternative B — bring your own directory (Tier 2)

The lawyer attaches or pastes the directory, a membership export, a conference attendee list, their
own contacts — and the skill matches that against the taxonomy with the same discipline. **Capability
risk: Low** (reading an attached file is documented; so is reading what the lawyer pasted).
**Fidelity: Same deliverable with a disclosed weaker guarantee** — the pool is whatever they brought
and its currency is theirs.

The precise policy position, which the maintainer should rule on: `LQC-W010` scans the skill's own
`*.md` files, so a card that contains no URL and relays links the lawyer supplied does not trip the
validator, and section 8's sentence is about what a shipped skill *links to*, not about what a lawyer
brings into their own session. I read that as permitted. It is close enough to the line that it should
be an explicit decision rather than an inference.

### Alternative C — browser use (Tier 2, tenant-dependent)

Edge automation reading the live directory is the literal substitution for Q3, and a rendered directory
page is exactly what the skill wants to quote. But browser use is web-client only and "disabled by
default" until a tenant admin enables it, so no card may depend on it. **U**, **probe P10.** Worth
naming; not worth building first.

### Which to build first

**A, with B as a mode inside it.** One card, two pools: "I'll look for people here in your
organisation; if you have a directory or a list of your own, attach it and I will use that too." The
taxonomy, the sanitized need and the two-or-three-with-a-why discipline are identical in both, so the
body barely branches. C is a line in the notes, not a build.

### Effort and companion count

4 files today, **1 companion** after the strip (`references/taxonomy.md`, 1.9 KB) — the smallest of
the fourteen, and it survives the surgery untouched. The card is a handful of `replace` rules on §2 and
the two miss-paths, plus deleting the marker section. This is the cheapest surgery of the six; the
question is only what the skill is for.

### Bundle and routing collisions

Both bundles. It collides with Enterprise Search on "who knows about X" — which Alternative A resolves
by handing off to it rather than competing — and with nothing in either shipped bundle, because
nothing in either bundle is about people.

### The honest counter

Q3 is the skill; changing the pool changes the skill. Q4's citation rule ("a citation is something you
fetched and can quote, or it is not a citation") is respected better by Alternative A than by upstream,
because a tenant document really was retrieved. Q5 and Q6's sanitization survive verbatim. Q7 and Q8
both end by handing over the directory link, which is the one thing a shipped skill may not do, so both
miss-paths need rewriting — and that is a policy consequence, not a capability one.

**Policy block: yes** — the directory URL and profile links (Q3, Q7, Q8) under section 8. Alternative A
removes the need for them entirely; Alternative B needs the ruling described above.

### What the lawyer actually gets

They say "I need to talk to someone who has actually done a data-room review with AI before I commit to
this approach". The skill asks what the need is, writes it back as two sanitized sentences with no
client or matter in them, waits for a yes, then comes back with two or three people in their own firm,
each with one line on why — grounded in a document it names and quotes — and one line on what to say
when they reach out. If nobody fits, it says so rather than padding. It never messages anyone, never
books anything, and never claims someone is good at this, only that this is what the record shows.

---

## 4. lq-reflect

The hardest of the six, and the only one of the fourteen whose README reason ("host session
transcripts") was right. Its value is reading the lawyer's own past sessions across a window, by exact
file, with a consent architecture built out of hashes and previews: "run `scripts/debrief_scan.py
--list` with the window and `--state ~/.lq` for candidates (metadata only, no content)" (Q3), then
"retrieve its complete messages and surrounding responses through `session_reader.py --session <exact
filename> --manifest <file> --confirmed --lines <start> <end>`" (Q4), over "since the last debrief, or
the last seven days on a first run" (Q6).

Two alternatives. Build the first.

### Alternative A — "review this piece of work" (Tier 1 capability, Tier 3 promise)

A re-scoped skill with a changed name. The unit of review stops being the week and becomes the work in
front of them: this conversation, plus whatever they attach.

| # | Upstream step | Cowork-native substitute | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `onboarding.py offer` | Deleted | S7 | D |
| 2 | "What this review is", said before anything else | Unchanged, verbatim | — | D |
| 3 | Window: 24h / 3d / 7d / 30d / one session (Q6) | No window. The scope is this conversation and the files they attached, inferred from what they said | S9 | D for the scope; **X** for the window |
| 4 | Metadata-only candidate scan (Q3) | Removed. There is nothing to discover: the lawyer's attaching *is* the selection | S1b | D |
| 5 | Hash-bound manifest, confirmed before any read (Q3) | The list of what will be read, shown before reading, with an explicit yes | S12 | D for the consent; **X** for hashing |
| 6 | Quote what they actually typed | From an attached file: D. From earlier in this conversation: documented that a skill can "reference earlier messages"; whether recall is verbatim is not | S6 | D / **U** (P9) |
| 7 | Retrieve complete messages before relying on a preview (Q4) | Not needed for an attached file; for the conversation, the text is either there or it is not, and the skill says which | S12 | D |
| 8 | Check the kept change from last time | Read the dated review note the lawyer attached; otherwise ask what they were going to try | S1b | D |
| 8b | (as above, unattached) | Read the last note back from the Cowork folder | S1a | **U** (P2) |
| 9 | Five to seven moments, each with a quote | Unchanged, bounded by step 6 | — | D |
| 10 | "Where did they do by hand what a tool would do?" via `catalog.py` | Name skills from the static bundle map, with the availability sentence | S8 | D |
| 11 | Attribute every moment | Unchanged | — | D |
| 12 | One change, with a countable signature | Unchanged | — | D |
| 13 | The moment to keep | Unchanged | — | D |
| 14 | Second read by a fresh subagent | Skipped, and said in one line — the skill's own instruction for a host without workers | S11 | D |
| 15 | Show, then `append` to the store | Write the dated review note to the Output folder, name it, and say to bring it back next time | S1a + S1b | D (write) |
| 16 | Close with the counters from `status` | Count from what was brought | S12 | D |
| 17 | The nomination handoff to `my-lq-moment` | A scope statement unless that skill ships | S8 | D |

**Capability risk: Medium.** Step 6 is the only load-bearing U and it is the hinge of the whole skill:
"A moment with no quote is not a moment; drop it." If the model cannot reproduce what the lawyer
actually typed earlier in the same conversation, every moment has to come from an attached file, and
the skill becomes useful only to lawyers who bring material. P9 settles it. Step 8b is a
convenience-level U (P2).

**Fidelity: Core promise not deliverable.** The text that says so is Q13, from `references/reading.md`:
"Avoid custom transcript searches, ad hoc Python extraction, database content reads, `cat`, `rg` or
subagent reads that bypass the selection." That is a rule against improvising exactly the substitute an
adapter reaches for, and it is right — the selection architecture is the consent architecture. Q6's
window and Q3/Q4's selection machinery cannot be reproduced, so the alternative must be a different
skill with a different name and a smaller claim. "Review this piece of work with me" is that claim.
Note what it is *not* allowed to be: the chat-only branch (Q9) shipped as the whole product is,
in the rebucket's phrase, lq-mirror with extra steps — and lq-mirror ships in both bundles. The
re-scope only earns its place if it is anchored on a concrete piece of work rather than on the lawyer.

**Failure modes.**
- Step 6 (U): **Silent, and the worst in this paper.** A model asked "how did that go?" will produce a
  fluent account of a session whether or not it can see it, with quotes that read like quotes.
  **Mitigation, three parts:** the card lists what it is reading, by name, before any finding; a moment
  without a verbatim quote is dropped, as upstream requires; and where the quote is reconstructed
  rather than read, the skill says "as I understand it, you asked…" and never uses quotation marks.
- Step 8b (U): **Silent** — a kept change that quietly is not checked. **Mitigation:** say the file
  was not found and ask.
- Step 3 (X): **Loud** — a lawyer who asks for "the last seven days" is told, in one line, that this
  reviews the work in front of us and what to attach if they want more.

**Tier.** Alternative A is **Tier 3** on the promise and Tier 1 on capability: everything load-bearing
except step 6 is documented, and step 6's mitigation makes its failure loud. Ship it under a changed
name.

**Probes.** P9 (can it quote the lawyer's own earlier words verbatim) is load-bearing and should be run
before this is built. P2 upgrades step 8b. P5 and P7 bear on Alternative B. P11 bears on the cadence.

### Alternative B — the same, inside a resumed task (Tier 2)

Two upgrades, each waiting on a probe: (i) the last review note is read back from the Cowork folder
without the lawyer attaching it (P2); (ii) the review runs inside a resumed task, so "this
conversation" covers days of work rather than one sitting (P5 and P7 together — resumption is
documented only as a UI affordance, and no page says what re-enters the model's context). A third,
weaker upgrade: a scheduled weekly run over placed files (P11, U). None of these gets back to Q6's
window across *every* session; the best case is one thread reviewed deeply.

**Which to build first: A.** B is A plus probe results, and every probe result improves A without
changing its card.

### Effort and companion count

The largest surgery of the six. The upstream body is 3,161 words — already over `LQC-W006`'s
3,000-word warning before anything is added — and the sections that go are structural: "State — one
script writes" in full, steps 1 and 2 of "The run", step 8, the nomination handoff, the catalog bullet,
the ending door. This is a **full-file `SKILL.md` overlay**, not a set of `replace` rules, plus
`exclude: scripts/**`. 12 files today, 5 companions after the strip; `store-contract.md` and
`reading.md` describe the machinery and go; `mining.md` describes working a scan frontier that no
longer exists and needs a rewrite or a drop. `bottlenecks.md` and `technique-ladder.md` are the
intellectual core and survive untouched. **2 companions** (3 if `mining.md` is rewritten).

### Bundle and routing collisions

Both bundles. Two live collisions. `lq-mirror` ships in both and already claims "assess me" and "where
am I with AI" — and an under-specified debrief skill will take those. `timenarratives` takes "write up
what I did today", which is one paraphrase from "go through what I did today"; its own description
already ends with a scope statement precisely because that boundary is thin. The re-scoped
description must open with the object ("one piece of work you have just finished") and carry explicit
hand-offs both ways.

### The honest counter

Q13 forbids improvising a read path, and the alternative respects it by not reading anything the lawyer
did not put in front of it. Q5's honesty about the limit — "the reader protects exact selection and
reports omissions — it does **not** detect every client reference, and a model reading a mixed session
has already received its content" — matters more here, not less: an attached session file is a file the
lawyer chose, so the consent is stronger, but the client-material warning is identical and must survive
verbatim. Q2 ("If the sandbox refuses a write, say so and give the exact command for the lawyer to
run") is the one line that cannot survive — there is no command to give — and it is replaced by naming
the Output file.

**Policy block:** none of substance. The catalog step is the section 8 constraint already handled by
S8; nothing here is an external link.

### What the lawyer actually gets

They finish a piece of work and say "that was harder than it should have been — what would you do
differently?" The skill says what it can see, asks before quoting anything, and comes back with three
short items: one thing they did well, one concrete change to try, and why that change helps their
actual work, each anchored in something they actually typed. Then one change to keep, written out with
a countable signature, in a short dated note it saves to the Output folder and names — and it tells
them to bring that note back next time so it can check whether the change held. What they lose is the
week: it cannot go and look at Tuesday, and it will say so plainly rather than reconstructing Tuesday
from nothing.

---

## 5. lq-apply

Turn the journey into an artifact — an application answer, a CV, a public profile — from confirmed
evidence, with the gaps shown rather than filled. Of the six this is the one whose Cowork-native
version needs the least invention and loses the most purpose.

### The alternative, step by step

| # | Upstream step | Cowork-native substitute | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `onboarding.py offer` | Deleted | S7 | D |
| 2 | Read `profile.json` and `journey.jsonl` through the store contract (Q1) | Read the dated evidence or review note the lawyer attached; read confirmed `[lq-apply]` lines from an attached `lqplaybook.md` | S1b, S1c | D |
| 2b | (as above, unattached) | Read the evidence file back from the Cowork folder | S1a | **U** (P2) |
| 3 | Empty or missing store → start one, compile from this session (Q9) | The default path, not the exception — promoted verbatim | S11 | D |
| 4 | A selected project or CV folder they point at | Files they attach or a folder they name | — | D |
| 5 | A confirmed public handle | Named as reported, never verified; no fetch is attempted or claimed | S5 | **X** for verification; D for saying so |
| 6 | Inventory before highlights | Unchanged | — | D |
| 7 | Honest attribution — built / co-built / forked / tested / deployed | Unchanged | — | D |
| 8 | Declared versus inferred, gaps surfaced before ready | Unchanged | — | D |
| 9 | Choose the format: application / cv / profile (Q10) | cv and profile only; the application format goes with its destination | S10 | policy |
| 10 | Fetch the form's current fields when reachable (Q4) | Removed. Q4's own provisional rule is kept for anything the lawyer supplies about a form | S11 | D |
| 11 | Draft every field; insert the gap marker rather than invent | Unchanged | — | D |
| 12 | "Where it goes. Local file, saved where they say" (Q2) | A named file in the Output folder, or a Word document through the Word built-in on request; evidence notes in a separate file, as upstream requires | S2, S13 | D |
| 13 | The ending — the website door (Q11) | A scope statement: this is a draft they own, it goes nowhere, and nothing here submits anything | S10 | policy |

**Capability risk: Low.** Every load-bearing step is D. Step 2b is a convenience U; step 5's lost
verification is a documented absence the skill already has words for.

**Fidelity: Different deliverable.** Upstream's artifact exists to be submitted: "the real LQ
application, which is LQ Assess: a short form at https://assess.legalquants.com and then a 90-minute
observed work session; the assessment is the application" (Q10), closing on "the application is LQ
Assess... when they are ready; the public profile lives on legalquants.com once it is real" (Q11).
Remove the destination and what remains is an evidence-based professional profile with an honest gap
account. That is less than upstream, and it is not nothing: the discipline — declared kept apart from
inferred, attribution separated, "Gaps are asked, never filled — not even when they ask for 'polish' or
say everyone exaggerates", no verdict language anywhere — is the part a lawyer cannot get from a
generic CV drafter, and it ports intact.

**Failure modes.** Step 2b (U): **Silent** — a thin draft that looks like a complete one because the
evidence file was not found. **Mitigation:** the skill names the file it looked for, and the inventory
step (7) already shows what it read and what remains uncovered, which converts this to loud if kept.
Step 5 (X): **Silent** if the model describes a public profile it did not read. **Mitigation:** the
skill's own rule — never attribute work without confirming it belongs to them — plus an explicit
"reported, not verified" label wherever a handle is used.

**Tier 3**, conditions: (a) the destination and both URLs go; (b) the first line says it is not
connected to any application or assessment, so the changed promise is visible before the draft, not
after; (c) the collision with `writing` is resolved in the description; (d) the gap discipline is kept
word for word, because it is the reason to ship it at all. **A Tier 2 variant** exists if P2 passes:
the evidence file is read back unprompted and the skill becomes a running record rather than a one-off
draft. Build the Tier 3 version first; P2 improves it without changing its card.

**Probes.** P2 for step 2b. Nothing else is waiting.

**Effort and companion count.** 4 files today, no scripts of its own, **1 companion**
(`references/formats.md`, 2.9 KB) which needs a rewrite to drop the application slug mapping. The card
is a handful of `replace` rules plus the marker deletion — a small surgery. The hard part is the
description, which has to distinguish "arrange my evidence of working well with AI" from `writing`'s
"draft this document for me" without naming a product.

**Bundle and routing collisions.** Both bundles. `lq-mirror` on self-assessment — resolvable, since
lq-mirror gives a reading and this gives an artifact — and `writing` on "draft my CV", which is the
one that needs an explicit hand-off in both descriptions.

**The honest counter.** Q5 — "Never used: raw transcripts, unconfirmed or proposed items, anything that
looks like a client, a matter, or document content" — is honoured trivially. Q8's rule that writes go
only through the save door becomes "writes nothing at all", which is stricter. Q9 is the alternative's
own foundation and upstream calls it a normal mode, not a degradation. What the alternative cannot
honour is Q10 and Q11, and it should not try to imitate them with a vaguer door.

**Policy block: yes**, and decisive for the format — `assess.legalquants.com` and `legalquants.com`
under section 8. The capability picture is nearly clean; the purpose is what the policy removes.

**What the lawyer actually gets.** They say "help me write up what I've actually done with AI". The
skill asks what to draw on, in order, starting with anything they have kept and ending with just
talking to it, and says at the top that it is not connected to any application or assessment. It shows
an inventory of what it read before it writes anything, asks one or two questions about work it
suspects is missing, and drafts a one-page legal-AI CV or a profile in which every line is traceable to
something they confirmed. Then it shows the gaps as a short list, in plain words, and refuses to fill
them however they ask. It saves the draft as a named file and keeps the private evidence notes in a
second one. Nothing is submitted, and it says so.

---

## 6. my-lq-moment

The one the rebucket already called a candidate for amber, and the one I would build first. Its scope
is what Cowork documents that a skill has: "Scope is the **current session only**: no history, no
transcripts of other sessions, no `~/.lq/`, no profile or playbook reads" (Q2). Its blocker is one
step — a bundled script that shells out to local image programs.

### The alternative, step by step

| # | Upstream step | Cowork-native substitute | Pattern | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `onboarding.py offer` | Deleted | S7 | D |
| 2 | Explain before evidence; state the training exclusion up front | Unchanged | — | D |
| 3 | The consent gate: "May I inspect and assess only the work evidence in this current session?" | Unchanged | — | D |
| 4 | Evidence: this session's conversation, the tool and skill events, the workspace artifacts (Q8) | The conversation: D. Files in the Input and Output folders: D. Tool and skill events: nothing documents that a skill can enumerate them | S6 | D / D / **C** (P9) |
| 5 | Insufficient evidence → automatic refusal, never a lower bar | Unchanged, and it is the mitigation for step 4 | S11 | D |
| 6 | Judge against `references/rubric.md` | Unchanged | — | D |
| 7 | The receipt: Before → Move → Result → Check → Takeaway | Unchanged | — | D |
| 8 | Confirm facts, then sharing, then confidentiality | Unchanged | — | D |
| 9 | The post, built to `references/copy.md` | Unchanged | — | D |
| 10 | The cover: the bundled template with two sentences set over it, rendered by `render_cover.py` (Q3) | An HTML card for the preview pane built to `references/cover.md`, embedding the bundled template image | S4 | D for the HTML; **U** for whether the bundled image appears in the output (P7 for a template, **P8** for this 583 KB PNG) |
| 10b | (fallback within the same step) | A plain styled card with no template image, or a square slide through the PowerPoint built-in | S4, S13 | D |
| 11 | "the script refuses more than twelve [words]" | The skill counts the words itself and shows the shortened sentence | S3 | D |
| 12 | If no PNG: hand over the file and the one-line conversion (Q9) | Unchanged in substance — the lawyer exports the image. Q9's prohibitions carried verbatim | S11, S4 | D |
| 13 | Practice example, labelled everywhere, `--practice` on the renderer | The label is written into the HTML and the post by the skill | S3 | D |
| 14 | Publication is entirely theirs; never post (Q5) | Unchanged, and easier: a skills-only package has no channel out | — | D |
| 15 | One line may stay, saved through `profile_store.py` (Q6, Q7) | Nothing is saved. On yes, the exact line is handed to them for their own file | S1c, lq-mirror move 2 | D |
| 16 | The ending — `$lq-apply` is where moments compound (Q10) | A scope statement, unless lq-apply ships | S8 | D |

**Capability risk: Medium.** Two U/C steps. Step 10's bundled binary asset is U and has a documented
fallback in the same step, so it is not fatal. Step 4's tool-and-skill-event evidence is C and is the
one that decides whether this skill is useful: if Cowork exposes little of its own session to a skill,
the rubric's honest answer is *insufficient evidence*, every time. The skill would be loudly useless
rather than quietly wrong — which is the right failure, and still a failure. P9 settles it.

**Fidelity: Same deliverable with a disclosed weaker guarantee.** The receipt, the judgement, the
rubric, the post and the confidentiality pass are untouched. The cover becomes an HTML card or a slide
the lawyer exports, and nothing is kept afterwards. Upstream's own text authorises the conversion path
(Q9) and forbids the tempting shortcut in the same breath — "Do not draw anything yourself, ask an
image model, or claim a PNG exists" — so the adaptation is inside the skill's own rules, not around
them.

**Failure modes.**
- Step 4 (C): **Loud**, because of the insufficient-evidence rule in §1 "Consent and scope" — "If the
  host cannot supply real evidence (some hosts expose little), say so plainly: that is an automatic
  *insufficient evidence* outcome, and it ends in refusal, not in a lower bar" — which is already
  written and must be kept verbatim. Without it this would be the most dangerous step in the paper: a
  moment awarded on a session the skill could not actually see.
- Step 10 (U): **Loud** — a missing image in a preview pane is visible. **Mitigation:** the skill says
  which form of the cover it produced.
- Step 15: no failure — it writes nothing.

**Tier 2.** Ship after P8 passes, or ship now with the announced degrade: a plain styled cover. I
would ship now with the degrade and treat the template as an upgrade, because the cover's value is the
two sentences, not the background.

**Probes.** P8 (does a bundled binary companion reach an output file), P9 (what a skill can see and
quote of its own session). P7 is the adjacent check on the shipped `legaldesign` and `cite-check`
templates and is worth running first because it is free — those skills already ship.

**Effort and companion count.** The surgery the rebucket sketched, and it is accurate: `exclude:
scripts/**`; a `sections` overlay on step 3 replacing the render command with "fill the supplied cover
template with the two approved sentences and save it as an HTML page for the preview pane" — the
pattern `cite-check` uses with its report template and `legaldesign` uses throughout; a `replace`
deleting step 5's store write; a `replace` on the ending. Watch `LQC-W009`: "the renderer" and
"subprocess" are host words and must not survive in any `*.md`. 10 files today, **6 companions** after
the strip (`copy.md`, `cover.md`, `examples.md`, `rubric.md`, `assets/README.md`, and
`assets/cover-template.png` at 583 KB) — 6 of 20 files, 583 KB of the 5 MB per-file cap, 602 KB of the
10 MB total. `cover.md` needs a rewrite for the HTML form. If P8 fails, the template and its README go
and it is **4 companions**.

**Bundle and routing collisions.** Both bundles, as a core-adjacent reflective skill. `lq-mirror`
already claims "assess me", "what's my archetype" and "where am I with AI"; this one's ask is narrower
("was this session the good kind?") and the two descriptions need an explicit hand-off in both
directions. `legaldesign` owns "make me a polished page for the preview pane" and would otherwise take
the cover request — the cover must be described as part of this skill's output, never as a design job.

**The honest counter.** Q2 and Q7 forbid reading history, the profile or a playbook, and the
alternative reads none of them. Q3's "never by an image model" and Q9's three prohibitions survive
unchanged and must stay in the body. Q5's "Never post, transmit, schedule, queue, or invoke a
publishing connector, even when asked" survives and is now also structurally true. What is lost, and
what the card's `notes` must say: the rasterised PNG, the fixed template if P8 fails, and the kept
line — so a moment becomes a reading, not a record.

**Policy block:** none. my-lq-moment is the only one of the six with no external URL anywhere in its
own text. There is a judgement call that is not a policy block: "My LQ Moment" is a LegalQuants
construct and the rubric judges against that programme's standard, in a bundle installed by tenants who
are not members. The skill's own rules already forbid implying membership or certification; the
maintainer should decide whether that is enough.

**What the lawyer actually gets.** They finish something that went unusually well and say "was that
actually impressive or am I flattering myself?" The skill explains what it is about to do, asks
permission to look at this session's work, and then either says plainly that this is not an earned
moment and why — or gives them a private receipt: what the situation was, what they did, what came
back, what they checked, what to take from it, with every claim tied to something in the session. If
they want it, they get a LinkedIn post in their own voice and a cover card that opens in the preview
pane, with two short sentences on it, which they can export as an image themselves. It never posts
anything, never saves anything, and if the session does not give it enough to go on it says so and
stops rather than lowering the bar.

---

## Summary

| Skill | Alternative in one line | Capability risk | Fidelity | Worst failure mode | Tier | Probes | Policy block? | Companions after surgery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legalquants | A returning-lawyer mode inside `lq-start`: where you are, one next step, memory only from what they attach | Low | Different deliverable | Silent — reads on from an empty journey it never found | 3 | P2 (upgrade), P11 (optional) | Yes — Residency URL; installed-skills claim | 0 merged, 1 standalone |
| lq-ask | A dated library reader: the community's published material, shipped as companions, cited by title and date | Low | Different deliverable | Silent staleness — a six-month-old answer that sounds current | 2 | P6 (optional step only) | Yes — Substack, site, GitHub | ~5 (new content to write) |
| lq-ask (B) | The same skill against a declared `agentConnectors` MCP corpus server | Low on the route | Same deliverable | Loud — connector absent, degrade to A | 4 | none | Yes — plus a server to operate | 1 + manifest entries |
| lq-connect | Colleague finder: the same sanitized need and taxonomy, matched against people via Enterprise Search | Medium | Different deliverable | Silent — three padded, adjacent matches | 3 | P12; P10 for the browser variant | Yes — directory and profile links | 1 |
| lq-connect (B) | Bring your own directory: they attach the list, the skill matches it | Low | Same deliverable, weaker guarantee | Loud — no list, no matches | 2 | none | Needs a ruling on relayed links | 1 |
| lq-reflect | "Review this piece of work": this conversation plus what they attach, one change kept in a dated note they carry | Medium | Core promise not deliverable | Silent — a fluent account of a week it cannot see | 3 (Tier 1 capability) | P9 (load-bearing), P2, P5, P7, P11 | No | 2–3 |
| lq-apply | Evidence-based CV or profile with an honest gap account, drawn from what they bring or just the conversation | Low | Different deliverable | Silent — a thin draft that looks complete | 3 | P2 (upgrade) | Yes — assessment and site, decisive for the format | 1 |
| my-lq-moment | The same receipt, rubric and post; the cover becomes an HTML card or a slide they export; nothing kept | Medium | Same deliverable, weaker guarantee | Loud — insufficient evidence, refused | 2 | P8, P9; P7 free today | No | 4–6 |

### Build order

1. **my-lq-moment.** Smallest surgery, highest fidelity, no policy block, and the repo has already done
   this exact operation once on lq-mirror.
2. **lq-apply**, re-scoped. Low risk, small card, and the gap discipline is worth having on its own —
   conditional on the maintainer being content with a CV skill that goes nowhere.
3. **lq-connect** as a colleague finder, after P12. Cheapest surgery of the six; the only open question
   is whether the tenant's search returns people.
4. **lq-reflect**, re-scoped and renamed, after P9. Biggest surgery and the sharpest collision with
   `lq-mirror`, but the one change checked next time is a mechanic nothing else in either bundle has.
5. **lq-ask** as a dated library reader — blocked on somebody writing the library, not on Cowork.
6. **legalquants**, folded into `lq-start` rather than shipped beside it.

### Probes this paper adds

- **P8 — does a bundled binary companion reach an output file?** Package a skill carrying a small PNG
  and an HTML template that references it. Prompt: *"Build the card from your supplied template and
  tell me which of your packaged files it used."* Pass: the rendered page shows the image and the reply
  names the file. Fail (record separately): the page renders without it, or the reply claims an image
  that is not there. Settles my-lq-moment's cover, and the general question P7 opens for HTML
  templates.
- **P9 — what can a skill see and quote of its own session?** In one conversation, do some work: type a
  distinctive sentence, have a file created, invoke a second skill. Then prompt: *"Quote back, word for
  word, the sentence I typed at the start of this session; list the files created in this session; and
  list the skills and tools used. Say for each whether you are reading it or reconstructing it."*
  Pass: verbatim quote, correct file list, correct skill and tool list, with honest attribution. Fail,
  in two distinguishable ways: a refusal (usable — the cards adapt) or a fluent paraphrase presented as
  a quote (the dangerous one, and the reason lq-reflect waits on this). Settles the hinge of
  lq-reflect's alternative and step 4 of my-lq-moment's.
- **P10 — browser use: tenant posture and skill-initiated navigation.** With browser use enabled by an
  admin, prompt a skill step that needs a public page: *"Open the page at <public URL> and quote its
  first heading and the first sentence under it. Tell me how you retrieved it."* Pass for the
  alternative: the quote comes back and Cowork names the route. Record the tenant's admin posture
  either way; a refusal citing a disabled setting is an equally useful result. Settles lq-connect's
  Alternative C and the optional step in lq-ask.
- **P11 — a scheduled task running a custom skill over placed files.** Schedule a task that names a
  custom skill and a file already in the Cowork folder. Pass: the run history shows it ran, an output
  file appears, and the output reflects the placed file. Fail: the schedule exists but the skill is not
  invoked, or nothing is written. Settles S14 for every cadence-shaped idea in both halves of this
  analysis.
- **P12 — Enterprise Search as a people finder.** Prompt: *"Who in my organisation has worked on <a
  topic with real internal material behind it>? Name up to three people and, for each, quote the
  document that shows it."* Pass: named people with quotable documents. Fail: documents with no people,
  or names with nothing behind them. Settles the load-bearing step of lq-connect's Alternative A.

### One thing worth saying to the maintainer

Five of these six skills already contain their own Cowork-native version, written by their own authors
as the branch for a host that could not do the full thing — lq-ask Q5, lq-apply Q9, lq-reflect Q9,
my-lq-moment Q9 and its insufficient-evidence rule. In every case that branch is closer to what Cowork
can do than anything an adapter would invent, and shipping it costs no new capability claim and no new
promise. The design work in this paper is mostly the work of deciding whether the branch, standing
alone, is still a skill worth having — and of writing the one sentence that tells the lawyer which
branch they are in.
