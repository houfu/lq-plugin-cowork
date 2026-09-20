## Before you start

- Read [references/schemas.md](references/schemas.md) and
  [references/framework-schema.md](references/framework-schema.md) in full.
  They define the master register and the framework, and every artifact you
  produce has to match them.
- Before producing any page for the lawyer, read
  [references/review-ui.md](references/review-ui.md) in full. It is the
  contract for the setup, test-results and crosswalk pages.
- Before the substantive passes, read
  [references/shared/execution-modes.md](references/shared/execution-modes.md),
  which is how this review runs, and the contract for whichever pass you are
  about to make:
  [one-document reading](references/shared/metadata-reader-prompt.md),
  [one relationship pair](references/shared/edge-resolver-prompt.md),
  [one unit against one lens](references/shared/finding-worker-prompt.md), or
  [checking one finding](references/shared/finding-checker-prompt.md).
- If the lawyer has attached an `lqplaybook.md`, or placed one in the session's
  Input folder, read only its confirmed `[diligence]` entries — default lenses,
  optional materiality rules, report voice, register format — and apply them.
  Do not read any profile file, and never write to the playbook. A preference
  that emerges during the run is offered as one exact `[diligence]` line the
  lawyer can add to their own file; it shapes future work only once they have
  added it.
- Taking documents in: an attached file must be under 200 MB, and an encrypted
  file cannot be read at all, even where the lawyer has access. Say both in the
  first reply of any run that takes a room in, try every file, and park with a
  stated reason whatever did not open.
- Confidentiality: no client-identifying facts in any artifact except the
  report surfaces themselves. Nothing leaves this session; there is no channel
  by which it could. Working files stay in the session's Output folder — they
  cannot be deleted, so name them on delivery rather than describing them as
  cleared away.
- Say once, in the first reply and again on the delivery, what this run does
  not do: it never calls the result complete or verified beyond its own careful
  reading, it works a tranche at a time, and it parks what it cannot read.
