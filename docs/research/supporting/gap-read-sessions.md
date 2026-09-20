# Gap-read: session/transcript/memory access in Microsoft 365 Copilot Cowork

Extraction only. Product under investigation is **Microsoft 365 Copilot Cowork** at
`learn.microsoft.com/en-us/microsoft-365/copilot/cowork/` — not Anthropic's Claude Cowork.
A live web search for background context returned several third-party blog/forum hits that
use "Cowork" to mean **Claude's** Cowork (e.g. thebrandusa.com, aicoworkapp.com,
emergingai.substack.com, a Facebook post). Those were **not** fetched and are **not** used
as sources anywhere below — flagging this because the confusion the task warned about is real
and shows up in the wild.

All pages fetched via `curl -sL` with a browser User-Agent, then stripped of tags with a
Python one-liner (script/style removed, tags stripped, entities unescaped, whitespace
collapsed) and grepped. No quote below was reconstructed from memory or from a search
snippet; every quote was independently re-verified against the raw downloaded HTML with a
second, targeted `grep`/`python3` pass before being copied into this file. Local files live in
`/private/tmp/claude-501/-Users-houfu-Projects-lq-lq-plugin-cowork--claude-worktrees-cowork-capabilities-docs-b30f44/46547141-e7e3-4f63-aebb-16f93275d79f/scratchpad/gap-read-sessions/`.

---

## 1. Use Copilot Cowork

- URL: https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "Use Copilot Cowork | Microsoft Learn"
- Page date: "Last updated on 2026-09-14" (footer); `ms.date` meta = 2026-09-14

Quotes:

1. **Heading "Start a session".** "The Cowork home page has a chat input where you can type or speak your request. Below it, a list of your recent tasks appears, so you can resume a previous session." — Confirms the skeptic's first quote verbatim; describes a UI list of recent tasks used to "resume a previous session," without saying what resuming supplies to the model versus the screen.

2. **Heading "Use voice input" (Tip callout).** "Check the home page for your recent tasks. Select any task to return to that session without starting over." — Confirms the skeptic's second quote verbatim; "without starting over" is the only hint at what resuming changes, and it isn't defined further here.

3. **Heading "Control the session".** "Cowork provides controls to pause, resume, or stop work at any time." — Introduces pause/resume as controls over a single currently-running task, a different mechanism from the cross-session "recent tasks" list above.

4. **Heading "Control the session" (Resume).** "After pausing, select Resume to continue from where Cowork stopped." — Same-session resume-after-pause; not about reopening a session from a previous day.

5. **Heading "Control the session" (Cancel).** "To stop Cowork's current work entirely, select Cancel . Canceling clears the current task so you can send a new message without needing to resume." — Implies an uncanceled task stays available for later resumption, but does not say what "clears" removes or what resuming keeps.

6. **Heading "Manage your tasks".** "To see all your sessions with Cowork, select the My tasks view. To display only specific tasks, select a category in the Filters dropdown menu." — Names "My tasks" as the list view for finding past sessions.

7. **Heading "Manage your tasks".** "Select a task to open its session and continue working." — States that selecting a past task opens its session to "continue working," again without detailing what is restored to the model versus only displayed.

Silent on: memory across chats (the word "memory" never appears on this page); what resumption technically restores to the model's context (no statement distinguishing UI display from model context); programmatic access to interaction records; retrieving prior chats other than the one task selected.

---

## 2. Copilot Cowork common questions (FAQ)

- URL: https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "Copilot Cowork common questions | Microsoft Learn"
- Page date: "Last updated on 2026-09-14"

Quotes:

1. **Heading "Can I pause or stop Cowork while it's working?"** "Resume : Continue from where Cowork stopped." — Same-session resume-after-pause control, mirroring page 1.

2. **Heading "What happens if I lose my connection?"** "Cowork automatically reconnects and picks up where it left off. Progress made while you were disconnected is preserved, so you don't lose any work." — Describes reconnection after a dropped connection preserving "progress"; not explicitly the multi-day "recent tasks" resumption.

