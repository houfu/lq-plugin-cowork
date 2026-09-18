# lq-plugin-cowork

Turns the open [LegalQuants skills](https://github.com/LegalQuants/lq-plugin-oss)
into Microsoft 365 Copilot **Cowork** plugin packages: a zip per bundle with a
Teams `manifest.json` (v1.28), two icons, and one folder per skill under
`skills/`. Upstream is vendored read-only as a git submodule at `upstream/`
and pinned to an exact commit; nothing here edits it.

These packages are an independent adaptation under Apache-2.0. They are not an
official LegalQuants release.

## The layered adaptation model

Cowork is a different host from the one upstream writes for: no filesystem, no
shell, no `$name` or `/name` invocation grammar, and a router that picks a
skill from its `description` alone. Rather than fork the skills, this repo
adapts them in layers ordered by how brittle each layer is — a selection
manifest (`cowork.yaml`), then mechanical transforms the build applies to every
skill, then a per-skill `description` override, then literal string
replacements with expected counts, then heading-anchored section overlays, then
unified-diff patches, and only as a last resort a full-file `SKILL.md` overlay.
Always prefer the highest layer that does the job: the higher the layer, the
less an upstream release can silently break it. The full specification — config
schema, the exact pipeline order, every validation code, CLI behaviour — is
[docs/CONTRACT.md](docs/CONTRACT.md). Change the contract first, then the code.

## Quick start

```sh
git submodule update --init          # if you have not already
uv sync --project tools              # or: make setup
make package
```

`dist/` then holds, per bundle: the built tree, `<bundle>.zip`,
`<bundle>-trigger-tests.md`, and a shared `build-report.md`.

## Commands

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
| `make test` | `pytest` (root `pytest.ini` points it at `tools/tests`) |
| `make fmt` | `black tools` |
| `make clean` | `rm -rf dist` |

`--out DIR` sends a build somewhere other than `dist/`, which is what keeps two
people building at once from treading on each other.

Useful variables: `BUNDLE=<id>` restricts build/validate/package/triggers,
`TO=<ref>` picks what bump/drift resolve (default `origin/main`),
`SKILL=<name>` restricts `anchor`, `REPORT=<path>` moves the drift report.

Exit codes: `0` success, `1` error (bad config, missing card, git failure),
`2` validation or anchor failure.

## Adding or adjusting a skill

One folder per shipped skill, named after the skill:

```
skills/<name>/
  skill.yaml        # the card (required)
  SKILL.md          # full-file overlay (optional, last resort)
  sections/*.md     # section overlay bodies (optional)
  patches/*.patch   # unified diffs (optional)
  files/**          # extra or replacement companion files (optional)
```

To add a skill: create `skills/<name>/skill.yaml` with `name`, `upstream`
(`<group>/<name>` under `upstream/skills/`), `anchored_to` (the SHA in
`cowork.yaml`), a Cowork-shaped `description`, and `triggers` (3-5 positive
prompts, 3-5 negative ones each tagged `-> other-skill`). Add `notes` when the
card's `bucket` is `amber`. Then list the skill in the right bundle in
`cowork.yaml` and run `make package`.

To adjust one: reach for the highest layer that works — `exclude` a companion
folder, then `replace` an exact string (with `expect:` so a silent upstream
rename fails loudly), then a `sections:` overlay keyed on the heading line,
then a patch.

When a warning is correct to leave in place — upstream's own authority links in
a reference file, say — record the decision in the card rather than silencing
it globally:

```yaml
suppress:
  - code: LQC-W010
    file: "references/getting-authorities.md"   # optional glob; omit for the whole skill
    reason: "upstream-authored court and legislation URLs"
```

`code` must be a warning; an error can never be suppressed. `reason` is
required, and every suppression is listed in `dist/build-report.md` under
"Suppressed warnings", so the decision stays visible.

Section 4 of the contract has the full card schema, and section 6
lists every error and warning code the build can emit.

## What the build warns about

Errors fail the build; warnings are printed, listed in `dist/build-report.md`
and left for the card owner to judge. Every warning reports `file:line`, and
all of them run over every `*.md` in the built skill unless the rule names
SKILL.md.

| Code | What it means |
| --- | --- |
| `LQC-W001` | a vendor word survives (`Codex`, `ChatGPT`, `Claude`, …) |
| `LQC-W002` | a `$name` or `` `/name` `` invocation token survives |
| `LQC-W003` | SKILL.md names a skill that is not in the same bundle |
| `LQC-W004` | a path escapes the skill folder (`../`), or a relative Markdown link points at a file that is not packaged |
| `LQC-W005` | `scripts/` or `schemas/` is mentioned but not packaged |
| `LQC-W006` | the SKILL.md body runs past 3,000 words |
| `LQC-W007` | `hooks`, `~/.lq/`, `CLAUDE_PLUGIN_ROOT`, `argument-hint` or `disable-model-invocation` is mentioned |
| `LQC-W008` | an amber card has no `notes` |
| `LQC-W009` | a phrase from `transforms.host_words` survives — host machinery Cowork does not have (`the scribe`, `exit code`, `subprocess`, …) |
| `LQC-W010` | an external `http(s)://` URL the adaptation introduced; a URL that appears anywhere in the upstream skill folder is upstream's and stays exempt wherever it was moved to |

## Bumping upstream

```sh
make drift          # report only; the submodule and the pin do not move
make bump           # fetch, report, check out the new SHA, rewrite the pin
```

`drift` fetches upstream, resolves `TO` (default `origin/main`), creates a
temporary git worktree at that commit and builds every bundle against it with
anchor failures downgraded to report entries. The report lands in
`dist/upstream-drift.md` and lists, per skill: whether the upstream folder
still exists, whether its `SKILL.md` or `description` changed since the card's
`anchored_to`, companion files added or removed upstream, whether a full-file
overlay's base moved, plus every anchor failure, validation error and warning,
and any upstream skill that is in no bundle. Read it top to bottom: rows under
"Skills that moved upstream" are things to re-read; rows under "Anchor
failures" are things that will not build until a card is fixed.

After `make bump`, fix whatever the report flagged, re-run `make package`, and
then `make anchor` to record that each card has been reviewed against the new
pin. `make anchor SKILL=<name>` does one card at a time.

## Sideloading and testing triggers

```sh
npm install -g @microsoft/m365agentstoolkit-cli
atk auth login
atk install --file-path dist/legalquants-litigation-cowork.zip --scope Personal
```

Then open `dist/<bundle>-trigger-tests.md`. It is a checklist table per skill:
each positive prompt must activate that skill, each negative prompt must not
(the arrow names the skill that should take it instead). Type each prompt into
Cowork in a fresh session, record what actually activated in the Result column,
and treat every surprise as a `description` problem — the description is the
only thing Cowork routes on, so overlapping descriptions and missing hand-offs
are what misfires.

## Bundles

| Bundle | Skills |
| --- | --- |
| `legalquants-litigation-cowork` | lq-start, writing, correspondence, client-update, depositions, new-matter, organize-case-docs, cite-check, pressuretest, document-discovery, legaldesign, timenarratives, wiki, closing-checklist, lq-mirror |
| `legalquants-transactional-cowork` | lq-start, closing-checklist, playbook-builder, playbook-review, legaldesign, timenarratives, wiki, lq-mirror |

Manifest ids, names, descriptions and membership live only in `cowork.yaml`.

## What is deliberately left out

Fourteen of the thirty-one upstream skills do not ship, and this is a decision
rather than a backlog. Each of them is a thin instruction layer over something
Cowork does not have:

| Skill | Depends on |
| --- | --- |
| read-redline, sigpack, closing-bible, definition-check, conform | local Python pipelines that do the actual work |
| diligence, docreview | local parallel worker runtimes plus fail-closed receipt gates |
| regulatory | scripts that fetch from the network |
| legalquants, lq-ask, lq-connect | a local `~/.lq/` store and a community corpus behind a connector |
| lq-reflect, lq-apply, my-lq-moment | host session transcripts |

Cowork has no filesystem, no shell, no network fetch and no transcript access,
so shipping these as prose would ship the instructions without the machinery —
a skill that promises receipts it cannot produce is worse than no skill. The
honest long-term route for this group is a remote MCP connector declared in the
manifest under `agentConnectors`, which keeps the pipeline server-side and
leaves Cowork doing what it is good at. That is out of scope for this repo as
it stands.

## Licence and attribution

Upstream is Apache-2.0 and so is everything here. Section 4(b) of that licence
requires modified files to carry prominent notices, so:

- every shipped `SKILL.md` carries a modification notice as its first body
  line, naming the exact upstream commit it was adapted from, and repeats that
  commit in frontmatter under `metadata.adapted-from`;
- every Markdown companion the adaptation changed carries the same notice as
  its first line, naming its own path; a companion this repository added
  carries an "Added by the lq-plugin-cowork adaptation" notice instead; a
  companion that is byte-identical to upstream is left exactly as upstream
  wrote it. The build cannot annotate a non-Markdown companion, so any that
  changed are listed in `dist/build-report.md` under "Companions changed
  without an in-file notice" and must be accounted for in the card's `notes`;
- upstream's `LICENSE` travels at the root of every zip;
- [`NOTICE.md`](NOTICE.md) travels beside it, describing the kind of changes
  made and where the originals live.

Symlinks are never followed and never packaged: one under a skill folder is an
error (`LQC-C007`), because a link is the easy way for content nobody reviewed
to end up inside a shipped zip. Packages are also byte-reproducible — every zip
entry is stamped 1980-01-01 unless `SOURCE_DATE_EPOCH` says otherwise — so two
builds of the same commit produce identical archives.

The bundles are an independent adaptation. They are not an official
LegalQuants release, are not endorsed by the upstream project, and are not
supported by it.
