# Cowork capability claims: verification

19 September 2026

Scope: the README sentence in "What is deliberately left out" of `houfu/lq-plugin-cowork`, and the parallel
claims in the README intro, the README skill table, CHANGELOG, CONTRIBUTING, NOTICE and `docs/CONTRACT.md`
section 8. The product under test is **Microsoft** 365 Copilot Cowork, documented at
`learn.microsoft.com/en-us/microsoft-365/copilot/cowork/`. It is not Anthropic's Claude Cowork; that
confusion appears in live search results and every such source was excluded.

---

## 1. Summary

Not one of the four words survives as written. "No filesystem" is true only of a local disk, and the README
contradicts it two paragraphs earlier by describing work from the Cowork Input and Output folders. "No shell"
is contradicted by Microsoft's own plugin development page, which says a skill's `scripts/` folder is
executed, and contradicted again by two other Microsoft pages that call a skill prose-only. "No network
fetch" is refuted at the host level by Microsoft's web search article, which states in Microsoft's own voice
that it applies to Cowork, and by a dedicated Learn page for Edge browser automation. "No transcript access"
rests on documentary silence rather than a documented denial, and past sessions are in fact stored and
re-enterable.

The maintainer's decision is untouched. The fourteen skills should still stay out, and a remote MCP connector
declared under `agentConnectors` remains the honest route. What changes is the reason given. The reasons that
survive the evidence are: no local disk and no working directory that outlives a task; a script runtime that
Microsoft documents as existing but never specifies, with no named interpreter, no named packages, no binary
path and a 20 file, 10 MB companion cap; web reach that exists at the host level and is tenant-controlled,
with no skill-level fetch primitive and no raw bytes or hashes; and session logs that exist as compliance
records and as resumable tasks, with no documented way for a skill to read a past session. Stated that way the
claim is stronger than the four words, and it stops the README contradicting itself.

| Claim | Verdict | Confidence | In one line |
|---|---|---|---|
| no filesystem | Misleading as written | High | True of a local disk only: Cowork reads and writes OneDrive-backed Input and Output folders, but has no working directory that outlives a task and cannot delete OneDrive or SharePoint content. |
| no shell | Misleading as written, and contested by Microsoft's own documentation | Medium | One Microsoft page says a skill's `scripts/` folder is "Executed, not loaded into context"; two others call a skill prose-only; no page anywhere names an interpreter, a package or a binary. |
| no network fetch | Misleading as written | High | The host reaches the web through Bing-backed search and, where an admin enables it, Edge browser automation; what is absent is a skill-level fetch that yields raw bytes a receipt could hash. |
| no transcript access | Undocumented, not documented-absent; misleading as written; accurate only on the narrow upstream meaning | Low to medium | Nothing documents a skill reading a past session's log, but sessions persist and are resumable, and Purview retains Cowork conversation transcripts. |

---

## 2. What Cowork has and lacks, per claim

Tiers below rank Microsoft documentation first, then machine-readable artefacts, then Microsoft announcements
and Microsoft-authored samples, then practitioner and community sources. Practitioner and community items are
observed or asserted behaviour and are ranked below Microsoft's documentation throughout.

### 2.1 Filesystem

Verdict: misleading as written. Confidence: high.

Microsoft denies local-disk access and in the same breath names the store Cowork does work with. Session files
live in OneDrive, outputs persist there after the session ends, and custom skills load from a OneDrive folder.
What is genuinely absent is the upstream capability: arbitrary absolute paths, a private `~/.lq/` store, a run
directory, a ledger written beside a deal folder, and deletion. The strongest single fact is not "no
filesystem" at all but the per-task environment: it is destroyed when the task finishes and users cannot see
it, so nothing a skill writes there outlives the task.

Two scoping points, both applied from the skeptic's review. The companion-file path rules are a **packaging**
rule about the contents of the uploaded `.zip`, not a runtime prohibition on where a skill may write; the real
support for the sibling-folder point is the local-device denial plus the OneDrive-only model. And nothing in
the record documents that a skill **cannot** write a file to the user's own OneDrive Cowork folder and read it
back in a later session. That is undocumented, not denied, and the wording must not harden it.

- "Cowork can't access or edit files stored locally on your device. It works with files in OneDrive and SharePoint." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq — Microsoft documentation, page dated 2026-09-14 — Bearing: Microsoft's own statement of the by-design limitation. It supports "no local disk" precisely and refutes "no filesystem" in the same sentence by naming the store Cowork does use.
- "Input folder / Files you provided as context for the session. / Output folder / Files Cowork created. Each file has Download and Preview buttons." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: documents the exact folders the README's own first paragraph relies on. This is a documented read and write surface a skill works from.
- "You can also access files that Cowork creates directly in your OneDrive Cowork folder at any time." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: output is not ephemeral. Files Cowork writes persist outside the session, which is the opposite of "no filesystem" at the level a lawyer cares about.
- "Cowork uses the files only for the duration of the task and removes the temporary environment when the task finishes. Users can't view or access this environment." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-admin-governance — Microsoft documentation, 2026-09-14 — Bearing: the nearest thing to a working directory is per-task and destroyed. This, not "no filesystem", is the real reason a `~/.lq/` store or a run ledger cannot be ported.
- "Cowork can't delete files or folders in OneDrive or SharePoint." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq — Microsoft documentation, 2026-09-14 — Bearing: one specific absent file operation, correctly scoped to OneDrive and SharePoint content. It is not a general statement that Cowork deletes nothing.
- "Cowork inherits your permissions, so it can access only the files and emails you can already access. If you don't have access to a file or email, Cowork can't access it either." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq — Microsoft documentation, 2026-09-14 — Bearing: the reach model is the user's own permissions. Nothing here carves out a private area a skill controls, and nothing here forbids reading back a file the user can reach.
- "Use relative paths only (no absolute paths) / No path traversal ( .. segments)" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: **packaging only.** These are companion-file rules applied to the uploaded package, so they rule out shipping a package that addresses absolute paths. They are not a documented runtime rule about where a running skill may write.
- "Cloud hosting means files are not stored locally, security is strongly enforced, and your tasks keep running even when your laptop is off." — https://www.microsoft.com/en-us/copilot/blog/2026/06/16/copilot-cowork-is-now-generally-available — Microsoft announcement, 2026-06-16 — Bearing: Microsoft frames the architecture as cloud hosted with no local storage, corroborating the narrow "no local disk" reading rather than the broad "no filesystem" one.
- "Copilot Cowork uses file storage outside the sandbox for a variety of purposes; for example, to output a file to the user. To support this, there is a service that syncs files between the storage and the sandbox." — https://www.promptarmor.com/resources/microsoft-copilot-cowork-sandbox-bypass — Practitioner, observed behaviour, security vendor write-up dated 2026-08-25 (the vulnerability it describes was reported 24 June 2026 and mitigated 19 August 2026) — Bearing: describes the mechanism as a sandbox plus a file sync service rather than a mounted filesystem, consistent with the Learn pages and explaining why arbitrary local paths do not exist. Ranked below Microsoft's documentation.

### 2.2 Shell

Verdict: misleading as written, and contested by Microsoft's own documentation. Confidence: medium.

Microsoft's plugin development page says a skill's `scripts/` folder is executed rather than loaded as text,
labels the folder "Executable utilities", and names an example `.py` file. A second Microsoft page names
script execution as a background operation and confines its non-execution promise to pre-publish static
checks. Against that, the Customize page calls a skill "instructions to the AI" and the manage-plugins page
calls skills "Prompt-based workflows". The documentation does not reconcile this, so the repo's position is
provisional and a tenant probe is still needed. "No shell" is wrong as a flat statement; "Cowork executes your
scripts" would be equally wrong to assert in the repo's voice.

The bar the upstream skills set is not "a bundled script runs". It is bundled Python plus pdfplumber,
python-docx, LibreOffice, Poppler and Tesseract, parallel workers and detached runs. Against that bar, a
whole-page grep of the plugin development page returns zero hits for python, interpreter, sandbox, bash, node
and binary in any sense tied to the Cowork runtime. Nothing documents what a script runs in.