3. **Heading "How do I manage my tasks?"** "To show all your sessions with Cowork, select Tasks from the main navigation. You can switch between two views: Recent : Shows your tasks in reverse chronological order. You can filter by status (In progress, Needs input, Done, Failed)." — Describes the Tasks/Recent list as a chronological, filterable view of past sessions.

4. **Heading "How do I manage my tasks?"** "Select any task to jump back into its session." — Confirms the skeptic's third quote verbatim. Identical "jump back into its session" phrasing to the other pages; again silent on what is restored to the model.

Silent on: memory (the word never appears on this page); what resumption restores to the model versus the UI only; programmatic/API access to interaction records; retrieving prior related chats outside the one selected task.

---

## 3. What's new in Copilot Cowork

- URL: https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/whats-new
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "What's new in Copilot Cowork | Microsoft Learn"
- Page date: "Last updated on 2026-09-14"

This is a dated changelog table. Every entry mentioning memory, sessions, history, models, scripts, code, execution, browser use, or connectors, verbatim, with its date:

1. **September 2026 — New features — "Claude Fable 5.1 model".** "Fable 5.1 is now available in the model selector as the most advanced model for ambitious work, replacing Fable 5." — New model, no session/memory content.

2. **September 2026 — New features — "GPT 6 Astra model".** "GPT 6 Astra is now available in the model selector as the latest model for tough problems." — New model.

3. **September 2026 — New features — "Plugins on the mobile app".** "Plugins are discoverable and configurable on the mobile app. To find them, select the attach menu ( + ) > Skills ." — Connector/plugin discoverability change on mobile.

4. **August 2026 — Enhancements — "Workspace file input for plugin tools".** "Plugin connector tools can now accept files from your session as input. Plugin authors declare a tool parameter with contentEncoding: base64 , and Cowork resolves the workspace file to content before calling the tool—so a tool can convert a document, analyze an image, or attach a file to another system." — A connector tool reading files "from your session" is a within-session capability, not cross-session memory.

5. **August 2026 — Enhancements — "Local browser use".** "This feature moved from Frontier to general availability to all Microsoft 365 Copilot tenants. Cowork can complete web tasks for you in Microsoft Edge on your device, using your existing sign-ins and your organization's policies. Requires that Edge is installed." — Browser-use reaching general availability; unrelated to transcript/memory access.

6. **June 2026 (general availability).** "Microsoft 365 Copilot Cowork is generally available to all Microsoft 365 Copilot tenants worldwide in tier-1 languages." — Marks Cowork's GA date.

7. **June 2026 — New features — "Claude Opus 4.8 model".** "Opus 4.8 is now available as a model option in the model selector." — New model.

8. **June 2026 — New features — "Claude Sonnet 5 model".** "Sonnet 5 is now available in the model selector as the efficient choice for everyday tasks, replacing Sonnet 4.6." — New model.

9. **June 2026 — New features — "Claude Fable 5 (Preview) model".** "Fable 5 is now available in preview in the model selector for your toughest challenges. Fable 5 is off by default; an admin turns it on in the Microsoft 365 admin center under Copilot settings. Fable 5 requires data retention, so your prompts and responses for that model are retained by the model provider, and Cowork shows a banner while it's selected." — The clearest changelog link between a Cowork model choice and conversation data being retained (by the model provider, not necessarily replayed into context).

10. **June 2026 — New features — "Local browser use (Frontier)".** "Cowork can complete web tasks for you in Microsoft Edge on your device, using your existing sign-ins and your organization's policies. In Frontier and requires that Edge is installed." — Earlier Frontier-only release of browser use.

11. **June 2026 — New features — "Upload a plugin package".** "Upload your own plugin package from the Customize > Plugins tab. Cowork converts a Claude or other compatible package into a publishable package, including bundled skills and connectors." — Connectors entry.

12. **June 2026 — Enhancements — "Expanded plugin catalog".** "The Microsoft 365 App Store now lists Microsoft and partner plugins for Cowork at launch, including Microsoft plugins (Dynamics 365 Customer Service, Dynamics 365 Sales, Dynamics 365 ERP, Fabric IQ) and partner connectors (Jira, Salesforce, ServiceNow, SAP ERP, Workday HCM, Zendesk, and more)." — Connector catalog at GA.

