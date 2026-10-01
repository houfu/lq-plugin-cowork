# The probes

Generated from `probes.yaml` by `lqcowork catalog`; do not edit by hand.
`<run>` is the run folder and `<skill>` this skill's folder;
`hprobe.py steps <probe> --run <run>` prints the steps with both filled in.

| Probe | Tests | Method | Cost | Question |
|---|---|---|---|---|
| P1 | EXEC BIN | script | free | Does a bundled script actually run, and in what? |
| P2 | PERSIST FS | two-session | two-session | Does a file written in one session come back in the next? |
| P3 | IN DOCX | agent | low | Does Cowork report tracked changes in a Word document? |
| P4 | VISION | agent | low | Can Cowork tell what is on a page? |
| P5 | SESSION | two-session | two-session | What does a resumed task remember? |
| P6 | SEARCH | agent | low | Is web search on in this tenant, and what comes back? |
| P7 | OUT SKILLDIR | agent | free | Can a skill's output carry a file that shipped with the skill? |
| P8 | OUT | agent | low | Can Cowork build a PDF out of chosen pages of supplied PDFs? |
| P9 | IN OUT | agent | low | Does an Excel workbook survive a round trip with its arithmetic intact? |
| P10 | OUT DOCX | agent | low | Can Cowork produce a Word document carrying real tracked changes? |
| P11 | SESSION | user | free | What can a skill see and quote of its own session? |
| P12 | NET | agent | low | Browser use: does what it reads reach the skill? |
| P13 | SCHED | two-session | two-session | Can a scheduled run work over files placed earlier? |
| P14 | SEARCH | user | admin | Enterprise Search as a people finder |
| P15 | MCP TOOLS | agent | setup | Can the harness connect to an MCP server and call one of its tools? |
| P16 | FS | agent | low | Can the agent walk a folder it was pointed at, and make one beside it? |
| P17 | HASH | agent | free | Can the harness compute a file's SHA-256? |
| P18 | NET HASH | agent | low | Can the harness fetch a URL's raw bytes into a file? |
| P19 | SUB | agent | low | Can the harness run an isolated worker that sees only its packet? |
| P20 | HTML | user | low | Can the user open a generated page and hand back the file it saves? |
| P21 | SKILLDIR EXEC | script | free | Is the skill folder on disk, with its scripts and assets reachable? |
| P22 | OUT | agent | low | Can the harness annotate a PDF with highlights and comment-pane notes? |
| P23 | OUT DOCX SKILLDIR | agent | low | Can the harness fill a packaged Word template and edit its table in place? |
| P24 | INVOKE | user | low | Does an explicit-invocation-only skill stay quiet until it is called by name? |
| P25 | TOOLS | agent | free | Does a tool call actually execute? |
| P26 | IN | agent | free | Can the harness read every supplied format, whole? |
| P27 | OUT | agent | free | Can the harness hand a file back to the user? |

## P1: Does a bundled script actually run, and in what?

Tests EXEC, BIN. Method script; cost free; checked by `hprobe.py check P1`.

Whether a script packaged inside a skill is executed at all, and what interpreter and libraries it would run under. Nothing ships with a script under the no-scripts policy, so a result changes no tier; it is the input to the maintainer's decision about that policy and to the original, not re-scoped, paths of closing-bible, definition-check and read-redline.

**Steps.** Run `python3 <skill>/scripts/hprobe.py env --run <run>`. It records the Python version, the importable packages (pypdf, pdfplumber, docx, openpyxl, PIL, fitz, playwright), every executable the vendored skills call (pdftoppm, pdfinfo, pdftotext, soffice, tesseract, chromium, rsvg-convert, magick, inkscape, codex) and whether the script could read a fixture and write to the output folder. Show the printed line verbatim. If the command cannot be run, record P1 as fail with observer agent and say why.

**Worst outcome to watch for:** fluent-fake.

## P2: Does a file written in one session come back in the next?

Tests PERSIST, FS. Method two-session; cost two-session; checked by `hprobe.py check P2`.

Whether state written to the Cowork folder is reachable from a later session without the lawyer attaching it. No tier turns on it, by design: every cross-session design brings its own state instead. It is an ergonomics upgrade for sigpack's ledger, regulatory's refresh baseline, legalquants step 3b, lq-reflect step 8b and lq-apply step 2b.