**What the new gap read adds, and whether it moves the verdict.** It strengthens the "something executes" side
without moving the verdict, and I am saying so rather than moving it silently. Microsoft's own teaching repo
and Microsoft's own community catalogue both ship Cowork-targeted SKILL.md files whose workflow text tells the
agent to run `python scripts/<file>.py`, which is much harder to square with a prose-only reading than the
Learn table alone. Three things hold the verdict at medium. First, every one of those interpreter and package
claims is community-authored or sample text, not a Microsoft statement about the runtime. Second, the single
Microsoft-authored sample that would prove it, `zava-claims-export`, instructs `python scripts/build_report.py`
and cites `openpyxl`, yet that script returns HTTP 404 in Microsoft's own repository, so the instruction is
written against a runtime nobody in the public record has exercised. Third, the ASKILL-* validation codes exist
verbatim only on the Learn page and appear nowhere in the 13,122-file Agents Toolkit tree, so the layer that
would enforce anything about `scripts/` is closed-source. On the narrow sub-point "a bundled script runs", the
evidence is now strong. On the claim actually under test, which is whether a Cowork skill has a shell, nothing
has changed.

- "Scripts ( scripts/ ) / Executed, not loaded into context / N/A" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: Microsoft's own skill-loading table says scripts are executed rather than read as text. This alone makes the flat words "no shell" wrong.
- "scripts/ # Executable utilities" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: the same page's example folder tree labels the directory as executable utilities, so the table row is not a one-off wording slip.
- "scripts/extract-clauses.py - Automated clause extraction utility" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: the page's sample skill names a Python file as a resource. It is the only concrete script Microsoft shows, and it is shown as a resource listing, never with an invocation syntax.
- "Some background operations, like script execution, run without displaying individual steps. This approach keeps the session focused on results." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: a second Microsoft page names script execution as something Cowork does during a session, independently of the plugin development page.
- "Static checks review the skill's structure and limits, scan any bundled code for security issues, and check the skill's text for prompt-injection patterns. Code is never executed during static checks." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: confirms skills are expected to carry bundled code at all, and confines the non-execution promise to pre-publish checks. Read carefully this is a negative scoping, not an affirmative statement that code runs elsewhere.
- "run the skill against realistic prompts. Cowork evaluates the output, the actions the skill takes, and how efficiently it uses tools." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: behavioural checks run a skill and watch what it does, which presupposes a skill does things rather than only being read.
- "A skill runs as instructions to the AI. Only upload skills from sources you trust. The first time you upload a skill, Cowork shows a reminder about this." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-customize — Microsoft documentation, 2026-09-15 — Bearing: a Microsoft page that flatly describes a skill as instructions, in tension with the two pages above. This is the contradiction that keeps the verdict at medium.
- "Skills: Prompt-based workflows that teach Cowork new domain expertise, such as financial analysis, legal research, or HR workflows." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-manage-plugins — Microsoft documentation, 2026-09-01 — Bearing: a fourth Microsoft page characterises skills as prompt-based workflows. The same phrase also appears in the plugin development page's own overview.
- "Maximum companion files / 20 / Maximum size per companion file / 5 MB / Maximum total companion size / 10 MB / Download timeout (all companions) / 15 seconds" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: the payload budget is far below what the upstream pipelines need. This is a concrete, citable reason the fourteen stay out that does not depend on claiming nothing runs.
- "The following Claude plugin features aren't yet supported in the Microsoft 365 manifest:" and "commands/ (slash commands) / Not yet supported" and "bin/ (executables) / Not applicable" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17, re-fetched and confirmed 19 September 2026 for this report — Bearing: **scoped.** This is the "What's not converted" table describing what the `atk import openplugin` conversion carries over from a Claude plugin. It shows `commands/` is not yet supported rather than permanently absent, and it is not a rule that a Cowork package may not contain a binary. Nothing documents a path for one either.
- "Path to the folder within the app package that contains the SKILL.md file." — https://developer.microsoft.com/json-schemas/teams/v1.28/MicrosoftTeams.schema.json — Machine-readable — Bearing: the v1.28 `agentSkills` entry declares exactly one property, a folder path. There is no execution, runtime, capability or permission flag anywhere in the machine-readable contract, so everything known about script execution rests on prose.
- "Agent skill declarations following the Agent Skills open standard (agentskills.io). Each entry references a SKILL.md folder." — `packages/manifest/src/json-schemas/teams/v1.30/MicrosoftTeams.schema.json` in https://github.com/OfficeDev/microsoft-365-agents-toolkit — Machine-readable — Bearing: the newer v1.30 schema in Microsoft's open-source toolkit constrains only the folder path string and says nothing about what may be inside it. A full-repo search of 13,122 files found zero occurrences of "ASKILL", so the package-level rules on the Learn page are enforced somewhere closed-source.
- "At a high level, an Agent Skill is a structured instruction file that teaches Cowork when and how to execute a specific domain workflow. Skills are not generic prompts. They include intent signals, execution guidance, and output expectations so Cowork can reliably select and run the right behavior for a given request." — https://microsoft.github.io/copilot-camp/pages/copilot-cowork/01-cowork-skills/ — Microsoft-authored sample and lab — Bearing: Microsoft's own teaching material sits on the instructions side of the split. The three sample skills in this lab's repository folder ship only `SKILL.md` with no `scripts/` folder at all.
- `python scripts/build_report.py --in "<input.xlsx>" --out working/claims_report.xlsx --title "Insurance Claims Report"` and "the script streams values with openpyxl; for very large exports (tens of thousands of rows) warn the user it may take a moment." — `src/cowork/zava-claims-sso/skills/zava-claims-export/SKILL.md` in https://github.com/microsoft/copilot-camp — Microsoft-authored sample — Bearing: a Microsoft-authored Cowork SKILL.md instructs a literal Python invocation and names a third-party package. The referenced `scripts/` folder and `build_report.py` both return HTTP 404 in the repository, so the sample assumes a runtime it does not ship or demonstrate.
- "Browse skills and plugins contributed by the community: drop-in instructions and script bundles that teach your agents new tricks. Find one, download the markdown (and scripts), and add it to Cowork, Copilot Studio, or Scout." — https://microsoft.github.io/cat-agent-skills/ — Microsoft-hosted catalogue, community-authored submissions — Bearing: the catalogue's own framing distinguishes instructions from script bundles and names Cowork as an install target. 52 of its entries are tagged for Cowork.
- "This is an Agent Skill: the agent loads SKILL.md and follows its workflow, running the bundled Python scripts to observe the runtime. You normally trigger it with natural-language requests." — `submissions/agent-harness-explorer/README.md` in https://github.com/microsoft/cat-agent-skills — Community, asserted behaviour, hosted in a Microsoft repository — Bearing: a Cowork-tagged skill states that the agent itself runs its bundled Python. Its SKILL.md workflow contains the literal instruction "1. Run `python scripts/capture_snapshot.py --catalog references/python-library-catalog.yaml --out snapshot.json`." Author-asserted, not Microsoft-documented.
- "Runs in the standard Python environment for Cowork, Copilot Studio, and Scout, with matplotlib and pandas — nothing to install or set up." — `submissions/chart-builder/README.md` in https://github.com/microsoft/cat-agent-skills — Community, asserted behaviour, hosted in a Microsoft repository — Bearing: the single most specific infrastructure claim found anywhere. No Microsoft page corroborates it, and a second Cowork-tagged skill in the same catalogue describes itself as standard-library only with no third-party dependencies. Not usable as a basis for a repo claim.
- "The code interpreter capability uses the reasoning model to allow declarative agents to write and run Python code in a sandboxed environment." — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/code-interpreter — Microsoft documentation, 2026-06-18 — Bearing: cited to show what a documented Microsoft code-execution primitive looks like when it exists. It is scoped to declarative agents, and the word "Cowork" appears zero times on that page, so it proves nothing about Cowork.
- "The agent decides to execute the Skill's bundled scripts. The script generates a full document consistency report, but it also initiates an exploit." — https://www.promptarmor.com/resources/microsoft-copilot-cowork-sandbox-bypass — Practitioner, observed behaviour, 2026-08-25; vulnerability reported 24 June 2026, mitigated 19 August 2026 — Bearing: a bundled skill script actually ran. The vendor is not a neutral observer and the specific bug it describes is patched, so this corroborates execution without establishing today's intended posture.

