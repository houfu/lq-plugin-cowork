# The artifacts and the master register

Every step produces one of two things: a row in the master register, or a named
file in the session's Output folder. The register is the one that travels. It
is the state the lawyer carries from session to session, it holds the privilege
state, it is the reconciliation, and its arithmetic is there to be opened and
checked. Build it with the Excel skill and hand it back at the end of every
tranche.

Keep the shapes stable. Same columns, same order, same wording of a status,
every time. A file written for the lawyer to read is Markdown or HTML; the file
written for the next session to re-read is the register.

## The master register (Excel)

**`Documents`** — one row per file taken in. `Privilege` is the first column
after the label, and it is read before anything else happens in a session.

| Column | What it holds |
| --- | --- |
| `Doc` | Short stable label, assigned in order: `D001`, `D002`. |
| `Privilege` | `pending`, `candidate`, `privileged`, `needs-review`, `not-privileged`, or `not-flagged`. |
| `Filename` | The file's name as produced. |
| `Custodian` | The first folder segment of the produced path, or blank. |
| `Pages` | Page count for paginated formats; blank otherwise. |
| `Date` | The document's own date, ISO, or blank. |
| `First line` | The first line of text on page one, verbatim — **unless the row is held**, in which case this column stays blank. |
| `Readable` | `native`, `scanned`, `encrypted`, `unreadable`. |
| `Unit` | The thread or family label this document belongs to, or its own label. |
| `Status` | `inventoried`, `read`, `reviewed`, `parked`, `held`. |
| `Parked because` | Free text; blank unless `Status` is `parked`. |

`Filename`, `Pages`, `Date` and `First line` together are the document's
fingerprint. Re-read all four at the start of every session and compare them
against the register, reporting any mismatch, naming the row and both readings,
before anything else. For a held document the first line is not recorded at
all, so its fingerprint is the other three: that is the price of the rule that
no text from a held document is written anywhere, and it is the right price.

**`Findings`** — one row per request or issue per reviewable unit.

| Column | What it holds |
| --- | --- |
| `Privilege` | The unit's privilege state, copied from `Documents`. First column, again. |
| `Unit` | The thread or singleton label. |
| `Request` | The request or issue id, e.g. `rfp-set-001`. |
| `Status` | `present`, `absent`, `unresolved`, `parked`, `held`. |
| `Section` | Where in the document the passage sits. |
| `Quote` | The verbatim words the finding rests on — **blank whenever the unit is held**, without exception. |
| `Where` | Page and location. |
| `Characterization` | One factual sentence within the framework's word cap. |
| `Quote located` | `yes` once the quote has been found again in the source. |
| `Second pass` | `confirmed`, `refuted`, `unresolved`, or blank. |
| `Lawyer ruling` | `responsive`, `not-responsive`, `needs-review`, `privileged`, or blank. |
| `Tranche` | Which tranche produced the row. |

A held row exists — the unit is visibly accounted for — and carries no words
from the document. Nothing is written into a held row that a reader could use
to reconstruct what the document says.

**`Counts`** — the reconciliation, as live formulas rather than typed numbers:
units, requests, expected rows, filled rows, parked rows, held rows, and the
difference. Write them as formulas so the lawyer can see how each number was
reached, and state in the reply the row count read in and the row count written
out. A workbook that came back with a formula flattened to a number, or with
rows dropped, looks exactly like one that did not; the two stated counts are
what makes that visible. None of this is a warrant that the production was
covered, and it is never described as one.

## The production inventory

Text, spreadsheet and message formats each give up their words differently, and
what is read should be said rather than assumed:

- A word-processing file gives its body text. Tracked changes, comments and
  embedded objects are not interpreted; say so where a document plainly has
  them.
- A spreadsheet gives one non-empty cell per line, sheet by sheet in the order
  they appear, with the cell reference as the location anchor. Formulas are not
  evaluated; what is read is the stored value.
- An email gives its From, To, Cc, Date and Subject followed by the plain text
  body, or the visible text where there is no plain part. Attachments are
  separate documents with their own rows.
- A flattened PDF or an image is a single unit. Its filename is never evidence
  of a participant, a date or a thread.

## Gaps

A Markdown list in the Output folder, and a `Gaps` sheet in the register when
the lawyer wants it sortable. One entry per gap with a type, a plain sentence
and its evidence: `index-missing`, `referenced-absent`, `unreadable`,
`duplicate`, `custodian-gap` and `thread-gap`. The message and thread
types are defined in the disputes contracts, `comms-schemas.md`, which the
skill body names. Parked means visible; nothing leaves the count by being
dropped.

## The read of each document

One short block per document, in one Markdown file for the tranche, summarised
into the `Documents` row. Follow
[the one-document reading contract](metadata-reader-prompt.md): type, title,
parties, date, the instruments it refers to, each carrying the exact words it
came from, and a status of `complete`, `metadata-incomplete` or
`quote-unverified`. Where the identity of a document is already settled by its
message headers and no step needs a separate read, say so and skip it rather
than reading it twice; a document whose read was skipped is still fully in
scope for the review itself, and its row says which it was.

A held document is read only far enough to decide it is held. After that it
contributes a row, a privilege state and nothing else.

## The framework and the read-back

The framework and its read-back are in
[the checklist compiler contract](framework-schema.md). The read-back is a
table the lawyer reads and confirms: one row per request or issue, plain
English, no field names.

## The pages the lawyer sees

Two HTML files in the Output folder, opened in the preview pane: the review
setup page and the Requests and Documents findings page. What they must contain
is in [the review page contract](review-ui.md). Both are built by hand from the
register's own rows, so a number on a page and a number in the register are the
same number.
