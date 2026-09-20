# Cowork capability fact-check: scheduling, file formats, outputs, skills, browser, folders (A-F)

Extraction only, no judgment. All quotes below are copied verbatim (exact words, no ellipsis inside a quote) from stripped page text, character-for-character, cross-checked against each page's `rel="canonical"` tag and `ms.date`/"Last updated on" metadata. Every page fetched is Microsoft's own documentation (learn.microsoft.com or support.microsoft.com) for **Microsoft 365 Copilot Cowork**, not Anthropic's Claude Cowork.

Letters: **A** = scheduled/event-driven tasks, **B** = input file types/reading, **C** = outputs/writing back, **D** = built-in skills, **E** = browser use, **F** = working with folders.

---

## 1. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `gap-read-sessions/use-cowork.html`; verified by exact canonical-URL match and re-checked `ms.date` before reuse — no content taken from memory or a snippet).
Page title: "Use Copilot Cowork | Microsoft Learn"
Page date: "Last updated on 2026-09-14"

1. [B] "Cowork can work with a wide variety of files. You can upload files to provide context, and download files that Cowork creates for you." — heading "Work with files". Shows both directions: upload for context, download of created files.
2. [C] "When Cowork creates or updates files during a session, you can grab them from the side panel." — heading "Download output files". "Updates" implies editing an existing file, not only creating new ones.
3. [C] "When Cowork produces multiple output files, select Download All at the top of the output file list to download every file as a single zip archive. The archive can include up to 50 files and 500 MB total." — heading "Download output files" (Tip). States an output-bundle limit: 50 files / 500 MB.
4. [F] "You can also access files that Cowork creates directly in your OneDrive Cowork folder at any time." — heading "Download output files". Names a fixed default output location (a "Cowork" folder in OneDrive).
5. [B] "Cowork supports the following file types: Word doc, docx, docm, dot, dotx, odt, rtf Excel csv, xls, xlsm, xlsx, ods PowerPoint odp, ppt, pptm, pptx PDF pdf Markdown md, markdown, mdx Image png, jpg, jpeg, gif, webp, bmp, svg, ico Text txt, log Code js, ts, py, java, c, cpp, go, rb, rs, and others Config json, yaml, yml, toml, ini, xml, env Notebook ipynb Audio mp3, wav, m4a, ogg, aac, flac Video mp4, mov, avi, mkv, webm, wmv Archive zip, rar, 7z, tar, gz, bz2" — heading "Supported file types". The full extension table; no email format (.eml/.msg) or OCR/scanned-image note appears in this table.
6. [B] "You can preview many file types directly inside Cowork. You don't need to download them first. The preview opens alongside your session in a split view." — heading "Preview documents".
7. [B] "PDF : Renders inline with page navigation. Use Ctrl+F to search within the document." — heading "Supported preview formats". Describes on-screen rendering of a PDF's existing text, not OCR of a scanned/image-only PDF.
8. [B] "Email : Opens email references in a side-by-side preview panel." — heading "Supported preview formats". Confirms email as a referenceable/previewable item.
9. [A/C/F] "Input folder Files you provided as context for the session. Output folder Files Cowork created. Each file has Download and Preview buttons." — heading "What's in the side panel". Confirms a session has a distinct Input folder (files the user placed) and Output folder.
10. [A] "Schedule Scheduled prompts you created, with options to edit, pause, resume, or delete them." — heading "What's in the side panel".
11. [A] "Automations : Automated tasks, including scheduled prompts that run at a set time and event-driven tasks that run when something happens." — heading "Manage your tasks". Names the two automation kinds side by side.
12. [F] "Browse OneDrive files To pull in the files you need, you can browse your OneDrive files and folders directly from Cowork. From the file selection interface, open the OneDrive file browser. Browse your files and folders in the tree view. Use the breadcrumb trail at the top to navigate, or select a folder to open it. To include a file in your session, select it." — heading "Browse OneDrive files". Selection is per-file via a tree view; the sentence does not say a whole folder can be attached as a unit.
13. [D] "Cowork uses specialized skills as it works. When Cowork loads a new skill during your session, a message such as "Preparing to compose emails" appears, and the skill shows up in the side panel. The following out-of-the-box skills are available:" — heading "Cowork skills".
14. [D] "Word Create and edit Word documents. Excel Create and edit Excel spreadsheets. PowerPoint Create and edit PowerPoint presentations. PDF Work with PDF documents. Email Compose, reply, forward, and send emails. Save drafts and manage attachments. Scheduling Schedule meetings. Calendar Management Create events using natural language, add Teams meeting links, and manage your calendar." — heading "Cowork skills" (table, part 1 of 2). The PDF skill's one-line description is only "Work with PDF documents" — no detail on merge/split/annotate.
15. [D] "Meetings Prepare meeting intelligence. Daily Briefing Prepare your daily briefing. Enterprise Search Search across your organization. Deep Research Conducts in-depth research across multiple sources to compile comprehensive answers and analysis on complex topics. Communications Draft stakeholder communications. Adaptive Cards Generates interactive card-based responses with structured layouts, buttons, and data displays in the conversation. App (Frontier) Build lightweight, interactive apps from a description, then refine, open, publish, and share them. No coding required." — heading "Cowork skills" (table, part 2 of 2). The skill is named "Deep Research", not "Researcher".
16. [D/F] "When you're happy with the draft, confirm in chat. Cowork saves the skill to your OneDrive /Documents/Cowork/skills/ folder, where it becomes available in your next session." — heading "Build a skill from the Customize page".
17. [D] "You can create up to 50 custom skills. Each SKILL.md file can be up to 1 MB. Skills can also include up to 20 companion files (such as reference documents and scripts), with a total of 10 MB per skill." — heading "Build a skill manually in OneDrive" (Note).
18. [D] "Cowork also supports plugin skills from the Microsoft 365 App Store. When you acquire a plugin, its skills appear alongside the built-in skills and are available in your sessions. Plugin skills work the same way as built-in skills—Cowork activates them automatically based on your session context, and active skills appear in the side panel." — heading "Use plugin skills". Distinguishes plugin skills from built-in skills while noting they behave the same way.
19. [A] "You can schedule a prompt to run automatically on a recurring basis. To create a scheduled prompt, describe what you want and when in your message. For example, "Send me a daily briefing every morning at 9 AM" or "Create a weekly status report every Friday."" — heading "Schedule prompts".
20. [A] "Cowork sets up the schedule based on your request. You can manage your scheduled prompts from the Automations page in the left navigation, or from the Schedule section of the side panel during a session." — heading "Schedule prompts".
21. [A] "The Automations page has two tabs: Runs (each past or upcoming run of a schedule) and Manage schedules (the schedule definitions themselves, where you can edit, pause, resume, or delete)." — heading "Schedule prompts". Directly names the "Runs" tab as the run-history view, separate from the schedule definition itself.
22. [A] "When you activate a draft scheduled prompt, Cowork asks whether to Activate and run now (starts immediately so you can watch and approve actions) or Activate (the first run happens at the next scheduled time). You can create up to 25 scheduled prompts." — heading "Schedule prompts". States a hard cap: 25 scheduled prompts.
23. [A] "Scheduled prompts run on a recurring schedule. Event-driven tasks run when something happens — when you receive a matching email, or when a Teams message arrives (including when you're @mentioned) . Instead of watching your inbox or a channel yourself, you describe what to watch for, and Cowork notices the event and prepares a response." — heading "Set up event-driven tasks".
24. [A] "Cowork proposes the automation in a Set up trigger? card that shows: When : The event that starts the task, such as When you receive an email , When a Teams channel message arrives , or When a Teams chat message arrives . For Teams triggers, you can limit it to messages that mention you." — heading "Set up event-driven tasks". Names the trigger types explicitly.
25. [A] "Run in : Whether each run starts a new conversation or continues the current one. What it does : The instructions Cowork follows when the event fires." — heading "Set up event-driven tasks". Bears on whether a run can be chained/continued rather than always starting fresh.
26. [A] "Event-driven tasks appear alongside your scheduled prompts on the Automations page. Each one shows its state— Active , Draft , or Paused —and when it last fired. Select a task to open its details, review its run history, and edit, pause, resume, or delete it." — heading "Set up event-driven tasks". Uses the literal phrase "review its run history".
27. [A] "Event-driven tasks default to draft-and-approve. When a task would send an email, post a message, or change a shared system, Cowork prepares the action and asks for your approval before it happens. Every task runs with your permissions and sees only what you can see. Cowork applies rate limits so a task can't fire too often, and it delivers results only to you unless you approve otherwise." — heading "Set up event-driven tasks" (Note).
28. [C] "Generate images Cowork can create images for you by using the built-in image-generation skill. Ask Cowork to make an image—for example, "Create a landscape image of a mountain lake at sunset," "Draw a square icon of a coffee cup for my slide deck," or "Generate three concept images for a campaign poster."" — heading "Generate images".
29. [C] "Automatically uses the ChatGPT Images 2.0 model for image generation. Asks clarifying questions if your prompt is missing detail, like the orientation, style, or where you want to use the image. Saves the finished image to your session and to your OneDrive output folder." — heading "Generate images".

