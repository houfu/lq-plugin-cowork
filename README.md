# lq-plugin-cowork

Two Microsoft 365 Copilot **Cowork** plugin packages built from the open
[LegalQuants skills](https://github.com/LegalQuants/lq-plugin-oss): seventeen
legal workflow skills — drafting, cite-checking, discovery, deal playbooks,
closing checklists — adapted to a host with no filesystem and no shell. Each
package is a zip with a Teams `manifest.json` (v1.28), two icons and one folder
per skill. The skills contain no code and call no external service; they work
from the files in your Cowork Input and Output folders. These bundles are an
independent adaptation under Apache-2.0: **not an official LegalQuants
release**, and not supported by the upstream project.

## Status

**Pre-release (v0.1.0). Nothing here has been exercised in a live Cowork
tenant.** The packages build, validate and ship reproducibly, and every skill
has been read line by line against what Cowork can actually do — but nothing has
been sideloaded, triggered or run against real documents in Microsoft 365. The
maintainer has no Copilot capacity to do that, **so testers are wanted**:
installing one bundle and typing a handful of prompts is the most useful thing
anyone can do for this repo right now. Start at
[docs/TESTING.md](docs/TESTING.md); every skill has an open
[UAT issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
waiting for a result.

## Get the skills

**[Releases](https://github.com/houfu/lq-plugin-cowork/releases)** ·
[latest](https://github.com/houfu/lq-plugin-cowork/releases/latest). You do not
need to clone this repository to install anything — and a GitHub **Code >
Download ZIP** of this repository, or of a `skills/<name>/` folder, is **not**
installable: those are build inputs (see [skills/README.md](skills/README.md)),
not a working skill.

| Route | Download | How | Good for |
| --- | --- | --- | --- |
| Upload one skill | `<name>.skill` from the release | Cowork **Customize** > **Skills** tab > arrow next to **Add** > **Upload skill** | A lawyer testing a single skill: no admin, no terminal |
| Install the full plugin | one of the two bundle `.zip` files below | see [docs/INSTALL.md](docs/INSTALL.md) | A tester or team wanting the whole bundle |
| Developer source | clone the repo | `skills/<name>/` folders are build inputs, not skills; `make package` builds everything | Working on the adaptation itself |

| Bundle | Who it suits |
| --- | --- |
| `legalquants-litigation-cowork.zip` | Litigators and disputes teams: drafting, cite-checking, depositions, discovery, case organisation, client reporting. 15 skills. |
| `legalquants-transactional-cowork.zip` | Corporate, M&A and commercial teams: negotiation playbooks, playbook review, closing checklists. 8 skills. |

Six skills are in both bundles. Install one to start: the two can coexist, but a
duplicated skill name across two enabled plugins is worth reporting.

Each release carries: the two bundle zips; one `<name>.skill` upload-ready
archive per skill (17, contract section 5b) for the single-skill route above;
`<bundle>-trigger-tests.md` for each bundle, the routing acceptance tests
generated from the cards; `build-report.md` — skills, buckets, file counts,
adaptation notes and warnings; and `SHA256SUMS`. v0.1.0 is marked a GitHub
pre-release. See [CHANGELOG.md](CHANGELOG.md) for what changed and
[docs/RELEASING.md](docs/RELEASING.md) for how a release is cut.

## Install

Three routes, in full in [docs/INSTALL.md](docs/INSTALL.md):

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
tests (does the right skill activate?) and behaviour tests (does it do what its
description promises?), with synthetic inputs and pass criteria for every skill.
About ten minutes per skill, and no client material — never use any. Report
through the
[UAT report form](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml),
or pick up one of the open
[help wanted issues](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
— one per skill, each carrying that skill's routing checklist; the pinned
[status board](https://github.com/houfu/lq-plugin-cowork/issues/18) links all
seventeen. A misfire is a description problem, and a description is one line in
a YAML card, so a good report usually turns into a one-line fix.

## What is inside

| Skill | Bundle | What it does |
| --- | --- | --- |
| `lq-start` | both | Names the one skill that fits the work in front of you, with the sentence to type, or lays out the whole map of both bundles. |
| `legaldesign` | both | Turns work already done into one polished, evidence-grounded HTML one-pager or slide brief that opens in the preview pane. |
| `timenarratives` | both | Drafts time-entry narratives for a named lawyer and matter from the conversation and supplied documents — no hours, rates or billability. |
| `wiki` | both | Keeps a personal legal wiki as linked Markdown notes in a folder you own, and answers from it: reusable law and method, never matter facts. |
| `closing-checklist` | both | Drafts an editable Word closing checklist from the anchor agreement, or updates an existing one against revised documents. |
| `lq-mirror` | both | A twelve-question conversation about how you actually work with AI, giving back an honest reading, an archetype and one move for the week. |
| `writing` | litigation | Drafts and revises advocacy — pleadings, motions, briefs, hearing outlines — and neutral client analysis, tied to the supplied record. |
| `correspondence` | litigation | Triages inbound litigation correspondence and drafts meet-and-confer letters, settlement demands and counteroffers, with an explicit no-send gate. |
| `client-update` | litigation | Prepares evidence-first status reporting: matter updates, decision addenda, outside-counsel reports and portfolio views. It drafts; it never sends. |
| `depositions` | litigation | Plans a deposition end to end — objectives, chronology, exhibits, outlines, Rule 30(b)(6) topics, witness preparation — and mines the transcript afterwards. |
| `new-matter` | litigation | Opens a litigation matter through a human-confirmed intake and produces one reviewable matter record, shown for approval before anything is saved. |
| `organize-case-docs` | litigation | Turns a matter's documents into a provenance-backed workspace: source manifest, chronology with locators, proof chart, trackers, briefing. |
| `cite-check` | litigation | Checks citations, quotations and pincites in a brief against the authorities you supply, and produces a colour-coded HTML report. |
| `pressuretest` | litigation | Attacks a legal position against the documents supplied for it — logic, dates, figures, cross-document consistency — and adjudicates every attack. |
| `document-discovery` | litigation | Plans and drafts U.S. federal preservation and discovery work: legal holds, request sets, itemised responses and objections, subpoena triage, privilege-log queues. |
| `playbook-builder` | transactional | Builds or updates an approved contract playbook in Markdown from precedents and negotiated agreements, every position linked to its source text. |
| `playbook-review` | transactional | Reviews a counterparty draft against that playbook and returns a clause-anchored issues list with proposed wording, internal guidance and an external comment. |

Manifest ids, names, descriptions and bundle membership live only in
`cowork.yaml`. Built skills are in `dist/<bundle>/skills/<name>/SKILL.md` after
a build, and inside each zip.

## What is deliberately left out

Fourteen of the thirty-one upstream skills do not ship, and this is a decision
rather than a backlog. Each is a thin instruction layer over something Cowork
does not have:

| Skill | Depends on |
| --- | --- |
| read-redline, sigpack, closing-bible, definition-check, conform | local Python pipelines that do the actual work |
| diligence, docreview | local parallel worker runtimes plus fail-closed receipt gates |
| regulatory | scripts that fetch from the network |
| legalquants, lq-ask, lq-connect | a local `~/.lq/` store and a community corpus behind a connector |
| lq-reflect, lq-apply, my-lq-moment | host session transcripts |

Cowork has no filesystem, no shell, no network fetch and no transcript access,
so shipping these as prose would ship the instructions without the machinery — a
skill that promises receipts it cannot produce is worse than no skill. The
honest long-term route for this group is a remote MCP connector declared under
`agentConnectors`, which keeps the pipeline server-side. That is out of scope
here, and porting one is not a contribution this repo wants; see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Building from source

```sh
git submodule update --init          # if you have not already
uv sync --project tools              # or: make setup
make package
```

`dist/` then holds, per bundle: the built tree, `<bundle>.zip`,
`<bundle>-trigger-tests.md`, and a shared `build-report.md`.

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
`patches/*.patch` and `files/**`. Cards, the layer ladder, `suppress:`, what the
build warns about and how to read `dist/upstream-drift.md` after `make drift` or
`make bump` are all in [CONTRIBUTING.md](CONTRIBUTING.md); section 4 of the
contract has the full card schema and section 6 every error and warning code.

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
