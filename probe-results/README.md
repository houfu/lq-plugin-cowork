# probe-results/

One `results.json` per harness run of the [harness-probe skill](../harness-probe/SKILL.md),
in the `lq-harness-probe-results/1` shape described in
[results-format.md](../harness-probe/references/results-format.md). The build
validates every file here (LQC-K007), and the build report and the site's
Verdicts page judge each one against `capabilities.yaml`.

To add one: run the skill on a harness, then attach `<run>/results.json` to a
[Probe report](https://github.com/houfu/lq-plugin-cowork/issues/new?template=probe-report.yml).
A maintainer copies it here as `<harness-slug>.json`. Results files hold probe
outcomes about synthetic fixtures only: nothing confidential, no client material.

| File | Harness | Recorded |
|---|---|---|
| [claude-code-web.json](claude-code-web.json) | Claude Code on the web, in its cloud container, the agent probing itself | 1 October 2026 |
