# Capability switches: a plan

Status: proposal, 28 September 2026. Nothing here is implemented except the
draft probe skill in [diagnostics/capability-check/](../diagnostics/capability-check/).
It amends nothing in [CONTRACT.md](CONTRACT.md) until the decisions in section 7
are made.

## 1. The question

Fourteen of the thirty-one skills were adapted around capabilities nobody has
confirmed in a live tenant ([probes.yaml](../probes.yaml), P1 to P14). Where
the answer was unknown, each card was written for the cautious answer. Two
things are wanted:

1. **A skill that finds out**, in a real tenant, which of the cautious answers
   were needed.
2. **Switches**, so that a skill built for a tenant where a capability is
   confirmed uses its fuller behaviour there, while every other tenant keeps the
   cautious one.

The first is drafted. The second is possible, and this document says how,
where, and — as importantly — where a switch is the wrong tool.

## 2. What the probe results actually decide

Mapping every probe against the cards and the research
([cowork-alternatives-and-risk.md](research/cowork-alternatives-and-risk.md))
gives three kinds of dependency, and only one of them needs a switch.

| Kind | What a pass does | Probes | Needs a switch? |
| --- | --- | --- | --- |
| **Switch** | The card has a cautious path and a fuller one; a pass lets a build choose the fuller one | P2, P3, P4, P8, P11, P13, P14 (and P1, behind a policy decision) | Yes |
| **Already adapts** | The card already tries the fuller thing and tells the lawyer which one they got; a pass just means the fallback stops showing up | P7b (my-lq-moment), P10 (read-redline, conform), P6 (cite-check) | No |
| **Confirms** | No behaviour changes; a limit or a guard is confirmed | P5, P6 (mostly), P7a, P9, P12 | No |

The per-skill detail is in
[references/switches.md](../diagnostics/capability-check/references/switches.md),
the skill's own copy of this table in plain words.

A second distinction matters more for the design: **who the answer belongs
to.**

- **Platform facts** — P3, P4, P7, P8, P9, P10, P11, and probably P2 and P5.
  Whether Cowork can see a tracked change is a property of Cowork, not of a
  tenant. Once two tenants agree, it is true for everyone, and the right
  response is to change the shipped card for everyone. That is the process the
  repository already has: `status: probe-gated` becomes `shipped`, the tier is
  discharged, the known issue is closed. No switch is needed.
- **Tenant posture** — P6 (web search can be turned off by an administrator),
  P12 (browser use is off by default), P13 (scheduling), P14 (depends on what
  material the tenant holds), and P1 if scripts ever turn out to be gated by
  policy. These genuinely differ between tenants, and only these need a switch
  that outlives the first confirmation.

So switches earn their keep in two situations: tenant-posture capabilities, and
the **interval** between one tester confirming a platform fact and the
maintainer being willing to change the default for everyone. That interval is
real — the research asks for two tenants before most defaults move — and an
early-adopter tenant should not have to wait out.

## 3. Three ways to switch

### A. Build-time profiles (recommended)

A capability profile — the same `lq-capabilities.md` the probe skill writes —
is fed to the build. Cards carry conditional overlays that apply only when a
named probe has passed in that profile. The build produces a package for that
tenant; the default build, with no profile, is byte-for-byte what ships today.

- **For:** it fits the existing layered design exactly (conditional replace,
  sections and files are just the overlays the contract already has, with a
  condition); the shipped text contains one path only, so no card grows and the
  model never has to choose; everything stays validated, reproducible and
  reviewable; the build report can say which switches took.
- **Against:** a switch needs a rebuild and a re-install, so it needs someone
  with a terminal, or a GitHub Actions workflow that takes a profile as input.
  A tenant-specific package also needs a decision about its identity (section
  7).

### B. Runtime switches (not recommended as the main mechanism)

Each skill reads an attached `lq-capabilities.md`, as it already reads
`lqplaybook.md`, and picks its path from the `[capabilities]` block.

- **For:** one package for everyone, no rebuild.
- **Against:** every affected card must carry both paths, against a body budget
  of about two thousand words; the lawyer must attach the file every session
  (P2 is itself unconfirmed); a stale or hand-edited file could switch off a
  caution silently, which is exactly the failure the cautions exist to prevent;
  and testing has to cover both branches of every card in every tenant.

