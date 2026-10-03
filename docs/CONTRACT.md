# lq-cowork build contract

This file is the single source of truth for how this repository turns the
vendored LegalQuants skills into Microsoft 365 Copilot Cowork plugin packages.
Tooling implements it; skill adaptation cards conform to it. Change the
contract first, then the code.

Upstream: <https://github.com/LegalQuants/lq-plugin-oss>, pinned as a git
submodule at `upstream/` (SHA recorded in `cowork.yaml`). Upstream authors
skills under `upstream/skills/<group>/<name>/` where group is one of `core`,
`litigation`, `transactional`, `companion`. We read the **authored** tree, not
the generated `upstream/plugins/` bundles (those add `LICENSE` and
`agents/openai.yaml` per skill and carry Codex hooks we do not want).

## 1. Principles

Adaptations are layered by brittleness, most robust first. Prefer the highest
layer that does the job.

1. **Selection manifest** — `cowork.yaml` says which skills go in which bundle.
2. **Mechanical transforms** — rule-based rewrites the build applies to every
   skill (strip files, drop Claude-only frontmatter, rewrite `$name`/`/name`
   tokens, remove vendor-neutral-waiver comments). Pattern-anchored, never
   line-anchored.
3. **Frontmatter overrides** — the Cowork trigger-phrase `description` lives in
   the skill card and replaces the upstream description wholesale.
4. **Literal replacements** — `replace:` rules in the card (exact string, all
   occurrences, with an expected count). Fail loudly when the anchor text is
   gone.
5. **Section overlays** — replace or delete a whole Markdown section by its
   heading text.
6. **Patch files** — unified diffs, for the rare edit nothing above can express.
7. **Full-file overlays** — our own `SKILL.md` for skills we effectively rewrite
   (lq-start). Upstream's copy is only the thing we diff against on a bump.

Every adapted file must carry an Apache-2.0 §4(b) modification notice, and
upstream's `LICENSE` travels at the zip root.

## 2. Repository layout

```
lq-cowork/
  upstream/                    # git submodule, read-only, pinned SHA
  cowork.yaml                  # bundles, developer block, global transforms, pin
  probes.yaml                  # the capability probes (section 3), each tied to capability codes
  capabilities.yaml            # every skill's capability levels, two profiles (section 4b)
  probe-results/*.json         # recorded harness-probe runs, judged by the build and the site
  harness-probe/               # the repository's own Agent Skill: runs the probes, writes the report
    SKILL.md, references/, scripts/, assets/fixtures/, data/catalog.json (generated)
  harness-probe-invoke/        # its explicit-invocation companion, for probe P24
  skills/README.md             # says these folders are build inputs, not skills (section 5b)
  skills/<name>/               # one adaptation folder per shipped skill
    skill.yaml                 #   the card (required)
    SKILL.md                   #   full-file overlay (optional)
    sections/*.md              #   section overlay bodies (optional)
    patches/*.patch            #   unified diffs (optional)
    files/**                   #   extra/replacement companion files (optional)
  branding/color.png           # 192x192 full-colour icon
  branding/outline.png         # 32x32 single-colour outline icon
  NOTICE.md                    # attribution + modification notice (zip root)
  CHANGELOG.md                 # Keep a Changelog; a release's notes are read from it
  tools/                       # uv-managed Python project (package: lqcowork)
    pyproject.toml
    src/lqcowork/...
    src/lqcowork/site/         #   the static site: generator, templates, stylesheet
    tests/...
  docs/CONTRACT.md             # this file
  docs/RELEASING.md            # how a release is cut (contract section 7)
  dist/                        # generated, gitignored: bundles, zips, dist/skills/<name>.skill,
                               #   dist/harness/<name>.skill, reports
  .github/workflows/           # build.yml, release.yml, site.yml, upstream-drift.yml
  .github/dependabot.yml       # keeps the pinned action versions current
  Makefile                     # thin wrappers around `uv run --project tools lqcowork ...`
```

`skills/<name>/` is named after the **shipped** skill name, which equals the
upstream skill name and the Cowork folder name. The card's `upstream:` field
says where the source lives (`<group>/<name>`).

## 3. `cowork.yaml`

```yaml
upstream:
  repo: https://github.com/LegalQuants/lq-plugin-oss
  sha: fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0     # full SHA; bump-upstream rewrites it
  path: upstream                                     # submodule path
  skills_root: skills                                # authored skills live at <path>/<skills_root>/<group>/<name>

developer:                                           # manifest.developer, verbatim
  name: LegalQuants
  websiteUrl: https://legalquants.com
  privacyUrl: https://www.legalquants.com/privacy
  termsOfUseUrl: https://www.legalquants.com/terms

package:
  version: 0.1.0                                     # manifest.version (semver, x.y.z)
  accentColor: "#2D2D2D"
  icons:
    color: branding/color.png
    outline: branding/outline.png
  root_files:                                        # copied to the zip root
    - upstream/LICENSE                               # -> LICENSE
    - NOTICE.md

strip:                                               # gitignore-style globs, relative to each skill folder, applied on copy
  - LICENSE
  - "agents/**"
  - ".*"
  - "**/.*"
  - "**/__pycache__/**"

transforms:
  drop_frontmatter: [disable-model-invocation, argument-hint, allowed-tools]
  strip_waivers: true                                # remove <!-- vendor-neutral-waiver: ... --> comments
  skill_tokens: true                                 # rewrite $name and /name for every upstream skill name
  vendor_words: [Codex, CODEX, ChatGPT, Claude, Cursor, Gemini]   # validation WARNS if any survive
  host_words: [lqprofile.md, the scribe, ...]        # host machinery that does not exist in Cowork (LQC-W009)
  claim_words: [receipt, receipts, certified, ...]   # promises nothing can back (LQC-W011); omitted = the default list

replace: []                                          # global literal replacements, same shape as a card's replace list

bundles:
  - id: legalquants-litigation-cowork                # zip base name and dist folder
    guid: 5d40f9d0-bbfe-5aa7-a4e9-10b4e0b676bf       # stable; generated once (uuid5) and pinned here
    mirror: legalquants-litigation                   # upstream plugin id in upstream/plugin.release.yaml
    exclude_skills: []                               # optional; each entry {name, reason}; none today
    name:
      short: LQ Litigation Skills                    # <= 30 chars (Teams manifest limit)
      full: LegalQuants Skills for Litigators for Copilot Cowork   # <= 100 chars
    description:
      short: Source-grounded workflows for litigators   # <= 80 chars
      full: >-                                       # <= 4000 chars; must say it is an adaptation
        ...
  - id: legalquants-transactional-cowork
    ...
  - id: some-other-bundle                            # a bundle may still list its own skills
    skills:                                          # order = manifest order; <= 20; names must have a card
      - lq-start
      - writing
```

A bundle declares **either** `mirror` **or** `skills`; both on one bundle is a
config error, and so is neither. `exclude_skills` only belongs on a mirrored
bundle.

Mirror derivation, at config load: read `<upstream.path>/plugin.release.yaml`,
find `plugins[].id == mirror` (a missing id is a config error), take its
`skill_groups` in the listed order, and for each group the skill folder names
under `<upstream.path>/<skills_root>/<group>/` in alphabetical order; then
append `include_skills` (`<group>/<name>`) in the listed order; then remove
every `exclude_skills` name. A folder counts as a skill when it holds a
`SKILL.md`. That list is the bundle's `skills` for every purpose — manifest
order, build, triggers, report and site. An explicit `skills` list keeps
working and is unaffected.

