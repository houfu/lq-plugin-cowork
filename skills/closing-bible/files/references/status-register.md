# The status register

The register is a workbook the lawyer keeps, built through the built-in Excel
skill. It does the job a computed balance used to do, and it does it differently:
the arithmetic is on the face of it, so a lawyer can sort it, filter it and add
it up themselves in ten seconds. A sentence claiming everything is accounted for
cannot be checked at all; forty-three rows with a status column can.

## Columns

One row per expected item, in the order of the confirmed index.

| Column | What it holds |
|---|---|
| `item` | The index number. Never renumbered once the index is confirmed. |
| `title` | The document as the lawyer would name it |
| `parties` | The parties, where they are known |
| `checklist_ref` | The row of the lawyer's checklist this item answers, or blank where the index was drafted from the documents |
| `execution_expected` | Yes, no, or unknown |
| `status` | One of the nine, from `references/status-taxonomy.md` |
| `qualification` | One line, for anything not `ready`: what is wrong and what would resolve it |
| `selected_source` | The filename of the version selected as final, or blank where none could be |
| `why_this_one` | The evidence that separated it from the other members of its family |
| `execution_finding` | `appears-signed`, `appears-incomplete`, `appears-unsigned`, `unclear`, `not-inspected` or `not-expected` |
| `document_date` | The date printed on the execution page, verbatim, or blank |
| `missing_components` | Each schedule, annex, exhibit or page referred to and not attached, and where the reference was seen |
| `family_files` | Every file grouped into this item, so a duplicate is visible rather than absorbed |
| `read_in_session` | The date of the run that produced this row |

Below the last row, separated by one blank row:

| Row | What it holds |
|---|---|
| Count | A live count of the rows above, and a count per status, each written as a formula over the rows rather than as a number typed in |
| Documents supplied | How many documents the lawyer attached for this run |
| Outcome | `accounted-for`, `qualified` or `open`, with the method and scope line beside it |

## The two numbers, every time

Say both in the reply, in words, whenever the register is written:

> Read 43 rows from the register you attached; wrote 47.

That is the whole mitigation for a workbook that comes back from a round trip
having quietly lost a row or turned a count formula into a typed number. It is
not a guarantee. It is a pair of numbers a lawyer can compare against the file in
front of them, and a difference they did not ask for is something they see in the
reply rather than find in a month.

If no register was attached, say that too, before anything else, and say that
this run starts from the documents alone.

## What the register may not say

It may not describe itself as a balance anybody struck, and it may not use the
vocabulary of a guarantee about its own counting. Its count row is arithmetic the
lawyer can redo; its status column is a reading. Say which is which. The outcome
line always carries the method and the scope — *"counted from the 43 rows written
this session, on the 43 documents supplied"* — and never stands alone as a claim
about the closing.
