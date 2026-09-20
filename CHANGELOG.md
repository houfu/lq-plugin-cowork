# Changelog

Everything notable that changes in this repository, newest first.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The
version numbers are the Teams manifest version in `cowork.yaml`
(`package.version`). Microsoft's guidance for app packages is to increment that
number for every update, and what a re-upload at the same number does is
undocumented, so every published change gets its own version.
[docs/RELEASING.md](docs/RELEASING.md) is how a release is cut.

## [Unreleased]

## [0.2.0] - 2026-09-20

Every upstream skill now ships, in three bundles that mirror the three plugins
upstream publishes. If you installed 0.1.0, read *Changed* before you upgrade:
two skills move bundles.

### Added

- **`legalquants-companion-cowork`**, a third bundle — 8 skills: `legalquants`,
  `lq-ask`, `lq-connect`, `lq-mirror`, `lq-reflect`, `lq-apply`,
  `my-lq-moment` and `lq-start`. It mirrors upstream's `legalquants-companion`
  plugin: your journey with AI as a lawyer — ask, assess, reflect, apply,
  connect. Install it on its own; it is for the lawyer, not the matter.
- **The fourteen skills 0.1.0 left out**, adapted rather than ported, each with
  a risk tier saying how far its promise moved from the original. Tier 1, on
  documented capabilities with loud failures: `regulatory`. Tier 2, one named
  probe or a degrade announced in the reply: `read-redline`,
  `definition-check`, `diligence`, `docreview`, `my-lq-moment`. Tier 3,
  re-scoped so the promise itself changed and the description says so:
  `sigpack`, `closing-bible`, `conform`, `legalquants`, `lq-ask`, `lq-connect`,
  `lq-reflect`, `lq-apply`. `read-redline` ships probe-gated: it works, and it
  says in the reply that it could not confirm it can see tracked changes until
  probe P3 comes back from a live tenant.
- **A `cowork:` block on every card**, required by the build: the tier, the
  status, a paragraph written for a lawyer saying how the skill differs from
  the original, the known issues with their failure mode — silent or loud — and
  the workarounds the adaptation puts in place of upstream's machinery. New
  validation codes enforce it: `LQC-K001` (the block is missing or malformed),
  `LQC-K002` (a tier that needs a connector, or a tier 2 or 3 card with no
  known issue), `LQC-K003` (a known issue naming a probe that does not exist),
  and `LQC-W011`, which warns when a built skill uses a word — *receipt*,
  *certified*, *proved*, *guaranteed complete* — to claim something the lawyer
  cannot inspect. `LQC-B001` and `LQC-B002` cover the mirrored bundles.
- **`probes.yaml`**, the fourteen capability probes: the questions about Cowork
  that nobody has answered in a live tenant, each with the exact prompt a
  tester types, what a pass and a fail look like, and which skills the result
  unlocks. [docs/TESTING.md](docs/TESTING.md) Part E is the tester's version,
  and each probe has or will have its own `uat` issue.
- **A site**, built from these same sources and published from `main`:
  <https://houfu.github.io/lq-plugin-cowork/>. The bundles and their skills,
  what changed for each one, every known issue filterable by failure mode and
  probe, the probes themselves, the install and testing guides, and a
  downloads page linking every release asset:
  <https://houfu.github.io/lq-plugin-cowork/downloads.html>.
- `lqcowork build --skill NAME` builds one skill through every transform and
  check without needing it to be in a buildable bundle, which is what a card
  author wants while writing one. `lqcowork site` renders the site from a built
  `dist/`; `make site` runs both.
- **One `.skill` archive per skill, all thirty-one of them**, a release asset
  alongside the three bundles: every `package` run now also writes
  `dist/skills/<name>.skill` — `SKILL.md` at the root, that skill's companion
  files, `LICENSE` and `NOTICE.md` — so a tester or lawyer can install one
  skill through Cowork's **Upload skill** control instead of a whole plugin.
  Built by the new `lqcowork archives` command, validated with five new rules,
  `LQC-U001`-`LQC-U005` ([docs/CONTRACT.md](docs/CONTRACT.md) section 5b and
  section 6), and published as release assets next to the bundles with their
  own checksums in `SHA256SUMS`.
