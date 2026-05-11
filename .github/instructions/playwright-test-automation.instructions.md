---
description: "Use when editing Playwright + TypeScript verification under test-automation/. Keeps tests deterministic and repo-relative."
applyTo: "test-automation/**"
---

# Playwright verification guidelines (test-automation/)

- Use `@playwright/test` with TypeScript.
- Prefer deterministic checks (no time-based sleeps).
- For doc quality checks, read files via `fs/promises` and assert on headings/required sections.
- Keep tests independent; avoid relying on global state.
- Use repo-relative paths for file operations.
- Write specific assertions with clear error messages.
