# Architecture Audit — task-manager-api

- Generated at: 2026-11-12T20:38:28Z
- Stack: Python 3.14, Flask 3.0, Flask-SQLAlchemy 3.1, SQLite; dependencies declared in `task-manager-api/requirements.txt`.
- Files analyzed: 15 Python source files, plus the dependency manifest and README.
- Domain: task management, with users, categories, task status/priority and summary reports.
- Architecture before: one Flask entry point, SQLAlchemy models, route blueprints, one notification service and shared helpers. Routes combined HTTP, validation, queries, business rules and response serialization; there were no controllers or repositories.

## Summary

- CRITICAL: 4
- HIGH: 3
- MEDIUM: 5
- LOW: 0
- Total: 12

## Findings

### [CRITICAL] TMA-001 — Application secret embedded in source
- File: `task-manager-api/app.py:11-13`
- Evidence: the database URI and Flask `SECRET_KEY` are assigned as source literals; secret value: `[REDACTED]`.
- Description: boot configuration was fixed in the module and included a committed signing key.
- Impact: the key could be reused to forge signed session data, and deployments could not safely configure independent credentials.
- Recommendation: load secret and database settings from environment/configuration and keep only placeholders in `.env.example`.
- Deprecated API: não aplicável.

### [CRITICAL] TMA-002 — SMTP credentials embedded in notification service
- File: `task-manager-api/services/notification_service.py:7-10`
- Evidence: SMTP host/account/password were stored as instance defaults; credential values: `[REDACTED]`.
- Description: email credentials were part of source code and the service printed exception text.
- Impact: repository access could expose a usable email credential; exception text could disclose provider details.
- Recommendation: inject SMTP settings from environment and avoid logging provider exception contents.
- Deprecated API: não aplicável.

### [CRITICAL] TMA-003 — MD5 used as the password verifier
- File: `task-manager-api/models/user.py:27-32`
- Evidence: `set_password` and `check_password` both used `hashlib.md5`.
- Description: passwords were stored as fast, unsalted MD5 digests.
- Impact: stolen hashes are cheap to crack and reuse across accounts.
- Recommendation: use a salted password KDF such as Werkzeug `generate_password_hash`/`check_password_hash`; users with legacy MD5 hashes need password resets.
- Deprecated API: não aplicável.

### [CRITICAL] TMA-004 — User serializer returned the password hash
- File: `task-manager-api/models/user.py:16-25`
- Evidence: public `to_dict()` included the `password` model field.
- Description: create, update, detail and login responses reused this serializer.
- Impact: API consumers could obtain password verifiers and use them for offline cracking.
- Recommendation: expose an explicit public DTO that excludes password fields.
- Deprecated API: não aplicável.

### [HIGH] TMA-005 — Login returned a predictable placeholder token
- File: `task-manager-api/routes/user_routes.py:207-210`
- Evidence: the login response assembled a token from a fixed `fake-jwt-token-` prefix and the numeric user ID.
- Description: the value looked like an authentication token but was predictable and was not cryptographically signed.
- Impact: clients could mistake a placeholder for a credential suitable for authorization.
- Recommendation: apply PB-11 from the refactoring playbook: issue a real signed JWT with an explicit algorithm, minimal claims, configurable secret and expiration; update tests and documentation rather than preserving the placeholder for compatibility.
- Deprecated API: não aplicável.

### [HIGH] TMA-006 — Route handlers mixed HTTP, persistence and business logic
- File: `task-manager-api/routes/task_routes.py:11-63`
- Evidence: `get_tasks` queried tasks, fetched each user/category, calculated overdue status, serialized the response and caught errors in one route handler.
- Description: the same responsibility mixing recurred in user and report/category routes.
- Impact: behavior was hard to test independently and changes to storage or rules required editing HTTP handlers.
- Recommendation: retain routes as HTTP adapters and move use cases and queries to controllers/services and repositories.
- Deprecated API: não aplicável.

### [HIGH] TMA-007 — Entry point coupled configuration, route registration and database creation
- File: `task-manager-api/app.py:9-31`
- Evidence: the module built the Flask app, assigned settings, registered blueprints, declared health/root routes and called `db.create_all()` at import time.
- Description: application construction had no factory or injectable test configuration.
- Impact: importing the module had database side effects and tests could not select isolated settings cleanly.
- Recommendation: use an application factory, a dedicated configuration module and explicit test configuration.
- Deprecated API: não aplicável.

### [MEDIUM] TMA-008 — Task listing performed per-row relationship queries
- File: `task-manager-api/routes/task_routes.py:14-52`
- Evidence: after loading all tasks, the loop separately called `User.query.get` and `Category.query.get` for each task.
- Description: query count grew with the number of returned tasks.
- Impact: task list latency and database load grew linearly with related rows.
- Recommendation: eager-load user/category relationships in the task query.
- Deprecated API: `Query.get` was used in this route; use the current session lookup API or relationship eager loading.