- **"Route 0 — Upload a single skill"** in [docs/INSTALL.md](docs/INSTALL.md):
  the fastest install path, needing no plugin, no administrator and no `atk`,
  with an upload troubleshooting checklist when Cowork refuses an archive.
- **`metadata.version` in every built `SKILL.md`**, stamped from
  `cowork.yaml`'s `package.version`. A `.skill` archive carries no
  `manifest.json`, so this is the only place a skill uploaded on its own says
  which release it came from.

### Changed

- **Bundle membership now mirrors upstream's, so two skills move.**
  `closing-checklist` is transactional only — it is no longer in the litigation
  bundle. `lq-mirror` is in the companion bundle only — it is no longer in
  either practice bundle. If you were reaching for one of those from the other
  bundle, install the bundle it now lives in. The litigation bundle stays at
  15 — it loses those two and gains `regulatory` and `docreview` — and the
  transactional bundle goes from 8 skills to 14.
- A bundle can now declare that it mirrors an upstream plugin instead of
  listing its skills, so membership is derived from
  `upstream/plugin.release.yaml` at build time. A skill upstream adds to a
  mirrored group fails the build with `LQC-B001` — write a card, or exclude it
  with a reason — rather than disappearing quietly.
- **The capability statement was wrong and is corrected.** 0.1.0 said Cowork
  has no filesystem, no shell, no network fetch and no transcript access. What
  Microsoft actually documents is narrower and stranger: Cowork works from
  OneDrive and SharePoint rather than a local disk; it documents a skill's
  `scripts/` folder as executed while three other pages call a skill
  prose-only, and no page anywhere names an interpreter, a package or a binary;
  web reach exists but is tenant-controlled and off by default for browser use;
  and nothing gives a skill a URL's raw bytes to hash. Cards still ship no
  scripts — because a script's runtime cannot be relied on, not because nothing
  runs. [docs/CONTRACT.md](docs/CONTRACT.md) section 8 carries the full
  corrected list, dated, with Microsoft's own words.
- **From 0.2.0, a release is published as GitHub's latest rather than as a
  pre-release**, unless its tag carries a suffix such as `-rc.1`. v0.1.0 stays
  marked pre-release as it was published. This is a packaging change only:
  *Known limitations* below still says nothing here has run in a live tenant.