Silent on: E (only a "Related content" link to "Use the local browser with Cowork"; the page itself gives no browser detail).

---

## 2. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-faq

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `gap-read-sessions/cowork-faq.html`; verified by canonical-URL match and `ms.date`).
Page title: "Copilot Cowork common questions | Microsoft Learn"
Page date: "Last updated on 2026-09-14"

1. [D] "Cowork has built-in skills: Word, Excel, PowerPoint, PDF, Email, Scheduling, Calendar Management, Meetings, Daily Briefing, Enterprise Search, Communications, Deep Research, Adaptive Cards, and App (Frontier). The App skill lets you build lightweight, interactive apps in Cowork without writing code. You can also create your own custom skills by placing a SKILL.md file in a subfolder of your OneDrive /Documents/Cowork/skills/ folder (for example, /Documents/Cowork/skills/weekly-report/SKILL.md )." — heading "What skills does Cowork have?". Matches the use-cowork skills list exactly.
2. [F] "Cowork inherits your permissions, so it can access only the files and emails you can already access. If you don't have access to a file or email, Cowork can't access it either. When a referenced file or email has a sensitivity label, Cowork shows that label and displays the highest sensitivity label for the session." — heading "What can Cowork access?". Says a sensitivity label is shown, not that a labelled file is blocked.
3. [B] "Some plugin tools can act on files from your session—for example, to convert a document, analyze an image, or attach a receipt to a record in another system. When a tool needs a file, Cowork sends the file you point to, and the plugin acts on it." — heading "Can a plugin work with my files?".
4. [B] "Word : .doc , .docx , .docm , .dot , .dotx , .odt , .rtf Excel : .csv , .xls , .xlsm , .xlsx , .ods PowerPoint : .odp , .ppt , .pptm , .pptx PDF : .pdf Image : .png , .jpg , .jpeg , .gif , .webp , .bmp , .svg , .ico Archive : .zip , .rar , .7z , .tar , .gz , .bz2" — heading "What file types does Cowork support?". Same extension categories as use-cowork's table (excerpted here).
5. [B] "Can I preview files without downloading them? Yes. You can preview the following file types directly in the session:" — same heading. The list that follows (not reproduced again here) matches use-cowork's preview-formats list.
6. [A] "Recent : Shows your tasks in reverse chronological order. You can filter by status (In progress, Needs input, Done, Failed)." — heading "How do I manage my tasks?".
7. [A] "Automations : Shows your scheduled prompts with options to edit, pause, resume, or delete them. This view only appears when you have at least one scheduled prompt." — heading "How do I manage my tasks?".
8. [A] "Can I schedule recurring prompts? Yes. Describe what you want and when in your message—for example, "Send me a daily briefing every morning at 9 AM." Cowork sets up the schedule based on your request. You can manage your scheduled prompts from the Automations tab in the Tasks view, or from the Schedule section of the side panel." — same heading.
9. [A] "Can Cowork act automatically when something happens? Yes. In addition to scheduled prompts, you can set up event-driven tasks that run when a matching email arrives or when a Teams message is posted, including when you're @mentioned . Describe what to watch for in your message, and Cowork proposes the automation for you to review and confirm. By default, event-driven tasks prepare actions for your approval rather than acting on their own, and each task runs with your permissions." — same heading.
10. [E] "Can Cowork use my local browser? Yes. Cowork can complete web tasks for you in Microsoft Edge on your device, using the sites you're already signed in to. The browser tab runs on your machine, your credentials and cookies stay on your device, and Cowork uses only the access you already have. If Cowork hits a sign-in step it can't complete on its own, it hands the browser back to you to finish." — same heading.
11. [C/F] "Where are my files saved? Files that Cowork creates are saved to your OneDrive and SharePoint workspace. You can browse them in the side panel during a session or access them directly in OneDrive at any time." — same heading. Says the workspace, not a user-named folder.
12. [C] "Can I download all output files at once? Yes. When Cowork produces multiple files, select Download All at the top of the output file list to download everything as a single zip archive." — same heading.
13. [B/F/C] "Are there known limitations? Yes. The following limitations are by design: Cowork can't access or edit files stored locally on your device. It works with files in OneDrive and SharePoint. Cowork can't delete files or folders in OneDrive or SharePoint. Microsoft doesn't validate custom skills created by users. Review custom skill outputs carefully. Attached files must be less than 200 MB. Cowork can't read encrypted files, even if the user has access." — heading "Are there known limitations?". The single most load-bearing quote for B: confirms the 200 MB per-file limit and states encrypted files cannot be read (the word used is "encrypted", not "password-protected").

