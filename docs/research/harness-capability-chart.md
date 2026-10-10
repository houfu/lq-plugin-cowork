# Harness capability chart for the vendored skills

1 October 2026

This chart answers one question: **what does a harness need, beyond a chat-completion loop that can use
skills, to run each vendored upstream skill?** It covers all thirty-one skills in `upstream/skills/` at the
pinned SHA `fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0`, not the Cowork adaptations in `skills/`. The
adaptations exist precisely because Cowork lacks some of what is listed here; their own levels are in
[The Cowork cards](#the-cowork-cards).

**The data is `capabilities.yaml`.** Every level below lives in that file at the repository root, with
each degradable level's fallback wording and the probes that decide it. The matrices, counts and ladders
in this document are generated from it by `lqcowork chart` (between `<!-- gen:... -->` markers), and the
build fails when they drift. The [harness-probe skill](../../harness-probe/SKILL.md) judges a real
harness against the same data.

A standalone write-up of this research, for sharing outside the repository, is
[harness-capability-research.md](harness-capability-research.md) (regenerate it with
`tools/scripts/research_doc.py`).

## Baseline assumed

The harness already has these, so they are not listed per skill:

- **Multi-turn chat with the user.** This includes every approval gate, "stop and wait" checkpoint and
  three-question intake the skills use.
- **Agent Skills support.** The harness discovers skills by description, loads `SKILL.md` and loads the
  skill's own text files (`references/*.md`, schemas, prompts) into context on demand.

Everything else is a capability the harness must add. That includes executing tool calls (TOOLS) and
connecting to MCP servers (MCP). The baseline returns text only.

## Capability codes

| Code | Capability the harness must add |
|---|---|
| **TOOLS** | Tool execution. The harness gives the model callable tools, runs each call and returns the result within the turn. Every capability that acts rather than reads goes through a tool call: OUT, FS, PERSIST, EXEC, BIN, NET, SEARCH, VISION, DOCX, SUB, SESSION, SCHED, MCP, and the auxiliary HASH and SKILLDIR. A skill's TOOLS level is therefore the strongest of its levels in those codes. |
| **MCP** | Connecting to an MCP server: local stdio or remote HTTP, with authorisation, tool and resource discovery, and routing of calls. Equivalent connector mechanisms count too: OpenAPI tools, Cowork `agentConnectors` and claude.ai connectors. Presupposes TOOLS. The service a skill connects to is named in [MCP connection](#mcp-connection). |
| **IN** | Read files the user supplies: pdf, docx, xlsx, eml, txt/md, csv, images. Needs no TOOLS when the harness places attachments in context. |
| **OUT** | Write and hand back files: html, docx, pdf, json, csv, md, png/svg. |
| **FS** | A real filesystem. This covers user-named paths, recursive folder walks, a run or work directory, sibling output folders, and the skill directory itself present on disk. |
| **PERSIST** | Storage that outlives the session. Examples are `~/.lq/`, `~/.wiki/`, a ledger or registry in a matter folder, and earlier run folders. |
| **EXEC** | Run the bundled Python scripts. These are stdlib-only unless the detail table says otherwise. |
| **BIN** | External executables: Poppler, LibreOffice, tesseract, headless Chromium, an SVG rasteriser, or the `codex` CLI. |
| **NET** | Fetch a public URL and read it. A skill that hashes what it fetches (regulatory) also needs the **raw bytes**, which probe P18 tests; a model's summary of a page never counts. |
| **SEARCH** | A web search engine. |
| **VISION** | The model looks at rendered page images, such as signature pages, redline marks or layout QA. |
| **DOCX** | Read or write Word OOXML structure (tracked changes, comments, table XML), not just the text. |
| **SUB** | Isolated worker contexts: parallel subagents, or a fresh-context reviewer call. |
| **SESSION** | Read conversation transcripts: the current session's events and tool calls, or past sessions. |
| **SCHED** | Background, detached or hook-driven runs that outlive the turn. |
| **HTML** | The user opens a generated offline HTML page in a browser. For docreview and document-discovery, the user's decisions come back as a downloaded JSON file. |

Three **auxiliary codes** are rated like the rest but drawn in their own table, not as matrix columns:

| Code | Capability |
|---|---|
| **HASH** | The host computes a file's SHA-256 because no bundled script does it for the skill. Where a script the skill runs does the hashing, EXEC covers it instead. |
| **SKILLDIR** | The skill's folder exists on a real filesystem, so its scripts, assets and sibling skills are reachable by path. |
| **INVOKE** | The skill is explicit-invocation only (`disable-model-invocation: true` or `allow_implicit_invocation: false`), so the harness must let the user call it by name. |

A **facet** narrows a code to the one thing a particular probe tests: `OUT:pdf-assemble` is "build a PDF
from chosen pages" (P8), `DOCX:tracked-write` is "write Word tracked changes" (P10). A matrix cell shows
the strongest level among a code and its facets; the facet tables list them.

A reliable clock is left out: every skill that needs a date accepts one from the user, or gets it from a
script.

**Levels.** Each level comes from the skill's own text.

| Symbol | Level | Meaning |
|---|---|---|
| ● | Required | The skill cannot produce its core deliverable, or it stops. |
| ◐ | Degradable | The skill documents a fallback and says what is lost, typically "provisional", "not script-verified", "unvalidated preview", or a check reported as not run. |
| ○ | Optional | An enhancement only. |
| blank | Not used | |

## Matrix

The vendored upstream skills (profile `upstream` in `capabilities.yaml`).

<!-- gen:matrix-upstream -->
| Skill | TOOLS | MCP | IN | OUT | FS | PERSIST | EXEC | BIN | NET | SEARCH | VISION | DOCX | SUB | SESSION | SCHED | HTML |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **core** | | | | | | | | | | | | | | | | |
| legaldesign | ● | ○ | ● | ● | ● | ○ | ◐ | ○ | ○ |  | ◐ |  |  |  |  | ● |
| lq-start | ● |  |  |  | ● |  | ● |  |  |  |  |  |  |  |  |  |
| regulatory | ◐ | ○ | ◐ | ○ | ◐ | ○ | ◐ |  | ◐ | ◐ |  |  | ○ |  |  |  |
| timenarratives | ◐ | ○ | ○ | ◐ | ○ | ○ | ◐ |  |  |  |  | ○ |  | ◐ |  |  |
| wiki | ● |  | ● | ○ | ● | ● | ◐ |  | ○ |  |  |  | ◐ | ○ | ○ | ◐ |
| **companion** | | | | | | | | | | | | | | | | |
| legalquants | ◐ |  |  |  | ◐ | ◐ | ◐ |  |  |  |  |  |  |  |  |  |
| lq-apply | ● |  | ○ | ● | ○ | ◐ | ◐ |  | ◐ |  |  |  |  |  |  |  |
| lq-ask | ◐ | ◐ | ○ |  |  |  | ◐ |  | ◐ |  |  |  |  |  |  |  |
| lq-connect | ● |  |  |  |  |  | ◐ |  | ● |  |  |  |  |  |  |  |
| lq-mirror | ○ |  |  | ○ |  | ○ | ○ |  |  |  |  |  |  |  |  |  |
| lq-reflect | ● |  | ● | ○ | ● | ● | ● |  |  |  |  |  | ◐ | ● |  |  |
| my-lq-moment | ● |  | ◐ | ● | ◐ | ○ | ● | ◐ |  |  |  |  |  | ● |  |  |
| **litigation** | | | | | | | | | | | | | | | | |
| cite-check | ● | ○ | ● | ● | ● | ○ | ◐ | ○ | ○ | ◐ |  |  | ◐ |  |  | ○ |
| client-update | ◐ | ○ | ◐ | ○ |  | ○ | ○ |  | ○ | ○ |  |  | ◐ |  |  |  |
| correspondence | ○ | ○ | ◐ | ○ |  | ○ |  |  | ○ | ○ |  |  |  |  |  |  |
| depositions | ○ | ○ | ◐ | ○ |  | ○ |  |  | ○ | ○ |  |  |  |  |  |  |
| docreview | ● |  | ● | ● | ● | ○ | ◐ | ○ |  |  | ◐ |  | ◐ |  | ○ | ● |
| document-discovery | ● | ○ | ● | ● | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ |  |  |  | ◐ |
| new-matter | ◐ | ○ | ○ | ◐ | ◐ | ○ |  |  |  |  |  |  |  |  |  |  |
| organize-case-docs | ● | ○ | ● | ◐ | ● | ● | ◐ | ○ |  |  | ○ |  |  |  |  |  |
| pressuretest | ◐ |  | ● | ◐ | ◐ |  | ◐ |  |  |  |  |  | ○ |  |  | ◐ |
| writing | ◐ | ○ | ○ | ○ |  | ○ |  |  | ◐ | ◐ |  |  |  |  |  |  |
| **transactional** | | | | | | | | | | | | | | | | |
| closing-bible | ● |  | ● | ● | ● | ○ | ● | ◐ |  |  | ◐ |  | ○ |  |  |  |
| closing-checklist | ● | ○ | ● | ● | ● | ○ | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ |  |  |  |
| conform | ● | ○ | ● | ● | ● |  | ● |  | ○ |  |  |  | ◐ |  |  | ◐ |
| definition-check | ◐ | ○ | ◐ | ◐ | ◐ | ○ | ◐ | ○ |  |  |  | ◐ | ◐ |  |  | ◐ |
| diligence | ● |  | ● | ● | ● | ○ | ◐ | ○ |  |  | ◐ |  | ◐ |  | ○ | ● |
| playbook-builder | ● |  | ● | ● | ● | ● | ◐ |  |  |  | ◐ | ◐ |  |  |  |  |
| playbook-review | ● |  | ● | ● | ● | ◐ | ◐ |  |  |  | ◐ | ◐ | ◐ |  |  |  |
| read-redline | ● |  | ● | ● | ● | ○ | ◐ | ◐ |  |  | ◐ | ● |  |  |  |  |
| sigpack | ● |  | ● | ● | ● | ● | ◐ | ◐ |  |  | ● | ○ | ◐ |  |  |  |
<!-- /gen:matrix-upstream -->

<!-- gen:counts-upstream -->
7 skills have no ● at all and run on the baseline alone, in their documented degraded form where they have ◐ items: client-update, correspondence, definition-check, depositions, new-matter, regulatory, writing. TOOLS is ● for 19 skills, ◐ for 9 and ○ for 3.
<!-- /gen:counts-upstream -->

Auxiliary codes:

<!-- gen:aux-upstream -->
| Skill | HASH | SKILLDIR | INVOKE |
|---|---|---|---|
| cite-check |  | ◐ |  |
| client-update | ○ |  |  |
| closing-bible |  | ● |  |
| closing-checklist |  | ○ |  |
| conform |  | ● |  |
| definition-check |  | ◐ |  |
| depositions | ○ |  |  |
| diligence |  | ◐ |  |
| docreview |  | ◐ |  |
| document-discovery |  | ◐ |  |
| legaldesign |  | ◐, ◐ asset |  |
| legalquants |  | ◐ | ● |
| lq-apply |  | ◐ | ● |
| lq-ask |  | ◐ | ● |
| lq-connect |  | ◐ | ● |
| lq-mirror |  | ○ | ● |
| lq-reflect |  | ● |  |
| lq-start |  | ● | ● |
| my-lq-moment |  | ●, ● asset | ● |
| organize-case-docs | ● |  |  |
| playbook-builder |  | ◐ |  |
| playbook-review |  | ◐ |  |
| pressuretest |  | ◐ | ● |
| read-redline |  | ◐ |  |
| regulatory |  | ◐ |  |
| sigpack |  | ◐ |  |
| timenarratives |  | ◐ | ● |
| wiki |  | ◐ |  |
<!-- /gen:aux-upstream -->

Facets, with the probes that decide them:

<!-- gen:facets-upstream -->
| Skill | Facet | Level | Probes |
|---|---|---|---|
| closing-bible | `OUT:pdf-assemble` | ◐ | P8 |
| closing-checklist | `DOCX:table-edit` | ◐ | P23 |
| document-discovery | `OUT:docx-template` | ● | P23 |
| read-redline | `OUT:pdf-annotate` | ◐ | P22 |
| sigpack | `OUT:pdf-assemble` | ● | P8 |
<!-- /gen:facets-upstream -->

### Changes since the first audit

A second audit of every skill (which also rated the Cowork cards) disputed some cells. These were
accepted, because in each the skill's own text documents a fallback or a deliverable the first pass
missed:

- **regulatory:** NET and FS drop from ● to ◐. Without a verified fetch or file retention the answer is
  labelled "provisional and unverified" (`SKILL.md:593`, `:612`), which is the definition of ◐. With no
  ● left, regulatory now runs on the baseline in its provisional form.
- **definition-check:** FS and IN drop to ◐. Its C0 and C1 profiles review pasted or host-extracted text
  with no runtime (`references/capability-routing.md:13`). HTML is ◐ (the report falls back to the
  conversation).
- **playbook-review:** PERSIST drops to ◐; a playbook can be supplied by path instead of the registry
  (`SKILL.md:29`).
- **HTML:** cite-check ○ (a static report), and pressuretest and conform ◐ (offline report with a chat
  fallback).
- **INVOKE:** nine skills are explicit-invocation only, not six. lq-apply, my-lq-moment and pressuretest
  set `allow_implicit_invocation: false` in `agents/openai.yaml`.

## Per skill: what is hard, what it runs on, what degrades

"Py" is the minimum Python version the scripts need. "stdlib" means no third-party imports.

### core

| Skill | Hard requirements (●) | Runtime the scripts need | What degrades without the ◐ items |
|---|---|---|---|
| legaldesign | Read the work product; write one self-contained `.html` file plus `artifact.spec.json`; the user opens it in a browser (it uses `localStorage` and `showSaveFilePicker`). | `scaffold.py`: Py ≥3.10, stdlib. `exhibit.py` (optional source clips): Py ≥3.11, **PyMuPDF**, **Playwright with Chromium**. | Without scripts the model must hand-build the runtime and validation, and must not claim checks it did not run. Without vision, multi-viewport visual QA is reported as not done. |
| lq-start | Run `catalog.py`, which walks the host's plugin install folders and reads `$CODEX_HOME/config.toml`. Its output is the only list a skill may be named from. | Py 3, stdlib. | Nothing degrades. Without exec it cannot name installed skills. |
| regulatory | None: its verified route needs the publisher's **raw bytes** saved and hashed (NET ◐, P18), and without them it answers in its labelled provisional form. A rendering from a web-fetch tool is rejected. | 8 scripts, Py 3, stdlib (`urllib`). Some publishers need a correct TLS trust store and a browser User-Agent. | Without a fetch, the answer is labelled "provisional and unverified". Search is only for locating an instrument, never as a source. A PDF source needs a text extraction step. Refresh needs a prior run folder. |
| timenarratives | None. | 40 scripts, Py ≥3.11, stdlib. Publishing needs an atomic no-replace rename (`renameat2`, `renamex_np` or Windows `os.rename`). | Without exec the output is an "Unvalidated preview" and no files are published. Related chats need a host conversation reader, otherwise coverage is labelled partial. Explicit invocation only. |
| wiki | A persistent wiki directory plus the `~/.wiki/wikis.json` registry; reading sources in full. | `wiki.py`: Py ≥3.11, stdlib. | Without exec it falls back to a Markdown workflow: no deterministic gate, no hash-chained history, no tamper check. The layer-3 gate needs a **fresh-context reviewer** (SUB). Automatic retrieval needs Codex lifecycle hooks, which are off by default. Browse wants an inline rich renderer and falls back to Markdown. |

### companion

| Skill | Hard requirements (●) | Runtime the scripts need | What degrades without the ◐ items |
|---|---|---|---|
| legalquants | None. | Calls the sibling scripts `onboarding.py`, `profile_store.py` and `catalog.py`. Py ≥3.11, stdlib. | Without exec and `~/.lq/`, it asks the user where they are instead of reading their journey state. Explicit invocation only. |
| lq-apply | Write the draft (and its evidence notes) to a local file. | Sibling scripts only. | Without `~/.lq/` it builds the draft from a short interview. Without a fetch of assess.legalquants.com, the draft is marked provisional. |
| lq-ask | None. | `source_access.py` plus the sibling `evidence.py` (stdlib `urllib`). | Without the **lq-mcp** connector or a fetch, it answers from the static list in `sources.md` and says the live corpus is unreachable. Explicit invocation only. |
| lq-connect | Read legalquants.com/community and member profile pages. | Sibling `evidence.py` (GitHub API, raw.githubusercontent). | The bounded evidence excerpts are dropped. The skill still hands over profile links. Explicit invocation only. |
| lq-mirror | None. | None of its own. | Nothing: the core is twelve chat questions. Explicit invocation only. |
| lq-reflect | Read **past session transcripts** (`~/.codex/sessions`, `~/.claude/projects` JSONL); write `~/.lq/`; hash-bound consent manifests. | 4 scripts, Py ≥3.11, stdlib. | Live mode works chat-only. The retrospective mode cannot run without transcripts. Without workers, the second-read critique is skipped. |
| my-lq-moment | **Current-session evidence**: conversation, tool and skill events, and the workspace files produced. Render and write the cover image. | `render_cover.py`: Py ≥3.11, stdlib. Needs any one SVG→PNG rasteriser: `rsvg-convert`, ImageMagick, Inkscape, `qlmanage` or headless Chromium. | With no checkable evidence it returns an honest "not earned". With no rasteriser it delivers an SVG only. It may ask for elevated (unsandboxed) execution. |

### litigation

| Skill | Hard requirements (●) | Runtime the scripts need | What degrades without the ◐ items |
|---|---|---|---|
| cite-check | Read the brief and the authorities; a run directory; write an HTML report built from the bundled template. | 10 scripts, Py 3, stdlib. The packaged fan-out shells out to **`codex exec`**. | Workers run sequentially (up to 6 in parallel by default). Without search, a case that was not supplied gets `not_supplied_search_unavailable`. A CourtListener MCP is optional. |
| client-update | None. | None. | Parallel workers are optional; otherwise it reads pasted sources. |
| correspondence | None. | None. | Without file reading the inbound email is pasted. |
| depositions | None. | None. | Without file reading the transcripts are pasted. An authorised realtime transcript feed is optional. |
| docreview | A production folder plus a run directory; JSON and HTML outputs; the lawyer opens the `file://` HTML gates and returns the downloaded JSON receipts. Privilege rulings have **no chat substitute**. | 48 scripts, Py ≥3.11, stdlib. **Poppler** and **LibreOffice** are optional. The `codex exec` worker adapter is optional. | Without exec the run cannot be labelled "coverage-certified" or "script-verified". Without vision, scans are parked as "Needs rendering". It requires a fixed higher-capability model at medium effort or above for workers. A detached runner is optional. |
| document-discovery | Read the RFPs and the example responses; write a DOCX shell from a **bundled binary .docx template**. | 4 scripts, Py 3, stdlib. They read `../assets` from the skill directory. | Without fetch or search, outputs are labelled "authority check incomplete". If the HTML review page is not used, decisions are made in chat. Rendering pages in a word processor for QA is optional. |
| new-matter | None. | None. | Without a filesystem, the matter record is returned in chat marked "unsaved". |
| organize-case-docs | Read and walk the matter folder; keep a workspace that is updated across turns. A **SHA-256 manifest** is required, and no script is bundled, so the harness needs some way to hash files. | None bundled. | Without file writes it only proposes a layout. OCR is optional. |
| pressuretest | Read the selected documents whole. | 3 entry scripts, Py ≥3.12, stdlib. | Without exec the reading is delivered in chat, the checks are reported as not run, and date calculations are left unresolved. Deep mode is optional and needs workers. |
| writing | None. | None. | Without fetch or search, source gaps are disclosed. |

### transactional

| Skill | Hard requirements (●) | Runtime the scripts need | What degrades without the ◐ items |
|---|---|---|---|
| closing-bible | Walk the closing folder; write to a sibling folder; run the script. There is **no by-hand fallback** for the index, receipt or exceptions list. | 7 scripts, Py ≥3.12, stdlib. **pypdf** for the combined PDF (optional). **Poppler** and **LibreOffice** are optional or degradable. | Without vision, execution pages are recorded as `not-inspected` and the receipt is capped at `qualified`. Without LibreOffice, Word files stay native and are not in the combined PDF. |
| closing-checklist | Read the anchor agreement; write an editable `.docx`. | 2 scripts, Py 3, stdlib OOXML. | Without exec, a host Word editor must do the editing. Without vision, the page-render QA is reported as outstanding. With no `.docx` output at all, only an interim chat table is possible. |
| conform | Two `.docx` files plus two **definition-check ledgers**, hash-checked by the script. It **hard-stops** without exec. | 10 files, Py ≥3.12, stdlib. Calls `definition-check/scripts/normalize_terms.py`. | Without workers, it runs sequentially and does not claim independent review. Note that no command renders `conform.html`. |
| definition-check | None: with no runtime it falls to profile C1 (reduced-assurance review of host-extracted text) or C0 (pasted text). Its full route needs the `.docx`, output and work directories (OS temp). | ~50 files, Py ≥3.12, stdlib. Uses `fcntl`/`msvcrt` locks and hard links on the adapter path. The `codex exec` worker adapter is optional. | Without exec, it is a reduced-assurance review of host-extracted text (C1) that never says "no issues". Without workers, it runs sequentially. Without file output, the report is given in chat. |
| diligence | Walk the data room; a run directory; write HTML, JSON and CSV; the user opens the HTML pages. | 47 scripts, Py ≥3.11, stdlib. **Poppler** and **LibreOffice** are optional. The `codex exec` adapter is optional. | Without exec it is not "coverage-certified". Without vision, scans go to "Needs rendering". It requires a higher-capability model for mapping and a sample recall gate. A detached runner is optional. |
| playbook-builder | Read 1–5 sources (docx/md/txt/pdf, or xlsx/csv for an import); write a sealed package plus `playbook-registry.json` that persists for playbook-review. | 3 files, Py 3, stdlib. **pdfplumber** and **pypdf** are optional for PDF text. | Without exec, hashing and receipts are done by host means, or the receipt is not claimed. Without vision, scanned PDF pages stay `pending-vision`. |
| playbook-review | Read the contract package; write the Word issues matrices. The playbook comes from `playbook-registry.json` found by walking up from the working directory, or by explicit path. | Same runtime as builder. The DOCX is written by hand-built OOXML. | Without exec, a receipt is unavailable. Without vision, scanned pages are left pending. Without workers, it runs sequentially. |
| read-redline | Read tracked changes (`w:ins`, `w:del`, moves, `rPrChange`, comments), or the colour marks in a compare PDF; write an annotated copy and an Issues List `.docx`. | 7 scripts, Py ≥3.11. **pdfplumber** and **pypdf** for the PDF path. **python-docx** for the issues list. Poppler `pdftoppm` is run by the agent. | Without vision or render, the visual reconciliation is reported as not run. If the harness cannot annotate a PDF, only the issues list is delivered. |
| sigpack | A closing folder with a ledger that persists across sessions; **visual review of every candidate and returned page**. With no way to render, it refuses to compile. | `sigpack.py`, Py 3. **pypdf** is required. **Pillow** is needed for triage contact sheets. **pdfplumber** is optional. **Poppler** `pdftoppm` does the rendering. | Without LibreOffice, it asks for PDFs instead of converting docx, and draft mode is lost. Without tesseract, there is no OCR. Without workers, page reading is sequential. |

## Capabilities that come bundled with others

These requirements do not show as their own column but a harness builder will hit them:

- **The skill directory must exist on a real filesystem, with its siblings installed.** Scripts import
  sibling modules and read `../assets` and `../schemas`. Several skills call another skill's scripts by
  relative path:
  - every companion skill calls `../legalquants/scripts/onboarding.py`;
  - companion skills write the store through `../lq-reflect/scripts/profile_store.py`;
  - legalquants, lq-reflect and lq-mirror call `../lq-start/scripts/catalog.py`;
  - conform calls `../definition-check/scripts/normalize_terms.py`.

  Loading `SKILL.md` as text is not enough.
- **Hard skill-to-skill data dependencies:**
  - conform needs definition-check ledgers (schema `0.14.0`);
  - playbook-review needs a playbook-builder registry;
  - closing-bible optionally consumes the sigpack ledger;
  - legaldesign optionally consumes cite-check output;
  - organize-case-docs hands off to docreview.
- **Explicit invocation.** Nine skills set `disable-model-invocation: true` or
  `allow_implicit_invocation: false`, so the harness must let the user call a skill by name. They are
  the INVOKE entries in the auxiliary table: legalquants, lq-apply, lq-ask, lq-connect, lq-mirror,
  my-lq-moment, lq-start, timenarratives and pressuretest.
- **Per-worker model and effort control.** docreview and diligence require one fixed, higher-capability model
  at medium effort or above for finding workers. The cite-check, docreview, diligence and definition-check
  `codex` runners pin a worker model. A harness whose SUB support cannot choose a model per worker fails
  these contracts.
- **Provider-specific assumptions to replace or shim:**
  - `catalog.py` reads `.claude-plugin`/`.codex-plugin` layouts and `$CODEX_HOME`;
  - lq-reflect parses Codex and Claude Code JSONL transcript formats;
  - the worker runners shell out to `codex exec`;
  - wiki automation expects Codex lifecycle hooks.

  A different harness needs its own equivalents or falls back.
- **Python version.** The floor across the set is **3.12**: definition-check, conform and closing-bible
  gate on it, pressuretest declares it, and most of the rest need 3.11 for `datetime.UTC`.

## TOOLS and MCP in more detail

### Tool execution

TOOLS is the capability almost everything else depends on. Plain chat completion only returns text. A
skill that writes a file, walks a folder, runs a script, fetches a page, renders a page, starts a worker
or reads a past chat does each of these through a tool call that the harness executes. That is why the
TOOLS column is derived from the other columns, not audited separately. The generated counts under each
matrix give how many skills need it at each level.

The skills do not care whether a tool is built into the harness or attached over MCP. Most of them
describe a **tool cascade**: the bundled scripts first, then host-native tools, then a licensed service
that the user or firm selects (`upstream/AGENTS.md`, "Tool cascade"). Examples:

- diligence and docreview, `references/shared/execution-modes.md:75`;
- read-redline, `SKILL.md:124`;
- sigpack, `SKILL.md:135`;
- playbook-builder, `SKILL.md:282-287`;
- regulatory, `SKILL.md:612-617`.

What the skills do care about is how a tool behaves. Three conditions apply to every tool, however it is
connected:

1. **The tool must actually perform the operation.** The rule is "do not claim SHA-256 identity …
   automated count reconciliation unless a host-native tool actually performed it"
   (`execution-modes.md:96-98`).
   - A tool that summarises a page or describes a file does not satisfy NET, hashing or DOCX.
   - regulatory rejects a web-fetch tool's rendering as "a model's summary of the text, not the text"
     (`SKILL.md:46-49`).
2. **Client material stays inside a boundary that is already authorised.** Remote processing is allowed
   only where the "connector, network, DMS, or hosted-service data boundary is already authorized", and it
   is recorded (`capability-routing.md:9`). Several skills make this concrete:
   - cite-check sends only citation metadata to a public service (`getting-authorities.md:77`);
   - client-update never uploads matter material "merely to format or summarize it" (`SKILL.md:56`);
   - closing-checklist does not upload matter documents to a new service (`SKILL.md:30`);
   - wiki Position notes "never leave the machine".

   In practice, for the matter skills, any tool that touches the documents must run locally or inside the
   firm's own approved system.
3. **The bundled scripts can only see a filesystem.** They take paths, import sibling modules, read
   `../assets`, and call other skills' scripts by relative path.
   - A code-execution tool satisfies EXEC only if the skill folders and the user's workspace are both
     inside its filesystem.
   - A remote sandbox that holds neither does nothing for the script path.
   - Uploading matter files into a remote sandbox falls under condition 2.

### MCP connection

MCP means the harness can connect to an MCP server: start or reach it (local stdio or remote HTTP), handle
its authorisation, list its tools and resources, and route the model's calls to it. Other connector
mechanisms count in the same way: OpenAPI tools, Cowork `agentConnectors` and claude.ai connectors. MCP
presupposes TOOLS.

The MCP column marks the skills that ask for a server by name or by kind:

- **No skill needs MCP (●).**
- **lq-ask is the only ◐.** It falls back to a static source list when lq-mcp is absent.
- **The rest are ○.** They use a connection only if one is present and authorised.

| Skill | What the connection is for | Level | Rule |
|---|---|---|---|
| lq-ask | **lq-mcp**, guest scope | ◐ | A connector being present "does not prove member access". The member tier (LQ Brain) needs an authorised capability response and is not shipped (`SKILL.md:44-59`). |
| cite-check | **CourtListener MCP** | ○ | Used only when the host exposes it and the user authorises it. Only citation metadata is sent (`getting-authorities.md:75-77`). |
| definition-check, conform | "network/connectors/MCP/DMS", as profile C5 | ○ | Only inside an already-authorised boundary, and remote processing is recorded. The example given is retrieving a source ledger from a DMS (`references/capability-routing.md`). |
| regulatory, closing-checklist, new-matter, organize-case-docs, depositions, client-update, writing, correspondence, document-discovery, timenarratives, legaldesign | Unnamed, firm-selected systems: DMS, matter management, docket, e-billing, e-discovery or transcript platforms, licensed legal research or retrieval | ○ | Only when the user or firm selects one, and never assumed. new-matter never reports a system as queried unless it actually returned a result (`SKILL.md:100`). |
| my-lq-moment, correspondence, sigpack, playbook-review, diligence | Publishing, email, calendar, docketing, e-signature | **Forbidden** | These skills never send, post, file, docket or run an e-signature process, even when the connection exists. A harness should not expose such tools to them. |

MCP can also carry the tools behind other capabilities. In that case, the three conditions above apply to
each server. The table below says what a tool must do to count for each capability, whether it is built
in or comes from a server.

| Code | Example tools, built in or over MCP | Counts when | Does not count |
|---|---|---|---|
| IN | Attachment into context; a filesystem tool; a DMS connector | The whole document arrives. For the script path, the file must also land where the scripts can read it. IN alone needs no TOOLS when the harness places attachments in context. | A connector that returns snippets or summaries. A remote DMS used for documents outside its authorised boundary. |
| OUT | Filesystem write; DMS write; a file-return or artifact tool | The user gets a file they can open. docx and pdf output also need a tool that produces that format (see DOCX and BIN). | — |
| FS | Filesystem tools with list, recursive walk, read, write and make-directory | Paths stay stable across calls, and EXEC (if used) sees the same tree. | Tools that address items by ID with no paths. They serve the model-read fallback, not the scripts. |
| PERSIST | The same filesystem tools on durable storage | The files the skills expect survive between sessions: `~/.lq/`, `~/.wiki/wikis.json`, `sigpack.ledger.json`, `playbook-registry.json`, earlier run folders. | A generic memory or key-value store. No skill reads one, and the bundled scripts are the only writers of these stores. |
| EXEC | A code-execution tool, local or sandboxed | It runs Python ≥3.12 with both the skill folders and the workspace mounted. | A sandbox without the skill folders. A remote sandbox that matter files must be uploaded into. |
| BIN | The EXEC sandbox with the binaries installed; render and convert tools (LibreOffice, PDF rendering) | The agent itself calls the binary, as read-redline and sigpack do with `pdftoppm`. | Binaries that scripts launch via `subprocess` (closing-bible, docreview, diligence, sigpack). These must be inside the EXEC sandbox. |
| NET | A fetch tool | For regulatory, it saves the **raw response bytes** to the workspace so they can be hashed. For lq-connect and the live parts of lq-ask, a readable page is enough. | For regulatory, a fetch tool that converts HTML to Markdown. |
| SEARCH | A search tool (Brave, Bing, Tavily and similar) | Queries carry citation metadata only, never client text (cite-check). | — |
| VISION | A render tool that returns page images as image content, plus a multimodal model | Every page asked for is rendered and actually looked at. sigpack refuses to compile otherwise. | OCR text standing in for the image: sigpack decides `signed` from the render alone. No tool can give the model vision it lacks. |
| DOCX | A Word or OOXML tool that exposes tracked changes, comments and table structure, and can write them | It reports `w:ins`/`w:del`/moves with their authors, and comments (read-redline). It can edit a table in place (closing-checklist). | A plain docx-to-text converter. |
| SUB | Host subagents; MCP sampling, where a server asks the client for a fresh completion; a tool that calls another model | Each call is a fresh context holding only its packet. docreview and diligence also need the model and effort chosen per call. | A tool that shares the parent's context. |
| SESSION | Host conversation tools (list and read past chats); the host's own event log | timenarratives reads past chats through "host-native conversation list and read tools" (`conversation-context.md:9-13`). | A third-party server, since the transcript lives in the host. timenarratives prefers native readers to a local session scanner, and rules out browser scraping, reverse-engineered private APIs and uploading chat history. lq-reflect's scripts read Codex and Claude Code JSONL files on disk, so a transcript tool would need a new reader. |
| SCHED | A scheduler or trigger tool; host routines | It can keep a long-running process with a heartbeat alive for the detached review runners. | wiki's automatic retrieval, which needs host lifecycle hooks. A tool cannot add those. |
| HTML | A host artifact surface or MCP Apps UI to show the page; chat upload for the JSON it returns | The user can open the page and hand back the file it downloads. | Untested. The pages are written for `file://` and rely on Blob downloads and `localStorage`. |

### If every tool comes over MCP

Suppose a harness has TOOLS and MCP but no built-in tools, so every action goes to a server. Each skill is
placed according to its ● cells.

| Verdict | Skills | What the servers must provide |
|---|---|---|
| Needs no tools | **12**: client-update, correspondence, definition-check, depositions, legalquants, lq-ask, lq-mirror, new-matter, pressuretest, regulatory, timenarratives, writing | Nothing: their ● cells are at most IN (attachments) and INVOKE. Optional extras: lq-mcp for lq-ask; a raw-bytes fetch and a filesystem server for regulatory's verified route; search and fetch for writing, correspondence and client-update. |
| Works with any server (only public or personal data is involved) | **2**: lq-connect, lq-apply | Fetch. |
| Works only with local or approved servers, because client material is involved | **12**: cite-check, document-discovery, closing-checklist, playbook-builder, playbook-review, legaldesign, wiki, organize-case-docs, read-redline, sigpack, docreview, diligence | All need a filesystem server with write. Some need more, listed below. |
| Works only with a co-located code server | **3**: lq-start, conform, closing-bible | A code-execution server whose filesystem holds both the skill folders and the workspace. lq-start also needs the host's plugin install tree inside it. |
| Needs the host itself | **2**: lq-reflect, my-lq-moment | Past transcripts (lq-reflect) and the current session's tool and event log (my-lq-moment) belong to the host. lq-reflect also needs co-located exec over those transcripts. |

The counts sum to 31.

For the twelve client-material skills, some need more than a filesystem server with write:

- **organize-case-docs:** a tool that computes SHA-256 hashes.
- **document-discovery:** a docx server that starts from the bundled template.
- **closing-checklist:** a docx server that edits tables in place.
- **read-redline:** a docx server that reads tracked changes.
- **sigpack:** a render server and a multimodal model.
- **docreview and diligence:** a UI that accepts the returned JSON files.
- **wiki:** its Position notes must stay on the machine.

## Build-out order for a harness

Each rung adds a fixed set of capabilities to everything below it. A skill **runs** from the first rung
where every ● it has is met, and **runs as intended** from the first rung where every ● and ◐ is met.
Facets sit on the rung that supplies them (`OUT:pdf-assemble` needs the document stack at rung 4).
Every skill appears once in each of the last two columns.

<!-- gen:ladder-upstream -->
| Rung | Add | Runs from here (every ● met) | Runs as intended from here (every ● and ◐ met) |
|---|---|---|---|
| 0 | Baseline only: chat plus Agent Skills | **7**: client-update, correspondence, definition-check, depositions, new-matter, regulatory, writing | **0** |
| 1 | IN (attachments in context) and calling a skill by name (INVOKE) | **5**: legalquants, lq-ask, lq-mirror, pressuretest, timenarratives | **3**: correspondence, depositions, lq-mirror |
| 2 | TOOLS with OUT, FS and PERSIST: a durable workspace, skills materialised on disk | **6**: cite-check, closing-checklist, lq-apply, playbook-builder, playbook-review, wiki | **1**: new-matter |
| 3 | EXEC, SKILLDIR, HASH and DOCX: a Python 3.12 stdlib sandbox over the workspace and the skill folders | **6**: closing-bible, conform, document-discovery, lq-start, organize-case-docs, read-redline | **3**: legalquants, lq-start, organize-case-docs |
| 4 | BIN and VISION: pypdf, pdfplumber, python-docx, Pillow, Poppler, LibreOffice, and a model that reads rendered pages | **1**: sigpack | **4**: closing-bible, closing-checklist, playbook-builder, read-redline |
| 5 | HTML: the user opens a generated page and returns its file | **3**: diligence, docreview, legaldesign | **2**: legaldesign, pressuretest |
| 6 | SUB: isolated workers, model chosen per worker | **0** | **8**: client-update, conform, definition-check, diligence, docreview, playbook-review, sigpack, wiki |
| 7 | NET (raw bytes) and SEARCH | **1**: lq-connect | **6**: cite-check, document-discovery, lq-apply, lq-connect, regulatory, writing |
| 8 | SESSION: the session's own events and past transcripts | **2**: lq-reflect, my-lq-moment | **3**: lq-reflect, my-lq-moment, timenarratives |
| 9 | MCP connection | **0** | **1**: lq-ask |
| 10 | SCHED: scheduled runs and hooks | **0** | **0** |
<!-- /gen:ladder-upstream -->

The ladder for the Cowork cards is in [The Cowork cards](#the-cowork-cards).

MCP sits late on this ladder because no skill requires it. A harness that gets its tools from MCP servers
instead of building them in needs MCP at rung 2. It is then bound by the conditions in
[Tool execution](#tool-execution).

## The Cowork cards

The same codes, rated for the adapted Microsoft 365 Copilot Cowork cards as built (profile `cowork` in
`capabilities.yaml`). The cards ship no scripts and call no external service, so EXEC, BIN and SKILLDIR
almost vanish; the host's own Word, Excel and PDF handling and its web search carry what is left. Each
card's probe-citing known issue is tied to a code or a facet here, and validation (LQC-K006) fails a card
that cites a probe testing nothing its profile rates.

<!-- gen:matrix-cowork -->
| Skill | TOOLS | MCP | IN | OUT | FS | PERSIST | EXEC | BIN | NET | SEARCH | VISION | DOCX | SUB | SESSION | SCHED | HTML |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **core** | | | | | | | | | | | | | | | | |
| legaldesign | ● | ○ | ● | ● |  |  |  |  |  |  | ◐ |  |  |  |  | ● |
| lq-start |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| regulatory | ● |  | ◐ | ● | ○ | ○ |  |  |  | ○ | ◐ |  |  |  |  |  |
| timenarratives | ○ |  | ○ | ○ | ○ |  |  |  |  |  |  | ○ |  | ○ |  |  |
| wiki | ● |  | ● | ● | ● | ◐ |  |  |  |  |  |  | ◐ |  |  | ◐ |
| **companion** | | | | | | | | | | | | | | | | |
| legalquants | ◐ |  | ◐ |  | ◐ | ○ |  |  |  |  |  |  |  |  |  |  |
| lq-apply | ● |  | ◐ | ● | ◐ | ○ |  |  | ○ |  |  | ○ |  |  |  |  |
| lq-ask | ○ |  |  |  |  |  |  |  |  | ○ |  |  |  |  |  |  |
| lq-connect | ◐ |  | ○ |  |  |  |  |  |  | ◐ |  |  |  |  |  |  |
| lq-mirror | ○ |  |  | ○ |  |  |  |  |  |  |  |  |  |  |  |  |
| lq-reflect | ○ |  | ○ | ○ | ○ | ○ |  |  |  |  |  |  |  | ○ |  |  |
| my-lq-moment | ● |  | ◐ | ◐ | ○ |  |  |  |  |  |  |  |  | ● |  | ◐ |
| **litigation** | | | | | | | | | | | | | | | | |
| cite-check | ● |  | ● | ● |  |  |  |  |  | ◐ |  |  |  |  |  | ○ |
| client-update | ○ | ○ | ◐ | ○ |  | ○ |  |  |  | ○ |  | ○ |  |  |  |  |
| correspondence | ○ | ○ | ◐ |  |  |  |  |  |  | ○ |  |  |  |  |  |  |
| depositions | ○ | ○ | ◐ | ○ |  | ○ |  |  |  |  |  |  |  |  |  |  |
| docreview | ● |  | ● | ● | ● | ◐ |  |  |  |  | ◐ |  |  |  |  | ● |
| document-discovery | ● | ○ | ● | ● |  |  |  |  | ◐ | ◐ | ◐ | ◐ |  |  |  |  |
| new-matter | ◐ | ○ | ○ | ◐ | ◐ | ○ |  |  |  | ○ |  |  |  |  |  |  |
| organize-case-docs | ● | ○ | ● | ◐ | ● | ● |  |  |  |  |  |  |  |  |  |  |
| pressuretest | ◐ |  | ● | ◐ | ○ |  |  |  |  |  |  | ○ |  |  |  | ○ |
| writing | ◐ | ○ | ○ |  |  |  |  |  | ◐ | ◐ |  |  |  |  |  |  |
| **transactional** | | | | | | | | | | | | | | | | |
| closing-bible | ● |  | ● | ● |  | ◐ |  |  |  |  | ◐ | ○ |  |  |  |  |
| closing-checklist | ● | ○ | ● | ● |  |  |  |  | ○ | ○ | ◐ | ● |  |  |  |  |
| conform | ◐ |  | ● | ◐ |  |  |  |  |  |  |  | ◐ |  |  |  |  |
| definition-check | ● |  | ◐ | ● |  | ○ |  |  |  |  |  |  |  |  |  | ● |
| diligence | ● |  | ● | ● |  | ◐ |  |  |  |  | ◐ |  |  |  | ○ | ● |
| playbook-builder | ● |  | ● | ● |  | ◐ |  |  |  |  | ◐ | ◐ |  |  |  |  |
| playbook-review | ◐ |  | ● | ◐ |  | ◐ |  |  |  |  | ◐ | ◐ |  |  |  |  |
| read-redline | ● |  | ● | ● |  |  |  |  |  |  | ◐ | ● |  |  |  | ● |
| sigpack | ● |  | ● | ● |  | ◐ |  |  |  |  |  | ● |  |  |  |  |
<!-- /gen:matrix-cowork -->

<!-- gen:counts-cowork -->
12 skills have no ● at all and run on the baseline alone, in their documented degraded form where they have ◐ items: client-update, correspondence, depositions, legalquants, lq-ask, lq-connect, lq-mirror, lq-reflect, lq-start, new-matter, timenarratives, writing. TOOLS is ● for 16 skills, ◐ for 7 and ○ for 7.
<!-- /gen:counts-cowork -->

<!-- gen:aux-cowork -->
| Skill | HASH | SKILLDIR | INVOKE |
|---|---|---|---|
| client-update | ○ |  |  |
| depositions | ○ |  |  |
| document-discovery |  | ◐ |  |
| legaldesign |  | ◐ asset |  |
| my-lq-moment |  | ◐ asset |  |
| organize-case-docs | ● |  |  |
| wiki | ◐ |  |  |
<!-- /gen:aux-cowork -->

<!-- gen:facets-cowork -->
| Skill | Facet | Level | Probes |
|---|---|---|---|
| closing-bible | `OUT:pdf-assemble` | ◐ | P8 |
| closing-bible | `OUT:xlsx-roundtrip` | ◐ | P9 |
| conform | `DOCX:tracked-write` | ◐ | P10 |
| definition-check | `OUT:xlsx-roundtrip` | ◐ | P9 |
| diligence | `OUT:xlsx-roundtrip` | ◐ | P9 |
| docreview | `OUT:xlsx-roundtrip` | ◐ | P9 |
| lq-connect | `SEARCH:org` | ◐ | P14 |
| playbook-review | `DOCX:tracked-write` | ○ | P10 |
| read-redline | `DOCX:tracked-write` | ◐ | P10 |
| sigpack | `OUT:xlsx-roundtrip` | ◐ | P9 |
| timenarratives | `SESSION:resume` | ○ | P5 |
<!-- /gen:facets-cowork -->

<!-- gen:ladder-cowork -->
| Rung | Add | Runs from here (every ● met) | Runs as intended from here (every ● and ◐ met) |
|---|---|---|---|
| 0 | Baseline only: chat plus Agent Skills | **12**: client-update, correspondence, depositions, legalquants, lq-ask, lq-connect, lq-mirror, lq-reflect, lq-start, new-matter, timenarratives, writing | **5**: lq-ask, lq-mirror, lq-reflect, lq-start, timenarratives |
| 1 | IN (attachments in context) and calling a skill by name (INVOKE) | **3**: conform, playbook-review, pressuretest | **3**: client-update, correspondence, depositions |
| 2 | TOOLS with OUT, FS and PERSIST: a durable workspace, skills materialised on disk | **7**: cite-check, closing-bible, document-discovery, lq-apply, playbook-builder, regulatory, wiki | **4**: legalquants, lq-apply, new-matter, pressuretest |
| 3 | EXEC, SKILLDIR, HASH and DOCX: a Python 3.12 stdlib sandbox over the workspace and the skill folders | **3**: closing-checklist, organize-case-docs, sigpack | **2**: conform, organize-case-docs |
| 4 | BIN and VISION: pypdf, pdfplumber, python-docx, Pillow, Poppler, LibreOffice, and a model that reads rendered pages | **0** | **6**: closing-bible, closing-checklist, playbook-builder, playbook-review, regulatory, sigpack |
| 5 | HTML: the user opens a generated page and returns its file | **5**: definition-check, diligence, docreview, legaldesign, read-redline | **5**: definition-check, diligence, docreview, legaldesign, read-redline |
| 6 | SUB: isolated workers, model chosen per worker | **0** | **1**: wiki |
| 7 | NET (raw bytes) and SEARCH | **0** | **4**: cite-check, document-discovery, lq-connect, writing |
| 8 | SESSION: the session's own events and past transcripts | **1**: my-lq-moment | **1**: my-lq-moment |
| 9 | MCP connection | **0** | **0** |
| 10 | SCHED: scheduled runs and hooks | **0** | **0** |
<!-- /gen:ladder-cowork -->

## Method and confidence

Six Sonnet subagents each audited one slice of `upstream/skills/`. Every `SKILL.md`, reference, schema
and script import was read against the fixed code list above. Levels were taken from each skill's own
"fallback", "cascade" and "if the host…" language, with file and line evidence.

The orchestrator then cross-checked the heaviest claims by grep across the tree, and the claims held:

- Third-party imports appear only in read-redline, sigpack, closing-bible, playbook-builder,
  playbook-review and legaldesign `exhibit.py`.
- Network calls appear only in `regulatory/scripts/fetch_source.py` and
  `legalquants/scripts/evidence.py`.
- The external binaries invoked are exactly Poppler, LibreOffice, tesseract, Chromium, Inkscape,
  `rsvg-convert` and `codex`.

The TOOLS column is derived from the other cells, as the code list explains. The MCP column, and the
rules quoted in the TOOLS and MCP section, come from a further sweep of every skill's Markdown. That sweep
searched for MCP, connector, host-native and tool-cascade language and for data-boundary rules. Every
rule quoted is cited to the file it came from.

A second pass of four Sonnet subagents rated every adapted Cowork card as built into `dist/`, rated the
auxiliary codes for both profiles, quoted each degradable level's fallback wording with file and line,
and disputed the first pass where the text disagreed (see
[Changes since the first audit](#changes-since-the-first-audit)). Facets tie each card's probe-citing
known issue to the code that probe decides.

No script was executed in either audit. Levels describe what the skills say about themselves. What a real
harness does is measured by the [harness-probe skill](../../harness-probe/SKILL.md), whose reports the
site renders under Verdicts.
