# The matter ledger

One file per closing, kept by the lawyer. They attach it at the start of a
session and it comes back to the Output folder updated, with today's date in the
name. It is the only memory this skill has between sessions: nothing written in
one session comes back on its own in the next.

It is a plain table — an Excel workbook through the built-in Excel skill, or a
Markdown table where the lawyer prefers one. Excel is the better default,
because a lawyer can sort it, filter it and count it themselves, which is the
whole point of keeping it visible rather than computing it invisibly.

## Columns

One row per signature block, not per page. A two-party page is two rows, because
a page can be half signed and a status that sits on the page cannot say so.

| Column | What it holds |
|---|---|
| `id` | Short document code plus page, stable and readable: `VA-p9`. Every report, filename and conversation refers to it. Never renumber. |
| `document` | The file the page came out of, as the lawyer names it |
| `page` | The page number in that document |
| `agreement` | The document's own name, as the parties would say it |
| `party` | The legal entity or individual bound — in capitals, as the block prints it |
| `signatory` | The human being who signs, or `Unknown` |
| `capacity` | The role or authority they sign in, including the chain where an entity signs through another |
| `marks_required` | Every required mark in the block: two directors, a director and a secretary, a chop and a representative, a signatory and a witness on a deed. One is the default. |
| `copies_required` | How many originals this party signs of this page. One by default. |
| `witness_required` | Yes where the instrument is a deed or the block prints a witness line |
| `status` | `required`, `sent` or `returned` — and nothing else (see below) |
| `set` | The grouping this row went out in, and the filename it went out as |
| `sent_on` | The date that set went out |
| `returned_on` | The date the lawyer says a page for this row came back |
| `lawyer_note` | What the lawyer said about the returned page, in their words, attributed to them |
| `flag` | Anything `Unknown` in the matrix, or anything the lawyer wants watched |

Add a row for a spare blank page some firms put at the back for a late party:
`party` empty, `status` `required`, and a `flag` saying it is spare and unassigned.
It becomes live when the lawyer assigns a party to it.

## The three statuses, and why there are only three

```
required  →  sent  →  returned
```

- `required` — on the matrix, nothing drafted or sent yet.
- `sent` — the page went out in a set on `sent_on`.
- `returned` — the lawyer has said a page for this row came back, on `returned_on`.

There is no `signed`, no `partial`, no `blank`, no `unclear` and no
`wrong-version`, and their absence is deliberate. Every one of those is a verdict
about a page somebody has looked at, and nothing in this skill looks at a
returned page. `returned` means a page arrived. It says nothing about whether the
block is executed, whether the printed name matches, whether a witness signed, or
whether the page came from the version the parties agreed. Where the lawyer has
looked and told you, their words go in `lawyer_note`, attributed and dated — not
into `status`, which would make their reading look like the skill's finding.

A row never moves backwards, and a row nobody has said anything about stays where
it is.

## The standing line

Recomputed from the rows whenever the ledger is written, printed in the reply,
and shown even when nothing is outstanding:

> 27 rows: 27 required · 27 sent on 12 August · 21 returned · 6 outstanding.
> Counted from the 27 rows in the ledger attached to this session. The returned
> column is what the lawyer has told me came back, not an inspection of any page.

Three rules about that line. It names the method and the scope, so a reader knows
what produced the number. It never borrows the vocabulary of a guarantee, because
nothing here balances against anything the lawyer can check independently beyond
the rows themselves — and the rows are the point: 27 of them with a status column
can be checked in ten seconds. And it never says a closing is done.

Say the row count you read and the row count you wrote every time you hand the
ledger back. If a workbook comes back from a round trip without its rows or its
count, those two numbers are how the lawyer sees it, and they see it in the reply
rather than only in the file.

## Where it lives and what it may contain

The ledger is a work-product file in the lawyer's own matter folder. It carries
party and signatory names because it must. It never goes into a preference file
and never leaves the matter. Nothing written to the Output folder can be deleted
afterwards, so each session's copy is named with its date and the lawyer decides
what to keep.