### C. Try, then say which you got (use it where it already exists)

The card attempts the fuller behaviour and tells the lawyer which form it
produced. It needs no profile at all, and five cards already do it (section 2,
"Already adapts").

- **For:** self-correcting, honest by construction, and it notices the day a
  capability disappears.
- **Against:** only works where a failed attempt is visible to the lawyer. It
  is unusable where the failure is silent — P3 is the example: a document read
  without its tracked changes looks exactly like a clean document.

### Recommendation

- **C** wherever the failure is loud. Extend it rather than adding switches
  (P10 for playbook-review, P6 for lq-ask's optional step).
- **A** for everything in the "switch" row, silent failures above all.
- **B** not at all, except that a skill may keep reading `lqplaybook.md` for
  preferences as it does today.
- Promote a platform fact to the default for everyone as soon as it is
  confirmed in two tenants, and delete the switch.

## 4. Rules a switch must keep

These are the design constraints the tooling and the card reviews enforce.

1. **A switch only ever relaxes an announced degrade.** It never removes a
   guard that catches a silent failure. The guards that stay on regardless:
   read-redline's rule that "no tracked changes" needs a quoted insertion and
   deletion with authors; every register's printed read and written row counts;
   docreview's privilege hold and its hard stop without a register; every
   skill's duty to name a page it could not read; lq-reflect labelling anything
   reconstructed.
2. **Only `pass` switches.** `partial`, `fail`, `disabled` and `unknown` all
   build the cautious path.
3. **A result has an age.** A pass older than a set window (proposal: 180 days)
   still switches but raises a warning in the build, because Cowork changes
   under the skills, and the research dates every fast-moving fact.
4. **The package says what it was built from.** The profile's tenant label and
   date, and every switch that took, go into the built skill's metadata and the
   build report, so a lawyer or an administrator can see why a skill behaves
   differently from the documentation.
5. **The site documents the default build.** A tenant build is a deviation from
   it, stated in its own build report.
6. **The probe skill switches nothing.** It collects evidence; a build acts on
   it.

## 5. What the build would need (for the tooling work, when approved)

Stated as contract changes, not code.

1. **A profile input.** `lqcowork build --profile PATH` (and `package`), reading
   the `[capabilities]` block of an `lq-capabilities.md`. An unknown probe id or
   a malformed line is a config error. No `--profile` means every probe is
   `unknown`, which is today's build.
2. **A condition on overlays.** `replace`, `sections`, `patches` and `files`
   entries may carry `when: P3` (apply only on a pass) or `unless: P3` (apply
   only without one), and a list form for probe sets (sigpack's fuller version
   needs P4 and P8 and one of P2 or P9, though the research treats that as a
   different card, not a switch).
3. **A condition on the `cowork` block.** A known issue may carry
   `resolved_when: P3`; a card may carry `status_when` and `tier_when`
   overrides; the build report and the tenant package's notes use the resolved
   values.
4. **Validation in both states.** CI builds the default and an "every probe
   passes" profile, so a conditional overlay whose anchor text has gone stale
   fails the build even though no real tenant has switched it yet. The
   `when:` probe id must exist in `probes.yaml` (extends `LQC-K003`).
5. **Provenance.** Stamp `metadata.capability-profile` in each built skill, add
   a "Capability profile" section to the build report listing each switch that
   took and its date, and warn on results past the age window.
6. **The probe skill in the build.** A card kind with no upstream source (the
   contract requires `upstream:` today), shipped as `capability-check.skill`
   next to the other single-skill archives but in no bundle.

## 6. Step by step

Each phase stands on its own and can stop there.

### Phase 0 — use the probe skill as it is (no tooling)

1. Zip `diagnostics/capability-check/` as described in
   [diagnostics/README.md](../diagnostics/README.md) and upload it to a test
   tenant.
2. Run **P7a** first: it needs no preparation and tests the skill's own
   template. If it fails, the skill's HTML-page findings for five other skills
   change before anything else does.
3. Run **P3** and **P4**: between them they decide the most switches.
4. Report each result through the UAT form, and file the profile.
5. Adjust the probe skill from what the first real runs show — its wording has
   never met Cowork either.

### Phase 1 — fix what the mapping found, independent of switches

The mapping behind this document turned up mismatches that are worth fixing
whatever is decided about switches:

1. **playbook-review** is listed as unlocked by P3 in `probes.yaml`, but the card
   reads no tracked-changes input; and its known issue tied to P10 tells the
   lawyer they can ask for a tracked-changes copy while the body forbids
   applying tracked changes. Decide which is intended and make the card agree
   with itself.
2. **P7's `unlocks`** names read-redline, docreview and definition-check, none
   of which carries a P7 known issue, and omits legaldesign (which does) and
   cite-check (whose report template depends on it).
3. **P12's `unlocks`** names lq-connect and lq-ask, neither of which mentions
   browser use at all.
4. **lq-connect** ships as `shipped`, though the research asked that it either
   wait for P14 or announce up front that it may not be able to find people.
5. **P2 behaviour is inconsistent:** legalquants and lq-apply look in the Cowork
   folder when told a file is there; lq-reflect's known issue says it does not
   look.
6. Probe tags that exist only on cards (timenarratives on P5, wiki and docreview
   on P2) and probes no card tags (P1, P13): decide whether each is intended.

### Phase 2 — the build learns profiles (the smallest useful switch)

1. Contract change first: section 5's items 1, 2 and 4 above.
2. Tooling: the profile parser, `when`/`unless` on overlays, the all-pass CI
   build.
3. Convert **one card** as the pilot: read-redline on P3. It is the only
   `probe-gated` card today, its switch is well defined (drop the banner and the
   gated status; keep the quote-before-nil rule), and it is the most valuable
   probe in the set.
4. Build a tenant package from a real profile and have the tester re-run the
   read-redline smoke test against it.

### Phase 3 — convert the remaining switch cards

In the order the research's build order implies, each with its own conditional
overlays and a `resolved_when` on its known issue:

1. P4: diligence and docreview (review scans rather than park them),
   closing-bible (inspect scanned execution pages), regulatory (accept a scanned
   official PDF).
2. P14: lq-connect — here the switch runs the other way; the default should gain
   the up-front announcement (Phase 1, item 4), and a pass removes it.
3. P11: lq-reflect (verbatim quotes from the conversation), my-lq-moment (tool
   and skill events as evidence).
4. P2: "look in the Cowork folder by name before asking for the file" across
   sigpack, regulatory, legalquants, lq-reflect, lq-apply, diligence and wiki —
   one shared sentence, so one shared section overlay. docreview keeps its hard
   stop.
5. P8: closing-bible offers the combined bible PDF.
6. P13: diligence, docreview, regulatory, legalquants, lq-reflect offer a
   schedule as a step, naming the cap.

### Phase 4 — make it usable without a terminal

1. A `workflow_dispatch` GitHub Actions workflow that takes a profile file and
   produces the tenant's bundles and `.skill` archives as run artifacts, never
   as a release.
2. A section in [INSTALL.md](INSTALL.md) for administrators: how to get a tenant
   build, and that it replaces the stock plugin rather than sitting beside it
   (section 7, decision 2).

### Phase 5 — promote and retire

When a platform probe is confirmed in two tenants, change the default card for
everyone, remove its switch and its conditional overlays, and close its known
issue. Over time the switches that remain should be only the tenant-posture
ones.

## 7. Decisions needed before Phase 2

1. **Build-time, runtime or both.** This plan recommends build-time profiles
   plus "try and say" (section 3). A runtime switch is possible but spends
   every card's word budget and trusts a file nobody validates.
2. **The identity of a tenant package.** Keep the stock bundle's app id, so a
   tenant build replaces the stock plugin (simplest for an administrator, but
   the version number no longer says everything), or give tenant builds their
   own id (they can sit side by side, and duplicate skill names across enabled
   plugins then become a routing problem).
3. **Whether the probe skill may carry a script and an image.** P1 and P7b
   cannot run from it today because the project ships no scripts. A diagnostic
   package outside every bundle could carry one small script and one small
   image purely to answer those two probes, without changing the no-scripts
   policy for the legal skills. It would be the first code shipped to a tenant
   from this repository, so it is the maintainer's call.
4. **How many tenants confirm a platform fact** before the default changes for
   everyone. The research says two; this plan assumes the same.
5. **The age window** for a pass (section 4, rule 3).
