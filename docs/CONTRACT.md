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
    tests/...
  docs/CONTRACT.md             # this file
  docs/RELEASING.md            # how a release is cut (contract section 7)
  dist/                        # generated, gitignored
  .github/workflows/           # build.yml, release.yml, upstream-drift.yml
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

replace: []                                          # global literal replacements, same shape as a card's replace list

bundles:
  - id: legalquants-litigation-cowork                # zip base name and dist folder
    guid: 3d3f0d5c-4a1b-5e9a-9f2c-7b2f4b0a1c11       # stable; generated once (uuid5) and pinned here
    name:
      short: LQ Litigation Skills                    # <= 30 chars (Teams manifest limit)
      full: LegalQuants litigation skills for Copilot Cowork   # <= 100 chars
    description:
      short: Litigation drafting, cite-checking, discovery and case organisation   # <= 80 chars
      full: >-                                       # <= 4000 chars; must say it is an adaptation
        ...
    skills:                                          # order = manifest order; <= 20; names must have a card
      - lq-start
      - writing
      - ...
  - id: legalquants-transactional-cowork
    ...
```

Bundle membership (decided; edit here, not in code):

| bundle | skills |
| --- | --- |
| `legalquants-litigation-cowork` | lq-start, writing, correspondence, client-update, depositions, new-matter, organize-case-docs, cite-check, pressuretest, document-discovery, legaldesign, timenarratives, wiki, closing-checklist, lq-mirror |
| `legalquants-transactional-cowork` | lq-start, closing-checklist, playbook-builder, playbook-review, legaldesign, timenarratives, wiki, lq-mirror |

Manifest ids, names and descriptions live only in `cowork.yaml`. The package
`description.full` must state that the bundle is adapted from
LegalQuants/lq-plugin-oss under Apache-2.0 and is not an upstream release.

## 4. The skill card: `skills/<name>/skill.yaml`

```yaml
name: wiki                        # == folder name == upstream skill name == Cowork folder name
upstream: core/wiki               # <group>/<name> under upstream/skills/
bucket: amber                     # green | amber  (from the portability assessment; informational)
anchored_to: fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0   # upstream SHA this card was written against

description: |                    # REQUIRED. Replaces upstream description wholesale. 1-1024 chars after strip.
  Keeps a Markdown legal wiki in a OneDrive folder ...
  Use when the user asks to "add this to the wiki", "what does the wiki say about", ...
  Do not use for drafting documents (use the writing skill) or ...

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

notes: |                          # REQUIRED for amber skills. What changed and why, for the README table and the drift report.
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

- `name`, `upstream`, `anchored_to`, `description`, `triggers` are required.
  `notes` is required when `bucket: amber`.
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
    `metadata.adapted-for: "Microsoft 365 Copilot Cowork"`. Existing
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
`dist/build-report.md` (per skill: bucket, files, bytes, warnings; per bundle:
skill count, manifest summary).

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
| LQC-W008 | a card's `bucket: amber` has no `notes` |
| LQC-W009 | any `*.md` of the skill contains a phrase from `transforms.host_words` (case-insensitive; default list: `lqprofile.md`, `the scribe`, `the validator`, `the renderer`, `run directory`, `PyMuPDF`, `Playwright`, `pdfplumber`, `pypdf`, `--dry-run`, `--yes`, `exit code`, `python interpreter`, `interpreter floor`, `subprocess`, `parallel workers`, `sidecar`) — host machinery that does not exist in Cowork |
| LQC-W010 | any `*.md` of the skill contains an `http(s)://` URL other than `https://github.com/LegalQuants/lq-plugin-oss` (external links and calls to action are not allowed in shipped skills; a URL that occurs anywhere in the upstream skill folder, in any file, is upstream-authored and exempt wherever the adaptation moved it to) |

Warnings report `file:line`. All W-codes run over every `*.md` in the built
skill unless the rule names SKILL.md.

## 7. CLI

Package `lqcowork` in `tools/`, Python ≥ 3.11, runtime dependency PyYAML only,
dev dependencies pytest and black (black-formatted, line length 88).

```
uv run --project tools lqcowork build      [--bundle ID] [--report-anchors] [--upstream-path P] [--out DIR]
uv run --project tools lqcowork validate   [--bundle ID] [--out DIR]   # validates dist/<bundle>/ without rebuilding
uv run --project tools lqcowork package    [--bundle ID] [--out DIR]   # build + validate + zip + trigger tests + report
uv run --project tools lqcowork bump-upstream [--to REF] [--dry-run] [--report PATH]
uv run --project tools lqcowork anchor     [--skill NAME]              # set anchored_to = current pin after review
uv run --project tools lqcowork triggers   [--bundle ID] [--out DIR]   # write dist/<bundle>-trigger-tests.md only
uv run --project tools lqcowork release-check --tag vX.Y.Z [--out DIR] # does a tag agree with the tree?
```

Exit codes: 0 ok, 1 error, 2 validation/anchor/release-check failure. Every
command prints a one-line summary per bundle. `--upstream-path` lets
bump-upstream build against a temporary checkout without moving the pinned
submodule. `--out DIR` sends a build, and everything read back from it,
somewhere other than `dist/`, which is what lets two people — or a
reproducibility check that builds twice — work at once.

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

- Cowork has no local filesystem. Session files live in the user's OneDrive
  `Cowork` folder (side panel shows Input folder / Output folder); custom
  skills live in `/Documents/Cowork/skills/`. Cowork cannot read encrypted or
  sensitivity-labelled files and cannot delete files.
- Whether bundled scripts execute is undocumented. Cards assume **no script
  runs**. Every step must have a host-native path (Cowork reads documents,
  drafts, and produces Word/Excel/PowerPoint/PDF/HTML/Markdown itself).
- Built-in skills to hand off to, by exact name: Word, Excel, PowerPoint,
  PDF, Email, Scheduling, Calendar Management, Meetings, Daily Briefing,
  Enterprise Search, Deep Research, Communications, Adaptive Cards, App.
  HTML, Markdown, CSV and PDF files render in Cowork's preview pane.
- Users invoke skills in natural language; Cowork routes on `description`.
  There is no `$name` or `/name` argument grammar; modes must be inferred
  from what the user says. Refer to sibling skills as "the cite-check skill".
- Skill body target is under ~2,000 words (< 5,000 tokens); detail belongs in
  `references/`, which the agent loads on demand. Reference companion files
  explicitly in the body so the agent knows they exist.
- Cowork scores skills on trigger clarity, instruction specificity, scope
  boundaries and robustness, and runs a conflict scan; explicit hand-offs
  between competing skills resolve conflicts.
- Cowork cannot delete files. Never instruct deletion or claim clean-up; say
  that any intermediate file remains in the Output folder and name it.
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
- Sibling bundle: lq-start may present the full map of both bundles, each
  skill labelled with its bundle, with one neutral sentence that a skill
  responds only if its bundle is available in the tenant and that plugin
  availability is managed by the Microsoft 365 administrator. No other skill
  names the other bundle. No shipped skill links to an external site,
  sign-up, assessment or product; the only URL a shipped skill may carry is
  the upstream repository in the licence notice.
- Nothing in a shipped skill may mention Codex, ChatGPT, Claude, "CODEX for
  Legal", hooks, `~/.lq/`, or another LegalQuants plugin as an install target.
  The closing line "CODEX for Legal is a workflow aid, not legal advice. The
  judgement stays yours." becomes "LegalQuants skills are a workflow aid, not
  legal advice. The judgement stays yours."
