# Gap-read: Cowork skills, scripts, and execution — verbatim source pull

Fetched via `curl -sL` with a Chrome user-agent header into
`/private/tmp/claude-501/-Users-houfu-Projects-lq-lq-plugin-cowork--claude-worktrees-cowork-capabilities-docs-b30f44/46547141-e7e3-4f63-aebb-16f93275d79f/scratchpad/gap-read-scripts/`,
HTML stripped with a python3 one-liner (removed `script`/`style`, stripped tags, `html.unescape`,
collapsed whitespace) and grepped. All six assigned pages returned HTTP 200 on the first attempt —
no WebFetch/jina fallback was needed. GitHub source files were fetched via `raw.githubusercontent.com`
and the GitHub Contents/Trees API (also all HTTP 200, no auth token used or needed for these public
repos).

---

## 1. https://microsoft.github.io/cat-agent-skills/

**Fetched:** Yes — `curl` direct, HTTP 200, 409,534 bytes.
**Title:** "CAT Agent Skills" (site description: "Discover, browse, and download reusable skills for
Cowork, Copilot Studio, and Scout AI agents.")
**Page date:** No page-level date metadata (Astro static site, no `ms.date`/`datePublished`). Individual
skill cards carry their own `createdAt`/`updatedAt` (see below).

### Quotes

1. **Heading: page intro (H1 "The gallery of skills for your AI agents")**
   > "Browse skills and plugins contributed by the community: drop-in instructions and script bundles that teach your agents new tricks. Find one, download the markdown (and scripts), and add it to Cowork, Copilot Studio, or Scout."

   Shows the catalogue's own framing: it explicitly distinguishes "instructions" from "script bundles" as two things a skill can carry, and names Cowork as one of three install targets.

2. **Platform filter counts**
   > "All platforms Cowork 52 Copilot Studio 71 Scout 43"

   52 of the catalogue's entries are tagged for Cowork specifically.

3. **Tag filter + card data attributes (structured `data-platforms`/`data-tags` on each `.skill-item`)**
   Cross-referencing `platforms` containing "Cowork" against `tags` containing "python" or "scripts"
   (tag-cloud shows "python 7 ... scripts 7" total across the whole catalogue) yields exactly four
   skills, all `data-type="skill"`, each with an individual named author (not "Microsoft"):
   - **agent harness explorer** — tags `diagnostics, runtime, python, capabilities, snapshots, scripts`; author "Chris Garty and Andrew Hess"
   - **chart builder** — tags `data, charts, matplotlib, scripts`; author "Adi Leibowitz"
   - **accessibility pass** — tags `accessibility, documents, presentations, powerpoint, quality, scripts`; author "Tim Karlsson"
   - **phi de-identifier** — tags `healthcare, hls, phi, privacy, redaction, hipaa, compliance, scripts`; author "Rafael Lopez Alcaraz"

   These are community submissions hosted in Microsoft's own `microsoft/cat-agent-skills` GitHub repo
   (PR-based, per the site's "Contribute a skill" flow), not Microsoft-authored skills.

Followed two of the four into their GitHub source (`microsoft/cat-agent-skills`, path
`submissions/<slug>/`, fetched via `raw.githubusercontent.com` and the Contents API, all HTTP 200):

### 1a. `submissions/agent-harness-explorer/SKILL.md` and `README.md`

4. **`SKILL.md`, heading "## Workflow" → "### Inspect (no save)"**
   > "1. Run `python scripts/capture_snapshot.py --catalog references/python-library-catalog.yaml --out snapshot.json`."

   A direct instruction inside SKILL.md's own workflow telling the agent to invoke `python` on a
   bundled script.

5. **`SKILL.md`, heading "## Bundled files"**
   > "`scripts/` — `inspect_python.py`, `inspect_runtime.py`, `inspect_tools.py`, `capture_snapshot.py`, `canonicalize_snapshot.py`, `compare_snapshots.py`, `generate_markdown_report.py`, `generate_library_inventory.py`, `generate_html_report.py`, `archive_snapshot.py`. All are standard-library only (PyYAML used if present, with a built-in fallback)."

   Ten script files ship with the skill, all `.py` (Python), all invoked with the literal `python`
   command per the workflow steps above.

6. **`README.md`, heading "## How the skill is used"**
   > "This is an Agent Skill: the agent loads SKILL.md and follows its workflow, running the bundled Python scripts to observe the runtime. You normally trigger it with natural-language requests."

   States plainly, in the skill's own documentation, that the agent (not just a human developer) runs
   the bundled scripts.

7. **`README.md`, heading "## Running the scripts directly"**
   > "You can also run the pipeline yourself from the `scripts/` folder. Requires Python 3.8+ (developed on 3.13); no third-party dependencies."

   The only place in any source fetched for this task that names a concrete Python version — but it is
   framed as instructions for a human running the scripts manually outside the agent, not a documented
   guarantee about what interpreter Cowork itself provides.

### 1b. `submissions/chart-builder/SKILL.md` and `README.md`

8. **`SKILL.md`, heading "## Usage"**
   > "CLI: python scripts/charts.py grouped_bar sales.csv --x region --y revenue --group quarter --stacked --out by_quarter.png"

   A second literal "run this script" instruction, again invoked as `python scripts/<file>.py`.

9. **`SKILL.md`, heading "## Bundled files"**
   > "`scripts/charts.py` — the toolkit: `load_data`, `apply_theme`, `save_fig`, and six chart functions (`bar`, `grouped_bar`, `line`, `scatter`, `histogram`, `pie`), plus a CLI. Depends on `matplotlib` and `pandas`; runs headless."

   One script file (`charts.py`, Python), and this is the only place found that names specific
   third-party Python packages (`matplotlib`, `pandas`) as dependencies of a Cowork-tagged skill.

10. **`README.md`, heading "## Why use this?"**
    > "Your agent can already make charts without any skill. When you ask for one, it writes a fresh, one-off chart script on the spot and runs it."

    A community author's claim that the base agent (grouped as Cowork/Copilot Studio/Scout) already
    has ad hoc script-writing-and-running behavior even with no skill installed at all.

11. **`README.md`, heading "## Requirements"**
    > "Runs in the standard Python environment for Cowork, Copilot Studio, and Scout, with matplotlib and pandas — nothing to install or set up."

    The single most specific claim found anywhere in this research naming a "standard Python
    environment for Cowork" with named pre-installed packages. Important caveat: this is third-party,
    community-authored text on a Microsoft-hosted gallery page — not an official Microsoft Learn
    statement, and no Learn page corroborates it.

**Silent on:** Neither the catalogue index nor either skill's source names which Python interpreter
binary/path Cowork actually invokes (both just assume `python` is on some PATH), names no sandbox or
isolation model, names no non-Python external binaries, and states no Cowork-enforced allow-list of
companion file types (the "no third-party dependencies" vs. "depends on matplotlib and pandas"
contradiction between the two skills is itself unresolved by any Microsoft page).

---

## 2. Copilot Developer Camp — Cowork labs

### 2a. https://microsoft.github.io/copilot-camp/pages/copilot-cowork/01-cowork-skills/

**Fetched:** Yes — `curl` direct, HTTP 200, 69,933 bytes.
**Title:** "Build your first skill - Copilot Developer Camp"
**Page date:** No date metadata found on this page.

1. **Heading: "Exercise 1: Understand what Agent Skills are" (lab intro paragraph)**
   > "At a high level, an Agent Skill is a structured instruction file that teaches Cowork when and how to execute a specific domain workflow. Skills are not generic prompts. They include intent signals, execution guidance, and output expectations so Cowork can reliably select and run the right behavior for a given request."

   Microsoft's own lab definition of a skill — closer to "instructions" framing than to "executable"
   framing, though it uses "execute" to describe the workflow the instructions describe.

2. **Heading: "Step 1: Review the role of skills in Cowork"**
   > "Cowork uses skills as reusable execution patterns. During a task, Cowork can load one or more skills based on conversation intent and then run a step-by-step workflow."

3. **Heading: "Step 2: Compare built-in skills and custom skills"**
   > "Custom skills complement built-in skills. They do not replace all of Cowork behavior, but they extend Cowork with your business context."

   Closest statement in this lab to what the agent can/cannot do — framed around skill scope, not
   about execution mechanics or a shell.

4. **Link followed:** the lab's "you can download the whole source code of the skill from
   [this file path]" points to
   `https://github.com/microsoft/copilot-camp/blob/main/src/cowork/weekly-status-mail/SKILL.md`.
   Checked via the GitHub Contents API: the folder `src/cowork/weekly-status-mail/` contains **only**
   `SKILL.md` — no `scripts/` folder, no companion files of any kind. This Microsoft-authored sample
   skill ships zero scripts.

**Silent on:** scripts, execution mechanism, Python, sandbox, installed packages, external binaries,
allowed file types — the lab discusses skill *authoring* (frontmatter, triggers, guardrails) but not
script execution at all in this exercise.

### 2b. https://microsoft.github.io/copilot-camp/pages/copilot-cowork/02-cowork-plugins/

**Fetched:** Yes — `curl` direct, HTTP 200, 77,173 bytes.
**Title:** "Build your first plugin - Copilot Developer Camp"
**Page date:** No date metadata found on this page.

1. **Heading: "Step 1: Review what a Cowork plugin contains"**
   > "Skills: instruction-driven workflows that tell Cowork how to execute domain tasks"

2. **Heading: same step, folder-tree code sample**
   ```
   plugin-root-folder/
   ├── manifest.json
   ├── color.png
   ├── outline.png
   └── skills/
           ├── skill-01/
           │   └── references/
           │       └── reference-file-01.md
           │       └── reference-file-02.md
           │   └── scripts/
           │       └── script-file-01.py
           │   └── SKILL.md
   ```
   Shown as illustrative structure only — this exact tree is not a real shipped example (see below).

3. **Heading: "Step 3: Add optional companion references and scripts"**
   > "For complex skills, keep SKILL.md concise and add supporting files such as: references/*.md for domain details and standards; scripts/* for repeatable utilities"

4. **Heading: inside a "vibe-coding" prompt template developers can paste into GitHub Copilot
   Agent Mode, under "### Quality bar"**
   > "Ensure scripts run on Windows PowerShell and common cross-platform shells when feasible."

   Important nuance: this line is about the plugin's *packaging/build* scripts (the `package.json`
   zip/deploy scripts a developer runs to build the `.zip`), not about the SKILL.md's own `scripts/`
   folder content or about what Cowork executes at runtime.

5. **Checked Microsoft's own shipped sample plugins in this repo for real scripts.** Via the GitHub
   Trees API (`src/cowork/` recursive listing, 23 entries) and Contents API:
   - `CopilotDevCamp-for-cowork/skills/{dev-camp-deck,dev-camp-document,foundry-research}/` — each
     folder contains **only** `SKILL.md`. No `scripts/`, no `.py` files anywhere.
   - `zava-claims-sso/skills/zava-claims-export/SKILL.md` — **this one is different.** Its own text,
     under heading "## Workflow", step 2 ("Build the report into scratch space"), reads:
     > "python scripts/build_report.py --in "<input.xlsx>" --out working/claims_report.xlsx --title "Insurance Claims Report""

     and under "## Guardrails" → "Large files":
     > "the script streams values with openpyxl; for very large exports (tens of thousands of rows) warn the user it may take a moment."

     This is a literal run-instruction naming a third-party Python package (`openpyxl`). **However**,
     querying the GitHub Contents API directly for
     `src/cowork/zava-claims-sso/skills/zava-claims-export/scripts` returns HTTP 404, and fetching
     `.../zava-claims-export/scripts/build_report.py` directly also returns HTTP 404 — the folder
     contains only the 5,786-byte `SKILL.md` itself. Microsoft's own copilot-camp repo ships a
     Cowork-targeted SKILL.md whose instructions assume a Python script that is not actually present
     in the committed repository.

**Silent on:** which interpreter runs the scripts, Python version, sandbox/isolation, and any
Cowork-enforced file-type allow-list. "PowerShell and cross-platform shells" (point 4) refers to
developer build tooling, not an agent-side shell.

---

## 3. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development

**Fetched:** Yes — `curl` direct, HTTP 200, 108,352 bytes. (The fetched HTML contains a boilerplate
"Access to this page requires authorization" fragment that appears to be a generic Learn-site sign-in
prompt component; the full article body — tables, code samples, FAQ — was present in the same
response, so the content is treated as fully retrieved.)
**Title:** "Build plugins for Copilot Cowork | Microsoft Learn"
**Page date:** `ms.date` meta = 2026-09-17T00:00:00Z; body also shows "Last updated on 2026-09-17".

### Grep pass (case-insensitive) over the stripped text for every requested term

| Term | Hits |
|---|---|
| script / scripts/ | multiple (folder trees, companion-file rules, FAQ) |
| execut | 4 (`bin/ (executables)`, `Executable utilities`, `Executed, not loaded into context`, `Tool execution`) |
| python | **0** |
| .py | 2 (both are the same illustrative filename, `extract-clauses.py`) |
| interpreter | **0** |
| runtime | 1 ("The agent connects them at runtime" — about connector *tools*, not scripts) |
| sandbox | **0** |
| shell | 2 (both "PowerShell", re: a legacy Windows-only conversion script for the CLI, unrelated to skill execution) |
| bash | **0** |
| node | **0** |
| binary | **0** |
| bin/ | 1 (see quote 2 below) |
| ASKILL | 12 (the full validation-code table, see quotes 6–7) |

### Quotes

1. **Heading: "In this article" (top-of-page overview, under "You can extend Cowork with:")**
   > "Skills: Prompt-based workflows that teach Cowork new domain expertise, such as financial analysis, legal research, or HR workflows."
   > "Connectors: Remote servers that give Cowork access to external data sources and APIs."

   This is the exact "Prompt-based workflows" framing referenced in the fact-check question.

2. **Heading: "### What's not converted" (table: "Claude plugin feature | Status")**
   > "bin/ (executables) | Not applicable"

   Context matters: this table documents what is lost when the `atk import openplugin` CLI converts a
   *Claude Code plugin* into an M365 app package. `bin/` here is a Claude-plugin feature being marked
   "Not applicable" to the conversion — it is not a statement about whether Cowork's own skill runtime
   executes binaries.

3. **Heading: "### Step 2: Add reference materials (optional)" (folder-tree code sample)**
   ```
   skills/
   └── contract-analysis/
       ├── SKILL.md               # Core workflow (~1,500-2,000 words ideal)
       ├── references/            # Deep-dive docs loaded on demand
       │   ├── clause-taxonomy.md
       │   └── risk-scoring.md
       └── scripts/               # Executable utilities
           └── extract-clauses.py
   ```

4. **Same section, "three layers" loading table**
   > "Scripts (scripts/) | Executed, not loaded into context | N/A"

5. **Same section, markdown template shown for a SKILL.md's own "## Additional Resources" list**
   > "- **`references/clause-taxonomy.md`**-Full taxonomy of contract clause types
   > - **`references/risk-scoring.md`**-Risk scoring methodology and thresholds
   > - **`scripts/extract-clauses.py`**-Automated clause extraction utility"

   Note this is shown only as a *reference listing* format (how to cite the script file to the agent
   as a resource) — the page never shows the literal invocation syntax (`python scripts/x.py`) that
   the real GitHub-hosted SKILL.md examples in sections 1 and 2 do.

6. **Heading: "## Validation rules" → "### Manifest-level validation" (full table)**
   > "ASKILL-M001 | `folder` is required on each `agentSkills` entry | Error
   > ASKILL-M002 | `agentSkills` array can have up to 20 items | Error
   > ASKILL-M003 | `folder` path can have up to 256 characters | Error"

7. **Heading: "### Package-level validation" (full table)**
   > "ASKILL-P001 | Folder referenced in manifest exists in ZIP | Check your ZIP structure | Error
   > ASKILL-P002 | Folder contains a `SKILL.md` file | Add missing `SKILL.md` | Error
   > ASKILL-P003 | `SKILL.md` has valid YAML frontmatter between `---` delimiters | Fix YAML syntax | Error
   > ASKILL-P004 | Frontmatter includes `name` field | Add `name:` to frontmatter | Error
   > ASKILL-P005 | Frontmatter includes `description` field | Add `description:` to frontmatter | Error
   > ASKILL-P006 | `name` matches the folder name (last path segment) | Rename folder or fix `name:` | Error
   > ASKILL-P007 | `name` is kebab-case | Use `my-skill` not `MySkill` or `my_skill` | Error
   > ASKILL-P008 | No duplicate `folder` values in the array | Remove duplicates | Error"

8. **Heading: "### Companion file validation"**
   > "The portal validates companion files (reference materials, scripts, and other files alongside SKILL.md) at upload and sync time:"

   followed by a rule list (max 20 companion files, 5 MB each / 10 MB total, relative paths only, no
   path traversal, no backslashes/null bytes, no hidden files, no Windows-reserved names, safe
   characters only). **None of these rows carry an ASKILL- code** — this table's columns are
   "Rule | Severity" only, unlike the two tables above which have a "Code" column. There is no
   file-*type*/extension allow-list anywhere in this section — "any file other than SKILL.md" counts
   as a companion file regardless of extension (`.py`, `.md`, or otherwise).

9. **Heading: FAQ**
   > "What's the maximum number of skills per package? Twenty (20) skills (per ASKILL-M002). For connectors, the limit is 10 per package."
   > "Can skills reference connector tools from the same package? Yes, and they should. Name the tools explicitly in your SKILL.md workflow (for example, "Use the search_case_law tool to..."). The agent connects them at runtime."

**Silent on:** Which interpreter/process executes `scripts/*` (no "python", "interpreter", "runtime
environment", "sandbox", "node", or "bash" tied to script execution anywhere on the page), no installed
-package list, no external-binary story beyond the unrelated Claude-plugin `bin/` conversion note, and
no file-*extension* allow-list for companion files (only path-safety and size rules).

---

## 4. ASKILL-* validation rules — search of the Microsoft 365 Agents Toolkit source

Per the task instructions, since nothing was found, here is exactly what was searched:

1. **Confirmed repo identity.** `OfficeDev/teams-toolkit` and `OfficeDev/microsoft-365-agents-toolkit`
   resolve to the same GitHub repository (id 348248652; the toolkit was renamed). Default branch: `dev`.
   The npm package `@microsoft/m365agentstoolkit-cli` (registry fetched, HTTP 200; latest `1.1.16`)
   lists `"repository": {"url": "git+https://github.com/OfficeDev/microsoft-365-agents-toolkit.git"}` —
   i.e. the same source tree, so no separate npm-only search was needed.

2. **Full recursive file tree.** Fetched
   `GET /repos/OfficeDev/microsoft-365-agents-toolkit/git/trees/dev?recursive=1` (HTTP 200,
   `"truncated": false`, 13,122 entries). Filtered all paths case-insensitively for `"skill"` (266
   matches — every `SKILL.md`, test fixture, and doc in the repo, listed and reviewed) and for
   `"openplugin"` (61 matches). **No path in the entire repository contains the substring "askill".**

3. **Fetched and grepped (case-insensitive, for the literal string `ASKILL`) every source file in**
   `packages/fx-core/src/component/generator/openPlugin/`: `validation.ts` (24,180 bytes),
   `skillValidation.ts` (2,670 bytes), `errors.ts` (225 bytes), `fileSystem.ts` (6,799 bytes),
   `parser.ts` (15,848 bytes), `mapper.ts` (14,190 bytes), `types.ts` (7,179 bytes). **Zero matches
   for "ASKILL" in any of these files.**

4. **`skillValidation.ts` does implement its own, differently-coded SKILL.md checks** (used by the
   `atk import openplugin` CLI command, not the web-portal upload flow). Quoted verbatim from the
   fetched source:
   > `"folder name must contain only lowercase letters, numbers, and single hyphens"`
   > `"SKILL.md must begin with YAML frontmatter"`
   > `` `frontmatter name must exactly match the parent folder '${skillName}'` ``
   > `` `frontmatter description must contain 1-${SKILL_DESCRIPTION_MAX_LENGTH} characters` `` (1024)
   > `"frontmatter license must be a non-empty string"`
   > `` `frontmatter compatibility must contain 1-${SKILL_COMPATIBILITY_MAX_LENGTH} characters` `` (500)
   > `"frontmatter metadata must map string keys to string values"`
   > `"frontmatter allowed-tools must be a string"`

   This file checks name pattern, YAML validity, name/description/license/compatibility/metadata/
   `allowed-tools` — but never touches companion files, scripts, or file extensions at all, and uses
   none of the ASKILL- codes or exact wording from the Learn page.

5. **JSON Schema cross-check.** Fetched the newest of 30 versioned Teams/M365 manifest schemas in the
   repo, `packages/manifest/src/json-schemas/teams/v1.30/MicrosoftTeams.schema.json` (126,895 bytes),
   and extracted its `agentSkills` property definition verbatim:
   ```json
   {
     "type": "array",
     "description": "Agent skill declarations following the Agent Skills open standard (agentskills.io). Each entry references a SKILL.md folder.",
     "maxItems": 20,
     "items": {
       "type": "object",
       "properties": { "folder": { "type": "string", "maxLength": 256 } },
       "required": ["folder"],
       "additionalProperties": false
     }
   }
   ```
   The three numeric limits match ASKILL-M001/M002/M003 exactly, but the schema file itself never
   contains the string "ASKILL", and it constrains only the `folder` path string — it says nothing
   about what may exist inside that folder (no script/file-type mention at all).

6. **Web search** for the literal strings `"ASKILL-M001"`, `"ASKILL-P001"`, and `"ASKILL-" github.com
   OfficeDev` returned no relevant hits — only unrelated third-party projects coincidentally named
   "askill" (e.g., an unrelated "package manager for AI agent skills" at askill.sh, and a GitHub user
   named Askill), none connected to Microsoft or this validation system.

**Conclusion:** the ASKILL-* codes and their exact rule text, as far as this search could determine,
exist only on the Microsoft Learn page itself (Section 3 above). The open-source Agents Toolkit repo
implements a related but independently-worded, non-ASKILL-coded local check (`skillValidation.ts`) plus
a JSON Schema that numerically matches the three manifest-level limits — but the full rule set shown on
the Learn page (all eight ASKILL-P00x package-level rules, and the entire unlabeled companion-file
rule table) is not present anywhere in this public repository, consistent with that layer running in
Microsoft's closed-source submission portal rather than in open-source tooling.

---

## 5. https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/code-interpreter

**Fetched:** Yes — `curl` direct, HTTP 200, 58,651 bytes.
**Title:** "Code Interpreter Capability for Declarative Agents for Microsoft 365 Copilot | Microsoft Learn"
**Page date:** `ms.date` meta = 2026-06-18T00:00:00Z; body confirms "Last updated on 2026-06-18".

### Quotes

1. **Heading: "In this article" (opening paragraphs)**
   > "Code interpreter is an advanced tool designed to solve complex tasks via Python code. It uses the reasoning model to write and run code, enabling users to solve complex math problems, analyze data, generate visualizations, and more. After the code runs, code interpreter outputs the results and the related code that it generates."

2. **Heading: "## Code interpreter capability examples"**
   > "The code interpreter capability uses the reasoning model to allow declarative agents to write and run Python code in a sandboxed environment."

   This is the one explicit "sandboxed" claim found in this entire research pass — but it is scoped to
   the **CodeInterpreter capability of declarative agents**, a manifest-`capabilities` feature, not to
   Cowork's skill/`scripts/` mechanism.

3. **Heading: "## Enable code interpreter in Microsoft 365 Agents Toolkit"**
   > "You must be using version 1.2 or later of the declarative agent manifest schema to add the CodeInterpreter capability."

4. **Heading: "### Create graphs and charts"**
   > "When the user selects the </> Code button, the agent provides the corresponding Python code."

### Cowork mentions

Grepped the entire stripped page text (case-insensitive) for "cowork": **zero occurrences.** The word
"Cowork" does not appear anywhere on this page.

**Silent on:** any relationship between this CodeInterpreter capability and Cowork's skills/scripts
system (the two are never connected on this page), which specific sandbox technology is used, any
non-Python language, installed package list beyond "Python code," and external binaries.

---

## 6. https://support.microsoft.com/en-us/microsoft-365-copilot/get-started-with-researcher-in-microsoft-365-copilot

**Fetched:** Yes — `curl` direct, HTTP 200, 138,183 bytes.
**Title:** "Get started with Researcher in Microsoft Copilot | Microsoft Support"
**Page date:** `<meta name="updated_at" content="2026-09-09 04:56 PM" />` (only date marker found on
this page; no `ms.date`/`datePublished`/`dateModified` meta present).

### Quote

1. **Heading: "## Is Researcher the same as Deep Research?"**
   > "Researcher and Deep Research were very similar experiences that helped customers create detailed research reports and analyses. As part of ongoing updates to Copilot, Deep Research has been retired and Researcher is now the in-depth research experience available to Microsoft 365 Premium and Pro subscribers. Existing Deep Research reports are not deleted."

**Silent on:** scripts, execution, interpreters, installed packages, external binaries, sandboxing,
and allowed file types — this page's entire subject is the Researcher/Deep Research feature identity
and retirement, unrelated to Cowork's extensibility mechanics. It was fetched solely to confirm the
retirement claim and its date.

---

# Summary

- Microsoft's own Learn page (cowork-plugin-development, updated 2026-09-17) confirms a skill's
  `scripts/` folder is "Executed, not loaded into context," gives `scripts/extract-clauses.py` as the
  example, and separately calls skills "Prompt-based workflows" — both framings coexist on the same
  page. It never names an interpreter, sandbox, package, or binary, and its `bin/ (executables): Not
  applicable` row is about converting a *Claude plugin's* bin/ folder, not about Cowork's own runtime.
- Real, fetched SKILL.md files answer the "do Microsoft's sample skills ship scripts the agent is told
  to run" question with a clear yes for the community catalogue (`cat-agent-skills`): both
  `agent-harness-explorer` and `chart-builder` contain literal `python scripts/<file>.py` instructions
  inside their own workflow text, with ten and one `.py` files respectively.
- Microsoft's own copilot-camp teaching repo is split: three sample Cowork skills ship zero scripts,
  but `zava-claims-sso/skills/zava-claims-export/SKILL.md` instructs `python scripts/build_report.py
  ...` and cites the `openpyxl` package — yet that script file returns HTTP 404 in the repo; it's
  referenced but not actually shipped.
- One community README (chart-builder) makes the single most specific infrastructure claim found
  anywhere: "the standard Python environment for Cowork... with matplotlib and pandas" — but this is
  third-party text on a Microsoft-hosted gallery, not an official Learn statement, and no Learn page
  corroborates it.
- The ASKILL-* codes exist, verbatim, only on the Learn page. A full-repo search (13,122 files, no
  truncation) of OfficeDev/microsoft-365-agents-toolkit found zero occurrences of "ASKILL"; the repo's
  own SKILL.md validator uses different, uncoded error text, and its JSON Schema matches the three
  manifest-level numeric limits but defines nothing about companion-file types or scripts.
- The code-interpreter page confirms Microsoft has a "sandboxed" Python capability, but it is for
  **declarative agents**, not Cowork — "Cowork" appears zero times on that page.
- The Researcher support page (updated 2026-09-09) confirms "Deep Research has been retired and
  Researcher is now the in-depth research experience."
- No page in this pass — Learn, copilot-camp, or the toolkit source — ever names what interpreter,
  binary, or process actually executes a Cowork skill's `scripts/*`.

Full detail, headings, and all verbatim quotes with context: `gap-read-scripts.md` (this file) at
`/private/tmp/claude-501/-Users-houfu-Projects-lq-lq-plugin-cowork--claude-worktrees-cowork-capabilities-docs-b30f44/46547141-e7e3-4f63-aebb-16f93275d79f/scratchpad/gap-read-scripts.md`.
