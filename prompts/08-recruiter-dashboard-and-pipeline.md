# Implementation Prompt: Recruiter Dashboard and Application Pipeline

## Status

Implemented and validated. Do not expand scope beyond this prompt.

## Goal

Build the internal recruiter portal on top of the existing recruitment models and shared template shell. Add Django login, staff-only recruiter pages for dashboard metrics, job creation, and application pipeline management, secure resume access, interview-note submission, and an idempotent local development seed command. Preserve the existing public job board and candidate submission flow.

## Skills read

- `.agents/skills/architect` — align requirements and existing project conventions before implementation.
- `.agents/skills/django-forms` — use model-backed forms, centralize validation, and render errors.
- `.agents/skills/django-views` — use generic views and authentication/authorization mixins where appropriate.
- `.agents/skills/imprint` — capture reusable UI patterns in `ui-registry.md` after building the recruiter UI.
- No new model is currently required; reuse the existing `JobPosting`, `Application`, and `InterviewNote` models.

## Existing code inspected

- `AGENTS.md` — project status, prompt-approval workflow, Django conventions, resume security, UI accessibility, and checks.
- `README.md` — implemented public capabilities, planned recruiter functionality, setup, and security limitations.
- `prompts/05-design-system-and-base-template.md` and `prompts/07-public-job-board-and-application.md` — prior design and implementation decisions.
- `core/settings.py` — Django auth, templates, messages, SQLite, and current local `DEBUG=True` configuration.
- `core/urls.py` — root tracker URLconf mount and `/tracker/` compatibility mount.
- `tracker/models.py` — `Department`, `JobPosting`, `Candidate`, `Application`, `InterviewNote`, application/job status choices, required interview-note metadata, and resume validation.
- `tracker/forms.py` — existing public `ApplicationForm`; use explicit `ModelForm.Meta.fields`.
- `tracker/views.py` and `tracker/urls.py` — existing public routes and namespaced URL patterns.
- `tracker/templates/tracker/base.html`, `partials/navbar.html`, and `partials/status_badge.html` — Tailwind CDN shell, navigation, focus treatment, and six established status colors.
- `tracker/tests.py` — current test conventions and public-flow coverage.
- No existing recruiter views/routes, management commands, `ui-registry.md`, or `.agents/django-project-context.md` were found.

## Language and decisions

- **Recruiter:** an authenticated Django user with `is_staff=True`. There is no separate recruiter role model.
- **Resume preview:** candidate files may only be accessed through a recruiter-authenticated endpoint; never expose or link to a public media URL.
- **Interview note:** the form collects a 1–5 rating and notes. Populate the existing required `interviewer_name` from the signed-in user's full name, falling back to username, and set `scheduled_at` to the submission time.
- **Total Applicants:** count application submissions (`Application` rows), not distinct `Candidate` records, since each pipeline row represents an application for one role.
- **Seed recruiter:** `recruiter` / `password123` is local development test data only. The command must not overwrite an existing account's password or silently grant staff privileges to a conflicting existing username.
- **Dashboard versus pipeline:** `/recruiter/` contains the four metric cards and a clear link to the full pipeline; `/recruiter/applications/` contains the pipeline table.
- **Action routes:** use `/recruiter/applications/<int:pk>/status/`, `/recruiter/applications/<int:pk>/notes/`, and `/recruiter/applications/<int:pk>/resume/` for the protected pipeline actions.
- **Routes and namespaces:** add the requested root paths through `tracker/urls.py`, preserving both existing URLconf mounts and the `tracker` root namespace. Because the same URLconf is mounted at `/tracker/`, its routes remain available under that prefix too. Use root `tracker` names for links and redirects.
- **No extra product scope:** do not add recruiter registration, role models, logout/account routes, APIs, unrelated job editing, dependencies, or production infrastructure.

## Files likely to change

