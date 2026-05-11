# Requirements

**Source:** [EPMCDMETST-41952](https://jiraeu.epam.com/browse/EPMCDMETST-41952) / [user-story.md](user-story.md)

## Scope

A single-page Task Manager web application with a Python backend and HTML/JS frontend that allows a user to create, view, complete, and delete tasks. Data is persisted via local file or in-memory storage. No authentication is required.

## Functional Requirements

- **FR-1 (P0): Display Tasks** — The application shall display all existing tasks in a list when the page loads.
- **FR-2 (P0): Add Task** — The application shall allow the user to enter a task name in an input field and save it by clicking an "Add Task" button; the new task shall appear in the task list.
- **FR-3 (P0): Mark Task Complete** — The application shall allow the user to mark a task as complete by clicking a checkbox next to it; completed tasks shall be rendered with strikethrough styling.
- **FR-4 (P0): Delete Task** — The application shall allow the user to remove a task from the list by clicking a "Delete" button associated with that task.
- **FR-5 (P0): Empty Input Validation** — The application shall display the error message "Task name is required" when the user clicks "Add Task" while the task input field is empty.
- **FR-6 (P1): Completed Task Sorting** — The application shall display completed tasks at the bottom of the task list.
- **FR-7 (P1): Clear Completed** — The application shall provide a "Clear Completed" button that removes all completed tasks from the list in a single action.

## Non-Functional Requirements

- **NFR-1 (P0): Single-Page Architecture** — The application shall be implemented as a single-page web application with a Python backend serving a REST API and an HTML/JS frontend.
- **NFR-2 (P0): No Authentication** — The application shall not require user authentication or authorization.
- **NFR-3 (P0): Local Data Persistence** — The application shall persist task data using local file storage or in-memory storage; no external database shall be required.
- **NFR-4 (P1): Immediate UI Feedback** — The UI shall provide immediate visual feedback when the user adds, completes, or deletes a task without requiring a full page reload.

## Assumptions

- **A-1:** The application is single-user; concurrent access handling is not required.
- **A-2:** The Python backend serves both the API endpoints and the static frontend files.
- **A-3:** Each task has at minimum a name (string) and a completion status (boolean).
- **A-4:** The application runs locally on `localhost`.
- **A-5:** If file-based storage is used, the file is co-located with the application and does not require user-configurable paths.

## Out of Scope

- **OOS-1:** User authentication and authorization.
- **OOS-2:** Multi-user or collaborative features.
- **OOS-3:** External database integration (e.g., PostgreSQL, MySQL, SQLite on a remote server).
- **OOS-4:** Task editing (renaming a task after creation).
- **OOS-5:** Task metadata beyond name and completion status (e.g., due dates, priorities, categories).
- **OOS-6:** Deployment to production hosting or containerization.

## Acceptance Criteria

- **AC-1 → FR-1:** Given the task page is open, when the page loads, then existing tasks are displayed in a list.
- **AC-2 → FR-2:** Given the task input field is visible, when the user enters a task name and clicks "Add Task", then the task is saved and appears in the list.
- **AC-3 → FR-3:** Given a task exists, when the user clicks the checkbox next to it, then the task is marked as complete with strikethrough styling.
- **AC-4 → FR-4:** Given a task exists, when the user clicks the "Delete" button, then the task is removed from the list.
- **AC-5 → FR-5:** Given the task input is empty, when the user clicks "Add Task", then an error message displays stating "Task name is required".
- **AC-6 → FR-6:** Given tasks exist, when the page loads, then completed tasks appear at the bottom of the list.
- **AC-7 → FR-7:** Given tasks exist, when the user clicks "Clear Completed", then all completed tasks are removed.

## Traceability Matrix

| AC   | FR   | User Story AC       | Priority |
|------|------|----------------------|----------|
| AC-1 | FR-1 | Primary AC #1        | P0       |
| AC-2 | FR-2 | Primary AC #2        | P0       |
| AC-3 | FR-3 | Primary AC #3        | P0       |
| AC-4 | FR-4 | Primary AC #4        | P0       |
| AC-5 | FR-5 | Primary AC #5        | P0       |
| AC-6 | FR-6 | Additional AC #1     | P1       |
| AC-7 | FR-7 | Additional AC #2     | P1       |

## Open Questions

- None.
