---
name: "SDLC 03 Design Review"
description: "Review architecture.md and produce design-review.md with a verdict."
argument-hint: "Confirm architecture.md is ready for review"
agent: "sdlc-step-03-design-review"
model: ["GPT-5 (copilot)"]
---

Critically review `architecture.md` against `requirements.md`.

Produce `design-review.md` with:
- Scored review (categories)
- Findings with severity
- Verdict: approve | approve_with_concerns | reject
- Recommended fixes
