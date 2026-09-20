# How a review runs here

One legal method, one set of per-pass contracts, one path. The original skill
chose between a bundled program and a portable fallback at the start of a run.
Here there is no program to choose, so the portable path is the only path, and
it is described below as the method rather than as a degrade.

State this once, before any long stretch of work, in the lawyer's own terms:
the method is the same, the assurances are not the same, and the account below
says exactly which checks the original performed automatically and this run
performs by reading.

## The one path

1. Work through the room one document at a time, in the order the plan sets.
   Each document, each candidate pair, each unit and lens, and each checking
   pass gets its own focused pass against the same contract and the same
   result shape, and nothing is decided across several units at once.
2. Produce the artifact shapes named in the data-contract reference for each
   step. Where a shape was a file a program validated, it becomes a row in the
   master register or a named Markdown or JSON file in the Output folder.
3. Keep the authoritative state in the master register. Nothing is held only in
   the conversation, because the conversation does not travel to the next
   session and the register does.
4. Before advancing a gate, check by reading: that every identifier resolves,
   that every quoted passage belongs to the document it is attributed to, that
   every issue has a row for every reviewable unit or a visible parked reason,
   and that the counts agree. A second, separate pass still looks at every
   finding that matters, seeing the finding and its quote but not the reasoning
   that produced it.
5. Park any document or claim whose text, quote, membership or count cannot be
   checked against something readable. Never turn a check that could not run
   into confidence.

## What the lawyer brings in, and its limits

Documents arrive as attachments, or in the session's Input folder. Two limits
belong in the first reply of any run that takes documents in:

- A single attached file must be under 200 MB. Say so when a room contains
  anything larger, and ask the lawyer to split or supply it another way.
- Encrypted files cannot be read at all, even where the lawyer has access.
  Attempt each one, list the ones that came back unreadable, and park them
  with that reason. A sensitivity label on a file is not the same thing: try a
  labelled file, and report what actually happened rather than assuming.

Selecting a whole folder as one unit is not something to rely on; documents are
chosen file by file.

## Tranches

The room is worked a tranche at a time, one tranche per session.

- **The lawyer chooses the tranche.** There is no published limit on how many
  documents one session may take, so no ceiling is inferred here. Propose a
  size, say what it rests on, and let the lawyer set it.
- **The method does not change between tranches.** Same framework, same gates,
  same quote rule, same second pass. What changes is the boundary, and the
  boundary is stated on every delivery, not only at the end.
- **Each tranche's rows are appended to the master register**, which the lawyer
  keeps and attaches at the start of the next session.
- **When the register is not attached**, say so in the first reply, name the
  file that was expected, and say which tranches are on the record and which
  are not. What happens next depends on what the register carries: where it
  carries only continuity, the run continues on the reduced scope it can see;
  where it carries a lawyer's hold, the run stops.
- If a tranche's outputs are handed over as one download, that archive holds at
  most 50 files and 500 MB, which is a real constraint on tranche size.

A recurring or fixed-time run can be set up in ordinary language, with a page
listing past and upcoming runs, and a cap of 25 scheduled prompts in total.
Whether such a run picks up files placed earlier and writes its outputs back is
not something this skill relies on: offer it as something the lawyer may set
up, never as a step in the method.

## The quality gate before scale

Substantive issue mapping is a high-recall legal judgment task. Read carefully
and slowly on this work, and more carefully still on scanned, long, dense or
high-consequence material.

Calibrate before scale. The sample must contain at least one responsive
document whose responsiveness was confirmed against the source and one
plausible negative, and the same method must recover every known positive at
the same batch size planned for the full run. Schema-shaped answers, valid
quotes and a fast pass do not establish recall. An all-negative result on
image-only material gets a second, bounded look during calibration. A missed
known positive stops the scaling step: change the approach, the batch size or
the framing, and get the revised plan confirmed.

No single pass takes more than 12 issues at once. Fewer for long, image-heavy
or fact-dense units. Nothing raises that bound.

## What is not the same as the original

Say this once, before any long stretch of work, and put it on the delivery:

- The identity of a file here is a fingerprint read from the file — its name,
  its page count, its date, the first line of its first page — compared again
  at the start of the next session. It is not a cryptographic hash, and it
  does not detect a change that leaves all four the same.
- Quotes are located by reading, not by an automatic text match. Every quoted
  passage is found again in the source and its place recorded, and that is a
  careful reading rather than a machine check.
- The second pass is a second pass by the same reader working from the finding,
  the quote and the framework item alone, without the first pass's reasoning.
  Record it as a second pass. Do not call it independent review.
- The count reconciliation is arithmetic in a workbook the lawyer can open and
  check, not a check performed by a program. That is why it lives in the
  register rather than in a sentence.
- Because of all four, the result is a clearly labelled review with an
  unresolved queue beside it. It is never described as verified by anything
  other than this skill's own reading, and never in the vocabulary of formal
  assurance: nothing here is a warrant of completeness, and no artifact is
  described as one.

Name the checks that could not run, each time, in those words. The method
carries across; the assurance does not.

## Failure, parking and picking up again

- Retry a rejected judgment at most twice, then park it with a reason.
  A problem reading a file is not a judgment failure and has its own small
  budget. A fault that repeats in the same way stops the run.
- Parked work never restarts quietly. Unparking is a visible decision by a
  named person with a stated reason, recorded as a row.
- The register's status column is the record of what has been done. Pick up
  only from rows the register carries; never re-run a row already recorded, and
  never quietly change one.
- Intermediate files stay in the session's Output folder. Nothing is deleted
  and nothing is described as cleaned up; name the files that remain.
- No reduced run ever weakens a lawyer-only ruling, a privilege hold, the
  requirement that a claim carry its quote, or a stop condition.
