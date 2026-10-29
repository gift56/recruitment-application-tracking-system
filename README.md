# Recruitment and Application Tracking System

A Django-based foundation for organizing recruitment workflows, job openings, candidate records, applications, and interview feedback.

> **Project status:** In active development. The core data models, Django admin, public job board, candidate application flow, and staff-only recruiter portal are available. Authentication roles beyond Django's `is_staff` flag and production infrastructure remain future work.

## What the project is about

The goal is to provide a central place for recruiters and hiring teams to manage job postings and follow applications through a consistent hiring pipeline:

**Applied → Screening → Interview → Offer → Hired / Rejected**

The system is being developed with a focus on clear Django app structure, explicit validation, secure resume handling, and maintainable recruitment records.

## Current capabilities

- **Recruitment data model:** Departments, job postings, candidates, applications, and interview notes are represented in the `tracker` app.
- **Job posting status:** Job postings can be marked Active or Inactive.
- **Application stages:** Applications use Applied, Screening, Interview, Offer, Hired, and Rejected statuses.
- **Interview feedback:** Interview notes are linked to applications and include an interviewer, a 1–5 rating, notes, and scheduled time.
- **Django admin:** All tracker models are registered with useful list views, filters, and search. Application stages have color-coded badges, and interview notes can be edited inline on an application.
- **Resume validation:** Candidate resumes are restricted to PDF and DOCX files, limited to 5 MiB, and checked for expected document content.
- **Public home page:** The site root (`/`) shows a recruitment hero, job search, and the four newest active openings. The same page is available at `/tracker/`.
- **Public job board:** `/jobs/` lists active job postings with title/location search, department filters, and pagination; homepage cards, job listings, and active job details show a labeled salary range (or “Not provided” for older postings with no range).
- **Candidate applications:** Candidates can submit their contact details, optional resume and portfolio URL, and cover letter for active jobs. Resume uploads retain PDF/DOCX, 5 MiB, and document-content validation.
- **Recruiter portal:** Staff sign in at `/login/`; `/recruiter/` shows applicant, active-posting, interview, and hired metrics; `/recruiter/jobs/` lists all postings; and `/recruiter/jobs/create/` creates job postings with a required salary range. Recruiters can also add departments at `/recruiter/departments/create/`, edit job details/status, and delete jobs that have no applications. A job with applications cannot be deleted; mark it Inactive to retain its history.
- **Private recruiter data:** Recruiter routes require an authenticated staff user. Resume files are delivered through a protected recruiter route rather than a public media link.
- **Development seed data:** `uv run python manage.py seed_data` creates Engineering, Product, and Design departments, three active sample jobs, and a local test recruiter account (`recruiter` / `password123`). This fixed credential is for local development only; the command refuses to run when `DEBUG` is false.
- **Automated tests:** The tracker test suite covers model behavior, validation, admin registrations, templates, public job filtering and details, application submissions, recruiter access and workflows, private resume delivery, seed data, and URL behavior.

Public pages expose active job information only; candidate records, applications, and uploaded resume contents are not displayed. Candidate and application information is available through the staff-protected recruiter portal and Django admin.

## Planned product work

The following are goals for future development, not current features:

- Fine-grained authentication roles for recruiters, hiring managers, and candidates beyond the current `is_staff` access check.
- Advanced pipeline filtering and additional recruitment analytics.
- Production-ready database, media storage, and deployment configuration.

## Technology

- Python 3.12+
- Django 6.1.2 (current development environment)
- SQLite (current local database configuration)
- `uv` for the documented local Python environment workflow

PostgreSQL is a possible future production database, but it is not configured in the current settings. The project does not currently include a dependency manifest or lockfile.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) installed and available on your `PATH`
- Git, to clone the repository

## Local setup

Run these commands from the repository root, where `manage.py` is located.

### 1. Create an environment

Clone the repository using the **Code** button on GitHub, then change into the project directory. From the repository root, create a virtual environment:

```shell
uv venv
```

Activate the virtual environment if desired:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```shell
source .venv/bin/activate
```

### 2. Install Django

There is no project dependency manifest yet, so install the Django version currently used by the project:

```shell
uv pip install "Django==6.1.2"
```

### 3. Configure the local secret

Copy `.env.example` to `.env`:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```shell
cp .env.example .env
```

Edit `.env` and replace the placeholder `DJANGO_SECRET_KEY` value with a newly generated, private key for your local environment. The settings loader reads the project-root `.env` file and does not override an existing process environment variable. `.env` is ignored by git; never commit it or share its contents. `.env.example` is only a template.

### 4. Set up the database and admin account

```shell
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

For quick local portal testing, seed sample departments, jobs, and a recruiter account:

```shell
uv run python manage.py seed_data
```

The local test account is `recruiter` / `password123`. Do not reuse this credential outside local development.

### 5. Start the development server

```shell
uv run python manage.py runserver
```

Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and sign in with the superuser account to manage tracker records through Django admin. The local test recruiter can sign in at `/login/` and use the staff portal.

## Development checks

Run from the repository root:

```shell
uv run python manage.py check
uv run python manage.py makemigrations --check
uv run python manage.py test tracker
```

## Project structure

```text
.
├── core/
│   ├── settings.py       # Django settings and local environment loading
│   ├── urls.py           # Project URL configuration
│   └── wsgi.py           # WSGI entry point
├── prompts/              # Approved implementation prompts
├── tracker/
│   ├── admin.py          # Django admin registrations and configuration
│   ├── forms.py          # Candidate application form and input validation
│   ├── migrations/       # Database schema migrations
│   ├── models.py         # Recruitment data models and resume validation
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py # Local development sample data command
│   ├── templates/
│   │   └── tracker/      # Shared layout, partials, public pages, and recruiter portal
│   ├── tests.py          # Model, admin, public-flow, recruiter, and seed tests
│   ├── urls.py           # Namespaced public and staff recruiter routes
│   └── views.py          # Public job flow and staff recruiter views
├── .env.example          # Safe local environment template
└── manage.py             # Django management commands
```

## Security and production readiness

This repository is intended for local development and is **not production-ready**:

- `DEBUG` is currently enabled in `core/settings.py`. Do not deploy with debug enabled.
- The current database configuration uses SQLite. Production database configuration has not been implemented.
- `DJANGO_DEBUG` and `DATABASE_URL` are documented project goals but are not currently consumed by settings.
- Configure production `ALLOWED_HOSTS`, secure transport and cookie settings, secrets, database credentials, backups, and monitoring before deployment.
- Plan private, durable media storage and access controls before handling real candidate resumes in a deployed system.
- Keep `.env`, credentials, candidate data, and uploaded resumes out of source control.
- Preserve and test resume extension, size, and content validation when changing file handling.
- Recruiter pages, status changes, interview-note submission, and resume delivery require authenticated staff access. Public job browsing and candidate application submission are intentionally anonymous.
- The fixed development seed credential is not suitable for production. The project still requires production authentication/authorization design, private durable media storage, and deployment hardening before handling real candidate data.

## Contributing

The codebase is under active development. Before opening a change, run the development checks above and keep implementation claims and documentation aligned with the actual code.
