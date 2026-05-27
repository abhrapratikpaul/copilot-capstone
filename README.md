# Agentic SDLC Capstone

This repo is scaffolded for an **8-step Agentic SDLC pipeline** driven by GitHub Copilot Agents, Prompts, Skills, Instructions, and Hooks.

## Folder Layout
- `dev/` — Development code (**Python**) only
- `test-automation/` — Verification automation (**Playwright + TypeScript**) only
- `.github/agents/` — 8 custom Copilot agents (one per SDLC step)
- `.github/prompts/` — 8 runnable prompts (one per SDLC step)
- `.github/skills/` — 8 skills (one per SDLC step)
- `.github/instructions/` — file-specific coding instructions
- `.github/hooks/` — agent hooks (guardrails)

## SDLC Documents
- [user-story.md](user-story.md) — Source user story (from Jira)
- [requirements.md](requirements.md) — Functional/non-functional requirements
- [architecture.md](architecture.md) — Technical architecture
- [design-review.md](design-review.md) — Design review verdict
- [impl-plan.md](impl-plan.md) — Implementation plan

## SDLC Pipeline Steps

| Step | Agent | Artifact |
|------|-------|----------|
| 1 | `@sdlc-step-01-requirements` | `requirements.md` |
| 2 | `@sdlc-step-02-architecture` | `architecture.md` |
| 3 | `@sdlc-step-03-design-review` | `design-review.md` |
| 4 | `@sdlc-step-04-impl-plan` | `impl-plan.md` |
| 5 | `@sdlc-step-05-implementation` | code under `dev/` |
| 6 | `@sdlc-step-06-review` | review notes |
| 7 | `@sdlc-step-07-verify` | tests under `test-automation/` |
| 8 | `@sdlc-step-08-pr` | PR description |

## How to Run the Pipeline

### Option 1: Full Pipeline
In Copilot Chat, invoke `@sdlc` to run all 8 phases with gating between each step.

### Option 2: Individual Steps
Type `/` in Copilot Chat and pick the step prompt:
- **SDLC 01 Requirements**
- **SDLC 02 Architecture**
- **SDLC 03 Design Review**
- **SDLC 04 Implementation Plan**
- **SDLC 05 Implementation**
- **SDLC 06 Review**
- **SDLC 07 Verify**
- **SDLC 08 PR**

### Option 3: Direct Agent Invocation
Use the agent picker to invoke specific step agents directly (e.g., `@sdlc-step-02-architecture`).

## Getting Started

1. **Create a Jira Story** with requirements and acceptance criteria
2. **Populate `user-story.md`** with the story details (or use MCP to fetch from Jira)
3. **Run the pipeline** using `@sdlc` or individual prompts
4. **Review and approve** at each gate

## MCP Servers

This project uses the following MCP servers (configured in `.vscode/mcp.json`):
- **epam-jira** — Fetch Jira ticket details
- **epam-confluence** — Fetch Confluence documentation
- **github** — Create branches and PRs

## Environment Variables

Required environment variables (set in your environment, never commit):
- `EPAM_JIRA_API_TOKEN` — Jira API token
- `EPAM_CONFLUENCE_API_TOKEN` — Confluence API token
- `GITHUB_TOKEN` — GitHub personal access token
