# Implementation Prompt: Initial Models and App Setup

## Goal

Create the initial recruitment-tracking database schema in `tracker/models.py` and register the `tracker` Django app in `core/settings.py` and `core/urls.py`. Include the minimum app scaffolding and initial migration needed to make the app load and the schema usable. Do not build views, forms, admin screens, or unrelated product features.

## Skills read

- `.agents/skills/django-models`
- `.agents/skills/architect`

Follow the repository's `AGENTS.md` conventions. Apply Django conventions appropriate to this project; do not import Sentry-specific model infrastructure from the supporting skill.

## Existing code inspected

- `AGENTS.md` — project workflow, schema roadmap, architecture and security requirements.
- `core/settings.py` — Django project settings and installed apps.
- `core/urls.py` — currently mounts only Django admin.
- `manage.py` — project settings module is `core.settings`.
- The workspace currently has no `tracker` app or `prompts/` directory.

## Decisions and assumptions

- `Candidate` is a standalone candidate record, not a profile linked to Django's `User`.
- `JobPosting.status` choices are `Active` and `Inactive`, defaulting to `Active`.
- `salary_range` is a human-readable text value rather than separate numeric bounds.
- Mount the app URLconf under `/tracker/`; create the minimal `tracker/urls.py` module needed for that include. Do not invent application endpoints.
- Use `PROTECT` for department/job/candidate relationships where deleting a referenced record could erase or orphan recruitment history; interview notes may cascade with their application.
- Treat salary range, candidate phone, resume and portfolio URL as optional; keep names and required application relationships required.
- Resume uploads are limited to 5 MiB and PDF/DOCX. Validate file extension and actual content/container type, and use a generated/sanitized storage name rather than trusting a supplied filename.
- Keep indexes explicit and useful for expected filters and ordering; avoid redundant indexes already created for foreign keys or unique fields.
- The current settings file has existing secret configuration. Never copy or expose its value. Follow `AGENTS.md`'s environment-only secret requirement when making settings changes; use `DJANGO_SECRET_KEY` with explicit missing-value behavior, and document any required local environment setup.

## Files likely to change

- `tracker/__init__.py`
- `tracker/apps.py`
- `tracker/models.py`
- `tracker/urls.py`
- `tracker/migrations/__init__.py`
- `tracker/migrations/0001_initial.py`
- `tracker/tests.py` or a focused `tracker/tests/` module
- `core/settings.py`
- `core/urls.py`

## Implementation requirements

1. Create a valid Django app config for `tracker` and add it to `INSTALLED_APPS`.
2. Define these models in `tracker/models.py`:
   - `Department`: `name`, `description`.
   - `JobPosting`: `title`, FK to `Department`, `location`, `salary_range`, `description`, `requirements`, `status`, `created_at`.
   - `Candidate`: `full_name`, `email`, `phone`, resume `FileField`, `portfolio_url`.
   - `Application`: FKs to `Candidate` and `JobPosting`, status choices `Applied`, `Screening`, `Interview`, `Offer`, `Hired`, `Rejected`, `applied_at`, `cover_letter`.
   - `InterviewNote`: FK to `Application`, `interviewer_name`, integer `rating` constrained to 1–5, `notes`, `scheduled_at`.
3. Use Django `TextChoices` or equivalent named choices for statuses, with intentional defaults. Use appropriate field types, `blank`/`null` settings, `related_name` values, and `on_delete` behavior. Use `auto_now_add=True` for `created_at` and `applied_at`.
4. Add a useful custom `__str__` to every model.
5. Add explicit, descriptively named database indexes for likely listing/filtering queries (including job status/date, application status/date and job/status, and interview-note application/schedule). Avoid duplicating implicit FK indexes. Enforce the interview rating range at both model validation and database-constraint level.
6. Add model tests covering string representations, choices/defaults, foreign-key relationships, rating boundaries, and resume file validation. Tests should also confirm invalid statuses/ratings cannot be persisted where database constraints apply.
7. Mount `tracker.urls` in `core/urls.py` under `/tracker/` with the app namespace. Keep its initial `urlpatterns` empty; do not add placeholder product behavior or views.
8. Create and apply the initial migration for all five models. Do not edit unrelated project files or add unnecessary dependencies.

## Security requirements

- Restrict resume uploads to `.pdf` and `.docx`, enforce the 5 MiB limit, and reject mismatched/invalid content rather than trusting only the client-supplied filename or MIME header.
- Keep upload paths safe and avoid allowing user-controlled path components.
- Do not add endpoints or weaken authentication, CSRF, or middleware settings. This task adds no request-handling views, forms, or public data access.
- Do not expose, reproduce, or commit secrets. Load the Django secret from the `DJANGO_SECRET_KEY` environment variable in accordance with `AGENTS.md`; fail clearly if it is missing rather than silently falling back to a hard-coded value.

## Acceptance criteria

- The five models and their required fields, choices, relations, `__str__` methods, and indexes are present.
- Invalid interview ratings and unsafe/oversized resume files are rejected.
- `tracker` is installed and its namespaced URLconf is included under `/tracker/`.
- The initial migration is generated and applies cleanly.
- Focused model tests pass; no unrelated views, forms, or features are introduced.

## Checks to run

Run from the project root using `uv run`, with `DJANGO_SECRET_KEY` set to a local test-only value in the shell environment:

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`
4. `uv run python manage.py migrate`
5. Start the development server with `uv run python manage.py runserver` and confirm it starts successfully.

Report the exact results. Do not commit any secret value or `.env` file.

## Exact manual test steps

1. Set `DJANGO_SECRET_KEY` in the local shell environment; do not place a real secret in source control.
2. Run `uv run python manage.py makemigrations tracker`, then `uv run python manage.py migrate`.
3. Run `uv run python manage.py check`, `uv run python manage.py makemigrations --check`, and `uv run python manage.py test tracker`; confirm all succeed.
4. Start the development server with `uv run python manage.py runserver` and confirm it starts successfully; stop it after verification.
5. In a Django shell (`uv run python manage.py shell`), create a department, job posting, candidate, application and interview note; confirm each `__str__` is useful and each relationship resolves.
6. Confirm an interview rating of 1 and 5 is accepted, while 0 and 6 are rejected.
7. Exercise resume validation with a valid PDF and DOCX, a disallowed extension, a file with a mismatched/invalid content signature, and a file larger than 5 MiB; only valid files should pass.
8. Confirm Django can import the namespaced `tracker` URLconf under `/tracker/` without introducing a product endpoint.