Silent on: nothing entirely — every letter A-F gets at least one direct answer on this page, though none of it addresses OCR/scanned PDFs, Word tracked changes/comments, PDF merge/split, or pointing a task at a whole folder.

---

## 3. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/ (overview)

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `reader-2/page3_overview.html`; canonical tag is exactly `https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/`).
Page title: "Copilot Cowork overview | Microsoft Learn"
Page date: "Last updated on 2026-09-08"

1. [C] "Creates documents : Builds Word documents, Excel spreadsheets, PowerPoint presentations, and PDFs. Manages files : Browses and manages files in OneDrive and SharePoint." — heading "What is Cowork?".
2. [A] "Schedules prompts : Runs prompts on a schedule so recurring tasks happen automatically." — heading "What is Cowork?".
3. [D] "Create apps (Frontier) : Use the App skill to build lightweight, interactive apps from a description. There's no coding required. You can refine the app in chat, open, publish, and share it with your stakeholders." — heading "What is Cowork?".
4. [C] "Create Word documents, Excel spreadsheets, PowerPoint presentations, and PDFs from scratch. Edit and refine existing documents you share in the session. Browse your entire Work IQ to pull in the content you need. Create SharePoint and OneDrive folders. Reorganize your existing files into new or existing folders." — heading "Documents and files". Explicitly separates "from scratch" creation from editing a document the user shared, and confirms Cowork can create SharePoint/OneDrive folders.
5. [F] "Browse your SharePoint and OneDrive folders and select files to work with." — heading "Research and search".
6. [A] "Run prompts on a schedule, so recurring tasks happen automatically. Set up event-driven tasks that run when something happens, such as when you receive an email or a Teams message." — heading "Automation".
7. [D] "Cowork uses specialized skills as it works. When Cowork loads a new skill during your session, the skill shows up in the side panel. Each skill corresponds to a specific type of task. Cowork has built-in skills, including Word, Excel, PowerPoint, PDF, Email, Scheduling, Calendar Management, Meetings, Daily Briefing, Enterprise Search, Communications, Deep Research, Adaptive Cards, and App (Frontier). You can also create your own custom skills." — heading "Skills". A third independent copy of the same 14-skill list.
8. [D] "You can extend Cowork with custom skills . Cowork discovers your custom skills automatically at the start of each session. You can create up to 50 custom skills." — heading "Skills".
9. [D] "Cowork supports plugins from the Microsoft 365 App Store that add new skills and connectors. Plugins can give Cowork specialized expertise-such as financial analysis or legal research-or connect it to external data sources and services." — heading "Extend with plugins". Legal research is named as an example plugin specialty — i.e., Microsoft frames "legal research" as plugin territory, not a built-in skill.
10. [B] "Tell Cowork what you need. For example, "Send a meeting recap to my team" or "Create a slide deck summarizing Q3 results." You can also attach files by dragging them into the chat." — heading "How you work with Cowork".
11. [A] "Cowork helps you stay organized with built-in project and task management. Task views : Display all of your tasks or filtered views based on task status or use the Automations tab to manage your scheduled prompts." — heading "Manage your work".

