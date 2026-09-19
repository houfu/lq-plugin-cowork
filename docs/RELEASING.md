# Cutting a release

A release is a tag. `make release TAG=vX.Y.Z` checks the tag against the tree
and pushes it; [.github/workflows/release.yml](../.github/workflows/release.yml)
does the rest — tests, packaging, a reproducibility check, and a GitHub release
carrying both zips. Nothing is built on your machine and uploaded by hand, so
what people download is what CI built from the tagged commit.

This is the maintainer's procedure. It needs no secrets: the workflow runs with
the repository's own `GITHUB_TOKEN` and `contents: write`.

## Why the version has to move

`package.version` in `cowork.yaml` becomes `version` in each bundle's
`manifest.json`. **Microsoft's guidance for Microsoft 365 app packages is to
keep the app id and increment the version for every update.** No Microsoft page
says what a re-upload that keeps the same number does — rejected, ignored or
replaced — so [docs/INSTALL.md](INSTALL.md) lists it as unverified, and the only
safe assumption is that a tenant served a second package calling itself 0.1.0
keeps the old skills. So every published change, including a one-word fix to
one description, gets a new version. There is no such thing as re-issuing a
version here.

Semver applied to skills, roughly: **patch** for wording, a description tweak, a
fixed link; **minor** for a new skill in a bundle, or a skill that now does
something it did not; **major** for a bundle that loses a skill or changes what
the packages are for. While the major is 0, everything is a pre-release
(see below).

## The procedure

1. **Bump the version.** In `cowork.yaml`, `package.version: X.Y.Z`. That one
   line is the whole version: the manifests, the build report and the
   trigger-test checklists all read it.

2. **Move the changelog.** In `CHANGELOG.md`, turn the accumulated
   `## [Unreleased]` entries into `## [X.Y.Z] - YYYY-MM-DD`, leave a fresh empty
   `## [Unreleased]` above it, and add the link reference at the foot of the
   file:

   ```markdown
   [Unreleased]: https://github.com/houfu/lq-plugin-cowork/compare/vX.Y.Z...HEAD
   [X.Y.Z]: https://github.com/houfu/lq-plugin-cowork/releases/tag/vX.Y.Z
   ```

   This section is not housekeeping: it is pasted verbatim into the release
   notes, so write it for someone deciding whether to install the thing.

3. **Build it.** `make package`. It must end with zero errors; read the warnings
   and decide about each one. `dist/` now carries manifests at the new version,
   which is what `release-check` compares against. `validate` already enforces
   `SKILL.md` at the root of every `dist/skills/<name>.skill` (`LQC-U001`), but
   open one by hand anyway (`unzip -l dist/skills/<name>.skill`, or a zip
   viewer) as a last human check before anyone downloads it — this is exactly
   the thing UAT issue 19 found missing when a folder was zipped by hand.

4. **Commit.** The version bump and the changelog belong in one commit on the
   default branch, pushed, green in CI. `make release` refuses to tag a dirty
   tree, and a tag on an unpushed commit is a tag nobody else can resolve.

5. **Release.**

   ```sh
   make release TAG=vX.Y.Z
   ```

   It refuses, and does nothing at all, when the working tree is not clean, when
   the tag already exists here or on `origin`, or when `make release-check` says
   the tag and the tree disagree. Otherwise it creates an annotated tag and
   pushes that tag alone.

   To see the verdict without tagging anything, run the check on its own:

   ```sh
   make release-check TAG=vX.Y.Z
   ```

   It exits 2 and says which of these is wrong: the tag is not `v` plus a semver
   version; `package.version` is not the tag's version; `CHANGELOG.md` has no
   `## [X.Y.Z]` section; a built `dist/<bundle>/manifest.json` still carries the
   old version. Contract section 7 has the exact rules.

## What CI does with the tag

The `release` workflow runs on any pushed tag matching `v*`:

1. checks out the tag with its submodule, installs the tooling;
2. `make test`, `make fmt-check`, `make package`;
3. `make release-check TAG=<tag>` — the same check again, on a clean checkout,
   so a tag that was pushed some other way cannot skip it;
