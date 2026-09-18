<!--
Thanks for the pull request. Keep it small and single-purpose: one skill, or one
tooling change. A description fix and a build change do not belong on the same
branch. CONTRIBUTING.md has the detail behind every box below.
-->

## What this changes

<!-- One or two sentences. If it fixes a UAT report, link the issue: "Fixes #12". -->

## Why this layer

<!--
Which adaptation layer did you use, and why was nothing higher enough?
The ladder, highest first:
  exclude → replace (with expect:) → sections: overlay → patch → full-file SKILL.md overlay
Skip this if the change is tooling or documentation only.
-->

## Checklist

- [ ] **Highest layer that works.** A `replace` would not have done it, a
      `sections:` overlay would not have done it, and the PR says why.
- [ ] **`make package` is green.** No new errors. Any new warning is either
      fixed or suppressed in the card with a `reason`.
- [ ] **Card `notes` updated.** If the built output changed, the card records
      what changed and why. An amber card with no `notes` fails the build.
- [ ] **No edits under `upstream/`.** The submodule is read-only; the pin has
      not moved unless this PR is a deliberate upstream bump.
- [ ] `make test` passes, and `make fmt-check` is clean if Python changed.
- [ ] Trigger tests regenerated where a `description` or `triggers` changed, and
      the misfiring prompt added to `triggers` if this fixes a routing report.
