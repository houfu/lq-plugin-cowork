# Changelog

Everything notable that changes in this repository, newest first.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The
version numbers are the Teams manifest version in `cowork.yaml`
(`package.version`). Microsoft's guidance for app packages is to increment that
number for every update, and what a re-upload at the same number does is
undocumented, so every published change gets its own version.
[docs/RELEASING.md](docs/RELEASING.md) is how a release is cut.

## [Unreleased]

### Added

- Single-skill upload archives: every `package` run now also writes
  `dist/skills/<name>.skill` (`SKILL.md`, companions, `LICENSE` and
  `NOTICE.md`, one per shipped skill) alongside the two bundle zips, so a
  tester or lawyer can install one skill through Cowork's **Upload skill**
  control instead of a whole plugin. Built by the new `lqcowork archives`
  command, validated with five new rules, `LQC-U001`-`LQC-U005` (contract
  section 5b and section 6), and published as release assets next to the
  bundles, with their own checksums in `SHA256SUMS`.
- `metadata.version` stamped into every shipped `SKILL.md`, so a skill
  uploaded on its own still says which release it came from.
- "Route 0 — Upload a single skill" in [docs/INSTALL.md](docs/INSTALL.md): the
  fastest install path, needing no plugin, no administrator and no `atk`.

### Changed

- Labelled `skills/<name>/` as build inputs, not shippable skills, with a new
  [skills/README.md](skills/README.md) and a matching section in
  [README.md](README.md#get-the-skills): closes the confusion in
  [UAT issue 19](https://github.com/houfu/lq-plugin-cowork/issues/19), where a
  tester zipped `skills/pressuretest/` from this repository, found no
  `SKILL.md` in it, and rebuilt the skill by hand.

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
- Fourteen of the thirty-one upstream skills deliberately do not ship. Each one
  is a thin instruction layer over a local filesystem, a shell, a network fetch
  or a session transcript, none of which Cowork has.

[Unreleased]: https://github.com/houfu/lq-plugin-cowork/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/houfu/lq-plugin-cowork/releases/tag/v0.1.0
