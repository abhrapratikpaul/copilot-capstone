# Implementation Plan

## Pipeline Context

| Artifact | Status | Role |
|----------|--------|------|
| `requirements.md` | Approved | FR/NFR/AC source of truth |
| `architecture.md` | Approved with concerns | Component design, contracts, ADRs |
| `design-review.md` | Verdict: approve_with_concerns (83/100) | DR-1 through DR-7 findings to address during implementation |

## Problem Summary

Build a single-page Task Manager web application with a Python backend (stdlib only) and vanilla HTML/JS frontend. The app allows a user to create, view, complete, delete, and clear-completed tasks. Data is persisted to a local JSON file. No authentication, no external dependencies, runs on `localhost:8080`.

## Key Requirements & Constraints

### Functional Requirements

| ID | Summary | Priority |
|----|---------|----------|
| FR-1 | Display all tasks on page load | P0 |
| FR-2 | Add a task via input field + "Add Task" button | P0 |
| FR-3 | Mark task complete via checkbox (strikethrough) | P0 |
| FR-4 | Delete a task via "Delete" button | P0 |
| FR-5 | Show "Task name is required" on empty input | P0 |
| FR-6 | Sort completed tasks to the bottom | P1 |
| FR-7 | "Clear Completed" removes all completed tasks | P1 |

### Non-Functional Requirements

| ID | Summary | Priority |
|----|---------|----------|
| NFR-1 | Single-page architecture: Python REST API + HTML/JS frontend | P0 |
| NFR-2 | No authentication | P0 |
| NFR-3 | Local data persistence (in-memory + JSON file) | P0 |
| NFR-4 | Immediate UI feedback (no full page reload) | P1 |

### Constraints

- Python code lives only under `dev/`.
- Playwright + TypeScript verification lives only under `test-automation/`.
- Zero external Python dependencies (stdlib only per ADR-001).
- Server binds to `127.0.0.1:8080`.
- Task IDs are UUID4 strings.

## Architecture Summary

Five components in a unidirectional dependency chain:

```
Frontend (static/index.html)
  → API Router (routes.py)
    → Task Service (service.py)
      → Storage Layer (storage.py)

HTTP Server (server.py) binds to localhost, routes /api/* to API Router, serves static files.
```

| Component | File | Responsibility |
|-----------|------|----------------|
| Storage Layer | `dev/src/app/storage.py` | In-memory dict + JSON file read/write |
| Task Service | `dev/src/app/service.py` | Business logic: CRUD, sort, validate |
| API Router | `dev/src/app/routes.py` | HTTP method + path dispatch, JSON parsing, response formatting |
| HTTP Server | `dev/src/app/server.py` | Bind to host:port, route requests, serve static files |
| Frontend | `dev/src/app/static/index.html` | Single HTML page with embedded JS/CSS |

## Design Review Conditions

All findings from `design-review.md` must be addressed during implementation. None are blocking.

| Finding | Severity | Resolution Strategy | Addressed In |
|---------|----------|---------------------|--------------|
| DR-1: PATCH ignores unexpected fields | Major | PATCH handler extracts only `completed` field; silently ignores other fields (tolerant reader) | Step 3 |
| DR-2: Task name max-length inconsistent | Major | Enforce 200-char max in Task Service; return `400 { "error": "Task name exceeds maximum length" }` | Step 2 |
| DR-3: Route conflict `/completed` vs `/{id}` | Minor | Match literal `/completed` before parameterized `/{id}` in route dispatch | Step 3 |
| DR-4: 405 catch-all undocumented | Minor | Add 405 response for unsupported methods on valid paths | Step 3 |
| DR-5: Static file Content-Type not specified | Minor | Use Python `mimetypes` module for Content-Type headers on static files | Step 4 |
| DR-6: Auto-create `data/` directory | Minor | Use `os.makedirs(..., exist_ok=True)` in Storage Layer init | Step 1 |
| DR-7: No graceful shutdown | Minor | Handle `SIGINT` in HTTP Server; complete pending writes before exit | Step 4 |