13. **June 2026 — Enhancements — "Refreshed admin governance".** "The admin guidance now covers model toggles, browser-use controls, consumption visibility, and Purview integration in one place." — Names admin controls covering model and browser-use, not a memory/history control.

14. **May 2026 — New features — "Claude Opus 4.7 model".** "Opus 4.7 is now available as a model option in the model selector." — New model.

15. **April 2026 — New features — "Search task history".** "Home page task list is scrollable with search and status filters, replacing the static five-item view." — The only entry on this page using the word "history"; it describes a UI search/filter change to the task list, not memory or model context.

16. **April 2026 — New features — "Plugins".** "Browse, install, and manage plugins from the Microsoft 365 App Store to add new skills and connectors." — Connectors entry.

Silent on: the word "memory" never appears anywhere on this page (verified by full-page grep); no entry describes what session resumption restores to the model; no entry describes programmatic/API access to interaction records; "transcript" never appears.

---

## 4a. Manage Copilot personalization and memory

- URL: https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-personalization-memory
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "Manage Copilot personalization and memory | Microsoft Learn"
- Page date: "Last updated on 2026-09-02"

Quotes:

1. **Heading (intro, Important callout).** "Copilot personalization and memory are in preview and subject to change." — Frames the whole memory feature as preview/subject to change as of this page's date.

2. **Heading (intro).** "Copilot memory is available to Copilot Chat users with and without a Microsoft Copilot license." — Explicitly scopes memory to "Copilot Chat" users; Cowork is not named here or anywhere else on this page.

3. **Heading (intro).** "Memories, which include saved memories, details inferred from chat history and custom instructions, are stored in the user's Exchange mailbox in a hidden folder." — States storage location/composition of "memories": a mailbox folder, distinct from any session-log store.

4. **Heading "Manage Enhanced personalization control".** "To configure the control programmatically via Microsoft Graph, a tenant administrator can write a script using Microsoft Graph." — The only "programmatic" access this page describes is an admin script that toggles the personalization control itself, not one that reads chat or session content.

5. **Heading "Retention policies for memories".** "Retention policies and retention labels configured in Purview by organization admins don't apply to Copilot memory. There are no admin controls to enforce retention rules specifically for Copilot memory." — Org-wide Purview retention rules do not govern Copilot memory.

6. **Heading "Chat history".** "Details from the chat history are dynamic. Copilot might update or discard older details as it learns what's most helpful to retain." — Chat-history-derived memory is dynamically pruned by Copilot, not a fixed transcript log.

7. **Heading "How can tenant admins respond to Data Subject Requests related to Copilot memory?"** "Admins can use eDiscovery and Microsoft Graph Explorer to search, export, and delete users' memory data." — The one place this page describes exporting memory data; it is an admin/compliance action via eDiscovery and Graph Explorer, not a stated in-session skill capability.

8. **Heading "Is there audit logging for Copilot memory?"** "Memory and personalization actions don't generate audit log entries in Purview." — States memory/personalization actions are not captured in Purview audit logs.

Silent on: Cowork by name (zero occurrences anywhere on the page, confirmed by grep); whether the memory system described here applies to, or is used within, Cowork sessions specifically; what session resumption restores; whether a skill/agent running inside a session can call an API to read this memory or chat-history data mid-session (only admin/eDiscovery access is described).

---

## 4b. How Microsoft Copilot Chat history works

- Requested URL: https://support.microsoft.com/en-us/topic/revisit-your-microsoft-365-copilot-chat-history-6ea899e3-3bb1-450a-a2ae-220341ac193a
- Canonical URL after redirect: https://support.microsoft.com/en-us/microsoft-365-copilot/how-microsoft-365-copilot-chat-history-works
- Fetched: yes, via `curl` (HTTP 200, redirected)
- Page title: "How Microsoft Copilot Chat history works | Microsoft Support"
- Page date: `updated_at` meta = 2026-08-18

Quotes:

