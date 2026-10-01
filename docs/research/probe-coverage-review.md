# Do the capability probes cover the harness chart, and do they produce a report?

1 October 2026

This document reviews `probes.yaml` (P1–P14), docs/TESTING.md Part E and the tooling that reads them. It
checks them against [harness-capability-chart.md](harness-capability-chart.md) and asks two questions:

1. Does the probe set test every capability the chart says the vendored skills need?
2. Does it produce a report that says which skills run as intended, which run on a fallback and which
   cannot run?

**Short answer: no to both.**

- Of the chart's sixteen capabilities:
  - four are covered;
  - nine are covered in part;
  - three are not probed at all: MCP connection, isolated workers and the interactive HTML round trip.
- The probes never test hashing a file, which organize-case-docs needs outright (●) and every fallback
  receipt relies on.
- Even if all fourteen probes passed, eighteen skills would still have a ● capability that no probe
  checks. That list includes docreview, diligence and legaldesign.
- There is no report. Probe results live only as free text in GitHub issues. Nothing records an outcome
  in a form a tool can read, and nothing turns outcomes into a verdict for each skill. Each card's tier
  and status are set by hand when the card is designed.

## The probes answer a narrower question

The two documents look at different things:

- **The probes are about Cowork.** Their header says so: "Fourteen questions about Microsoft 365
  Copilot Cowork … each one is a thing a card would like to rely on". They test the **adapted cards**
  against **one host**.
- **The chart is about any harness.** It covers the **upstream skills** on any harness, starting from a
  chat loop with skills support.

Some gaps below follow from that narrower brief. P1, for example, cannot run from the released bundles
because the cards ship no scripts. Even so, if the probes are to confirm that a harness can run the
vendored skills, those gaps have to be closed.

## Coverage by capability

**Covered** means a pass would show that the capability is present at the level the skills need.