**Steps.** Session one: run `hprobe.py check P2 --run <run> --phase write`, then use your own file tool to write the printed token into `lq-probe-persist.txt` in the user's workspace root (not the run folder). Tell the user to come back in a new session on a later day. Session two, with nothing attached: find `lq-probe-persist.txt` yourself, then run `hprobe.py check P2 --run <run> --phase read --answer <token you found>`. If the run folder itself is gone, record P2 as fail.

**Worst outcome to watch for:** refusal.

## P3: Does Cowork report tracked changes in a Word document?

Tests IN, DOCX. Method agent; cost low; checked by `hprobe.py check P3`.

Whether Cowork can see tracked insertions, deletions and comments in a Word document at all, and whether it returns an honest nil on a clean copy. Word tracked changes are nowhere mentioned in Microsoft's pages.

**Steps.** Open `<run>/fixtures/docx/tracked.docx` and `clean.docx` with your own tools. For tracked.docx list the inserted text and its author, the deleted text and its author, and the comment text. Then run `hprobe.py check P3 --run <run> --answer "ins=<text>;ins_author=<name>; del=<text>;del_author=<name>;comment=<text>;clean=none"` (clean=none if clean.docx has no tracked changes, otherwise list what you saw).

**Worst outcome to watch for:** silent.

## P4: Can Cowork tell what is on a page?

Tests VISION. Method agent; cost low; checked by `hprobe.py check P4`.

Whether Cowork can say, page by page, what a PDF carries — strikethrough and underline, handwriting and signatures, and whether a page is scanned rather than typed. OCR, scanned PDFs and handwriting are nowhere mentioned.

**Steps.** Look at `<run>/fixtures/vision/page.png` as an image (not via OCR text). It shows a short code in large letters and a scribbled mark in one corner. Run `hprobe.py check P4 --run <run> --answer "code=<code>;corner=<top-left|top-right|bottom-left|bottom-right>"`.

**Worst outcome to watch for:** fluent-fake.

## P5: What does a resumed task remember?

Tests SESSION. Method two-session; cost two-session; checked by `hprobe.py check P5`.

What re-enters the model's context when a task is resumed, and whether a brand-new task can see the previous one. The mechanism of continuation is documented; what it carries is not. No tier turns on it: it bounds lq-reflect's week-wide alternative.

**Steps.** Session one: remember the token printed by `hprobe.py check P5 --run <run> --phase token` and stop. Next day, resume that same task or conversation and ask what the token was; then open a brand-new task and ask the same. Record P5 pass if the resumed task has it and the new one does not, with `hprobe.py record P5 pass --observer user`.

**Worst outcome to watch for:** fluent-fake.

## P6: Is web search on in this tenant, and what comes back?

Tests SEARCH. Method agent; cost low; checked by `hprobe.py check P6`.

Whether web search is enabled here, and whether what comes back is a page address the lawyer can check or a rendering they cannot. It confirms a limit rather than lifting one, and informs lq-ask's optional step and regulatory's locator-only use of search.

**Steps.** Search the web (not from memory) for section 1 of the Bribery Act 2010 on legislation.gov.uk. Run `hprobe.py check P6 --run <run> --url <the address you read> --answer "<the opening sentence, word for word>" --bytes <length of the page you fetched, or 0 if your tool only gave you a rendering>`.

**Worst outcome to watch for:** fluent-fake.

## P7: Can a skill's output carry a file that shipped with the skill?

Tests OUT, SKILLDIR. Method agent; cost free; checked by `hprobe.py check P7`.

Whether a companion file packaged inside a skill reaches something the lawyer receives. Carrying the asset is documented; reaching an output is not. Two arms, one probe: P7a a text or HTML template, P7b a bundled binary image. P7a is free today and should be the first probe the programme runs.

**Steps.** Copy `<skill>/assets/fixtures/badge.png` into `<run>/outputs/` and write `<run>/outputs/card.html` that shows it with an <img> tag. Then run `hprobe.py check P7 --run <run>`. The badge must be the packaged file, byte for byte, not a new image.

**Worst outcome to watch for:** fluent-fake.

## P8: Can Cowork build a PDF out of chosen pages of supplied PDFs?

Tests OUT. Method agent; cost low; checked by `hprobe.py check P8`.

Whether Cowork can assemble a new PDF from chosen pages of supplied ones. Merging or splitting PDFs is nowhere mentioned, and the PDF built-in's entire description is the single line "Work with PDF documents".

