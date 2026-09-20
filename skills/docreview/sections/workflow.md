## Workflow

### 0. Read the register first

At the start of every session, before anything else: open the master register
the lawyer attached. State how many units are held and list their labels. Then
re-read each document's filename, page count, date and first line of page one
and compare them against the register, reporting any mismatch by row with both
readings. Only then start work.

If no register was attached, say which file was expected, say that without it
the privilege state is unknown, and **produce no findings**. Offer to start a
fresh register from this tranche if the lawyer confirms this is a new matter.

### 1. Inventory the production

Walk the tranche. Record in `Documents` a stable label, the privilege state
(`pending` until anything says otherwise), the filename, the custodian, the
page count, the date, the first line of page one, whether it reads as native
text or as a scan, and the unit it belongs to. Where the production ships an
index or load file, compare it against what is actually there and record every
duplicate, unreadable file and index gap. Encrypted files cannot be read: list
them and park them. A file with a sensitivity label is attempted like any
other, and what came back is reported. Report the counts to the lawyer: files,
readable, scanned, parked, and the gaps so far.

### 2. Map the production and plan the reads

Group messages into threads by their reference chains and normalised subjects,
and note the recurring participant sets as channels, per
[references/comms-schemas.md](references/comms-schemas.md). A thread is a
review unit; a message outside one is a unit on its own. Flattened PDFs and
images stay singletons. Never infer a custodian, date, participant or thread
from a filename. Then decide which documents need a separate identity read and
which are already identified by their headers; propose both plans to the lawyer
and let them choose. A document whose separate read is skipped stays fully in
scope for the review itself.

### 3. Compile and read back the review questions

The lawyer supplies the request sets, pleadings, chronology or issue list. For
served or otherwise enumerated instruments, build the census first: every
served number, series and word of text preserved, gaps left as gaps. Show the
whole census, then compile exactly one framework item per non-staged element.
For prose inputs, compile conservative questions without inventing a legal
position. Include the four privilege signals. Check the framework by reading it
against [references/shared/framework-schema.md](references/shared/framework-schema.md),
then write the read-back. The confirmed framework is the only instruction
channel into any later pass.

### 4. Get a plain-language setup confirmation

Choose up to five representative threads or singletons and build the setup page
per [references/shared/review-ui.md](references/shared/review-ui.md), carrying
the read-back, the collection counts, the gaps, the sample and the held count.
It asks the lawyer four questions: are these the right review questions, does
the collection coverage look right, is this a useful test sample, and may the
proposed separate identity reads be skipped. Say on the page that agreeing
authorises the displayed sample and nothing else — not a full run, and never a
change to a privilege hold. Record what was agreed as a dated line in the
register naming the framework version, the sample units and the metadata
policy. A bare "continue" is not that.

### 5. Run and merge the test sample

Work the sample one unit and one lens at a time under
[references/shared/finding-worker-prompt.md](references/shared/finding-worker-prompt.md),
holding only that unit and that lens. Append a `Findings` row for every request
against every sampled unit — present, absent, unresolved, parked or held, never
blank. A present row carries the verbatim words and where they sit. Retry a
rejected judgment at most twice, then park it with a reason. A unit that is
held, outside the agreed scope, or whose quote could not be located stays
parked rather than becoming a finding.

### 6. Obtain lawyer privilege rulings

Before showing any finding that depends on them, show the lawyer every pending
candidate: the document, which of the four signals fired, and a short plain
reason. Where a quoted passage is what raised the signal, put it in the
conversation with the queue and in no file. Make sure each candidate's source
is actually openable before asking for a ruling.

The lawyer answers **Privileged**, **Not privileged** or **Need more review**
for each. Record the ruling, the date and that the lawyer made it, in the
`Privilege` column, without overwriting the reason or the signals. Only
`not-privileged` releases a unit; pending, `privileged` and `needs-review` stay
held across every lens, and a held document holds its whole thread. Never
decide privilege yourself, and never release a hold on your own reading.

From here on, and in every later session: no text from a held unit is written
anywhere — not into a finding, not onto a page, not into a summary, not into
the register. A held row carries its label, its state and its reason type, and
nothing else.

### 7. Check the findings again

For every present finding, find its quoted words again in the source and record
where they sit; a quote you cannot locate turns the finding to unresolved. Then
make a second pass over every present finding under
[references/shared/finding-checker-prompt.md](references/shared/finding-checker-prompt.md),
working from the finding, its quote and its framework item without revisiting
the reasoning that produced it. A refuted or unresolved verdict turns the
finding to unresolved and keeps the objection. Record it in the register as a
second pass by the same reader; do not call it independent review. Where the
lawyer's feedback changes a framework field, compile a new version and get the
revised plan confirmed before running again.

### 8. Review findings in Requests and Documents

Build the findings page per
[references/shared/review-ui.md](references/shared/review-ui.md) from the
register's rows: a Requests view answering which documents respond to each
request, a Documents view reversing the same rows, responsive items first and
reviewed negatives collapsed. An unresolved legal call is **Needs a decision**,
not unreadable. A file with unresolved calls appears once under **Needs
attention**; a file that could not be read appears as parked with its reason.
Documents outside the agreed scope are never called non-responsive. Held units
appear as held, with no words from them anywhere on the page. The page is
self-contained, loads nothing from outside itself, and is opened in the preview
pane.

The lawyer may rule a finding **Responsive**, **Not responsive**, **Needs
review** or **Privileged**, and may separately say they have looked at every
page of an image-only document. Record each ruling beside its finding without
altering the finding, its quote, its second-pass verdict or its privilege
state. A **Privileged** ruling holds the unit and blanks its words from that
point on. Rebuild the page from the register to show the rulings; that rebuild
reads no document again.

### 9. Scale only after calibration

Agree the scope of the full or targeted run before starting it: which units,
how many, and the boundary of this tranche. The sample must have recovered
every positive that was confirmed against the source, at the same batch size
planned for the run; a schema-shaped answer and a fast pass are not
calibration. Then run the same sequence — findings, privilege, second pass,
page, rulings — over the tranche, appending rows to the register. State the row
count read in and the row count written out, hand the register back, and name
the tranche boundary. The next tranche begins with the lawyer attaching it
again.

### 10. Reconcile and deliver

Reconcile in the register, not in a sentence. The `Counts` sheet holds units,
requests, expected rows, filled rows, parked rows and held rows as live
formulas, and the difference must be zero or explained by rows the lawyer can
see. Every privilege candidate has an explicit ruling, and no held unit
contributes a finding. If it does not come right, fix the run, never the
numbers.

The delivery says: which tranche it covers, what is outside it, how many units
are held and which, what was parked and why, and which checks the original
performed automatically and this run performed by reading. It does not describe
the review as covered, or as carrying any warrant beyond this skill's own
careful reading, and it does not use the vocabulary of formal assurance about
its own arithmetic. The register and the pages stay in the Output folder and
are named in the reply.