## Pre-Implementation Baseline

### Existing Files (relevant)

| File | State | Notes |
|------|-------|-------|
| `dev/src/app/__init__.py` | Exists, empty | Will be modified in Step 6 |
| `dev/tests/__init__.py` | Exists, empty | No changes needed |
| `dev/pyproject.toml` | Exists | Has `pytest` in dev dependencies; no changes needed |

### Files to Create

| File | Step |
|------|------|
| `dev/src/app/storage.py` | 1 |
| `dev/src/app/service.py` | 2 |
| `dev/src/app/routes.py` | 3 |
| `dev/src/app/server.py` | 4 |
| `dev/src/app/static/index.html` | 5 |
| `dev/src/app/__main__.py` | 6 |
| `dev/tests/test_storage.py` | 7 |
| `dev/tests/test_service.py` | 8 |
| `dev/tests/test_routes.py` | 9 |

### Files to Modify

| File | Step |
|------|------|
| `dev/src/app/__init__.py` | 6 |

## Implementation Steps

### Wave 0 — No Dependencies

#### Step 1: Storage Layer — `dev/src/app/storage.py` (new)

- **Purpose:** Manage the in-memory task collection (`dict` keyed by task ID) and handle read/write to `dev/src/app/data/tasks.json` for persistence across restarts.
- **Files:** `dev/src/app/storage.py` (new)
- **Dependencies:** None
- **AC/FR Mapping:** FR-1 (data availability), NFR-3 (local persistence)
- **Complexity:** Low
- **DR Findings Addressed:** DR-6 (auto-create `data/` directory via `os.makedirs(..., exist_ok=True)`)
- **Key Behaviors:**
  - On init: attempt to load tasks from `data/tasks.json`; if file missing or empty, start with empty dict.
  - `get_all() → list[dict]` — return all tasks as a list.
  - `get(id: str) → dict | None` — return a single task or None.
  - `save(task: dict) → dict` — upsert a task and flush to JSON file.
  - `remove(id: str) → bool` — delete a task by ID, flush, return True/False.
  - `remove_where(predicate)` — delete tasks matching predicate, flush.
  - Every mutation flushes the entire dict to the JSON file (write-on-every-mutation per ADR-002).
  - JSON file format: `{ "tasks": [ ... ] }`.
- **Verify:**
  ```
  cd dev && python -c "from app.storage import TaskStorage; s = TaskStorage(); print('storage OK')"
  ```

#### Step 2: Task Service — `dev/src/app/service.py` (new)

- **Purpose:** Implement business logic for task CRUD operations, input validation, and sorting.
- **Files:** `dev/src/app/service.py` (new)
- **Dependencies:** None (uses Storage Layer interface, but can be coded independently with same API contract)
- **AC/FR Mapping:** FR-1 (list), FR-2 (create), FR-3 (update), FR-4 (delete), FR-5 (validation), FR-6 (sort), FR-7 (clear completed)
- **Complexity:** Medium
- **DR Findings Addressed:** DR-2 (enforce 200-char max on task name)
- **Key Behaviors:**
  - Constructor accepts a `TaskStorage` instance (dependency injection for testability).
  - `create_task(name: str) → dict` — validate non-empty (after strip), validate ≤200 chars, assign UUID4 ID, `completed=False`, save via storage.
  - `list_tasks() → list[dict]` — get all tasks, sort incomplete first / completed last (FR-6).
  - `update_task(id: str, completed: bool) → dict | None` — update only `completed` field, return updated task or None if not found.
  - `delete_task(id: str) → bool` — remove by ID, return success.
  - `clear_completed() → None` — remove all tasks where `completed=True`.
  - Raise `ValueError` with specific messages for validation failures: `"Task name is required"`, `"Task name exceeds maximum length"`.
- **Verify:**
  ```
  cd dev && python -c "from app.service import TaskService; print('service OK')"
  ```

---

### Wave 1 — Depends on Wave 0

