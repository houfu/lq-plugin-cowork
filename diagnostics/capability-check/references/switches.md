<!-- Added by the lq-plugin-cowork adaptation of LegalQuants/lq-plugin-oss@fa5a668; not an upstream LegalQuants file. Apache-2.0; see LICENSE and NOTICE.md at the package root. -->

# What each result switches

For each probe: which skills a result changes, what they do today, and what a
**pass** would let them do instead. This skill switches nothing itself. A switch
takes effect only when a package is built from the profile and installed, or
when the maintainer changes the shipped skill for everyone.

Three kinds of result appear below, and it matters which one you are reading
out:

- **Switch** — the skill has a cautious path and a fuller one, and a pass lets a
  build choose the fuller one.
- **Already adapts** — the skill already tries the fuller thing and tells the
  lawyer which one they got. A pass means the fallback stops appearing; nothing
  needs switching.
- **Confirms** — a pass changes no behaviour. It records that a limit or a
  guard is right for this tenant.

Some guards stay whatever the result, because they cost little and they catch
the day the capability quietly stops working. Each entry names them.

---

## P1 — scripts run

- **Kind:** switch, but also a policy decision. The project ships no scripts at
  all today; a pass is evidence for the maintainer, not a switch a build can
  flip on its own.
- **Would reopen:** the original, program-driven paths of closing-bible (the
  full closing bible rather than the index), definition-check (the parser path)
  and read-redline (the parser and page renderer). Even then, a script would be
  an optional accelerator; the reading path stays and stays authoritative.
- **Cannot help:** my-lq-moment and sigpack, which need programs other than a
  script interpreter.

## P2 — a file written earlier can be found later

- **Kind:** switch, for ergonomics only. No skill depends on it.
- **sigpack:** the signing ledger could be found in the Cowork folder instead
  of being attached every time.
- **regulatory:** a refresh could find the earlier note and its provision list
  itself.
- **legalquants, lq-reflect, lq-apply:** the last note or evidence file could be
  read back without being attached. lq-apply becomes a running record rather
  than a one-off draft.
- **diligence, wiki:** the register or the wiki folder could be found by name.
- **Stays:** docreview's hard stop. With no privilege register in front of it,
  it gives no findings, whatever P2 says.

## P3 — tracked changes in a Word file can be read

- **Kind:** switch.
- **read-redline:** loses its "could not tell" banner and its probe-gated
  status on the Word path.
- **playbook-review, conform:** could read a counterparty's markup as markup
  rather than as accepted text. Neither skill has this path written yet.
- **Stays:** read-redline may still not report "no tracked changes" unless it
  can quote one insertion and one deletion with their authors.

## P4 — each page of a PDF can be described, scans included

- **Kind:** switch.
- **diligence, docreview:** scanned documents could be reviewed rather than
  parked as unreadable.
- **closing-bible:** a scanned execution page could be inspected rather than
  recorded as not inspected and carried as not ready.
- **regulatory:** a scanned official PDF could be read rather than refused.
- **read-redline:** the PDF path's page-by-page check becomes a real check.
- **sigpack:** the first of the results a fuller signing-and-compiling version
  would need, alongside P8 and one of P2 or P9. That would be a different skill,
  not a switch.
- **Stays:** every skill still names any page it could not read.

## P5 — a resumed task remembers

- **Kind:** confirms. No skill depends on it.
- **lq-reflect:** a review could run inside a resumed task and so cover days of
  one thread's work. It never covers other tasks.

## P6 — web search is on and returns a checkable address

- **Kind:** confirms, with one optional step.
- **cite-check:** already adapts — it says plainly when it could not search.
- **regulatory:** search may help find the publisher's page; it is never quoted
  as the source.
- **lq-ask:** could offer, once and only if asked, a search labelled as a search
  rendering. Not written yet.

## P7a — a packaged template reaches the output

- **Kind:** confirms.
- **legaldesign, cite-check, read-redline, docreview, definition-check:** their
  HTML pages already rest on this. A fail is the serious result here: those
  pages would need a plain-page path.

## P7b — a packaged image reaches the output

- **Kind:** already adapts.
- **my-lq-moment:** keeps its designed cover instead of falling back to a plain
  card.

## P8 — a PDF can be built from chosen pages

- **Kind:** switch.
- **closing-bible:** could offer the combined closing bible as one PDF again.
  Bookmarks and volumes stay unestablished.
- **sigpack:** nothing on its own; see P4.

## P9 — a workbook keeps its rows and live formulas

- **Kind:** confirms.
- **diligence, docreview, closing-bible, definition-check, sigpack:** their
  count rows can be trusted as live formulas.
- **Stays:** every register still prints the number of rows it read and the
  number it wrote.

## P10 — Cowork can write real tracked changes

- **Kind:** already adapts.
- **read-redline, conform:** the marked-up Word copy comes back as tracked
  changes rather than old text beside new.
- **playbook-review:** could offer a tracked-changes copy on request. Not
  written yet; today the skill declines to.

## P11 — a skill can quote its own session

- **Kind:** switch.
- **lq-reflect:** may quote the lawyer's words from the conversation verbatim,
  rather than only from attached files.
- **my-lq-moment:** may count the skills and tools used as evidence, so fewer
  sessions are turned away for too little evidence.
- **Stays:** anything reconstructed is still labelled as reconstructed.

## P12 — browser use is enabled and quotable

- **Kind:** confirms. No skill depends on it, and a pass does not license any
  skill to browse: that is a policy question as well as a capability one.

## P13 — a scheduled run works over placed files

- **Kind:** switch, small.
- **diligence, docreview:** could offer the next tranche as a scheduled run.
- **regulatory, legalquants, lq-reflect:** could offer a check-in on a cadence.
- **Stays:** the twenty-five scheduled-prompt cap is named whenever a schedule
  is offered.

## P14 — Enterprise Search finds people

- **Kind:** switch, load-bearing.
- **lq-connect:** a pass is what its organisation-search half rests on. A fail
  means it should announce up front that it cannot find people here, and work
  only from a list the lawyer brings.