**Steps.** Build `<run>/outputs/assembled.pdf` containing page 3 of `<run>/fixtures/pdf/first.pdf` followed by pages 1 and 2 of `<run>/fixtures/pdf/second.pdf`, using your own tools. Then run `hprobe.py check P8 --run <run>`.

**Worst outcome to watch for:** fluent-fake.

## P9: Does an Excel workbook survive a round trip with its arithmetic intact?

Tests IN, OUT. Method agent; cost low; checked by `hprobe.py check P9`.

Whether a workbook's structure and formulas survive being handed back and forth. The round trip itself is documented; whether the arithmetic survives is not. After P3, the probe with the widest reach in the document-pipeline half.

**Steps.** Open `<run>/fixtures/xlsx/tracker.xlsx`. Add the four rows listed in `<run>/fixtures/xlsx/new-rows.txt` below the existing six, keep the count row's formula a live formula, and save the result as `<run>/outputs/tracker-out.xlsx`. Then run `hprobe.py check P9 --run <run>`.

**Worst outcome to watch for:** silent.

## P10: Can Cowork produce a Word document carrying real tracked changes?

Tests OUT, DOCX. Method agent; cost low; checked by `hprobe.py check P10`.

Whether Cowork can write a Word file whose edits are recorded as tracked changes rather than applied as plain text. Producing a Word document with tracked changes or comments is nowhere stated. Neither dependent step is load-bearing; both improve.

**Steps.** Open `<run>/fixtures/docx/clause.docx` and apply the three edits in `<run>/fixtures/docx/edits.txt` as Word tracked changes attributed to "Review", not as plain edits. Save as `<run>/outputs/clause-tracked.docx` and run `hprobe.py check P10 --run <run>`.

**Worst outcome to watch for:** loud.

## P11: What can a skill see and quote of its own session?

Tests SESSION. Method user; cost free; checked by observation.

Whether a skill can quote the lawyer's own words back verbatim, list the files created and list the skills and tools used, and whether it says honestly which of those it is reading and which it is reconstructing. A refusal blocks nothing: it forces every quote to come from an attached file.

**Steps.** Ask the user to type a sentence of their own choosing at the start of the session (before the probes). Near the end, quote it back word for word, list the files created in this session and the tools and skills used, and say for each whether you are reading it or reconstructing it. The user judges and you record with `hprobe.py record P11 <pass|fail| fluent-fake> --observer user`.

**Worst outcome to watch for:** fluent-fake.

## P12: Browser use: does what it reads reach the skill?

Tests NET. Method agent; cost low; checked by `hprobe.py check P12`.

Two things. (a) Availability: is browser use enabled in this tenant, and what did it take to enable it — it needs Edge, runs only in Cowork on the web, and is disabled by default until an admin turns it on. (b) Quotability: does page content or a downloaded file become something the session, and therefore a skill, can quote. No design depends on it.

**Steps.** Fetch https://example.com/ with your own tool (a fetch or browser tool, not search) and run `hprobe.py check P12 --run <run> --answer "<the page's first heading, verbatim>" --bytes <byte length if your tool reports it, else 0>`.

**Worst outcome to watch for:** fluent-fake.

## P13: Can a scheduled run work over files placed earlier?

Tests SCHED. Method two-session; cost two-session; checked by `hprobe.py check P13`.

Whether an automated run can read files the lawyer placed earlier, write outputs, and load a custom skill. The scheduling machinery is documented; what a run can reach is not. No card is built on it; any of them may offer a cadence as a closing line, and must name the twenty-five scheduled-prompt cap when they do.

**Steps.** Run `hprobe.py check P13 --run <run> --phase arm` and note the command it prints. Use the harness's own scheduler to run that command at least ten minutes from now, after this turn has ended. In a later session run `hprobe.py check P13 --run <run> --phase verify`. Record whether it was a scheduled prompt or a process that outlived the turn in --notes.

**Worst outcome to watch for:** silent.

## P14: Enterprise Search as a people finder

Tests SEARCH. Method user; cost admin; checked by observation.

Whether Enterprise Search can answer who in the organisation has worked on a topic, with a quotable document behind each name. Microsoft's whole statement about it is the line "Enterprise Search Search across your organization".

**Steps.** Cowork only: run the Cowork prompt above in a tenant with real internal material and record the outcome with `hprobe.py record P14 <outcome> --observer user`. On any other harness, record P14 as not-run.

**Worst outcome to watch for:** fluent-fake.

## P15: Can the harness connect to an MCP server and call one of its tools?

