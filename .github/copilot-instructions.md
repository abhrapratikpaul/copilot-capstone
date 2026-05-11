# Copilot Workspace Instructions

## Project goal
Build an Agentic SDLC pipeline for a small application using GitHub Copilot Agents.

## Hard constraints
- **Python dev code lives only under `dev/`**.
- **Playwright + TypeScript verification lives only under `test-automation/`**.
- Do not mix TS tooling/config into `dev/` and do not add Python tooling/config into `test-automation/`.

## Docs workflow
- Treat `user-story.md` as the source input.
- Keep `requirements.md`, `architecture.md`, `design-review.md`, and `impl-plan.md` consistent with each other.
- When updating docs, prefer small, auditable diffs.

## Safety
- Never output or commit secrets.
- Prefer environment variables (document names in README when needed).

## Git
- Keep changes scoped to the current SDLC step.

## Copilot SDLC Agents

This repository defines **8 custom Copilot agents**, one per SDLC step, plus matching prompts and skills.

## Steps
1. **Requirements** → updates `requirements.md` from `user-story.md`
2. **Architecture** → updates `architecture.md` based on `requirements.md`
3. **Design Review** → reviews `architecture.md`, writes `design-review.md`
4. **Implementation Planning** → writes `impl-plan.md`
5. **Implementation** → adds Python code under `dev/`
6. **Review** → performs structured self-review and suggests fixes
7. **Verify** → adds/runs Playwright TypeScript verification under `test-automation/`
8. **PR** → creates branch + opens PR via GitHub MCP (after confirmation) and generates PR description/checklist

## Where to run
- Prompts: `.github/prompts/*.prompt.md` (type `/` in Copilot Chat)
- Agents: `.github/agents/*.agent.md` (agent picker)
- Skills: `.github/skills/*/SKILL.md` (type `/`)