| Code | Probes | Coverage | What is not tested |
|---|---|---|---|
| TOOLS | none directly; P1 implicitly | Partial | No probe asks only "did the tool call execute, or was it narrated?". P1 comes closest: its worst outcome is a description of the script instead of its output. |
| MCP | none | **None** | Nothing tests connecting to an MCP server: lq-mcp for lq-ask, CourtListener for cite-check, or the C5 integrations of definition-check and conform. P14 tests Enterprise Search, which is a host feature, not an MCP connection. |
| IN | P3 (docx), P4 (pdf), P9 (xlsx) | Partial | eml or msg (docreview, diligence, correspondence); images; reading a long document **whole**, which pressuretest and cite-check require. |
| OUT | P7 (html, png), P8 (pdf), P9 (xlsx), P10 (docx with tracked changes) | Partial | An editable docx built from a bundled `.docx` template (document-discovery); editing a docx table in place (closing-checklist); an annotated PDF with comment-pane notes (read-redline); json, csv and svg outputs. |
| FS | P2 (one named file) | Partial | Walking a user-named folder recursively and counting what is in it, which a data room, production, closing folder or matter folder all need. Also untested: creating a run folder or a sibling output folder, and keeping paths stable across calls. This capability is ● for 17 skills. |
| PERSIST | P2 | Partial | P2 tests the Cowork Output folder only. Home-directory stores (`~/.lq/`, `~/.wiki/wikis.json`) and finding a registry by walking up parent folders (playbook-review) are untested. |
| EXEC | P1 | Partial | P1 needs a throwaway probe package. Its pass bar is "a real Python version string", not ≥3.12. It does not test that a script can read the user's file and write to the workspace, that sibling-skill paths such as `../lq-start/scripts/catalog.py` resolve, or whether network access is on or off. |
| BIN | P1 | Partial | It checks `soffice`, `pdftoppm` and `tesseract`. It misses `pdfinfo` and `pdftotext`, headless Chromium, any SVG rasteriser (`rsvg-convert`, ImageMagick, Inkscape) and `codex`. |
| NET | P6, P12 | Partial | Both ask for a quotation and a URL. Neither tests that the **raw bytes** are saved to a file that can be hashed, which regulatory requires (●). Calls to the GitHub API (lq-connect evidence) are untested. |
| SEARCH | P6 | Covered | — |
| VISION | P4 | Covered | Page-level marks, signatures and scans. The multi-viewport HTML layout check in legaldesign is not covered, but it is ◐. |
| DOCX | P3 (read), P10 (write) | Covered | Tracked changes are covered both ways. Writing comments (read-redline's annotated docx) and editing tables are untested. |
| SUB | none | **None** | Parallel workers, a fresh-context reviewer, and choosing the model and effort for each worker are all untested. This is ◐ in nine skills, and wiki's gate reviewer has no documented fallback. |
| SESSION | P5, P11 | Covered | P11 covers the current session and P5 a resumed task. Reading related past chats for timenarratives (◐) is untested. |
| SCHED | P13 | Partial | A scheduled prompt only. A detached long-running process (the docreview and diligence runners) and lifecycle hooks (wiki) are untested. |
| HTML | P7a only in part | **None** | P7a checks that a template's structure reaches the output. Nothing tests that the user can open the page, that `localStorage` and Blob downloads work, or that the returned JSON file can be uploaded back. This is ● for legaldesign, docreview and diligence. |

Three requirements in the chart's "bundled with others" section also have no probe:

- **Hashing.** No probe asks for a SHA-256 of a file. That is ● for organize-case-docs, and the
  fallback paths of every receipt-producing skill depend on it.
- **Explicit invocation.** The `disable-model-invocation` skills are lq-start, legalquants, lq-ask,
  lq-connect, lq-mirror and timenarratives. TESTING.md Part A tests routing for them, but no probe does.
- **Choosing the model for each worker.** docreview and diligence require it.

### Skills that a full pass would still leave unconfirmed

These skills have at least one ● capability rated None or Partial above:

- **HTML:** legaldesign, docreview, diligence.
- **FS (recursive walk, run folders):** these 17 skills:
  - legaldesign, lq-start, regulatory, wiki, lq-reflect, cite-check;
  - docreview, organize-case-docs, closing-bible, closing-checklist, conform, definition-check;
  - diligence, playbook-builder, playbook-review, read-redline, sigpack.
- **Hashing:** organize-case-docs.
- **NET (raw bytes):** regulatory.
- **EXEC (≥3.12, workspace access, sibling skills):** lq-start, conform, closing-bible, lq-reflect,
  my-lq-moment.

Taken together that is 18 of the 31 skills. Nine more have no ● at all, so they need no probe to run.
The last four depend on IN or OUT cells that the probes cover only in part: lq-apply, lq-connect,
pressuretest and document-discovery.

## Is a report produced?

No. This is how probe results are handled today:

1. **Recording.** TESTING.md says probe results are recorded "the same way" as skill tests: one UAT report
   per result, and one issue per probe labelled `probe`. But `.github/ISSUE_TEMPLATE/uat-report.yml`
   offers only Routing and Behaviour report types and a skill dropdown. A tester has no way to say which
   probe they ran, what the outcome was, or what the tenant's posture was. So a result ends up as a
   free-text comment on the probe's issue.
2. **Storage.** `probes.yaml` has no field for a result, a date, a tenant posture or an issue link.
   Nothing in the repository holds an observed outcome.
3. **Aggregation.** The build report and the site's `probes.html` render each probe's question, its pass
   and fail criteria and its `unlocks` list. They do not show results. The site shows each card's
   `cowork.tier` and `cowork.status`. Those are set by hand in each `skill.yaml`, and only `read-redline`
   is `probe-gated`. No probe outcome changes them automatically.
4. **Mapping from probes to skills.** `unlocks` in `probes.yaml` and the `probe:` references in the cards'
   `known_issues` disagree for nine of the fourteen probes:
   - **P2** is cited by eight cards but `unlocks: []`.
   - **P3** unlocks playbook-review, but that card cites P10.
   - **P4** and **P8** unlock sigpack, but sigpack cites only P2 and P9.
   - **P5** is cited by timenarratives but `unlocks: []`.
   - **P6** is cited by cite-check and lq-ask but `unlocks: []`.
   - **P7** unlocks read-redline, docreview and definition-check, which do not cite it; legaldesign
     cites it but is not unlocked by it.
   - **P10** is cited by playbook-review, which it does not unlock.
   - **P12** unlocks lq-ask and lq-connect, which do not cite it.

   A report built on either list would therefore disagree with one built on the other.
5. **A rule for verdicts.** Nothing defines how probe outcomes become "runs as intended", "runs on a
   fallback" or "cannot run" for a skill. The chart's ●/◐/○ levels are the missing input. They exist
   only as a Markdown table, not as data a tool can read.

## Plan to close the gaps

This plan is in steps. Each step can be reviewed on its own.

### Step 1 — Tie every probe to the chart's capability codes

- Add a field to each probe in `probes.yaml` listing the capability codes it tests, for example P1 →
  EXEC, BIN and P3 → IN, DOCX.
- With that field in place, the coverage table above can be generated instead of maintained by hand.
- Add a validation rule: every code in the chart must be tested by at least one probe, or be listed as
  deliberately unprobed with a reason.

### Step 2 — Add the missing probes and tighten the weak ones

Each new probe is one prompt with synthetic files, in the existing format.

| New probe | Capability | What a pass looks like |
|---|---|---|
| MCP connection | MCP | The harness connects to a named test MCP server, lists its tools and calls one. The reply quotes the tool's real result and names the server. |
| Folder walk | FS | Given a folder of 23 synthetic files in nested subfolders, the agent lists every relative path and gives the exact count. It also creates a sibling `run/` folder and writes a file into it. |
| File hash | hashing | It returns the SHA-256 of a supplied file, and the value matches one computed outside the harness. |
| Raw fetch | NET | It saves the raw bytes of a public page to a file, reports the byte length and the SHA-256, and both match one external fetch. |
| Fresh worker | SUB | It sends a sealed packet to a worker that must not see the parent's context; a canary phrase in the parent must not come back. It records which model the worker used. |
| HTML round trip | HTML | The user opens a generated page, ticks two boxes and downloads the JSON file. The agent reads the uploaded file back and names the two boxes. |
| Skills on disk | EXEC, FS | A probe skill runs a script that imports a sibling module and calls `../<other-skill>/scripts/x.py`. Both print. |
| PDF annotation | OUT | A returned PDF carries highlights and comment-pane notes at named places. |
| Docx from a template | OUT, DOCX | A bundled `.docx` template is copied, a table row is edited in place, and the house format survives. |
| Explicit invocation | — | A skill marked explicit-invocation-only does not fire on a matching prompt, but does fire when called by name. |

Tighten three existing probes:

- **P1:** require Python ≥3.12, and check `pdfinfo`, `pdftotext`, Chromium and an SVG rasteriser. Also
  require the script to read one attached file and write one file to the output folder.
- **P6 and P12:** report the raw byte length alongside the quotation.
- **P13:** record whether the run was a scheduled prompt or a process that outlives the turn.

### Step 3 — Record results as data

- Add a probe-results file, or one results file per harness or tenant. Each entry holds:
  - the probe id;
  - the outcome: `pass`, `fail`, `refused`, `fluent-fake` or `not-run`;
  - the date;
  - the client and version;
  - the posture (web search, browser use, admin actions);
  - the link to the issue it came from.
- Add a **Probe** report type to the UAT issue form, with a probe dropdown and an outcome dropdown. A
  maintainer then copies each result into the results file. A script that reads issues can do this later.

### Step 4 — Make the chart's levels readable by a tool

- Store each skill's ●/◐/○ level per capability as data: either in the card (`skill.yaml`) or in one
  capabilities file next to `probes.yaml`.
- Generate the Markdown matrix from that data so it cannot drift.
- Keep two profiles: upstream (the vendored skill) and Cowork (the adapted card). The adaptations
  deliberately lower some levels, so the two profiles differ.

### Step 5 — Define the verdict rule

These verdicts apply per harness profile, to the results on file:

| Verdict | Rule |
|---|---|
| **Runs as intended** | Every ● and every ◐ capability has a passing probe. |
| **Runs on a fallback** | Every ● passes, but at least one ◐ fails or is refused. The report names each lost ◐ and quotes the skill's own fallback wording (for example "provisional and unverified" or "not coverage-certified"). |
| **Cannot run** | At least one ● fails or is refused. The report names the probe. |
| **Untested** | No ● fails, but at least one ● has no result or no probe. The report says which. |

Optional (○) capabilities never change a verdict. They are listed as "also available" or "also missing".

The `unlocks` field then stops being maintained by hand. It follows from the capability codes plus the
levels. Add a validation rule that fails when a card cites a probe whose codes do not touch that card's
capabilities.

### Step 6 — Generate the report

- Add a section to `build-report.md` and a page on the site, built from the data in steps 1, 3 and 4.
- For each harness profile, show four lists matching the verdicts in step 5. Each skill's line gives the
  probes behind its verdict and their dates.
- Show a coverage table like the one above, generated rather than written.
- Add a "what to probe next" list: the untested ● cells, ranked by how many skills each would move out
  of Untested.
- Where a card's hand-set `cowork.status` disagrees with the computed verdict, flag it rather than
  overwrite it. The maintainer decides.

### Step 7 — Seed the report honestly

- On day one, with no results recorded, every skill except the nine with no ● is **Untested**. That is
  the true state, as the README says: "nothing here has been exercised in a live Cowork tenant".
- Put P7a first, because it costs nothing. Then run the new folder-walk, hash and HTML round-trip probes.
  Together they clear the only unprobed ● for twelve skills. The other six of the eighteen also need the
  tightened P1 or the raw-fetch probe.

## Method

- Read `probes.yaml` in full, docs/TESTING.md Part E, `.github/ISSUE_TEMPLATE/uat-report.yml`, and the
  probe handling in `tools/src/lqcowork/config.py`, `build.py`, `site/generate.py` and
  `tools/scripts/uat_issues.py`.
- Compared probe `unlocks` with each card's `known_issues[].probe` using a short script.
- Took the coverage judgements from the chart's matrix and from each probe's own pass and fail wording.
- No probe was run.