### 2.3 Network fetch

Verdict: misleading as written. Confidence: high.

Cowork reaches the public web by routes Microsoft documents. The web search article states in Microsoft's own
voice that its contents apply to Cowork, says Cowork has no user-facing web search toggle, and describes an
admin policy option that disables web search in Cowork by name, which only makes sense if Cowork has it.
Browser use has a dedicated Learn page and drives a real Edge tab on the user's device. Declared connectors
make genuine outbound HTTPS calls carrying a `copilot-cowork/1.0` User-Agent. The repo's own 18 September 2026
assessment already conceded "web access, which Cowork has", so the README contradicts the repo's own research.

Two corrections carried from the skeptic. The route through Bing-backed search is documented at the
Copilot-family level and attached to Cowork by a note and an admin switch, not by any Cowork page describing a
web tool a skill can invoke, so "three documented routes" slightly overstates it. And the GA blog of 16 June
2026 **predates** the maintainer's 18 September 2026 assessment by three months; it cannot be cited as
evidence that the product moved after the assessment. What it does show is a scope shift over time: the GA post
scoped browser use to Frontier, and the what's-new page records it moving to general availability in August
2026 while the Learn page of 16 September 2026 presents it as tenant-admin-gated and off by default.

What is absent is the upstream capability rather than reach. Nothing documents a primitive that hands a skill
the raw bytes at a URL so it can hash them into a SHA-256 receipt. Bing grounding returns a search service's
rendering; browser use returns a rendered page in the user's own Edge under tenant policy; a connector is a
declared MCP server the package author must operate. Upstream's own rule forbids quoting a web-fetch tool's
rendering in place of the raw bytes, so what Cowork offers is precisely what upstream refuses to accept. The
regulatory skill stays out, but for receipts, not reach.

- "The information about web search in this article also applies to Researcher , Analyst , and Cowork in Microsoft Copilot. While web search isn't a prerequisite for using Researcher, Analyst, and Cowork, enabling web search is recommended to get the most value out of using them. Researcher has a Web search toggle accessible in the input box. Analyst and Cowork don't have a Web search toggle for users." — https://learn.microsoft.com/en-us/microsoft-365/copilot/manage-public-web-access — Microsoft documentation, 2026-08-18 — Bearing: Microsoft states directly that its web search article covers Cowork. The single clearest refutation of "no network fetch" as a statement about the host.
- "When web search is enabled, Microsoft Copilot and Microsoft Copilot Chat may fetch information from the Bing search service when information from the web helps to provide a better, more grounded response." — https://learn.microsoft.com/en-us/microsoft-365/copilot/manage-public-web-access — Microsoft documentation, 2026-08-18 — Bearing: names the mechanism as fetching from the Bing search service, which is a search rendering, not the publisher bytes an upstream receipt is computed over. It supports both halves of the verdict.
- "If the IT admin chooses the Disabled in Microsoft Copilot Work mode; Enabled in Microsoft Copilot Web mode and Microsoft Copilot Chat option, web search in Researcher and Cowork in Microsoft Copilot will be disabled." — https://learn.microsoft.com/en-us/microsoft-365/copilot/manage-public-web-access — Microsoft documentation, 2026-08-18 — Bearing: an admin control that disables web search in Cowork by name presupposes Cowork has it, and shows the capability is tenant-dependent. A shipped skill cannot rely on it either way.
- "Microsoft Copilot Cowork can complete browser automation for you in Microsoft Edge on your device, using the sites you're already signed in to." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-local-browser — Microsoft documentation, 2026-09-16 — Bearing: a second documented web-reaching route. It is automation on the user's device, not a server-side fetch, which is why it cannot yield reproducible publisher bytes.
- "Tenant admins must enable Cowork browsing by performing the following steps. This feature is disabled by default." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-local-browser — Microsoft documentation, 2026-09-16 — Bearing: browser use is off unless an admin turns it on, so a shipped skill cannot assume it. This supports keeping the regulatory skill out while showing the flat denial is wrong.
- "Browser use via Edge. In Frontier, Cowork can browse the web through a local Edge browser following the enterprise policies in place for your users today." — https://www.microsoft.com/en-us/copilot/blog/2026/06/16/copilot-cowork-is-now-generally-available — Microsoft announcement, 2026-06-16 — Bearing: browser use was announced as a Frontier-scoped capability three months **before** the repo's 18 September 2026 assessment, so this is not evidence of a change after the assessment. It is evidence that the scope of the capability has been moving.
- "This feature moved from Frontier to general availability to all Microsoft 365 Copilot tenants. Cowork can complete web tasks for you in Microsoft Edge on your device, using your existing sign-ins and your organization's policies. Requires that Edge is installed." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/whats-new — Microsoft documentation, 2026-09-14, entry dated August 2026 — Bearing: dates the Frontier-to-GA move for browser use, which is why every browser-use statement in the repo needs a date on it.
- "No. Skills-only packages work well for prompt-based workflows. Connectors are only needed when your skill requires live data from an external system." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: confirms a skills-only package, which is what this repo ships, has no network channel of its own and that any outbound reach must be declared separately. This is the sentence that actually justifies the repo's design.
- "User-Agent request header / Every outbound request Cowork sends to your server / copilot-cowork/1.0" — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development — Microsoft documentation, 2026-09-17 — Bearing: Cowork makes genuine outbound HTTP requests to a declared connector's server. That is real network capability, scoped to connectors rather than available ad hoc to a skill.
- "An agent connector represents a mechanism to enable agents to access information from systems outside of Microsoft 365, often via an MCP Server. Other mechanisms include using OpenAPI descriptions for calling external HTTP APIs." — https://developer.microsoft.com/json-schemas/teams/v1.28/MicrosoftTeams.schema.json — Machine-readable — Bearing: the manifest schema itself defines connectors as the declared channel to outside systems, which is the machine-readable support for the repo's stated honest route of a remote MCP connector under `agentConnectors`.
- "The agent runs in a sandbox, which is intended to block network access and prevent the agent from running code that reaches any untrusted services." — https://www.promptarmor.com/resources/microsoft-copilot-cowork-sandbox-bypass — Practitioner, observed behaviour, 2026-08-25; reported 24 June 2026, mitigated 19 August 2026 — Bearing: a vendor's characterisation, not Microsoft's, that the control on skill code is the sandbox's network boundary. It is the clearest statement that the skill compute environment and the host have different network postures, which is the layering the README collapses.
- "This vulnerability was reported to Microsoft on June 24, 2026, and has been mitigated as of August 19, 2026." — https://www.promptarmor.com/resources/microsoft-copilot-cowork-sandbox-bypass — Practitioner, 2026-08-25 — Bearing: date-bounds the vendor's egress findings. The bypass was patched a month before this review, so it is evidence that skill code once reached the network through a bug, not evidence of the intended posture today.

### 2.4 Transcript access

Verdict: undocumented, not documented-absent; misleading as written; accurate only on the narrow upstream
meaning. Confidence: low to medium.

On the upstream meaning, which is the host agent's own session logs read across past sessions, no source
documents that a Cowork skill can do it. The plugins page scopes plugin skills explicitly to the current
conversation. But the negative rests on silence plus one scoping sentence, and three facts make the flat words
wrong about the product. Past sessions persist and are re-enterable from a recent-tasks list. A skill can
reference earlier messages inside the conversation it is in, so on a resumed session the "current
conversation" is itself a past session. And Purview treats Cowork conversation transcripts as records in
scope for eDiscovery, stored in the user's mailbox.

