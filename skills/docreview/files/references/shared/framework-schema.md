# The checklist compiler contract

Compiling turns the lawyer's requests, pleadings, chronology or issue list into
the framework: the single statement of what is being looked for, against which
every pass is judged. This document is the contract, and there is nothing that
enforces it automatically, so check a compiled framework against this document
by reading it.

Three rules govern everything here:

1. **The framework is the only instruction channel.** Carry the confirmed
   framework verbatim into every pass. Nothing else about the review questions
   reaches a pass. If a calibration is not written in the framework, it does
   not exist — and that matters more here than upstream, because one reader
   working through a production is likelier to absorb an instruction out of a
   document than a program was.
2. **Versions are immutable.** Every recompile increments the version and
   writes a new file beside the last one in the Output folder, named for its
   version. The calibration check-in freezes one version; the register records
   which version the run used. Calibration history is the difference between
   versions.
3. **Knobs are fields.** Calibrating means editing named fields, never writing
   a freehand instruction into a pass.

## The framework

```json
{
  "framework_version": 2,
  "confirmed": false,
  "frame": {"kind": "requests", "label": "Defendant's RFP Set One, served 2026-05-01"},
  "source_inputs": [
    {"kind": "rfp", "label": "Defendant's RFP Set One"},
    {"kind": "issues-list", "label": "matter issues, from the pleadings"}
  ],
  "lenses": [
    {
      "lens_id": "rfp-set-one",
      "name": "Requests for production, set one",
      "items": [
        {
          "issue_id": "rfp-set-001",
          "target_ref": "rfp-set-one/1",
          "question": "Documents concerning the meter 6315 outage.",
          "hit_rule": "The document concerns the outage, its cause, or its reporting.",
          "exclusions": ["Routine distribution lists that merely mention the meter"],
          "evidence": {
            "required": "verbatim quote plus location",
            "unresolved_when": "The document refers to an attachment or thread not in the production, or the quote cannot be located"
          },
          "answer_shape": {
            "statuses": ["present", "absent", "unresolved"],
            "characterization_max_words": 30,
            "template": "LOCATION: state the responsive content factually (QUOTE)."
          },
          "disposition": "report",
          "overlap_owner": null
        }
      ]
    }
  ],
  "privilege_signals": ["attorney-domain", "legend", "legal-advice-content", "counsel-name"]
}
```

Field meanings, and which are calibration knobs (K):

- `frame.kind`: `requests` when the items serve enumerated requests, `issues`
  for a prose issue list. The two compile differently; see below.
- `target_ref`: for a requests frame, the served element this item answers.
  Exactly one item per element, and exactly one element per item.
- `question`: the request or issue, in the lawyer's own terms.
- `hit_rule` (K): what counts as responsive. The most load-bearing field.
- `exclusions` (K): what looks responsive and is not. Where the calibration
  check-in's noise complaints land.
- `materiality` (optional K): ranking rules only where the lawyer supplied
  them. Omit the field when the input is silent; never invent a default
  severity.
- `evidence.required`: fixed at quote plus location; not a knob.
- `evidence.unresolved_when` (K): when a pass must stop deciding and leave the
  row unresolved for a person.
- `answer_shape.template` and `characterization_max_words` (K): what the
  finding text looks like.
- `disposition`: `report`, `register` (also feeds the further-enquiries list),
  or `queue` (straight to the unresolved queue for a human).
- `overlap_owner` (K): when two lenses can catch the same document, the lens
  that owns it; the other suppresses the duplicate.
- `privilege_signals`: the four signals that raise a candidate. They are fixed,
  they are never narrowed to fit a schedule, and they are set out in the
  disputes contracts, `comms-schemas.md`, which the skill body names.

## The read-back

The read-back is derived from the framework: it keeps the version and whether
the framework has been confirmed, then carries one row per item with the lens,
the request or issue id, the question, the hit rule, any materiality rule, and
what evidence is required. Where materiality is omitted, the read-back says
`not requested`. It goes on the setup page. The read-back is a deliverable the
lawyer reads and confirms, never an internal artifact; it must stay plain
English, one line per field, no field names and no schema jargon.

## The findings rows

The findings live in the `Findings` sheet of the master register, whose columns
are set out in [the artifacts and the master register](schemas.md). Five rules
about them belong here, beside the framework they are judged against:

- A unit is the confirmed thread where one exists, else the single document.
  `Current` reasoning applies to amended instruments only, not to messages.
- `band` and its basis are filled only when the confirmed framework item
  carries a `materiality` rule; where ranking was not requested, both stay
  blank and no severity is invented.
- Every present finding has its quote found again in the source before it is
  reported, and then goes to a second pass. That second pass covers every
  present finding and is never selected by band, so a request with no ranking
  rule cannot escape it. A refuted or unresolved verdict turns the finding to
  unresolved and keeps the objection; nothing disappears.
- A held unit contributes a row with no words in it, and contributes nothing to
  a deliverable.
- Coverage invariant: for each lens, the rows of every status plus that lens's
  parked units equals the count of reviewable units. The `Counts` sheet is
  where that arithmetic is done and where the lawyer can check it.

## How compiling works

Compiling is a reading step, with these constraints: read the lawyer's raw
inputs in whatever format they arrive, propose lenses and items, and produce
output matching the shape above — checked by reading it against this contract,
with two attempts and then a question to the lawyer rather than a loop. Never
invent a materiality threshold or a default severity: where the lawyer's input
is silent, the item omits `materiality` and the read-back marks it
`not requested`. Vague inputs compile to conservative hit rules plus an
explicit empty exclusions list: over-inclusion is tuned down at the calibration
check-in, silence is never tuned up.

**A prose issue list** may be consolidated where two of the lawyer's points are
plainly one question, as long as the consolidation is shown in the read-back
and they agree to it. Pleadings and chronologies compile this way.

**Served requests may not.** Build the census first, keep every served number,
series and word of the text, and compile exactly one framework item per
non-staged element with no grouping, dropping, duplicating, renumbering or
relabelling. Sets the lawyer chose not to compile stay visible as staged rather
than silently absent. Check the one-to-one mapping by reading it against the
census before the framework is shown. Interpretive notes may be added later
without changing that structural map.
