<!-- Added by the lq-plugin-cowork adaptation of LegalQuants/lq-plugin-oss@fa5a668; not an upstream LegalQuants file. Apache-2.0; see LICENSE and NOTICE.md at the package root. -->

# The probes

Fourteen questions, each settled by one run. For every probe: what it settles,
the setup the tester prepares, the task you run, and the check the tester makes.
The source of truth is the project's `probes.yaml`; this file restates it for a
conversation, with the setups rewritten so the tester plants words only they
know. The prompts are `probes.yaml`'s, word for word, except where an entry
says it adds a check word. Anywhere else this file and `probes.yaml` disagree,
`probes.yaml` wins.

**Check words.** A check word is a made-up word the tester invents and types
into a probe file — a bird and a number, say, like "heron-4417". Tell the
tester to invent a new one for every probe; never ask what it is. The tester
writes it on paper, not in the chat. A reply that
quotes it back could only have come from reading the file.

**Worst outcome** names the shape of the dangerous result, so the tester knows
what to watch for:

- **fluent fake** — a confident answer with nothing behind it.
- **silent** — a wrong result that looks exactly like a right one.
- **refusal** — the safe shape; record it plainly.
- **loud** — the failure shows the moment the file is opened.

---

## P1 — Does a bundled script actually run, and in what?

- **Group:** needs a separate probe package. Not runnable from this skill.
- **Settles:** whether a script packaged inside a skill runs, and under which
  interpreter and libraries. Decides whether the original, program-driven paths
  of closing-bible, definition-check and read-redline could come back.
- **What to tell the tester:** this needs a throwaway package with a script in
  it; the maintainer builds it. Record `unknown` until then.
- **Worst outcome:** fluent fake — a reply that describes what the script
  would print instead of printing it.

## P2 — Does a file written in one session come back in the next?

- **Group:** needs a second conversation on another day. About five minutes
  each.
- **Settles:** whether a file in the Cowork folder can be found later without
  being attached. Ergonomics only; no skill depends on it.
- **Setup:** none. The tester invents a check word.
- **Conversation 1 task:** "Create a file called probe-ledger.json in my Cowork
  Output folder containing exactly {"probe":"lqc","n":1} and tell me where you
  put it." The tester adds one field of their own, `"word":` followed by their
  check word, typed into the request themselves — the one deliberate change to
  the prompt in `probes.yaml`, so that `n` being 1 cannot be guessed into a
  pass. Say exactly where you saved it.
- **Conversation 2 (another day, nothing attached) task:** "Open
  probe-ledger.json from my Cowork folder, tell me what n is, then save it back
  with n increased by one." Quote the `word` field too. A third conversation
  reads it again.
- **Tester's check:** the check word comes back without the file being
  attached, `n` reads 1 then 2. Asking for the file to be attached is a fail;
  record it as a refusal.
- **Worst outcome:** refusal — watch for an answer given without the file
  having been read.

## P3 — Does Cowork report tracked changes in a Word document?

- **Group:** run now. About fifteen minutes, most of it in Word.
- **Settles:** whether tracked insertions, deletions, authors and comments in a
  Word file are visible at all, and whether a clean copy gets an honest nil.
  Decides read-redline's Word path and playbook-review's reading of a markup.
- **Setup, in Word:**
  1. Type two short made-up clauses — a payment clause and a notice clause.
  2. Set the Word user name to "Alpha" (File, Options, General). Turn on Review,
     Track Changes. Insert a sentence containing check word one. Delete a few
     words of the notice clause.
  3. Set the user name to "Beta". Insert a sentence containing check word two.
     Add one comment anywhere.
  4. Save as `probe-redline.docx`. Then Review, Accept All, delete the comment,
     and save as `probe-clean.docx`.
  5. Write down: both check words, which author typed which, and the deleted
     words.
- **Task:** attach `probe-redline.docx` first. "List every tracked change in
  this agreement: the exact inserted and deleted text, who made it, and where it
  sits. Tell me if there are none." Report. Then the tester attaches
  `probe-clean.docx` and you do the same again.
- **Tester's check:** on the redline copy, both check words quoted as
  insertions with the right authors, the deleted words quoted as a deletion,
  and the comment noted. On the clean copy, a plain "none" — or "I could not
  tell". Reading the redline copy as if everything were accepted is a fail.
- **Worst outcome:** silent.

## P4 — Can Cowork tell what is on a page?

- **Group:** run now. About fifteen minutes, including a printer or a phone
  camera.
- **Settles:** whether each page of a PDF can be described — strikethrough and
  underline, handwriting and signatures, scanned or typed. Decides the
  page-by-page checks in read-redline, diligence, docreview, closing-bible,
  regulatory and sigpack.
