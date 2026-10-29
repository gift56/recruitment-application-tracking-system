# Implementation Prompt: Django Admin Setup

## Goal

Register all five tracker models (`Department`, `JobPosting`, `Candidate`, `Application`, and `InterviewNote`) in Django admin through `tracker/admin.py`. Configure useful list columns, filters, and search for each model, render application stages as custom status badges, and provide an inline editor for interview notes on the `Application` admin page. Do not change the data model or build non-admin product features.

## Skills read

- `.agents/skills/architect`

No Django-admin-specific skill is available in the approved skill list. Follow the repository's `AGENTS.md` conventions and Django's built-in admin patterns.

## Existing code inspected

- `AGENTS.md` — project workflow, product scope, architecture, and security requirements.
- `tracker/models.py` — the five model definitions, field names, relationships, and status choices.
- `tracker/admin.py` — does not currently exist.
- `tracker/tests.py` — existing model test conventions and fixtures.
- `core/settings.py` — confirms Django admin is installed and the `tracker` app is enabled.
- `prompts/01-models-setup.md` and `prompts/02-environment-configuration.md` — established implementation-prompt format.

## Decisions and assumptions

- Keep all admin registrations and configuration in `tracker/admin.py`; do not change models, migrations, project settings, or URLs.
- Use Django's built-in admin authentication and model permissions. Do not add a custom admin site or weaken access controls.
- Use a `TabularInline` or similarly compact inline for `InterviewNote` on `Application`; show its interviewer, rating, notes, and scheduled time as appropriate.
- The application status badge is an admin list display for the existing `Application.status` choices. Render only fixed, developer-defined labels and color values; do not interpolate untrusted content into HTML.
- Use current model field names (`JobPosting.status`, `Application.status`, `Application.applied_at`, `InterviewNote.scheduled_at`); do not introduce legacy names such as `is_active` or `applied_date`.
- Keep any new tests in the existing `tracker/tests.py` unless the repository's test structure requires otherwise.

## Files likely to change

- `tracker/admin.py` — new model admin registrations, list configuration, status badge, and inline.
- `tracker/tests.py` — focused coverage for admin registrations and the custom status badge.

## Implementation requirements

1. Register `Department`, `JobPosting`, `Candidate`, `Application`, and `InterviewNote` exactly once.
2. Provide an appropriate `ModelAdmin` configuration for each model:
   - `Department`: display its name and a useful description value; allow search by name and description.
   - `JobPosting`: display title, department, location, status, and creation time; filter by department, status, and creation time; search by title, location, description, requirements, and department name.
   - `Candidate`: display full name, email, phone, and portfolio URL; search by full name, email, and phone.
   - `Application`: display candidate, job posting, custom status badge, and application time; filter by status and application time; search by candidate name/email and job title.
   - `InterviewNote`: display application, interviewer, rating, and scheduled time; filter by rating and scheduled time; search by interviewer name, notes, candidate name/email, and job title.
3. Use Django admin's supported related-field lookup syntax for searches and ensure list columns reference real model fields or valid admin display methods.
4. Implement a readable custom status badge for all six `Application.Status` values (`Applied`, `Screening`, `Interview`, `Offer`, `Hired`, `Rejected`). Give stages distinguishable colors with accessible contrast, provide a safe fallback for any unexpected value, and use Django's safe HTML formatting helper rather than marking arbitrary strings safe.
5. Add an `InterviewNote` inline to the `Application` admin. Ensure notes can be added and edited in the parent application page and existing notes show useful identifying fields.
6. Preserve model validation and existing behavior. Do not add custom save logic, bulk-edit shortcuts, extra models, endpoints, templates, or dependencies.
7. Add focused tests to confirm all models are registered, the application admin includes the interview-note inline, and the badge outputs the expected label/style for each supported stage without unsafe interpolation.

## Security requirements

- Keep admin access protected by Django's standard authentication and permissions; do not expose admin data through public views or custom URLs.
- Use Django's safe HTML formatting utilities for badge output, with fixed trusted style values and the model's known status label. Do not concatenate or mark user-controlled values as safe.
- Do not bypass model validation or resume upload validators in the admin.
- Do not modify CSRF, middleware, authentication, or permission settings.

## Acceptance criteria

- All five tracker models are registered exactly once and have meaningful `list_display`, `list_filter`, and `search_fields` settings.
- The `Application` list displays a styled badge for every configured status.
- The `Application` change page provides an inline editor for related `InterviewNote` records.
- Admin configuration uses actual model fields and relation paths and introduces no unrelated behavior.
- Focused admin tests and the configured Django checks pass.

## Checks to run

Run from the project root using `uv run`; ensure `DJANGO_SECRET_KEY` is configured in the shell or project-root `.env` without placing a real secret in source control:

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`

Report the exact results. No migration should be created for this admin-only change.

## Exact manual test steps

1. From the project root, run `uv run python manage.py createsuperuser` if no admin account exists.
2. Start the server with `uv run python manage.py runserver`.
3. Sign in at `/admin/` using the superuser account.
4. Confirm Department, Job posting, Candidate, Application, and Interview note are available in the tracker section.
5. Open each model's changelist and confirm its configured columns, filters, and search work with representative records.
6. Open an Application changelist and confirm each supported stage appears as a readable, color-coded badge.
7. Open an Application record, add and edit an InterviewNote using the inline, save, and confirm the note is associated with that application.
8. Sign out and confirm admin pages require authentication.
9. Stop the development server and run the checks listed above.