Tests MCP, TOOLS. Method agent; cost setup; checked by `hprobe.py check P15`.

Whether the harness can reach an MCP server at all - start or connect to it, list its tools and route a call to it - which is how lq-mcp, CourtListener and the C5 integrations of definition-check and conform would arrive. No skill requires MCP, but fifteen use it if present.

**Steps.** Register the bundled server with the harness (see references/mcp-setup.md; for example `claude mcp add hprobe -- python3 <skill>/scripts/mcp_probe_server.py --run <run>`). Run `hprobe.py check P15 --run <run> --phase nonce` for a nonce, call the server's `probe_challenge` tool with it, and run `hprobe.py check P15 --run <run> --answer <digest>`. If only some other MCP server is connected, call one of its read-only tools, quote the result, and record P15 with `hprobe.py record P15 pass --observer user` once the user confirms it.

**Worst outcome to watch for:** fluent-fake.

## P16: Can the agent walk a folder it was pointed at, and make one beside it?

Tests FS. Method agent; cost low; checked by `hprobe.py check P16`.

Whether the harness can list a user-named folder recursively with exact relative paths and an exact count, and create a sibling run folder - the filesystem fifteen upstream skills require for a data room, a production, a closing folder or a matter folder.

**Steps.** With your own file tools (not hprobe.py), list every file under `<run>/fixtures/tree/` by its path relative to that folder, one per line, and save the list as `<run>/outputs/sibling-run/listing.txt`, creating the sibling-run folder. Then run `hprobe.py check P16 --run <run> --count <how many files you found>`.

**Worst outcome to watch for:** fluent-fake.

## P17: Can the harness compute a file's SHA-256?

Tests HASH. Method agent; cost free; checked by `hprobe.py check P17`.

Whether the host can fingerprint a file when no bundled script does it. organize-case-docs requires it for its manifest, and every fallback receipt in the review skills depends on it.

**Steps.** Compute the SHA-256 of `<run>/fixtures/hash/blob.bin` with your own tool (a shell, a code tool, or a hash tool - not hprobe.py), then run `hprobe.py check P17 --run <run> --answer <hex digest>`.

**Worst outcome to watch for:** fluent-fake.

## P18: Can the harness fetch a URL's raw bytes into a file?

Tests NET, HASH. Method agent; cost low; checked by `hprobe.py check P18`.

Whether a fetch returns the bytes a publisher served, saved where they can be hashed, rather than a rendering. regulatory's verified route rests on it; a model's summary of a page is not the page.

**Steps.** Download https://raw.githubusercontent.com/LegalQuants/lq-plugin-oss/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/LICENSE byte for byte to `<run>/outputs/fetched-LICENSE` with your own tool, then run `hprobe.py check P18 --run <run>`.

**Worst outcome to watch for:** fluent-fake.

## P19: Can the harness run an isolated worker that sees only its packet?

Tests SUB. Method agent; cost low; checked by `hprobe.py check P19`.

Whether the harness can hand a sealed packet to a fresh-context worker (a subagent or a separate model call) that cannot see the parent's context, and say which model ran it. Nine upstream skills fan out work this way, and docreview and diligence also need the model chosen per worker.

**Steps.** Run `hprobe.py check P19 --run <run> --phase canary` and keep the printed canary in this conversation only. Start a fresh worker (subagent or separate model call) whose whole input is the contents of `<run>/fixtures/sub/packet.txt`. Save the worker's reply verbatim to `<run>/outputs/worker-reply.txt`, then run `hprobe.py check P19 --run <run> --model "<model the worker ran on>"`.

**Worst outcome to watch for:** fluent-fake.

## P20: Can the user open a generated page and hand back the file it saves?

Tests HTML. Method user; cost low; checked by `hprobe.py check P20`.

Whether the interactive HTML round trip works: the user opens an offline page the skill generated, makes choices, the page saves them as a JSON download, and that file comes back to the skill. legaldesign, docreview and diligence require it.

**Steps.** Give the user `<run>/outputs/roundtrip.html` (written by init). Ask them to open it in a browser, tick Alpha and Gamma, press Download decisions and hand the downloaded `hprobe-decisions.json` back to you; put it at `<run>/inputs/hprobe-decisions.json`, then run `hprobe.py check P20 --run <run>`.

**Worst outcome to watch for:** loud.

## P21: Is the skill folder on disk, with its scripts and assets reachable?

Tests SKILLDIR, EXEC. Method script; cost free; checked by `hprobe.py check P21`.

