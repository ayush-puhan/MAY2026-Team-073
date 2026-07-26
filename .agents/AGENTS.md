# ClubConnect Architecture Rules

## General Development Rules
- **Dual-Implementation API Strategy**: Ensure strict parity between `backendApis` and `mockbackendApis` for all endpoints.
- **Naming Conventions**: Use `PascalCase` for React components/folders (e.g., `GlobalCalendar`) and `camelCase` for API files/folders.
- **Modular UI & Scoped CSS**: Use CSS modules with locally scoped media queries.
- **Strict Icon Registry Adherence**: NO hardcoded icons (like `"mdi:calendar-star"` or `"mdi:menu"`). All icons must be added to and imported from `src/assets/icons/registry.js`.

## Database & Mock Data Handling
- **ALWAYS inspect backend ORM models first:** Before creating, modifying, or relying on any frontend mock data (`db.json`) or API simulation logic, you MUST inspect the canonical SQLAlchemy models located in `Application\backend\app\database\models` and `Application\backend\app\database\enums.py`.
- **Maintain 1:1 Parity:** The frontend mock database must strictly adhere to the exact schema defined by the backend. Do not invent arbitrary attributes, omit required constraints, or flatten relationships that the backend normalizes.
- **Client-Side Joins:** `json-server` does not natively handle complex SQL joins. When mocking endpoints that return nested data (like an `Event` with its `Club`, `University`, and `Interests`), you must implement a Mock API layer (`src/api/mockbackendApis/`) that fetches the normalized tables and performs the in-memory joins before returning the payload to the UI components. Do not embed nested structures directly into `db.json`.