**What the new gap read adds, and whether it moves the verdict.** It closes the lead the earlier review left
open and firms up the "undocumented" label on both sides, without changing it. Session resumption is
documented only as a UI list of recent tasks; no page says what resuming restores to the model as opposed to
the screen. None of the three core Cowork pages uses the word "memory" at all. The Copilot memory and
chat-history documentation is written entirely in terms of Copilot Chat and never names Cowork in its body
text. The Graph `aiInteractionHistory` API never names Cowork, names Teams, Word and Outlook as its examples,
and has no delegated permission at all, so there is no path for an in-session skill acting as the user. Against
that, one newly found support page does say Cowork saves conversation and task history and retains task logs,
but it is explicitly scoped to the personal-accounts Preview edition, not the enterprise tenant product. On
balance this tightens the negative half without licensing "Cowork cannot", so the verdict label stands and the
confidence sits at the medium end of low-to-medium.

- "Plugin skills work within the current conversation context. They can read files you attached, reference earlier messages, and coordinate with other active skills." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugins — Microsoft documentation, 2026-08-27 — Bearing: the strongest positive statement of scope. A plugin skill sees this conversation, including earlier messages in it, and nothing wider. It supports the decision while showing "no transcript access" is too absolute.
- "The Cowork home page has a chat input where you can type or speak your request. Below it, a list of your recent tasks appears, so you can resume a previous session." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: past sessions persist and can be resumed. This is why the reworded sentence must survive resumption rather than assuming a session is always new.
- "Check the home page for your recent tasks. Select any task to return to that session without starting over." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: "without starting over" is the only hint at what resuming changes, and the page never defines it. This is the exact point the tester probe has to settle.
- "Select a task to open its session and continue working." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: the same UI-level statement again, with no distinction drawn between what is restored to the model and what is merely displayed.
- "Select any task to jump back into its session." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq — Microsoft documentation, 2026-09-14 — Bearing: the FAQ agrees with the Use Cowork page in identical terms and is equally silent on context restoration.
- "Select a task to open its details, review its run history, and edit, pause, resume, or delete it." — https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork — Microsoft documentation, 2026-09-14 — Bearing: the only "history" feature described is a scheduled task's own past runs, not a conversational transcript a skill could read.
- "Copilot memory is available to Copilot Chat users with and without a Microsoft Copilot license." — https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory — Microsoft documentation, 2026-09-02 — Bearing: Microsoft's memory feature is scoped to Copilot Chat. Cowork is not named anywhere on this page, so whether the memory system reaches Cowork sessions is undocumented.
- "Memories, which include saved memories, details inferred from chat history and custom instructions, are stored in the user's Exchange mailbox in a hidden folder." — https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory — Microsoft documentation, 2026-09-02 — Bearing: locates memory in a mailbox folder, distinct from any session-log store, and the only programmatic access the page describes is an admin script that toggles the control.
- "Copilot doesn't remember every detail from your previous chats, only what's useful for personalizing its responses to your questions and tasks." — https://support.microsoft.com/en-us/microsoft-365-copilot/how-microsoft-365-copilot-chat-history-works — Microsoft documentation, 2026-08-18 — Bearing: even where memory exists, Microsoft denies verbatim recall. Memory is selective inference, not a replayed transcript, so it would not serve an upstream reflect-style workflow even if it applied to Cowork.
- "Conversation and task history : Your prompts and Copilot's responses are saved so you can review past tasks." and "Microsoft Copilot Cowork for personal accounts is currently in Preview." — https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-uses-stores — Microsoft documentation, 2026-09-15 — Bearing: the clearest statement that Cowork itself saves prompts and responses, and the callout that scopes the whole article to the personal-accounts Preview edition rather than the enterprise product. Records exist; the page says nothing about a skill reading them.
- "In addition, some Cowork interactions are subject to both automated and human review for product improvement and digital safety purposes. Task logs, screenshots, and outputs are retained for limited periods to support functionality, safety, and troubleshooting." — https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-uses-stores — Microsoft documentation, 2026-09-15, personal-accounts Preview — Bearing: task logs are retained for Microsoft's own purposes. Microsoft-side retention infrastructure, not an in-session read capability.
- "Conversation transcripts — The full text of a user's Cowork conversations, including prompts and responses." — https://learn.microsoft.com/en-us/purview/ai-copilot-cowork — Microsoft documentation, 2026-06-22 — Bearing: Microsoft uses the word transcript for Cowork conversations and puts them in scope for eDiscovery. The records exist, so a flat "no transcript access" misdescribes the product even where it correctly describes what a skill can reach.
- "Because user prompts and responses for AI apps are stored in a user's mailbox, you can create a case and use search when a user's mailbox is selected as the source for a search query." — https://learn.microsoft.com/en-us/purview/ai-copilot-cowork — Microsoft documentation, 2026-06-22 — Bearing: locates the transcripts in the user's mailbox behind an eDiscovery case. That is an admin surface. Nothing here gives a running skill a route to them.
- "The system automatically generates audit logs when a user interacts with Copilot, Cowork, or an AI application." — https://learn.microsoft.com/en-us/purview/audit-copilot — Microsoft documentation, 2026-08-26 — Bearing: confirms automatic capture of Cowork interactions in the compliance log, again on the admin side. This is the distinction the reworded sentence must draw.
- "Get all Microsoft 365 Copilot interaction data, including user prompts to Copilot and Copilot responses. This API captures the user intent, the resources accessed by Copilot, and the response to the user for Microsoft 365 apps such as Teams, Word, and Outlook." — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/aiinteractionhistory-getallenterpriseinteractions — Microsoft documentation, 2026-02-23 — Bearing: the nearest thing to a transcript API. Cowork is never named on the page, its permission table offers only the application permission `AiEnterpriseInteraction.Read.All` with delegated access marked "Not supported", so there is no stated path for a skill acting as the user.
- "The AI interaction history API returns interactions recorded by Microsoft 365 AI experiences that write to the interaction history service." — https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/resources/aiinteractionhistory — Microsoft documentation, 2025-12-04 — Bearing: coverage is defined by which experiences write to a shared service, and Cowork is never listed among them. Whether Cowork sessions are even in the store is undocumented.
- "Opus 4.7 was more comprehensive in its search for recently edited documents; it expanded exfiltration to include every document used in previous Cowork Copilot sessions that week, as well as the files stored in more typical document locations that were found when the model was set to 'Auto'." — https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files — Practitioner, observed behaviour, 2026-05-07 — Bearing: some cross-session recall of documents used previously. That is not reading a past session's transcript, but it is the closest counter-evidence found and is part of why confidence is not higher.

---

## 3. Conflicts and gaps

### Microsoft against Microsoft on script execution

Four Microsoft pages, all current, do not agree. `cowork-plugin-development` (2026-09-17) says a skill's
`scripts/` folder is "Executed, not loaded into context", labels it "Executable utilities" and names
`scripts/extract-clauses.py`. `use-cowork` (2026-09-14) names "script execution" as a background operation and
scopes its non-execution promise to static checks. Against them, `cowork-customize` (2026-09-15) says "A skill
runs as instructions to the AI" and `cowork-manage-plugins` (2026-09-01) says "Skills: Prompt-based workflows".
The documentation never reconciles this. Microsoft's own samples are split the same way: three copilot-camp
Cowork skills ship only a `SKILL.md`, while a fourth instructs `python scripts/build_report.py` against a
script that is not in the repository. The most probable reading is that a skill is primarily prose and that a
`scripts/` folder, when present, is executed, but the repo should say that the pages disagree and that its
position is provisional until a tenant probe settles it.

### What remains undocumented

- **The runtime.** No Microsoft page names the interpreter, language, version, preinstalled packages,
  dependency install path or external binaries for `scripts/`. A whole-page grep of the plugin development page
  returns zero hits for python, interpreter, sandbox, bash, node and binary as descriptions of the Cowork
  runtime; the only PowerShell hits are the legacy conversion script that runs on the author's own machine. The
  one specific claim in the record, a community README's "standard Python environment for Cowork... with
  matplotlib and pandas", is contradicted by a second Cowork-tagged skill in the same catalogue describing
  itself as standard-library only.
- **Persistence of a skill-written file across sessions.** What is documented is that the per-task environment
  is destroyed and that outputs persist in the user's OneDrive Cowork folder. Whether a skill can write a file
  at a fixed OneDrive path and read it back in a later session without the user pointing at it is neither
  documented nor denied. The repo must not claim it is impossible.
