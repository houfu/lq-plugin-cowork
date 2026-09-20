# Contributing

This repository adapts the open [LegalQuants
skills](https://github.com/LegalQuants/lq-plugin-oss) into three Microsoft 365
Copilot Cowork plugin packages — litigation, transactional and companion —
mirroring the three plugins upstream publishes, so all thirty-one skills ship.
It is a small, opinionated build, and the most valuable contribution right now
has nothing to do with Python.

## Ways to help

### 1. Test a bundle in a real tenant and report what happened

This is the one the project actually needs. Nothing here has been run in a live
Cowork tenant. If you have Microsoft 365 Copilot with Cowork, install a bundle
([docs/INSTALL.md](docs/INSTALL.md)), work through
[docs/TESTING.md](docs/TESTING.md), and file what you saw with the
[UAT report form](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml).
There is one open
[help wanted issue](https://github.com/houfu/lq-plugin-cowork/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
per skill, each carrying that skill's routing checklist; claim one in a comment
so two people do not test the same thing.

Worth more than a skill test: run one of the **fourteen capability probes** in
Part E of [docs/TESTING.md](docs/TESTING.md). Each is one prompt in one fresh
conversation, and each settles a question about Cowork that nobody has
answered — several skills move a tier the day a probe comes back. They have
their own issues, labelled `probe`.

A negative result is a result. "Typed the prompt, a different skill answered" is
the single most useful sentence you can send. Sanitise everything and never
paste client material — see Part C of [docs/TESTING.md](docs/TESTING.md).

### 2. Fix a description

Cowork routes on a skill's `description` and nothing else, so a misfire is a
description problem, not a code problem. The fix is an edit to
`skills/<name>/skill.yaml`: sharpen the trigger phrases, add the missing
hand-off sentence ("Do not use for X (use the Y skill)"), or adjust the
overlapping neighbour's description in the same pull request. Add the prompt
that misfired to that card's `triggers` so the regression is recorded, then run
`make package` and check `dist/<bundle>-trigger-tests.md`.

Descriptions are capped at 1024 characters (`LQC-D001`), so every sentence has
to earn its place.

### 3. Review or improve a section overlay

Every amber and red card carries two records. `notes` is the technical one —
what the adaptation changed from upstream, in build terms. `cowork.differs` is
the lawyer-facing one: one paragraph, plain words, no file names, saying how
this skill differs from the original. Those two are where the judgement calls
live, and a second reader is welcome: does the rewritten section still carry the
legal method upstream intended, or did something load-bearing go out with the
scripts? Does `differs` say the thing a lawyer would want to have been told
before they relied on it? Compare `upstream/skills/<group>/<name>/SKILL.md` with
`dist/<bundle>/skills/<name>/SKILL.md` and say what you find. If you change an
overlay, update both records in the same commit.

### 4. Adapting a red skill

A **red** card is one of the fourteen skills whose upstream version leans on
machinery a Cowork package cannot carry: a local Python pipeline, a worker
runtime, a network fetch it can hash, a `~/.lq/` store, or the agent's own past
session logs. All fourteen now ship, adapted rather than ported. If you want to
improve one, or re-adapt one after an upstream release moves it, this is the
shape of the work.

**Never ship the instructions without the machinery.** A skill that promises
receipts it cannot produce is worse than no skill. Every step needs a path the
host can actually take, and where no path exists the skill says so in the reply
rather than proceeding as though it had one.

**Set the tier by the three tests, in order.** The tier is mechanical, not a
mood:

1. Did the promise change? If the skill now hands back a different deliverable,
   or its own text says a version without the missing thing is unacceptable, it
   is **tier 3** — re-scoped, and the description has to say so in its first
   clause. Nothing below this test rescues it.
2. Otherwise, is a load-bearing step undocumented or contested? Then it is
   **tier 2**, and the tier is discharged when the named probe passes.
3. Otherwise, are all its failures loud — does the lawyer see it fail? Then
   **tier 1**. If a characteristic failure is silent, so that a wrong result
   looks exactly like a right one, it is **tier 2** with a degrade the skill
   announces, however clean the capability picture.

**Tier 4** means a load-bearing step needs a remote MCP connector under
`agentConnectors` — a server somebody operates. That is the honest route for
anything needing a fetch it can hash, and a tier 4 card may not ship in a
bundle (`LQC-K002`).

**Reach for a substitution pattern before inventing one.** The fourteen were
designed against a catalogue, and re-using it keeps them consistent:

- state the lawyer carries — an attached register or dated note — in place of a
  private store, and the skill names the file it looked for when it is missing;
- an Excel register through the built-in Excel skill as the visible record, in
  place of a count a script used to compute;
- an HTML page for the preview pane in place of a rendered image or an
  annotated PDF;
- sequential passes in one session in place of parallel workers, with the
  execution shape recorded and the word "independent" declined;
- tranches the lawyer sizes, in place of a run over a whole folder;
- the publisher's own document, downloaded and attested by the lawyer, in place
  of a fetch;
- a hand-off to a named built-in — Word, Excel, PowerPoint, PDF, Enterprise
  Search — in place of a bundled program;
- the skill's own documented degraded mode promoted to being the only mode,
  which is usually closer to what Cowork can do than anything an adapter would
  invent;
- and, where none of those works, say the gap out loud: unavailable is said,
  not implied.

**Fill in the `cowork:` block.** It is required on every card and the build
refuses without it (`LQC-K001`): `tier`, `status` (`shipped`, or `probe-gated`
when the skill ships now with a degrade it announces until a probe passes),
`differs` — one paragraph for a lawyer — and, for tier 2 and 3, at least one
known issue (`LQC-K002`). A known issue carries an id unique across the
repository, a title, a detail saying what the lawyer would see and what to do
about it, and `failure: silent | loud`. Where a probe would settle it, name the
probe; `LQC-K003` warns if `probes.yaml` does not define it. `workarounds`
records what the adaptation does instead of upstream's machinery, one line for
each side.

**Name the probe rather than guessing.** `probes.yaml` at the repository root
holds the fourteen capability probes, each with the exact prompt a tester types
and what its result unlocks. If your adaptation rests on something nobody has
tested, it belongs behind a probe — and if `probes.yaml` has no probe for it,
propose one in the pull request rather than writing the card as though the
question were settled.

**Watch the claim words.** `LQC-W011` warns when a built skill says *receipt*,
*certified*, *proved* or *guaranteed complete*. The rule behind it has two
limbs. Where a count or a completeness claim comes from the skill's own reading
rather than from something the lawyer can check independently, those words may
not be used: the permitted form names the method and the scope — "no issues
found in the 62 clauses I read", never "no issues found". And where an answer
rests on a dated snapshot rather than a live source, *currently*, *now*, *the
latest* and *up to date* may not be used, and the snapshot's date appears in the
description, in the first line of the answer and in the closing scope statement.
Like every warning it can be suppressed with a reason; unlike most, it usually
should not be.

## Setup

```sh
git clone --recurse-submodules https://github.com/houfu/lq-plugin-cowork
uv sync --project tools     # or: make setup
make package
```

[docs/DEVELOPING.md](docs/DEVELOPING.md) covers the tooling itself: module
layout, the test suite and how the fixtures work.
[docs/CONTRACT.md](docs/CONTRACT.md) is the specification — config schema,
pipeline order, every validation code, CLI behaviour. Change the contract first,
then the code.

## Adding or adjusting a skill

One folder per shipped skill, named after the skill:

```
skills/<name>/
  skill.yaml        # the card (required)
  SKILL.md          # full-file overlay (optional, last resort)
  sections/*.md     # section overlay bodies (optional)
  patches/*.patch   # unified diffs (optional)
  files/**          # extra or replacement companion files (optional)
```

To add a skill, create `skills/<name>/skill.yaml` with `name`, `upstream`
(`<group>/<name>` under `upstream/skills/`), `anchored_to` (the SHA in
`cowork.yaml`), a Cowork-shaped `description`, `triggers` (3-5 positive
prompts, 3-5 negative ones each tagged `-> other-skill`), and the `cowork:`
block — tier, status, `differs`, and the known issues and workarounds that
follow from them (section 4 above). Add `notes` when the card's `bucket` is
`amber` or `red`.

You do not have to wait for the skill to be in a buildable bundle:

```sh
uv run --project tools lqcowork build --skill <name>
```

builds that one skill into `dist/skills-only/<name>/` through every transform
and runs its per-skill checks. When it is clean, the skill joins a bundle —
which, for a bundle that mirrors an upstream plugin, means writing the card and
letting the mirror pick it up — and `make package` builds the lot.

To adjust one, reach for the **highest layer that does the job** — the higher
the layer, the less an upstream release can silently break it:

1. `exclude` a companion file or folder;
2. `replace` an exact string, with `expect:` so a silent upstream rename fails
   loudly instead of quietly doing nothing;
3. a `sections:` overlay keyed on the heading line;
4. a unified-diff patch;
5. a full-file `SKILL.md` overlay — last resort, and it has to be re-read on
   every upstream bump.

When a warning is correct to leave in place — upstream's own authority links in
a reference file, say — record the decision in the card rather than silencing it
globally:

```yaml
suppress:
  - code: LQC-W010
    file: "references/getting-authorities.md"   # optional glob; omit for the whole skill
    reason: "upstream-authored court and legislation URLs"
```

`code` must be a warning; an error can never be suppressed. `reason` is
required, and every suppression is listed in `dist/build-report.md` under
"Suppressed warnings", so the decision stays visible. Section 4 of the contract
has the full card schema.

## What the build warns about

Errors fail the build; warnings are printed, listed in `dist/build-report.md`
and left for the card owner to judge. Every warning reports `file:line`, and all
of them run over every `*.md` in the built skill unless the rule names SKILL.md.

| Code | What it means |
| --- | --- |
| `LQC-W001` | a vendor word survives (`Codex`, `ChatGPT`, `Claude`, …) |
| `LQC-W002` | a `$name` or `` `/name` `` invocation token survives |
| `LQC-W003` | SKILL.md names a skill that is not in the same bundle |
| `LQC-W004` | a path escapes the skill folder (`../`), or a relative Markdown link points at a file that is not packaged |
| `LQC-W005` | `scripts/` or `schemas/` is mentioned but not packaged |
| `LQC-W006` | the SKILL.md body runs past 3,000 words |
| `LQC-W007` | `hooks`, `~/.lq/`, `CLAUDE_PLUGIN_ROOT`, `argument-hint` or `disable-model-invocation` is mentioned |
| `LQC-W008` | an amber or red card has no `notes` |
| `LQC-W009` | a phrase from `transforms.host_words` survives — host machinery Cowork does not have (`the scribe`, `exit code`, `subprocess`, …) |
| `LQC-W010` | an external `http(s)://` URL the adaptation introduced; a URL that appears anywhere in the upstream skill folder is upstream's and stays exempt wherever it was moved to |
| `LQC-W011` | a claim word survives (`receipt`, `certified`, `proved`, `guaranteed complete`, …) — a claim the model cannot back with something the lawyer can inspect must not be worded as one |
| `LQC-K003` | a known issue names a `probe` that `probes.yaml` does not define |
| `LQC-B002` | a mirrored bundle excludes a skill, with the reason, so the build and drift reports both show it |

Three errors come with the `cowork:` block and the mirrored bundles, and none
of them can be suppressed: `LQC-K001`, a missing or malformed block — no
`tier`, `status` or `differs`, a known issue without an id, title, detail or
failure mode, or a duplicate id anywhere in the repository; `LQC-K002`, a tier 4
card in a bundle, a tier 2 or 3 card with no known issue, or a `probe-gated`
card whose known issues name no probe; and `LQC-B001`, a mirrored bundle
deriving a skill that has no card — write one, or exclude it with a reason.

Section 6 of [docs/CONTRACT.md](docs/CONTRACT.md) is the authoritative list,
including every error code.

## Bumping upstream

```sh
make drift          # report only; the submodule and the pin do not move
make bump           # fetch, report, check out the new SHA, rewrite the pin
```

`drift` fetches upstream, resolves `TO` (default `origin/main`), creates a
temporary git worktree at that commit and builds every bundle against it with
anchor failures downgraded to report entries. The report lands in
`dist/upstream-drift.md` and lists, per skill: whether the upstream folder still
exists, whether its `SKILL.md` or `description` changed since the card's
`anchored_to`, companion files added or removed upstream, whether a full-file
overlay's base moved, plus every anchor failure, validation error and warning,
and any upstream skill that is in no bundle. Read it top to bottom: rows under
"Skills that moved upstream" are things to re-read; rows under "Anchor failures"
are things that will not build until a card is fixed.

After `make bump`, fix whatever the report flagged, re-run `make package`, and
then `make anchor` to record that each card has been reviewed against the new
pin. `make anchor SKILL=<name>` does one card at a time.

## Never edit `upstream/`

`upstream/` is a read-only git submodule pinned to an exact commit. Nothing in
this repository edits it, and a pull request that does will be declined: the
whole point of the layer ladder is that an upstream release can be pulled in
without re-doing the adaptation by hand. If upstream is wrong, fix it upstream.

## Pull requests

The template asks four things, and they are the whole review:

- **Highest layer that works.** If a `replace` would have done it, do not ship a
  patch; if a section overlay would have done it, do not ship a full-file
  overlay. Say in the PR why the layer you picked was necessary.
- **`make package` is green.** No new errors; new warnings explained or
  suppressed with a `reason`. Run `make test` too, and `make fmt` if you touched
  Python (black, line length 88).
- **Card `notes` updated.** If the built output changed, the card says what
  changed and why. An amber or red card without `notes` is warned about
  (`LQC-W008`). If what the lawyer gets changed, `cowork.differs` and the known
  issues change with it, and a card with no `cowork:` block at all fails the
  build (`LQC-K001`).
- **No edits under `upstream/`.**

Keep pull requests small and single-purpose — one skill, or one tooling change.
A description fix and a build change do not belong in the same branch.

## Licensing

This project is Apache-2.0, like upstream. By contributing you agree that your
contribution is licensed under the same terms. Do not paste in material you do
not have the right to license this way, and do not paste client or confidential
material anywhere — issues, PRs, test fixtures or skill content.

You do not need to add licence headers by hand. The build stamps the Apache-2.0
section 4(b) notices itself: a modification notice as the first body line of
every shipped `SKILL.md` naming the upstream commit, the same notice on every
Markdown companion the adaptation changed, an "Added by the lq-plugin-cowork
adaptation" notice on companions this repository wrote, upstream's `LICENSE` at
the root of every zip and [`NOTICE.md`](NOTICE.md) beside it. If a non-Markdown
companion changed, the build cannot annotate it and lists it in
`dist/build-report.md` instead — account for it in the card's `notes`.
