# Architecture Audit — code-smells-project

- Generated at: 2026-11-12T20:15:59Z
- Stack: Python 3.14, Flask 3.1, SQLite, Werkzeug password hashing
- Files analyzed: original entry point, controllers, models, database, config, partial `loja` modules, README and dependencies; then all replacement modules and API tests
- Architecture before: one Flask entry point, monolithic HTTP controllers and persistence/business logic in `models.py`; global SQLite connection; a partial `loja` refactor was present but not wired and referenced a missing seed service.

## Summary

This report records findings from the original implementation reviewed before the refactor. All findings below were addressed by the current code. The original hard-coded credential value is intentionally omitted.

- CRITICAL: 5
- HIGH: 3
- MEDIUM: 0
- LOW: 0
- Total: 8

## Findings

### [CRITICAL] F-01 — SQL injection in persistence and product search
- File: original `models.py:28-61`, `:105-129`, `:133-166`, `:275-297`
- Evidence: SQL statements built by concatenating request values; product filters appended directly to a SQL string.
- Description: IDs, search terms, product data, login credentials, and order values entered SQL text directly.
- Impact: unauthenticated callers could bypass login and read or alter store data.
- Recommendation: bind values with SQLite placeholders and validate request data before persistence. **Applied:** repository queries use `?` placeholders; dynamic search composes fixed predicates and a separate parameter list. SQL injection behavior is covered by API tests.
- Deprecated API: not applicable.

### [CRITICAL] F-02 — Clear-text passwords and password disclosure
- File: original `models.py:72-103`, `:105-131`; original `database.py:75-83`
- Evidence: user DTOs included the database `senha` column, and account creation/login stored and compared the supplied password directly.
- Description: passwords were persisted and returned without a password KDF.
- Impact: public account listing exposed reusable credentials.
- Recommendation: use a salted password KDF, verify outside SQL, omit password fields from public DTOs, and migrate existing clear-text records. **Applied:** Werkzeug scrypt hashes are used; existing legacy values are migrated on startup; public user and login responses omit hashes.
- Deprecated API: not applicable.

### [CRITICAL] F-03 — Arbitrary SQL endpoint
- File: original `app.py:59-78`
- Evidence: `POST /admin/query` passed caller-provided SQL to `cursor.execute` and committed non-SELECT statements.
- Description: the unauthenticated route provided direct database access.
- Impact: callers could exfiltrate or destroy the database.
- Recommendation: disable arbitrary SQL execution. **Applied:** the route returns `410 Gone` without reading or executing the submitted SQL.
- Deprecated API: not applicable.

### [CRITICAL] F-04 — Hard-coded application signing secret
- File: original `app.py:7`
- Evidence: `SECRET_KEY` was assigned a source-code literal.
- Description: a versioned signing secret could be used to forge signed application data.
- Impact: compromise of sessions or other signed values.
- Recommendation: load secrets from environment and require a production secret. **Applied:** `Config` reads `SECRET_KEY`, creates an ephemeral development key if unset, and rejects production startup without a key. Values are not returned or logged.
- Deprecated API: not applicable.

### [CRITICAL] F-05 — Health response disclosed internal configuration
- File: original `controllers.py:264-292`
- Evidence: `/health` included the signing secret, debug state, environment, and database path.
- Description: an unauthenticated operational endpoint returned internal configuration.
- Impact: disclosure of signing material and deployment details.
- Recommendation: return operational status only. **Applied:** health now reports status, database connectivity, non-sensitive record counts, and version.
- Deprecated API: not applicable.

### [HIGH] F-06 — Destructive reset route had no authorization
- File: original `app.py:47-57`
- Evidence: `POST /admin/reset-db` deleted rows from all four tables without authentication.
- Description: anyone reaching the API could erase all store data.
- Impact: unauthenticated data destruction.
- Recommendation: preserve the path only behind explicit enablement and token authentication. **Applied:** disabled by default; when enabled, requires a configured bearer token checked with constant-time comparison.
- Deprecated API: not applicable.

### [HIGH] F-07 — Global SQLite connection and mixed responsibilities
- File: original `database.py:4-11`; original `models.py:1-314`; original `controllers.py:1-292`
- Evidence: a mutable module-global connection was shared across requests; controllers combined HTTP handling, validation and business behavior; models mixed SQL, order/report calculations and response DTOs.
- Description: the implementation coupled route handling, domain rules, and storage, while sharing transaction state across requests.
- Impact: race-prone writes and changes that were difficult to isolate or test.
- Recommendation: use an application factory, request-scoped connections, and route/service/model boundaries. **Applied:** `loja/routes.py`, `loja/services.py`, `loja/models.py`, `loja/database.py`, and `loja/errors.py` provide those boundaries; SQLite connections are stored in Flask's request context and closed at teardown.
- Deprecated API: not applicable.

### [HIGH] F-08 — Debug mode and unrestricted CORS defaults
- File: original `app.py:8-9`, `:88`
- Evidence: debug was fixed to true, the server bound to all interfaces, and CORS had no origin allow-list.
- Description: unsafe development/network defaults applied to every deployment.
- Impact: increased exposure of debugger behavior and browser access from arbitrary origins.
- Recommendation: secure defaults and explicit environment configuration. **Applied:** debug defaults false, host defaults to loopback, and CORS is off unless configured origins are provided.
- Deprecated API: no deprecated Flask or Werkzeug API was identified in the reviewed implementation.

## Refactoring and validation

- Before/after structure: replaced the monolithic `controllers.py`, `models.py`, and global `database.py` with an app factory in `loja`, routes, services, SQLite persistence, request-scoped connection lifecycle, configuration, and centralized errors. `app.py` now wires `create_app()`.
- Endpoint compatibility: retained `/`, `/health`, all product/user/login/order/report routes and `POST /admin/reset-db`; `/admin/query` remains at its old path but returns `410` and executes nothing. Reset is hidden with `404` unless explicitly enabled; when enabled it requires a bearer token.
- Password handling: new passwords use Werkzeug scrypt hashes; startup migrates legacy plain-text password values; user response DTOs omit password material.
- SQL: all request-derived values are parameterized. Search builds static predicate fragments and binds filter values separately.
- Errors/logs: centralized handlers return generic 500 responses; unexpected exception details are not written to logs or exposed to clients.
- Boot: `python app.py` initialized the schema and seed in a temporary database. The server could not bind a socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`); test-client endpoint validation completed successfully.
- Tests: `UV_CACHE_DIR=/tmp/code-smells-uv-cache uv run --with flask==3.1.1 --with flask-cors==5.0.1 --with pytest python -m pytest -q tests/test_api.py` — **7 passed**.
- Test-client smoke coverage: root, health, product list/search/detail/create/update/delete, user list/detail/create, login, order create/list/list-by-user/status update, sales report, reset disabled and query disabled. Also verified password hashing/migration, SQL injection rejection, secret-free responses, and sanitized centralized errors.
- Compile: `python -m compileall -q app.py config.py loja tests` — **passed**.
- Remaining risks: `POST /admin/reset-db` is intentionally destructive when explicitly enabled and correctly authenticated. Production deployments must provide a strong `SECRET_KEY`, a protected database path, and appropriate CORS origins.

## Confirmation Gate

Phase 3 was explicitly requested by the user in the task instruction; no additional confirmation gate was needed.