Silent on: E (the only browser-word hit is "You can use Cowork in your browser at m365.cloud.microsoft", i.e. accessing Cowork itself, not Cowork driving a browser).

---

## 4. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/whats-new

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `gap-read-sessions/whats-new.html`; verified by canonical-URL match and `ms.date`).
Page title: "What's new in Copilot Cowork | Microsoft Learn"
Page date: "Last updated on 2026-09-14"

1. [A] "Event-driven tasks Set up tasks that run when something happens, such as when you receive a matching email or a Teams message (including when you're @mentioned) . Describe what to watch for in your message, and Cowork proposes the automation for you to review and confirm. Event-driven tasks appear alongside scheduled prompts on the Automations page." — heading "August 2026" / "New features". Dates the feature's introduction to August 2026.
2. [E] "Local browser use This feature moved from Frontier to general availability to all Microsoft 365 Copilot tenants. Cowork can complete web tasks for you in Microsoft Edge on your device, using your existing sign-ins and your organization's policies. Requires that Edge is installed." — heading "August 2026" / "Enhancements". Local browser use reached GA in August 2026, having previously been Frontier-only (per the June 2026 GA entry further down the same page).
3. [B/D] "Workspace file input for plugin tools Plugin connector tools can now accept files from your session as input. Plugin authors declare a tool parameter with contentEncoding: base64 , and Cowork resolves the workspace file to content before calling the tool—so a tool can convert a document, analyze an image, or attach a file to another system." — heading "August 2026" / "Enhancements". This is a plugin-tool capability, not a built-in skill.
4. [D] "Expanded skills support You can now add 50 custom skills through natural language or OneDrive." — heading "April 2026" / "New features". Dates the 50-custom-skill ceiling to April 2026 (up from an unspecified earlier lower number).

Silent on: C, F (no output-format or folder-browsing changelog entries on this page).

