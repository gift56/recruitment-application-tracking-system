# Recruitment and Application Tracking System

A Django-based foundation for organizing recruitment workflows, job openings, candidate records, applications, and interview feedback.

> **Project status:** In active development. The core data models and Django admin are available. The public job board, candidate application flow, role-specific dashboards, and analytics are planned and are not implemented yet.

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
- **Automated tests:** The tracker test suite covers model behavior, validation, admin registrations, status badges, and interview-note inline configuration.

There is currently no public job board, candidate-facing application submission form, recruiter dashboard, or analytics page. The `/tracker/` URL namespace is mounted but has no application endpoints yet.

## Planned product work

The following are goals for future development, not current features:

- Authentication roles for recruiters, hiring managers, and candidates, with appropriate access controls.
- Public active-job listings and job detail pages.
- Candidate application submission and resume upload forms.
- Recruiter-facing application pipeline tools and filtering.
- Role-specific dashboards and recruitment analytics.
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

### 5. Start the development server

```shell
uv run python manage.py runserver
```

Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and sign in with the superuser account. The tracker records can be managed through Django admin.

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
│   ├── migrations/       # Database schema migrations
│   ├── models.py         # Recruitment data models and resume validation
│   ├── tests.py          # Model and admin tests
│   └── urls.py           # Tracker URL namespace (currently no endpoints)
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
- Apply authentication and authorization checks to any future recruiter, hiring-manager, or candidate-facing functionality.

## Contributing

The codebase is under active development. Before opening a change, run the development checks above and keep implementation claims and documentation aligned with the actual code.