#### Step 3: API Router — `dev/src/app/routes.py` (new)

- **Purpose:** Map HTTP methods and paths to handler functions. Parse JSON request bodies, invoke Task Service methods, and format JSON responses with correct status codes.
- **Files:** `dev/src/app/routes.py` (new)
- **Dependencies:** Step 1 (Storage), Step 2 (Service)
- **AC/FR Mapping:** AC-1 through AC-7 (all endpoints serve the ACs)
- **Complexity:** High
- **DR Findings Addressed:** DR-1 (PATCH extracts only `completed` field), DR-3 (literal `/completed` before `/{id}`), DR-4 (405 catch-all)
- **Endpoints:**

  | Method | Path | Handler | Success | Errors |
  |--------|------|---------|---------|--------|
  | GET | `/api/tasks` | `list_tasks` | 200 `[tasks]` | — |
  | POST | `/api/tasks` | `create_task` | 201 `{task}` | 400 (empty name, max length, invalid JSON) |
  | PATCH | `/api/tasks/{id}` | `update_task` | 200 `{task}` | 404, 400 |
  | DELETE | `/api/tasks/{id}` | `delete_task` | 204 | 404 |
  | DELETE | `/api/tasks/completed` | `clear_completed` | 204 | — |

- **Key Behaviors:**
  - Route matching: check path segments in order — literal `/api/tasks/completed` (DELETE) before `/api/tasks/{id}` (PATCH, DELETE).
  - PATCH: parse JSON body, extract only `completed` field, ignore all other fields (DR-1, tolerant reader).
  - POST: validate `Content-Type: application/json`; parse body; delegate validation to service.
  - Return 405 `{ "error": "Method not allowed" }` for unsupported methods on valid paths (DR-4).
  - Return 400 `{ "error": "Invalid JSON" }` for malformed request bodies.
  - All responses set `Content-Type: application/json`.
  - Provide a `handle_request(method, path, headers, body) → (status, headers, body)` function that the HTTP Server calls.
- **Verify:**
  ```
  cd dev && python -c "from app.routes import route_request; print('routes OK')"
  ```

#### Step 4: HTTP Server — `dev/src/app/server.py` (new)

- **Purpose:** Start a Python stdlib HTTP server on `127.0.0.1:8080`. Route `/api/*` requests to the API Router. Serve static files from `dev/src/app/static/` for all other paths. Handle graceful shutdown.
- **Files:** `dev/src/app/server.py` (new)
- **Dependencies:** Step 3 (Routes)
- **AC/FR Mapping:** NFR-1 (single-page architecture), all ACs (server is the runtime host)
- **Complexity:** Medium
- **DR Findings Addressed:** DR-5 (use `mimetypes` module for static file Content-Type), DR-7 (graceful SIGINT handling)
- **Key Behaviors:**
  - Subclass `http.server.BaseHTTPRequestHandler`.
  - Override `do_GET`, `do_POST`, `do_PATCH`, `do_DELETE` to delegate to the API router for `/api/*` paths.
  - For non-API paths: serve files from `static/` directory. Map `/` to `/index.html`. Use `mimetypes.guess_type()` for Content-Type headers (DR-5).
  - Reject paths containing `..` to prevent path traversal (security requirement from architecture).
  - Bind to `127.0.0.1:8080` (localhost only, per security considerations).
  - Register `signal.SIGINT` handler for graceful shutdown (DR-7): set a shutdown flag, let current request complete, then exit.
  - Suppress default stderr logging of each request (optional, for cleaner output).
- **Verify:**
  ```
  cd dev && python -c "from app.server import TaskHTTPServer; print('server OK')"
  ```

---

### Wave 2 — Depends on Wave 1

#### Step 5: Frontend — `dev/src/app/static/index.html` (new)

