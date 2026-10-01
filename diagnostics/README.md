# diagnostics/

Skills for testing the **environment**, not the legal skills. They are not
adaptation cards, they have no upstream source, and they are not part of any
bundle or release yet. See [docs/capability-switches.md](../docs/capability-switches.md)
for the plan that would bring them into the build.

## capability-check

Runs the fourteen capability probes from [probes.yaml](../probes.yaml), one per
conversation, and records the results in a capability profile,
`lq-capabilities.md`, that the tester keeps and brings back each time. The
profile's `[capabilities]` block is the input the capability switches are
designed to read.

Unlike a folder under `skills/`, this folder **is** a finished skill:
`SKILL.md` sits at its root with its frontmatter, and nothing is added at build
time.

### Trying it before it is packaged

1. Get `capability-check.skill`. Until the build packages it, it is made by
   hand with the repository's own archive writer, so it has the same shape as
   every released `.skill`: the contents of `diagnostics/capability-check/`
   at the archive root plus upstream's `LICENSE` and `NOTICE.md`, sorted
   entries, fixed 1980 timestamps, byte-reproducible. It goes to
   `dist/skills/capability-check.skill`, which is not committed. A hand-made
   zip of the folder's contents also uploads, but leaves out the licence
   files.
2. In Cowork, **+**, **Customize**, **Skills**, the arrow next to **Add**,
   **Upload skill**, and pick the file.
3. In a new conversation: "Check what Cowork can do here." You should get the
   probe menu and a blank `lq-capabilities.md` in the Output folder.
4. Run **P7a** first, in its own fresh conversation.

Synthetic material only, as everywhere in [docs/TESTING.md](../docs/TESTING.md).

### Answer key the skill must never see

Some checks need a value the tester compares against that the skill cannot
know. Those values live here, outside the skill folder, and must never be
copied into it.

| Probe | What the tester looks for | Expected value |
| --- | --- | --- |
| P7a | The footer line starting "Template marker:" in the HTML the skill saved | `LQC-7A-ORRERY-5382` |

Every other probe uses check words the tester invents on the day, so there is
nothing to keep here for them. If the marker ever leaks into the skill's own
text, change it in `assets/probe-template.html` and here together.