`bump-upstream` already lists upstream skills in no bundle; with `mirror`, a
skill added upstream to a mirrored group also surfaces as `LQC-B001` at the
next build, which is the pressure we want.

Bundle membership (mirrored from upstream; change it upstream, or exclude it
here with a reason):

| bundle | mirrors | skills |
| --- | --- | --- |
| `legalquants-litigation-cowork` | `legalquants-litigation` | core 5 + litigation 10 = 15 |
| `legalquants-transactional-cowork` | `legalquants-transactional` | core 5 + transactional 9 = 14 |
| `legalquants-companion-cowork` | `legalquants-companion` | companion 7 + core/lq-start = 8 |

All thirty-one upstream skills ship. `name.short` is ours; `name.full` is
upstream's `display_name` plus ` for Copilot Cowork`; `description.short` is
upstream's `short_description`. `description.full` says what is in the bundle,
naming every skill, how routing works, that this is an adaptation, and the
closing line.

Manifest ids, names and descriptions live only in `cowork.yaml`. The package
`description.full` must state that the bundle is adapted from
LegalQuants/lq-plugin-oss under Apache-2.0 and is not an upstream release.

A `guid` is generated once and never changes: an app id is the identity
Microsoft 365 remembers a sideloaded package by. The first two were generated
before the method was written down here, so it is not recorded; the third,
`legalquants-companion-cowork`, is
`uuid5(NAMESPACE_URL, "https://github.com/houfu/lq-plugin-cowork#legalquants-companion-cowork")`
= `420f3a25-7f35-5b17-a3c5-6a9362c9e9ce`, and that is the method for any
bundle added after it.

### `probes.yaml`

At the repository root: the capability probes, each one a question about
what a harness can actually do. P1 to P14 were written for Cowork and
transcribed from `docs/research/cowork-alternatives-and-risk.md` section 3;
P15 to P27 close the gaps in `docs/research/probe-coverage-review.md`.

```yaml
probes:
  - id: P3
    title: Does Cowork report tracked changes in a Word document?
    settles: "..."                # what a result decides, and why it is not documented
    setup: "..."                  # optional
    prompt: "..."                 # the exact text a tester types
    pass: "..."
    fail: "..."
    bad_outcome: silent           # refusal | fluent-fake | silent | loud
    tests: [IN, DOCX]             # capability codes from capabilities.yaml
    cost: low                     # free | low | setup | two-session | admin
    harness:                      # how the harness-probe skill runs it on any harness
      method: agent               # script | agent | user | two-session
      check: docx-read            # the `hprobe.py check` verifier, or null
      steps: "..."                # what the agent does; <run> and <skill> are filled in
```

`id`, `title`, `settles`, `prompt`, `pass`, `fail` and `bad_outcome` are
required; `setup` is optional. Duplicate ids, an unknown `bad_outcome`, an
unknown `cost` and an unknown `harness.method` are config errors. An absent
`probes.yaml` is not: every card that names a probe then gets `LQC-K003`,
which says exactly that. With `capabilities.yaml` present, `tests` and
`harness` are required (`LQC-K004`).

**`unlocks` is derived, not written.** The skills a probe unlocks are the
skills whose cowork-profile required or degradable levels it decides: a
probe decides a code when it is one of the code's `evidence` probes, or one
of a skill's extra `evidence` probes for that code or facet. `load_config`
fills `Probe.unlocks` that way; a `probes.yaml` that still declares
`unlocks:` is refused (`LQC-K004`). Without `capabilities.yaml`, a declared
`unlocks` list is read as before.

It is read by validation (`LQC-K003` to `LQC-K008`), the build report, the
site, `tools/scripts/uat_issues.py --probes` and, as
`harness-probe/data/catalog.json`, by the harness-probe skill.
`docs/TESTING.md` Part E summarises it and links to the site.

## 4. The skill card: `skills/<name>/skill.yaml`

```yaml
name: wiki                        # == folder name == upstream skill name == Cowork folder name
upstream: core/wiki               # <group>/<name> under upstream/skills/
bucket: amber                     # green | amber | red  (from the portability assessment; informational)
anchored_to: fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0   # upstream SHA this card was written against

description: |                    # REQUIRED. Replaces upstream description wholesale. 1-1024 chars after strip.
  Keeps a Markdown legal wiki in a OneDrive folder ...
  Use when the user asks to "add this to the wiki", "what does the wiki say about", ...
  Do not use for drafting documents (use the writing skill) or ...

cowork:                           # REQUIRED on every card. The lawyer-facing account of the adaptation.
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

frontmatter:                      # optional. Set/override keys after mechanical transforms. null deletes.
  compatibility: null

exclude:                          # optional. gitignore-style globs relative to the skill folder, in addition to global strip.
  - "scripts/**"
  - "schemas/**"
  - "references/automation.md"

replace:                          # optional. Literal string replacement, all occurrences.
  - from: "Run `scripts/wiki.py`"
    to: "Open the wiki folder"
    files: ["SKILL.md"]           # optional; default ["SKILL.md"]; globs allowed, e.g. "references/*.md"
    expect: 1                     # optional; number of occurrences expected across the listed files.
                                  #   Mismatch (or 0 when omitted) is an ANCHOR failure.

sections:                         # optional. Heading-anchored replacement in SKILL.md.
  - match: "## Automation is an optional enhancement"   # exact heading line, after trimming trailing spaces
    file: sections/automation.md  # file content replaces the whole section, heading line included
  - match: "## Finish well"
    delete: true                  # remove the section entirely

patches:                          # optional. Applied last, with `git apply`, paths relative to the skill folder.
  - patches/docreview-link.patch

files: files                      # optional. Directory copied over the skill folder after copy+exclude (adds or replaces companions).

notes: |                          # REQUIRED for amber and red skills. What changed and why, in build terms, for the README table and the drift report.
  Dropped scripts/ and schemas/; the body's chat path is the documented fallback ...

suppress:                         # optional. Accept a named warning, on the record.
  - code: LQC-W010                #   must be a warning code; an error can never be suppressed
    file: "references/getting-authorities.md"   # optional glob relative to the skill; omitted = the whole skill
    reason: "upstream-authored court and legislation URLs"   # REQUIRED

triggers:                         # REQUIRED. Live trigger tests for Cowork (step 3 of the plan).
  positive:                       # 3-5 natural-language prompts that MUST activate this skill
    - "Add this ruling to our wiki under limitation periods."
  negative:                       # 3-5 adjacent prompts that must NOT activate it (name the skill that should, in a trailing "-> name" tag)
    - "Draft a reply to opposing counsel's letter about the deposition date. -> correspondence"
```

Rules for cards:

- `name`, `upstream`, `anchored_to`, `description`, `cowork`, `triggers` are
  required. `notes` is required when `bucket` is `amber` or `red`.
- `notes` stays the technical record — what changed, in build terms.
  `cowork.differs` is the lawyer-facing account of the same change, in plain
  words and without file names. Both are required on an amber or red card:
  `differs` on every card, by `LQC-K001`; `notes` by `LQC-W008`.
- The `cowork` block is checked by `LQC-K001` and `LQC-K002` (errors) and
  `LQC-K003` (a warning); section 6 has the rules. A known issue's `id` is
  unique across the repository, which is what lets the build report, the site
  and the UAT programme all refer to the same thing.
- A section body file (`sections/*.md`) starts with the new heading line (it
  may differ from `match`) and contains the whole replacement section.
