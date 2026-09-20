# The artifacts and the master register

Every step below produces one of two things: a row in the master register, or a
named file in the session's Output folder. The register is the one that
travels. It is the state the lawyer carries from session to session, it is the
reconciliation, and its arithmetic is there to be opened and checked. Build it
with the Excel skill and hand it back at the end of every tranche.

Keep the shapes stable. Same columns, same order, same wording of a status,
every time. A file written for the lawyer to read is Markdown or HTML; a file
written for the next session to re-read is the register.

## The master register (Excel)

One sheet per table. Columns in this order, and no others inserted between
them.

**`Documents`** — one row per file taken in.

| Column | What it holds |
| --- | --- |
| `Doc` | Short stable label, assigned in order: `D001`, `D002`. Used everywhere else. |
| `Filename` | The file's name as supplied. |
| `Pages` | Page count for paginated formats; blank otherwise. |
| `Date` | The document's own date, ISO, or blank. |
| `First line` | The first line of text on page one, verbatim. |
| `Readable` | `native`, `scanned`, `encrypted`, `unreadable`. |
| `Role` | `substantive` or `instruction`. Default `substantive`. |
| `Family` | The `Doc` label of the base agreement, or its own label when it stands alone. |
| `Status` | `inventoried`, `read`, `reviewed`, `parked`. |
| `Parked because` | Free text; blank unless `Status` is `parked`. |

`Filename`, `Pages`, `Date` and `First line` together are the document's
fingerprint. Re-read all four at the start of every session and compare them
against the register. A mismatch is reported to the lawyer before anything
else happens, naming the row and both readings. This finds a swapped or
re-exported file; it does not find a change that leaves all four the same, and
the card says so.

A request list, schedule or instruction document is marked `instruction` only
once the lawyer confirms it governs the review rather than being an agreement
to review. Instruction files stay in the document count and in the source
table but never become a sample unit or a row in the issue grid.

**`Findings`** — one row per issue per reviewable unit. This sheet is the
crosswalk and the coverage arithmetic at once.

| Column | What it holds |
| --- | --- |
| `Unit` | The family label where relationships exist, else the `Doc` label. |
| `Issue` | The issue id from the framework, e.g. `coc-01`. |
| `Status` | `present`, `absent`, `unresolved`, `parked`. |
| `Section` | Clause or section reference. Blank unless `present`. |
| `Quote` | The verbatim words the finding rests on. Blank unless `present`. |
| `Where` | Where the quote sits: page and clause. |
| `Characterization` | One factual sentence, within the framework's word cap. |
| `Current` | `yes` when the whole family including later amendments was read and this states the position now in force. |
| `Quote located` | `yes` once the quote has been found again in the source and `Where` recorded. |
| `Second pass` | `confirmed`, `refuted`, `unresolved`, or blank where not yet checked. |
| `Tranche` | Which tranche produced the row. |

**`Counts`** — the reconciliation, as live formulas rather than typed numbers.

| Cell | What it says |
| --- | --- |
| Units | How many reviewable units the `Documents` sheet holds. |
| Issues | How many issues the confirmed framework holds. |
| Expected rows | Units times issues. |
| Filled rows | How many `Findings` rows have a `Status` other than blank. |
| Parked | How many rows are `parked`, and how many documents are parked. |
| Difference | Expected minus filled minus parked. |

Write these as formulas, so the lawyer can see how each number was reached.
Then, in the reply, state the row count read in and the row count written out.
A workbook that comes back with a formula flattened to a number, or with rows
dropped, looks exactly like a workbook that did not; the two stated counts are
what makes that visible. Neither the formula nor the stated counts is a proof
of coverage, and none of this is described as one.

## The gap list

A Markdown list in the Output folder, and a `Gaps` sheet in the register when
the lawyer wants it sortable. One entry per gap, each with a type, a plain
sentence and its evidence:

- `index-missing` — an index row with no matching file. Evidence: the index row.
- `referenced-absent` — a document names an instrument the room does not hold.
  Evidence: the quote that names it.
- `unreadable` — encrypted, scanned beyond reading, or corrupt. Evidence: what
  was attempted and what came back.
- `duplicate` — the same document under two names. Evidence: the two filenames
  and what makes them the same.

Parked means visible. Nothing leaves the count by being dropped.

## The metadata note, per document

One short block per document, written into the Output folder as one Markdown
file for the tranche, and summarised into the `Documents` row. Follow
[the one-document reading contract](shared/metadata-reader-prompt.md) and use
these fields:

- `doc_type` — `agreement`, `amendment`, `sow`, `schedule`, `exhibit`,
  `guaranty`, `other`.
- `title` — the document's own title.
- `parties` — the contracting parties only.
- `dated` — the document's own execution, made-as-of or effective date.
- `references` — the distinct instruments needed to assemble the family, each
  with the exact words that name it, and whether that instrument might be
  missing from the room.
- Every one of those claims carries the exact words it came from. Where the
  page was an image rather than text, say so and give the page number; an
  image transcription is a proposal for the lawyer's eyes, never treated as
  read text.
- `status` — `complete`, `metadata-incomplete`, or `quote-unverified`. A
  parked document stays in the counts.

## Families

One entry per family in the same tranche file, and the `Family` column in the
register:

- `family` — the base agreement's `Doc` label.
- `members` — base first, then by date, then by label, each with its role:
  `base`, `amendment`, `sow-under`, `schedule-of`, `guarantees`, `supersedes`,
  `duplicate-of`.
- `basis` — for each member after the base, the exact words in that document
  that place it in the family, and whether the link was read straight off a
  reference string or decided under
  [the relationship contract](shared/edge-resolver-prompt.md).

A link decided rather than read is shown to the lawyer as proposed, with its
quote, and becomes settled only when the lawyer confirms the family map.

## The framework and the read-back

The framework and its read-back live in
[the checklist compiler contract](framework-schema.md). The read-back is a
table the lawyer reads and confirms, not an internal artifact: one row per
issue, plain English, no field names.

## The pages the lawyer sees

Three HTML files, written to the Output folder and opened in the preview pane:
the review setup, the test results, and the final crosswalk. What they must
contain and how they must read is in
[the review page contract](review-ui.md). They are built by hand from the
register's own rows, so a number on a page and a number in the register are
the same number.