1. **Heading "How do I find my chat history?"** "You'll find your chat history in the Microsoft Copilot app." — The "chat history" this article documents lives in the Microsoft Copilot app's own "Chats" list (left-side navigation), reached by going to "Copilot Chat."

2. **Heading "How do I turn off Copilot personalization based on chat history?"** "Copilot Memory automatically collects key details from your previous chat conversations and remembers it for future conversations." — Restates the memory mechanism; scoped to "chat conversations," not named as covering Cowork tasks.

3. **Heading "How does Copilot use my chat history?"** "Copilot may use context from previous chat conversations to improve future responses by making inferences about what is important to remember." — Memory feeds "context" into future responses as inferences, not stated as a full restored transcript.

4. **Heading "How does Copilot use my chat history?"** "Copilot doesn't remember every detail from your previous chats, only what's useful for personalizing its responses to your questions and tasks." — Explicitly denies full-transcript recall; memory is selective inference, not verbatim replay.

Silent on: Cowork — the string "Cowork" appears only in this page's left-navigation table of contents (as link labels: "Cowork," "Get started with Cowork," "What Cowork uses and stores"), never once in the article body itself; whether this "chat history" mechanism has any relationship to Cowork's own task/session list; programmatic access to interaction records.

---

## 4c. Personalize what Microsoft Copilot remembers

- Requested URL: https://support.microsoft.com/en-us/topic/personalize-what-microsoft-365-copilot-remembers-cba7b79a-c46f-4ca7-b46e-2fa22c563f90
- Canonical URL after redirect: https://support.microsoft.com/en-us/microsoft-365-copilot/personalize-what-microsoft-365-copilot-remembers
- Fetched: yes, via `curl` (HTTP 200, redirected)
- Page title: "Personalize what Microsoft Copilot remembers | Microsoft Support"
- Page date: `updated_at` meta = 2026-09-14

Quotes:

1. **Heading (intro).** "Microsoft Copilot offers you tailored experiences by remembering key details and preferences from your conversations with Microsoft Copilot Chat using Copilot Memory." — Again scopes the remembering mechanism to "conversations with Microsoft Copilot Chat."

2. **Heading "Revisit your chat history".** "Copilot keeps a history of your previous conversations with Copilot Chat. Copilot can make inferences about what matters to you using previous conversations to respond to subsequent conversations." — States Copilot Chat keeps a conversation history used for inference in later conversations.

3. **Heading "Use temporary chat to limit what Copilot Chat remembers".** "These conversations won't access or store any personalized information. Also, the conversation won't appear in your chat history and can't be referenced or accessed later by you or Copilot." — An explicit opt-out mode where the conversation is neither stored nor later accessible "by you or Copilot" — implying non-temporary chats are, in some form, referenceable/accessible later by Copilot.

4. **Heading "Use temporary chat to limit what Copilot Chat remembers".** "However, your organization's data retention policy might require retaining temporary chat data. Your IT administrator might be able to access this data during the retention period." — Org retention policy can override even temporary-chat non-storage; the stated accessor is an IT administrator, not the agent itself.

Silent on: Cowork — again present only in the page's left-navigation menu, never in the article body; Cowork's own task/session resumption; whether "referenced or accessed later... by Copilot" means the model can pull prior-chat content back into a live context window, or only that saved-memory inferences surface as personalization signals.

---

## 4d. Microsoft Q&A: "Memory in Cowork"

- URL: https://learn.microsoft.com/en-us/answers/questions/5912428/memory-in-cowork
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "Memory in Cowork - Microsoft Q&A"
- Page date: question posted 2026-06-05T14:35:55.5+00:00; the one answer posted 2026-06-05T14:36:17+00:00 (one minute later)

**Caveat, stated plainly because it matters for a fact-check:** this thread's only answer is labeled **"AI answer"**, and the page itself carries the disclaimer "AI-generated content may be incorrect. Read our transparency notes for more information." It has 0 comments and shows no "Accepted" or "Recommended" marking. It is community/AI-generated content, not verified Microsoft documentation, and its own "References" list points back to the same Learn/Support memory pages already quoted above (plus unrelated Azure AI Foundry Agent Service memory docs) — it cites no Cowork-specific source for its claims.

