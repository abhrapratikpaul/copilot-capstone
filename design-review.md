# Design Review

## Meta
- **Date:** 2025-05-11
- **Verdict:** approve_with_concerns
- **Overall Score:** 83/100
- **Ready for Implementation:** yes

## Summary

The architecture in [architecture.md](architecture.md) is well-structured, clearly documented, and covers all functional and non-functional requirements from [requirements.md](requirements.md). The layered component design (HTTP Server → API Router → Task Service → Storage Layer) follows SRP, and the four ADRs provide sound justification with documented alternatives and consequences. Two major concerns exist: (1) the PATCH endpoint contract does not specify handling of unexpected request body fields, and (2) the task name max-length constraint mentioned in the Security section is absent from the API contract and data model. Neither concern is blocking, but both should be resolved before or during implementation.

## Requirements Coverage

| Requirement | Architectural Home | Covered? |
|---|---|---|
| FR-1 (Display Tasks) | GET /api/tasks + Frontend rendering | Yes |
| FR-2 (Add Task) | POST /api/tasks + Frontend form + DOM append | Yes |
| FR-3 (Mark Complete) | PATCH /api/tasks/{id} + checkbox toggle + strikethrough | Yes |
| FR-4 (Delete Task) | DELETE /api/tasks/{id} + DOM removal | Yes |
| FR-5 (Empty Input Validation) | ADR-004 (client + server), POST 400 response | Yes |
| FR-6 (Completed Task Sorting) | Task Service sort logic (incomplete first) | Yes |
| FR-7 (Clear Completed) | DELETE /api/tasks/completed + DOM removal | Yes |
| NFR-1 (Single-Page Architecture) | G-1; Python http.server + vanilla HTML/JS | Yes |
| NFR-2 (No Authentication) | G-2; explicitly excluded | Yes |
| NFR-3 (Local Data Persistence) | G-3; ADR-002 (in-memory dict + JSON file) | Yes |
| NFR-4 (Immediate UI Feedback) | G-4; DOM manipulation without page reload | Yes |

All 7 ACs map 1:1 to FRs, and each FR has a clear architectural component and data flow. No requirement is orphaned.

## Architectural Soundness

- **SRP:** Each of the five components has a single, well-defined responsibility. The Task Service owns business logic; the Storage Layer owns persistence; the API Router owns HTTP dispatch. Clean separation.
- **Data flow:** Five Mermaid sequence diagrams trace every user action from Browser → API → Service → Storage and back. This is thorough and aids implementation.
- **Layering:** The dependency chain (Frontend → API Router → Task Service → Storage Layer) is unidirectional. No circular dependencies.
- **Testability:** Each layer is independently testable. The testing strategy explicitly covers unit tests for Service and Storage, integration tests for API Router, and E2E tests for all ACs.

## Assumption Challenges

- **A-1 (Single-user):** Reasonable for scope, but the architecture does not mention behavior if two browser tabs are opened simultaneously. Since both tabs share the same in-memory state via the server, this is inherently safe for reads, and write conflicts are unlikely for a single human user. Acceptable.
- **A-5 (File co-located):** The architecture specifies `dev/src/app/data/tasks.json` and states the file is "created automatically if absent." This implicitly requires the server to create the `data/` directory as well. The architecture should clarify whether the directory is also auto-created (see DR-6).
- **"completed" as a URL segment (R-3):** The architecture assumes no task ID will equal the string `"completed"`. Since IDs are UUID4 (36-character hex-dash strings), this is safe—but worth noting the assumption.

## Complexity Concerns

- **Manual HTTP routing (ADR-001):** This is the primary source of accidental complexity. The architecture acknowledges the trade-off and mitigates via comprehensive testing (R-2). The decision is defensible given the zero-dependency goal.
- **Write-on-every-mutation:** Simple and correct for single-user. No unnecessary caching, batching, or transaction layers. Appropriately minimal.
- **Dual validation (ADR-004):** Slightly more code, but the duplication is a single rule ("name required") and the defense-in-depth benefit is worth it.

## Alternative Approaches

All four ADRs document alternatives with pros/cons:
- ADR-001: Flask and FastAPI considered. Rationale for rejection is sound.
- ADR-002: Pure in-memory and SQLite considered. JSON file is the right middle ground.
- ADR-003: React/Vue via CDN considered. Vanilla JS avoids build tooling in `dev/`.
- ADR-004: Client-only and server-only considered. Both-sides approach is correct.

No major alternative was overlooked.

## Missing Considerations

See findings DR-5, DR-6, and DR-7 below.

## Design Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | 88/100 | Excellent structure, Mermaid diagrams, explicit contracts. Minor gaps in edge-case specification. |
| Completeness | 78/100 | All FRs/NFRs covered. Gaps in PATCH validation rules, max-length constraint in contract, 405 documentation. |
| Soundness | 82/100 | Clean layering, well-reasoned ADRs, dual validation. Route conflict mitigation is directionally correct but thin. |
| Simplicity | 90/100 | Appropriately minimal. No over-engineering. Manual routing is the only accidental complexity, and it's acknowledged. |
| Scalability | 75/100 | Single-user design fits requirements. Bottlenecks identified in R-4. No unnecessary scaling provisions. |
| Maintainability | 82/100 | High cohesion, low coupling. Clear component boundaries. JSON file is debuggable. Minor boilerplate concern with manual routing. |
| **Overall** | **83/100** | Rounded average of dimension scores. |

