# The disputes contracts

The inventory, reading plan, document records and gap list are set out in
[the artifacts and the master register](shared/schemas.md). This file defines
the two things that belong to a litigation production: how messages are grouped
into review units, and how privilege is held.

## Messages

One record per unique message, written into the tranche's Markdown file and
summarised into the register:

- `path` — the produced path, and from it the custodian, which is the first
  path segment and nothing else.
- `from`, `to`, `cc` — always lists, even when there is one name or none.
- `date` — normalised to UTC, with the sender's own offset kept beside it,
  because a collection gap is counted in the sender's months.
- `subject`, `message id`, `in reply to`, `references` — as the headers give
  them.
- `has attachments` — an attachment is its own document with its own row.
- `duplicate paths` — where the same message was produced more than once.

Never infer a custodian, a date, a participant or a thread relationship from a
filename.

## Threads and channels

- A **thread** is a set of messages joined by their reference chains and a
  normalised subject. A thread is the review unit. A message with no thread
  around it is a unit on its own.
- A **channel** is a normalised set of participants that recurs at least three
  times. Channels are context for the lawyer, not review units.
- Record, per custodian, how many messages fall in each month. A month with no
  messages sitting between two months that have them is a gap worth naming.

A flattened PDF or an image stays a single unit.

## Gaps this layer adds

- `custodian-gap` — an empty custodian month between populated neighbours, or
  a custodian named in the index with nothing produced.
- `thread-gap` — a cited message id that is not in the production, or a missing
  archive copy. Record it too when the production holds documents but no
  readable messages at all, so the limit is visible rather than implied.

## Privilege: the queue and the hold

This is the part of the skill that carries the most weight, and the part where
the adaptation is furthest from the original. Upstream, the hold lived in a
file a program refused to release. Here it is a rule this skill applies to
itself, with the production in front of it. Four things make that rule as
strong as it can be made, and all four are mandatory.

**1. Privilege is the first column.** In `Documents` and in `Findings`, the
privilege state comes first, so it cannot be scrolled past. Read it at the
start of every session, before any other work.

**2. The held count is stated before anything is produced.** The first reply of
every session says how many units are held and lists their labels. Not at the
end, not in a footnote: first, and in the open.

**3. No text from a held unit is written anywhere.** Not into a finding, not
into a page, not into a summary, and not into the register itself — a held row
carries its label, its state and its reason type, and its quote and first-line
columns stay blank. The state file cannot leak what the deliverable must not
say.

**4. No register, no findings.** If the lawyer has not attached the register,
this skill does not know what is held, and it therefore produces no findings at
all. It says so, names the file, and stops. This is the one place where a
missing attachment is a hard stop rather than a reduced scope, and it is a hard
stop precisely because the state carries a legal hold rather than a record of
progress.

### Raising a candidate

Never decide privilege. Any of four signals raises a candidate: an
`attorney-domain` address, a `legend` on the face of the document, content that
is `legal-advice-content`, or a `counsel-name`. A candidate records the
document label, which signals fired, and a short reason in the skill's own
words. Where a quote is what raised the signal, it goes to the lawyer in the
conversation with the queue, and it is not written into any file.

### The queue, and the ruling

Show the lawyer every pending candidate before showing any finding that depends
on it, as a plain-language list: the document, why it was raised, and how to
open it. The lawyer answers **Privileged**, **Not privileged** or **Need more
review** for each one.

Only `not-privileged` releases a unit. Pending, `privileged` and `needs-review`
all stay held, across every request and every lens. A held document holds its
whole thread or family. Write the ruling into the `Privilege` column with the
date and that the lawyer made it; the reason and signals that were already
there are not overwritten. Nothing in this skill releases a hold by itself, and
a re-run never quietly changes a ruling.

Reconciliation, the findings page and any export stop rather than proceed if a
finding turns out to touch a held unit.

## The setup approval

One page, before any review, asking the lawyer four questions in plain words:

1. Are these the right review questions?
2. Does the collection coverage look right?
3. Is this a useful test sample?
4. Where a separate identity read of the non-message documents was proposed as
   unnecessary, may it be skipped?

The page authorises the displayed test sample and nothing else. It does not
authorise a full run, it does not change a privilege hold, and reading it is
not approval. Record the answer as a dated line in the register naming exactly
what was agreed: the framework version, the units in the sample, and the
metadata policy. A bare "continue" is not that.

## Request sets and issue lists

Where the lawyer supplies served requests — requests for production, requests
for admission, interrogatories — build the census first, before any
interpretation:

- Keep the served number, the series where there is one, and the text of each
  element exactly as served.
- A plain designator is a positive integer. A compound designator such as `D-1`
  is stored as number 1 with series `D`. Plain `1` and `D-1` are different
  requests.
- Numbering gaps stay gaps. A duplicate or an unclassifiable designator is
  refused rather than guessed.
- Count the elements and the instruments, including any set the lawyer chose
  not to compile into this run; those stay visible as staged.

Then compile one framework item per non-staged element, one to one, with no
grouping, dropping, renumbering or relabelling, each item pointing at the
element it serves. Check that mapping by reading it against the census: every
element represented exactly once. Interpretive consolidation is only ever
available for a prose issue list, never for served requests.

## The findings page

One HTML page in the Output folder, opened in the preview pane, built from the
register's rows, following [the review page contract](shared/review-ui.md):

- **Requests** is the default view: one row per served request, its full text,
  responsive documents first, reviewed negatives collapsed. A request with
  nothing responsive is visible without being overstated beyond the scope the
  lawyer agreed.
- **Documents** reverses the same rows and shows each produced file once.
- A file with one or more unresolved calls appears once under **Needs
  attention**, not once per request. Unresolved does not mean unreadable; say
  which it is.
- A page read as an image is labelled **Needs your eyes**, and the lawyer is
  asked to look at every page and at the proposed matches and non-matches
  before saying they have reviewed it.
- Held units are shown as held — the label, the state, nothing else. No quote,
  no characterization, no extract.
- Statuses read **Responsive**, **Nothing found** and **Needs a decision**.
  Documents outside the scope the lawyer agreed are never called
  non-responsive.

The page carries the privilege state as a document property and never releases
a hold.

## What the lawyer rules, and what that changes

The lawyer may rule a finding **Responsive**, **Not responsive**, **Needs
review** or **Privileged**, and may separately say they have looked at every
page of an image-only document. Those rulings go into the `Lawyer ruling`
column beside the finding; they never overwrite the finding, its quote, its
second-pass verdict or its privilege state, which stay as they were. A
**Privileged** ruling blanks the quote in the register and on the page from
that point on, and the unit is held from then on.

Rebuild the page from the register to show the rulings. That rebuild is a
re-render of rows already decided and needs no fresh reading of any document.
