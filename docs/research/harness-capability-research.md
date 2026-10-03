# Which harness capabilities each LegalQuants skill needs

*A capability-to-skill study of the 31 open-source LegalQuants legal skills, and of their adaptations for Microsoft 365 Copilot Cowork. 2 October 2026.*

## Summary

The LegalQuants skills ([LegalQuants/lq-plugin-oss](https://github.com/LegalQuants/lq-plugin-oss/tree/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/), pinned at `fa5a668`) are Agent Skills: folders holding a `SKILL.md` with instructions, reference documents, and in many cases Python scripts, schemas and templates. Whether one runs depends on the **harness** - the agent product that loads it - and harnesses differ widely in what they can do beyond chatting. This study asks, for each of the 31 skills: **starting from a chat model that can load skills, what more must the harness provide, how badly does the skill need it, and what does the skill do without it?**

Each skill was read in full and rated against 19 capability codes, at three levels:

- **● required**: without it the skill cannot produce its core deliverable, or it stops;
- **◐ degradable**: the skill documents a fallback, and says what is lost;
- **○ optional**: an enhancement.

The same codes were rated twice: for the skills as published upstream, and for the adapted cards an independent project ships for Microsoft 365 Copilot Cowork, which removes every script.

What stands out:

- **Tool execution decides most of it.** 19 of the 31 upstream skills cannot run in a chat-only harness that executes no tool calls; 9 more fall back without it. Every capability that acts rather than reads (files, folders, scripts, fetch, search, workers) arrives through a tool call.
- **A real filesystem and a script runtime come next.** 16 skills require reading supplied files, 14 require handing files back and 15 require a real folder structure (a data room, a production, a closing folder). The scripts are almost all standard-library Python; the version floor is **3.12**, and only a handful need third-party packages (pypdf, pdfplumber, python-docx, Pillow) or programs (Poppler, LibreOffice).
- **MCP is never required.** One skill falls back without its named connector (`lq-ask` and lq-mcp); 14 more use a connection if one is present and authorised, and five refuse to use publishing, email, docketing or e-signature connectors at all.
- **Few skills need nothing.** 7 upstream skills have no required capability and run, degraded where they have degradable ones, on the baseline alone: `client-update`, `correspondence`, `definition-check`, `depositions`, `new-matter`, `regulatory`, `writing`.
- **The Cowork adaptation trades scripts for host features.** Script execution drops from 24 skills to 0; the host's own Word, Excel and PDF handling, web search and organisational search carry what is left. 12 Cowork cards need nothing beyond the baseline.
- **Capability is not enough on its own.** Several skills also need their folder present on disk with sibling skills installed, a call-by-name invocation, a choice of model per worker, or provider-specific layouts; and any tool that touches client material must stay inside an approved data boundary.

A companion tool, the `harness-probe` skill, turns this table into a measurement: it runs 27 probes on a real harness and reports which skills run as intended, run on a fallback, cannot run, or are untested ([section 10](#10-measuring-a-real-harness)).

## Contents

1. [Question and baseline](#1-question-and-baseline)
2. [Method](#2-method)
3. [The capability codes](#3-the-capability-codes)
4. [Results: the upstream skills](#4-results-the-upstream-skills)
5. [Results: the Cowork cards](#5-results-the-cowork-cards)
6. [Capability by capability](#6-capability-by-capability)
7. [Skill by skill](#7-skill-by-skill)
8. [Requirements that are not a single capability](#8-requirements-that-are-not-a-single-capability)
9. [Supplying capabilities through tools and MCP](#9-supplying-capabilities-through-tools-and-mcp)
10. [Measuring a real harness](#10-measuring-a-real-harness)
11. [Build-out order for a harness](#11-build-out-order-for-a-harness)
12. [Limitations](#12-limitations)

## 1. Question and baseline

The baseline harness is assumed to have exactly two things, so neither is listed per skill:

- **Multi-turn chat with the user**, including every approval gate, "stop and wait" checkpoint and short intake interview the skills use.
- **Agent Skills support**: it discovers skills by their description, loads `SKILL.md`, and loads the skill's own text files (references, schemas, prompts) into context on demand.

It returns text only: no tool calls, no files, no network. Everything else is a capability the harness must add. A reliable clock is not rated, because every skill that needs a date accepts one from the user or gets it from a script.

## 2. Method

1. **First audit.** Six reviewer agents each read one slice of the upstream skills in full - every `SKILL.md`, reference, schema and script, and every script import - against a fixed list of capability codes. Each level was taken from the skill's own language ("fallback", "if the host...", "tool cascade", "if unavailable") and recorded with a file and line.
2. **Spot checks.** The heaviest claims were checked across the whole tree: third-party imports appear only in read-redline, sigpack, closing-bible, playbook-builder, playbook-review and legaldesign's optional `exhibit.py`; network calls only in regulatory's `fetch_source.py` and legalquants' `evidence.py`; the programs invoked are exactly Poppler, LibreOffice, tesseract, Chromium, Inkscape, `rsvg-convert` and `codex`.
3. **Second audit.** Four reviewer agents rated the adapted Cowork cards as built, rated three auxiliary codes for both profiles, quoted the skill's own fallback wording for every degradable level, and disputed the first audit where the text disagreed. Accepted corrections: regulatory's network and filesystem needs are degradable (it answers in a labelled "provisional and unverified" form); definition-check's filesystem and file input are degradable (it has a reduced-assurance text-only profile); playbook-review's persistence is degradable (a playbook can be supplied by path); four skills rate the HTML hand-back; and nine skills, not six, are explicit-invocation only.
4. **Derivation.** The TOOLS level is not audited separately: it is the strongest level among the codes that act through a tool call. A **facet** (for example `OUT:pdf-assemble`) narrows a code to the one thing a particular probe tests, so that a skill needing only to write a text file is not judged on PDF assembly.
5. **Probe ties.** Every code and facet is tied to the probe that measures it (section 10), and every known issue on a Cowork card that cites a probe was checked to rate something that probe measures.

No skill was executed during the audits. The levels describe what each skill says about itself; what a particular harness actually does is measured separately.

## 3. The capability codes

| Code | Capability | What counts |
| --- | --- | --- |
| **TOOLS** | Tool execution | The harness gives the model callable tools, runs each call and returns the result within the turn. Derived: the strongest of the action codes (everything except IN, HTML and INVOKE). |
| **MCP** | MCP connection | Connect to an MCP server (local stdio or remote HTTP), discover its tools and route calls to it; equivalent connector mechanisms count. Includes equivalent connector mechanisms (OpenAPI tools, Copilot agent connectors, claude.ai connectors). |
| **IN** | Read supplied files | Read files the user supplies (pdf, docx, xlsx, eml, text, images) whole. Needs no tool when the harness places attachments in context. |
| **OUT** | Hand back files | Write a file and hand it to the user.  |
| **FS** | Real filesystem | User-named paths, recursive folder walks, run and sibling output folders, stable paths.  |
| **PERSIST** | Storage that outlives the session | A file written in one session can be found in a later one without being attached again.  |
| **EXEC** | Run bundled scripts | Run the skills' bundled Python scripts; P1's facts are judged against each skill's exact needs. Python 3.8 to 3.12 depending on the skill; almost all standard library. |
| **BIN** | External executables | Poppler, LibreOffice, tesseract, headless Chromium, an SVG rasteriser or the codex CLI on the path.  |
| **NET** | Fetch a URL | Fetch a public page and quote it; skills that hash what they fetch add the raw-bytes probe. Skills that hash what they fetch (regulatory) also need the raw bytes, not a model's summary. |
| **SEARCH** | Web search | Search the web and return an address the user can check.  |
| **VISION** | See rendered pages | The model looks at a rendered page image and reports what is on it.  |
| **DOCX** | Word OOXML structure | Read tracked changes, comments and tables in a Word file, not just its text.  |
| **SUB** | Isolated workers | A fresh-context worker that sees only its packet, with the model chosen per worker.  |
| **SESSION** | Conversation transcripts | Quote the current session's own words and events, and say which are read and which reconstructed.  |
| **SCHED** | Background or scheduled runs | A run that happens after the turn ends and can read and write files.  |
| **HTML** | Interactive HTML round trip | The user opens a generated offline HTML page, and the file it downloads comes back to the skill.  |
| **HASH** | File digest by the host | Compute a SHA-256 of a file where no bundled script does it for the skill. Auxiliary. Only where no bundled script does the hashing for the skill. |
| **SKILLDIR** | Skill folder on disk | The skill's scripts, assets and sibling skills are reachable by path. Auxiliary. Scripts import siblings, read ../assets, and call other skills' scripts by path. |
| **INVOKE** | Call a skill by name | An explicit-invocation-only skill does not fire on its own, but fires when the user calls it by name. Auxiliary. `disable-model-invocation: true` or `allow_implicit_invocation: false`. |

## 4. Results: the upstream skills

The skills as published upstream, scripts included.

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

Levels: ● required, ◐ degradable, ○ optional, blank not used. A cell shows the strongest level of a code and its facets. Auxiliary codes and facets:

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

| Skill | Facet | Level | Probes |
|---|---|---|---|
| closing-bible | `OUT:pdf-assemble` | ◐ | P8 |
| closing-checklist | `DOCX:table-edit` | ◐ | P23 |
| document-discovery | `OUT:docx-template` | ● | P23 |
| read-redline | `OUT:pdf-annotate` | ◐ | P22 |
| sigpack | `OUT:pdf-assemble` | ● | P8 |

## 5. Results: the Cowork cards

The adapted cards as built for Microsoft 365 Copilot Cowork. They ship no scripts and call no external service; they rely on the host's own document handling, web search and organisational search instead.

| Skill | TOOLS | MCP | IN | OUT | FS | PERSIST | EXEC | BIN | NET | SEARCH | VISION | DOCX | SUB | SESSION | SCHED | HTML |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **core** | | | | | | | | | | | | | | | | |
| legaldesign | ● | ○ | ● | ● |  |  |  |  |  |  | ◐ |  |  |  |  | ● |
| lq-start |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| regulatory | ● |  | ◐ | ● | ○ | ○ |  |  |  | ○ | ◐ |  |  |  |  |  |
| timenarratives | ○ |  | ○ | ○ | ○ |  |  |  |  |  |  | ○ |  | ○ |  |  |
| wiki | ● |  | ● | ● | ● | ● |  |  |  |  |  |  | ◐ |  |  | ◐ |
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
| playbook-builder | ● |  | ● | ● |  | ● |  |  |  |  | ◐ | ◐ |  |  |  |  |
| playbook-review | ◐ |  | ● | ◐ |  | ◐ |  |  |  |  | ◐ | ◐ |  |  |  |  |
| read-redline | ● |  | ● | ● |  |  |  |  |  |  | ◐ | ● |  |  |  | ● |
| sigpack | ● |  | ● | ● |  | ◐ |  |  |  |  |  | ● |  |  |  |  |

Levels: ● required, ◐ degradable, ○ optional, blank not used. A cell shows the strongest level of a code and its facets. Auxiliary codes and facets:

| Skill | HASH | SKILLDIR | INVOKE |
|---|---|---|---|
| client-update | ○ |  |  |
| depositions | ○ |  |  |
| document-discovery |  | ◐ |  |
| legaldesign |  | ◐ asset |  |
| my-lq-moment |  | ◐ asset |  |
| organize-case-docs | ● |  |  |
| wiki | ◐ |  |  |

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

## 6. Capability by capability

The same data read the other way: for each capability, which skills need it. Upstream first; the Cowork count follows in brackets.

**TOOLS - Tool execution.** ● 19 (16) · ◐ 9 (7) · ○ 3 (7)

- Required upstream: `cite-check`, `closing-bible`, `closing-checklist`, `conform`, `diligence`, `docreview`, `document-discovery`, `legaldesign`, `lq-apply`, `lq-connect`, `lq-reflect`, `lq-start`, `my-lq-moment`, `organize-case-docs`, `playbook-builder`, `playbook-review`, `read-redline`, `sigpack`, `wiki`
- Degradable upstream: `client-update`, `definition-check`, `legalquants`, `lq-ask`, `new-matter`, `pressuretest`, `regulatory`, `timenarratives`, `writing`
- Optional upstream: `correspondence`, `depositions`, `lq-mirror`

**MCP - MCP connection.** ● 0 (0) · ◐ 1 (0) · ○ 14 (9)

- Degradable upstream: `lq-ask`
- Optional upstream: `cite-check`, `client-update`, `closing-checklist`, `conform`, `correspondence`, `definition-check`, `depositions`, `document-discovery`, `legaldesign`, `new-matter`, `organize-case-docs`, `regulatory`, `timenarratives`, `writing`

**IN - Read supplied files.** ● 16 (15) · ◐ 6 (8) · ○ 5 (5)

- Required upstream: `cite-check`, `closing-bible`, `closing-checklist`, `conform`, `diligence`, `docreview`, `document-discovery`, `legaldesign`, `lq-reflect`, `organize-case-docs`, `playbook-builder`, `playbook-review`, `pressuretest`, `read-redline`, `sigpack`, `wiki`
- Degradable upstream: `client-update`, `correspondence`, `definition-check`, `depositions`, `my-lq-moment`, `regulatory`
- Optional upstream: `lq-apply`, `lq-ask`, `new-matter`, `timenarratives`, `writing`

**OUT - Hand back files.** ● 14 (14) · ◐ 5 (6) · ○ 8 (5)

- Required upstream: `cite-check`, `closing-bible`, `closing-checklist`, `conform`, `diligence`, `docreview`, `document-discovery`, `legaldesign`, `lq-apply`, `my-lq-moment`, `playbook-builder`, `playbook-review`, `read-redline`, `sigpack`
- Degradable upstream: `definition-check`, `new-matter`, `organize-case-docs`, `pressuretest`, `timenarratives`
- Optional upstream: `client-update`, `correspondence`, `depositions`, `lq-mirror`, `lq-reflect`, `regulatory`, `wiki`, `writing`

**FS - Real filesystem.** ● 15 (3) · ◐ 7 (3) · ○ 2 (5)

- Required upstream: `cite-check`, `closing-bible`, `closing-checklist`, `conform`, `diligence`, `docreview`, `legaldesign`, `lq-reflect`, `lq-start`, `organize-case-docs`, `playbook-builder`, `playbook-review`, `read-redline`, `sigpack`, `wiki`
- Degradable upstream: `definition-check`, `document-discovery`, `legalquants`, `my-lq-moment`, `new-matter`, `pressuretest`, `regulatory`
- Optional upstream: `lq-apply`, `timenarratives`

**PERSIST - Storage that outlives the session.** ● 5 (3) · ◐ 3 (5) · ○ 18 (8)

- Required upstream: `lq-reflect`, `organize-case-docs`, `playbook-builder`, `sigpack`, `wiki`
- Degradable upstream: `legalquants`, `lq-apply`, `playbook-review`
- Optional upstream: `cite-check`, `client-update`, `closing-bible`, `closing-checklist`, `correspondence`, `definition-check`, `depositions`, `diligence`, `docreview`, `document-discovery`, `legaldesign`, `lq-mirror`, `my-lq-moment`, `new-matter`, `read-redline`, `regulatory`, `timenarratives`, `writing`

**EXEC - Run bundled scripts.** ● 5 (0) · ◐ 19 (0) · ○ 3 (0)

- Required upstream: `closing-bible`, `conform`, `lq-reflect`, `lq-start`, `my-lq-moment`
- Degradable upstream: `cite-check`, `closing-checklist`, `definition-check`, `diligence`, `docreview`, `legaldesign`, `legalquants`, `lq-apply`, `lq-ask`, `lq-connect`, `organize-case-docs`, `playbook-builder`, `playbook-review`, `pressuretest`, `read-redline`, `regulatory`, `sigpack`, `timenarratives`, `wiki`
- Optional upstream: `client-update`, `document-discovery`, `lq-mirror`

**BIN - External executables.** ● 0 (0) · ◐ 4 (0) · ○ 8 (0)

- Degradable upstream: `closing-bible`, `my-lq-moment`, `read-redline`, `sigpack`
- Optional upstream: `cite-check`, `closing-checklist`, `definition-check`, `diligence`, `docreview`, `document-discovery`, `legaldesign`, `organize-case-docs`

**NET - Fetch a URL.** ● 1 (0) · ◐ 5 (2) · ○ 8 (2)

- Required upstream: `lq-connect`
- Degradable upstream: `document-discovery`, `lq-apply`, `lq-ask`, `regulatory`, `writing`
- Optional upstream: `cite-check`, `client-update`, `closing-checklist`, `conform`, `correspondence`, `depositions`, `legaldesign`, `wiki`

**SEARCH - Web search.** ● 0 (0) · ◐ 4 (4) · ○ 4 (6)

- Degradable upstream: `cite-check`, `document-discovery`, `regulatory`, `writing`
- Optional upstream: `client-update`, `closing-checklist`, `correspondence`, `depositions`

**VISION - See rendered pages.** ● 1 (0) · ◐ 8 (10) · ○ 2 (0)

- Required upstream: `sigpack`
- Degradable upstream: `closing-bible`, `closing-checklist`, `diligence`, `docreview`, `legaldesign`, `playbook-builder`, `playbook-review`, `read-redline`
- Optional upstream: `document-discovery`, `organize-case-docs`

**DOCX - Word OOXML structure.** ● 1 (3) · ◐ 4 (4) · ○ 3 (5)

- Required upstream: `read-redline`
- Degradable upstream: `closing-checklist`, `definition-check`, `playbook-builder`, `playbook-review`
- Optional upstream: `document-discovery`, `sigpack`, `timenarratives`

**SUB - Isolated workers.** ● 0 (0) · ◐ 10 (1) · ○ 4 (0)

- Degradable upstream: `cite-check`, `client-update`, `conform`, `definition-check`, `diligence`, `docreview`, `lq-reflect`, `playbook-review`, `sigpack`, `wiki`
- Optional upstream: `closing-bible`, `closing-checklist`, `pressuretest`, `regulatory`

**SESSION - Conversation transcripts.** ● 2 (1) · ◐ 1 (0) · ○ 1 (2)

- Required upstream: `lq-reflect`, `my-lq-moment`
- Degradable upstream: `timenarratives`
- Optional upstream: `wiki`

**SCHED - Background or scheduled runs.** ● 0 (0) · ◐ 0 (0) · ○ 3 (1)

- Optional upstream: `diligence`, `docreview`, `wiki`

**HTML - Interactive HTML round trip.** ● 3 (5) · ◐ 5 (2) · ○ 1 (2)

- Required upstream: `diligence`, `docreview`, `legaldesign`
- Degradable upstream: `conform`, `definition-check`, `document-discovery`, `pressuretest`, `wiki`
- Optional upstream: `cite-check`

**HASH - File digest by the host.** ● 1 (1) · ◐ 0 (1) · ○ 2 (2)

- Required upstream: `organize-case-docs`
- Optional upstream: `client-update`, `depositions`

**SKILLDIR - Skill folder on disk.** ● 5 (0) · ◐ 18 (3) · ○ 2 (0)

- Required upstream: `closing-bible`, `conform`, `lq-reflect`, `lq-start`, `my-lq-moment`
- Degradable upstream: `cite-check`, `definition-check`, `diligence`, `docreview`, `document-discovery`, `legaldesign`, `legalquants`, `lq-apply`, `lq-ask`, `lq-connect`, `playbook-builder`, `playbook-review`, `pressuretest`, `read-redline`, `regulatory`, `sigpack`, `timenarratives`, `wiki`
- Optional upstream: `closing-checklist`, `lq-mirror`

**INVOKE - Call a skill by name.** ● 9 (0) · ◐ 0 (0) · ○ 0 (0)

- Required upstream: `legalquants`, `lq-apply`, `lq-ask`, `lq-connect`, `lq-mirror`, `lq-start`, `my-lq-moment`, `pressuretest`, `timenarratives`

## 7. Skill by skill

Each entry gives the skill's purpose in its own words, its levels under both profiles with the probes that decide each one, the exact runtime its scripts need, and - for every degradable level - the skill's own words for what happens without it. Upstream references link to the pinned commit.

### Core

#### legaldesign

*Create one polished, editable, evidence-grounded HTML explanation of supplied or completed legal work.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| MCP | ○ | ○ | P15 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| FS | ● |  | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| NET | ○ |  | P12 |
| VISION | ◐ | ◐ | P4 |
| HTML | ● | ● | P20 |
| SKILLDIR | ◐ |  | P21 |
| `SKILLDIR:asset` | ◐ | ◐ | P7 |

**Script runtime (upstream):** Python ≥3.10.

**Without its degradable capabilities (upstream):**

- **EXEC**: “Where script execution is unavailable, host-native tools must provide equivalent safe serialization, validation, and the finished shared runtime; do not claim unperformed checks.” ([legaldesign/references/build.md:104](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/legaldesign/references/build.md#L104))
- **VISION**: “Correct failures and rerun affected/dependent checks; disclose anything unavailable. Do not claim a browser check from code inspection. (Multi-viewport and interaction QA is reported as not done.)” ([legaldesign/references/qa.md:3](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/legaldesign/references/qa.md#L3))
- **SKILLDIR**: “scaffold.py reads assets/, schemas/ and DESIGN.md relative to the skill folder and exhibit.py sits beside it; without them the same host-native-tools fallback as EXEC applies (equivalent serialization, validation and the shared runtime, no unperformed checks claimed).” ([legaldesign/references/build.md:104](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/legaldesign/references/build.md#L104))
- **SKILLDIR:asset**: “Host-native tools must provide the finished shared runtime; do not claim unperformed checks.” ([legaldesign/SKILL.md:18](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/legaldesign/SKILL.md#L18))

**Without its degradable capabilities (Cowork card):**

- **VISION**: “You do not have a real browser at several window sizes. Do every check you can by reading the file and looking at the preview, and list the rest in the handoff as outstanding, by name.” (Cowork card `legaldesign`, built references/qa.md line 7)
- **SKILLDIR:asset**: “Nothing checks that the finished page truly follows the structure of the packaged template or component the skill says it used, so a page that looks plausible but does not really follow that structure would read as correct.” (Cowork card `legaldesign`, known issue KI-legaldesign-3 (“Whether a packaged template actually shaped the output is unverified”))

**What the Cowork adaptation changed:** Removed scaffold.py/exhibit.py, the JSON schemas, blank templates and the cite-check adapter: the model now writes the spec and the single self-contained HTML itself and the preview pane renders it, so EXEC, BIN, NET and the SKILLDIR/HASH needs are gone; authentic source clips exist only if the lawyer supplies one (the exhibit sha256 fields were dropped from the contract). Packaged assets/*.html are filled examples the model only reads. Optional licensed service kept as a one-line mention (SKILL.md:48).

#### lq-start

*Ask which CODEX for Legal skill fits the work in front of you.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● |  | P25 |
| FS | ● |  | P16 |
| EXEC | ● |  | P1 |
| SKILLDIR | ● |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.8.

**What the Cowork adaptation changed:** Replaced the live catalog.py scan (EXEC, FS over the host plugin tree, SKILLDIR sibling walk) with a static references/map.md that the model only reads, so no host capability beyond baseline chat and skill loading is needed. The built frontmatter has no disable-model-invocation, so INVOKE is dropped; the card says deliberate selection is the Sources picker.

#### regulatory

*Regulatory research, refreshing earlier research, jurisdiction comparison and legality checks built on primary sources — retrieves the instrument from its official publisher, proves which version it is, and quotes only from the bytes it...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ● | P25 |
| MCP | ○ |  | P15 |
| IN | ◐ | ◐ | P26 |
| OUT | ○ | ● | P27 |
| FS | ◐ | ○ | P16 |
| PERSIST | ○ | ○ | P2 |
| EXEC | ◐ |  | P1 |
| NET | ◐ |  | P12, P18 |
| SEARCH | ◐ | ○ | P6 |
| VISION |  | ◐ | P4 |
| SUB | ○ |  | P19 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.8.

**Without its degradable capabilities (upstream):**

- **IN**: “For PDF source text, use this cascade: the host's built-in document extraction or a separately available open-source extractor, then a firm-approved OCR/document service; feed the resulting text to extract_provisions.py. User-supplied official downloads may be checked with host tools but must retain origin and version evidence.” ([regulatory/SKILL.md:571](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/regulatory/SKILL.md#L571))
- **FS**: “Without Python, network or file retention, perform the same checks with available host tools, or use the provisional route.” ([regulatory/SKILL.md:612](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/regulatory/SKILL.md#L612))
- **EXEC**: “Scripts are optional host capabilities. Without Python/network/file retention, perform the same checks using available host tools and record their coverage; if equivalent checks cannot be completed, use the provisional route. Never claim script verification when the scripts did not run.” ([regulatory/SKILL.md:612](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/regulatory/SKILL.md#L612))
- **NET**: “If the official source cannot be fetched or verified, the answer begins 'provisional and unverified' for the affected points.” ([regulatory/SKILL.md:593](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/regulatory/SKILL.md#L593))
- **SEARCH**: “Search is only for finding the instrument; the user may supply a link (used immediately), and for an unmapped jurisdiction local counsel may know the publisher off the top of their head, so one question saves the exercise.” ([regulatory/SKILL.md:96](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/regulatory/SKILL.md#L96))
- **SKILLDIR**: “The eight scripts import sibling integrity.py and read references/jurisdictions/ and references/discovery.md by relative path; without the folder on disk the same fallback as EXEC applies (equivalent checks with host tools, else the provisional route).” ([regulatory/SKILL.md:612](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/regulatory/SKILL.md#L612))

**Without its degradable capabilities (Cowork card):**

- **IN**: “If they would rather not go and get it, say plainly what that costs: the answer comes back under the provisional heading of the delivery gate, because nothing will have been read from the publisher.” (Cowork card `regulatory`, built SKILL.md line 164)
- **VISION**: “Some publishers serve older instruments as scans with no text layer.” (Cowork card `regulatory`, known issue KI-regulatory-2 (“A scanned or image-only publisher PDF stops the run”))

**What the Cowork adaptation changed:** Dropped all eight scripts and the fetch: the lawyer downloads the publisher's document into the Input folder and a provenance block (publisher, address, date, lawyer's attestation) replaces the fetch record and the SHA-256, so NET, EXEC, SKILLDIR and HASH are gone; version, provision extraction, quote re-finding and receipt audit are now self-performed by the model and stated as such. The note, provision list and verification record are always written to the Output folder (OUT); FS is only the optional offer to make a dated folder (SKILL.md:84); search or browsing tools may only help find the address and are never quoted (SKILL.md:148, :213).

#### timenarratives

*Draft concise time-entry narratives from the lawyer's work in the current conversation, selected related chats, LQ skill exchanges, and supplied accounts, documents or expressly selected folders.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ○ | P25 |
| MCP | ○ |  | P15 |
| IN | ○ | ○ | P26 |
| OUT | ◐ | ○ | P27 |
| FS | ○ | ○ | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ◐ |  | P1 |
| DOCX | ○ | ○ | P3 |
| SESSION | ◐ |  | P11 |
| `SESSION:resume` |  | ○ | P5 |
| SKILLDIR | ◐ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **OUT**: “Return an in-memory, unposted draft; the machine-readable JSON/Markdown artifacts are published only after validation, and without the scripts none are published (the draft is shown in chat as an unvalidated preview).” ([timenarratives/SKILL.md:48](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/timenarratives/SKILL.md#L48))
- **EXEC**: “If the bundled scripts cannot run, label the result Unvalidated preview. Do not call it copy-ready or final, do not publish machine-readable artifacts, and state which checks could not run.” ([timenarratives/SKILL.md:48](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/timenarratives/SKILL.md#L48))
- **SESSION**: “Where retrieval is unavailable, use the current context and any explicitly selected export or brief account the lawyer supplies. Do not pretend memory or a summary is a complete transcript; state material coverage gaps.” ([timenarratives/SKILL.md:18](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/timenarratives/SKILL.md#L18))
- **SKILLDIR**: “About 40 scripts import each other and read ../schemas by relative path; if they cannot run from the skill folder the result is labelled Unvalidated preview and no machine-readable artifacts are published.” ([timenarratives/SKILL.md:48](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/timenarratives/SKILL.md#L48))

**What the Cowork adaptation changed:** Removed the 40-script pipeline, schemas and related-chat retrieval (SESSION and EXEC gone; SKILLDIR and HASH no longer needed): every draft is shown in the reply as an Unvalidated preview with model-copied exact quotes. A Markdown or Word file is written only on request (Word through the built-in Word skill), so OUT, DOCX and hence TOOLS are optional. The built frontmatter has no disable-model-invocation, so INVOKE is dropped.

#### wiki

*Build, explore, and maintain a lawyer's personal legal wiki: linked, source-grounded Markdown notes that preserve reusable law and method, never matter facts.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ○ | ● | P27 |
| FS | ● | ● | P16 |
| PERSIST | ● | ● | P2 |
| EXEC | ◐ |  | P1 |
| NET | ○ |  | P12 |
| SUB | ◐ | ◐ | P19 |
| SESSION | ○ |  | P11 |
| SCHED | ○ |  | P13 |
| HTML | ◐ | ◐ | P20 |
| HASH |  | ◐ | P17 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **EXEC**: “If local execution is unavailable, use the Markdown workflow. (Browse: when scripts are unavailable, read the eligible Markdown notes directly.)” ([wiki/SKILL.md:29](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/wiki/SKILL.md#L29))
- **SUB**: “Layer 3 is the adversarial reader panel run in a fresh context; all three layers fail closed, and a gate that cannot reach a verdict returns a failure, not a pass (the note is parked, never landed).” ([wiki/references/gate_prompts.md:15](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/wiki/references/gate_prompts.md#L15))
- **HTML**: “Use another native artifact capability if needed, or Markdown links/a table when visual rendering is unavailable.” ([wiki/SKILL.md:105](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/wiki/SKILL.md#L105))
- **SKILLDIR**: “Helper files are resolved relative to the directory holding the loaded SKILL.md (wiki.py plus wiki_retrieval.py and wiki_wording.py); if local execution is unavailable, use the Markdown workflow.” ([wiki/SKILL.md:22](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/core/wiki/SKILL.md#L22))

**Without its degradable capabilities (Cowork card):**

- **SUB**: “All three layers fail closed. A gate that cannot reach a verdict returns a failure, not a pass. (Layer 3, the adversarial reader panel, is still specified as run in a fresh context.)” (Cowork card `wiki`, built references/gate_prompts.md line 19)
- **HTML**: “Build it as one index file the preview pane renders: Markdown for a plain collection, or a single self-contained HTML page when search and filters would genuinely help.” (Cowork card `wiki`, built SKILL.md line 118)
- **HASH**: “Authorised non-matter local material: record a content hash when available (and the wording record's sha256 of the block); with no way to hash, the block is compared character by character and, if exactness cannot be verified, the card says so.” (Cowork card `wiki`, built references/source_policy.md line 11)

**What the Cowork adaptation changed:** Dropped wiki.py and the .wiki sidecar (hash chain, lock, versions, automation): the wiki is a plain folder the lawyer names, log.md is the only record, notes are withdrawn not deleted, Browse builds a Markdown or single-file HTML index, and automation (SCHED) is stated as absent. Gaps: gate_prompts.md:15 and :11 still describe layer 1 as deterministic checks in code that no longer exist, and positions.md:41 still asks for a sha256 of each wording block with no way to compute it.

### Companion

#### legalquants

*Your journey with AI as a lawyer, one next step at a time.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ◐ | P25 |
| IN |  | ◐ | P26 |
| FS | ◐ | ◐ | P16 |
| PERSIST | ◐ | ○ | P2 |
| EXEC | ◐ |  | P1 |
| SKILLDIR | ◐ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **TOOLS**: “No explicit tool fallback. Closest: a verb that is not installed is not an option; say the next step in plain words instead and move on.” ([legalquants/SKILL.md:51-54](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/legalquants/SKILL.md#L51-L54))
- **FS**: “No explicit fallback for an unreadable ~/.lq. Closest: store status returning exists:false is 'a normal answer, never an error'.” ([legalquants/SKILL.md:46](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/legalquants/SKILL.md#L46))
- **PERSIST**: “'{"exists": false}' is a normal answer, never an error (missing store is expected on a fresh machine).” ([legalquants/SKILL.md:46](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/legalquants/SKILL.md#L46))
- **EXEC**: “No explicit fallback for missing scripts. Closest: exists:false is normal, and only skills that appear in catalog output may be offered; otherwise say the next step in plain words.” ([legalquants/SKILL.md:46,51-54](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/legalquants/SKILL.md#L46))
- **SKILLDIR**: “Sibling scripts (onboarding.py, ../lq-reflect profile_store.py, ../lq-start catalog.py) are called by relative path. Same closest wording as EXEC; the SKILL.md states no fallback for an unreachable skill folder.” ([legalquants/SKILL.md:38-54](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/legalquants/SKILL.md#L38-L54))

**Without its degradable capabilities (Cowork card):**

- **TOOLS**: “If they say the note is already in their Cowork folder, ask what it is called, look for it, and say in one line whether you found it.” (Cowork card `legalquants`, built SKILL.md line 58-60)
- **IN**: “With nothing to go on, ask one question rather than guess.” (Cowork card `legalquants`, built SKILL.md line 68-69)
- **FS**: “Look for the named note and say in one line whether you found it; name anything looked for and not found before saying where they are.” (Cowork card `legalquants`, built SKILL.md line 58-60,65-68)

**What the Cowork adaptation changed:** Removed the onboarding marker, ~/.lq profile, store counters and catalog script (no scripts, no PERSIST, no SKILLDIR); it now works from the conversation plus an attached lqplaybook.md or note and states what it had. Frontmatter has no disable-model-invocation, so no INVOKE.

#### lq-apply

*Put your experience into words: drafts your LQ application, a CV, or a public profile from your saved journey and the sources you choose — real evidence, your words to finish.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ○ | ◐ | P26 |
| OUT | ● | ● | P27 |
| FS | ○ | ◐ | P16 |
| PERSIST | ◐ | ○ | P2 |
| EXEC | ◐ |  | P1 |
| NET | ◐ | ○ | P12 |
| DOCX |  | ○ | P3 |
| SKILLDIR | ◐ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **PERSIST**: “Empty or missing store: say so honestly and start one now, then compile from what they give you in this session. Never send them away to wait.” ([lq-apply/SKILL.md:64-67](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-apply/SKILL.md#L64-L67))
- **EXEC**: “already_shown, another_session_is_showing_it or any error -> straight to the task. The task is never gated on this.” ([lq-apply/SKILL.md:33-35](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-apply/SKILL.md#L33-L35))
- **NET**: “Fetch the form's current fields when reachable; when unreachable, say the draft is provisional - never claim a fixed field count or an exact form match.” ([lq-apply/SKILL.md:98-101](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-apply/SKILL.md#L98-L101))
- **SKILLDIR**: “Sibling scripts ../legalquants/scripts/onboarding.py and ../lq-reflect/scripts/profile_store.py; failure path is 'any error -> straight to the task' plus the short-conversation source when nothing else exists.” ([lq-apply/SKILL.md:33-35,62](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-apply/SKILL.md#L33-L35))

**Without its degradable capabilities (Cowork card):**

- **IN**: “Nothing kept, nothing attached: say so honestly and compile from what they give you in this session. A normal way to run this, not a degraded one.” (Cowork card `lq-apply`, built SKILL.md line 72-74)
- **FS**: “If they say it is already in their Cowork folder, ask what it is called, look for it, and say in one line whether you found it; never carry on as though you had.” (Cowork card `lq-apply`, built SKILL.md line 49-51)

**What the Cowork adaptation changed:** Dropped the onboarding marker, ~/.lq store reads, the live assess.legalquants.com fetch and the whole application format; now drafts a CV or profile from attached files or conversation and writes the draft plus an evidence-notes file to the Output folder (Word doc via the host Word skill on request). OUT rated R because the card names an Output file as where the draft goes and gives no fallback if it cannot be written, though the draft is also shown verbatim in chat.

#### lq-ask

*Ask what LegalQuants has said in public: answers from the published Insights essays, the free weekly digest and the public repositories, with a link to each page it read; member discussions only through an LQ member connection, and it sa...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ○ | P25 |
| MCP | ◐ |  | P15 |
| IN | ○ |  | P26 |
| EXEC | ◐ |  | P1 |
| NET | ◐ |  | P12 |
| SEARCH |  | ○ | P6 |
| SKILLDIR | ◐ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **TOOLS**: “If lq-mcp is not available: say so in one plain line ('the live corpus isn't reachable from here') and work from the public surfaces in references/sources.md instead.” ([lq-ask/SKILL.md:61-66](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-ask/SKILL.md#L61-L66))
- **MCP**: “If it is not available: say so in one plain line and work from the public surfaces instead. Never pretend a citation from that file is a live query result.” ([lq-ask/SKILL.md:61-66](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-ask/SKILL.md#L61-L66))
- **EXEC**: “onboarding.py: any error -> straight to the task. evidence.py: no resolution -> cite the build's title and description only, with no invented profile link.” ([lq-ask/SKILL.md:37-39,77-80](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-ask/SKILL.md#L37-L39))
- **NET**: “Name the source sets actually searched and any that were unavailable. Unavailable is said, not implied. Never claim a source you did not retrieve.” ([lq-ask/SKILL.md:82-85](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-ask/SKILL.md#L82-L85))
- **SKILLDIR**: “Scripts/source_access.py plus ../legalquants/scripts/evidence.py and onboarding.py by relative path; same wording as EXEC (error -> straight to the task; no resolution -> title and description only).” ([lq-ask/SKILL.md:37-39,73-80](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-ask/SKILL.md#L37-L39))

**What the Cowork adaptation changed:** Replaced the live lq-mcp, GitHub and builds-directory lookups and all scripts with a dated static library in references/sources.md that the model only reads; asks nothing of the host beyond chat. Deep Research is mentioned only as something the user may ask for themselves. No disable-model-invocation in frontmatter, so no INVOKE.

#### lq-connect

*Find a person, not an answer: matches what you're working on to LegalQuants members with public profiles — real practitioners who've been through it — and hands you their profile links.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ◐ | P25 |
| IN |  | ○ | P26 |
| EXEC | ◐ |  | P1 |
| NET | ● |  | P12 |
| `SEARCH:org` |  | ◐ | P14 |
| SKILLDIR | ◐ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **EXEC**: “No hit anywhere -> the existing known-for/works line stands on its own, silently; this step never stalls the hand-over and is never surfaced as a gap.” ([lq-connect/SKILL.md:91-94](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-connect/SKILL.md#L91-L94))
- **SKILLDIR**: “Calls ../legalquants/scripts/evidence.py and onboarding.py by relative path; failure paths are 'any error -> straight to the task' and the no-hit line above.” ([lq-connect/SKILL.md:33-35,82-94](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-connect/SKILL.md#L33-L35))

**Without its degradable capabilities (Cowork card):**

- **TOOLS**: “Nobody fits well? Say so plainly, say what you searched and what you could not see, and suggest the search the lawyer could run themselves.” (Cowork card `lq-connect`, built SKILL.md line 94-97)
- **SEARCH**: “Nobody fits well? Say so plainly, say what you searched and what you could not see. A document this session cannot open is not evidence: name it as unopened and move on. A brought list is a second pool.” (Cowork card `lq-connect`, built SKILL.md line 68-71,78-81,94-97)
- **SEARCH:org**: “Nobody fits well? Say so plainly, say what you searched and what you could not see. A document this session cannot open is not evidence: name it as unopened and move on. A brought list is a second pool.” (Cowork card `lq-connect`, built SKILL.md line 68-71,78-81,94-97)

**What the Cowork adaptation changed:** Replaced the public legalquants.com directory fetch and evidence.py excerpts with a hand-off to the host Enterprise Search skill over the organisation's own material, plus an optional directory or attendee list the lawyer attaches. SEARCH rated D (not R) because the brought-list pool and the honest-miss answer remain when search is unavailable; the card gives no wording specific to a missing Enterprise Search skill.

#### lq-mirror

*A short, honest reading of where you stand with AI as a lawyer — your archetype, in language that respects you.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ○ | ○ | P25 |
| OUT | ○ | ○ | P27 |
| PERSIST | ○ |  | P2 |
| EXEC | ○ |  | P1 |
| SKILLDIR | ○ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11.

**What the Cowork adaptation changed:** Removed the onboarding marker, store save door and live catalog ending; the twelve-question conversation is pure chat and the summary is shown in the reply. OUT O only because, if asked, the summary is handed over as a note they can save to their own folder (SKILL.md:62-63), which the host may realise as an Output file. No INVOKE: built frontmatter lacks disable-model-invocation.

#### lq-reflect

*Look at how you're actually working with AI: a weekly retrospective on your sessions, or help right now when a session has gone sideways.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ○ | P25 |
| IN | ● | ○ | P26 |
| OUT | ○ | ○ | P27 |
| FS | ● | ○ | P16 |
| PERSIST | ● | ○ | P2 |
| EXEC | ● |  | P1 |
| SUB | ◐ |  | P19 |
| SESSION | ● | ○ | P11 |
| SKILLDIR | ● |  | P21 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **SUB**: “Second read, where the host has parallel workers. Without workers, skip this and say so in one line; the debrief is complete without it.” ([lq-reflect/SKILL.md:199-205](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/lq-reflect/SKILL.md#L199-L205))

**What the Cowork adaptation changed:** Dropped the ~/.lq store, transcript scanners, manifests, window mode and the subagent second read; reviews only this conversation plus attached or Input-folder files, and on yes writes one dated Markdown note to the Output folder for the lawyer to bring back. Everything host-side is optional because the review runs on conversation text alone; no cross-session PERSIST or SESSION is asked of the host. No INVOKE (upstream is implicit too).

#### my-lq-moment

*Did something genuinely impressive just happen in this session?*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ◐ | ◐ | P26 |
| OUT | ● | ◐ | P27 |
| FS | ◐ | ○ | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ● |  | P1 |
| BIN | ◐ |  | P1 |
| SESSION | ● | ● | P11 |
| HTML |  | ◐ | P20 |
| SKILLDIR | ● |  | P21 |
| `SKILLDIR:asset` | ● | ◐ | P7 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.11; one of `rsvg-convert`, `magick`, `convert`, `inkscape`, `chromium`, `chromium-browser`, `google-chrome`.

**Without its degradable capabilities (upstream):**

- **IN**: “If the host cannot supply real evidence (some hosts expose little), say so plainly: an automatic insufficient evidence outcome, ending in refusal, not in a lower bar.” ([my-lq-moment/SKILL.md:69-71](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/my-lq-moment/SKILL.md#L69-L71))
- **FS**: “If the cover template file is missing, the skill cannot produce a cover: say so and give the approved text.” ([my-lq-moment/assets/README.md:6-7](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/my-lq-moment/assets/README.md#L6-L7))
- **BIN**: “If no PNG: ask to re-run with elevated execution; only if that also fails, say so, hand over the SVG and the approved text, and give the one-line conversion.” ([my-lq-moment/SKILL.md:187-195](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/companion/my-lq-moment/SKILL.md#L187-L195))

**Without its degradable capabilities (Cowork card):**

- **IN**: “Say which of those you can actually see here, and name anything on that list you cannot see rather than assuming it: what you cannot see is not evidence.” (Cowork card `my-lq-moment`, built SKILL.md line 55-57)
- **OUT**: “The cover is the page this skill builds on the template, or the announced plain card, or not at all: never a placeholder, never a PNG claimed rather than produced.” (Cowork card `my-lq-moment`, built SKILL.md line 290-292)
- **HTML**: “Offer the third form, one square slide through the built-in PowerPoint skill, if they would rather have that; give the one-line conversion to a square image.” (Cowork card `my-lq-moment`, built SKILL.md line 202-207)
- **SKILLDIR**: “If the packaged template does not come through into the page, build a plain styled card on a near-black ground and say in one line that the template image is not in it. If the file is missing, say so and give the approved text.” (Cowork card `my-lq-moment`, built SKILL.md line 199-203)
- **SKILLDIR:asset**: “If the packaged template does not come through into the page, build a plain styled card on a near-black ground and say in one line that the template image is not in it. If the file is missing, say so and give the approved text.” (Cowork card `my-lq-moment`, built SKILL.md line 199-203)

**What the Cowork adaptation changed:** render_cover.py and the SVG-to-PNG rasteriser are gone; the cover is now an HTML page written to the Output folder on top of the bundled cover-template.png and shown in the preview pane, with a plain-card and a PowerPoint-slide fallback, and the one kept line is handed over in the reply instead of saved through the store. SESSION stays R: the card still refuses (insufficient evidence) if the host cannot show current-session evidence. No INVOKE: built frontmatter lacks disable-model-invocation.

### Litigation

#### cite-check

*Verify supplied citations, check authorities, and detect hallucinated case law before filing.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| MCP | ○ |  | P15 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| FS | ● |  | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| NET | ○ |  | P12 |
| SEARCH | ◐ | ◐ | P6 |
| SUB | ◐ |  | P19 |
| HTML | ○ | ○ | P20 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.9.

**Without its degradable capabilities (upstream):**

- **EXEC**: “If the environment does not allow you to run the script or you encounter errors that cannot be quickly fixed, gracefully degrade to assigning units to native workers.” ([cite-check/SKILL.md:54](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/cite-check/SKILL.md#L54))
- **SEARCH**: “Report one simple outcome: the environment could not search; the search did not find the case and it may be hallucinated; or the case was found but was not supplied.” ([cite-check/SKILL.md:27](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/cite-check/SKILL.md#L27))
- **SUB**: “If the packaged script is unavailable on a host, keep the same one-unit assignments with host workers or process those assignments one at a time.” ([cite-check/SKILL.md:38](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/cite-check/SKILL.md#L38))
- **SKILLDIR**: “If local scripts are unavailable, render the same validated report data with the supplied template using host-native capabilities (the scripts and template are in the skill folder).” ([cite-check/SKILL.md:56](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/cite-check/SKILL.md#L56))

**Without its degradable capabilities (Cowork card):**

- **SEARCH**: “Report one simple outcome: no search capability was available; the search did not find the case and it may be hallucinated; or the case was found but was not supplied.” (Cowork card `cite-check`, built SKILL.md line 31)

**What the Cowork adaptation changed:** The scripted per-unit fan-out, probe and aggregate_report.py are gone: the card reviews every unit itself in one conversation, applies the amber colour rule to its own results and fills the report template by hand (SUB and EXEC no longer asked). Case-existence search is routed to the host's Deep Research and Enterprise Search skills, and the report is saved as an HTML file for the preview pane.

#### client-update

*Prepare evidence-first litigation matter, event, portfolio, or outside-counsel status updates that separate verified developments from analysis, recommendations, and decisions, and make deadlines, budgets, exposure, risks, owners, source...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ○ | P25 |
| MCP | ○ | ○ | P15 |
| IN | ◐ | ◐ | P26 |
| OUT | ○ | ○ | P27 |
| PERSIST | ○ | ○ | P2 |
| EXEC | ○ |  | P1 |
| NET | ○ |  | P12 |
| SEARCH | ○ | ○ | P6 |
| DOCX |  | ○ | P3 |
| SUB | ◐ |  | P19 |
| HASH | ○ | ○ | P17 |

**Without its degradable capabilities (upstream):**

- **TOOLS**: “The plain Markdown/table workflow is complete without external tools.” ([client-update/SKILL.md:50](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/client-update/SKILL.md#L50))
- **IN**: “If a source is missing, unreadable, conflicting, or outside coverage, say so.” ([client-update/SKILL.md:38](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/client-update/SKILL.md#L38))
- **SUB**: “When the host offers parallel workers, divide only independent sources or matters ... otherwise perform the same steps sequentially.” ([client-update/SKILL.md:58](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/client-update/SKILL.md#L58))

**Without its degradable capabilities (Cowork card):**

- **IN**: “If a source is missing, unreadable, conflicting, or outside coverage, say so.” (Cowork card `client-update`, built SKILL.md line 40)

**What the Cowork adaptation changed:** Parallel-worker (SUB) language and the temporary dataset deleted on completion were replaced by sequential work in the session and an Output-folder working table that is never described as removed; Word, Excel or PowerPoint versions are left to the built-in skills. Method is otherwise unchanged and still runs on plain chat.

#### correspondence

*Triage inbound and draft source-grounded U.S.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ○ | ○ | P25 |
| MCP | ○ | ○ | P15 |
| IN | ◐ | ◐ | P26 |
| OUT | ○ |  | P27 |
| PERSIST | ○ |  | P2 |
| NET | ○ |  | P12 |
| SEARCH | ○ | ○ | P6 |

**Without its degradable capabilities (upstream):**

- **IN**: “If the user supplies only a summary, distinguish the summary from the underlying record and limit the draft accordingly.” ([correspondence/SKILL.md:48](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/correspondence/SKILL.md#L48))

**Without its degradable capabilities (Cowork card):**

- **IN**: “If the user supplies only a summary, distinguish the summary from the underlying record and limit the draft accordingly.” (Cowork card `correspondence`, built SKILL.md line 50)

**What the Cowork adaptation changed:** The temporary JSON dataset deleted on completion became an in-session working table, the ABA, FRCP and FRE guardrails moved into references/professional-guardrails.md, and the no-send line now names the Email skill or the lawyer's mail client as the separate sending step. The draft stays in chat; nothing is sent.

#### depositions

*Prepare, conduct, and close the loop on a deposition using claims, elements, chronology, exhibits, admissions, impeachment, ethics, and transcript evidence.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ○ | ○ | P25 |
| MCP | ○ | ○ | P15 |
| IN | ◐ | ◐ | P26 |
| OUT | ○ | ○ | P27 |
| PERSIST | ○ | ○ | P2 |
| NET | ○ |  | P12 |
| SEARCH | ○ |  | P6 |
| HASH | ○ | ○ | P17 |

**Without its degradable capabilities (upstream):**

- **IN**: “Start with host-native document reading and local, open-source extraction. If that is unavailable, ask the user for readable text or exports.” ([depositions/SKILL.md:20](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/depositions/SKILL.md#L20))

**Without its degradable capabilities (Cowork card):**

- **IN**: “If a source cannot be read, say so and ask for readable text or an export rather than working from its filename.” (Cowork card `depositions`, built SKILL.md line 27)

**What the Cowork adaptation changed:** Tool cascade rewritten to read documents the lawyer supplies or places in the Input folder, with no mention of local extraction tools; the transcript-platform rung stays optional. Method, templates and the optional real-time transcript checkpoint are unchanged.

#### docreview

*Review an incoming litigation production against the matter's requests or issues, with deterministic inventory and coverage receipts, a plain-language setup approval, human privilege decisions, source-linked Requests/Documents HTML, and...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| `OUT:xlsx-roundtrip` |  | ◐ | P9 |
| FS | ● | ● | P16 |
| PERSIST | ○ | ◐ | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| VISION | ◐ | ◐ | P4 |
| SUB | ◐ |  | P19 |
| SCHED | ○ |  | P13 |
| HTML | ● | ● | P20 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **EXEC**: “If local scripts cannot run, follow the portable fallback ... without stable file identity and complete count reconciliation, do not call the result coverage-certified.” ([docreview/SKILL.md:61-65](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/docreview/SKILL.md#L61-L65))
- **VISION**: “Legacy, corrupt, unsupported, or incomplete formats remain Needs rendering; image transcriptions remain labeled Needs your eyes.” (upstream/skills/litigation/docreview/SKILL.md:115-116 and references/comms-schemas.md:250)
- **SUB**: “using isolated workers when available and the same jobs sequentially otherwise.” ([docreview/SKILL.md:62](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/docreview/SKILL.md#L62))
- **SKILLDIR**: “Continue inside the same skill. Use host-native file and document tools for the mechanical operation named by each workflow step (scripts, schemas and prompts live in the skill folder).” ([docreview/references/shared/execution-modes.md:72-76](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/docreview/references/shared/execution-modes.md#L72-L76))

**Without its degradable capabilities (Cowork card):**

- **OUT:xlsx-roundtrip**: “Upstream a program checked that every request had exactly one result for every reviewable unit.” (Cowork card `docreview`, known issue KI-docreview-3 (“The coverage count is arithmetic this skill did itself”))
- **PERSIST**: “The register is the only thing that carries the privilege state between sessions.” (Cowork card `docreview`, known issue KI-docreview-7 (“Without the register attached, the skill produces nothing”))
- **VISION**: “A page read as an image is labelled Needs your eyes, and the lawyer is asked to look at every page and at the proposed matches and non-matches.” (Cowork card `docreview`, built references/comms-schemas.md line 154)

**What the Cowork adaptation changed:** All scripts, hashing, worker fan-out, run directory and JSON gate receipts are gone: one document at a time in the conversation, state held in an Excel master register the lawyer re-attaches each session (no register means no findings), per-document fingerprints instead of hashes, counts as workbook formulas, and the setup, privilege and findings pages hand-written as self-contained HTML for the preview pane. Rulings are recorded in the register or in chat, so HTML is a viewing surface only.

#### document-discovery

*Plan, draft, and review U.S.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| MCP | ○ | ○ | P15 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| `OUT:docx-template` | ● |  | P23 |
| FS | ◐ |  | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ○ |  | P1 |
| BIN | ○ |  | P1 |
| NET | ◐ | ◐ | P12 |
| SEARCH | ◐ | ◐ | P6 |
| VISION | ○ | ◐ | P4 |
| DOCX | ○ | ◐ | P3 |
| HTML | ◐ |  | P20 |
| SKILLDIR | ◐ | ◐ | P21 |

**Script runtime (upstream):** Python ≥3.8.

**Without its degradable capabilities (upstream):**

- **FS**: “If interactive HTML or local scripting is unavailable, use the available host tools to present the same exact request/wording decisions and record explicit review.” ([document-discovery/references/objection-review.md:92](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/document-discovery/references/objection-review.md#L92))
- **NET**: “If the applicable local order or current rule cannot be checked, label the output 'authority check incomplete,' identify what must be checked, and avoid a definitive deadline.” ([document-discovery/SKILL.md:53](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/document-discovery/SKILL.md#L53))
- **SEARCH**: “If the applicable local order or current rule cannot be checked, label the output 'authority check incomplete'; never claim a citator, local-rule, or docket search was performed when it was not.” ([document-discovery/SKILL.md:38,53](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/document-discovery/SKILL.md#L38))
- **HTML**: “present the same source-linked candidates as a readable catalog and capture explicit decisions in chat against exact resulting entries.” ([document-discovery/references/objection-library-builder.md:38](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/document-discovery/references/objection-library-builder.md#L38))
- **SKILLDIR**: “Use a supplied DOCX example when available. Otherwise start with the bundled RFP shell (the scripts also read ../assets); adapt a copy with host document tools.” ([document-discovery/references/response-shells.md:11,23](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/document-discovery/references/response-shells.md#L11))

**Without its degradable capabilities (Cowork card):**

- **NET**: “If the applicable local order or current rule cannot be checked, label the output 'authority check incomplete,' identify what must be checked, and avoid a definitive deadline or procedural instruction.” (Cowork card `document-discovery`, built SKILL.md line 59)
- **SEARCH**: “If the applicable local order or current rule cannot be checked, label the output 'authority check incomplete,' identify what must be checked.” (Cowork card `document-discovery`, built SKILL.md line 59)
- **VISION**: “Describe an unavailable application check accurately.” (Cowork card `document-discovery`, built references/response-shells.md line 49)
- **DOCX**: “If an essential component cannot be inspected, cleaned or preserved with available tools, identify the specific obstacle. Do not call a degraded document ready.” (Cowork card `document-discovery`, built references/response-shells.md line 43)
- **SKILLDIR**: “Use a supplied DOCX example when available. Otherwise start with the bundled RFP shell packaged with this skill at assets/rfp-response-shell.docx.” (Cowork card `document-discovery`, built references/response-shells.md line 11)

**What the Cowork adaptation changed:** The objection-library and objection-review HTML apps, their scripts and the Word assembly helpers were dropped; an approved bank of wording is now a document the lawyer supplies, and Word output goes through the host Word skill, starting from the one binary assets/rfp-response-shell.docx only when no example is supplied. Incoming-production review is out of scope rather than handed to docreview.

#### new-matter

*Open a litigation matter through a human-confirmed intake that records the parties, role, side, forum, engagement and authority, conflicts posture, emergency dates, preservation posture, status, stable identifiers, and field-level proven...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ◐ | P25 |
| MCP | ○ | ○ | P15 |
| IN | ○ | ○ | P26 |
| OUT | ◐ | ◐ | P27 |
| FS | ◐ | ◐ | P16 |
| PERSIST | ○ | ○ | P2 |
| SEARCH |  | ○ | P6 |

**Without its degradable capabilities (upstream):**

- **TOOLS**: “If a capability is unavailable, continue with user-provided files and mark the missing source; never claim that a configured integration was checked.” ([new-matter/SKILL.md:24](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/new-matter/SKILL.md#L24))
- **OUT**: “If the host cannot write to the user-designated location, return the complete record in the template format and say that it remains unsaved.” ([new-matter/SKILL.md:184](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/new-matter/SKILL.md#L184))
- **FS**: “If the result is ambiguous or unavailable, show the candidates or access gap and ask the user; a failed, inaccessible, or unclear check is not not-found.” ([new-matter/SKILL.md:40-42](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/new-matter/SKILL.md#L40-L42))

**Without its degradable capabilities (Cowork card):**

- **TOOLS**: “If a capability is unavailable, continue with user-provided files and mark the missing source; never claim that a configured integration was checked merely because it is listed.” (Cowork card `new-matter`, built SKILL.md line 25)
- **OUT**: “If the host cannot write to the user-designated location, return the complete record in the template format and say that it remains unsaved.” (Cowork card `new-matter`, built SKILL.md line 185)
- **FS**: “If the result is ambiguous or unavailable, show the candidates or access gap and ask the user; do not guess (architecture check of a user-identified matter folder).” (Cowork card `new-matter`, built SKILL.md line 41-43)

**What the Cowork adaptation changed:** Save destination is now whatever the lawyer names at approval (session Output folder or a OneDrive matter folder) instead of a known workspace, and non-federal forum rules are retrieved from the forum's own published sources because the regulatory skill is not carried. Preview-before-save gate and unsaved-record fallback are unchanged.

#### organize-case-docs

*Turn an accepted or active litigation matter’s documents and metadata into a provenance-backed case workspace with source inventory, chronology, proof charts, issue and evidence mapping, trackers, lifecycle controls, and an explicit docr...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| MCP | ○ | ○ | P15 |
| IN | ● | ● | P26 |
| OUT | ◐ | ◐ | P27 |
| FS | ● | ● | P16 |
| PERSIST | ● | ● | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| VISION | ○ |  | P4 |
| HASH | ● | ● | P17 |

**Without its degradable capabilities (upstream):**

- **OUT**: “Before writing anything, confirm the intended destination and whether the user wants only a proposed layout or an actual workspace.” ([organize-case-docs/SKILL.md:77](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/organize-case-docs/SKILL.md#L77))
- **EXEC**: “Start with host-native document reading and local, open-source inventory or extraction. If a source cannot be read, preserve it, mark it unreadable, and ask for a readable export.” ([organize-case-docs/SKILL.md:20](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/organize-case-docs/SKILL.md#L20))

**Without its degradable capabilities (Cowork card):**

- **OUT**: “Before writing anything, confirm the intended destination and whether the user wants only a proposed layout or an actual workspace.” (Cowork card `organize-case-docs`, built SKILL.md line 84)

**What the Cowork adaptation changed:** Tool cascade now just reads supplied or Input-folder documents and marks unreadable ones; the docreview sibling link became a stand-alone handoff template. The sha256 manifest column, 'hashes reconcile' gate and exhibit hash fields were kept unchanged with no fallback, so a hash-capable host tool is still needed (no script ships).

#### pressuretest

*Pressure-test a legal position against the documents the user supplies.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ◐ | P25 |
| IN | ● | ● | P26 |
| OUT | ◐ | ◐ | P27 |
| FS | ◐ | ○ | P16 |
| EXEC | ◐ |  | P1 |
| DOCX |  | ○ | P3 |
| SUB | ○ |  | P19 |
| HTML | ◐ | ○ | P20 |
| SKILLDIR | ◐ |  | P21 |
| INVOKE | ● |  | P24 |

**Script runtime (upstream):** Python ≥3.12.

**Without its degradable capabilities (upstream):**

- **TOOLS**: “If no interpreter or usable filesystem exists, deliver the same complete reading structure directly in chat with an explicit statement that deterministic checks and/or the saved record were unavailable.” ([pressuretest/SKILL.md:629-632](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/pressuretest/SKILL.md#L629-L632))
- **OUT**: “If artifacts cannot be created or delivered, use --format chat to deliver the complete checked reading view in chat, in consecutive parts if necessary.” ([pressuretest/SKILL.md:566-568](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/pressuretest/SKILL.md#L566-L568))
- **FS**: “If no interpreter or usable filesystem exists, deliver the same complete reading structure directly in chat; do not simulate a pass.” ([pressuretest/SKILL.md:629-632](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/pressuretest/SKILL.md#L629-L632))
- **EXEC**: “Calculator-dependent time findings stay unresolved if computation cannot be performed; if the helpers cannot run, deliver the full result in chat with the checks explicitly marked not run.” ([pressuretest/SKILL.md:633,646-647](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/pressuretest/SKILL.md#L633))
- **HTML**: “Deliver the full reading structure in chat (--format chat) when the report cannot be written.” ([pressuretest/SKILL.md:19](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/pressuretest/SKILL.md#L19))
- **SKILLDIR**: “Machinery never outranks delivery: if the helpers cannot run, deliver the full result in chat (scripts, schema and report-template.html are in the skill folder).” ([pressuretest/SKILL.md:646-647](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/pressuretest/SKILL.md#L646-L647))

**Without its degradable capabilities (Cowork card):**

- **OUT**: “If a file cannot be produced or delivered, give the complete checked reading view in chat instead, in consecutive parts if necessary, and disclose which outputs and checks were unavailable.” (Cowork card `pressuretest`, built SKILL.md line 446-449)

**What the Cowork adaptation changed:** The calculator, renderer and validator scripts are gone: the card fills assets/report-template.html itself, self-checks quote occurrence, and shows the count behind every date instead of running compute_period. A Word copy is available on request through the Word skill. The built frontmatter no longer carries explicit-invocation-only, so INVOKE is not required in the Cowork build (upstream allow_implicit_invocation was false).

#### writing

*Draft or revise U.S.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ◐ | P25 |
| MCP | ○ | ○ | P15 |
| IN | ○ | ○ | P26 |
| OUT | ○ |  | P27 |
| PERSIST | ○ |  | P2 |
| NET | ◐ | ◐ | P12 |
| SEARCH | ◐ | ◐ | P6 |

**Without its degradable capabilities (upstream):**

- **TOOLS**: “If a source cannot be retrieved or processed, preserve the gap and continue only within the disclosed evidence boundary.” ([writing/SKILL.md:60](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/writing/SKILL.md#L60))
- **NET**: “If a source cannot be retrieved or processed, preserve the gap and continue only within the disclosed evidence boundary.” ([writing/SKILL.md:60](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/writing/SKILL.md#L60))
- **SEARCH**: “When the record or authority set is incomplete, say so in the draft or handoff.” ([writing/SKILL.md:56](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/litigation/writing/SKILL.md#L56))

**Without its degradable capabilities (Cowork card):**

- **TOOLS**: “If a source cannot be retrieved or processed, preserve the gap and continue only within the disclosed evidence boundary.” (Cowork card `writing`, built SKILL.md line 63)
- **NET**: “If a source cannot be retrieved or processed, preserve the gap and continue only within the disclosed evidence boundary.” (Cowork card `writing`, built SKILL.md line 63)
- **SEARCH**: “When the record or authority set is incomplete, say so in the draft or handoff.” (Cowork card `writing`, built SKILL.md line 59)

**What the Cowork adaptation changed:** Essentially unchanged from upstream: only the playbook read (Input folder, read-only), and the cite-check and pressuretest handoffs now name sibling skills without a slash command. The draft stays in chat and no file output is asked.

### Transactional

#### closing-bible

*Audit a transaction closing folder after signing against the agreed closing checklist or the sigpack ledger, and account for the whole set — which version of each document is final, what appears executed and dated, what is missing, dupli...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| `OUT:pdf-assemble` | ◐ | ◐ | P8 |
| `OUT:xlsx-roundtrip` |  | ◐ | P9 |
| FS | ● |  | P16 |
| PERSIST | ○ | ◐ | P2 |
| EXEC | ● |  | P1 |
| BIN | ◐ |  | P1 |
| VISION | ◐ | ◐ | P4 |
| DOCX |  | ○ | P3 |
| SUB | ○ |  | P19 |
| SKILLDIR | ● |  | P21 |

**Script runtime (upstream):** Python ≥3.12; programs `soffice`.

**Without its degradable capabilities (upstream):**

- **OUT:pdf-assemble**: “Without pypdf everything else is still written, combined_pdf is null, and the lawyer is told in one line.” ([closing-bible/SKILL.md:196](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-bible/SKILL.md#L196))
- **BIN**: “Poppler is probed at run time; without it the census records page counts as unknown and the skill continues. Without LibreOffice, Word files stay native and are left out of the combined PDF.” ([closing-bible/SKILL.md:192](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-bible/SKILL.md#L192))
- **VISION**: “If neither Poppler nor the host's document tools can render a family's execution pages, say the visual check could not run, record not-inspected with the reason, and carry it as not ready.” ([closing-bible/SKILL.md:194](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-bible/SKILL.md#L194))

**Without its degradable capabilities (Cowork card):**

- **OUT:pdf-assemble**: “Merging chosen documents into one bookmarked PDF, and splitting it into volumes, is nowhere documented in Cowork and is not attempted.” (Cowork card `closing-bible`, known issue KI-closing-bible-5 (“No combined bible PDF”))
- **OUT:xlsx-roundtrip**: “Every number in the index and the register comes from the model's own reading of the documents supplied.” (Cowork card `closing-bible`, known issue KI-closing-bible-1 (“The count is a reading, and the register is what makes it checkable”))
- **PERSIST**: “Without the register there is no history: say so in the first reply, name what you looked for, and treat the run as a fresh reading of what is in front of you.” (Cowork card `closing-bible`, built SKILL.md line 150)
- **VISION**: “Where the execution pages are a scan or an image, record not-inspected with the reason, propose unsigned, and let the reconciliation carry it as not ready. Never describe a page you did not read.” (Cowork card `closing-bible`, built SKILL.md line 107)

**What the Cowork adaptation changed:** Scripts, census hashing, combined PDF build and build/update modes were removed; the card reads attached documents, shows an index, exceptions list and an Excel status register (host Excel skill), with Word only on request. No hashing is asked of the host (fingerprints are explicitly disclaimed), so HASH and SKILLDIR are blank.

#### closing-checklist

*Draft an editable Word transaction closing checklist from an SPA or other anchor agreement, or propose and apply substantive changes to an existing checklist after revised agreements, additional documents or lawyer instructions.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| MCP | ○ | ○ | P15 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| FS | ● |  | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| NET | ○ | ○ | P12 |
| SEARCH | ○ | ○ | P6 |
| VISION | ◐ | ◐ | P4 |
| DOCX | ◐ | ● | P3 |
| `DOCX:table-edit` | ◐ |  | P23 |
| SUB | ○ |  | P19 |
| SKILLDIR | ○ |  | P21 |

**Script runtime (upstream):** Python ≥3.8.

**Without its degradable capabilities (upstream):**

- **EXEC**: “Scripts, connectors and parallel workers are optional. Without code execution, use host reading/editing capabilities and the same review gates.” ([closing-checklist/SKILL.md:33-35](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-checklist/SKILL.md#L33-L35))
- **VISION**: “Render and inspect every page ... If rendering is unavailable, say visual QA remains outstanding; structural checks alone are not visual approval.” ([closing-checklist/SKILL.md:229-231](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-checklist/SKILL.md#L229-L231))
- **DOCX**: “The helper refuses nested item tables and vertical merges. Use a capable host Word editor, preserving the same approval and verification contract, or report the specific unmet requirement.” ([closing-checklist/references/word-workflow.md:119-124](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-checklist/references/word-workflow.md#L119-L124))
- **DOCX:table-edit**: “Without a way to edit the Word table, give an explicitly labelled interim table and disclose the unmet deliverable.” ([closing-checklist/SKILL.md:233](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/closing-checklist/SKILL.md#L233))

**Without its degradable capabilities (Cowork card):**

- **VISION**: “Render and inspect every page ... If rendering is unavailable, say visual QA remains outstanding; structural checks alone are not visual approval.” (Cowork card `closing-checklist`, built SKILL.md line 248-250)

**What the Cowork adaptation changed:** Both helper scripts and word-workflow.md were removed; the Word checklist is now produced and revised through the host's built-in Word skill (DOCX and OUT rated R because the only fallback, an interim chat table at SKILL.md:49-52, is labelled an unmet deliverable). The external copy is built fresh instead of through the helper's sanitiser.

#### conform

*Adapt a selected clause from a source or precedent document into a core document's own vocabulary, or check a core document for leftover source-document vocabulary, using current /definition-check ledgers for both documents.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ◐ | P25 |
| MCP | ○ |  | P15 |
| IN | ● | ● | P26 |
| OUT | ● | ◐ | P27 |
| FS | ● |  | P16 |
| EXEC | ● |  | P1 |
| NET | ○ |  | P12 |
| DOCX |  | ◐ | P3 |
| `DOCX:tracked-write` |  | ◐ | P10 |
| SUB | ◐ |  | P19 |
| HTML | ◐ |  | P20 |
| SKILLDIR | ● |  | P21 |

**Script runtime (upstream):** Python ≥3.12.

**Without its degradable capabilities (upstream):**

- **SUB**: “If subagents are unavailable, one model may perform the same roles sequentially; record that execution shape and do not claim independent review.” ([conform/SKILL.md:98](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/conform/SKILL.md#L98))
- **HTML**: “The clean text is always given in the reply alongside the redline.” ([conform/SKILL.md:118](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/conform/SKILL.md#L118))

**Without its degradable capabilities (Cowork card):**

- **OUT**: “The mapping table in the reply and saved as conform-mapping.md; the clean text of the conformed clause in the reply, written out rather than recovered from the document.” (Cowork card `conform`, built SKILL.md line 104-106)
- **DOCX**: “Ask for the changes as real tracked changes and tell the lawyer which they have: marks Word shows in its review pane, or the old wording set beside the new.” (Cowork card `conform`, built SKILL.md line 105)
- **DOCX:tracked-write**: “Ask for the changes as real tracked changes and tell the lawyer which they have: marks Word shows in its review pane, or the old wording set beside the new.” (Cowork card `conform`, built SKILL.md line 105)

**What the Cowork adaptation changed:** The two-ledger preflight, content-hash check, normalisation script in the sibling definition-check folder, packet workers and conform.html were all removed; both vocabularies are now read in-session and the redline goes out as a Word document through the host Word skill, with the full mapping table and clean text always in the reply. No hashing, sibling-skill path or worker is asked of the host.

#### definition-check

*Review a lawyer-provided contract and produce a visual report that annotates defined terms and drafting issues, plus a machine-readable term index that agents can reference during drafting.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ◐ | ● | P25 |
| MCP | ○ |  | P15 |
| IN | ◐ | ◐ | P26 |
| OUT | ◐ | ● | P27 |
| `OUT:xlsx-roundtrip` |  | ◐ | P9 |
| FS | ◐ |  | P16 |
| PERSIST | ○ | ○ | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| DOCX | ◐ |  | P3 |
| SUB | ◐ |  | P19 |
| HTML | ◐ | ● | P20 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.12.

**Without its degradable capabilities (upstream):**

- **IN**: “Request pasted or exported text if the DOCX body is inaccessible.” ([definition-check/references/capability-routing.md:13](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/references/capability-routing.md#L13))
- **OUT**: “In-conversation report when writing is unavailable.” ([definition-check/SKILL.md:223](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/SKILL.md#L223))
- **FS**: “C0/C1: analyse only the content the host exposes, as a reduced-assurance review; never claim deterministic parity.” ([definition-check/references/capability-routing.md:13](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/references/capability-routing.md#L13))
- **EXEC**: “C1_HOST_TEXT: complete host-extracted text, no executable runtime; perform reduced-assurance model review and never translate a missing parser or skipped method into 'no issues found'.” ([definition-check/references/capability-routing.md:14](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/references/capability-routing.md#L14))
- **DOCX**: “Reduced-assurance review of host text must state structural, exact-location, tracked-change, and non-body omissions.” ([definition-check/references/capability-routing.md:14](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/references/capability-routing.md#L14))
- **SUB**: “If subagents, search, retrieval, or artifact writes are unavailable, run the strongest lower profile and list the omitted agentic methods.” ([definition-check/SKILL.md:126](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/SKILL.md#L126))
- **HTML**: “When writing is unavailable the report is given in the conversation.” ([definition-check/SKILL.md:223](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/SKILL.md#L223))
- **SKILLDIR**: “Read capability-routing.md when the original DOCX cannot be processed with the packaged deterministic checker or when any required runtime is absent or restricted.” ([definition-check/SKILL.md:35](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/definition-check/SKILL.md#L35))

**Without its degradable capabilities (Cowork card):**

- **IN**: “If the body cannot be read, ask for the text to be pasted or exported rather than guessing at it.” (Cowork card `definition-check`, built SKILL.md line 50)
- **OUT:xlsx-roundtrip**: “The counts in the Excel register are counts the skill made and wrote down.” (Cowork card `definition-check`, known issue KI-definition-check-2 (“The register's arithmetic is written, not computed”))

**What the Cowork adaptation changed:** The deterministic checker, worker fan-out, ledger/matter machinery and normalisation script were removed; the card is the upstream instruction-only mode, adding a unit list, an Excel definitions register (host Excel skill) and a self-contained definition-check.html written to the Output folder with no fallback if it cannot be written. No hash, script or worker is asked of the host.

#### diligence

*Use when a data room, deal folder, or contract portfolio needs review against an issue checklist and the lawyer needs factual results they can inspect: every match pin-cited, every agreement accounted for, scoped negatives shown, and eve...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| `OUT:xlsx-roundtrip` |  | ◐ | P9 |
| FS | ● |  | P16 |
| PERSIST | ○ | ◐ | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ○ |  | P1 |
| VISION | ◐ | ◐ | P4 |
| SUB | ◐ |  | P19 |
| SCHED | ○ | ○ | P13 |
| HTML | ● | ● | P20 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.11.

**Without its degradable capabilities (upstream):**

- **EXEC**: “The fallback is method-compatible, not assurance-equivalent; without script checks the run may deliver a labelled review and unresolved queue but may not call the result coverage-certified.” ([diligence/references/shared/execution-modes.md:93-101](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/diligence/references/shared/execution-modes.md#L93-L101))
- **VISION**: “A missing or stale render becomes Needs rendering and stops approval for dependent results; it never changes a model proposal or evidence receipt.” ([diligence/SKILL.md:125-126](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/diligence/SKILL.md#L125-L126))
- **SUB**: “Use native workers when the host provides them; otherwise run the jobs sequentially. Worker selection never changes the plans, prompts, schemas, gates, or coverage equation.” ([diligence/references/shared/execution-modes.md:78-80](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/diligence/references/shared/execution-modes.md#L78-L80))
- **SKILLDIR**: “If a host cannot execute local scripts, preserve the same artifact shapes, assignments, validations, and gate conditions with host-native document and data capabilities.” ([diligence/SKILL.md:42](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/diligence/SKILL.md#L42))

**Without its degradable capabilities (Cowork card):**

- **OUT:xlsx-roundtrip**: “Upstream a program checked that every issue had exactly one result for every reviewable agreement.” (Cowork card `diligence`, known issue KI-diligence-2 (“The coverage count is arithmetic this skill did itself”))
- **PERSIST**: “When the register is not attached, say so before anything else, name the file that was expected, and say which tranches are on the record; then continue on the reduced scope you can see.” (Cowork card `diligence`, built SKILL.md line 75-78)
- **VISION**: “Where a page cannot be read (a scan, an image, a format that did not open) it goes to a visible Needs your eyes queue with the reason, and every dependent finding is held.” (Cowork card `diligence`, built SKILL.md line 224-228)

**What the Cowork adaptation changed:** Scripts, schemas, hashing and fan-out were removed; the upstream portable fallback became the only path (sequential, tranche at a time, fingerprint of four fields instead of a hash, same-reader second pass). State lives in an Excel master register the lawyer re-attaches, and HTML setup, test and crosswalk pages are built by the model for the preview pane. SCHED is only offered as an optional lawyer-set routine (references/shared/execution-modes.md:72-76).

#### playbook-builder

*Build or update an approved contract playbook from one to five lawyer-selected templates, precedents, negotiated agreements, or KM notes.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| FS | ● |  | P16 |
| PERSIST | ● | ● | P2 |
| EXEC | ◐ |  | P1 |
| VISION | ◐ | ◐ | P4 |
| DOCX | ◐ | ◐ | P3 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.8.

**Without its degradable capabilities (upstream):**

- **EXEC**: “If the script cannot run, use host-native hashing, document reading, and file writing where available, preserving the same manifest, approval, provenance, and receipt contract.” ([playbook-builder/SKILL.md:281-287](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-builder/SKILL.md#L281-L287))
- **VISION**: “If that capability is not available, keep the document pending and do not claim complete coverage.” ([playbook-builder/references/pdf-intake.md:22](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-builder/references/pdf-intake.md#L22))
- **DOCX**: “A Word file with unresolved tracked changes, an encrypted source, or a materially unreadable page cannot be treated as settled evidence; keep it visible and resolve or exclude it at the gate.” ([playbook-builder/SKILL.md:98-100](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-builder/SKILL.md#L98-L100))
- **SKILLDIR**: “If the script cannot run, use host-native hashing, document reading, and file writing where available, while preserving the same manifest, approval, provenance, and receipt contract.” ([playbook-builder/SKILL.md:283-286](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-builder/SKILL.md#L283-L286))

**Without its degradable capabilities (Cowork card):**

- **VISION**: “Where a page cannot be read at all, keep it pending and do not claim complete coverage.” (Cowork card `playbook-builder`, built references/pdf-intake.md line 24)
- **DOCX**: “A Word file with unresolved tracked changes, an encrypted source, or a materially unreadable page cannot be treated as settled evidence. Keep it visible and resolve or exclude it at the gate.” (Cowork card `playbook-builder`, built SKILL.md line 104-107)

**What the Cowork adaptation changed:** Script, schema, hashes, receipt and registry were removed; the playbook is one Markdown file (plus curation and coherence reports) found again by file name in a folder the lawyer chose, and the seal becomes a read-through check. Leftover upstream wording still mentions a document hash (SKILL.md:123) and a canonical playbook.json (SKILL.md:191), which the card no longer produces.

#### playbook-review

*Review counterparty contracts, outbound drafts, or revised contract packages against an approved Playbook Engine contract playbook.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ◐ | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ◐ | P27 |
| FS | ● |  | P16 |
| PERSIST | ◐ | ◐ | P2 |
| EXEC | ◐ |  | P1 |
| VISION | ◐ | ◐ | P4 |
| DOCX | ◐ | ◐ | P3 |
| `DOCX:tracked-write` |  | ○ | P10 |
| SUB | ◐ |  | P19 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.8.

**Without its degradable capabilities (upstream):**

- **PERSIST**: “A playbook can be supplied by explicit path instead of the registry; the skill halts only when neither exists.” ([playbook-review/SKILL.md:29](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-review/SKILL.md#L29))
- **EXEC**: “If it cannot run, use host-native hashing, reading, diffing, and rendering where available while preserving the same source-bound artifact contract.” ([playbook-review/SKILL.md:415-419](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-review/SKILL.md#L415-L419))
- **VISION**: “If that capability is not available, keep the document pending and do not claim complete coverage.” ([playbook-review/references/pdf-intake.md:22](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-review/references/pdf-intake.md#L22))
- **DOCX**: “If exact hashes, visual page reconciliation, markup reconstruction, or coverage validation cannot be produced, state which receipt is unavailable and do not claim completeness.” ([playbook-review/SKILL.md:419-421](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-review/SKILL.md#L419-L421))
- **SUB**: “The host may use isolated parallel workers for thematic batches when available; otherwise run the same batches sequentially.” ([playbook-review/SKILL.md:219-220](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-review/SKILL.md#L219-L220))
- **SKILLDIR**: “If it cannot run, use host-native hashing, reading, diffing, and rendering where available while preserving the same source-bound artifact contract.” ([playbook-review/SKILL.md:415-419](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/playbook-review/SKILL.md#L415-L419))

**Without its degradable capabilities (Cowork card):**

- **OUT**: “Write the deliverables as a table in the reply, a Markdown file, and, when the lawyer asks for it, a Word document through the built-in Word skill.” (Cowork card `playbook-review`, built SKILL.md line 31-34)
- **PERSIST**: “Ask for the file by name if the request does not identify it. There is no library to search and no registry; if the lawyer does not know where theirs is, ask them to point at the folder.” (Cowork card `playbook-review`, built SKILL.md line 49-53)
- **VISION**: “Where a page cannot be read at all, keep it pending and do not claim complete coverage.” (Cowork card `playbook-review`, built references/pdf-intake.md line 24)
- **DOCX**: “A document with unresolved tracked changes, an encrypted file, or a page you cannot read is not settled evidence: keep it visible and resolve or exclude it at the gate.” (Cowork card `playbook-review`, built references/playbook-format.md line 99-101)

**What the Cowork adaptation changed:** Seventeen script steps, JSON artifacts, registry discovery and script-made Word exports were removed; the issues list is a triage table in the reply plus issues-list.md, with internal and external Word cuts through the host Word skill only on request, and the playbook is found by file name. Nothing asks the host to hash, run scripts or dispatch workers.

#### read-redline

*Use when a counterparty sends a redline, blackline, or compare PDF, or a Word file with tracked changes, and you need every change, what matters, and a marked-up copy to hand back.*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| `OUT:pdf-annotate` | ◐ |  | P22 |
| FS | ● |  | P16 |
| PERSIST | ○ |  | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ◐ |  | P1 |
| VISION | ◐ | ◐ | P4 |
| DOCX | ● | ● | P3 |
| `DOCX:tracked-write` |  | ◐ | P10 |
| HTML |  | ● | P20 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.11; packages `pdfplumber`, `pypdf`, `docx`; programs `pdftoppm`, `pdfinfo`.

**Without its degradable capabilities (upstream):**

- **OUT:pdf-annotate**: “If the host cannot annotate, deliver the issues list only and say the annotated PDF could not be produced.” ([read-redline/SKILL.md:124](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/read-redline/SKILL.md#L124))
- **EXEC**: “If the scripts cannot run, use host-native PDF reading, rendering, and annotation capabilities to preserve the same calibration, extraction, reconciliation, rating, and coverage rules.” ([read-redline/SKILL.md:124](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/read-redline/SKILL.md#L124))
- **BIN**: “If the host cannot render pages, say plainly that visual reconciliation did not run and the completeness receipt is unavailable.” ([read-redline/SKILL.md:124](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/read-redline/SKILL.md#L124))
- **VISION**: “If the host cannot render pages, say plainly that visual reconciliation did not run and the completeness receipt is unavailable.” ([read-redline/SKILL.md:124](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/read-redline/SKILL.md#L124))
- **SKILLDIR**: “If the scripts cannot run, use host-native PDF reading, rendering, and annotation capabilities to preserve the same rules; if it cannot annotate a PDF, deliver the grounded issues list.” ([read-redline/SKILL.md:124](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/read-redline/SKILL.md#L124))

**Without its degradable capabilities (Cowork card):**

- **VISION**: “If you cannot tell what is on a page (a scan, an image, an unresolved layout), name the page and say the page-by-page reconciliation did not run for it. Do not describe a page you could not read.” (Cowork card `read-redline`, built SKILL.md line 54)
- **DOCX:tracked-write**: “When you ask for the review inside a document, the skill produces a new Word document and asks for the changes to be recorded as real tracked changes.” (Cowork card `read-redline`, known issue KI-read-redline-4 (“A marked-up Word copy may come back as plain text”))

**What the Cowork adaptation changed:** The seven scripts (parsers, calibration gate, annotators, issues-list builder) were removed; the document is read directly, the calibration gate is a self-applied rule recorded in redline-calibration.md, and the annotated PDF is replaced by a self-contained Marked Passages HTML page plus a Word issues list through the host Word skill. DOCX is rated R because the Word path depends on seeing tracked-change tags and the only documented outcome when they cannot be seen is to report 'could not tell' (SKILL.md:84-87).

#### sigpack

*Use for wet-ink and mixed closings on a folder of execution PDFs: find every signature page, read who signs (party, signatory, capacity), open the matter ledger, build the signature packs by agreement, counterparty or signatory with the...*

| Capability | Upstream | Cowork card | Decided by |
| --- | --- | --- | --- |
| TOOLS | ● | ● | P25 |
| IN | ● | ● | P26 |
| OUT | ● | ● | P27 |
| `OUT:pdf-assemble` | ● |  | P8 |
| `OUT:xlsx-roundtrip` |  | ◐ | P9 |
| FS | ● |  | P16 |
| PERSIST | ● | ◐ | P2 |
| EXEC | ◐ |  | P1 |
| BIN | ◐ |  | P1 |
| VISION | ● |  | P4 |
| DOCX | ○ | ● | P3 |
| SUB | ◐ |  | P19 |
| SKILLDIR | ◐ |  | P21 |

**Script runtime (upstream):** Python ≥3.8; packages `pypdf`; programs `pdftoppm`, `soffice`.

**Without its degradable capabilities (upstream):**

- **EXEC**: “If the script cannot run, use host-native PDF and document capabilities while preserving the same ledger, classification, page-by-page visual review, matching, and receipt rules.” ([sigpack/SKILL.md:135](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/sigpack/SKILL.md#L135))
- **BIN**: “If Word conversion is unavailable, ask for PDFs rather than treating the documents as converted. If soffice is missing the command stops and says so.” ([sigpack/SKILL.md:64](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/sigpack/SKILL.md#L64))
- **SUB**: “If the host has no parallel workers, work through the candidates yourself: render each and look at it beside its text.” ([sigpack/SKILL.md:72](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/sigpack/SKILL.md#L72))
- **SKILLDIR**: “If the script cannot run, use host-native PDF and document capabilities while preserving the same ledger, classification, page-by-page visual review, matching, and receipt rules.” ([sigpack/SKILL.md:135](https://github.com/LegalQuants/lq-plugin-oss/blob/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/skills/transactional/sigpack/SKILL.md#L135))

**Without its degradable capabilities (Cowork card):**

- **OUT:xlsx-roundtrip**: “The ledger is handed to Excel and handed back.” (Cowork card `sigpack`, known issue KI-sigpack-2 (“A ledger workbook can come back from a round trip short a row or a formula”))
- **PERSIST**: “If no ledger was attached, say so in the first reply, state that you are working from what is in front of you and nothing carries over from an earlier session, and carry on.” (Cowork card `sigpack`, built SKILL.md line 56)

**What the Cowork adaptation changed:** The 90 KB script, folder scan, render-and-look review of returned pages, compile and balanced receipt were removed and explicitly disclaimed (no VISION asked: returned pages are never inspected). What remains is the signing matrix, pages drafted on the lawyer's Word template through the host Word skill, instruction table, cover note and chasers, with the ledger carried as an attached Excel or Markdown file.

## 8. Requirements that are not a single capability

- **The skill folder must exist on disk, with its siblings.** Scripts import sibling modules and read `../assets` and `../schemas`. Several call another skill's scripts by relative path: every companion skill calls `legalquants/scripts/onboarding.py` and writes its store through `lq-reflect/scripts/profile_store.py`; legalquants, lq-reflect and lq-mirror call `lq-start/scripts/catalog.py`; conform calls `definition-check/scripts/normalize_terms.py`. Loading `SKILL.md` as text is not enough (code SKILLDIR).
- **Skill-to-skill data.** conform needs definition-check ledgers (schema 0.14.0); playbook-review needs a playbook-builder registry; closing-bible optionally reads the sigpack ledger; legaldesign optionally reads cite-check output; organize-case-docs hands off to docreview.
- **Calling a skill by name.** Nine upstream skills are explicit-invocation only (code INVOKE): `legalquants`, `lq-apply`, `lq-ask`, `lq-connect`, `lq-mirror`, `lq-start`, `my-lq-moment`, `pressuretest`, `timenarratives`.
- **A model per worker.** docreview and diligence require one fixed, higher-capability model at medium effort or above for their finding workers; the packaged worker runners pin a model. A harness whose subagents cannot choose a model fails these contracts.
- **Provider-specific assumptions.** `lq-start` reads `.claude-plugin` and `.codex-plugin` layouts and `$CODEX_HOME`; lq-reflect parses Codex and Claude Code transcript files; the worker runners shell out to `codex exec`; wiki's automatic retrieval expects Codex lifecycle hooks. Another harness needs equivalents or falls back.
- **Python version.** The floor across the set is 3.12: definition-check, conform and closing-bible gate on it and pressuretest declares it; most of the rest need 3.11.

## 9. Supplying capabilities through tools and MCP

A harness can provide a capability natively or through a tool attached over MCP; the skills accept either. Most describe a *tool cascade* - bundled scripts first, then host-native tools, then a service the user or firm selects. Three conditions in the skills' own text decide whether a given tool counts:

1. **It must actually perform the operation.** "Do not claim SHA-256 identity ... automated count reconciliation unless a host-native tool actually performed it." A tool that summarises a page or describes a file does not count; regulatory rejects a fetch tool's rendering as "a model's summary of the text, not the text".
2. **Client material stays inside an approved boundary.** Remote processing only where the "connector, network, DMS, or hosted-service data boundary is already authorized". cite-check sends only citation metadata to public services; client-update never uploads matter material "merely to format or summarize it"; wiki's position notes "never leave the machine". For the matter skills, any tool touching documents must run locally or inside the firm's own approved system.
3. **Scripts only see a filesystem.** A code-execution tool counts only if the skill folders and the user's workspace are both inside it.

Connectors the skills name: **lq-mcp** (lq-ask, degradable), **CourtListener MCP** (cite-check, optional, citation metadata only), and "network/connectors/MCP/DMS" integrations (definition-check and conform, optional, already-authorised only). About a dozen more accept a firm-selected DMS, docket, e-discovery or legal-research system. my-lq-moment, correspondence, sigpack, playbook-review and diligence refuse to publish, send, docket or run e-signature even when such a connector exists.

## 10. Measuring a real harness

The levels say what each skill needs; a probe measures whether a harness has it. Each code has primary probes, and a skill can add probes for a facet:

| Code | Decided by | Probe question |
| --- | --- | --- |
| TOOLS | P25 | Does a tool call actually execute? |
| MCP | P15 | Can the harness connect to an MCP server and call one of its tools? |
| IN | P26 | Can the harness read every supplied format, whole? |
| OUT | P27 | Can the harness hand a file back to the user? |
| FS | P16 | Can the agent walk a folder it was pointed at, and make one beside it? |
| PERSIST | P2 | Does a file written in one session come back in the next? |
| EXEC | P1 | Does a bundled script actually run, and in what? |
| BIN | P1 | Does a bundled script actually run, and in what? |
| NET | P12 | Browser use: does what it reads reach the skill? |
| SEARCH | P6 | Is web search on in this tenant, and what comes back? |
| VISION | P4 | Can Cowork tell what is on a page? |
| DOCX | P3 | Does Cowork report tracked changes in a Word document? |
| SUB | P19 | Can the harness run an isolated worker that sees only its packet? |
| SESSION | P11 | What can a skill see and quote of its own session? |
| SCHED | P13 | Can a scheduled run work over files placed earlier? |
| HTML | P20 | Can the user open a generated page and hand back the file it saves? |
| HASH | P17 | Can the harness compute a file's SHA-256? |
| SKILLDIR | P21 | Is the skill folder on disk, with its scripts and assets reachable? |
| INVOKE | P24 | Does an explicit-invocation-only skill stay quiet until it is called by name? |

P1 to P14 were first written for Microsoft 365 Copilot Cowork and keep their original titles; the harness-probe skill runs every one of them on any harness.

Facet and extra probes: **P5** What does a resumed task remember?; **P7** Can a skill's output carry a file that shipped with the skill?; **P8** Can Cowork build a PDF out of chosen pages of supplied PDFs?; **P9** Does an Excel workbook survive a round trip with its arithmetic intact?; **P10** Can Cowork produce a Word document carrying real tracked changes?; **P14** Enterprise Search as a people finder; **P18** Can the harness fetch a URL's raw bytes into a file?; **P22** Can the harness annotate a PDF with highlights and comment-pane notes?; **P23** Can the harness fill a packaged Word template and edit its table in place?.

A skill's verdict on a harness follows from the probe results:

| Verdict | Rule |
| --- | --- |
| Runs as intended | every required and every degradable capability has a passing probe |
| Runs on a fallback | every required capability passes; at least one degradable one failed or is unprobed |
| Cannot run | at least one required capability failed |
| Untested | no required capability failed, but at least one has no result yet |

Before any probe has run, the upstream skills stand at 0 as intended, 7 on a fallback and 24 untested; the Cowork cards at 5, 7 and 19.

**One measured harness.** Claude Code on the web, probing its own cloud container on 1 October 2026: 8 skills run as intended, 4 on a fallback, 2 cannot run and 17 remain untested. The blocks were concrete: the container's default `python3` is 3.11, below the 3.12 floor of closing-bible and conform, and without the PDF libraries read-redline expects it runs on its documented fallback. The report's *what to build next* therefore names one capability, running Python scripts on 3.12 or later, which would unblock two skills and upgrade two more. Its egress allow-list blocks some public sites but not GitHub, so fetching passes. The untested skills wait on probes that need a person (opening a page, calling a skill by name, judging a quotation) or a second session.

The probe skill is `harness-probe` in the [houfu/lq-plugin-cowork](https://github.com/houfu/lq-plugin-cowork) repository; the levels in this study are its `capabilities.yaml`.

## 11. Build-out order for a harness

If a harness were built up one capability group at a time, this is where each skill would start to run (every ● met) and run as intended (every ● and ◐ met).

**Upstream skills**

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

**Cowork cards**

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

## 12. Limitations

- Levels come from reading the skills, not running them. A skill can promise a fallback it handles badly, or need something its text does not mention; only a probe run on a real harness shows that.
- The audits were done by AI reviewer agents with file-and-line evidence, then spot-checked and cross-audited. A level is a judgement where a skill's text is ambiguous; those calls are recorded with the quote they rest on.
- The upstream skills change. This study is pinned to commit [`fa5a668`](https://github.com/LegalQuants/lq-plugin-oss/tree/fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/); a later upstream version may need different levels.
- The Cowork profile describes cards as built by one independent adaptation project at version 0.2.0; it is not an official LegalQuants or Microsoft statement.
- LegalQuants skills are a workflow aid, not legal advice.

---

*Generated from `capabilities.yaml` and `probes.yaml` in [houfu/lq-plugin-cowork](https://github.com/houfu/lq-plugin-cowork) by `tools/scripts/research_doc.py`. The interactive version of these tables, with every probe and the recorded harness verdicts, is the project site's Probes and Verdicts pages.*