- **`skills/<name>/` is labelled a build input, not a shippable skill**, with a
  new [skills/README.md](skills/README.md) and a matching section in
  [README.md](README.md#which-do-i-want): closes the confusion in
  [UAT issue 19](https://github.com/houfu/lq-plugin-cowork/issues/19), where a
  tester zipped `skills/pressuretest/` from this repository, found no
  `SKILL.md` in it, and rebuilt the skill by hand.

### Known limitations

- **Nothing here has been exercised in a live Microsoft 365 Copilot Cowork
  tenant.** That was true of 0.1.0 and it is still true. The packages build and
  validate as far as the tooling can tell, and every skill has been read
  against what Cowork documents, but no skill has been sideloaded, triggered or
  run against real documents. Treat every routing and behaviour claim as
  untested: [docs/TESTING.md](docs/TESTING.md) says how to report what you
  find.
- **Sixteen of the thirty-one skills ship at tier 2 or 3** — thirteen of the
  fourteen re-admitted ones, plus `cite-check`, `timenarratives` and
  `playbook-review`. That means a weaker guarantee than upstream gives,
  announced in the reply rather than hidden. The characteristic failure of most
  of them is silent — a count the model performed itself, an occurrence it did
  not notice — which is why each of those skills hands back a workbook or a
  stated count you can check in seconds. Every known issue is listed on the
  site with its failure mode.
- **Fourteen capability probes are unrun.** Their results move tiers: P3
  (tracked changes) releases `read-redline` from its degrade, P9 (workbook
  round trip) settles the register pattern four skills rest on, P11 (what a
  skill can quote of its own session) settles `lq-reflect` and `my-lq-moment`,
  and P14 (Enterprise Search as a people finder) settles `lq-connect`.
- **`lq-ask` answers from a library that has to be written and dated.** It
  cites by title and date, never by link, and says in every answer what it
  could not look at and how old the library is.
- **`docreview`'s privilege hold is a rule the model applies, not a lock.**
  Upstream, only a `not-privileged` ruling released a document, enforced by a
  record. Here the privilege state is the register's first column, the held
  count and ids are stated before anything is produced, no quoted text from a
  held document is written anywhere, and no register attached means no findings
  at all — and it is still a rule and not a lock. Read `KI-docreview-1` before
  you put a real production through it.

## [0.1.0] - 2026-09-18

The first release: two Microsoft 365 Copilot Cowork plugin packages built from
the open LegalQuants skills, seventeen distinct skills between them.

### Added

- **`legalquants-litigation-cowork`** — 15 skills: `lq-start`, `writing`,
  `correspondence`, `client-update`, `depositions`, `new-matter`,
  `organize-case-docs`, `cite-check`, `pressuretest`, `document-discovery`,
  `legaldesign`, `timenarratives`, `wiki`, `closing-checklist`, `lq-mirror`.
- **`legalquants-transactional-cowork`** — 8 skills: `lq-start`,
  `closing-checklist`, `playbook-builder`, `playbook-review`, `legaldesign`,
  `timenarratives`, `wiki`, `lq-mirror`. Six skills ship in both bundles, so the
  two packages cover seventeen distinct skills.
- Upstream pinned at
  [`fa5a668`](https://github.com/LegalQuants/lq-plugin-oss/commit/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0)
  and vendored read-only as a git submodule. Nothing in this repository edits
  it: the adaptation is a selection manifest, mechanical transforms and one card
  per skill, layered so that an upstream release breaks loudly rather than
  silently. Every adapted file carries its Apache-2.0 section 4(b) notice, and
  upstream's `LICENSE` and this repository's `NOTICE.md` travel at the root of
  each zip.
- `lqcowork`, the build tooling behind `make`: `build`, `validate`, `package`,
  `triggers`, `bump-upstream`, `anchor` and `release-check`. It emits a Teams
  v1.28 manifest, byte-reproducible zips, a routing acceptance-test checklist
  per bundle and a build report, and it enforces the validation rules in
  [docs/CONTRACT.md](docs/CONTRACT.md) section 6.
- A weekly upstream drift check that builds every bundle against the current
  upstream `main`, and opens or updates one issue when a vendored skill has
  moved or an adaptation no longer applies.
- Tag-driven releases: `make release TAG=vX.Y.Z` checks the tag against the
  tree and pushes it, and CI tests, packages, verifies the build is
  reproducible, and publishes the zips, the trigger-test checklists, the build
  report and `SHA256SUMS` as release assets.

### Known limitations

- **Nothing here has been exercised in a live Microsoft 365 Copilot Cowork
  tenant.** The packages build and validate as far as the tooling can tell, and
  the skill content has been read against what Cowork can actually do, but no
  skill has been sideloaded, triggered or run against real documents.
  Treat every routing and behaviour claim as untested, and report what you find:
  [docs/TESTING.md](docs/TESTING.md) says how.
- Fourteen of the thirty-one upstream skills deliberately do not ship. Each is
  a thin instruction layer over machinery a Cowork skills-only package cannot
  carry: arbitrary local paths and a working directory that outlives the task,
  bundled binaries behind a script runtime Microsoft documents as executed but
  never specifies, raw fetched bytes that can be hashed into a receipt, or the
  agent's own past session logs. *(Corrected in 0.2.0, which ships all
  thirty-one as Cowork-native adaptations; the sentence as first published
  overstated what Cowork lacks.)*

[Unreleased]: https://github.com/houfu/lq-plugin-cowork/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/houfu/lq-plugin-cowork/releases/tag/v0.2.0
[0.1.0]: https://github.com/houfu/lq-plugin-cowork/releases/tag/v0.1.0