---

## 5. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-local-browser

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `reader-1/f1_cowork-local-browser.html`; verified by canonical-URL match).
Page title: "Use the local browser with Copilot Cowork | Microsoft Learn"
Page date: "Last updated on 2026-09-16"

1. [E] "Microsoft Copilot Cowork can complete browser automation for you in Microsoft Edge on your device, using the sites you're already signed in to. Cowork shows its work in a hidden Edge tab so you can stay in the conversation while it acts on your behalf." — intro paragraph.
2. [E] "Because the tab runs in your own copy of Edge, it uses your existing single sign-on, cookies, and sessions. The agent has exactly the same access to sites that you have when you browse by hand — no more and no less. Credentials, cookies, and session tokens stay on your device." — heading "How browser use works".
3. [E] "Where browser use is available Browser use is available in Cowork on the web at m365.cloud.microsoft . Surface Browser use supported? Cowork on the web (Microsoft Edge) Yes Cowork on the web (other browsers) Not yet. More information: If you're not using Microsoft Edge Microsoft Copilot desktop app No. If you ask the desktop app to run a browser task, Cowork tells you that browser tasks run in Cowork on the web." — heading "Where browser use is available". States the desktop app cannot run browser tasks at all.
4. [E] "In the Cowork conversation, describe the task—for example, "File my expense report in Concur for last week's trip to Seattle" or "Find the cheapest nonstop flight from SEA to JFK on Friday and put a hold on it." Watch the conversation. Cowork shows progress chips as it works, such as Opening Concur , Filling expense details , or Submitting form ." — heading "Run a browser task". Shows navigation and form-filling by example, not as an explicit bulleted capability list.
5. [E] "For most tasks, you never see the Edge tab. In a few cases, Cowork asks you to take over and shows the tab, including: When a CAPTCHA or human-verification prompt appears and must be resolved. When credentials , such as a password , or a multifactor authentication code are needed. When account settings must be changed, or when the account is locked or requires a password reset ." — heading "When Cowork hands the browser back to you". States what it cannot do unattended: CAPTCHAs, credential entry, account-locked recovery.
6. [E] "Sites your organization blocks Because Cowork drives your local Edge, it inherits every site restriction your admin already enforces — web filtering, Conditional Access, browser-management policy, and Microsoft Purview data loss prevention (DLP). The agent has the same reach you do, never more." — heading "Sites your organization blocks".
7. [E] "Resume an interrupted browser task If a browser task is interrupted — for example, you close the tab, put your device to sleep, or lose your network connection — Cowork pauses the task instead of failing it." — heading "Resume an interrupted browser task".

Silent on: A, B, C, D, F. This page also never states whether a file downloaded through the browser, or content read from a page, becomes part of the session's Input/Output folders — that specific sub-question of E is unanswered here.

---

## 6. https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-take-control-actions

Fetched: yes, via curl with a browser User-Agent (this task; not previously present in the shared scratchpad).
Page title: "Take control of Microsoft Copilot Cowork actions before they run (Preview) | Microsoft Support"
Page date: `ms.date` "09/14/2026"
Note: this article's "Important" banner states "Microsoft Copilot Cowork for personal accounts is currently in Preview. This information relates to a prerelease product that may be substantially modified before it's released."

1. [C] "Before Cowork takes certain actions, including writing files, it asks for your permission." — intro sentence.
2. [C] "When Cowork creates or modifies files during a conversation, they appear in the side panel on the right. The side panel shows the task Progress , the Input folder with files you provide as context, and the Output folder with files Cowork creates. Each output file has Download and Preview buttons." — heading "Review files and results". "Modifies" again implies in-place editing of a file, alongside creation.
3. [A] "For scheduled or recurring tasks, Copilot may ask for required approvals during setup so the task can run unattended in the future." — heading "When is user approval required?". Directly confirms a scheduled/recurring task can run unattended after its approvals are granted once at setup.
4. [C] "Account altering actions , including deleting files, modifying cloud storage, canceling subscriptions, or changing account settings." — heading "When is user approval required?" (bulleted list item). Names file deletion and cloud-storage modification as approval-gated action categories.

Silent on: B, D, F.

---

## 7. https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-manage-tasks-schedule-prompts

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `gap-read-sessions/cowork-manage-tasks.html`; verified by canonical-URL match). This is the support-article "known one" pointed to by task instruction 6 for scheduling.
Page title: "Manage tasks and schedule prompts in Microsoft Copilot Cowork (Preview) | Microsoft Support"
Page date: `ms.date` "09/14/2026"
Note: same personal-accounts-Preview banner as page 6 above.