- **Purpose:** Single HTML page with embedded CSS and JavaScript that provides the user interface for all task operations. Communicates with the backend exclusively via `fetch()` calls to the REST API.
- **Files:** `dev/src/app/static/index.html` (new)
- **Dependencies:** Step 3 (Routes — API must exist), Step 4 (Server — must serve the file)
- **AC/FR Mapping:** AC-1 (FR-1), AC-2 (FR-2), AC-3 (FR-3), AC-4 (FR-4), AC-5 (FR-5), AC-6 (FR-6), AC-7 (FR-7), NFR-4 (immediate feedback)
- **Complexity:** High
- **DR Findings Addressed:** None directly (frontend consumes the API contract)
- **Key Behaviors:**
  - **Task list display (FR-1, FR-6):** On page load, `GET /api/tasks` and render the list. Completed tasks rendered with `text-decoration: line-through`. List is already sorted by the backend.
  - **Add task form (FR-2, FR-5):** Input field + "Add Task" button. Client-side validation: if input is empty, display `"Task name is required"` error message without calling the API (ADR-004). On valid input, `POST /api/tasks`, then re-fetch and re-render the list.
  - **Checkbox toggle (FR-3):** Each task has a checkbox. On change, `PATCH /api/tasks/{id}` with `{ "completed": true/false }`. Re-fetch and re-render list to maintain sort order.
  - **Delete button (FR-4):** Each task has a "Delete" button. On click, `DELETE /api/tasks/{id}`. Remove task from DOM.
  - **Clear completed button (FR-7):** A "Clear Completed" button. On click, `DELETE /api/tasks/completed`. Re-fetch and re-render list.
  - **Error display:** A visible element for showing error messages (validation errors, API errors).
  - **No full page reloads (NFR-4):** All operations use `fetch()` and DOM manipulation.
- **Verify:**
  ```
  cd dev && python -c "import os; assert os.path.isfile('src/app/static/index.html'); print('frontend OK')"
  ```

#### Step 6: App Wiring — `dev/src/app/__init__.py` (modify) + `dev/src/app/__main__.py` (new)

- **Purpose:** Provide the application entry point. Wire Storage → Service → Routes → Server. Enable `python -m app` execution.
- **Files:** `dev/src/app/__init__.py` (modify), `dev/src/app/__main__.py` (new)
- **Dependencies:** Step 1 (Storage), Step 2 (Service), Step 3 (Routes), Step 4 (Server)
- **AC/FR Mapping:** All ACs (entry point enables the entire application)
- **Complexity:** Low
- **DR Findings Addressed:** None
- **Key Behaviors:**
  - `__init__.py`: Define a `main()` function that instantiates Storage, Service, passes them to the Router, starts the Server on `127.0.0.1:8080`, and prints the URL to stdout.
  - `__main__.py`: Call `from app import main; main()` to support `python -m app`.
  - The wiring order: `TaskStorage() → TaskService(storage) → configure routes(service) → start server`.
- **Verify:**
  ```
  cd dev && python -c "from app import main; print('wiring OK')"
  ```
  Full integration test (manual):
  ```
  cd dev/src && python -m app
  # Visit http://127.0.0.1:8080 in browser, verify page loads
  # Ctrl+C to stop
  ```

---

### Wave 3 — Depends on Wave 2

#### Step 7: Unit Tests — Storage — `dev/tests/test_storage.py` (new)

- **Purpose:** Verify Storage Layer CRUD operations, JSON file persistence, and edge cases.
- **Files:** `dev/tests/test_storage.py` (new)
- **Dependencies:** Step 1 (Storage)
- **AC/FR Mapping:** NFR-3 (persistence correctness)
- **Complexity:** Low
- **DR Findings Addressed:** DR-6 (test that `data/` directory is auto-created)
- **Test Cases:**
  - Save a task → `get_all()` returns it.
  - Save multiple tasks → `get_all()` returns all.
  - `get(id)` returns correct task; `get(nonexistent)` returns None.
  - `remove(id)` deletes the task; `remove(nonexistent)` returns False.
  - `remove_where(predicate)` removes matching tasks only.
  - After save, JSON file exists and contains correct data.
  - New `TaskStorage` instance loads tasks from existing JSON file (persistence across restarts).
  - Empty or missing JSON file → starts with empty dict (no crash).
  - Auto-creation of `data/` directory when it does not exist (DR-6).