### [MEDIUM] TMA-009 — Reports repeated queries while iterating users and categories
- File: `task-manager-api/routes/report_routes.py:53-68,157-165`
- Evidence: summary queried tasks once per user; category listing issued a task count query per category.
- Description: both report paths had N+1 query patterns.
- Impact: report latency and database load increased with user/category count.
- Recommendation: calculate grouped counts in aggregate queries and join them to their parent rows.
- Deprecated API: não aplicável.

### [MEDIUM] TMA-010 — Input validation was duplicated and inconsistent
- File: `task-manager-api/routes/user_routes.py:42-72,92-122`; `task-manager-api/routes/task_routes.py:92-114`
- Evidence: email/password/role checks and task title/status/priority checks were implemented directly in separate handlers.
- Description: create and update paths applied different checks and error messages.
- Impact: the same invalid input could receive different behavior depending on the endpoint.
- Recommendation: centralize shared validators and retain endpoint-specific public messages.
- Deprecated API: não aplicável.

### [MEDIUM] TMA-011 — Bare exception handlers obscured failures
- File: `task-manager-api/routes/user_routes.py:127-132,144-151`; `task-manager-api/routes/task_routes.py:62-63,231-238`
- Evidence: mutation handlers used bare `except:` blocks and returned generic errors without typed handling.
- Description: all exception types were treated identically and failures were difficult to diagnose.
- Impact: programming errors could be hidden as routine storage failures.
- Recommendation: catch expected persistence exceptions, roll back centrally and return sanitized API errors.
- Deprecated API: não aplicável.

### [MEDIUM] TMA-012 — Deprecated naive UTC clock API
- File: `task-manager-api/models/task.py:15-16`; `task-manager-api/routes/task_routes.py:30-32`
- Evidence: model defaults and overdue checks used `datetime.utcnow()`.
- Description: the API emitted `DeprecationWarning` under the Python 3.14 runtime used for validation.
- Impact: future Python versions may remove this API, and naive timestamps make timezone assumptions implicit.
- Recommendation: use timezone-aware UTC time; where existing SQLite `DateTime` columns require naive UTC, convert at the persistence boundary.
- Deprecated API: `datetime.utcnow()`; warning observed on Python 3.14. Replaced with `datetime.now(timezone.utc)` through `utils.time.utcnow()` while preserving naive UTC column values.

## Confirmation Gate

`Proceed with refactoring (Phase 3)? [y/n]`

Human confirmation: affirmative confirmation was included in the user's Phase 3 request on 2026-11-12. Work proceeded under that prior authorization.

## Refactoring and validation

- Before structure: `app.py`, `models/`, `routes/`, `services/`, `utils/`; SQL-heavy and rule-heavy route handlers.
- After structure: `config/`, `controllers/`, `repositories/`, `models/`, thin `routes/`, shared `validation.py`, `errors.py`, `utils/`, `services/`.
- Configuration: environment-backed `SECRET_KEY`, `DATABASE_URL`, SMTP settings, host and port; `.env.example` contains placeholders only. The application generates a process-local random key if `SECRET_KEY` is omitted.
- Security: Werkzeug password hashing is used; `User.to_dict()` excludes password; SMTP credentials are environment-backed; the seed password is required through `SEED_DEFAULT_PASSWORD`; login now issues an HS256 JWT with `sub`, `email`, `role`, `iat` and `exp`, using `SECRET_KEY` and configurable `JWT_EXPIRES_MINUTES`.
- Query behavior: task list eager-loads user/category, user listing and category listing use grouped queries, and report productivity is aggregated by user.
- Contract: all original route paths and methods remain registered, including root, health, tasks/search/stats, users and login, report summary/user, and category CRUD.
- Tests: `PYTHONPATH=/tmp/task-manager-test-deps /home/hlruffo/Desktop/desafio-skill-auditoria-refatoracao/.venv-task-manager/bin/python -m pytest -q` — PASS, 5 passed. Pytest was installed into `/tmp` for this run; `requirements-dev.txt` now declares it for normal project setup.
- Syntax/import: `python -m compileall -q app.py config controllers errors.py models repositories routes seed.py services utils validation.py` — PASS.
- Seed: ran `seed.py` against a temporary SQLite database with environment values supplied; PASS, 3 users, 4 categories and 10 tasks.
- Boot: ran `app.py` as a separate process on `127.0.0.1:5127` with the temporary SQLite database — PASS; process was stopped with Ctrl-C after checks.
- HTTP checks: root, health, task list/search/stats/detail/create/update/delete, user list/detail/tasks, login, report summary/user and category list/create/update/delete — PASS (200/201 as expected).
- Remaining risks: existing database rows containing MD5 hashes cannot be upgraded without the users' plaintext passwords; reset those passwords. The JWT signing key is process/configuration-managed and should be set to a unique deployment secret rather than relying on the development fallback. `db.create_all()` remains in the factory for compatibility; production schema evolution should use migrations.
- Deprecated API search: `datetime.utcnow()` was found and replaced as described above; no other deprecated API was identified in the analyzed Python sources.