- `tracker/views.py` — login configuration and recruiter dashboard, job-create, pipeline, status-update, note-create, and protected resume-serving views.
- `tracker/urls.py` — named login and recruiter routes.
- `tracker/forms.py` — `JobPostingForm` and an `InterviewNoteForm` with explicit field allowlists.
- `tracker/templates/tracker/login.html` — accessible login form.
- `tracker/templates/tracker/job_form.html` — job-posting creation form.
- `tracker/templates/tracker/recruiter_dashboard.html` — four metric cards and pipeline call to action.
- `tracker/templates/tracker/application_pipeline.html` — application table, status forms, resume links, and evaluation-note drawer/forms.
- `tracker/management/commands/seed_data.py` — idempotent local sample data command.
- `tracker/tests.py` or focused modules under `tracker/tests/` — authentication, authorization, forms, metrics, pipeline updates, note creation, resume access, and seed behavior.
- `tracker/templates/tracker/partials/navbar.html` — expose only valid recruiter/login links according to authentication and staff status.
- `ui-registry.md` — record recruiter UI patterns after building the components, following the imprint workflow; do not refactor existing unrelated pages.
- `AGENTS.md` and `README.md` — after implementation, update factual project status and document delivered routes/seed usage while retaining the distinction between local development and production.

Do not edit application code, README feature claims, or current project-status statements while this feature is awaiting approval. This prompt file is the only planned pre-approval change.

## Implementation requirements

### 1. Login and authorization

1. Add a Django `LoginView` at `/login/` using `tracker/login.html`; keep login CSRF protection and show bound field and non-field errors.
2. On successful login, send the user to the recruiter dashboard unless Django's validated `next` parameter requests another safe destination.
3. Use a shared authorization pattern for every `/recruiter/*` view:
   - anonymous visitors are redirected to `/login/` with the requested path preserved as `next`;
   - authenticated users without `is_staff=True` receive HTTP 403;
   - staff users may proceed.
4. Do not treat a login redirect alone as authorization. Protect status updates, note submissions, and resume delivery as well as HTML pages.
5. Keep public job browsing and candidate application submission anonymous and unchanged.
6. Preserve current `/`, `/tracker/`, `/admin/`, and public job route behavior. Avoid unresolved URL names or links to non-existent logout/account pages.

### 2. Job posting creation

1. Add `JobPostingForm` as a `forms.ModelForm` with an explicit `Meta.fields` allowlist: `title`, `department`, `location`, `salary_range`, `description`, `requirements`, and `status`.
2. Use existing model choices and validation. Render department as a usable select and provide appropriate multiline widgets for long text.
3. Add a staff-only create view at `/recruiter/jobs/create/`. On valid POST, save once, show a success message, and redirect to the recruiter dashboard or another implemented recruiter destination. Invalid forms must re-render with field and non-field errors.
4. Build `tracker/job_form.html` extending `tracker/base.html`, with labels, help text where useful, inline errors, CSRF token, and a visible cancel/back link to an implemented page.

### 3. Dashboard metrics

At `/recruiter/`, show four responsive summary cards:

- **Total Applicants:** count `Application` records.
- **Active Postings:** count `JobPosting` records with `JobPosting.Status.ACTIVE`.
- **Candidates in Interview:** count applications with `Application.Status.INTERVIEW`.
- **Hired Count:** count applications with `Application.Status.HIRED`.

Use database counts rather than loading complete record sets. Label metrics clearly and show zero naturally when there is no data. Do not add charts or dependencies. Provide a clear action to `/recruiter/applications/` and an implemented action to `/recruiter/jobs/create/`.

### 4. Application pipeline and status updates