- **Verify:**
  ```
  cd dev && python -m pytest tests/test_storage.py -v
  ```

#### Step 8: Unit Tests — Service — `dev/tests/test_service.py` (new)

- **Purpose:** Verify Task Service business logic, validation rules, sorting, and edge cases.
- **Files:** `dev/tests/test_service.py` (new)
- **Dependencies:** Step 2 (Service), Step 1 (Storage)
- **AC/FR Mapping:** AC-2 (FR-2), AC-3 (FR-3), AC-5 (FR-5), AC-6 (FR-6), AC-7 (FR-7)
- **Complexity:** Medium
- **DR Findings Addressed:** DR-2 (test 200-char max enforcement)
- **Test Cases:**
  - `create_task("Buy milk")` → returns task with UUID id, name, `completed=False`.
  - `create_task("")` → raises ValueError `"Task name is required"`.
  - `create_task("   ")` → raises ValueError `"Task name is required"` (whitespace-only).
  - `create_task("x" * 201)` → raises ValueError `"Task name exceeds maximum length"` (DR-2).
  - `create_task("x" * 200)` → succeeds (boundary).
  - `create_task("  Buy milk  ")` → name is trimmed to `"Buy milk"`.
  - `list_tasks()` → returns tasks sorted incomplete-first, completed-last (FR-6).
  - `update_task(id, completed=True)` → task is marked completed.
  - `update_task(nonexistent, completed=True)` → returns None.
  - `delete_task(id)` → task is removed.
  - `delete_task(nonexistent)` → returns False.
  - `clear_completed()` → removes only completed tasks; incomplete tasks remain.
  - `clear_completed()` with no completed tasks → no-op, no error.
- **Verify:**
  ```
  cd dev && python -m pytest tests/test_service.py -v
  ```

#### Step 9: Unit Tests — Routes — `dev/tests/test_routes.py` (new)

- **Purpose:** Verify API Router returns correct HTTP status codes, response bodies, and error handling for all endpoints.
- **Files:** `dev/tests/test_routes.py` (new)
- **Dependencies:** Step 3 (Routes), Step 2 (Service), Step 1 (Storage)
- **AC/FR Mapping:** AC-1 through AC-7 (all endpoints)
- **Complexity:** Medium
- **DR Findings Addressed:** DR-1 (PATCH ignores extra fields), DR-3 (route order), DR-4 (405 response)
- **Test Cases:**
  - `GET /api/tasks` → 200, returns JSON array.
  - `POST /api/tasks` with valid name → 201, returns task JSON.
  - `POST /api/tasks` with empty name → 400, `{ "error": "Task name is required" }`.
  - `POST /api/tasks` with name > 200 chars → 400, `{ "error": "Task name exceeds maximum length" }`.
  - `POST /api/tasks` with malformed JSON → 400, `{ "error": "Invalid JSON" }`.
  - `PATCH /api/tasks/{id}` with `{ "completed": true }` → 200, returns updated task.
  - `PATCH /api/tasks/{id}` with `{ "completed": true, "name": "hacked" }` → 200, name is unchanged (DR-1).
  - `PATCH /api/tasks/{nonexistent}` → 404, `{ "error": "Task not found" }`.
  - `DELETE /api/tasks/{id}` → 204, no body.
  - `DELETE /api/tasks/{nonexistent}` → 404.
  - `DELETE /api/tasks/completed` → 204 (DR-3: correct route, not treated as ID).
  - `PUT /api/tasks` → 405, `{ "error": "Method not allowed" }` (DR-4).
  - Responses have `Content-Type: application/json` (except 204).
- **Verify:**
  ```
  cd dev && python -m pytest tests/test_routes.py -v
  ```

---

## Wave Plan