- **Whether resumption restores context to the model.** Every page describes the recent-tasks list in UI terms:
  "resume a previous session", "return to that session without starting over", "jump back into its session",
  "open its session and continue working". None says whether prior messages re-enter the model's context or
  only the screen.
- **Whether web search is addressable by a skill.** Web search is documented at the Copilot-family level and
  attached to Cowork by a cross-product note and an admin switch. No Cowork page describes a web tool a skill
  can invoke by name, and nothing says whether Bing grounding is reachable by a skill at all or is only a
  model-grounding step.

### The repo against itself

The maintainer's 18 September 2026 assessment says of cite-check that "Public case search needs web access,
which Cowork has", and calls a web-fetch tool's rendering "Cowork's only retrieval", while the README says
Cowork has no network fetch. The README says no filesystem in the "left out" section and describes working
from the Input and Output folders in its first paragraph. The README says no transcript access while its own
skill table promises a depositions skill that "mines the transcript afterwards", meaning a deposition
document. `docs/CONTRACT.md` section 8 is the careful one and is closest to correct already; the looser
sentences in README, CHANGELOG, CONTRIBUTING and NOTICE should be brought up to it rather than the reverse.

### Deep Research: two features sharing a name

Microsoft has retired a Deep Research feature, and Microsoft still lists a Deep Research skill in Cowork.
These are not the same thing, and the report should not collapse them. The Researcher support page, updated 9
September 2026, says "Researcher and Deep Research were very similar experiences that helped customers create
detailed research reports and analyses. As part of ongoing updates to Copilot, Deep Research has been retired
and Researcher is now the in-depth research experience available to Microsoft 365 Premium and Pro
subscribers." That sentence is scoped to consumer plans: it says what is now available to Microsoft 365
Premium and Pro subscribers, not what a Cowork tenant has, and the page never mentions Cowork. On the Cowork
side, the same fourteen-skill built-in list, still naming "Deep Research", appears on three independent Cowork
pages dated 8 and 14 September 2026, the later of them five days after the retirement notice. The safe reading
is that a consumer research experience was retired in favour of Researcher while a Cowork built-in of the same
name remains documented. The repo should keep Deep Research in its list, date the list, and have a tester
confirm the name in a live tenant rather than rename it on the strength of a page about a different plan. The
Cowork skill list is a reader-recorded finding from those three pages; it is not one of the 38 quotations that
went through the verbatim check.

### The two packaging channels with different limits

These are easily mistaken for a contradiction. The packaged plugin path caps `agentSkills` at 20 per manifest
(ASKILL-M002, confirmed as `maxItems: 20` in the v1.28 and v1.30 schemas), with 20 companion files, 5 MB each
and 10 MB total. The Customize upload path allows a `.md` up to 1 MB or an archive up to 10 MB compressed, 50
MB uncompressed and up to 100 files. The OneDrive folder drop allows 50 custom skills per user. The repo
records only the packaged-plugin figures and should say which channel each number belongs to.

Two smaller conflicts carry forward into the contract. On encrypted files, the FAQ says flatly that Cowork
cannot read them while the Purview article says an AI app can return label-encrypted data to a user holding
EXTRACT as well as VIEW; cards should keep the stricter rule and note the qualification. On connector
authentication, the v1.28 schema declares `ApiKeyPluginVault` and `cowork-manage-plugins` lists it, while
`cowork-plugin-development` says API key authentication is not available in Cowork yet; treat the schema as
declaring a field that is not yet enabled.

---

## 4. Proposed wording

The repo text below uses the README's own voice, including em-dashes where the README already uses them.

### 4.1 README, "What is deliberately left out"

> Each of the fourteen leans on machinery a Cowork package cannot carry — a local disk and a working directory
> that outlives the task, bundled binaries such as LibreOffice and Tesseract, raw fetched bytes that can be
> hashed into a receipt, and the agent's own past session logs. Cowork does reach the web where a tenant allows
> it, and Microsoft documents a skill's `scripts/` folder as executed — but no page names the interpreter, the
> packages or the binaries a script could count on, companion files are capped at 20 files and 10 MB, and
> nothing hands a skill a URL's raw bytes to hash. Shipping these as prose would ship the instructions without
> the machinery — a skill that promises receipts it cannot produce is worse than no skill.

### 4.2 README, first paragraph (intro phrase)

Replace "adapted to a host with no filesystem and no shell" with:

> adapted to a host that works from your OneDrive files rather than a local disk, and that never says what a
> bundled script would run in — so these cards ship none

The rest of the sentence, "they work from the files in your Cowork Input and Output folders", is accurate and
should stay.

### 4.3 README skill table, depositions row

Replace "mines the transcript afterwards" with:

> mines the deposition transcript afterwards

### 4.4 CHANGELOG

> - Fourteen of the thirty-one upstream skills deliberately do not ship. Each is a thin instruction layer over
>   machinery a Cowork skills-only package cannot carry: arbitrary local paths and a working directory that
>   outlives the task, bundled binaries behind a script runtime Microsoft documents as executed but never
>   specifies, raw fetched bytes that can be hashed into a receipt, or the agent's own past session logs.

### 4.5 CONTRIBUTING

> Each is a thin instruction layer over a local Python pipeline, a worker runtime, a network fetch, a `~/.lq/`
> store or host session transcripts. Cowork has no local disk and no working directory that outlives a task;
> Microsoft documents a skill's `scripts/` folder as executed but names no interpreter, no packages and no
> binaries, while other Microsoft pages call a skill prose-only, so we ship no scripts and treat the point as
> unsettled; companion files are capped at 20 files and 10 MB; a skills-only package has no network channel of
> its own, and outside a connector you operate, nothing gives a skill a URL's raw bytes to hash; and nothing
> documents a skill reading a past session. None of the five survives the port intact.

### 4.6 NOTICE

> They have been adapted to run inside Microsoft 365 Copilot Cowork, which works from OneDrive and SharePoint
> rather than a local disk, documents a skill's `scripts/` folder as executed without specifying what runs it,
> and does not yet support a `commands/` invocation grammar (as of Microsoft's plugin development page of 17
> September 2026).

### 4.7 docs/CONTRACT.md section 8, "Cowork facts the cards are written against"

Full replacement. Verified against Microsoft documentation read on 19 September 2026; each bullet that turns on
a fast-moving fact carries its own date.