1. Add `/recruiter/applications/` with a staff-only pipeline table. Each row represents an `Application` and includes candidate name, target role, applied date, current status badge, an authorized resume action when a resume exists, and a status selector.
2. The selector offers exactly the existing stages in order: Applied → Screening → Interview → Offer → Hired → Rejected. Display the established status badge colors from the shared partial.
3. Optimize the pipeline queryset with `select_related`/`prefetch_related` for the related candidate, job, and interview notes only where needed. Order by newest application first. Pagination is optional unless needed to keep the page usable with larger datasets.
4. Submit status changes with a CSRF-protected POST to a dedicated recruiter route. Validate the submitted value against `Application.Status.choices` on the server, update only the requested application, show a success/error message, and use Post/Redirect/Get. Do not trust the `<select>` options as validation.
5. Do not expose candidate data or pipeline information through public views or templates.

### 5. Private resume access

1. Do not render `candidate.resume.url` or configure public media serving for recruiter files.
2. Add a staff-only endpoint for a pipeline resume action. Resolve the file through the related candidate/application, return 404 when no resume is attached or the file is unavailable, and serve it using Django's file response utilities with a safe filename and a content disposition appropriate to preview/download.
3. Preserve existing PDF/DOCX extension, 5 MiB size, and content validation. Do not weaken validation or expose file paths in responses.
4. Test that anonymous users are redirected, authenticated non-staff users are forbidden, staff can access a valid file, and absent files return 404. Ensure error behavior does not reveal server filesystem paths.

### 6. Evaluation notes

1. Add an `InterviewNoteForm` as a `ModelForm` with explicit editable fields `rating` and `notes` only. Keep rating constrained to 1–5 through the existing model validators and a usable select/radio control.
2. Provide an accessible drawer-like form for each application in the pipeline using semantic HTML and keyboard-operable controls. Prefer progressive enhancement (for example a `<details>` disclosure) over a JavaScript-only modal; do not add dependencies.
3. Submit notes via a CSRF-protected POST route associated with the application row. Set `application`, `interviewer_name`, and `scheduled_at` on the server; never accept these values from user input.
4. Validate before saving, display form errors accessibly, show a success message, and redirect back to the pipeline. Preserve existing notes and ensure one applicant's form cannot attach a note to another application's record by tampering with submitted data.

### 7. Local seed command

1. Implement `uv run python manage.py seed_data` to create the default departments Engineering, Product, and Design; three active sample jobs associated with those departments; and a staff test account with the requested credentials on a fresh local database.
2. Make repeated runs safe and idempotent: use stable lookups for departments/jobs and do not create duplicates. Do not reset a pre-existing user's password or silently turn a conflicting non-staff account into staff; report a clear `CommandError` for a conflicting username.
3. Guard the fixed development credential so the command refuses to run when `settings.DEBUG` is false. Do not claim this is safe production seeding; the current local settings use `DEBUG=True`.
4. Print a concise success summary without printing passwords except as required in the documented local manual test instructions. Keep the requested username/password documented explicitly as development-only test credentials.
5. Do not run or create schema migrations; existing models already support the seeded records.

### 8. UI, accessibility, and templates

1. Reuse `tracker/base.html`, its Tailwind CDN, system typography, slate/white surfaces, indigo accents, existing focus states, alert messages, and namespaced template organization. Do not introduce a frontend build pipeline or dependency.
2. Keep the login page focused and calm; keep forms and metric cards visually consistent with the existing light SaaS design.
3. Make the pipeline usable on small screens (for example, responsive card/list treatment or a horizontally scrollable table with a clear accessible label) and desktop widths.
4. Use semantic headings, table headers, form labels, accessible names, visible keyboard focus, sufficient contrast, and appropriate live/error roles. Ensure each repeated row form has unique IDs and correctly associated labels/errors.
5. Preserve Django template autoescaping. Never mark candidate data, notes, errors, or user names safe.
6. Follow the imprint workflow: inspect the existing UI baseline, update/create `ui-registry.md` with the recruiter component patterns after implementation, and do not make unrelated restyling changes.

## Security and privacy requirements