| Wave | Steps | Dependencies | Parallelizable |
|------|-------|--------------|----------------|
| 0 | Step 1 (Storage), Step 2 (Service) | None | Yes — independent |
| 1 | Step 3 (Routes), Step 4 (Server) | Wave 0 | Partially — Step 4 depends on Step 3 |
| 2 | Step 5 (Frontend), Step 6 (Wiring) | Wave 1 | Partially — Step 6 depends on Step 5 |
| 3 | Step 7 (Tests: Storage), Step 8 (Tests: Service), Step 9 (Tests: Routes) | Wave 2 | Yes — all three independent |

**Total:** 9 steps (8 new files, 1 modified file) across 4 waves.

## Risks

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| R-1 | Manual HTTP routing errors (ADR-001) | Broken endpoints | Medium | Comprehensive route tests (Step 9); match literal paths before parameterized paths (DR-3) |
| R-2 | JSON file corruption on crash during write | Lost task data | Low | Write-on-every-mutation is atomic enough for single-user; graceful SIGINT handler (DR-7) |
| R-3 | Route conflict: `/api/tasks/completed` vs `/api/tasks/{id}` | Wrong handler invoked | Low | Explicit literal match before parameterized match in route dispatch (DR-3); dedicated test case (Step 9) |
| R-4 | Frontend fetch errors silently swallowed | User sees stale data | Low | Frontend error display element; re-fetch list after every mutation |
| R-5 | Static file path traversal | Unauthorized file access | Low | Reject paths containing `..`; restrict serving to `static/` directory |

## Non-Functional Hardening Tasks

| NFR | How Addressed | Step |
|-----|---------------|------|
| NFR-1 (Single-page architecture) | Python stdlib HTTP server serves API + static files from single process | Step 4, Step 5 |
| NFR-2 (No authentication) | No auth code implemented; no secrets in codebase | All steps (by omission) |
| NFR-3 (Local data persistence) | In-memory dict + JSON file persistence; auto-create `data/` dir | Step 1 |
| NFR-4 (Immediate UI feedback) | Frontend uses `fetch()` + DOM manipulation; no page reloads | Step 5 |
| Security: localhost binding | Server binds to `127.0.0.1`, not `0.0.0.0` | Step 4 |
| Security: input validation | Client-side + server-side validation (ADR-004); 200-char max (DR-2) | Step 2, Step 3, Step 5 |
| Security: Content-Type enforcement | API checks `Content-Type: application/json` on request bodies | Step 3 |
| Security: path traversal prevention | Static file handler rejects `..` in paths | Step 4 |

## Post-Implementation Checklist

- [ ] All 9 steps completed (8 new files, 1 modified file)
- [ ] `cd dev/src && python -m app` starts server on `http://127.0.0.1:8080`
- [ ] All 7 ACs manually verifiable in browser
- [ ] `cd dev && python -m pytest tests/ -v` — all unit tests pass
- [ ] DR-1 addressed: PATCH ignores unexpected fields
- [ ] DR-2 addressed: 200-char max enforced, tested
- [ ] DR-3 addressed: literal `/completed` matched before `/{id}`
- [ ] DR-4 addressed: 405 returned for unsupported methods
- [ ] DR-5 addressed: static files served with correct Content-Type
- [ ] DR-6 addressed: `data/` directory auto-created
- [ ] DR-7 addressed: SIGINT graceful shutdown
- [ ] No external Python dependencies added (stdlib only)
- [ ] No secrets in codebase
- [ ] No Python tooling/config in `test-automation/`
- [ ] No TS tooling/config in `dev/`

## Pipeline Continuation

After implementation (Step 05) is complete:

1. **Review (Step 06):** Run structured self-review checklist against implementation — correctness, security, error handling, tests, clarity, DRY, dependency safety.
2. **Verify (Step 07):** Add/run Playwright + TypeScript E2E tests under `test-automation/tests/` covering all 7 ACs. Run `docs-quality.spec.ts` to validate document structure.
3. **PR (Step 08):** Create feature branch, open PR via GitHub MCP with description, change list, test evidence, and reviewer checklist.
