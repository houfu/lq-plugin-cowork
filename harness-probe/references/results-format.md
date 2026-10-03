# The results file

`<run>/results.json` is the whole record of a probe run. The report is
computed from it; the LegalQuants Cowork repository keeps contributed copies
in `probe-results/` and renders them on its site.

```json
{
  "schema": "lq-harness-probe-results/1",
  "harness": {
    "name": "Claude Code web, Opus",
    "profile": "upstream",
    "client": "claude.ai/code",
    "version": "",
    "model": "claude-...",
    "recorded_by": "",
    "posture": {"web_search": "on", "browser": "off"}
  },
  "results": [
    {
      "probe": "P17",
      "outcome": "pass",
      "date": "2026-10-01T09:30:00+00:00",
      "observer": "script",
      "evidence": "digest matches",
      "codes": {},
      "facts": {},
      "notes": "",
      "issue": ""
    }
  ]
}
```

- `profile` is the default the report uses: `upstream` (vendored skills) or
  `cowork` (adapted cards). `report --both` writes both.
- `outcome` is one of `pass`, `fail`, `refused`, `fluent-fake`, `not-run`,
  `pending`.
- `observer` says who judged it: `script` (hprobe.py checked it), `agent`,
  `user` or `maintainer`.
- `codes` overrides the outcome for single capability codes, as P1 does for
  EXEC and BIN.
- `facts` carries what a check measured; P1's facts (Python version, packages,
  programs) are judged against each skill's runtime needs.
- Several results for one probe may coexist; the newest by `date` wins, so a
  re-run never needs the old entry deleted.
- `issue` links the GitHub issue a result was reported in, when there is one.

Keep the file free of anything confidential: it holds probe outcomes about
synthetic fixtures and nothing else.
