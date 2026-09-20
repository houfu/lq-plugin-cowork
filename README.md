# lq-plugin-cowork

Three Microsoft 365 Copilot **Cowork** plugin packages built from the open
[LegalQuants skills](https://github.com/LegalQuants/lq-plugin-oss): all
thirty-one legal workflow skills — drafting, cite-checking, discovery, deal
playbooks, closing checklists, diligence, and the companion set — adapted to a
host that works from your OneDrive files rather than a local disk, and that
never says what a bundled script would run in, so these cards ship none. Each
package is a zip with a Teams `manifest.json` (v1.28), two icons and one folder
per skill. The skills contain no code and call no external service; they work
from the files in your Cowork Input and Output folders. These bundles are an
independent adaptation under Apache-2.0: **not an official LegalQuants
release**, and not supported by the upstream project.

Everything here, plus what changed in each skill, the known issues and the
capability probes, is on the site:
**<https://houfu.github.io/lq-plugin-cowork/>**.

## Status

**Pre-release (v0.2.0). Nothing here has been exercised in a live Cowork
tenant.** The packages build, validate and ship reproducibly, and every skill
has been read line by line against what Cowork can actually do — but nothing has
been sideloaded, triggered or run against real documents in Microsoft 365. The
maintainer has no Copilot capacity to do that, **so testers are wanted**:
installing one bundle and typing a handful of prompts is the most useful thing
anyone can do for this repo right now. Start at
[docs/TESTING.md](docs/TESTING.md); every skill has an open
[UAT issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
waiting for a result, and each of the fourteen capability probes has or will
have one of its own.

The site at <https://houfu.github.io/lq-plugin-cowork/> is built from this
repository by GitHub Actions and published from the `main` branch, so it says
the same thing the cards do.

## Get the packages

Built packages are attached to each release:
**[Releases](https://github.com/houfu/lq-plugin-cowork/releases)** ·
[latest](https://github.com/houfu/lq-plugin-cowork/releases/latest). You do not
need to clone this repository to install one.

| Bundle | Who it suits |
| --- | --- |
| [`legalquants-litigation-cowork.zip`](https://github.com/houfu/lq-plugin-cowork/releases/latest/download/legalquants-litigation-cowork.zip) | Litigators and disputes teams: source-grounded workflows for litigators, with the shared daily-practice tools. Drafting, cite-checking, depositions, discovery, document review, case organisation, client reporting. 15 skills. |
| [`legalquants-transactional-cowork.zip`](https://github.com/houfu/lq-plugin-cowork/releases/latest/download/legalquants-transactional-cowork.zip) | Corporate, M&A and commercial teams: contract and deal workflows, with the shared daily-practice tools. Negotiation playbooks, redlines, defined terms, diligence, closing checklists and closing indexes. 14 skills. |
| [`legalquants-companion-cowork.zip`](https://github.com/houfu/lq-plugin-cowork/releases/latest/download/legalquants-companion-cowork.zip) | Any lawyer working out where they stand with AI: your journey with AI as a lawyer — ask, assess, reflect, apply, connect. 8 skills. |

The three mirror the three plugins upstream publishes, skill for skill, so a
skill upstream adds to a group shows up here as a build error rather than as a
silence. Five skills ship in both practice bundles — upstream's `core` group —
and `lq-start` is one of them and also ships in the companion bundle. Install
one to start: they can coexist, but a duplicated skill name across two enabled
plugins is worth reporting.

Every one of the thirty-one skills also ships on its own as a `<name>.skill`
archive — for example
[`regulatory.skill`](https://github.com/houfu/lq-plugin-cowork/releases/latest/download/regulatory.skill)
— small enough to upload straight into Cowork without installing a bundle at
all. [docs/INSTALL.md](docs/INSTALL.md) has the route.

Each release carries the three zips; a `.skill` archive per skill, thirty-one
of them; `<bundle>-trigger-tests.md` for each, the routing acceptance tests
generated from the cards; `build-report.md` — skills, tiers, statuses, known
issues, file counts, adaptation notes and warnings; and
[`SHA256SUMS`](https://github.com/houfu/lq-plugin-cowork/releases/latest/download/SHA256SUMS)
to check any of them against. `latest` always resolves to the newest release
that is not a pre-release: v0.1.0 was published as a pre-release, and from
0.2.0 a release is published as latest unless its tag carries a suffix such as
`-rc.1`, which marks it a pre-release instead. See
[CHANGELOG.md](CHANGELOG.md) for what changed and
[docs/RELEASING.md](docs/RELEASING.md) for how a release is cut.

## Install

Three routes, in full in [docs/INSTALL.md](docs/INSTALL.md), and rendered on the
[site](https://houfu.github.io/lq-plugin-cowork/install.html):

- **Yourself, in Cowork** — Customize page → Plugins tab → upload the `.zip`,
  shared with **Only you**.
- **Your whole tenant** — an administrator uploads it as a custom app in the
  Microsoft 365 admin center and assigns it to users or groups.
- **From a terminal** —
  `npm install -g @microsoft/m365agentstoolkit-cli`, `atk auth login m365`,
  then `atk install --file-path <zip> --scope Personal`.

Whether you can do the first and third depends on your tenant's custom-app
policy. Read [docs/INSTALL.md](docs/INSTALL.md) before promising anyone a demo.

## Test it and report

[docs/TESTING.md](docs/TESTING.md) is the acceptance-testing programme: routing
tests (does the right skill activate?), behaviour tests (does it do what its
description promises?) and the fourteen capability probes (what can Cowork
actually do?), with synthetic inputs and pass criteria for every one. About ten
minutes per skill, and no client material — never use any. Report through the
[UAT report form](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml),
or pick up one of the open
[help wanted issues](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
— one per skill, each carrying that skill's routing checklist; the pinned
[status board](https://github.com/houfu/lq-plugin-cowork/issues/18) links them
all. A misfire is a description problem, and a description is one line in a YAML
card, so a good report usually turns into a one-line fix. A probe result is
worth more than that: several skills move a tier on one.

## What is inside

The **tier** says how far a skill moved from the original. **0** ships as
written apart from its description and the mechanical transforms; **1** stands
only on capabilities Microsoft documents, and fails loudly when it fails; **2**
waits on one named probe, or ships now with a degrade it announces in the
reply; **3** is re-scoped — the promise itself changed, and the description says
so. Each card's own `cowork.tier` is the record, and the site renders it beside
the paragraph saying what differs and the known issues that follow from it.

Shared by the litigation and transactional bundles (upstream's `core` group):

| Skill | Bundle(s) | Tier | What it does |
| --- | --- | --- | --- |
| `lq-start` | all three | 1 | Names the one skill that fits the work in front of you, with the sentence to type, or lays out the whole map of all three bundles. |
| `legaldesign` | litigation, transactional | 1 | Turns work already done into one polished, evidence-grounded HTML one-pager or slide brief that opens in the preview pane. |
| `regulatory` | litigation, transactional | 1 | Answers what a regulation requires from the publisher's own document you downloaded and attested to, quoted verbatim with its version and date. |
| `timenarratives` | litigation, transactional | 2 | Drafts time-entry narratives for a named lawyer and matter from the conversation and supplied documents — no hours, rates or billability. |
| `wiki` | litigation, transactional | 1 | Keeps a personal legal wiki as linked Markdown notes in a folder you own, and answers from it: reusable law and method, never matter facts. |

The litigation bundle:

| Skill | Bundle(s) | Tier | What it does |
| --- | --- | --- | --- |
| `writing` | litigation | 0 | Drafts and revises advocacy — pleadings, motions, briefs, hearing outlines — and neutral client analysis, tied to the supplied record. |
| `correspondence` | litigation | 0 | Triages inbound litigation correspondence and drafts meet-and-confer letters, settlement demands and counteroffers, with an explicit no-send gate. |
| `client-update` | litigation | 0 | Prepares evidence-first status reporting: matter updates, decision addenda, outside-counsel reports and portfolio views. It drafts; it never sends. |
| `depositions` | litigation | 0 | Plans a deposition end to end — objectives, chronology, exhibits, outlines, Rule 30(b)(6) topics, witness preparation — and mines the deposition transcript afterwards. |
| `new-matter` | litigation | 0 | Opens a litigation matter through a human-confirmed intake and produces one reviewable matter record, shown for approval before anything is saved. |
| `organize-case-docs` | litigation | 0 | Turns a matter's documents into a provenance-backed workspace: source manifest, chronology with locators, proof chart, trackers, briefing. |
| `cite-check` | litigation | 2 | Checks citations, quotations and pincites in a brief against the authorities you supply, and produces a colour-coded HTML report. |
| `pressuretest` | litigation | 1 | Attacks a legal position against the documents supplied for it — logic, dates, figures, cross-document consistency — and adjudicates every attack. |
| `document-discovery` | litigation | 1 | Plans and drafts U.S. federal preservation and discovery work: legal holds, request sets, itemised responses and objections, subpoena triage, privilege-log queues. |
| `docreview` | litigation | 2 | Works a production tranche by tranche into a workbook, with privilege state as its first column and no findings at all when the register is missing. |

The transactional bundle:

| Skill | Bundle(s) | Tier | What it does |
| --- | --- | --- | --- |
| `closing-checklist` | transactional | 0 | Drafts an editable Word closing checklist from the anchor agreement, or updates an existing one against revised documents. |
| `playbook-builder` | transactional | 1 | Builds or updates an approved contract playbook in Markdown from precedents and negotiated agreements, every position linked to its source text. |
| `playbook-review` | transactional | 2 | Reviews a counterparty draft against that playbook and returns a clause-anchored issues list with proposed wording, internal guidance and an external comment. |
| `read-redline` | transactional | 2 | Reads the redline the other side sent back: the Word path first, themes, an issues list and an HTML marked-passage view, and no annotated PDF. |
| `sigpack` | transactional | 3 | Works out the signing matrix, drafts the pages, the instructions and the cover note and keeps the chase list; it never compiles an executed set. |
| `closing-bible` | transactional | 3 | Builds the closing index and the exceptions list into an Excel status register you can sort; never a receipt, and never the combined bible PDF. |
| `definition-check` | transactional | 2 | Reviews an agreement's defined terms: the real problems on top, an Excel definitions register under them, and a stated count of the clauses read. |
| `conform` | transactional | 3 | Refits a precedent clause to your agreement's vocabulary, both documents read in the one session, so there is no ledger and no hash to go stale. |
| `diligence` | transactional | 2 | Works a data room tranche by tranche into an Excel master register that carries the state and shows the coverage arithmetic; never coverage-certified. |

The companion bundle:

| Skill | Bundle(s) | Tier | What it does |
| --- | --- | --- | --- |
| `lq-mirror` | companion | 1 | A twelve-question conversation about how you actually work with AI, giving back an honest reading, an archetype and one move for the week. |
| `legalquants` | companion | 3 | A returning-lawyer conversation: where you are and one next step, remembering only what you bring into the session. |
| `lq-ask` | companion | 3 | Answers what other lawyers have published about working this way, from a dated library shipped with the skill, cited by title and date. |
| `lq-connect` | companion | 3 | Finds two or three colleagues inside your organisation who have actually done the thing, each grounded in a document it quotes; or matches a list you bring. |
| `lq-reflect` | companion | 3 | Reviews the piece of work in front of you — this conversation plus what you attach — and leaves one change to keep in a dated note you carry. |
| `lq-apply` | companion | 3 | Turns confirmed evidence into a legal-AI CV or a public profile, with an honest gap account: gaps are asked, never filled. |
| `my-lq-moment` | companion | 2 | Judges whether a session was genuinely the good kind, and if it was, gives you the write-up, a post in your own voice and a cover card. Nothing is kept. |

Manifest ids, names, descriptions and bundle membership live only in
`cowork.yaml`. Built skills are in `dist/<bundle>/skills/<name>/SKILL.md` after
a build, and inside each zip.

## What changed from the original

Every upstream skill ships. Fourteen of them ship as something their authors
would recognise but should not mistake for the same skill, because each of the
fourteen leans on machinery a Cowork package cannot carry — a local disk and a
working directory that outlives the task, bundled binaries such as LibreOffice
and Tesseract, raw fetched bytes that can be hashed into a receipt, and the
agent's own past session logs. Cowork does reach the web where a tenant allows
it, and Microsoft documents a skill's `scripts/` folder as executed — but no
page names the interpreter, the packages or the binaries a script could count
on, companion files are capped at 20 files and 10 MB, and nothing hands a skill
a URL's raw bytes to hash. Shipping these as prose would ship the instructions
without the machinery — a skill that promises receipts it cannot produce is
worse than no skill.

So none of them does. Each is instead a Cowork-native adaptation, with the
legal method kept and the mechanism replaced:
state the lawyer carries in an attached file instead of a private store, an
Excel register the lawyer can sort and check instead of a count a script used to
compute, an HTML page in the preview pane instead of a rendered image, one
session working sequentially instead of parallel workers, and the publisher's
own document placed by a human instead of a fetch. Where that changes what the
skill can promise, the tier says so and the description says so before the work
starts rather than after.

Skill by skill — what differs, the known issues with their failure modes, and
the probe that would settle each one — is on the site:
[what changed](https://houfu.github.io/lq-plugin-cowork/differences.html) and
[known issues](https://houfu.github.io/lq-plugin-cowork/known-issues.html). The
[probes](https://houfu.github.io/lq-plugin-cowork/probes.html) are the fourteen
questions about Cowork that nobody has answered in a live tenant; several skills
move a tier the day one of them comes back.

Two skills have a fuller version behind a remote MCP connector declared under
`agentConnectors` — a server somebody has to operate, which restores the
guarantee rather than working around it. That is not in this release.
[CONTRIBUTING.md](CONTRIBUTING.md) section 4 says what adapting one of these
skills involves, and what a card has to carry before it can ship.

## Building from source

```sh
git submodule update --init          # if you have not already
uv sync --project tools              # or: make setup
make package
```

`dist/` then holds, per bundle: the built tree, `<bundle>.zip`,
`<bundle>-trigger-tests.md`, and a shared `build-report.md`. `make site` builds
the static site into `dist/site/` from the same sources.

Upstream is vendored read-only as a git submodule at `upstream/`, pinned to an
exact commit; nothing here edits it. Rather than fork the skills, the build
adapts them in layers ordered by how brittle each layer is — a selection
manifest (`cowork.yaml`), mechanical transforms applied to every skill, a
per-skill `description` override, literal replacements with expected counts,
heading-anchored section overlays, unified-diff patches, and only as a last
resort a full-file `SKILL.md` overlay. Always prefer the highest layer that does
the job: the higher the layer, the less an upstream release can silently break
it. The full specification — config schema, pipeline order, every validation
code, CLI behaviour — is [docs/CONTRACT.md](docs/CONTRACT.md); change the
contract first, then the code. [docs/DEVELOPING.md](docs/DEVELOPING.md) covers
the tooling itself: module layout, tests and fixtures.

### Commands

Every target is a thin wrapper around `uv run --project tools lqcowork …`.

| Target | What it does |
| --- | --- |
| `make setup` | `uv sync --project tools` |
| `make build` | build `dist/<bundle>/` trees only |
| `make validate` | validate `dist/<bundle>/` without rebuilding |
| `make package` | build + validate + zip + trigger tests + build report |
| `make site` | render the static site into `dist/site/` from a built `dist/` |
| `make triggers` | write `dist/<bundle>-trigger-tests.md` only |
| `make drift` | `bump-upstream --dry-run`: report drift, move nothing |
| `make bump` | fetch upstream, report, move the submodule and the pin |
| `make anchor` | set every card's `anchored_to` to the current pin |
| `make test` | `pytest tools/tests` |
| `make fmt` / `make fmt-check` | `black tools`, and the check CI runs |
| `make release-check TAG=vX.Y.Z` | does the tag agree with `cowork.yaml`, `CHANGELOG.md` and `dist/`? |
| `make release TAG=vX.Y.Z` | check, tag, push; CI publishes ([docs/RELEASING.md](docs/RELEASING.md)) |
| `make clean` | `rm -rf dist` |

`--out DIR` sends a build somewhere other than `dist/`, which is what keeps two
people building at once from treading on each other. Useful variables:
`BUNDLE=<id>` restricts build/validate/package/triggers, `TO=<ref>` picks what
bump/drift resolve (default `origin/main`), `SKILL=<name>` restricts `anchor`,
`REPORT=<path>` moves the drift report. Exit codes: `0` success, `1` error (bad
config, missing card, git failure), `2` validation, anchor or release-check
failure.

### Adding or adjusting a skill, and bumping upstream

One folder per shipped skill: `skills/<name>/skill.yaml` (the card, required),
plus optional `SKILL.md` (full-file overlay, last resort), `sections/*.md`,
`patches/*.patch` and `files/**`. Every card carries a `cowork:` block — tier,
status, the paragraph a lawyer reads about how the skill differs, its known
issues and its workarounds — and the build refuses a card without one. While a
card is being written, `uv run --project tools lqcowork build --skill <name>`
builds that one skill and runs its checks without needing it to be in a
buildable bundle. Cards, the layer ladder, `suppress:`, what the build warns
about and how to read `dist/upstream-drift.md` after `make drift` or `make bump`
are all in [CONTRIBUTING.md](CONTRIBUTING.md); section 4 of the contract has the
full card schema and section 6 every error and warning code.

## Licence and attribution

Upstream is Apache-2.0 and so is everything here. Section 4(b) of that licence
requires modified files to carry prominent notices, so the build stamps them:

- every shipped `SKILL.md` carries a modification notice as its first body line,
  naming the exact upstream commit it was adapted from, and repeats that commit
  in frontmatter under `metadata.adapted-from`;
- every Markdown companion the adaptation changed carries the same notice as its
  first line, naming its own path; one this repository added carries an "Added
  by the lq-plugin-cowork adaptation" notice instead; one byte-identical to
  upstream is left exactly as upstream wrote it. The build cannot annotate a
  non-Markdown companion, so any that changed are listed in
  `dist/build-report.md` under "Companions changed without an in-file notice"
  and must be accounted for in the card's `notes`;
- upstream's `LICENSE` travels at the root of every zip, and
  [`NOTICE.md`](NOTICE.md) beside it, describing the kind of changes made and
  where the originals live.

Symlinks are never followed and never packaged: one under a skill folder is an
error (`LQC-C007`), because a link is the easy way for content nobody reviewed
to end up inside a shipped zip. Packages are byte-reproducible — every zip entry
is stamped 1980-01-01 unless `SOURCE_DATE_EPOCH` says otherwise — so two builds
of the same commit produce identical archives.

The manifest's `developer` block names LegalQuants because that is who wrote the
skills these packages adapt. It does not mean LegalQuants published, endorsed or
supports this package. The bundles are an independent adaptation: not an
official LegalQuants release, not endorsed by the upstream project, not
supported by it. Report a problem with an adapted skill
[here](https://github.com/houfu/lq-plugin-cowork/issues), not upstream.

LegalQuants skills are a workflow aid, not legal advice. The judgement stays
yours.
