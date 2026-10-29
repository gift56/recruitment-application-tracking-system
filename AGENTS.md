# Project Guidelines

## Project status and scope

- This is a Django recruitment-tracking project. `README.md` is the source of truth for implemented capabilities and the roadmap; do not describe planned features as available.
- The current verified stack is Python 3.12+, Django 6.1.2, `uv`, and SQLite. There is no dependency manifest or frontend build pipeline yet.
- The `tracker` app has recruitment models, admin configuration, tests, a public job board and candidate application flow, and a home page served at `/` and `/tracker/`. The root route uses the `tracker` namespace; the `/tracker/` mount uses `tracker_app` to avoid duplicate namespace ambiguity.
- Recruiter dashboards and account routes remain unimplemented. Do not redirect to or link to those destinations until their endpoints exist.
- Implement only the feature requested. Do not add authentication, APIs, routes, dependencies, or production infrastructure as incidental work.

## Workflow

1. Read this file, the relevant prompt in `prompts/`, and the code that the change will touch.
2. Read applicable skills named by the user and any clearly relevant skills available in the workspace. Do not invent skills or assume a skill exists at a path that is not present.
3. Before implementing a feature, create or update its detailed prompt in `prompts/` and ask the user to approve it. Do not implement application code until approval; after approval, reread and follow the approved prompt.
4. Ask a focused question only when a material product or implementation decision cannot be resolved from the request and repository.
5. Keep changes scoped, preserve existing behavior, update directly related documentation, and report checks and exact manual verification steps.

Prompts should describe the goal, applicable skills, inspected code, decisions, likely files, requirements, relevant security concerns, acceptance criteria, checks, and exact manual test steps. For UI work, also specify layout, typography, color/status use, accessibility, responsiveness, and template organization.
When a feature adds or changes routes or user-visible capabilities, update this file to keep the project status and constraints accurate, and update `README.md` after implementation so it distinguishes delivered behavior from planned work. While a feature is awaiting approval, label it as planned rather than implemented.

## Django and repository conventions

- Keep data, input validation, request handling, and presentation in their appropriate Django layers. Use explicit `ModelForm.Meta.fields` or `exclude` when forms are added.
- Use Django ORM and optimize related-object access with `select_related` or `prefetch_related` when the query shape warrants it. Do not use raw unparameterized SQL.
- Preserve existing model constraints and resume validation: PDF/DOCX only, maximum 5 MiB, and document-content validation. Do not weaken validation or expose uploaded resumes.
- Templates discovered through the app should be organized under `tracker/templates/tracker/`; keep shared layout and reusable partials namespaced there (for example `tracker/base.html` and `tracker/partials/`). Use `APP_DIRS` as currently configured; change template settings only when necessary.
- Use the project's existing styling/build setup when one exists. If introducing a new asset mechanism is necessary, keep it within the approved prompt and avoid adding dependencies without approval.
- UI must use semantic HTML, keyboard-accessible controls, visible focus states, responsive layouts, and Django's normal escaping. Do not mark user-controlled content safe.
- Do not add or imply working navigation, account, logout, or policy destinations unless corresponding URL patterns exist. Do not add unrelated routes to make a presentation-only template appear functional.
- Use Django's CSRF protection for any state-changing forms. Restricted views must enforce authentication and authorization appropriate to the feature.
- Keep secrets out of source control. `DJANGO_SECRET_KEY` is required through the project-root `.env` or process environment; never inspect, quote, or commit `.env` values.

## Current setup and checks

Use `uv run` from the repository root. The local environment needs a project-root `.env` with a private `DJANGO_SECRET_KEY`; see `.env.example` and `README.md` for setup. Current settings use SQLite and `DEBUG = True`; do not claim the project is production-ready or that `DJANGO_DEBUG`/`DATABASE_URL` are wired into settings.

Run the smallest relevant checks, then the project checks for Django changes:

```shell
uv run python manage.py check
uv run python manage.py makemigrations --check
uv run python manage.py test tracker
```

Run migrations only when schema changes require them. Report commands that were not run and why. For documentation-only changes, validate claims against the repository; Django checks are not required.
