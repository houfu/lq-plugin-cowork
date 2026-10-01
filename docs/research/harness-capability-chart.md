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

Everything else counts as an additional capability.

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

## Build-out order for a harness

Each rung assumes the ones before it. A skill is placed on the first rung where **all** of its ● cells are
met, so every skill appears exactly once. It then runs in its degraded form until its ◐ items are also
present.

| Rung | Add | Skills whose ● are all met here (new) | Main ◐ upgrades this rung brings |
|---|---|---|---|
| 0 | Baseline only | **9**: timenarratives, legalquants, lq-ask, lq-mirror, client-update, correspondence, depositions, new-matter, writing | — |
| 1 | IN, OUT, FS, PERSIST: a durable workspace with user-named folders, and the skills materialised on disk | **10**: lq-apply, pressuretest, cite-check, document-discovery, closing-checklist, definition-check, playbook-builder, playbook-review, wiki, organize-case-docs (which still needs some way to SHA-256 files) | new-matter and legalquants save their files. |
| 2 | EXEC: a Python ≥3.12 stdlib sandbox that can reach both the workspace and the skill folders | **4**: lq-start, conform, closing-bible, read-redline (Word path) | Script-verified receipts and hashes for almost every ◐ EXEC cell. timenarratives and wiki move off their fallback routes. |
| 3 | Document stack and VISION: **pypdf, pdfplumber, python-docx, Pillow**, **Poppler**, **LibreOffice**, and a model that reads rendered pages | **1**: sigpack | read-redline's PDF path, closing-bible's execution-page inspection, scans in diligence and docreview, closing-checklist's layout QA. |
| 4 | HTML: the user can open a generated local HTML file and return the JSON file it downloads | **3**: legaldesign, docreview, diligence | document-discovery's review page; wiki's rich browse view. |
| 5 | SUB: isolated worker contexts, with a model and effort choice for each worker | **0** | Parallel speed and independent review in cite-check, docreview, diligence, definition-check, conform and sigpack. wiki's fresh-context gate reviewer. |
| 6 | NET (raw bytes) and SEARCH | **2**: regulatory, lq-connect | Live sources for lq-ask and lq-apply. Authority checks for cite-check, writing and document-discovery. |
| 7 | SESSION: the current session's event log, plus access to past transcripts | **2**: lq-reflect, my-lq-moment | timenarratives can read related chats. |
| 8 | SCHED or hooks, and CONN (lq-mcp, CourtListener MCP, a DMS) | **0** | Optional extras only: wiki auto-retrieval, detached review runners, connector rungs. |

The counts sum to 31.

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

No script was executed. Levels describe what the skills say about themselves, not observed behaviour on
any harness.