## Findings

### Critical

None.

### Major

- **DR-1:** PATCH endpoint does not specify handling of unexpected request body fields.
  - Severity: major
  - Risk: If the implementation silently accepts arbitrary fields (e.g., `{ "completed": true, "name": "hacked" }`), it could allow unintended task mutations. If it ignores them silently, the API contract is ambiguous. If it rejects them, the error response is undefined.
  - Recommendation: Specify in the PATCH contract that only the `completed` field is accepted. State whether extra fields are silently ignored or result in a `400` error. Prefer ignoring unknown fields (tolerant reader pattern) for simplicity, but document the choice.

- **DR-2:** Task name max-length constraint is inconsistent across sections.
  - Severity: major
  - Risk: The Security section mentions "reasonable max length (e.g., 200 characters)" using hedging language ("e.g."). The API contract's POST endpoint and the Data Model section do not mention any length constraint. Implementers may omit the check entirely, or choose inconsistent limits.
  - Recommendation: Commit to a specific max length (e.g., 200 characters) in the Data Model definition and add a corresponding `400` error response to the POST contract: `{ "error": "Task name exceeds maximum length" }`.

### Minor

- **DR-3:** R-3 route conflict mitigation lacks routing pattern detail.
  - Severity: minor
  - Risk: The mitigation states the router "checks for the literal `completed` segment before treating the segment as an ID" but does not specify the routing mechanism (ordered route table, explicit string match, regex). An implementer could still get the order wrong.
  - Recommendation: Specify that routes are matched in declaration order, with the literal `/api/tasks/completed` route registered before the parameterized `/api/tasks/{id}` route. Alternatively, state that the router checks `segment == "completed"` before attempting UUID parsing.

- **DR-4:** 405 Method Not Allowed not documented in individual endpoint contracts.
  - Severity: minor
  - Risk: The error handling table includes 405, but no endpoint contract references it. An implementer might not implement the catch-all 405 handler.
  - Recommendation: Add a note at the API contract level: "Any request with an unsupported HTTP method for a valid path returns `405 { "error": "Method not allowed" }`."

- **DR-5:** Static file Content-Type headers not specified.
  - Severity: minor
  - Risk: If the server serves `index.html` without `Content-Type: text/html`, browsers may not render it correctly. Python's `http.server` uses the `mimetypes` module by default, but this implicit behavior is not documented.
  - Recommendation: Note that the server uses Python's `mimetypes` module (or equivalent) to set `Content-Type` headers for static files.

- **DR-6:** Auto-creation of data directory not explicit.
  - Severity: minor
  - Risk: If `dev/src/app/data/` does not exist, the server could crash on first write to `tasks.json`. The architecture says the file is "created automatically if absent" but does not mention the directory.
  - Recommendation: State that the Storage Layer creates the `data/` directory (e.g., via `os.makedirs(..., exist_ok=True)`) if it does not exist.

- **DR-7:** No graceful shutdown handling documented.
  - Severity: minor
  - Risk: If the server is killed mid-write to the JSON file, the file could be corrupted. For single-user localhost this is very low risk but worth noting.
  - Recommendation: Mention that the server handles `SIGINT` (Ctrl+C) gracefully, completing any pending JSON write before exiting.

## Positive Aspects

- **Thorough data flow documentation:** Five Mermaid sequence diagrams cover every user-facing operation. This level of detail will directly accelerate implementation.
- **Well-structured ADRs:** All four ADRs follow a consistent format (Context → Decision → Alternatives → Consequences) with genuine alternatives considered. No rubber-stamping.
- **Defense-in-depth validation (ADR-004):** Client-side + server-side validation is the correct approach, and the ADR justifies it well.
- **Explicit security section:** Localhost binding, path traversal prevention, Content-Type enforcement, and input validation are all called out—unusual thoroughness for a small project.
- **Complete traceability:** Every FR maps to a component, data flow, and test. Every AC maps to a Playwright test. No orphaned requirements.
- **Risk register:** Four risks with impact/likelihood/mitigation. R-3 (route conflict) is a genuine concern that was proactively identified.
- **Appropriate simplicity:** The architecture resists over-engineering. No unnecessary caching, middleware, or abstraction layers.

## Blocking Issues

None. All findings are major or minor; none are critical or blocking.

## Recommended Actions

- [SUGGESTED] Specify PATCH request body validation behavior in the API contract (DR-1).
- [SUGGESTED] Commit to a specific task name max length in the Data Model and POST contract (DR-2).
- [SUGGESTED] Clarify route evaluation order for the DELETE conflict (DR-3).
- [SUGGESTED] Add a catch-all 405 note to the API contract section (DR-4).
- [SUGGESTED] Document static file Content-Type handling (DR-5).
- [SUGGESTED] Specify auto-creation of the `data/` directory (DR-6).

## Sign-Off

- **overall_assessment:** approve_with_concerns
- **ready_for_implementation:** true
- **blocking_issues:** []
- **confidence_score:** 88/100
- **estimated_refinement_time:** 1–2 hours (to address DR-1 through DR-6 in architecture.md)
- **next_review_needed:** no