4. packages a **second** time into another directory and fails unless every
   zip *and* every single-skill archive under `dist/skills/*.skill` has the
   same SHA-256 as the first. The zips and the archives are byte-reproducible
   by construction; this is what keeps that true;
5. writes `dist/SHA256SUMS` over the zips, the single-skill archives and the
   Markdown assets;
6. composes the notes: this version's `CHANGELOG.md` section, a table of the
   bundles with their skills and zip sizes, an "Upload one skill" table listing
   every `<name>.skill` archive with its size and a pointer to Route 0 in
   `docs/INSTALL.md`, the upstream pin as a link to the exact commit, pointers
   to `docs/INSTALL.md` and `docs/TESTING.md`, the sentence that these bundles
   are an independent adaptation under Apache-2.0 and not an official
   LegalQuants release, and the checksums;
7. creates the release, titled with the tag, carrying:

   | Asset | What it is |
   | --- | --- |
   | `legalquants-litigation-cowork.zip` | the litigation package |
   | `legalquants-transactional-cowork.zip` | the transactional package |
   | `<name>.skill` (17 files) | one skill's `SKILL.md`, companions, `LICENSE` and `NOTICE.md` — upload-ready via Cowork's Upload skill control (contract section 5b) |
   | `legalquants-litigation-cowork-trigger-tests.md` | its routing checklist |
   | `legalquants-transactional-cowork-trigger-tests.md` | its routing checklist |
   | `build-report.md` | what went into the build: skills, buckets, files, bytes, warnings, suppressed warnings |
   | `SHA256SUMS` | checksums for all of the above |

Watch it in the Actions tab. If it fails, nothing is published: fix the cause,
and re-run the workflow against the same tag (below) rather than inventing a new
one.

## Re-publishing an existing tag

Actions → **release** → **Run workflow** → `tag: vX.Y.Z`. The workflow accepts
an existing tag as an input, checks that commit out, rebuilds it, and updates
the release in place: assets are re-uploaded with `--clobber` and the notes are
rewritten. Use it when the release notes came out wrong, when an asset failed to
upload, or when a CI-side failure meant no release was created at all.

It rebuilds from the tagged commit, so it will not pick up a fix you have only
committed to the default branch. A changed build needs a new version.

## Pre-releases

A release is marked "pre-release" on GitHub when either is true:

- the tag has a suffix — `v1.2.0-rc.1`, `v2.0.0-beta.2`; or
- the major version is 0.

So everything in the 0.x series is a pre-release, which is the honest label
while no skill has been exercised in a live Cowork tenant. A suffixed tag pairs
with an unsuffixed `package.version` — `v1.2.0-rc.1` ships `version: 1.2.0` —
because the Teams manifest version can only be `x.y.z`. Its changelog section
may be `## [1.2.0-rc.1]` or the `## [1.2.0]` section it is a candidate for.

## Withdrawing a bad release

A published zip cannot be unpublished from other people's downloads, so the
order is: stop the bleeding, then supersede it.

1. **Delete the release**, which removes the assets and the notes:

   ```sh
   gh release delete vX.Y.Z            # keeps the tag
   gh release delete vX.Y.Z --cleanup-tag   # and deletes the tag
   ```

2. **Decide about the tag.** Keep it if the release was public long enough for
   anyone to have taken it: the tag is then a true record of what they have, and
   deleting it makes their zip unexplainable. Delete it only for a release
   nobody could have seen — a wrong build published and caught in minutes:

   ```sh
   git push origin --delete vX.Y.Z
   git tag -d vX.Y.Z
   ```

   Never move a tag that has been pushed. A tag that once pointed at something
   published and now points at something else is the one failure mode that makes
   a checksum worthless.

3. **Bump and release again.** Fix the cause, add a changelog entry saying what
   was wrong with the withdrawn version, bump `package.version` — the withdrawn
   number is spent, because a tenant that installed it will not take a package
   that calls itself the same thing — and go through the procedure again.

If the problem is a bad *skill* rather than a bad build, the same rule holds:
the fix ships as a new version, and the release notes say what changed.