> - **No local disk; a OneDrive-backed file surface instead.** "Cowork can't access or edit files stored
>   locally on your device. It works with files in OneDrive and SharePoint." Session files live in the user's
>   OneDrive `Cowork` folder; the side panel shows an Input folder and an Output folder; files Cowork creates
>   remain reachable in that folder after the session; custom skills live in `/Documents/Cowork/skills/`.
>   Companion files inside a package must use relative paths with no `..` traversal — that is a packaging rule
>   about the uploaded `.zip`, not a rule about where a running skill may write.
> - **No working directory that outlives the task.** While a task runs, Cowork processes files in a temporary
>   isolated environment inside the Microsoft 365 service boundary, which "removes the temporary environment
>   when the task finishes" and which "Users can't view or access". Nothing written there survives, so no card
>   may rely on a run directory, a scratch path or a ledger that outlasts the task.
> - **State between sessions is undocumented, not forbidden.** Nothing says a skill cannot write a file into
>   the user's own OneDrive `Cowork` folder and read it back later; nothing says it can, either. No card may
>   depend on it until a tenant probe settles it, and no card may claim it is impossible.
> - **No deletion of OneDrive or SharePoint content.** "Cowork can't delete files or folders in OneDrive or
>   SharePoint." Attached files must be under 200 MB. Never instruct deletion and never promise clean-up; say
>   that any intermediate file remains in the Output folder, and name it. (This rule is about file content.
>   Users can still delete a skill or a scheduled task from the UI.)
> - **Encrypted and labelled files.** The Cowork FAQ says Cowork cannot read encrypted files even where the
>   user has access; the Purview article says an AI app can return label-encrypted data to a user holding
>   EXTRACT as well as VIEW. Cards take the FAQ's stricter rule and never depend on reading a labelled or
>   password-protected file.
> - **Scripts: Microsoft's own pages disagree, and our position is provisional.** The plugin development page
>   (17 September 2026) says a skill's `scripts/` folder is "Executed, not loaded into context", labels it
>   "Executable utilities" and names `scripts/extract-clauses.py`; the Use Cowork page (14 September 2026)
>   names "script execution" as a background operation and says code "is never executed during static checks".
>   The Customize page (15 September 2026) says "A skill runs as instructions to the AI" and the manage-plugins
>   page (1 September 2026) calls skills "Prompt-based workflows". Nothing reconciles them. No Microsoft page
>   names an interpreter, a language version, an installed package, a dependency install path or an external
>   binary; "python" does not appear on the plugin development page at all. Cards therefore ship no scripts and
>   give every step a host-native path — because a script's runtime cannot be relied on, not because nothing
>   runs. Revisit after the script probe.
> - **Companion budget.** 20 companion files per skill, 5 MB each, 10 MB total, 15 second download timeout.
>   There is no documented file-type allow-list; the rules are about path safety and size.
> - **Manifest features not yet supported** (plugin development page, 17 September 2026). The conversion table
>   marks `commands/` (slash commands), `agents/` (sub-agents) and `hooks/` (event handlers) "Not yet
>   supported", and `settings.json` and `bin/` (executables) "Not applicable". That table describes what the
>   `atk import openplugin` conversion carries over from a Claude plugin, so it is not a rule that a Cowork
>   package may not contain a binary — but nothing documents a path for one either. Treat `commands/` as not
>   yet supported rather than permanently absent, and re-check the table.
> - **Two packaging channels with different limits.** Plugin package: up to 20 skills per manifest (ASKILL-M002,
>   `maxItems: 20` in the v1.28 schema), up to 10 connectors, 256-character folder path (ASKILL-M003).
>   Customize upload: a `.md` up to 1 MB, or a `.zip` / `.skill` archive up to 10 MB compressed, 50 MB
>   uncompressed, up to 100 files. OneDrive folder drop: up to 50 custom skills per user.
> - **Web reach exists, is tenant-controlled, and no card may depend on it** (as at September 2026; this is the
>   fastest-moving fact here). Microsoft's web search article states it applies to Cowork, Cowork has no
>   user-facing web search toggle, and an admin policy option can disable web search in Cowork by name — so
>   search may simply be off in a given tenant. Browser use is Edge automation on the user's own device, web
>   client only, and "disabled by default" until a tenant admin enables it (Learn page of 16 September 2026);
>   it was announced Frontier-scoped in the GA post of 16 June 2026 and recorded as moving to general
>   availability in August 2026. A skills-only package has no network channel of its own. The only declared
>   channel is `agentConnectors`: Streamable HTTP over HTTPS with JSON-RPC 2.0, up to 10 per package,
>   anonymous or OAuth vault or dynamic client registration, with outbound requests carrying
>   `copilot-cowork/1.0`. API-key auth is declared in the schema but stated as not yet available in Cowork.
> - **No receipts without a connector you operate.** Outside a declared `agentConnectors` MCP server, nothing
>   documents a way for a skill to obtain a URL's raw bytes or to hash them. So no card may promise a fetch
>   receipt, a SHA-256 of a source, or a quotation guaranteed to come from publisher bytes rather than a search
>   or browser rendering. A remote MCP connector remains the honest route for anything that needs one.
> - **Sessions and transcripts** (as at September 2026). Plugin skills "work within the current conversation
>   context. They can read files you attached, reference earlier messages". Past sessions persist and can be
>   reopened from the recent-tasks list — "resume a previous session", "Select any task to jump back into its
>   session" — so on a resumed session the current conversation is itself a past session. What resumption
>   restores to the model, as opposed to the screen, is undocumented. Nothing documents a tool or API by which
>   a skill reads another session's log: Copilot memory and chat history are documented for Copilot Chat and
>   never name Cowork; the Graph `aiInteractionHistory` API never names Cowork and offers only an application
>   permission, with delegated access "Not supported". Purview retains Cowork "Conversation transcripts" for
>   audit and eDiscovery in the user's mailbox (Purview page of 22 June 2026; audit page of 26 August 2026),
>   but that is an admin surface, not something a skill can read. Where a card says "transcript" it must mean a
>   document the lawyer supplies — a deposition or a meeting transcript — never a session log.
> - **Built-in skills to hand off to, by exact name**, as listed by Microsoft on three Cowork pages dated 8 and
>   14 September 2026: Word, Excel, PowerPoint, PDF, Email, Scheduling, Calendar Management, Meetings, Daily
>   Briefing, Enterprise Search, Communications, Deep Research, Adaptive Cards, and App (Frontier). **Keep
>   "Deep Research" in this list.** A separate Researcher support page, updated 9 September 2026, says "Deep
>   Research has been retired and Researcher is now the in-depth research experience available to Microsoft 365
>   Premium and Pro subscribers" — but that is a statement about consumer plans, it never mentions Cowork, and
>   three Cowork pages still name Deep Research as a Cowork built-in. Treat them as two features sharing a
>   name. Have a tester confirm the name in a live tenant before it is changed here; do not rename it in this
>   repo on the strength of a page about a different plan. HTML, Markdown, CSV and PDF files render in Cowork's
>   preview pane.

---

## 5. Tester probes

Seven probes. Each names the undocumented point it settles and gives both signals, because for several of them
a plausible-looking answer is the worst outcome and must be recorded as such.

**Probe 1 — Does a bundled script actually run.** Package a skill with a tiny script that prints a unique
marker, the interpreter name and version, and the working directory. Type: *"Use the script-probe skill on the
file I attached. Run its bundled script and paste the script's raw output back to me exactly as it printed,
including the line that starts LQPROBE-MARKER and the interpreter version line. Do not summarise it and do not
write the report yourself."*
Settles: the contradiction between the plugin development and Use Cowork pages, which say `scripts/` is
executed, and the Customize and manage-plugins pages, which call a skill prose-only. This is the probe the
provisional CONTRACT bullet is waiting on.
Pass: the reply carries the exact marker string and a real interpreter version the tester never typed. That
proves execution and names the runtime.
Fail: Cowork paraphrases, says it cannot run scripts, or builds the report from the `SKILL.md` prose alone.
Record a fabricated marker separately — it is a different and worse result than a refusal, and it is the
failure mode that would most damage a shipped card.

**Probe 2 — What the runtime actually has installed.** Type: *"Run the script-probe skill's dependency check
and paste its raw output. I want the exact lines it prints for each of pdfplumber, pypdf, python-docx, and for
the results of shutil.which for soffice, pdftoppm and tesseract. Then tell me whether it could install a
missing package."*
Settles: the entirely undocumented package and binary story, and the one specific community claim in the
record, that Cowork has a "standard Python environment... with matplotlib and pandas". This decides whether
read-redline, sigpack, closing-bible, definition-check, conform, diligence and docreview could ever be ported
rather than replaced by a connector.
Pass for the current decision: the imports fail, all three binaries are absent, or the probe never runs.
Fail, meaning the decision needs revisiting: the document libraries import cleanly, or any of `soffice`,
`pdftoppm` or `tesseract` resolves to a path. Capture the verbatim output either way, because a partial result
(libraries present, binaries absent) changes the calculus for some skills and not others.

**Probe 3 — Web reach, and whether it yields bytes or a rendering.** Type: *"Fetch
https://www.iana.org/help/example-domains and quote the first full sentence of the page word for word. Then
tell me three things: whether you retrieved the page itself or a search result about it, the exact byte length
of what you retrieved, and the SHA-256 hash of those bytes."*
Settles: whether this tenant reaches the web at all, given that web search is admin-controllable and browser
use is off by default, and the undocumented point that matters more, whether anything gives a skill raw bytes
it can measure and hash.
Pass for the rewording: the quote comes back (reach exists) but the byte length and hash are refused or
obviously invented. Record which route Cowork says it used, and record the tenant's web search and browser use
settings, since both change the result.
Fail: an accurate byte length and a hash the tester can reproduce with `shasum` on the same file. That would
overturn the receipts point and put the regulatory skill back on the table.

