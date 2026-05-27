---
description: "Use when editing Python development code under dev/. Enforces clean CLI design, typing, and safe I/O."
applyTo: "dev/**"
---

# Python dev guidelines (dev/)

- Keep public entrypoints in `dev/src/*/cli.py`.
- Prefer `pathlib.Path` over raw string paths.
- Validate inputs early; return non-zero exit codes for failures.
- No network calls unless explicitly required by requirements.
- Use type hints on all public functions.
- Prefer small, single-responsibility functions.
- Handle errors explicitly with user-actionable messages.