1. [D] "As Cowork works, it loads specialized skills for tasks like creating documents, managing your calendar, and preparing briefings. When it uses a new skill during your conversation, a message such as "Preparing to compose emails" appears, and the skill shows up in the side panel." — heading "Extend Cowork with skills".
2. [D] "If you sign in with a work or school account, you can extend Cowork with your own custom skills stored in OneDrive, and share skills you create with other people in your organization." — heading "Extend Cowork with skills". Ties custom-skill creation/sharing to work-or-school accounts specifically.
3. [A] "To see all your conversations with Cowork, select the My tasks view. Use the Filters dropdown to show only specific tasks, such as those that need your input, are in progress, are complete, or are scheduled." — heading "Manage your tasks".
4. [A] "You can schedule a prompt to run automatically at a set time or on a recurring basis. Scheduled prompts are useful for tasks you want Cowork to handle regularly, such as a daily briefing or a weekly status report." — heading "Schedule prompts".
5. [A] "Describe the task and the timing in your message using natural language—for example, "Send me a daily briefing every morning at 9 AM." Cowork confirms the schedule and asks for your approval before activating it. You can edit, pause, or cancel scheduled prompts from the Scheduled tab in the My tasks view or the Scheduled section in the side panel." — heading "Schedule prompts".

Silent on: B, C, E, F.

---

## 8. https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-uses-stores

Fetched: yes, via curl with a browser User-Agent (reused from an earlier curl fetch by a sibling agent this session at `gap-read-sessions/cowork-uses-stores.html`; verified by canonical-URL match). Chosen for task instruction 6's "working with files" support article.
Page title: "What Microsoft Copilot Cowork uses and stores (Preview) | Microsoft Support"
Page date: `ms.date` "09/14/2026"
Note: same personal-accounts-Preview banner.

1. [A] "Conversation and task history : Your prompts and Copilot's responses are saved so you can review past tasks." — heading "Cowork can use and store limited data to perform and review tasks:" (bulleted list item).
2. [E] "Screenshots : For browser-based tasks, Copilot may capture screenshots of pages it interacts with to understand and complete the task. Copilot does not capture screenshots while you are in control of the browser, though screenshots taken once you return control of the browser to Copilot may include information you entered on the screen. Non-browser tasks do not capture page screenshots." — same list.
3. [A] "Connectors : Copilot may link to other services via connectors you authorize to perform tasks, such as drafting your emails or managing your calendar. Copilot accesses information from these services only as needed to perform a task, and upon your direction it may do so on a scheduled, recurring, or ongoing basis." — same list. Confirms connector-backed actions, not only prompts, can run on a schedule.
4. [C] "Generated files, apps, and other content : When Cowork creates or updates files, apps, or other content, it may use information from your current conversation, enabled skills, and authorized plugins. Review generated files, apps, and other content before sharing them." — same list.
5. [E] "Always review forms that Cowork has filled-in before submitting." — heading "Limitations".
6. [B/F] "Cowork can't access files stored on your local device. It works with files in OneDrive and other connected cloud services. Cowork can't delete files or folders in OneDrive or SharePoint." — heading "Limitations".

Silent on: D. No mention of scanned/OCR documents, tracked changes/comments, or pointing a task at a whole folder.

---

## 9. https://support.microsoft.com/en-us/microsoft-365-copilot/get-started-with-cowork

Fetched: yes, via curl with a browser User-Agent (this task; not previously present in the shared scratchpad). Chosen for task instruction 6's "what Cowork can create" support article; the actual page title covers personal accounts specifically.
Page title: "Get started with Microsoft Copilot Cowork for personal accounts (Preview) | Microsoft Support"
Page date: `ms.date` "09/14/2026"

1. [C] "Create and edit Word documents, Excel spreadsheets, PowerPoint presentations, and PDFs. Draft, reply to, and send email, and manage your calendar. Manage your files in OneDrive." — heading "What you can do with Cowork". First bullet group of the page's direct answer to "what can Cowork create".
2. [A] "Research topics across multiple sources and compile the results. Prepare daily briefings and summaries. Run prompts on a schedule so recurring tasks happen automatically." — heading "What you can do with Cowork", continuing the same bullet list.

Silent on: B, D, E, F (beyond the OneDrive file-management line already quoted under C).

---

## 10. https://support.microsoft.com/en-us/microsoft-365-copilot/cowork-start-conversation

Fetched: yes, via curl with a browser User-Agent (this task; not previously present in the shared scratchpad). Chosen for task instruction 6's "working with files" support article (attach-files detail).
Page title: "Start a conversation in Microsoft Copilot Cowork (Preview) | Microsoft Support"
Page date: `ms.date` "09/14/2026"
Note: same personal-accounts-Preview banner. This page also states the message box "can type up to 16,000 characters" — a lower figure than the 250,000-character limit given on the Learn pages (1 and 3 above) and in the FAQ, consistent with this being the older/personal-preview UI rather than the work-or-school Cowork documented elsewhere.

