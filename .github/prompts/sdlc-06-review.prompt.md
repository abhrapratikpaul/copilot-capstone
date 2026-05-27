---
name: "SDLC 06 Review"
description: "Perform structured self-review with line-anchored findings."
argument-hint: "Confirm implementation is complete"
agent: "sdlc-step-06-review"
model: ["GPT-5 (copilot)"]
---

Perform a structured code review of the implementation under `dev/`.

Produce findings grouped by severity:
- Critical (must fix)
- Major (should fix)
- Minor (consider)

Apply only minimal, clearly-correct fixes.