**Probe 4 — Does anything survive between sessions.** Type: *"Create a file called lq-probe-ledger.json in my
Output folder containing exactly {"probe":"LQ-2026-09","run":1}. Then tell me the full path where you saved
it."* Then close the session; the next day start a brand new session, attach nothing, and type: *"Read
lq-probe-ledger.json from my OneDrive Cowork folder and tell me the value of run, then increment it to 2 and
save it back."*
Settles: the point the CONTRACT bullet now leaves open rather than denying — whether a skill can write a file
and read it back in a later session, and whether it needs the user to point at it.
Pass for the rewording: the file is created at a stated OneDrive path, and in the new session Cowork reads it
back only because the user pointed at it, with no unprompted recall of the earlier run.
Fail, meaning the wording needs loosening further: Cowork volunteers the earlier run without being pointed at
the file. Record separately whether the write-back in session two succeeds, since that alone settles whether a
ledger pattern is viable through the user's own folder.

**Probe 5 — Whether a skill can reach a different past session.** Type: *"What did we work on in my previous
Cowork session? Quote the exact words I typed to you in that session, and tell me how you retrieved them."*
Ask this in a **new** session, not a resumed one.
Settles: the transcript claim on its upstream meaning, the agent's own session logs, and the gap this review
could not close from documentation — whether Copilot memory, which Microsoft documents only for Copilot Chat,
reaches Cowork.
Pass for "nothing documents reading a past session": Cowork says it cannot see previous sessions, or offers a
vague topical recollection with no verbatim text and no stated mechanism.
Fail: it reproduces the tester's actual earlier wording. Run it twice, once the same day and once after a
week, and note whether the tenant has Copilot memory enabled, because a positive result would directly affect
whether lq-reflect could be ported.

**Probe 6 — Whether a skill has any private place to keep state.** Type: *"Create a folder named lq-store next
to the file I attached, and save a file called state.json inside it. Then list everything in that folder and
give me its full path. If you cannot create a folder there, tell me exactly where you can create one."*
Settles: whether anything resembling the upstream `~/.lq/` store or a working folder beside a deal folder
exists, and whether a skill can choose a location rather than being confined to the session Output folder. This
is the fact behind leaving legalquants, lq-ask and lq-connect out.
Pass for the rewording: Cowork refuses, or writes only into the session Output folder or the OneDrive Cowork
folder, and says so plainly.
Fail: it creates a folder at an arbitrary location beside the source document and lists it back with a full
path. Record separately if it claims success and silently does nothing — that failure mode is the one most
likely to produce a skill that promises receipts it cannot produce.

**Probe 7 — What resumption actually restores (new, opened by the session gap read).** In session one, state a
distinctive fact in an unusual phrasing and get a response. The next day, reopen that same task from the recent
tasks list and type: *"Without scrolling up and without me repeating it, quote back the exact sentence I typed
to you yesterday in this task, and tell me whether you are reading it from our conversation or reconstructing
it."*
Settles: the single undocumented point every Microsoft page skirts — whether resuming a task re-injects prior
messages into the model's context or only renders them on screen. It decides whether "a skill sees the current
conversation" means anything different on a resumed session, which is what the reworded transcript sentence
turns on.
Pass for the CONTRACT wording as drafted: Cowork quotes the sentence verbatim and attributes it to the
conversation. That confirms resumption restores context, and the wording's careful "on a resumed session the
current conversation is itself a past session" is correct and necessary.
Fail, meaning the wording can be tightened: it cannot produce the sentence, or produces a paraphrase, which
would mean resumption is a UI affordance only. Either result is publishable; neither changes the decision on
the fourteen.

---

## 6. Contested points and dropped evidence

### Contested points

- **None of the skeptic's twelve rewording problems was rejected.** All twelve are fixed in section 4:
  persistence between sessions is now undocumented rather than denied; "cannot delete" is scoped to OneDrive
  and SharePoint files and folders; the intro phrase no longer implies there is no runtime; the script-execution
  conflict and the provisional-pending-a-probe position are stated in CONTRACT section 8; the binaries point is
  scoped to the conversion table; Bing search is caveated as admin-controllable; the connector exception now
  governs the raw-bytes denial; the transcript wording survives session resumption; the README skill table cell
  becomes "mines the deposition transcript afterwards"; `commands/` is "not yet supported" and dated; the
  browser-use and Purview bullets carry dates; and CONTRACT section 8 says plainly that Microsoft's pages
  disagree.
- **Whether "no shell" deserved the harsher grade.** The adjudicator graded it "inaccurate / high"; the skeptic
  refuted that as the harshest verdict resting on the thinnest evidence, since the adjudicator's own conflicts
  list says the docs never reconcile the point and a probe is needed. Resolved in the skeptic's favour at
  medium. The underlying fact stays contested until probe 1 runs.
- **Whether "no transcript access" deserved "accurate".** The adjudicator graded it accurate with
  qualification; the skeptic refuted that as documentary silence dressed up as a finding, given documented
  session resumption. Resolved in the skeptic's favour. A reader who thinks Purview records or a resumed
  session count as "transcript access" would call the original sentence simply wrong.
- **The Microsoft-hosted catalogue contradicts itself on the runtime.** `chart-builder` claims a "standard
  Python environment for Cowork... with matplotlib and pandas"; `agent-harness-explorer`, in the same
  Microsoft-hosted catalogue, describes its scripts as standard-library only with no third-party
  dependencies. Both are community-authored. Neither can ground a repo claim.
- **PromptArmor is not a neutral observer.** Both write-ups are security-vendor disclosures. The sandbox bypass
  was reported 24 June 2026 and mitigated 19 August 2026, so its egress findings describe a patched bug, not
  today's posture. Its findings are used only to corroborate Microsoft's documentation, never to carry a point
  on their own.
- **Encrypted files.** The FAQ's flat "cannot read encrypted files" and Purview's EXTRACT-plus-VIEW carve-out
  are not reconciled by Microsoft. Cards keep the stricter rule and note the qualification.
- **Connector API-key auth.** The v1.28 schema declares `ApiKeyPluginVault` and `cowork-manage-plugins` lists
  it, while `cowork-plugin-development` says it is not available in Cowork yet. Treated as a declared field
  that is not yet enabled.
- **The personal-accounts Preview edition.** The support page that says Cowork saves "Conversation and task
  history" and retains "task logs" is explicitly scoped to Cowork for personal accounts, in Preview. Whether the
  enterprise tenant product shares that data model is not stated. It is cited as a documented fact about that
  edition only.
- **"Deep Research" names two different features.** The Researcher support page of 9 September 2026 says Deep
  Research has been retired in favour of Researcher, "available to Microsoft 365 Premium and Pro subscribers",
  which is a consumer-plan statement that never mentions Cowork; three Cowork pages dated 8 and 14 September
  2026 still list Deep Research as a Cowork built-in. Both are Microsoft, and nothing connects them. The
  contract keeps the name, dates the list, and leaves confirmation to a tester in a live tenant.

### Dropped evidence

- **`cowork-network-endpoints`, "All Cowork service traffic flows through a single host pattern."** Deleted
  entirely. An admin firewall allow-list would never list a server-side Bing grounding call, so its silence
  supports nothing. It was being used as an argument from silence.
- **The GA blog's chronology bearing.** The claim that the 16 June 2026 GA post "post-dates the repo's 18 Sep
  2026 assessment framing" is factually backwards and is corrected, not repeated. The post predates the
  assessment by three months.
- **"Three documented routes" to the web.** Softened. Web search reaches Cowork by a cross-product note and an
  admin switch, not by any Cowork page describing a web tool a skill can invoke.
- **`bin/ (executables) / Not applicable` as proof that binaries are forbidden.** Demoted to what it is: a row
  in the "What's not converted" table describing the `atk import openplugin` conversion from a Claude plugin.
  The repo must not say Cowork forbids binaries.
- **PromptArmor's "session chat history" quote.** Not used to soften the transcript verdict. It was reached
  through a bug mitigated on 19 August 2026 and concerns the current session, not past ones.
