# Contributing

This repository adapts the open [LegalQuants
skills](https://github.com/LegalQuants/lq-plugin-oss) into two Microsoft 365
Copilot Cowork plugin packages. It is a small, opinionated build, and the most
valuable contribution right now has nothing to do with Python.

## Ways to help

### 1. Test a bundle in a real tenant and report what happened

This is the one the project actually needs. Nothing here has been run in a live
Cowork tenant. If you have Microsoft 365 Copilot with Cowork, install a bundle
([docs/INSTALL.md](docs/INSTALL.md)), work through
[docs/TESTING.md](docs/TESTING.md), and file what you saw with the
[UAT report form](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml).
There is one open
[help wanted issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
per skill, each carrying that skill's routing checklist; claim one in a comment
so two people do not test the same thing.

A negative result is a result. "Typed the prompt, a different skill answered" is
the single most useful sentence you can send. Sanitise everything and never
paste client material — see Part C of [docs/TESTING.md](docs/TESTING.md).

### 2. Fix a description

Cowork routes on a skill's `description` and nothing else, so a misfire is a
description problem, not a code problem. The fix is an edit to
`skills/<name>/skill.yaml`: sharpen the trigger phrases, add the missing
hand-off sentence ("Do not use for X (use the Y skill)"), or adjust the
overlapping neighbour's description in the same pull request. Add the prompt
that misfired to that card's `triggers` so the regression is recorded, then run
`make package` and check `dist/<bundle>-trigger-tests.md`.

Descriptions are capped at 1024 characters (`LQC-D001`), so every sentence has
to earn its place.

### 3. Review or improve a section overlay

Every amber card carries `notes` recording what the adaptation changed from
upstream and why. Those notes are where the judgement calls live, and a second
reader is welcome: does the rewritten section still carry the legal method
upstream intended, or did something load-bearing go out with the scripts?
Compare `upstream/skills/<group>/<name>/SKILL.md` with
`dist/<bundle>/skills/<name>/SKILL.md` and say what you find. If you change an
overlay, update the card's `notes` in the same commit — that is the record.

### 4. Porting a left-out skill: out of scope

Fourteen upstream skills are deliberately not shipped (see the README). Each is
a thin instruction layer over a local Python pipeline, a worker runtime, a
network fetch, a `~/.lq/` store or host session transcripts — none of which
Cowork has. Shipping one as prose would ship the instructions without the
machinery, and a skill that promises receipts it cannot produce is worse than no
skill. A pull request that ports one will be declined on that ground alone. The
honest route for that group is a remote MCP connector declared under
`agentConnectors`, which keeps the pipeline server-side; that is a different
project from this one.

## Setup

```sh
git clone --recurse-submodules https://github.com/houfu/lq-plugin-cowork
uv sync --project tools     # or: make setup
make package
```

[docs/DEVELOPING.md](docs/DEVELOPING.md) covers the tooling itself: module
layout, the test suite and how the fixtures work.
[docs/CONTRACT.md](docs/CONTRACT.md) is the specification — config schema,
pipeline order, every validation code, CLI behaviour. Change the contract first,
then the code.

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

To add a skill, create `skills/<name>/skill.yaml` with `name`, `upstream`
(`<group>/<name>` under `upstream/skills/`), `anchored_to` (the SHA in
`cowork.yaml`), a Cowork-shaped `description`, and `triggers` (3-5 positive
prompts, 3-5 negative ones each tagged `-> other-skill`). Add `notes` when the
card's `bucket` is `amber`. Then list the skill in the right bundle in
`cowork.yaml` and run `make package`.

To adjust one, reach for the **highest layer that does the job** — the higher
the layer, the less an upstream release can silently break it:

1. `exclude` a companion file or folder;
2. `replace` an exact string, with `expect:` so a silent upstream rename fails
   loudly instead of quietly doing nothing;
3. a `sections:` overlay keyed on the heading line;
4. a unified-diff patch;
5. a full-file `SKILL.md` overlay — last resort, and it has to be re-read on
   every upstream bump.

When a warning is correct to leave in place — upstream's own authority links in
a reference file, say — record the decision in the card rather than silencing it
globally:

```yaml
suppress:
  - code: LQC-W010
    file: "references/getting-authorities.md"   # optional glob; omit for the whole skill
    reason: "upstream-authored court and legislation URLs"
```

`code` must be a warning; an error can never be suppressed. `reason` is
required, and every suppression is listed in `dist/build-report.md` under
"Suppressed warnings", so the decision stays visible. Section 4 of the contract
has the full card schema.

## What the build warns about

Errors fail the build; warnings are printed, listed in `dist/build-report.md`
and left for the card owner to judge. Every warning reports `file:line`, and all
of them run over every `*.md` in the built skill unless the rule names SKILL.md.

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

Section 6 of [docs/CONTRACT.md](docs/CONTRACT.md) is the authoritative list,
including every error code.

## Bumping upstream

```sh
make drift          # report only; the submodule and the pin do not move
make bump           # fetch, report, check out the new SHA, rewrite the pin
```

`drift` fetches upstream, resolves `TO` (default `origin/main`), creates a
temporary git worktree at that commit and builds every bundle against it with
anchor failures downgraded to report entries. The report lands in
`dist/upstream-drift.md` and lists, per skill: whether the upstream folder still
exists, whether its `SKILL.md` or `description` changed since the card's
`anchored_to`, companion files added or removed upstream, whether a full-file
overlay's base moved, plus every anchor failure, validation error and warning,
and any upstream skill that is in no bundle. Read it top to bottom: rows under
"Skills that moved upstream" are things to re-read; rows under "Anchor failures"
are things that will not build until a card is fixed.

After `make bump`, fix whatever the report flagged, re-run `make package`, and
then `make anchor` to record that each card has been reviewed against the new
pin. `make anchor SKILL=<name>` does one card at a time.

## Never edit `upstream/`

`upstream/` is a read-only git submodule pinned to an exact commit. Nothing in
this repository edits it, and a pull request that does will be declined: the
whole point of the layer ladder is that an upstream release can be pulled in
without re-doing the adaptation by hand. If upstream is wrong, fix it upstream.

## Pull requests

The template asks four things, and they are the whole review:

- **Highest layer that works.** If a `replace` would have done it, do not ship a
  patch; if a section overlay would have done it, do not ship a full-file
  overlay. Say in the PR why the layer you picked was necessary.
- **`make package` is green.** No new errors; new warnings explained or
  suppressed with a `reason`. Run `make test` too, and `make fmt` if you touched
  Python (black, line length 88).
- **Card `notes` updated.** If the built output changed, the card says what
  changed and why. An amber card without `notes` fails the build (`LQC-W008`).
- **No edits under `upstream/`.**

Keep pull requests small and single-purpose — one skill, or one tooling change.
A description fix and a build change do not belong in the same branch.

## Licensing

This project is Apache-2.0, like upstream. By contributing you agree that your
contribution is licensed under the same terms. Do not paste in material you do
not have the right to license this way, and do not paste client or confidential
material anywhere — issues, PRs, test fixtures or skill content.

You do not need to add licence headers by hand. The build stamps the Apache-2.0
section 4(b) notices itself: a modification notice as the first body line of
every shipped `SKILL.md` naming the upstream commit, the same notice on every
Markdown companion the adaptation changed, an "Added by the lq-plugin-cowork
adaptation" notice on companions this repository wrote, upstream's `LICENSE` at
the root of every zip and [`NOTICE.md`](NOTICE.md) beside it. If a non-Markdown
companion changed, the build cannot annotate it and lists it in
`dist/build-report.md` instead — account for it in the card's `notes`.