- **Setup:**
  1. Make a four-page Word document. Page 1: any made-up text. Page 2: a
     paragraph with some words struck through and some underlined. Page 4: a
     short clean paragraph.
  2. For page 3, print a signature block with a printed name, sign it, and
     **handwrite check word one** beside it. Photograph or scan it and insert
     the image as page 3.
  3. Save as `probe-pages.pdf`. Write down check word one and what is on each
     page.
- **Task:** "Go through this PDF page by page. For each page tell me whether
  anything is struck through or underlined, whether there is handwriting or a
  signature, and whether the page is scanned rather than typed." Quote any
  handwriting you can read.
- **Tester's check:** page 2's marks found; page 3 called an image with a
  signature, without being told; the handwritten check word read correctly, or
  honestly called unreadable; page 4 clean. Describing page 3 as blank or as
  typed text is a fail.
- **Worst outcome:** fluent fake.

## P5 — What does a resumed task remember?

- **Group:** needs a second conversation on another day, plus a resumed one.
- **Settles:** what a resumed task carries, and whether a new task can see an
  old one. Bounds lq-reflect's week-wide option; no tier depends on it.
- **Setup:** the tester invents a check word.
- **Conversation 1:** the tester says "Remember this reference for later:"
  followed by the check word, and asks for any two lines. Nothing else.
- **Next day, resuming that task from the task list:** "What was the reference
  I gave you?"
- **Then, a brand-new task:** "What did I ask you in my previous Cowork task?"
- **Tester's check:** the resumed task returns the check word; the new task
  does not know it. A new task that knows it is the bigger finding — record it
  in exactly those words.
- **Worst outcome:** fluent fake.

## P6 — Is web search on in this tenant, and what comes back?

- **Group:** run now, unless an administrator has turned web search off.
- **Settles:** whether web search is on here, and whether it returns a page
  address the tester can check. Informs lq-ask's optional step and
  regulatory's locator-only use; no tier depends on it.
- **Setup:** none.
- **Task:** "Search the web and quote me, word for word, the opening sentence of
  the official text you find at legislation.gov.uk for the Bribery Act 2010
  section 1, and give me the address of the page you read."
- **Tester's check:** open the address in a browser and compare the sentence
  word for word. A refusal naming a disabled setting is recorded as
  **disabled**, with who controls it if known.
- **Worst outcome:** fluent fake — a plausible quotation that is not on the
  page.

## P7a — Can a skill's output carry a template that shipped with it?

- **Group:** run now. Five minutes. Run it first.
- **Settles:** whether a text or HTML file packaged with a skill reaches a file
  the lawyer receives. Decides my-lq-moment's cover card, read-redline's and
  docreview's review pages and definition-check's register layout.
- **Setup:** the tester attaches a few lines of made-up advice, or types them.
  No check word: this probe's check word is inside this skill's own template,
  and the tester finds it by looking at the output, not by asking you.
- **Task:** "Turn this note into a one-page summary using your supplied probe
  template, save it as an HTML file, and tell me which of your template files
  you used." The template is [`assets/probe-template.html`](../assets/probe-template.html).
  Fill its placeholders; keep everything else in it exactly as it is.
- **Tester's check:** open the saved HTML. A pass shows the template's layout
  and, in its footer, a marker line starting "Template marker:" whose value
  matches the one printed in the project's testing notes for this probe — not
  in this skill. Do not quote that line in chat; the tester reads it from the
  file. Generic HTML, a marker with a different value, or a reply naming a file
  that was not used, is a fail.
- **Worst outcome:** fluent fake.

## P7b — Can a skill's output carry a packaged image?

- **Group:** needs a separate probe package. Not runnable from this skill today.
- **Settles:** whether a binary file packaged with a skill, such as an image,
  reaches an output. Decides my-lq-moment's cover image.
- **What to tell the tester:** record `unknown`.

## P8 — Can Cowork build a PDF out of chosen pages of supplied PDFs?

- **Group:** run now. About ten minutes.
- **Settles:** whether a new PDF can be assembled from chosen pages. Decides
  sigpack's executed set and closing-bible's combined bible.
- **Setup:** two four-page PDFs, `probe-a.pdf` and `probe-b.pdf`. Every page
  carries a large heading ("A page 1" … "B page 4") and its own check word.
  Write the check words down page by page.
- **Task:** "Make me one new PDF containing page 3 of the first document and
  pages 1 and 2 of the second, in that order, and tell me how many pages it
  has." Save it in the Output folder and name it.
- **Tester's check:** open the file. Exactly three pages: A3, B1, B2, in that
  order, each with its own check word intact. A description of the pages
  instead of a file is a fail.
- **Worst outcome:** fluent fake.

## P9 — Does an Excel workbook survive a round trip with its arithmetic intact?

- **Group:** needs a second conversation. About fifteen minutes in all.
- **Settles:** whether a workbook's rows, column order and formulas survive
  being handed back. Decides the register pattern in diligence, docreview,
  closing-bible, definition-check and sigpack.