Quotes:

1. **The question, by Matthew Phang.** "Has anyone been able to successfully customize memory? Even a simple prompt saying "refer to me as x in future chats" will not work." — Establishes a user report that custom-instruction-style memory prompts did not persist in Cowork.

2. **The AI answer.** "Copilot Cowork memory is currently limited and may not support arbitrary custom instructions such as "refer to me as X in future chats."" — An unverified, AI-generated answer asserting a "Copilot Cowork memory" feature exists but is limited; this is the only fetched source that names a "Cowork memory" feature directly.

3. **The AI answer.** "Saved memories and custom instructions are managed through Settings > Personalization . Copilot can use these saved memories (for example, preferences) in future chats, including voice chats, but users manage them from the Personalization UI, not directly or reliably via ad‑hoc prompts." — Same AI answer, describing saved memories as UI-managed rather than prompt-managed.

4. **The AI answer.** "Retention and application of memories are controlled by the product's memory system, not by simple one‑off prompts." — Same AI answer, restating that memory persistence is system-controlled, not conversational.

Silent on: whether a skill running inside a Cowork session can programmatically read past session transcripts; cross-session JSONL-style logs; any Cowork-specific transcript API (the cited references are the general Copilot memory/history docs already covered, not anything Cowork-specific).

---

## 5a. aiInteractionHistory: getAllEnterpriseInteractions (Graph API)

- **As specified in the task**, `https://learn.microsoft.com/en-us/graph/api/aiinteractionhistory-getallenabledinteractions`, was fetched and returned **HTTP 404** ("404 - Page not found... We couldn't find this page."). That method name does not exist.
- A web search found the real method is named `getAllEnterpriseInteractions`, not "getAllEnabledInteractions." Substituted URL: https://learn.microsoft.com/en-us/graph/api/aiinteractionhistory-getallenterpriseinteractions
- Canonical URL after redirect: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/aiinteractionhistory-getallenterpriseinteractions
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "aiInteractionHistory: getAllEnterpriseInteractions | Microsoft Learn"
- Page date: `ms.date` meta = 2026-02-23

Quotes:

1. **Heading (intro).** "Get all Microsoft 365 Copilot interaction data, including user prompts to Copilot and Copilot responses. This API captures the user intent, the resources accessed by Copilot, and the response to the user for Microsoft 365 apps such as Teams, Word, and Outlook." — Names the specific apps in scope (Teams, Word, Outlook) via "such as," which is not stated to be an exhaustive list; Cowork is not among the named examples.

2. **Heading (Note callout).** "This API requires a valid Microsoft 365 Copilot license with the Microsoft Copilot with Graph‑grounded chat service plan." — States the licensing precondition.

3. **Heading "Permissions" (table row).** "Application: AiEnterpriseInteraction.Read.All" with the Delegated (work or school account) row reading "Not supported." — Only an application permission (admin-consented app identity) can call this API; there is no delegated/user-signed-in permission, and by extension no stated path for an in-session skill acting as the user to call it directly.

4. **Heading (Note callout, under HTTP request).** "This API doesn't retrieve interactions in agents created by Copilot Studio." — The page's one explicit scope exclusion; it names Copilot Studio agents as out of scope but says nothing about Cowork either way.

5. **Heading (Important callout).** "The set of interactions returned varies based on Copilot licensing and the AI experiences in your tenant that write to the interaction history service." — Makes coverage conditional on which "AI experiences... write to the interaction history service," without listing which experiences those are.

Silent on: Cowork is never named anywhere on this page (zero grep matches); whether Cowork sessions write to the "interaction history service" this API reads from; any statement that a skill or agent (as opposed to a separately consented application using `AiEnterpriseInteraction.Read.All`) could call this API from inside a running session.

---

## 5b. aiInteractionHistory resource type

- URL requested: https://learn.microsoft.com/en-us/graph/api/resources/aiinteractionhistory
- Canonical URL after redirect: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/ai-services/interaction-export/resources/aiinteractionhistory
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "aiInteractionHistory resource type | Microsoft Learn"
- Page date: "Last updated on 2025-12-04"

