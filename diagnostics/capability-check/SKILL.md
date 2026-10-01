---
name: capability-check
description: |
  Runs the LegalQuants capability probes in this Cowork tenant, one probe per
  conversation, and keeps the results in a capability profile the tester
  carries from one conversation to the next: which of the fourteen things the
  adapted skills were cautious about actually work here, with the evidence
  for each. Use when the user asks to "check what Cowork can do here", "run a
  capability probe", "test whether tracked changes can be read in this
  tenant", "record this probe result in my capability profile", "which
  LegalQuants skills could run their full version here", or "write up my
  probe results for the issue tracker". Do not use for testing whether a
  particular skill activates or behaves as described; this skill tests the
  environment, not the skills, and it never does legal work.
license: Apache-2.0
metadata:
  adapted-for: "Microsoft 365 Copilot Cowork"
  status: "draft; not yet part of the build, see docs/capability-switches.md"
---

# Capability check

The LegalQuants skills for Cowork were adapted around fourteen open questions
about what Cowork can do. Where the answer was unknown, the skill was written
for the cautious answer: it reads instead of running a program, it announces a
degrade, it hands the lawyer a register to check instead of a count it cannot
show. This skill finds out, in the tenant in front of you, which of those
cautious answers were needed.

It does that by running one **probe** at a time and recording what happened in
a **capability profile**: a Markdown file the tester keeps and brings back.
The profile is what later decides which skills can be switched up to their
fuller behaviour.

You are the instrument here, and the instrument is the thing under test. That
shapes every rule below.

## Rules that do not bend

1. **Synthetic material only.** Every file is one the tester invented for the
   probe. If anything attached looks like real client or matter material, stop
   and say so before reading further. P14 is the one probe that searches the
   tenant's real content; its entry says what may be recorded from it, and
   that is counts only.
2. **You never grade yourself.** You report what you did and what you saw; the
   tester compares it with what they know is in the file and gives the
   verdict. A pass is recorded only in the tester's words. Most probes exist
   because a confident answer with nothing behind it looks exactly like a
   right one, and you cannot tell those apart from the inside.
3. **The tester's check words stay with the tester.** Setups ask the tester to
   plant words of their own invention in the probe files. Never ask what they
   are and never guess them. If the tester types a file's check word into the
   chat before the probe has run, say the probe is spoiled for this
   conversation and ask them to pick new words and start a fresh one. Three
   probes — P2, P5 and P11 — are different by design: their setup has the
   tester type the check word into an earlier conversation or an earlier
   message, because what they test is whether it comes back.
4. **Say what you could not see.** "I could not tell" is a result. "There is
   nothing there" is a different result, and you may say it only when you can
   show why — never as a stand-in for not being able to look.
5. **Quote, do not paraphrase.** When a probe asks what a file or page says,
   give the exact text in quotation marks, or say you cannot give exact text.
6. **One probe per conversation.** A probe run in a conversation that already
   did other work measures the wrong thing. If this conversation has already
   run a probe or done other work, record results but run no new probe here;
   tell the tester to start a fresh conversation for it.

## What the tester can ask for

Work out which of these the tester wants from what they say. If they say
nothing specific, start with the first.

### 1. Start: the menu and a blank profile

Read [the probes](references/probes.md). Show the menu in four groups, one line
per probe — its id, its question in plain words, and roughly how long it takes:

- **Run now, in one conversation:** P3, P4, P6, P7a, P8, P10, P11.
- **Needs a second conversation on another day:** P2, P5, P9, P13.
- **Needs an administrator first:** P12, and P6 when web search is off.
- **Needs real tenant content:** P14. Only where the tester is allowed to
  search the organisation's material, and nothing from it is recorded but
  counts.
- **Needs a separate probe package:** P1 and P7b. Say they cannot run from this
  skill today and are listed so the profile is complete.

Recommend **P7a** first: it needs nothing prepared and it runs against this
skill itself. Recommend **P3** and **P4** next: between them they decide the most
skills.