1. [B] "Attach files : Drag and drop files onto the text box, select Upload images and files to browse your device, or select Attach cloud files to pick files from OneDrive or, for enterprise accounts, SharePoint or Teams." — bulleted list under the "Enter your request" steps. Shows SharePoint/Teams cloud-file attachment is gated to enterprise accounts; OneDrive is available to all.
2. [D] "Skill messages : Indicate when Cowork loads a skill it needs, such as "Preparing to compose emails" or "Preparing to create Word documents."" — heading "Follow along as Cowork works".

Silent on: A is referenced only by "Related topics" links ("Manage tasks and schedule prompts"), not described on the page itself; C, E, F entirely silent.

---

## 11. https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/get-started

Fetched: yes, via curl with a browser User-Agent (this task; found via web search for a Microsoft Learn page on Cowork automation per task instruction 7, not previously present in the shared scratchpad).
Page title: "Get started with Copilot Cowork | Microsoft Learn"
Page date: "Last updated on 2026-09-14"

1. [A] "Automations: View, edit, reschedule, and clean up your scheduled tasks without hunting through menus." — heading "Open Cowork" (bulleted description of the Cowork homepage).
2. [A] "You can filter tasks by those that need input, those that are still in progress, completed tasks, and scheduled tasks. The scheduled filter includes both scheduled prompts and event-driven tasks." — heading "View your created tasks". Confirms the task filter's "scheduled" bucket covers both automation kinds.
3. [C] "Preview files directly in the browser. Supported formats include PDF, Microsoft 365 documents (Word, Excel, PowerPoint), Markdown, code files, images, CSV, HTML, and email." — heading "Review your results". Lists HTML explicitly among previewable/output formats.
4. [C] "Download individual files to your device, or select Download All to download every file as a single zip archive." — heading "Review your results".

Silent on: B, D (beyond skill-message UI already covered elsewhere), E, F.

---

## Extra page: https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-available-plugins