Quotes:

1. **Heading "AI interactions returned".** "The AI interaction history API returns interactions recorded by Microsoft 365 AI experiences that write to the interaction history service." — Defines scope by which experiences "write to" a shared service, without listing Cowork among them.

2. **Heading "AI interactions returned".** "Microsoft 365 Copilot experiences that save interaction data to the interaction history service, such as Copilot in Microsoft 365 apps and the Microsoft 365 Copilot app, when enabled for the user and tenant." — The closest this page comes to naming Cowork's host app is "the Microsoft 365 Copilot app" (the app Cowork ships inside, per the "Applies to: Microsoft Copilot" line on pages 1–3) — but "Cowork" itself is not named.

3. **Heading "AI interactions returned".** "The following interactions are never returned by the API: Interactions from AI experiences that don't save data to the interaction history service. Interactions from consumer or personal Microsoft accounts." — A hard exclusion for consumer/personal accounts, notable given Cowork also ships a personal-accounts Preview edition (see pages 6–7 below).

4. **Heading "Licensing and prerequisites".** "Access to AI interaction export data might require a Microsoft 365 Copilot add-on license, depending on your tenant configuration and the interaction sources you want to export." — Licensing is conditional and tenant-dependent.

Silent on: Cowork by name (zero matches); whether Cowork task/session data is among the "Microsoft 365 AI experiences that write to the interaction history service"; any mechanism for a skill or in-session agent, versus an external admin-consented application, to call this API.

---

## 6. [Extra] What Microsoft Copilot Cowork uses and stores (Preview)

- URL: https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-uses-stores
- Found via: the left-navigation table of contents embedded in pages 4b/4c (link label "What Cowork uses and stores"), located precisely via web search since it wasn't directly linked from pages 1–3.
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "What Microsoft Copilot Cowork uses and stores (Preview) | Microsoft Support"
- Page date: `updated_at` meta = 2026-09-15

**Scope caveat, stated plainly:** this article's own "Important" callout says it is about **"Microsoft Copilot Cowork for personal accounts,"** explicitly labeled "currently in Preview," covering "a prerelease product that may be substantially modified before it's released." This is a different edition/audience than the enterprise-tenant Cowork that pages 1–3 describe as generally available tenant-wide since June 2026. The two are not stated to share a data model; treat this page's specifics as about the personal-accounts Preview edition, not confirmed for the enterprise GA edition.

Quotes:

1. **Heading (Important callout).** "Microsoft Copilot Cowork for personal accounts is currently in Preview." — Scopes the whole article to the personal-accounts preview edition.

2. **Heading (intro bulleted list — "Conversation and task history").** "Conversation and task history : Your prompts and Copilot's responses are saved so you can review past tasks." — The clearest statement among all fetched pages that Cowork (this edition) itself saves prompts and responses as history, for the stated purpose of letting the user "review past tasks."

3. **Heading (intro list — "Screenshots").** "Screenshots are retained for a limited time and are not used for training." — Describes a second, separate stored artifact type (browser screenshots) with limited retention, distinct from conversation/task history.

4. **Heading (intro list — "Connectors").** "Copilot does not independently store your information from these services." — For connector-sourced data specifically (not conversation history), the article says Copilot does not independently store it.

5. **Heading "Use of Cowork interactions".** "Microsoft will only use your Cowork interaction data for the limited purposes explained in the Microsoft Privacy Statement to troubleshoot problems, diagnose bugs, prevent abuse, and to monitor, analyze, and improve performance, and so we can provide Copilot to you." — States Microsoft's own declared purposes for using "Cowork interaction data."

6. **Heading "Use of Cowork interactions".** "In addition, some Cowork interactions are subject to both automated and human review for product improvement and digital safety purposes. Task logs, screenshots, and outputs are retained for limited periods to support functionality, safety, and troubleshooting." — Confirms "task logs" specifically are retained, for Microsoft's own review purposes, "for limited periods" — described as Microsoft-side retention infrastructure, not stated as an in-session skill/agent read capability.