- **`learn.microsoft.com/en-us/agent-framework/agents/skills`, "Scripts bundled in archive-type skills are
  never executed".** Dropped. Microsoft's voice, but a different product (the Agent Framework SDK). Reading it
  as a statement about Cowork would be a serious error in the opposite direction.
- **The code interpreter pages.** Kept only as a contrast. The capability is scoped to declarative agents and
  "Cowork" appears zero times on the page.
- **Excel add-in "Copilot skills" and Copilot Studio "skills".** Dropped as different systems that share the
  word. The Excel page's claim that Copilot "creates a runtime... and executes the scripts in your skill"
  would badly mislead a reader on the shell question.
- **Microsoft Q&A "Memory in Cowork".** Dropped as evidence. Its only answer is labelled an AI answer, carries
  Microsoft's own "AI-generated content may be incorrect" disclaimer, is unaccepted, and cites no
  Cowork-specific source.
- **All Anthropic Claude Cowork material** (Claude Code issues, `code.claude.com/docs/en/skills`, Reddit and
  Facebook threads). Dropped as the wrong product. The confusion is live in search results, and at least one
  of those pages discusses bundled-script permissions, which is exactly the question under test.
- **Paraphrase blogs and social posts** (hbs.net, admindroid, innfactory, egroup, myabt, holgerimbery,
  russ.cloud; LinkedIn, YouTube, Instagram, Facebook). Dropped as restatements of the Learn pages or
  unciteable, adding restatement risk rather than evidence.

---

## 7. Sources read

### Microsoft documentation

| URL | Tier | Page date | Fetched |
|---|---|---|---|
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork | Microsoft documentation | 2026-09-08 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq | Microsoft documentation | 2026-09-14 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork | Microsoft documentation | 2026-09-14 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/whats-new | Microsoft documentation | 2026-09-14 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-customize | Microsoft documentation | 2026-09-15 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-admin-governance | Microsoft documentation | 2026-09-14 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development | Microsoft documentation | 2026-09-17 | Yes (read by two readers, re-fetched by the skeptic, re-fetched again for this report) |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugins | Microsoft documentation | 2026-08-27 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-manage-plugins | Microsoft documentation | 2026-09-01 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-local-browser | Microsoft documentation | 2026-09-16 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-network-endpoints | Microsoft documentation | 2026-09-10 | Yes (evidence dropped) |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/manage-public-web-access | Microsoft documentation | 2026-08-18 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory | Microsoft documentation | 2026-09-02 | Yes |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/code-interpreter | Microsoft documentation | 2026-06-18 | Yes (declarative agents; no Cowork mention) |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/aiinteractionhistory-getallenterpriseinteractions | Microsoft documentation | 2026-02-23 | Yes (the `getAllEnabledInteractions` URL 404s; this is the real method) |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/resources/aiinteractionhistory | Microsoft documentation | 2025-12-04 | Yes |
| https://learn.microsoft.com/en-us/purview/ai-copilot-cowork | Microsoft documentation | 2026-06-22 | Yes |
| https://learn.microsoft.com/en-us/purview/audit-copilot | Microsoft documentation | 2026-08-26 | Yes |
| https://learn.microsoft.com/en-us/agent-framework/agents/skills | Microsoft documentation | 2026-09-18 | Yes (different product; dropped) |
| https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-uses-stores | Microsoft documentation | 2026-09-15 | Yes (personal-accounts Preview) |
| https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-manage-tasks-schedule-prompts | Microsoft documentation | 2026-09-15 | Yes (personal-accounts Preview) |
| https://support.microsoft.com/en-us/microsoft-365-copilot/how-microsoft-365-copilot-chat-history-works | Microsoft documentation | 2026-08-18 | Yes |
| https://support.microsoft.com/en-us/microsoft-365-copilot/personalize-what-microsoft-365-copilot-remembers | Microsoft documentation | 2026-09-14 | Yes |
| https://support.microsoft.com/en-us/microsoft-365-copilot/get-started-with-researcher-in-microsoft-365-copilot | Microsoft documentation | 2026-09-09 | Yes |

### Machine-readable and standards

| URL | Tier | Page date | Fetched |
|---|---|---|---|
| https://developer.microsoft.com/json-schemas/teams/v1.28/MicrosoftTeams.schema.json | Machine-readable | undated | Yes (also grepped as raw JSON) |
| https://github.com/OfficeDev/microsoft-365-agents-toolkit (full tree, 13,122 files; `skillValidation.ts`; v1.30 schema) | Machine-readable | fetched 2026-09-19 | Yes (zero occurrences of "ASKILL") |
| https://agentskills.io/specification | Standard | 2026-08-04 | Yes |
| https://agentskills.io/skill-creation/using-scripts | Standard | 2026-02-27 | Yes |
| https://agentskills.io/client-implementation/adding-skills-support | Standard | 2026-03-10 | Yes |

### Microsoft announcements and samples

| URL | Tier | Page date | Fetched |
|---|---|---|---|
| https://www.microsoft.com/en-us/copilot/blog/2026/06/16/copilot-cowork-is-now-generally-available | Microsoft announcement | 2026-06-16 | Yes |
| https://microsoft.github.io/copilot-camp/pages/copilot-cowork/01-cowork-skills/ | Microsoft-authored sample | no date on page | Yes |
| https://microsoft.github.io/copilot-camp/pages/copilot-cowork/02-cowork-plugins/ | Microsoft-authored sample | no date on page | Yes |
| https://github.com/microsoft/copilot-camp (`src/cowork/`: weekly-status-mail, CopilotDevCamp-for-cowork, zava-claims-sso) | Microsoft-authored sample | fetched 2026-09-19 | Yes (the `zava-claims-export` script path returns 404) |
| https://microsoft.github.io/cat-agent-skills/ | Microsoft-hosted catalogue, community submissions | no date on page | Yes |
| https://github.com/microsoft/cat-agent-skills (`submissions/agent-harness-explorer`, `submissions/chart-builder`) | Community, hosted in a Microsoft repository | fetched 2026-09-19 | Yes |

### Practitioner and community

| URL | Tier | Page date | Fetched |
|---|---|---|---|
| https://www.promptarmor.com/resources/microsoft-copilot-cowork-sandbox-bypass | Practitioner, observed behaviour | 2026-08-25 (reported 2026-06-24, mitigated 2026-08-19) | Yes |
| https://www.promptarmor.com/resources/microsoft-copilot-cowork-exfiltrates-files | Practitioner, observed behaviour | 2026-05-07 | Yes |
| https://futurework.blog/2026/08/28/copilot-cowork-browser-use-first-look | Practitioner, observed behaviour | 2026-08-28 (from URL) | Yes |
| https://github.com/agentskills/agentskills/discussions/452 | Community | 2026-07-08, reply 2026-07-10 | Yes |
| https://learn.microsoft.com/en-us/answers/questions/5912428/memory-in-cowork | Community (AI-generated answer, disclaimed) | 2026-06-05 | Yes (dropped as evidence) |

---

## 8. Method

An opus scout ran sixteen live searches and checked reachability, selecting sixteen sources and recording
thirteen dead ends, most of them Anthropic's Claude Cowork surfacing under the same word; four sonnet readers
then read those sixteen sources and extracted quotations with their headings; an opus adjudicator weighed the
four claims, wrote the evidence bearings, the conflicts list, a proposed rewrite of each repo sentence and six
tester probes; an opus skeptic re-fetched the two decisive Microsoft pages rather than trusting the extracts,
refuted two of the four verdicts, found three passages the readers had missed, corrected one citation error
and raised twelve rewording problems; a sonnet quote checker verified all 38 quotations against their sixteen
cited URLs, finding 37 verbatim and one near-verbatim through a tag-stripping artefact, with none missing and
no page unreachable; two sonnet gap readers then closed the two open leads, one reading eleven pages on
sessions, memory and the Graph interaction-history API, the other six pages plus GitHub sources on script
execution, the Agents Toolkit and the Researcher retirement; and this edit integrated all of it, applied the
skeptic's rulings and its twelve fixes, weighed the two gap reads against the affected verdicts, re-fetched
the plugin development page once to confirm the `commands/` row, and wrote the report.