Then ask the tester for the posture lines the profile opens with — a label for
the tenant (not its real name if they would rather not), the Cowork client
(web or desktop, and which browser), whether they know web search to be on or
off, and today's date — and create the profile as `lq-capabilities.md` in the
Output folder, in the format in [the profile format](references/profile-format.md),
with every probe marked `unknown`. Say plainly that the file stays in the
Output folder, that they should keep a copy, and that they attach it to every
later probe conversation so the results collect in one place. Then tell them
to open a fresh conversation for their first probe: this one has done work
now, so a probe run here would measure the wrong thing.

### 2. Run one probe

The tester names a probe, or describes the capability; match it to its id.

1. **Check the conversation is fresh** (rule 6). P11 is the one exception: its
   setup is the earlier work in the conversation, and the probe entry says
   which.
2. **Make sure the probe reaches you.** If any LegalQuants bundle or another
   skill is installed in this tenant, a probe's task can be picked up by a
   skill built for that kind of work — a tracked-changes request by a redline
   skill, say — and the result then measures that skill, not Cowork. Ask the
   tester to choose this skill in the conversation's Sources picker before
   typing the task, and record in the profile whether other LegalQuants skills
   were installed.
3. **Give the setup** from [the probes](references/probes.md): what to make, how
   to plant their own check words, and what to write down for themselves. Wait
   until they say it is ready and have attached what the probe needs.
4. **Say you are about to run it**, and run exactly the task the probe
   describes, as a lawyer would ask for it, on the attached files. Do the task
   for real: if the probe asks for a file, produce the file.
5. **Report in three parts**, in this order, under these headings:
   - **What I did** — the steps, including anything you tried that did not work.
   - **What I saw** — the exact text, pages, authors or cells, quoted.
   - **What I could not see or do** — every gap, named.
6. **Hand over the check.** Give the tester the check from the probe's entry —
   what to compare, and where to look in Word, Excel or the file itself — and
   ask for their verdict: **pass**, **partial**, **fail**, or **disabled** (the
   tenant has the feature turned off). A refusal from you is not a fail of the
   probe; it is a result, and it is recorded as what happened.
7. **Record it**, as in 3 below.

### 3. Record a result

This works whether the probe ran in this conversation or elsewhere.

- If the tester attached `lq-capabilities.md`, read it and add to it. If not,
  ask for it; if they have none, create one as in 1 and say so.
- Add one row to the results table and set the probe's line in the
  `[capabilities]` block, both exactly as [the profile format](references/profile-format.md)
  says. The verdict is the tester's word. The evidence is one short line: what
  you quoted or produced, and what the tester checked it against — never the
  tester's check words themselves.
- Never change an earlier row. A second run of the same probe is a new row, and
  the `[capabilities]` line takes the newer result with its date. If the two
  runs disagree, say so; the disagreement is itself worth reporting.
- Save the updated profile to the Output folder under the same name and tell the
  tester it is the version to keep. Cowork cannot delete the older copy, so
  say which is the current one by its date line.

### 4. What this unlocks

Read the attached profile and [the switch map](references/switches.md). For each
probe the tester has recorded, say in one or two lines which skills change and
how — the fuller behaviour a pass would let them switch to, or the caution a
fail confirms. Keep to the map's own words. Say that nothing changes in any
installed skill until the maintainer or administrator builds and installs a
package from the profile; this skill switches nothing itself.

### 5. Write up for the issue tracker

Produce the text of one report per probe for the project's UAT report form: the
probe id and question, the posture lines, the prompt as run, the three-part
report, the tester's verdict and the evidence line. Leave out the tester's check
words, anything from a real document, and for P14 every name and quotation —
the count of people named and whether each had a document is enough. Offer it
in chat to copy; this skill does not post anything anywhere.

## The standing check

On any run, ask the tester to note the exact names of the built-in skills their
tenant offers, as the side panel and the Sources picker show them, and record
the list verbatim in the profile's posture lines. One name in particular is in
doubt: whether the research built-in is called "Deep Research" or "Researcher"
in this tenant.

## What you must not do

- Say a probe passed. Only the tester says that.
- Invent a file, a page, an author, a formula or a search result to complete a
  report. An empty "What I saw" with a full "What I could not see" is a good
  result.
- Tell the tester a skill has been switched up. The profile is evidence; the
  switch happens in a build.
- Delete, overwrite or clean up anything. Every file you write stays in the
  Output folder and is named in your reply.

LegalQuants skills are a workflow aid, not legal advice. This one does no legal
work at all.
