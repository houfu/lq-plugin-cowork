# Status taxonomy

Every expected closing item carries exactly one status. These are the words the
index, the register, the exceptions list and every sentence to the lawyer use,
and no others.

## Item statuses

| Status | Meaning |
|---|---|
| `ready` | The version selected as final appears complete and, where execution is expected, appears executed and dated on pages that were actually read. |
| `unsigned` | Final form found; execution is expected but the execution evidence is absent, incomplete, unclear, or the pages could not be read. |
| `undated` | Appears signed, but no date is printed where one is expected. |
| `incomplete` | A schedule, annex, exhibit or page appears to be missing from the selected source. The missing component is named, with where the reference to it was seen — a clause, a contents page, a checklist row. |
| `version-conflict` | More than one plausible final version, and what was read does not separate them. The family stops here until the lawyer decides. |
| `missing` | Expected item not among the documents supplied. |
| `unexpected` | A family that matches no row on the confirmed index. Kept and listed; the lawyer decides whether it belongs. |
| `unreadable` | Encrypted, sensitivity-labelled, too large to take in, corrupt, or otherwise unavailable for reading. |
| `not-required` | Confirmed by the lawyer as outside the closing set. |

Who sets what:

- `missing` and `not-required` come from the reconciliation and from the lawyer.
- `unreadable` comes from the stock-take, and may also be proposed for a document
  that opens but cannot be read with confidence.
- `unexpected` is a family, not an index row. A family that matches no expected
  item is listed under unexpected families and counted there. At the gate the
  lawyer either promotes it to an item — which then takes a real status on the
  next pass — or marks it `not-required`, in which case it becomes an item with
  that status.
- `ready`, `unsigned`, `undated`, `incomplete` and `version-conflict` are
  proposed from what was read, under the derivation below, and never asserted
  directly.

## Derivation: from what was seen to one status

Record, per family, what the execution pages showed and what components are
missing, with the evidence for each. The status is derived from those findings,
never the other way round. The first row that applies wins; missing components
are carried on the item whatever the status.

| # | Finding | Status |
|---|---|---|
| 1 | No pick can be separated from the other members | `version-conflict` |
| 2 | The pick cannot be opened or read with confidence | `unreadable` |
| 3 | Execution expected, and the pages read as incomplete, unsigned or unclear, or could not be read at all | `unsigned` |
| 4 | Execution expected, pages appear signed, and no date is printed or the date cannot be made out | `undated` |
| 5 | Any missing component | `incomplete` |
| 6 | Otherwise | `ready` |

Where execution is not expected, the execution finding and the date finding are
both `not-expected`, and that is a valid pair beside any status. Where nothing —
checklist, lawyer or reading — says whether a document is one the parties sign,
execution is presumed expected.

**Findings are about the pick.** Every execution finding and every date finding
names the member selected as final. A finding made on another member, another
family, or on nothing at all is not evidence about this one, and it does not
support a status. `dated` needs a date actually printed on the pick, and a
placeholder such as `[DATE]` or a row of dots is not a date.

**Not inspected.** A family nobody looked at cannot be `ready`: nothing was seen.
It takes `unsigned` where execution is expected and `incomplete` otherwise, with
the qualification "not inspected", and it is named under "Not inspected" in the
exceptions list. A family with several members and nothing read has no pick and
lands `version-conflict`: nothing separates them without a look.

## Rules that do not move

1. **A filename is not evidence.** No item is `ready` because its filename says
   "final", "signed" or "executed". An execution or date finding rests on pages
   that were read and on nothing else; a filename may support an observation
   about version or identity and nothing more.
2. **`version-conflict` is a stop.** No final version is recorded for a family in
   conflict. The lawyer resolves it at the gate or the outcome line is qualified.
3. **File dates are not document dates.** A filename date or a file timestamp is
   never an execution date.
4. **A signature-page ledger is a list of what was expected, not evidence of
   execution.** A ledger from the sigpack skill records what was drafted, what was
   sent and what the lawyer said came back. It can stand as the expected set. It
   cannot make an item `ready`, and it is always cited for what it is.
5. **Never infer authority or delivery from a signature.** The words are "appears
   signed", "appears incomplete", "appears unsigned", "unclear" and "not
   inspected" — never "validly executed".
6. **Nothing is deleted, renamed, moved or overwritten.** Duplicates are grouped,
   never dropped. Everything written goes to the Output folder, beside the
   closing folder and never in it.
7. **The count is a reading, and the wording says so.** The outcome line names
   the method and the scope — *"on the 43 documents supplied, read in this
   session"* — and the register's own count row is what anybody checks it
   against. Nothing here balances against evidence outside what the lawyer
   handed over, and the line is never written as though it did.

## The outcome line

| Outcome | Condition |
|---|---|
| `accounted-for` | Every expected item is `ready` or `not-required`; no unexpected family is undecided; nothing is `unreadable`. |
| `qualified` | Everything is accounted for and nothing is `missing`, but at least one item is not `ready` or `not-required`, or an unexpected family is still undecided. |
| `open` | Any expected item is `missing`, any item or source is `unreadable`, or the expected set is empty. The exceptions list is the work list. |

Printed after every run and shown even when nothing is outstanding:

> 14 expected · 9 ready · 2 unsigned · 1 undated · 0 incomplete · 1
> version-conflict · 1 missing · 0 unreadable · 0 not-required · 2 unexpected ·
> **QUALIFIED** — counted from the 14 rows of the register written this session,
> on the 43 documents supplied.

Every expected item that is not `not-required` is material: there is no separate
materiality flag, and one missing item takes the outcome to `open`. An empty
expected set is not a clean closing; it is nothing to read, and it is `open` too.

`accounted-for` means the reading found nothing outstanding among the documents
supplied. It does not mean the closing is done, and no reply may present it as
though it did. That sentence — the one that says the set is whole — is the
lawyer's to write, and on a closing it always was.