Whether a skill's own folder exists on a real filesystem, so a bundled script can import its sibling modules and read ../assets by relative path - which every scripted upstream skill, and the cross-skill calls of the companion set and conform, assume.

**Steps.** Run `python3 <skill>/scripts/hprobe.py check P21 --run <run>`. It imports its sibling module, reads `<skill>/assets/fixtures/marker.bin` by relative path and lists any sibling skill folders it can see.

**Worst outcome to watch for:** fluent-fake.

## P22: Can the harness annotate a PDF with highlights and comment-pane notes?

Tests OUT. Method agent; cost low; checked by `hprobe.py check P22`.

Whether a PDF can be returned carrying real annotations - a highlight and a note in the comments pane - rather than a description of them. read-redline's annotated copy depends on it.

**Steps.** Add a highlight annotation and a comment (text) annotation whose contents are the token in `<run>/fixtures/pdf/annotate-token.txt` to `<run>/fixtures/pdf/plain.pdf`, with your own tools, and save it as `<run>/outputs/annotated.pdf`. Then run `hprobe.py check P22 --run <run>`.

**Worst outcome to watch for:** loud.

## P23: Can the harness fill a packaged Word template and edit its table in place?

Tests OUT, DOCX, SKILLDIR. Method agent; cost low; checked by `hprobe.py check P23`.

Whether a .docx shipped inside a skill can be copied, have one table cell changed in place and come back with its formatting intact - what document-discovery's response shell and closing-checklist's table edit need.

**Steps.** Copy `<skill>/assets/fixtures/template.docx` to `<run>/outputs/template-filled.docx`, change the second data row's Status cell to the token in `<run>/fixtures/docx/status-token.txt` without touching anything else, and run `hprobe.py check P23 --run <run>`.

**Worst outcome to watch for:** silent.

## P24: Does an explicit-invocation-only skill stay quiet until it is called by name?

Tests INVOKE. Method user; cost low; checked by `hprobe.py check P24`.

Whether the harness honours `disable-model-invocation` (or `allow_implicit_invocation: false`): the skill must not fire on a matching prompt, but must fire when the user calls it by name. Nine upstream skills are explicit-only and are unreachable without this.

**Steps.** Ask the user to install `harness-probe-invoke` beside this skill. Ask them to send "Check whether the invoke probe is wired up." and note whether that skill fired; then ask them to call it by name (for example `/harness-probe-invoke`). Run `hprobe.py check P24 --run <run> --answer <token it returned> --implicit <fired|quiet>`.

**Worst outcome to watch for:** silent.

## P25: Does a tool call actually execute?

Tests TOOLS. Method agent; cost free; checked by `hprobe.py check P25`.

Whether the harness runs the model's tool calls and returns real results, rather than letting a call be narrated. Nineteen upstream skills need tool execution and nine more fall back without it.

**Steps.** Read `<run>/fixtures/tools/token.txt` with a file-reading tool and run `hprobe.py check P25 --run <run> --answer "<exact contents>"`. If you have no tools, say so and record P25 as fail.

**Worst outcome to watch for:** fluent-fake.

## P26: Can the harness read every supplied format, whole?

Tests IN. Method agent; cost free; checked by `hprobe.py check P26`.

Whether a PDF, a Word file, a workbook, an email and a long text file can each be read in full, so a code on the last page is found. IN is required by sixteen upstream skills, and pressuretest and cite-check read documents whole.

**Steps.** Read every file in `<run>/fixtures/in/` (report.pdf, memo.docx, sheet.xlsx, message.eml, long.txt) in full and run `hprobe.py check P26 --run <run> --answer "pdf=<code>;docx=<code>;xlsx=<code>;eml=<code>;txt=<code>"`. On a harness without file tools, ask the user to attach the static copies in `in/` inside `<skill>/assets/fixtures/static.zip` instead.

**Worst outcome to watch for:** fluent-fake.

## P27: Can the harness hand a file back to the user?

Tests OUT. Method agent; cost free; checked by `hprobe.py check P27`.

Whether the skill can produce a file the user receives and can open - the most basic output every document skill relies on.

**Steps.** Write the token in `<run>/fixtures/out/token.txt` as the only line of `<run>/outputs/hello-probe.txt` with your own file tool, tell the user where it is, and run `hprobe.py check P27 --run <run>`. If your harness returns files by download rather than a shared folder, ask the user to confirm they received it.

**Worst outcome to watch for:** loud.
