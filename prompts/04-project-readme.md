# Implementation Prompt: Project README

## Goal

Create a professional, detailed root-level `README.md` introducing the Recruitment and Application Tracking System, describing what is currently implemented, explaining local setup and development requirements, and clearly separating the product roadmap from existing functionality. Make it suitable for a public GitHub repository without claiming that unfinished features exist.

## Skills read

- `.agents/skills/architect`

No additional skills are needed for this documentation-only task.

## Existing code inspected

- `AGENTS.md` — product goals, architecture, approved technology, environment variable policy, and standard checks.
- `core/settings.py` — current Django settings, `.env` loading, required `DJANGO_SECRET_KEY`, enabled apps, SQLite configuration, `DEBUG`, and URL configuration.
- `core/urls.py` and `tracker/urls.py` — mounted admin and empty tracker URL namespace.
- `manage.py` and `core/wsgi.py` — project entry points and settings module.
- `tracker/models.py` — current entities, application stages, interview ratings, and resume validation rules.
- `tracker/admin.py` — implemented model registrations, admin search/filter configuration, application status badges, and interview-note inline.
- `tracker/tests.py` — existing model and admin test coverage.
- `.env.example` and `.gitignore` — local secret setup and ignored files.
- Project root — no `README.md`, `pyproject.toml`, `requirements.txt`, or other dependency manifest currently exists.
- Active development environment — Python 3.12.13, Django 6.1.2, and uv 0.11.16.

## Decisions and assumptions

- Create only the root `README.md`; do not add or modify dependency manifests, runtime configuration, or application code.
- Describe the current project as an in-progress Django ATS foundation. Clearly identify models and Django admin as implemented, and role-based dashboards, public job listings/applications, and analytics as planned rather than available.
- Treat “what's needed” as the prerequisites, environment setup, install/run/test commands, security considerations, and further work required before production deployment.
- Since there is no dependency manifest, document the currently used Django version and a direct local installation command; do not imply that dependencies are locked or reproducibly managed.
- Use the actual setting names and behavior in code. `DJANGO_SECRET_KEY` is currently required and loaded from the project-root `.env` or process environment; SQLite is configured; `DEBUG` is currently enabled; `DATABASE_URL` and `DJANGO_DEBUG` are not currently wired into settings.
- Do not invent a repository URL, deployment target, license, badge, release status, screenshots, or contribution policy.
- Keep any production-readiness discussion factual and distinguish recommendations from implemented capabilities.

## Files likely to change

- `README.md` — new project overview, setup guide, current scope, roadmap, and development documentation.

## Implementation requirements

1. Write a clear title and summary that explain the recruitment/application tracking goal and current development status.
2. Include an “Implemented today” section accurately covering:
   - Department, job posting, candidate, application, and interview-note models.
   - Application stages and active/inactive job-posting status.
   - Django admin management, including searchable/filterable lists, stage badges, and interview notes inline on applications.
   - Resume validation for PDF/DOCX extensions, file size, and document content.
   - Existing automated test coverage without implying a user-facing job board or dashboard is already present.
3. Include a roadmap or “Planned work” section covering major intended product areas from `AGENTS.md`, with unfinished features clearly labeled.
4. Document the stack and prerequisites using verified versions: Python 3.12+, Django 6.1.2 as currently used, and uv as the documented local environment workflow. Identify SQLite as the current local database configuration and do not claim PostgreSQL is configured.
5. Give working setup instructions from a fresh checkout:
   - Install uv if needed and create a local virtual environment.
   - Install the currently used Django version without committing secrets.
   - Copy `.env.example` to `.env` and replace its placeholder with a newly generated local secret.
   - Apply migrations, create a superuser, run the development server, and access Django admin.
   - Include Windows PowerShell and POSIX shell variants for copying `.env.example` if useful; do not show or generate a real secret.
6. Document the actual development checks: `uv run python manage.py check`, `uv run python manage.py makemigrations --check`, and `uv run python manage.py test tracker`.
7. Describe the environment truthfully:
   - `DJANGO_SECRET_KEY` is required.
   - `.env` is ignored by git; `.env.example` is safe to commit.
   - The database is currently SQLite.
   - `DEBUG` is currently `True`; `DJANGO_DEBUG` and `DATABASE_URL` are not yet consumed by settings.
8. Include a concise project structure overview pointing to real files and directories only.
9. Include security and production-readiness notes: never commit `.env`/secrets, keep debug disabled in production, configure allowed hosts and an appropriate production database/media strategy before deployment, and maintain the existing resume validation.
10. Keep the README scannable with clear headings, concise prose, and correct Markdown command fences. Avoid unnecessary badges, unsupported claims, and placeholder URLs.

## Security requirements

- Never include actual secret values, contents from `.env`, or credentials in the README.
- Refer to `.env.example` as a template only; instruct developers to create their own `.env`.
- Do not advertise the current settings as production-ready. Explicitly disclose that debug mode is enabled and current database settings use SQLite.
- Do not claim that authentication roles, public application endpoints, or production media storage are implemented unless verified in the code.

## Acceptance criteria

- A root `README.md` exists and provides a useful, polished introduction for GitHub visitors.
- The README distinguishes implemented code from planned product features.
- All setup commands correspond to the current project layout and settings; no project URL, dependency manifest, license, or deployment behavior is invented.
- Secret handling, current SQLite/debug state, and production limitations are accurately disclosed.
- The README includes prerequisites, installation, environment configuration, migrations, admin access, tests, project structure, and next steps.
- No files other than `README.md` are changed for this documentation task.

## Checks to run

Documentation-only change; validate the README against the inspected project files and verify Markdown structure and command references. Do not run Django checks unless a documentation validation tool already exists in the project. Report any commands that were not run and why.

## Exact manual test steps

1. Open `README.md` at the repository root and verify the overview identifies the project and its current in-progress status.
2. Follow the setup steps in a clean local environment using a locally generated secret; confirm `.env` remains ignored by git.
3. Apply migrations, create a superuser, and start the server; verify Django admin is available at `/admin/`.
4. Run each documented Django check/test command and confirm the README commands match the project.
5. Review the implemented/planned sections and confirm they do not imply that public job board, application-submission, role-dashboard, analytics, or production database features already exist.