- A full-file overlay `skills/<name>/SKILL.md` must be a complete SKILL.md
  (frontmatter + body). The build still applies every mechanical transform to
  it and always overwrites `name`/`description` from the card, so the overlay's
  own frontmatter is documentation only.
- Cards must not reference `$name`/`/name` tokens, vendor names, `hooks`,
  `~/.lq/`, `scripts/` that were excluded, or files outside the skill folder.
- Descriptions follow Cowork's guidance: what the skill does in one sentence,
  then `Use when the user asks to "…", "…", "…"` with quoted trigger phrases,
  then a `Do not use for … (use the <name> skill)` hand-off naming the
  neighbouring skills that compete for the same requests. No calls to action,
  no marketplace links, no vendor names, no `$`/`/` invocation grammar.
- A skill that ships in more than one bundle may hand off by name only to
  skills present in every bundle it ships in, or to Cowork built-ins. For a
  competitor that is bundle-specific, use a scope statement instead ("Do not
  use for case chronologies or document timelines; this skill only drafts
  billing narratives") so the conflict is still resolved in the description.
- Trigger phrases must be things the skill actually does; never advertise an
  action the body then refuses (a no-send skill does not list "send …").
- `suppress` accepts a warning the card owner has judged and decided to keep.
  `code` must be an `LQC-Wnnn` warning; an error is never suppressible. `file`
  is an optional glob relative to the skill folder, matched against the
  warning's `file:line` location; omitting it covers the whole skill. `reason`
  is required and is what makes the decision auditable: `validate` drops the
  matching warnings and the build report lists every one of them under
  "Suppressed warnings" with its bundle, skill, code, file and reason.

## 4b. Capabilities, the probe skill and verdicts

### `capabilities.yaml`

At the repository root: what every vendored skill needs from a harness,
under two profiles - `upstream` (the skill as vendored) and `cowork` (the
adapted card as built). It is the data behind
`docs/research/harness-capability-chart.md`.

```yaml
codes:
  - id: OUT
    name: Hand back files
    summary: Write a file and hand it to the user.
    evidence: [P27]               # primary probes: decide this code for every skill
    column: true                  # false for auxiliary codes (HASH, SKILLDIR, INVOKE)
unprobed: []                      # [{code, reason}] for a code no probe tests, on purpose
skills:
  sigpack:
    group: transactional
    upstream:
      levels: {TOOLS: R, IN: R, OUT: R, OUT:pdf-assemble: R, VISION: R, EXEC: D}
      evidence: {OUT:pdf-assemble: [P8]}   # extra probes, per code or facet
      needs: {python: "3.8", packages: [pypdf], binaries: [pdftoppm, soffice]}
      fallbacks:
        EXEC: {text: "the skill's own words for what happens without it", ref: "file:line"}
    cowork:
      levels: {...}
      evidence: {...}
      fallbacks: {...}
      notes: "what the adaptation changed"
```

Levels are `R` (required: the core deliverable cannot be produced, or the
skill stops), `D` (degradable: the skill documents a fallback and what it
costs) and `O` (optional). A **facet** (`CODE:name`) narrows a code to the one
thing a probe tests; it has no primary probes, only its own `evidence`.
**TOOLS is derived**: the strongest level among the action codes OUT, FS,
PERSIST, EXEC, BIN, NET, SEARCH, VISION, DOCX, SUB, SESSION, SCHED, MCP, HASH
and SKILLDIR, facets included. `needs` (upstream only) is judged against
probe P1's recorded facts for EXEC and BIN.

### The harness-probe skill

`harness-probe/` is an Agent Skill this repository ships, not an adaptation.
On any harness it initialises a run folder with freshly generated synthetic
fixtures, walks the agent through every probe's `harness.steps`, verifies
each result against a salted answer key with `scripts/hprobe.py check`, and
writes the report. Its scripts are standard library only and Python 3.8
compatible. Static fixtures in `assets/fixtures/static.zip` serve harnesses that
cannot run scripts, and their answers can be checked later anywhere.
`harness-probe-invoke/` is its explicit-invocation companion for P24.

`harness-probe/data/catalog.json` and `harness-probe/references/probes.md`
are **generated** from `probes.yaml`, `capabilities.yaml` and the cards by
`lqcowork catalog`; the cards contribute each skill's tier, status and cited
probes to the cowork profile. `assets/fixtures/` is generated by
`hprobe.py fixtures` and checked for drift by the tests.

### The verdict

`harness-probe/scripts/hprobe_engine.py` is the only implementation; the
build tooling imports it. For one skill under one profile, a capability
passes when every probe deciding it passed (the newest result per probe
wins; a result's `codes` map can override single codes), fails when any
failed, was refused or was caught as a fluent fake, and is untested
otherwise. Then:

| Verdict | Rule |
| --- | --- |
| runs as intended | every R and every D passes |
| runs on a fallback | every R passes; at least one D failed or is unprobed (the report quotes its fallback wording) |
| cannot run | at least one R failed |
| untested | no R failed; at least one R is unprobed |

O levels never change a verdict. The report also ranks each failed
capability by the skills it would unblock (as their only blocker), help
unblock and upgrade from a fallback - what to build next on that harness -
and ranks unrun probes by how many untested skills each would clear, and, for the cowork profile, flags a
card whose hand-set `status` or `tier` disagrees with its verdict without
changing it.

### `probe-results/`

One `lq-harness-probe-results/1` JSON file per harness run
(`harness-probe/references/results-format.md`). The build validates each
(`LQC-K007`); the build report's **Harness verdicts** section and the site's
`verdicts.html` judge each one, beside an empty baseline per profile.

## 5. Build pipeline (per skill, in this order)

1. Resolve source `upstream/skills/<upstream>`; missing folder is an error.
2. Copy to `dist/<bundle>/skills/<name>/`, skipping paths matched by global
   `strip` and card `exclude`.
3. If `skills/<name>/SKILL.md` exists, replace the copied SKILL.md with it.
4. If the card's `files` directory exists, copy it over the skill folder.
5. Mechanical transforms:
   - SKILL.md frontmatter: parse YAML between the first two `---` lines; drop
     keys in `transforms.drop_frontmatter`.
   - All `*.md` files: remove `<!-- vendor-neutral-waiver: ... -->` comments.
     If the comment sits alone on its line, remove the line.
   - All `*.md` files, when `skill_tokens` is true: for every upstream skill
     name N (the 31 folder names under `upstream/skills/*/`):
     - `$N` → `N`
     - `` `/N` `` and `` `/N <args>` `` → `` `N` ``
     - `/N` preceded by start-of-line, whitespace, `(` or a quote, and followed
       by whitespace, punctuation or end-of-line → `N`
     Never touch path-like occurrences (`references/N.md`, `../N/`).
6. Global `replace` rules, then card `replace` rules (count-checked).
7. Card `sections` (missing heading = anchor failure).
8. Card `patches` via `git apply --directory=<skill dir> --unsafe-paths` (fail = anchor failure).
9. Card `frontmatter` overrides (null deletes).
10. Stamp: set `name` from the card, `description` from the card (stripped),
    `license: Apache-2.0`, and
    `metadata.adapted-from: "LegalQuants/lq-plugin-oss@<sha7> skills/<upstream>"`,
    `metadata.adapted-for: "Microsoft 365 Copilot Cowork"`,
    `metadata.version: "<package.version>"` (a string, e.g. `"0.2.0"`; the same
    value as the manifest version, so a `.skill` uploaded on its own still says
    which release it came from — there is no manifest beside it). Existing
    `metadata` keys are preserved. Insert as the first body line, right after
    the closing `---`:
    `<!-- Modified from LegalQuants/lq-plugin-oss@<sha7> (skills/<upstream>) for Microsoft 365 Copilot Cowork. Apache-2.0; see LICENSE and NOTICE.md at the package root. -->`
10b. Companion notices: after every transform, compare each `*.md` companion
    with the upstream file at the same relative path. If it differs, insert as
    its first line
    `<!-- Modified from LegalQuants/lq-plugin-oss@<sha7> (skills/<upstream>/<relpath>) for Microsoft 365 Copilot Cowork. Apache-2.0; see LICENSE and NOTICE.md at the package root. -->`
    followed by a blank line. If it has no upstream counterpart, insert
    `<!-- Added by the lq-plugin-cowork adaptation of LegalQuants/lq-plugin-oss@<sha7>; not an upstream LegalQuants file. Apache-2.0; see LICENSE and NOTICE.md at the package root. -->`.
    The build never modifies non-Markdown companions; a card that ships a
    changed or new non-Markdown companion through `files/` must say so in
    `notes`, and the build report lists such files under "Companions changed
    without an in-file notice".
11. Serialise frontmatter with `name` first, `description` second (block
    scalar `|`), then the rest in original order; `---` delimiters; body
    unchanged otherwise.
12. Validate (section 6). Errors fail the build; anchor failures also fail
    the build unless `--report-anchors` (used by bump-upstream) turns them
    into report entries.

Bundle assembly: `dist/<bundle>/manifest.json`, `color.png`, `outline.png`,
`LICENSE`, `NOTICE.md`, `skills/<name>/...`. A skill shared by two bundles is
built once and copied. Then `dist/<bundle>.zip` with everything at the zip
root (no top-level folder), plus `dist/<bundle>-trigger-tests.md` (the
positive/negative prompts from the cards as a checklist table; when a
negative prompt's `-> target` names a skill that is not in the bundle being
rendered, print `must not activate; expect none (<target> is not in this
bundle)`, and when it names a Cowork built-in from §8, case-insensitively,
print `must not activate; expect built-in <Name>`) and
`dist/build-report.md` (per skill: bucket, tier, status, known-issue count,
files, bytes, warnings; per bundle: skill count, manifest summary, the
`Mirrors upstream plugin <id>: groups …; includes …; excludes …` line with
upstream's `display_name` and `short_description` beside ours, a
`### Known issues` table of every known issue the bundle's cards declare —
id, skill, title, failure, probe — and the single-skill archives of section
5b).

## 5b. Single-skill archives: `dist/skills/<name>.skill`

Cowork's **Customize** page has an **Upload skill** control that takes one
skill at a time, without a plugin package, an administrator or `atk`: a `.md`
holding a single SKILL.md, or a `.zip`/`.skill` archive with `SKILL.md` at its
root plus the skill's companion files. That is the route a lawyer with no
developer tooling will use, and it is the route UAT issue 19 asked for after a
tester zipped `skills/pressuretest/` from this repository, found no SKILL.md in
it, and rebuilt the skill by hand. A lawyer who wants `regulatory` and nothing
else should not have to install a fifteen-skill plugin to get it. Every
`package` run therefore also writes one upload-ready archive per distinct
skill, from the same built tree the bundles are made from — thirty-one of them
when every bundle is built.

- Path `dist/skills/<name>.skill`, one per skill name across all selected
  bundles (a shared skill is built once and archived once; the bundle copies
  are byte-identical by construction). `<name>` is the shipped skill name,
  which is the folder name and the frontmatter `name`.
- Contents, all at the archive root, no top-level folder: the built skill
  folder (`SKILL.md` and its companions, exactly as in `dist/<bundle>/skills/<name>/`),
  plus each `package.root_files` entry under its own base name — `LICENSE`
  (upstream's) and `NOTICE.md` — because Apache-2.0 §4 travels with every
  distribution, and a single skill uploaded on its own is one.
- Written with the bundle zip writer: sorted entries, 1980 timestamps (or
  `SOURCE_DATE_EPOCH`), mode 0644, deflate, no `__MACOSX`, no dotfiles;
  byte-reproducible. Two builds into different `--out` directories produce
  equal bytes, and the release workflow re-checks that before it publishes.
- Checked against the Customize-page limits, not the plugin-package ones:
  LQC-U003 and LQC-U004 are 100 entries, 10 MB compressed and 50 MB
  uncompressed for the archive as a whole, where LQC-C001 to LQC-C003 are
  about a skill folder inside a plugin package (section 8, "Two packaging
  channels with different limits").
- There is no bare `.md` edition. A lone SKILL.md drops the companion files the
  body tells the agent to read, so it would upload cleanly and then misbehave.
  If a skill has no companions the archive still ships, for one download shape.

Each archive is validated (section 6, `LQC-U` codes) after it is written, the
same way bundle zips are. `package` prints one summary line per archive under
the bundle lines, the build report gets a `## Single-skill archives` section
(Archive | Entries | Compressed | Uncompressed | Bundles), and the release
publishes them all next to the bundles with their checksums (section 7 of
RELEASING.md).

## 5c. Harness-probe archives: `dist/harness/<name>.skill`

`package` also writes `dist/harness/harness-probe.skill` and
`dist/harness/harness-probe-invoke.skill`: the skill folder at the archive
root plus `LICENSE`, no `__pycache__` and no dotfiles, through the same
reproducible zip writer as section 5b. They are release assets, covered by
`SHA256SUMS` and the reproducibility check.

## 6. Validation rules

Error codes reuse Microsoft's where a rule matches; ours are `LQC-…`.

Errors (fail the build):

| Code | Rule |
| --- | --- |
| ASKILL-M001 | every `agentSkills` entry has `folder` |
| ASKILL-M002 | ≤ 20 `agentSkills` entries |
| ASKILL-M003 | `folder` ≤ 256 chars |
| ASKILL-P001 | referenced folder exists in the package |
| ASKILL-P002 | folder contains `SKILL.md` |
| ASKILL-P003 | valid YAML frontmatter between `---` delimiters |
| ASKILL-P004 | frontmatter has `name` |
| ASKILL-P005 | frontmatter has `description` |
| ASKILL-P006 | `name` equals the folder's last path segment |
| ASKILL-P007 | `name` is kebab-case: `^[a-z0-9]+(-[a-z0-9]+)*$`, 1-64 chars |
| ASKILL-P008 | no duplicate `folder` values |
| LQC-D001 | `description` is 1-1024 characters |
| LQC-C001 | ≤ 20 companion files per skill (everything except SKILL.md) |
| LQC-C002 | each companion ≤ 5 MB |
| LQC-C003 | companions ≤ 10 MB per skill |
| LQC-C004 | no hidden files or directories (leading `.`) |
| LQC-C005 | no Windows reserved names (`CON PRN AUX NUL COM1-9 LPT1-9`, case-insensitive, with or without extension) |
| LQC-C006 | file and directory names match `^[A-Za-z0-9 _.!-]+$`; no `..` segments; no backslashes |
| LQC-C007 | no symlinks in a skill folder (never followed, never packaged) |
| LQC-S001 | SKILL.md ≤ 1 MB |
| LQC-M001 | manifest has exactly the allowed top-level keys: `$schema manifestVersion version id developer name description icons accentColor agentSkills` (+ `agentConnectors` when present) |
| LQC-M002 | `manifestVersion` is `1.28`; `$schema` is the v1.28 URL; `version` matches `^\d+\.\d+\.\d+$`; `id` is a UUID |
| LQC-M003 | `name.short` ≤ 30, `name.full` ≤ 100, `description.short` ≤ 80, `description.full` ≤ 4000, all non-empty |
| LQC-M004 | `developer.name/websiteUrl/privacyUrl/termsOfUseUrl` present; URLs are https |
| LQC-M005 | `accentColor` matches `^#[0-9A-Fa-f]{6}$` |
| LQC-I001 | `color.png` is a PNG of exactly 192×192; `outline.png` exactly 32×32 (read the IHDR chunk) |
| LQC-Z001 | zip entries are at the root (`manifest.json`, icons, `skills/...`), no `__MACOSX`, no dotfiles |
| LQC-A001 | anchor failure (replace count mismatch, section heading missing, patch failed, overlay base missing) |
| LQC-U001 | a single-skill archive has `SKILL.md` at its root, and no entry starts with `./`, `/`, a top-level folder other than the skill's own subfolders, `__MACOSX`, or a dot |
| LQC-U002 | the archive's `SKILL.md` is byte-identical to `dist/<bundle>/skills/<name>/SKILL.md`, and its `LICENSE` and `NOTICE.md` are present |
| LQC-U003 | ≤ 100 entries (Cowork's archive upload limit) |
| LQC-U004 | ≤ 10 MB compressed and ≤ 50 MB uncompressed (Cowork's archive upload limits); each `.md` inside ≤ 1 MB |
| LQC-U005 | ≤ 20 files other than `SKILL.md`, `LICENSE` and `NOTICE.md`, and the two root notices themselves are the only extra files — the archive carries nothing the bundle folder does not |
| LQC-B001 | a mirrored bundle derives a skill that has no card under `skills/<name>/`. The message names the skill and says: write a card, or exclude it with a reason. One error per missing card, however many bundles derive it |
| LQC-K001 | `cowork` missing, or `tier`/`status`/`differs` missing or malformed; `tier` not an integer 0 to 4; `status` not one of the two; a known issue without `id`, `title`, `detail` or `failure`; a workaround without both keys; a duplicate known-issue `id` anywhere in the repository |
| LQC-K002 | `tier: 4` on a card in any bundle; `tier` 2 or 3 with no known issue; `status: probe-gated` with no known issue carrying `probe` |
| LQC-K004 | `capabilities.yaml` or `probes.yaml` malformed against each other: a code's evidence names an undefined probe; a probe tests an unknown code, has no `tests`, has no `harness`, or still declares `unlocks`; a skill level uses an unknown code or a level other than R/D/O; a facet has no evidence; evidence names an undefined probe; a card in the build has no capability entry |
| LQC-K005 | a capability code that no probe tests and that is not listed under `unprobed` with a reason (a warning when a listed code is in fact tested) |
| LQC-K006 | a profile's `TOOLS` differs from the strongest action-code level; a D level has no fallback wording; a card's known issue cites a probe whose `tests` touch none of the codes its cowork profile rates |
| LQC-K007 | a file in `probe-results/` is not valid `lq-harness-probe-results/1`, or records a probe `probes.yaml` does not define |
| LQC-K008 | `harness-probe/data/catalog.json`, `harness-probe/references/probes.md` or the generated blocks in the capability chart are out of date with their sources (`lqcowork catalog`, `lqcowork chart`) |

`LQC-B001`, `LQC-K001`, `LQC-K002` and `LQC-K004` to `LQC-K008` are read off
the cards and the repository data before anything is copied, and any of them stops the build there: half a bundle would bury
them under a manifest's worth of consequential errors. Every one is reported,
so a run names every card that needs work rather than the first.

`LQC-U001` to `LQC-U005` are read off the `.skill` archives themselves — by
`package` as soon as it writes one, and by `lqcowork archives`, which writes
and validates them from an existing build without building anything (it errors
if `dist/<bundle>/` is not there) — with `LQC-U002` comparing the archived `SKILL.md` against the
built bundle tree it came from. They carry the skill name and
`skills/<name>.skill` as their location.

Warnings (printed, and listed in the build report):

| Code | Rule |
| --- | --- |
| LQC-W001 | a vendor word from `transforms.vendor_words` survives in any `*.md` (case-sensitive whole word) |
| LQC-W002 | a `$name` or `` `/name` `` token for an upstream skill name survives |
| LQC-W003 | SKILL.md references a skill name (whole word, backticked or in "the X skill") that is not in the same bundle |
| LQC-W004 | a Markdown link or path in any `*.md` of the skill points outside the skill folder (`../`) or at a file that does not exist in the built skill |
| LQC-W005 | any `*.md` of the skill mentions `scripts/` or `schemas/` but the folder is absent from the built skill |
| LQC-W006 | SKILL.md body > 3,000 words |
| LQC-W007 | any `*.md` of the skill mentions `hooks`, `~/.lq/`, `CLAUDE_PLUGIN_ROOT`, `argument-hint`, or `disable-model-invocation` |
| LQC-W008 | a card's `bucket: amber` or `bucket: red` has no `notes` |
| LQC-W009 | any `*.md` of the skill contains a phrase from `transforms.host_words` (case-insensitive; default list: `lqprofile.md`, `the scribe`, `the validator`, `the renderer`, `run directory`, `PyMuPDF`, `Playwright`, `pdfplumber`, `pypdf`, `--dry-run`, `--yes`, `exit code`, `python interpreter`, `interpreter floor`, `subprocess`, `parallel workers`, `sidecar`) — host machinery that does not exist in Cowork |
| LQC-W010 | any `*.md` of the skill contains an `http(s)://` URL other than `https://github.com/LegalQuants/lq-plugin-oss` (external links and calls to action are not allowed in shipped skills; a URL that occurs anywhere in the upstream skill folder, in any file, is upstream-authored and exempt wherever the adaptation moved it to) |
| LQC-W011 | any `*.md` of the skill contains a phrase from `transforms.claim_words` (case-insensitive whole phrase; default list: `receipt`, `receipts`, `certified`, `coverage-certified`, `proved`, `proven`, `guaranteed complete`) — a claim the model cannot back with something the lawyer can inspect must not be worded as one |
| LQC-B002 | one per `exclude_skills` entry on a mirrored bundle, carrying its reason, so the build report and the drift report show what was left out and why |

Warnings report `file:line`. All W-codes run over every `*.md` in the built
skill unless the rule names SKILL.md. `LQC-W011` matches a whole phrase with
alphanumeric edges refused, so `proved` does not fire on `approved`, and
`receipt` does not fire on `receipts`, which is its own entry. Like every
warning it is suppressible through the card's `suppress` list, with a reason.

## 7. CLI

Package `lqcowork` in `tools/`, Python ≥ 3.11, runtime dependencies PyYAML,
Jinja2 and markdown-it-py and nothing else, dev dependencies pytest and black
(black-formatted, line length 88).

```
uv run --project tools lqcowork build      [--bundle ID | --skill NAME ...] [--report-anchors] [--upstream-path P] [--out DIR]
uv run --project tools lqcowork validate   [--bundle ID] [--out DIR]   # validates dist/<bundle>/ without rebuilding
uv run --project tools lqcowork package    [--bundle ID] [--out DIR]   # build + validate + zip + single-skill archives + trigger tests + report
uv run --project tools lqcowork site       [--out DIR]                # render <out>/site/ from a built <out>/ (section 9)
uv run --project tools lqcowork bump-upstream [--to REF] [--dry-run] [--report PATH]
uv run --project tools lqcowork anchor     [--skill NAME]              # set anchored_to = current pin after review
uv run --project tools lqcowork triggers   [--bundle ID] [--out DIR]   # write dist/<bundle>-trigger-tests.md only
uv run --project tools lqcowork archives   [--bundle ID] [--out DIR]   # write and validate dist/skills/<name>.skill from an existing build
uv run --project tools lqcowork release-check --tag vX.Y.Z [--out DIR] # does a tag agree with the tree?
uv run --project tools lqcowork catalog    [--check]                  # harness-probe/data/catalog.json + references/probes.md
uv run --project tools lqcowork chart      [--check]                  # regenerate the chart's <!-- gen:... --> blocks
uv run --project tools lqcowork verdicts                              # one line per probe-results file and baseline
```

The harness-probe skill has its own CLI, `harness-probe/scripts/hprobe.py`
(`init`, `status`, `steps`, `env`, `check`, `record`, `posture`, `report`,
`verdict`, `fixtures`), documented in its `SKILL.md`.

Exit codes: 0 ok, 1 error, 2 validation/anchor/release-check failure. Every
command prints a one-line summary per bundle; `package` prints one line per
skill archive under them (section 5b). `--upstream-path` lets
bump-upstream build against a temporary checkout without moving the pinned
submodule. `--out DIR` sends a build, and everything read back from it,
somewhere other than `dist/`, which is what lets two people — or a
reproducibility check that builds twice — work at once.

`build --skill NAME` is repeatable and is not combinable with `--bundle`. It
builds only those skills into `<out>/skills-only/<name>/` through every card
transform, and runs the checks that are about one skill folder — `ASKILL-P*`,
`LQC-C*`, `LQC-S*`, `LQC-D001`, `LQC-W*`, `LQC-K*` and `LQC-A001`. Bundle
assembly, the manifest checks, the zip and the report are skipped. There is
no bundle, so `LQC-W003` measures a hand-off against every card in the
repository instead: a name that exists somewhere passes. Card authors use it
before a skill is in any buildable bundle. A `--skill` with no card is a usage
error (exit 1), not `LQC-B001`, which is about a bundle's derived membership.

`bump-upstream`:

1. `git -C upstream fetch origin`; resolve `--to` (default `origin/main`) to a SHA.
2. Create a temporary worktree of upstream at that SHA (scratch dir).
3. Build all bundles against it with `--report-anchors`, collecting per skill:
   missing upstream folder; upstream `SKILL.md` changed since `anchored_to`
   (`git diff --stat anchored_to..SHA -- skills/<upstream>`); upstream
   `description` text changed; each `replace` rule whose count mismatched;
   each `sections.match` not found; each patch that failed; a full-file
   overlay whose upstream `SKILL.md` changed; companion files added/removed
   upstream; validation errors and warnings. Also list upstream skills that
   are in no bundle.
4. Write the Markdown report (default `dist/upstream-drift.md`).
5. Unless `--dry-run`: check the submodule out at the SHA, write
   `upstream.sha` in `cowork.yaml`, and print the next steps (review the
   report, fix cards, run `anchor`).
6. Exit 0 if nothing broke (informational changes only), 2 if any anchor or
   validation error, 1 on failure.

`release-check` is what a tag is held against before it is pushed, and again in
CI before the release is published. It only reads; it never builds and never
writes. `--tag` is required (omitting it is a usage error, exit 1). Four ways a
tag and the tree can disagree, each of them exit 2:

1. `--tag` is not `v` followed by a semver version — `v0.1.0`, `v1.2.0-rc.1`,
   `v1.2.0+20260918` all parse; `0.1.0`, `v1.2` and `v01.2.0` do not.
2. The tag's **release version** — the `MAJOR.MINOR.PATCH` core, with any
   pre-release or build metadata dropped — is not `package.version` in
   `cowork.yaml`. The core is what the comparison uses because the manifest
   version can be nothing else (LQC-M002), so `v1.2.0-rc.1` pairs with
   `version: 1.2.0`.
3. `CHANGELOG.md` is missing, or has no `## [X.Y.Z]` heading for this tag. The
   heading sought is the tag without its `v` (`## [1.2.0-rc.1]`); when the tag
   carries a pre-release or build suffix the core heading (`## [1.2.0]`) is
   accepted as well, so a release candidate may be described by the section it
   is a candidate for. Anything may follow the bracketed version on the heading
   line, which is where Keep a Changelog puts the date.
4. A built manifest disagrees. For every bundle, `dist/<bundle>/manifest.json`
   (or `<DIR>/<bundle>/manifest.json` under `--out`) is read **when it exists**
   and its `version` must equal the release version. A bundle that has not been
   built is reported as unbuilt and is not a failure — the check is as useful
   before `make package` as after it. A manifest that exists but is not JSON,
   like a missing `cowork.yaml`, is exit 1: the tree cannot be read, which is
   not the same as a tag being wrong.

Every check is printed, one line each, passes included, so a green run still
says what it looked at. Exit 0 when they all pass, 2 when any fails, 1 when the
repository could not be read.

## 8. Cowork facts the cards are written against

Verified against Microsoft documentation read on 19 September 2026; each bullet
that turns on a fast-moving fact carries its own date.

- **No local disk; a OneDrive-backed file surface instead.** "Cowork can't
  access or edit files stored locally on your device. It works with files in
  OneDrive and SharePoint." Session files live in the user's OneDrive `Cowork`
  folder; the side panel shows an Input folder and an Output folder; files
  Cowork creates remain reachable in that folder after the session; custom
  skills live in `/Documents/Cowork/skills/`. Companion files inside a package
  must use relative paths with no `..` traversal — that is a packaging rule
  about the uploaded `.zip`, not a rule about where a running skill may write.
- **No working directory that outlives the task.** While a task runs, Cowork
  processes files in a temporary isolated environment inside the Microsoft 365
  service boundary, which "removes the temporary environment when the task
  finishes" and which "Users can't view or access". Nothing written there
  survives, so no card may rely on a run directory, a scratch path or a ledger
  that outlasts the task.
- **State between sessions is undocumented, not forbidden.** Nothing says a
  skill cannot write a file into the user's own OneDrive `Cowork` folder and
  read it back later; nothing says it can, either. No card may depend on it
  until a tenant probe settles it, and no card may claim it is impossible.
- **No deletion of OneDrive or SharePoint content.** "Cowork can't delete files
  or folders in OneDrive or SharePoint." Attached files must be under 200 MB.
  Never instruct deletion and never promise clean-up; say that any intermediate
  file remains in the Output folder, and name it. (This rule is about file
  content. Users can still delete a skill or a scheduled task from the UI.)
- **Encrypted and labelled files.** The Cowork FAQ says Cowork cannot read
  encrypted files even where the user has access; the Purview article says an AI
  app can return label-encrypted data to a user holding EXTRACT as well as VIEW.
  Cards take the FAQ's stricter rule and never depend on reading a labelled or
  password-protected file.
- **Scripts: Microsoft's own pages disagree, and our position is provisional.**
  The plugin development page (17 September 2026) says a skill's `scripts/`
  folder is "Executed, not loaded into context", labels it "Executable
  utilities" and names `scripts/extract-clauses.py`; the Use Cowork page
  (14 September 2026) names "script execution" as a background operation and
  says code "is never executed during static checks". The Customize page
  (15 September 2026) says "A skill runs as instructions to the AI" and the
  manage-plugins page (1 September 2026) calls skills "Prompt-based workflows".
  Nothing reconciles them. No Microsoft page names an interpreter, a language
  version, an installed package, a dependency install path or an external
  binary; "python" does not appear on the plugin development page at all. Cards
  therefore ship no scripts and give every step a host-native path — because a
  script's runtime cannot be relied on, not because nothing runs. Revisit after
  the script probe.
- **Companion budget.** 20 companion files per skill, 5 MB each, 10 MB total,
  15 second download timeout. There is no documented file-type allow-list; the
  rules are about path safety and size.
- **Manifest features not yet supported** (plugin development page, 17 September
  2026). The conversion table marks `commands/` (slash commands), `agents/`
  (sub-agents) and `hooks/` (event handlers) "Not yet supported", and
  `settings.json` and `bin/` (executables) "Not applicable". That table
  describes what the `atk import openplugin` conversion carries over from a
  Claude plugin, so it is not a rule that a Cowork package may not contain a
  binary — but nothing documents a path for one either. Treat `commands/` as not
  yet supported rather than permanently absent, and re-check the table.
- **Two packaging channels with different limits.** Plugin package: up to 20
  skills per manifest (ASKILL-M002, `maxItems: 20` in the v1.28 schema), up to
  10 connectors, 256-character folder path (ASKILL-M003). Customize upload: a
  `.md` up to 1 MB, or a `.zip` / `.skill` archive up to 10 MB compressed, 50 MB
  uncompressed, up to 100 files. OneDrive folder drop: up to 50 custom skills
  per user.
- **Web reach exists, is tenant-controlled, and no card may depend on it** (as
  at September 2026; this is the fastest-moving fact here). Microsoft's web
  search article states it applies to Cowork, Cowork has no user-facing web
  search toggle, and an admin policy option can disable web search in Cowork by
  name — so search may simply be off in a given tenant. Browser use is Edge
  automation on the user's own device, web client only, and "disabled by
  default" until a tenant admin enables it (Learn page of 16 September 2026); it
  was announced Frontier-scoped in the GA post of 16 June 2026 and recorded as
  moving to general availability in August 2026. A skills-only package has no
  network channel of its own. The only declared channel is `agentConnectors`:
  Streamable HTTP over HTTPS with JSON-RPC 2.0, up to 10 per package, anonymous
  or OAuth vault or dynamic client registration, with outbound requests carrying
  `copilot-cowork/1.0`. API-key auth is declared in the schema but stated as not
  yet available in Cowork.
- **No receipts without a connector you operate.** Outside a declared
  `agentConnectors` MCP server, nothing documents a way for a skill to obtain a
  URL's raw bytes or to hash them. So no card may promise a fetch receipt, a
  SHA-256 of a source, or a quotation guaranteed to come from publisher bytes
  rather than a search or browser rendering. A remote MCP connector remains the
  honest route for anything that needs one.
- **Sessions and transcripts** (as at September 2026). Plugin skills "work
  within the current conversation context. They can read files you attached,
  reference earlier messages". Past sessions persist and can be reopened from
  the recent-tasks list — "resume a previous session", "Select any task to jump
  back into its session" — so on a resumed session the current conversation is
  itself a past session. What resumption restores to the model, as opposed to
  the screen, is undocumented. Nothing documents a tool or API by which a skill
  reads another session's log: Copilot memory and chat history are documented
  for Copilot Chat and never name Cowork; the Graph `aiInteractionHistory` API
  never names Cowork and offers only an application permission, with delegated
  access "Not supported". Purview retains Cowork "Conversation transcripts" for
  audit and eDiscovery in the user's mailbox (Purview page of 22 June 2026;
  audit page of 26 August 2026), but that is an admin surface, not something a
  skill can read. Where a card says "transcript" it must mean a document the
  lawyer supplies — a deposition or a meeting transcript — never a session log.
- **Built-in skills to hand off to, by exact name**, as listed by Microsoft on
  three Cowork pages dated 8 and 14 September 2026: Word, Excel, PowerPoint,
  PDF, Email, Scheduling, Calendar Management, Meetings, Daily Briefing,
  Enterprise Search, Communications, Deep Research, Adaptive Cards, and App
  (Frontier). **Keep "Deep Research" in this list.** A separate Researcher
  support page, updated 9 September 2026, says "Deep Research has been retired
  and Researcher is now the in-depth research experience available to Microsoft
  365 Premium and Pro subscribers" — but that is a statement about consumer
  plans, it never mentions Cowork, and three Cowork pages still name Deep
  Research as a Cowork built-in. Treat them as two features sharing a name. Have
  a tester confirm the name in a live tenant before it is changed here; do not
  rename it in this repo on the strength of a page about a different plan. HTML,
  Markdown, CSV and PDF files render in Cowork's preview pane.

The rules below are this repository's, not Microsoft's, and stand unchanged.

- Users invoke skills in natural language; Cowork routes on `description`.
  There is no `$name` or `/name` argument grammar; modes must be inferred
  from what the user says. Refer to sibling skills as "the cite-check skill".
- Skill body target is under ~2,000 words (< 5,000 tokens); detail belongs in
  `references/`, which the agent loads on demand. Reference companion files
  explicitly in the body so the agent knows they exist.
- Cowork scores skills on trigger clarity, instruction specificity, scope
  boundaries and robustness, and runs a conflict scan; explicit hand-offs
  between competing skills resolve conflicts.
- **Upload skill** (Customize page > Skills tab > arrow next to **Add**):
  accepts a `.md` with a single SKILL.md, or a `.zip`/`.skill` with `SKILL.md`
  at the root plus companions. Frontmatter must have `name` and `description`.
  A `.md` may be up to 1 MB; an archive up to 10 MB compressed, 50 MB
  uncompressed, 100 files. A skill whose name already exists is kept alongside
  the old one with a number appended, so re-uploads do not replace. Cowork
  shows a "only upload skills from sources you trust" reminder on first use.
  Uploaded skills land in `/Documents/Cowork/skills/` and appear after sync.
  Custom skills are not supported on mobile.
- Skill selection: Cowork activates a skill from its description, and the
  conversation's **Sources** picker lets the user choose plugins and skills
  for a request. Do not claim a `/` skill menu in chat, and do not claim a
  skill can see which other skills or bundles are installed.
- `lqplaybook.md`, `lqprofile.md` and "the scribe": upstream skills read
  personal preference files maintained by a companion skill that does not
  ship. In Cowork the rule for every skill is: it may read confirmed
  `[skill-name]` entries from an `lqplaybook.md` the lawyer has attached or
  placed in the session's Input folder; it never reads a profile file, never
  writes either file, never mentions a scribe or a journey; a preference
  discovered during the run is offered as one exact line the lawyer can add
  to their own file.
- Sibling bundles: lq-start may present the full map of all three bundles,
  each skill labelled with the bundles it belongs to, with one neutral
  sentence that a skill responds only if its bundle is available in the
  tenant and that plugin availability is managed by the Microsoft 365
  administrator. No other skill names a bundle it does not ship in. No
  shipped skill links to an external site, sign-up, assessment or product;
  the only URL a shipped skill may carry is the upstream repository in the
  licence notice. Two readings of that sentence are adopted for this release:
  citing a source by title and date, carrying no URL, is not a link; and
  relaying a link the lawyer supplied in their own session is not the skill
  linking to it.
- Nothing in a shipped skill may mention Codex, ChatGPT, Claude, "CODEX for
  Legal", hooks, `~/.lq/`, or another LegalQuants plugin as an install target.
  The closing line "CODEX for Legal is a workflow aid, not legal advice. The
  judgement stays yours." becomes "LegalQuants skills are a workflow aid, not
  legal advice. The judgement stays yours."

## 9. The site

`lqcowork site [--out DIR]` renders a static site into `<out>/site/` from a
build already sitting in `<out>/` (default `dist/`). It builds nothing: it
describes a build, so a tree that has not been packaged is an error, not a
thinner site. `make site` runs `package` and then `site`, which is the only
supported way to get one.

### What it reads

| Source | For |
| --- | --- |
| `cowork.yaml` | bundles, manifest names and descriptions, mirror lines, the package version, the upstream pin, the transform lists |
| `skills/<name>/skill.yaml` | the description, the triggers, the `cowork` block (tier, status, `differs`, known issues, workarounds), `notes`, `bucket` |
| `probes.yaml` | the probes page, and the link from a known issue to the probe that settles it |
| `capabilities.yaml`, `probe-results/*.json`, `harness-probe/scripts/hprobe_engine.py` | the verdicts page, the derived `unlocks` on the probes page |
| `upstream/plugin.release.yaml` | what upstream calls each mirrored plugin |
| `upstream/skills/<group>/<name>/SKILL.md` | the original description, quoted on the skill page |
| `<out>/<bundle>/skills/<name>/` | the files each skill actually ships; a skill in two bundles is read once |
| `<out>/skills/<name>.skill` | the size and file count shown beside a skill's upload archive; absent is not an error, and the link is written either way |
| `<out>/build-report.md` | the warnings table, shown per skill under a disclosure |
| `docs/INSTALL.md`, `docs/TESTING.md`, `CHANGELOG.md` | rendered through markdown-it-py (CommonMark plus tables, raw HTML escaped) |

`<out>/build-report.md` or a bundle's `<out>/<bundle>/skills/` tree missing is
an error (exit 1) whose message names what is absent and says to run `package`
first. A Markdown source that is absent is not: the page is still written, and
says which file it would have rendered and where to read it instead.

### Pages

| Page | Content |
| --- | --- |
| `index.html` | what this is and is not (an independent adaptation, not official, pre-release, nothing exercised in a live tenant); the bundles with skill counts, tier counts and links; the release assets by file name; how Cowork routes (natural language on the description, the Sources picker, no slash grammar); the tester call; a download block linking each bundle's zip by its latest-download URL with its skill count, the `.skill` archives through the downloads page, `SHA256SUMS` and the releases page; links to every other page and every skill |
| `bundles/<id>.html` | manifest name, ids and descriptions; the `Mirrors upstream plugin …` line with upstream's display name and description; the skills table (name, one-line purpose, tier, status, known-issue count); the trigger-test checklist as a table; a **Download** block at the top linking the zip, the trigger-test checklist and `SHA256SUMS`, and a `.skill` link on every row of the skills table |
| `skills/<name>.html` | what it does (the description's first sentence); when to use it (positive triggers); not for (negative triggers with the hand-off the checklist would print); the bundles it ships in; tier, status and bucket badges carrying the rubric; a **Get this skill** block after the badges with the `.skill` archive, what it is, its size and file count where one was built, and the bundle zips it also ships in; **How it differs from the original** (`cowork.differs`, with `notes` under a "Build notes" disclosure); known issues with failure shape and probe link; the workarounds table; the original description quoted; the upstream link at the pinned SHA; the files shipped; the build warnings; the UAT issue search |
| `known-issues.html` | every known issue across every card, with its skill, tier, failure shape and probe |
| `probes.html` | every probe in `probes.yaml`, the capability codes it tests and its cost, its prompt verbatim, what a pass and a fail look like, the worst outcome, what it unlocks (derived), and the harness-probe skill's steps for it |
| `verdicts.html` | the harness verdicts: one block per `probe-results/` file plus an empty baseline per profile, each with its four verdict lists (blocking capability and probe, or the fallback wording lost), what to probe next, cards that disagree with the verdict, and the probe coverage table |
| `differences.html` | the capability picture from section 8 in one screen; the mechanical transforms of section 5 in plain words; the claim-words rule with the list from `cowork.yaml`; the bundle structure against upstream's; the tier rubric with a count per tier; a table of every skill with its tier and a one-line `differs` excerpt |
| `downloads.html` | every published file in two tables: the bundle packages (name, skill count, `<id>.zip`, `<id>-trigger-tests.md`) and all the skill archives (skill, bundles, `<name>.skill`, and its size where one was built); then `SHA256SUMS`, `build-report.md`, the releases page, and the sentence about what "latest" resolves to |
| `install.html`, `testing.html`, `changelog.html` | the Markdown sources, rendered |

### Rules the pages keep

- **Reproducible.** Two runs of the same commit produce byte-identical files.
  There is no timestamp, no generated id and no ordering that depends on the
  filesystem; the only build-specific values on a page are the package version
  and the upstream SHA, both read from `cowork.yaml`.
- **Relative links only.** The site is served under `/lq-plugin-cowork/`, so
  no `href` or `src` is rooted at `/`. A page under `bundles/` or `skills/`
  reaches the root with `../`.
- **Release assets by their latest-download URL.** Every downloadable file
  is linked at `https://github.com/houfu/lq-plugin-cowork/releases/latest/download/<asset>`,
  which GitHub resolves to that asset on the most recent release that is not a
  pre-release. The assets are `<bundle.id>.zip` and
  `<bundle.id>-trigger-tests.md` per bundle, `<name>.skill` per skill,
  `build-report.md` and `SHA256SUMS`. No page names a version in a URL, so a
  release publishes without rebuilding the site; every download block says in
  as many words that those links resolve only once the current version is
  published. A size beside a `.skill` link is read from the built archive in
  `<out>/skills/`, so it is reproducible and absent rather than guessed when
  the archive is not there.
- **No external assets.** One stylesheet at `site/assets/site.css`, and
  nothing else fetched: no font service, no CDN, no image host. Links a reader
  clicks may of course leave the site.
- **No JavaScript beyond one filter.** The known-issues table carries an
  inline script that builds its own controls and hides rows. With scripting
  off there are no controls and the whole table is there, which is the only
  behaviour the page promises.
- **Card text is data.** Everything from a card, a probe or a manifest is
  escaped through Jinja2 autoescaping. Markdown sources are rendered with raw
  HTML escaped rather than passed through.
- **Design.** System fonts; light and dark through `prefers-color-scheme`;
  readable at phone width with a 16px side gutter and no horizontal page
  scroll; tables scroll inside their own wrapper; a skip link, landmark
  elements and a visible focus ring. Every page ends with the same footer: the
  package version, the upstream SHA linked to the tree at that commit,
  `Apache-2.0`, and the line that says this is not an official LegalQuants
  release.

### Publishing

`.github/workflows/site.yml` runs on a push to `main` and on
`workflow_dispatch`: checkout with submodules, `astral-sh/setup-uv` at the
version `build.yml` pins, `uv sync --project tools`, `make site`, then
`actions/configure-pages`, `actions/upload-pages-artifact` from `dist/site`
and `actions/deploy-pages`. Permissions are `contents: read`, `pages: write`
and `id-token: write`; the concurrency group is `pages`. The repository's
Pages source must be GitHub Actions. The published URL is
<https://houfu.github.io/lq-plugin-cowork/>.
