# Specification: release 0.2.0

Status: contract delta, written 20 September 2026 before any code. Sections A
to E amend [CONTRACT.md](CONTRACT.md) and are folded into it by the tooling
work; sections F to H direct the content and documentation work. Where this
file and CONTRACT.md disagree, this file wins until the fold is done.

Three decisions drive it:

1. **The bundles mirror the upstream release.** Upstream's
   `plugin.release.yaml` defines three audience plugins from four skill groups.
   We ship the same three, with the same membership, so every one of the
   thirty-one upstream skills ships. The fourteen previously excluded skills
   come in as Cowork-native adaptations at a stated risk tier; their names do
   not change.
2. **Every card carries a lawyer-facing account of how the skill differs from
   the original**, machine-readable, so the build report and the site render
   it: a tier, a status, a paragraph, known issues and workarounds.
3. **A small static site** lists the bundles and skills, the known issues and
   workarounds, the capability probes and the install and testing guides.
   Built from the same sources as the packages, published by GitHub Pages.

Research this rests on: [research/cowork-capability-verification.md](research/cowork-capability-verification.md)
(what Cowork has and lacks, with Microsoft's own words), and
[research/cowork-alternatives-and-risk.md](research/cowork-alternatives-and-risk.md)
(the design of each re-admitted skill, its tier, its failure modes and the
probes P1 to P14).

## A. Bundles mirror upstream (`cowork.yaml`)

A bundle may declare `mirror` instead of `skills`:

```yaml
bundles:
  - id: legalquants-litigation-cowork
    guid: 5d40f9d0-bbfe-5aa7-a4e9-10b4e0b676bf      # unchanged: an app id never changes
    mirror: legalquants-litigation                     # upstream plugin id in upstream/plugin.release.yaml
    exclude_skills: []                                 # optional; each entry {name, reason}; none today
    name: {short: ..., full: ...}
    description: {short: ..., full: ...}
```

Derivation, at config load: read `<upstream.path>/plugin.release.yaml`, find
`plugins[].id == mirror` (missing id is a config error), take its
`skill_groups` in the listed order, and for each group the folder names under
`<upstream.path>/<skills_root>/<group>/` in alphabetical order; then append
`include_skills` (`<group>/<name>`) in the listed order; then remove
`exclude_skills`. That list is the bundle's `skills` for every purpose
(manifest order, build, triggers, report, site). `mirror` and `skills` on the
same bundle is a config error. An explicit `skills` list keeps working.

- `LQC-B001` (error): a mirrored bundle derives a skill that has no card under
  `skills/<name>/`. The message names the skill and says: write a card, or
  exclude it with a reason.
- `LQC-B002` (warning): every `exclude_skills` entry, with its reason, so the
  build report and the drift report show it.
- The build report says, per bundle, `Mirrors upstream plugin <id>: groups a,
  b; includes …; excludes …`, and the upstream `display_name` and
  `short_description` beside ours.
- `bump-upstream` already lists upstream skills in no bundle; with `mirror`, a
  skill added upstream to a mirrored group also surfaces as `LQC-B001` at the
  next build, which is the pressure we want.

The three bundles:

| id | guid | mirror | skills |
| --- | --- | --- | --- |
| `legalquants-litigation-cowork` | `5d40f9d0-bbfe-5aa7-a4e9-10b4e0b676bf` (keep) | `legalquants-litigation` | core 5 + litigation 10 = 15 |
| `legalquants-transactional-cowork` | `f53d5df8-3b69-55e8-a12b-fdf244f3df55` (keep) | `legalquants-transactional` | core 5 + transactional 9 = 14 |
| `legalquants-companion-cowork` | new, uuid5 as the others were, pinned | `legalquants-companion` | companion 7 + core/lq-start = 8 |

Names: `name.short` stays `LQ Litigation Skills` / `LQ Transactional Skills`,
and `LQ Companion` for the third (≤ 30). `name.full` is upstream's
`display_name` plus ` for Copilot Cowork` (≤ 100). `description.short` is
upstream's `short_description` (≤ 80). `description.full` follows the existing
pattern (what is in it, how routing works, the adaptation notice, the closing
line) and lists every skill by name. `package.version` becomes `0.2.0`.

## B. The card: additions to `skills/<name>/skill.yaml`

`bucket` accepts `green | amber | red` (the September assessment's bucket;
informational). New, **required on every card**:

```yaml
cowork:
  tier: 2                         # 0 shipped as written apart from description and mechanics
                                  # 1 documented capabilities only, loud failures
                                  # 2 one named probe, or shipped now with an announced degrade
                                  # 3 re-scoped: the promise changed
                                  # 4 needs a connector -- a shipped card may not say 4 (LQC-K002)
  status: shipped                 # shipped | probe-gated  (probe-gated = shipped with an announced degrade until the probe passes)
  differs: |                      # REQUIRED. One paragraph for a lawyer: how this differs from the original. Plain words, no file names.
    The original runs a bundled script ...; here ...
  known_issues:                   # list; may be empty only when tier is 0 or 1 and status is shipped
    - id: KI-read-redline-1       # unique across the repository: KI-<skill>-<n>
      title: "Unseen tracked changes read as no changes"
      detail: "..."               # what the lawyer would see, and what to do about it
      failure: silent             # silent | loud  -- whether a wrong result would look right
      probe: P3                   # optional; a probe id from probes.yaml that settles it
  workarounds:                    # list; what the adaptation does instead of upstream's machinery
    - instead_of: "a bundled script computes the coverage count"
      cowork: "an Excel register lists every document and its status, so the count is visible and checkable"
```

Rules and codes:

- `LQC-K001` (error): `cowork` missing, or `tier`/`status`/`differs` missing
  or malformed; `tier` not an integer 0 to 4; `status` not one of the two;
  a known issue without `id`, `title`, `detail` or `failure`; a workaround
  without both keys; a duplicate `id` anywhere in the repository.
- `LQC-K002` (error): `tier: 4` on a card in any bundle; `tier` 2 or 3 with
  no known issue; `status: probe-gated` with no known issue carrying `probe`.
- `LQC-K003` (warning): a `probe` id that `probes.yaml` does not define.
- `LQC-W011` (warning): any `*.md` of the built skill contains a phrase from
  `transforms.claim_words` (case-insensitive; default list: `receipt`,
  `receipts`, `certified`, `coverage-certified`, `proved`, `proven`,
  `guaranteed complete`). A claim the model cannot back with something the
  lawyer can inspect must not be worded as one. Suppressible with a reason,
  like every warning.
- `notes` stays the technical record (what changed, in build terms);
  `cowork.differs` is the lawyer-facing account. Both required on amber and
  red cards.

## C. `probes.yaml`

At the repository root. The fourteen capability probes from
[research/cowork-alternatives-and-risk.md](research/cowork-alternatives-and-risk.md)
section 3, transcribed:

```yaml
probes:
  - id: P3
    title: Does Cowork report tracked changes in a Word document?
    settles: "..."
    setup: "..."                  # optional
    prompt: "..."                 # the exact text a tester types
    pass: "..."
    fail: "..."
    bad_outcome: fluent-fake      # refusal | fluent-fake
    unlocks: [read-redline]       # skill names; may be empty
```

Read by validation (`LQC-K003`), the build report, the site, and the UAT
issue renderer. `docs/TESTING.md` Part E summarises it and links to the site.

## D. CLI, build and dependencies

- `lqcowork build --skill NAME` (repeatable) builds only those skills into
  `<out>/skills-only/<name>/` through every card transform and runs the
  per-skill checks (`ASKILL-P*`, `LQC-C*`, `LQC-S*`, `LQC-W*`, `LQC-K*`,
  `LQC-A001`); it skips bundle assembly and manifest checks. Card authors use
  it before a skill is in any buildable bundle.
- `lqcowork site [--out DIR]` renders the site into `<out>/site/` from a
  built `<out>/` (see E); a missing build is an error with a message that
  says to run `package` first. `make site` runs `package` then `site`.
- Build report additions: per skill `Tier`, `Status` and known-issue count in
  the table; a `### Known issues` list per bundle (id, skill, title, failure,
  probe); the mirror line from A.
- Runtime dependencies become `PyYAML`, `Jinja2` and `markdown-it-py`
  (CONTRACT §7 amended). Nothing else. Black-formatted, tests in
  `tools/tests`.

## E. The site

`lqcowork site` writes a static site, relative links only, no external
assets, no JavaScript beyond an optional table filter, reproducible (the only
build-specific values are the package version and the upstream SHA; no
timestamps). It reads `cowork.yaml`, the cards, `probes.yaml`,
`upstream/plugin.release.yaml`, each upstream `SKILL.md` frontmatter (for the
original description), the built `dist/<bundle>/` trees (file counts),
`dist/build-report.md` warnings, `CHANGELOG.md`, `docs/INSTALL.md` and
`docs/TESTING.md` (rendered through markdown-it-py).

Pages, all under `dist/site/`:

| Page | Content |
| --- | --- |
| `index.html` | Welcome: what this is and is not (independent adaptation, not official, pre-release, nothing exercised in a live tenant), the three bundles with skill counts and download links to the latest release, how routing works in Cowork, the tester call, links to everything below. |
| `bundles/<id>.html` | Manifest name and description; `Mirrors upstream plugin …`; the skills table (name, one-line purpose, tier, status, known issues count); the trigger-test checklist rendered; the release asset name. |
| `skills/<name>.html` | What it does (card description, first sentence), when to use it (positive triggers), not for (negative triggers with their hand-offs), bundles it ships in, tier and status badges, **How it differs from the original** (`cowork.differs`, then `notes` under a "Build notes" disclosure), **Known issues** (each with failure mode and probe link), **Workarounds** table, upstream link (`https://github.com/LegalQuants/lq-plugin-oss/tree/<sha>/skills/<group>/<name>`), the original description quoted, files shipped, and a link to the skill's open UAT issue search. |
| `known-issues.html` | Every known issue across all cards, filterable by tier, failure and probe. |
| `probes.html` | P1 to P14 from `probes.yaml`, with what each unlocks. |
| `differences.html` | What changed for every skill: the capability picture in one screen (no local disk, scripts documented but unspecified, web reach tenant-controlled, sessions), the mechanical transforms, the claim-words rule, the bundle structure against upstream, the tier rubric. |
| `install.html`, `testing.html`, `changelog.html` | Rendered from the Markdown files. |

Design: one small stylesheet, system fonts, light and dark through
`prefers-color-scheme`, readable at phone width, tables that scroll rather
than overflow, skip-link and landmarks. A footer on every page with the
package version, the upstream SHA, the licence line and the not-official line.

Publishing: `.github/workflows/site.yml` on push to `main` and on
`workflow_dispatch`: checkout with submodules, `uv sync --project tools`,
`make site`, `actions/upload-pages-artifact` from `dist/site`,
`actions/deploy-pages`. Permissions `pages: write`, `id-token: write`,
`contents: read`. Pages source is GitHub Actions. URL:
`https://houfu.github.io/lq-plugin-cowork/`; README, INSTALL and the release
notes link to it.

## F. The fourteen re-admitted skills

One card each, following CONTRACT §4 and the design in
[research/cowork-alternatives-and-risk.md](research/cowork-alternatives-and-risk.md)
section 7 (the recommended "A" alternative; Tier 4 variants are not built).
Names unchanged. Rules that apply to all fourteen:

- Ship no scripts (`exclude: scripts/**`, and `schemas/**` where present).
  Every step has a host-native path; the repo's CONTRACT §8 policy stands.
- Follow the substitution catalogue: state kept in the Output folder or
  brought by the lawyer as an attached file; an Excel register through the
  built-in Excel skill as the visible receipt; HTML for the preview pane in
  place of rendered images; sequential processing in one session; the lawyer
  supplies the publisher's own document in place of a fetch.
- Policy defaults adopted for this release: no external links (no LegalQuants
  sign-up, assessment, directory or corpus URLs); citing a source by title
  and date without a URL is allowed; relaying a link the lawyer supplied in
  their own session is allowed; the claim-words rule applies.
- `docreview` ships with the four mitigations from the design (privilege state
  as the first register column; held count and ids stated before anything is
  produced; no quoted text from a held unit anywhere; no register attached
  means no findings) and a known issue `KI-docreview-1`, failure `silent`,
  saying the privilege hold is a rule the model applies, not an enforced lock.
- Descriptions follow the grammar in CONTRACT §4 and resolve every routing
  collision the design names (read-redline with playbook-review, sigpack with
  closing-checklist, regulatory with cite-check and the tenant's research
  built-in, lq-reflect with lq-mirror, my-lq-moment with lq-mirror and
  legaldesign, legalquants with lq-start).
- `cowork.tier` and `status` come from the design's summary table; each known
  issue comes from the design's failure modes; each workaround from its step
  table; `differs` is written fresh for a lawyer.
- Hand-off rules for shared skills: a core skill ships in litigation and
  transactional and may name only skills present in both, or a scope
  statement; a companion skill ships only in the companion bundle and may
  name any companion skill or lq-start.
- Build check before finishing: `uv run --project tools lqcowork build
  --skill <name>` (available once the tooling in D lands), zero errors, every
  warning either fixed or suppressed with a reason in the card.

## G. Documentation

- `README.md`: intro phrase and the "What is deliberately left out" section
  replaced per the verification report's proposed wording, rewritten for
  three bundles and all thirty-one skills; the skills table gains a tier
  column and covers all thirty-one; the depositions row says "mines the
  deposition transcript"; a link to the site near the top.
- `CHANGELOG.md`: `[Unreleased]` entries for 0.2.0: the third bundle, the
  fourteen skills with their tiers, the card block, the site, the corrected
  capability statement, the probes.
- `CONTRIBUTING.md`: section 4 ("Porting a left-out skill: out of scope") is
  replaced by "Adapting a red skill": the tier rubric, the substitution
  catalogue, the `cowork` block, the probe list.
- `NOTICE.md`: the verification report's proposed line.
- `docs/CONTRACT.md` section 8: the verification report's proposed bullets
  (section 4.7), which keep the no-scripts policy and correct its premise.
- `docs/INSTALL.md`: three bundles; the site link; Route 0 text if present
  stays.
- `docs/TESTING.md`: Part B gains one entry per re-admitted skill (synthetic
  inputs, pass criteria, what to watch for, as the existing entries do); a new
  Part E "Capability probes" summarising `probes.yaml` with the prompts, and
  saying which skills each result unlocks; the bundle table lists three.
- `tools/scripts/uat_issues.py` gains `--probes`, rendering one issue per
  probe from `probes.yaml` (title `Probe <id>: <title>`, label `uat` plus a
  new `probe` label), idempotent like the rest. Issues are created only when
  the maintainer runs it.

## H. Ownership for the work

| Slice | Owns |
| --- | --- |
| Tooling core | `tools/src/lqcowork/{config,build,validate,package,transforms,bump}.py`, existing tests, `cowork.yaml`, `probes.yaml`, `docs/CONTRACT.md` (fold A to D in), `tools/scripts/uat_issues.py` |
| Site | `tools/src/lqcowork/site/**`, `tools/src/lqcowork/cli.py` (the `site` command only), `tools/pyproject.toml`, `Makefile` (`site` target), `.github/workflows/site.yml`, `tools/tests/test_site.py`, `docs/CONTRACT.md` §7 CLI lines and a new §9 for the site |
| Cards, five slices | `skills/<name>/**` for the fourteen named skills only |
| Existing cards | `cowork:` blocks in the seventeen existing `skills/<name>/skill.yaml` |
| lq-start map | `skills/lq-start/**` after every card exists: the map covers three bundles and thirty-one skills |
| Documentation | `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `NOTICE.md`, `docs/INSTALL.md`, `docs/TESTING.md`, `docs/CONTRACT.md` §8 only |