Fetched: yes, via curl with a browser User-Agent (this task; found via web search while looking for the point-7 automation page, kept because it directly bears on D's built-in-vs-plugin distinction).
Page title: "Available plugins for Copilot Cowork | Microsoft Learn"
Page date: `ms.date` "2026-09-01"

1. [D] "Microsoft Copilot Cowork includes ready-to-use plugins that help teams connect more of the tools, data, and expertise they rely on every day." — intro paragraph. The rest of the page is a catalog of named third-party/Microsoft plugins (Jira, Salesforce, Dynamics 365, etc.), which are plugin skills, not built-in skills, and so fall outside categories A-F as defined for this fact-check.

Silent on: A, B, C, E, F.

---

## Summary table

| # | Documented (quote numbers) | Undocumented / not stated on any fetched page |
|---|---|---|
| **A. Scheduled/event-driven tasks** | Recurring or fixed-time scheduling in natural language; a "Runs" tab showing each past/upcoming run and literal "run history" for event-driven tasks; triggers named as "When you receive an email", Teams channel message, Teams chat message (with @mention filter); a cap of 25 scheduled prompts; "Run in" a new vs. continuing conversation; unattended execution after one-time setup approval; rate limiting on event-driven tasks. (Page 1 #9-11,19-27; Page 2 #6-9; Page 3 #2,6,11; Page 4 #1; Page 6 #3; Page 7 #3-5; Page 8 #1,3; Page 9 #2; Page 11 #1-2.) | Whether a scheduled/event-driven run can itself read files the user placed earlier and write outputs is implied by the shared Input/Output-folder model (Page 1 #9) but never stated for an automated run specifically; whether a run can be explicitly "chained" to a later run beyond "continues the current conversation"; no description of processing a large data room "in batches"; no numeric limit on event-driven tasks (only scheduled prompts' 25-task cap is given). |
| **B. Input file types and reading** | Full extension table (Word/Excel/PowerPoint/PDF/Markdown/Image/Text/Code/Config/Notebook/Audio/Video/Archive incl. zip); PDF and email are both previewable/referenceable; 200 MB per attached-file limit; encrypted files cannot be read. (Page 1 #5-8; Page 2 #3-5,13; Page 10 #1.) | No mention anywhere of OCR, scanned or image-only PDFs, handwriting recognition, Word tracked changes, or Word comments being read; "password-protected" is never used verbatim (only "encrypted" and, separately, "sensitivity label" — Page 2 #2,13 — with no statement on whether a labelled-but-unencrypted file is readable). |
| **C. Outputs and writing back** | Creates Word/Excel/PowerPoint/PDF from scratch and can "edit and refine existing documents you share"; "creates or updates/modifies files"; multi-file output as a single zip (up to 50 files/500 MB); files saved to OneDrive/SharePoint and to a dedicated OneDrive "Cowork" folder; image generation via "ChatGPT Images 2.0"; preview/output formats include PDF, Word, Excel, PowerPoint, Markdown, code, images, CSV, HTML, email; cannot delete files/folders. (Page 1 #2-4,28-29; Page 2 #11-13; Page 3 #1,4; Page 6 #1-2,4; Page 8 #4; Page 9 #1; Page 11 #3-4.) | No statement on producing a Word document with tracked changes or comments; no mention of annotating/marking up a PDF; no mention of merging or splitting PDFs or rendering a page to an image; no confirmation that a user can name a specific destination OneDrive/SharePoint folder (only "your OneDrive and SharePoint workspace" / a fixed default "Cowork" folder are named). |
| **D. Built-in skills** | The 14-item list — Word, Excel, PowerPoint, PDF, Email, Scheduling, Calendar Management, Meetings, Daily Briefing, Enterprise Search, Communications, Deep Research, Adaptive Cards, App (Frontier) — repeated identically on three independent pages, each with a one-line description on Page 1; custom-skill limits (50 skills, 1 MB SKILL.md, 20 companion files/10 MB); plugin skills distinguished from built-in skills but stated to "work the same way." (Page 1 #13-18; Page 2 #1; Page 3 #3,7-9; Page 4 #4; Page 7 #1-2; Page 10 #2; Extra page #1.) | The skill is called "Deep Research", never "Researcher"; the PDF skill's description is the single unelaborated line "Work with PDF documents" — no detail on what PDF operations it performs; no dedicated "App" skill detail beyond the one-line description quoted; "legal research" is named only as an example of what a third-party *plugin* (not a built-in skill) can add (Page 3 #9). |
| **E. Browser use** | Runs in a hidden Microsoft Edge tab using the user's own sign-in/cookies/sessions, "no more and no less" access than the user; works only in Cowork on the web in Microsoft Edge (not other browsers, not the desktop app); shown by example filling forms and navigating (expense report, flight booking); hands control back for CAPTCHAs, credential/MFA entry, and locked-account recovery; inherits organizational site-blocking (DLP, Conditional Access); pauses and can resume an interrupted browser task; captures screenshots of pages during browser tasks (not while the user holds control). (Page 2 #10; Page 4 #2; Page 5 #1-7; Page 8 #2,5.) | No explicit statement that a file downloaded through the browser, or content read from a page, lands among the session's Input/Output files — the local-browser page is silent on this specific link; no bulleted "can do X, cannot do Y" list — capabilities are shown only through examples. |
| **F. Working with folders** | Can create SharePoint/OneDrive folders and reorganize files into new or existing folders; can "browse your SharePoint and OneDrive folders and select files to work with" via a breadcrumb tree-view browser; a session has a named Input folder and Output folder; cannot delete files or folders; custom skills are saved into a fixed `/Documents/Cowork/skills/` OneDrive path. (Page 1 #4,9,12,16; Page 2 #2,11,13; Page 3 #4-5; Page 8 #6.) | No sentence confirms a task can be pointed at an entire SharePoint/OneDrive folder as a single unit (selection is described only file-by-file in a tree view); no statement of a folder-listing command/output; no numeric limit on how many files a single session can take (only the 200 MB per-file cap and the 50-file/500 MB *output-zip* cap are given — neither is a stated per-session input-file count). |

---

Pages added beyond the base list (per the "up to 4 more" allowance plus the explicit multi-article instructions 6-7): `cowork-take-control-actions` (explicitly named), `cowork-manage-tasks-schedule-prompts` and `cowork-uses-stores` (support articles for scheduling/files per instruction 6), `get-started-with-cowork` and `cowork-start-conversation` (support articles for "what Cowork can create" and "working with files" per instruction 6), `cowork/get-started` (Learn page on automations per instruction 7), and `cowork-available-plugins` (linked from the overview page's "Extend with plugins" section, kept for the built-in-vs-plugin distinction under D).

All twelve pages returned HTTP 200 to a plain `curl -sL` with a Chrome desktop User-Agent string; none required WebFetch or jina fallback. Five pages (use-cowork, cowork-faq, the overview, whats-new, cowork-local-browser) were fetches already sitting in this session's shared scratchpad from a sibling agent's run minutes earlier — each was re-verified here against its `rel="canonical"` tag before reuse, and all carry `ms.date`/"Last updated on" stamps of 2026-09-08 through 2026-09-16, i.e. fetched within the last two weeks of today's date (2026-09-19). The other seven pages were fetched fresh in this task.