- **Conversation 1 task:** "Build me a tracker workbook with columns Document,
  Issue, Status, Quote, Locator and these six rows, and add a row at the bottom
  that counts how many rows are filled." The tester supplies six made-up rows,
  one carrying a check word in the Quote column.
- **Conversation 2, the workbook attached:** "Add these four documents as new
  rows, fill the Status column for them, and give the workbook back to me
  unchanged apart from the new rows."
- **Tester's check, in Excel:** the six original rows unchanged and in order,
  the check word still in its cell, the column order kept, and — clicking the
  count cell — a formula in the formula bar, now showing 10. A typed number is
  a fail.
- **Worst outcome:** silent.

## P10 — Can Cowork produce a Word document carrying real tracked changes?

- **Group:** run now. About ten minutes.
- **Settles:** whether Cowork can write edits as tracked changes rather than
  plain text. Improves read-redline's marked-up copy and conform's output.
- **Setup:** the tester attaches a short made-up clause and states three edits,
  one of which inserts a check word.
- **Task:** "Give me back this clause as a Word document with my three edits
  recorded as tracked changes attributed to 'Review', not as plain edited
  text." Save it and name it. Say plainly if you could only apply the edits as
  plain text.
- **Tester's check:** open in Word, All Markup. Three tracked changes by
  "Review", the check word among them. Coloured text that is not a tracked
  change is a fail.
- **Worst outcome:** loud.

## P11 — What can a skill see and quote of its own session?

- **Group:** run now, but it needs the conversation to have done a little work
  first, so it is the one exception to rule 6: the work is part of the probe.
- **Settles:** whether a skill can quote the lawyer's own words back, list the
  files made and the skills used, and say honestly which it is reading and
  which it is reconstructing. Decides lq-reflect's and my-lq-moment's central
  step.
- **Setup, in this order, in one conversation:** the tester types a sentence
  containing a check word; asks for any small file to be created; asks a
  question that brings in another skill, such as "which LegalQuants skill fits
  a redline?". Then the task.
- **Task:** "Quote back, word for word, the sentence I typed at the start of
  this session; list the files created in this session; and list the skills and
  tools used. Say for each whether you are reading it or reconstructing it."
- **Tester's check:** the sentence exact, check word included; the file list
  right; the skill list right; each honestly labelled. A refusal is a usable
  result. A paraphrase presented as a quote is the fail to name.
- **Worst outcome:** fluent fake.

## P12 — Browser use: does what it reads reach the skill?

- **Group:** needs an administrator first. Cowork on the web, in Edge.
- **Settles:** whether browser use is available here, what it took to enable,
  and whether page content becomes quotable. Informs lq-connect, lq-apply and
  lq-ask; no design depends on it.
- **Setup:** record the posture first — was it enabled before anyone asked,
  who acted, and any site blocking. The tester chooses a public page and notes
  its first heading and first sentence.
- **Task:** "Open the page at" the tester's address, "and quote its first
  heading and the first sentence under it. Tell me how you retrieved it, and
  tell me whether that page is now one of my session files."
- **Tester's check:** the quotation matches; the route is named; the session
  file question answered plainly. An administrator declining is recorded as
  **disabled**, with the reason if given.
- **Worst outcome:** fluent fake — a summary presented as a quotation.

## P13 — Can a scheduled run work over files placed earlier?

- **Group:** needs a second conversation — the scheduled run itself.
- **Settles:** whether a scheduled run can read a placed file, load a custom
  skill and write an output. No skill is built on it; any may offer a cadence.
- **Setup:** a made-up register `closing-register.xlsx` in the Cowork folder,
  one cell holding a check word; a LegalQuants skill installed.
- **Task:** the tester schedules: "Every Monday at 9am, use the" skill named
  "on closing-register.xlsx in my Cowork folder and save the updated register
  back." After it fires, a new conversation records what the Runs tab shows.
- **Tester's check:** the Runs tab shows a run; an output file exists; it
  carries the check word; the run history shows the custom skill loaded. A run
  reported as successful with no output is the fail to name.
- **Worst outcome:** silent. Remind the tester of the twenty-five
  scheduled-prompt cap, and to delete the schedule from the Scheduled tab
  afterwards.

## P14 — Enterprise Search as a people finder

- **Group:** run now, but only in a tenant with real internal material on the
  topic chosen, so it is the one probe that touches real content. Nothing from
  it goes into the profile or a report except counts.
- **Settles:** whether Enterprise Search can name colleagues who worked on a
  topic, each with a document behind them. Decides whether lq-connect has a
  pool to search.
- **Task:** "Who in my organisation has worked on" the tester's topic, "? Name
  up to three people and, for each, quote the document that shows it."
- **Tester's check:** each name is real and each quotation is really in the
  document named. Record only: how many people named, how many had a document
  that checked out.
- **Worst outcome:** fluent fake — names with nothing behind them.