- Enforce `is_staff` authorization server-side on every recruiter route, including every POST and file-serving endpoint.
- Preserve Django CSRF protection on login and all state-changing forms.
- Use explicit form field allowlists; do not permit clients to set application status outside the dedicated validated action or set interview attribution fields.
- Keep candidate records, interview notes, and resumes private. Never expose resume URLs or content to public pages.
- Use a safe response filename and do not disclose storage paths or raw exception details.
- Treat the seed credentials as a local testing convenience only, guard the command outside DEBUG, and never claim the repository is production-ready.
- Do not add authentication roles, user registration, unrelated routes, dependencies, schema changes, or infrastructure.

## Acceptance criteria

- `/login/` renders the standard Django login flow using `tracker/login.html`; valid credentials reach the recruiter dashboard and invalid credentials display accessible errors.
- Anonymous users cannot access any recruiter route; authenticated non-staff users receive 403; staff can access authorized pages and actions.
- Staff can create a job using only the requested fields; invalid submissions preserve errors and do not create records.
- The dashboard displays correct counts for all four metrics, including zero and multiple applications for one candidate.
- The pipeline shows each application with candidate, target job, applied date, stage, conditional protected resume action, and a functional status selector.
- Invalid status values and unauthorized/malformed writes are rejected without changing records.
- Evaluation notes persist rating and notes with the signed-in staff user and current submission time, and cannot be attached to a different application by client tampering.
- Resume access is staff-only, handles missing files safely, and preserves the existing upload constraints.
- `seed_data` creates the requested departments, three active jobs, and a staff `recruiter` account on a fresh local database; reruns do not duplicate data or overwrite existing credentials.
- The current root, `/tracker/`, `/admin/`, and public job-board/application behavior remains intact.
- Responsive layouts, keyboard operation, visible focus, labels, accessible errors, safe escaping, and valid navigation are verified.
- No migrations or dependency changes are introduced.

## Checks to run

From the repository root, with the local `DJANGO_SECRET_KEY` configured in `.env` or the process environment, run:

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`
4. Run focused tests for the management command and recruiter views/forms if test modules are separated; avoid redundant suite runs.

Report exact results and any checks not run. Do not run migrations unless a newly approved schema change makes them necessary; this prompt expects none.

## Exact manual test steps

1. Run the three Django checks above and confirm no pending migrations.
2. On a fresh local database, run `uv run python manage.py seed_data` twice. Confirm both runs complete without duplicate departments/jobs or account changes. Confirm the test recruiter is staff and can log in with `recruiter` / `password123`.
3. Start the server with `uv run python manage.py runserver`.
4. Visit `/recruiter/` anonymously and confirm redirect to `/login/` with a safe `next` value. Sign in as the seeded recruiter and confirm the four dashboard metrics and links.
5. Sign in as an authenticated non-staff user and confirm `/recruiter/`, `/recruiter/applications/`, job creation, status updates, note submission, and resume delivery all return 403 or otherwise deny access.
6. As staff, create an active and inactive job through `/recruiter/jobs/create/`; confirm valid saves and invalid form errors. Confirm the public job board continues to expose only active jobs.
7. Create or submit applications with multiple stages, including multiple applications from one candidate. Confirm all four metric definitions and pipeline values, including that Total Applicants counts application submissions.
8. Change an application's status through the selector. Confirm valid stages persist, forged status values are rejected, and an unrelated application remains unchanged.
9. Submit a valid interview note for an application. Confirm rating validation, notes, signed-in interviewer attribution, submission timestamp, CSRF enforcement, and that tampering cannot change the associated application.
10. Test a valid PDF and DOCX resume through the staff-only route. Confirm staff-only access, no public resume URL, and safe handling of missing resumes.
11. Check login, job form, dashboard, pipeline, and note drawer at narrow and wide viewport widths. Navigate with keyboard only and verify focus, labels, accessible errors, and responsive table behavior.
12. Confirm `/`, `/tracker/`, `/jobs/`, existing application submissions, and `/admin/` still work; verify no dead logout/account links or unresolved URL names.
13. Stop the development server after verification.

Do not implement this prompt until the user explicitly approves it.
