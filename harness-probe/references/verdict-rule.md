# How a verdict is reached

Every skill is rated, per profile, in `data/catalog.json` (built from
`capabilities.yaml` in the repository): each capability it uses is **R**
required, **D** degradable (the skill documents a fallback) or **O** optional.

## A capability's status

Each capability code has **primary probes**; a skill may add **extra probes**
for the same code or for a facet of it (`OUT:pdf-assemble` is "build a PDF
from chosen pages"). For one skill, a capability is:

- **pass** when every one of those probes has passed;
- **fail** when any of them failed, was refused, or was caught as a fluent
  fake;
- **untested** otherwise (not run, or pending a second session).

The newest result for a probe wins. A result can also carry per-code
outcomes, so P1 can pass EXEC and fail BIN at the same time.

For **EXEC** and **BIN**, a passing P1 is then judged against the skill's own
needs: the minimum Python version, the third-party packages and the programs
its scripts call. A harness with Python 3.11 passes P1 but fails EXEC for a
skill whose scripts need 3.12.

## A skill's verdict

| Verdict | Rule |
|---|---|
| **Runs as intended** | Every R and every D capability passes. |
| **Runs on a fallback** | Every R passes, and at least one D failed or is not yet probed. The report quotes the skill's own wording for each lost D. |
| **Cannot run** | At least one R failed. The report names the capability and the probe. |
| **Untested** | No R failed, but at least one R is not yet probed. |

Optional capabilities never change a verdict; the report lists them as also
available or also missing.

A degradable capability that has not been probed counts against "as
intended": nobody can claim a skill runs in full on evidence that does not
exist. It is shown as "unprobed" rather than "failed".

## What to probe next

Probes not yet run are ranked by how many Untested skills they would clear
(it is the last unprobed required capability for them), then by how many
Untested skills they bear on, then by how many fallbacks they would confirm,
then by cost (free, low, setup, two-session, admin).

## Cards that disagree (cowork profile)

For the cowork profile the report compares each card's hand-set status and
tier with the computed verdict and flags, without changing anything: a shipped
card that cannot run on this harness, a probe-gated card whose gate could
lift, and a tier 0 or 1 card that is running on a fallback because a probe
failed.
