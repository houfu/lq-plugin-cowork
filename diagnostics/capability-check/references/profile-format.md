# The capability profile: `lq-capabilities.md`

One file per tenant. The tester keeps it and attaches it to every probe
conversation; the results collect in it. It has three parts, always in this
order. Keep the headings and the block markers exactly as shown: the build
tooling reads the `[capabilities]` block, and a skill that is switched at run
time reads the same lines.

## 1. Posture

```markdown
# LegalQuants capability profile

- Tenant: <a label the tester chooses>
- Client: <Cowork on the web in Edge | Cowork desktop | ...>
- Web search: <on | off | not known> (as the tester understands it)
- Browser use: <enabled | disabled | not known>; <who enabled it, if anyone>
- Built-in skills seen: <the exact names, verbatim, comma-separated>
- Profile started: <YYYY-MM-DD>
- Last updated: <YYYY-MM-DD>
```

## 2. Results

A table with one row per run, oldest first. Rows are never edited or removed;
a re-run is a new row.

```markdown
## Results

| Date | Probe | Verdict | Tester | Evidence |
| --- | --- | --- | --- | --- |
| 2026-10-01 | P7a | pass | AB | HTML saved as probe-summary.html; tester found the template footer and the marker matched |
| 2026-10-01 | P3 | partial | AB | both insertions quoted with authors; deletion missed; clean copy: "none" |
```

- **Verdict** is one of `pass`, `partial`, `fail`, `disabled`, in the tester's
  words. `disabled` means the tenant has the feature turned off, not that it
  failed.
- **Tester** is initials or a handle, never a full name.
- **Evidence** is one line: what the skill quoted or produced, and what the
  tester checked it against. Never the tester's check words, never content
  from a real document, and for P14 counts only.

## 3. The `[capabilities]` block

The switch lines, one per probe, always all fifteen (P7 has two arms), in
this order. Each line is `<probe>: <state> <date>`, where state is `pass`,
`partial`, `fail`, `disabled` or `unknown`, and the date is that of the run the
state came from (omitted for `unknown`). The latest run wins.

```markdown
## [capabilities]

P1: unknown
P2: unknown
P3: partial 2026-10-01
P4: unknown
P5: unknown
P6: unknown
P7a: pass 2026-10-01
P7b: unknown
P8: unknown
P9: unknown
P10: unknown
P11: unknown
P12: unknown
P13: unknown
P14: unknown
```

Nothing but these lines goes in the block. Comments, notes and caveats belong
in the Evidence column. A `partial` never switches anything on; it is recorded
so the maintainer can see what came close.