7. **Heading "Limitations".** "Cowork can only access the data and services that your account is authorized to use." — A general access-scoping statement; does not specifically address session-log access.

Silent on: whether the saved "conversation and task history" is exposed to a skill or to the agent itself via any API or tool call — the article addresses what Microsoft stores/uses, not what an in-session skill can query; any stated connection between this "conversation and task history" and the aiInteractionHistory Graph API (pages 5a/5b); whether this personal-accounts data model is the same one used by the enterprise-tenant GA Cowork of pages 1–3.

---

## 7. [Extra] Manage tasks and schedule prompts in Microsoft Copilot Cowork (Preview)

- URL: https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-manage-tasks-schedule-prompts
- Found via: same left-navigation table of contents as page 6, located via web search.
- Fetched: yes, via `curl` (HTTP 200)
- Page title: "Manage tasks and schedule prompts in Microsoft Copilot Cowork (Preview) | Microsoft Support"
- Page date: `updated_at` meta = 2026-09-15

Same personal-accounts-Preview scope caveat as page 6 applies (identical "Important" callout appears on this page too).

Quotes:

1. **Heading (Important callout).** "Microsoft Copilot Cowork for personal accounts is currently in Preview." — Same scope caveat as page 6.

2. **Heading "Manage your tasks".** "To see all your conversations with Cowork, select the My tasks view. Use the Filters dropdown to show only specific tasks, such as those that need your input, are in progress, are complete, or are scheduled." — A personal-accounts-edition description of the same "My tasks" list found in the enterprise Learn docs, here calling past tasks "conversations" rather than "sessions."

3. **Heading "Manage your tasks".** "Select a task to open its conversation and continue working." — Parallels the Learn FAQ's "Select any task to jump back into its session," substituting "conversation" for "session," again without stating what is restored to the model.

Silent on: memory (the word does not appear anywhere on this page); what "continue working" technically restores to the model; programmatic access to interaction records; any statement of whether this matches or differs from the enterprise-tenant Cowork's identical-sounding feature.

---

## Overall summary

Across all 11 fetched pages (one requested URL 404'd and was replaced with the correct one),
Microsoft's own docs describe **only a UI-level "recent tasks" / "My tasks" list** that lets a
user reopen a past Cowork task ("resume a previous session," "jump back into its session,"
"return to that session without starting over," "open its conversation and continue
working"). None of the three core Cowork pages (Use Cowork, FAQ, What's New) use the word
"memory" at all. The separate Copilot **memory/personalization** docs and the two
support.microsoft.com "chat history" articles are written entirely in terms of **"Copilot
Chat"** conversations and never name Cowork in their body text (only in shared left-nav
menus) — so it is undocumented whether that memory system reaches into Cowork sessions.
One newly-found support.microsoft.com page, "What Microsoft Copilot Cowork uses and
stores," does say Cowork itself saves "conversation and task history" (prompts and
responses) and separately retains "task logs" for Microsoft's own review — but that page is
explicitly scoped to the **personal-accounts Preview** edition of Cowork, not the
enterprise GA edition the other pages describe, and it never says whether a skill or the
agent itself can pull that saved history back into a live context window versus a human
just scrolling it in the UI. The Graph `aiInteractionHistory` / `getAllEnterpriseInteractions`
API never mentions Cowork, names Teams/Word/Outlook as its example apps, is
application-permission-only (no delegated/in-session path), and explicitly excludes Copilot
Studio agents and personal accounts. A Microsoft Q&A thread titled "Memory in Cowork" does
use the phrase "Copilot Cowork memory," but its only content is an unverified, disclaimed
"AI answer," not Microsoft documentation. **Undocumented across every page fetched:**
whether resuming a task/session re-injects prior messages into the model's context (as
opposed to only rendering them in the UI), and whether any skill or agent running inside
Cowork has a callable API or tool to read its own or another session's past transcript.

Output path: `/private/tmp/claude-501/-Users-houfu-Projects-lq-lq-plugin-cowork--claude-worktrees-cowork-capabilities-docs-b30f44/46547141-e7e3-4f63-aebb-16f93275d79f/scratchpad/gap-read-sessions.md`
