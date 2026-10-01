# Harness capability chart for the vendored skills

1 October 2026

This chart answers one question: **what does a harness need, beyond a chat-completion loop that can use
skills, to run each vendored upstream skill?** It covers all thirty-one skills in `upstream/skills/` at the
pinned SHA `fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0`, not the Cowork adaptations in `skills/`. The
adaptations exist precisely because Cowork lacks some of what is listed here.

## Baseline assumed

The harness already has these, so they are not listed per skill:

- **Multi-turn chat with the user.** This includes every approval gate, "stop and wait" checkpoint and
  three-question intake the skills use.
- **Agent Skills support.** The harness discovers skills by description, loads `SKILL.md` and loads the
  skill's own text files (`references/*.md`, schemas, prompts) into context on demand.

Everything else counts as an additional capability. The baseline includes no tool calling. Many of the
capabilities below can come from MCP servers or other tools instead of the harness itself; see
[Supplying capabilities through MCP](#supplying-capabilities-through-mcp-or-a-similar-tool-interface).

## Capability codes

| Code | Capability the harness must add |
|---|---|
| **IN** | Read files the user supplies: pdf, docx, xlsx, eml, txt/md, csv, images. |
| **OUT** | Write and hand back files: html, docx, pdf, json, csv, md, png/svg. |
| **FS** | A real filesystem. This covers user-named paths, recursive folder walks, a run or work directory, sibling output folders, and the skill directory itself present on disk. |
| **PERSIST** | Storage that outlives the session. Examples are `~/.lq/`, `~/.wiki/`, a ledger or registry in a matter folder, and earlier run folders. |
| **EXEC** | Run the bundled Python scripts. These are stdlib-only unless the detail table says otherwise. |
| **BIN** | External executables: Poppler, LibreOffice, tesseract, headless Chromium, an SVG rasteriser, or the `codex` CLI. |
| **NET** | Fetch a URL and get **raw bytes back**. A model's summary of a page does not count. |
| **SEARCH** | A web search engine. |
| **VISION** | The model looks at rendered page images, such as signature pages, redline marks or layout QA. |
| **DOCX** | Read or write Word OOXML structure (tracked changes, comments, table XML), not just the text. |
| **SUB** | Isolated worker contexts: parallel subagents, or a fresh-context reviewer call. |
| **SESSION** | Read conversation transcripts: the current session's events and tool calls, or past sessions. |
| **SCHED** | Background, detached or hook-driven runs that outlive the turn. |
| **CONN** | An external service via MCP or API. The skill row names it. |
| **HTML** | The user opens a generated offline HTML page in a browser. For docreview and document-discovery, the user's decisions come back as a downloaded JSON file. |

Two capabilities are left out as columns:

- **Hashing.** All SHA-256 work is done inside the bundled scripts, so EXEC covers it. The one exception is
  organize-case-docs, noted in its row.
- **A reliable clock.** Every skill that needs a date accepts one from the user, or gets it from a script.

**Levels.** Each level comes from the skill's own text.

| Symbol | Level | Meaning |
|---|---|---|
| ● | Required | The skill cannot produce its core deliverable, or it stops. |
| ◐ | Degradable | The skill documents a fallback and says what is lost, typically "provisional", "not script-verified", "unvalidated preview", or a check reported as not run. |
| ○ | Optional | An enhancement only. |
| blank | Not used | |

## Matrix

| Skill | IN | OUT | FS | PERSIST | EXEC | BIN | NET | SEARCH | VISION | DOCX | SUB | SESSION | SCHED | CONN | HTML |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **core** | | | | | | | | | | | | | | | |
| legaldesign | ● | ● | ● | ○ | ◐ | ○ | ○ | | ◐ | | | | | ○ | ● |
| lq-start | | | ● | | ● | | | | | | | | | | |
| regulatory | ◐ | ○ | ● | ○ | ◐ | | ● | ◐ | | | ○ | | | ○ | |
| timenarratives | ○ | ◐ | ○ | ○ | ◐ | | | | | ○ | | ◐ | | ○ | |
| wiki | ● | ○ | ● | ● | ◐ | | ○ | | | | ◐ | ○ | ○ | | ◐ |
| **companion** | | | | | | | | | | | | | | | |
| legalquants | | | ◐ | ◐ | ◐ | | | | | | | | | | |
| lq-apply | ○ | ● | ○ | ◐ | ◐ | | ◐ | | | | | | | | |
| lq-ask | ○ | | | | ◐ | | ◐ | | | | | | | ◐ | |
| lq-connect | | | | | ◐ | | ● | | | | | | | | |
| lq-mirror | | ○ | | ○ | ○ | | | | | | | | | | |
| lq-reflect | ● | ○ | ● | ● | ● | | | | | | ◐ | ● | | | |
| my-lq-moment | ◐ | ● | ◐ | ○ | ● | ◐ | | | | | | ● | | | |
| **litigation** | | | | | | | | | | | | | | | |
| cite-check | ● | ● | ● | ○ | ◐ | ○ | ○ | ◐ | | | ◐ | | | ○ | |
| client-update | ◐ | ○ | | ○ | ○ | | ○ | ○ | | | ◐ | | | ○ | |
| correspondence | ◐ | ○ | | ○ | | | ○ | ○ | | | | | | ○ | |
| depositions | ◐ | ○ | | ○ | | | ○ | ○ | | | | | | ○ | |
| docreview | ● | ● | ● | ○ | ◐ | ○ | | | ◐ | | ◐ | | ○ | | ● |
| document-discovery | ● | ● | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | ○ | | | | ○ | ◐ |
| new-matter | ○ | ◐ | ◐ | ○ | | | | | | | | | | ○ | |
| organize-case-docs | ● | ◐ | ● | ● | ◐ | ○ | | | ○ | | | | | ○ | |
| pressuretest | ● | ◐ | ◐ | | ◐ | | | | | | ○ | | | | |
| writing | ○ | ○ | | ○ | | | ◐ | ◐ | | | | | | ○ | |
| **transactional** | | | | | | | | | | | | | | | |
| closing-bible | ● | ● | ● | ○ | ● | ◐ | | | ◐ | | ○ | | | | |
| closing-checklist | ● | ● | ● | ○ | ◐ | ○ | ○ | ○ | ◐ | ◐ | ○ | | | ○ | |
| conform | ● | ● | ● | | ● | | ○ | | | | ◐ | | | ○ | |
| definition-check | ● | ◐ | ● | ○ | ◐ | ○ | | | | ◐ | ◐ | | | | |
| diligence | ● | ● | ● | ○ | ◐ | ○ | | | ◐ | | ◐ | | ○ | | ● |
| playbook-builder | ● | ● | ● | ● | ◐ | | | | ◐ | ◐ | | | | | |
| playbook-review | ● | ● | ● | ● | ◐ | | | | ◐ | ◐ | ◐ | | | | |
| read-redline | ● | ● | ● | ○ | ◐ | ◐ | | | ◐ | ● | | | | | |
| sigpack | ● | ● | ● | ● | ◐ | ◐ | | | ● | ○ | ◐ | | | | |

Nine skills have no ● at all: timenarratives, legalquants, lq-ask, lq-mirror, client-update,
correspondence, depositions, new-matter and writing. They run on the baseline alone, in their documented
degraded form wherever they have ◐ items.

## Per skill: what is hard, what it runs on, what degrades

"Py" is the minimum Python version the scripts need. "stdlib" means no third-party imports.

### core

| Skill | Hard requirements (●) | Runtime the scripts need | What degrades without the ◐ items |
|---|---|---|---|
| legaldesign | Read the work product; write one self-contained `.html` file plus `artifact.spec.json`; the user opens it in a browser (it uses `localStorage` and `showSaveFilePicker`). | `scaffold.py`: Py ≥3.10, stdlib. `exhibit.py` (optional source clips): Py ≥3.11, **PyMuPDF**, **Playwright with Chromium**. | Without scripts the model must hand-build the runtime and validation, and must not claim checks it did not run. Without vision, multi-viewport visual QA is reported as not done. |
| lq-start | Run `catalog.py`, which walks the host's plugin install folders and reads `$CODEX_HOME/config.toml`. Its output is the only list a skill may be named from. | Py 3, stdlib. | Nothing degrades. Without exec it cannot name installed skills. |
| regulatory | Fetch the publisher's **raw bytes**, save them to a run folder and hash them. A rendering from a web-fetch tool is rejected. | 8 scripts, Py 3, stdlib (`urllib`). Some publishers need a correct TLS trust store and a browser User-Agent. | Without a fetch, the answer is labelled "provisional and unverified". Search is only for locating an instrument, never as a source. A PDF source needs a text extraction step. Refresh needs a prior run folder. |
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
| definition-check | Read the `.docx`; output and work directories (OS temp). | ~50 files, Py ≥3.12, stdlib. Uses `fcntl`/`msvcrt` locks and hard links on the adapter path. The `codex exec` worker adapter is optional. | Without exec, it is a reduced-assurance review of host-extracted text (C1) that never says "no issues". Without workers, it runs sequentially. Without file output, the report is given in chat. |
| diligence | Walk the data room; a run directory; write HTML, JSON and CSV; the user opens the HTML pages. | 47 scripts, Py ≥3.11, stdlib. **Poppler** and **LibreOffice** are optional. The `codex exec` adapter is optional. | Without exec it is not "coverage-certified". Without vision, scans go to "Needs rendering". It requires a higher-capability model for mapping and a sample recall gate. A detached runner is optional. |
| playbook-builder | Read 1–5 sources (docx/md/txt/pdf, or xlsx/csv for an import); write a sealed package plus `playbook-registry.json` that persists for playbook-review. | 3 files, Py 3, stdlib. **pdfplumber** and **pypdf** are optional for PDF text. | Without exec, hashing and receipts are done by host means, or the receipt is not claimed. Without vision, scanned PDF pages stay `pending-vision`. |
| playbook-review | Find `playbook-registry.json` by walking up from the working directory; read the contract package; write the Word issues matrices. | Same runtime as builder. The DOCX is written by hand-built OOXML. | Without exec, a receipt is unavailable. Without vision, scanned pages are left pending. Without workers, it runs sequentially. |
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
- **Explicit invocation.** These skills set `disable-model-invocation: true` or
  `allow_implicit_invocation: false`, so the harness must let the user call a skill by name:
  - lq-start;
  - legalquants;
  - lq-ask;
  - lq-connect;
  - lq-mirror;
  - timenarratives.
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

## Supplying capabilities through MCP or a similar tool interface

The matrix says what each skill needs. It does not say how the harness supplies it. A harness that adds
one thing, a **tool-calling loop with an MCP client**, can supply most columns through tool servers
instead of building them in. Plain chat completion does not include tool calls, so this client is a
prerequisite for every MCP route below, but on its own it makes no skill runnable.

"Similar" means any tool the model calls during a turn: function calling, OpenAPI tools, host
connectors (Cowork `agentConnectors`, claude.ai connectors) and MCP Apps for UI. Everything in this
section applies to them in the same way.

### The skills already accept host tools

Most skills describe a **tool cascade**: the bundled scripts first, then host-native tools, then a
licensed service that the user or firm selects (`upstream/AGENTS.md`, "Tool cascade"). An MCP tool is a
host tool. Examples:

- diligence and docreview, `references/shared/execution-modes.md:75`;
- read-redline, `SKILL.md:124`;
- sigpack, `SKILL.md:135`;
- playbook-builder, `SKILL.md:282-287`;
- regulatory, `SKILL.md:612-617`.

definition-check and conform name MCP outright as profile `C5_APPROVED_INTEGRATIONS`
(`references/capability-routing.md`).

### Three rules decide whether a server counts

1. **The tool must actually perform the operation.** The rule is "do not claim SHA-256 identity …
   automated count reconciliation unless a host-native tool actually performed it"
   (`execution-modes.md:96-98`).
   - A server that summarises a page or describes a file does not satisfy NET, hashing or DOCX.
   - regulatory rejects a web-fetch tool's rendering as "a model's summary of the text, not the text"
     (`SKILL.md:46-49`).
2. **Client material stays inside a boundary that is already authorised.** Remote processing is allowed
   only where the "connector, network, DMS, or hosted-service data boundary is already authorized", and it
   is recorded (`capability-routing.md:9`). Several skills make this concrete:
   - cite-check sends only citation metadata to a public service (`getting-authorities.md:77`);
   - client-update never uploads matter material "merely to format or summarize it" (`SKILL.md:56`);
   - closing-checklist does not upload matter documents to a new service (`SKILL.md:30`);
   - wiki Position notes "never leave the machine".

   In practice, for the matter skills, any server that touches the documents must be local (stdio) or the
   firm's own approved system.
3. **The bundled scripts can only see a filesystem.** They take paths, import sibling modules, read
   `../assets`, and call other skills' scripts by relative path.
   - A code-execution server satisfies EXEC only if the skill folders and the user's workspace are both
     inside its filesystem.
   - A remote sandbox that holds neither does nothing for the script path.
   - Uploading matter files into a remote sandbox falls under rule 2.

### Capability by capability

| Code | MCP or tool route | Counts when | Does not count |
|---|---|---|---|
| IN | A filesystem server; a DMS connector (SharePoint/OneDrive, iManage, NetDocuments); upload into the chat | The tool returns the whole document. For the script path, the file must also land where the scripts can read it. | A connector that returns snippets or summaries. A remote DMS used for documents outside its authorised boundary. |
| OUT | A filesystem server with write; a DMS connector with write; a host file-return or artifact tool | The user gets a file they can open. docx and pdf output also need a tool that produces that format (see DOCX and BIN). | — |
| FS | A local filesystem server with list, recursive walk, read, write and make-directory | Paths stay stable across calls, and EXEC (if used) sees the same tree. | Connectors that address items by ID with no paths. They serve the model-read fallback, not the scripts. |
| PERSIST | The same filesystem server on durable storage | The files the skills expect survive between sessions: `~/.lq/`, `~/.wiki/wikis.json`, `sigpack.ledger.json`, `playbook-registry.json`, earlier run folders. | A generic memory or key-value server. No skill reads one, and the bundled scripts are the only writers of these stores. |
| EXEC | A code-execution server, local or sandboxed | It runs Python ≥3.12 and has both the skill folders and the workspace mounted. | A sandbox without the skill folders. A remote sandbox that matter files must be uploaded into. |
| BIN | The EXEC sandbox with the binaries installed; or dedicated render and convert servers (LibreOffice, PDF rendering) | The agent itself calls the binary, as read-redline and sigpack do with `pdftoppm`. | Binaries that scripts launch via `subprocess` (closing-bible, docreview, diligence, sigpack). These must be inside the EXEC sandbox, not behind a separate server. |
| NET | A fetch server | For regulatory, it saves the **raw response bytes** to the workspace so they can be hashed. For lq-connect and the live parts of lq-ask, a readable page is enough. | For regulatory, a fetch server that converts HTML to Markdown. |
| SEARCH | A search server (Brave, Bing, Tavily and similar) | Queries carry citation metadata only, never client text (cite-check). | — |
| VISION | A render server that returns page images as image content, plus a multimodal model | Every page asked for is rendered and actually looked at. sigpack refuses to compile otherwise. | OCR text standing in for the image: sigpack decides `signed` from the render alone. A server cannot give the model vision it lacks. |
| DOCX | A Word or OOXML server that exposes tracked changes, comments and table structure, and can write them | It reports `w:ins`/`w:del`/moves with their authors, and comments (read-redline). It can edit a table in place (closing-checklist). | A plain docx-to-text converter. |
| SUB | Host subagents; MCP sampling, where a server asks the client for a fresh completion; an "ask another model" tool | Each call is a fresh context holding only its packet. docreview and diligence also need the model and effort chosen per call. | A tool that shares the parent's context. |
| SESSION | Host conversation tools (list and read past chats); the host's own event log | timenarratives reads past chats through "host-native conversation list and read tools" (`conversation-context.md:9-13`). | A generic server, since the transcript lives in the host. timenarratives prefers native readers to a local session scanner, and rules out browser scraping, reverse-engineered private APIs and uploading chat history. lq-reflect's scripts read Codex and Claude Code JSONL files on disk, so a transcript server would need a new reader. |
| SCHED | A scheduler or trigger server; host routines | It can keep a long-running process with a heartbeat alive for the detached review runners. | wiki's automatic retrieval, which needs host lifecycle hooks. A server cannot add those. |
| CONN | The named connectors, listed in the next table | — | — |
| HTML | A host artifact surface or MCP Apps UI to show the page; chat upload for the JSON it returns | The user can open the page and hand back the file it downloads. | Untested. The pages are written for `file://` and rely on Blob downloads and `localStorage`. |

### Connectors the skills name

| Skill | Connector | Level | Rule |
|---|---|---|---|
| lq-ask | **lq-mcp**, guest scope | ◐ | A connector being present "does not prove member access". The member tier (LQ Brain) needs an authorised capability response and is not shipped (`SKILL.md:44-59`). |
| cite-check | **CourtListener MCP** | ○ | Used only when the host exposes it and the user authorises it. Only citation metadata is sent (`getting-authorities.md:75-77`). |
| definition-check, conform | "network/connectors/MCP/DMS", as profile C5 | ○ | Only inside an already-authorised boundary, and remote processing is recorded. The example given is retrieving a source ledger from a DMS. |
| closing-checklist, new-matter, organize-case-docs, depositions, client-update, writing, correspondence, document-discovery, timenarratives, legaldesign | Unnamed, firm-selected systems: DMS, matter management, docket, e-billing, e-discovery or transcript platforms, licensed legal research | ○ | Only when the user or firm selects one, and never assumed. new-matter never reports a system as queried unless it actually returned a result (`SKILL.md:100`). |
| my-lq-moment, correspondence, sigpack, playbook-review, diligence | Publishing, email, calendar, docketing, e-signature | **Forbidden** | These skills never send, post, file, docket or run an e-signature process, even when the connector exists. A harness should not expose such tools to them. |

### Which skills can run on MCP alone

Here, "MCP alone" means the harness has no local Python runtime of its own, only tool servers. Each skill
is placed according to its ● cells.

| Verdict | Skills | Servers that cover the ● cells |
|---|---|---|
| Needs nothing | **9**: timenarratives, legalquants, lq-ask, lq-mirror, client-update, correspondence, depositions, new-matter, writing | Optional extras: lq-mcp for lq-ask; search and fetch for writing, correspondence and client-update. |
| Yes, with any server (only public or personal data is involved) | **3**: lq-connect, lq-apply, regulatory | lq-connect and lq-apply need fetch. regulatory needs a fetch server that saves raw bytes, plus a filesystem server; its script verification stays ◐. |
| Yes, but the servers must be local or inside an approved boundary, because client material is involved | **14**: cite-check, pressuretest, document-discovery, closing-checklist, definition-check, playbook-builder, playbook-review, legaldesign, wiki, organize-case-docs, read-redline, sigpack, docreview, diligence | All need a filesystem server with write. Some need more, listed below. |
| Only with a co-located code server | **3**: lq-start, conform, closing-bible | A code-execution server whose filesystem holds both the skill folders and the workspace. lq-start also needs the host's plugin install tree inside it. |
| Needs the host itself | **2**: lq-reflect, my-lq-moment | Past transcripts (lq-reflect) and the current session's tool and event log (my-lq-moment) belong to the host. lq-reflect also needs co-located exec over those transcripts. |

The counts sum to 31.

For the fourteen client-material skills, some need more than a filesystem server with write:

- **organize-case-docs:** a tool that computes SHA-256 hashes.
- **document-discovery:** a docx server that starts from the bundled template.
- **closing-checklist:** a docx server that edits tables in place.
- **read-redline:** a docx server that reads tracked changes.
- **sigpack:** a render server and a multimodal model.
- **docreview and diligence:** a UI that accepts the returned JSON files.
- **wiki:** its Position notes must stay on the machine.

## Build-out order for a harness

Each rung assumes the ones before it. A skill is placed on the first rung where **all** of its ● cells are
met, so every skill appears exactly once. It then runs in its degraded form until its ◐ items are also
present.

Every rung can be built natively or through tool servers. The "Via MCP or tools" column needs the MCP
client prerequisite and is bound by the three rules above.

| Rung | Add | Via MCP or tools | Skills whose ● are all met here (new) | Main ◐ upgrades this rung brings |
|---|---|---|---|---|
| 0 | Baseline only | — | **9**: timenarratives, legalquants, lq-ask, lq-mirror, client-update, correspondence, depositions, new-matter, writing | — |
| — | Tool calling with an MCP client | The prerequisite for every route in this column | **0** | lq-mcp for lq-ask; CourtListener for cite-check; firm-selected connectors. |
| 1 | IN, OUT, FS, PERSIST: a durable workspace with user-named folders, and the skills materialised on disk | A local filesystem server on durable storage. A DMS connector only inside its approved boundary. | **10**: lq-apply, pressuretest, cite-check, document-discovery, closing-checklist, definition-check, playbook-builder, playbook-review, wiki, organize-case-docs (which still needs some way to SHA-256 files) | new-matter and legalquants save their files. |
| 2 | EXEC: a Python ≥3.12 stdlib sandbox that can reach both the workspace and the skill folders | A code-execution server, but only if the skill folders and the workspace are inside it. | **4**: lq-start, conform, closing-bible, read-redline (Word path) | Script-verified receipts and hashes for almost every ◐ EXEC cell. timenarratives and wiki move off their fallback routes. |
| 3 | Document stack and VISION: **pypdf, pdfplumber, python-docx, Pillow**, **Poppler**, **LibreOffice**, and a model that reads rendered pages | The packages and binaries go inside the EXEC sandbox. The agent can call separate render and convert servers itself. The model's vision cannot come from a server. | **1**: sigpack | read-redline's PDF path, closing-bible's execution-page inspection, scans in diligence and docreview, closing-checklist's layout QA. |
| 4 | HTML: the user can open a generated local HTML file and return the JSON file it downloads | A host artifact surface or MCP Apps to show the page, and chat upload for the JSON (untested against `file://` pages). | **3**: legaldesign, docreview, diligence | document-discovery's review page; wiki's rich browse view. |
| 5 | SUB: isolated worker contexts, with a model and effort choice for each worker | Host subagents, or MCP sampling or another tool that calls a model, with fresh context and a choice of model per call. | **0** | Parallel speed and independent review in cite-check, docreview, diligence, definition-check, conform and sigpack. wiki's fresh-context gate reviewer. |
| 6 | NET (raw bytes) and SEARCH | Fetch and search servers. For regulatory, the fetch server must save the raw bytes. | **2**: regulatory, lq-connect | Live sources for lq-ask and lq-apply. Authority checks for cite-check, writing and document-discovery. |
| 7 | SESSION: the current session's event log, plus access to past transcripts | Host conversation tools only. No generic server can supply it. | **2**: lq-reflect, my-lq-moment | timenarratives can read related chats. |
| 8 | SCHED or hooks, and CONN | Trigger servers and named connectors. Hooks must come from the host. | **0** | Optional extras only: wiki auto-retrieval, detached review runners, connector rungs. |

The counts sum to 31. Running purely on servers, with no runtime of its own, a harness gets:

- 26 skills as long as the servers respect the boundary rules;
- 3 more (lq-start, conform, closing-bible) only with a co-located code server;
- 2 (lq-reflect, my-lq-moment) only from host features.

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

The MCP section adds a further sweep of every skill's Markdown. It searched for MCP, connector, host-native and tool-cascade language and for data-boundary rules, and every rule it quotes is cited to the file it came from.

No script was executed. Levels describe what the skills say about themselves, not observed behaviour on
any harness.
