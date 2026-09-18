# The wiki — layout, history, receipts

The wiki is an OKF v0.2 bundle of plain Markdown notes with YAML frontmatter,
readable in any editor, diffable, openable in Obsidian. `note_types.md` says
what a note *means*; this file is the mechanical contract — what exists in the
folder, what each file may contain, what every change records, and what the
receipt says.

Everything here is a visible Markdown file the lawyer can read and edit. There
is no database and no hidden machine state: nothing is executed, so nothing
could maintain one honestly.

## Bundle layout

```
<wiki>/
  index.md                  # Wiki Home: browse topics, notes, sources and review work
  log.md                    # what landed when, newest first, written by hand
  sources/
    index.md                # human-browsable source catalogue
  review/
    index.md                # conflicts, gaps and proposed changes awaiting judgment
  pending/                  # proposed amendments awaiting review, one .md per proposal
  <practice area>/          # one directory per practice area
    index.md
    insights/               # Legal Insight notes
    checklists/             # Checklist notes
    traps/                  # Trap notes
    positions/              # Position notes — excluded from every export
```

- **`index.md`** is the Wiki Home: it declares `okf_version: "0.2"`, routes the
  lawyer to topics, note types, sources, recent changes and review work, and is
  capped at 200 lines (a hard budget: an index nobody can read is not an index).
  Regenerating it **always preserves the root frontmatter** and never lists
  `index.md` or `log.md` as concepts. Pending proposals are excluded from its
  counts.
- **`log.md`** is narration for the lawyer: date-grouped, `## YYYY-MM-DD`
  headings newest first, no frontmatter and no `type`. It is the record of what
  changed, and it is only as good as the discipline of writing to it — append to
  it in the same turn as the change, never afterwards from memory.
- **Path grammar**: each path segment matches `[A-Za-z0-9_][A-Za-z0-9_.\-]*`, and
  the characters `: * ? " < > |` are additionally forbidden so every wiki is
  writable on every platform. No path segment begins with a dot. Body links are
  relative to the note; paths in frontmatter resolve from the bundle root.
- A note edited outside this skill is never dropped: unrecognized frontmatter
  keys are preserved verbatim in source order. A note may be **renormalized**
  (canonical keys, canonical order) the next time it is changed.

## What every change records

There is no hash chain and no automatic history. What stands in its place is
plain and checkable: one entry in `log.md` per change, and the note itself.

Each `log.md` entry is one line under its date heading, naming:

- the operation: created · updated · renamed · merged · withdrawn · accepted
  proposal · declined proposal;
- the note, by its path inside the wiki;
- who asked for it, and in one clause, why.

Four rules keep the record worth having:

1. **Nothing lands without an entry.** A note written without a log line is an
   undocumented change; write both or write neither.
2. **The log is narration, never evidence of verification.** `verified` status
   is set only by an explicit act of the lawyer — accepting a proposal, or
   verifying a note by name — and is recorded in the note's own frontmatter.
3. **History is append-only by convention.** Do not rewrite earlier entries. A
   rename or a merge appends a new entry and leaves the old ones standing.
4. **Say what you cannot know.** A note changed in the editor or by a sync tool
   leaves no entry, so the log can be behind the folder. Where a note's content
   and its last entry disagree, report it as an unreviewed change, never as
   lawyer-verified.

**Withdrawing a note is not deleting it.** Nothing here can delete a file. A
withdrawn note is marked `status: withdrawn` in its frontmatter, taken out of
the indexes, and logged. The file stays in the folder until the lawyer removes
it themselves, and there is no recoverable prior version to restore from unless
their own file store keeps one.

**If matter material reaches the wiki, say so at once and stop.** Mark the note
withdrawn, name the file and every index that references it, and tell the lawyer
plainly that the file and any copies their file store has kept must be deleted
by them. Do not describe the leak as remediated; it is not, until they have done
it.

## Receipts

Every change ends with one short receipt in the reply. A status view prints the
full one:

> notes 47 · sources 31 · review 3 open · disputed 1 · stale 1 · unreviewed changes 2

Do not print a count you did not arrive at by reading. An estimate presented as
a count is worse than no count.

## Where the wiki lives, and what it may contain

Three places, three different rules, and they do not overlap. The **matter
folder** may hold client facts; that is what it is for. The **wiki** holds
gate-certified method and legal knowledge only. The **playbook** holds neither —
it holds preferences.

The wiki therefore lives **outside any matter folder**. It is cross-matter by
nature, its folder is chosen once and named by the lawyer, and it is found only
because they named it — nothing is scanned guessing for one. Nothing here reads
a transcript, logs a prompt or runs on its own.

**What this wiki may contain.** The wiki is a knowledge file, not a matter file.
It contains no party names, no signatory names, no matter numbers, no client
facts, and nothing from which a matter could be reconstructed — not in a note,
not in a filename, not in the log, not in a skip reason. Every candidate passes
the confidentiality gate before it lands, and the gate refuses rather than
guesses. What survives is law and method: what a provision requires, what to
check, what goes wrong, what argument held — statements that would be equally
true if the lawyer had never had that client. Anything that fails is parked in
`review/index.md` with a reason and is not written.

## Finding the wiki

Resolution order is: the folder the user named, then the folder already in use in
this conversation, then ask, suggesting `Documents/Cowork/wiki`. If several valid
wikis remain ambiguous, ask. A named folder that is not there is reported by
name; nothing is created at a stale path and nothing is scanned looking for a
wiki. A moved wiki is just a folder in its new place.

## Two people, one folder

Two people can have the same wiki folder open, and nothing here can stop them or
detect it. There is no lock. Write a note in one pass rather than in pieces, log
it in the same turn, and when a note's content does not match what the log says
about it, treat that as someone else's edit: report it and ask, rather than
overwriting it.

## No automation

Nothing about this wiki runs on its own. Notes are added when the lawyer asks
and retrieved when the lawyer asks, so there is no scope to configure and no
background state to record.
