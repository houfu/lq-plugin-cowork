# NOTICE

This package contains skills adapted from the LegalQuants open skills project:

- Upstream: <https://github.com/LegalQuants/lq-plugin-oss>
- Licence: Apache License, Version 2.0 (a copy travels as `LICENSE` beside
  this file)

The skills in this package are **modified** versions of the upstream files.
They have been adapted to run inside Microsoft 365 Copilot Cowork, which has
no local filesystem, no shell and no plugin invocation grammar. The usual
changes are: removing bundled scripts, schemas and other files that cannot
execute in Cowork; replacing local-execution instructions with host-native
steps; rewriting each skill's `description` into Cowork trigger phrasing; and
removing references to particular AI hosts and to other LegalQuants plugins.

In accordance with section 4(b) of the Apache License 2.0, every modified
`SKILL.md` carries a prominent notice on its first body line recording that
it was modified, which Microsoft 365 Copilot Cowork it was adapted for, and
the exact upstream commit it was adapted from. The same commit is recorded in
each skill's frontmatter under `metadata.adapted-from`, so the provenance of
any shipped file can be checked against the upstream repository.

Every Markdown companion file the adaptation changed carries the same notice
as its first line, naming its own path within the upstream skill. A companion
with no upstream counterpart carries instead a notice recording that it was
added by the lq-plugin-cowork adaptation and is not an upstream LegalQuants
file. Material written for this adaptation — a set of calibration examples, a
playbook format reference, a rewritten section — is therefore never presented
as LegalQuants' work.

These packages are an independent adaptation. They are **not** an official
LegalQuants release, are not built or endorsed by the upstream project, and
are not supported by it. Report problems with an adapted skill to whoever
built this package, not to the upstream repository.

LegalQuants skills are a workflow aid, not legal advice. The judgement stays
yours.
