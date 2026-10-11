---
name: lq-invoke-canary
description: >-
  Answers with a fixed token when the user calls it by name. It exists only
  so the LegalQuants harness probe (P24) can tell whether
  explicit-invocation-only skills stay quiet until they are called. Its name
  deliberately shares no stem with the probe skill.
disable-model-invocation: true
---

# Harness probe P24

You were invoked by name. Reply with exactly this line and nothing else:

INVOKE-OK-4K7R

Do not run any other skill and do not explain the token.
