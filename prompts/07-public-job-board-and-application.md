# Implementation Prompt: Public Job Board and Candidate Application

## Goal

Replace the temporary home page with a public recruitment landing page and implement the candidate-facing active job board, active job details, and application submission flow. Keep the existing recruitment models and resume security validation; do not add authentication, new models, migrations, dependencies, or recruiter functionality.

## Skills read

- `.agents/skills/architect` — align feature behavior and routing with existing project structure.
- `.agents/skills/django-views` — use namespaced URLs and generic class-based list/detail/create views where appropriate.
- `.agents/skills/django-forms` — use a `ModelForm`, centralize validation, and display field and non-field errors.
- No Tailwind-specific skill is available in this workspace; follow the existing namespaced templates and Tailwind utility styling.

## Existing code inspected

- `AGENTS.md` — project status, approval workflow, Django conventions, security requirements, and required checks.
- `README.md` — current capability claims, planned features, local setup, and project structure.
- `tracker/models.py` — `Department`, `JobPosting`, `Candidate`, and `Application` fields and relationships; `JobPosting.Status.ACTIVE`; `Candidate.resume` validation; `MAX_RESUME_SIZE` (5 MiB); and `validate_resume_file` content checks.
- `tracker/views.py` — current GET-only `home` function rendering the temporary home template.
- `tracker/urls.py` and `core/urls.py` — namespaced root route and existing `/tracker/` mount.
- `tracker/forms.py` — does not currently exist.
- `tracker/templates/tracker/home.html` — current temporary landing page.
- `tracker/templates/tracker/base.html` and `tracker/templates/tracker/partials/` — shared Tailwind shell, alert display, navigation, and footer.
- `tracker/tests.py` — existing model, upload-validation, template, admin, and home-route tests.
- `prompts/05-design-system-and-base-template.md` and `prompts/06-models-and-wiring.md` — prior implementation prompt conventions.

## Decisions and assumptions

- “Active” means `JobPosting.status == JobPosting.Status.ACTIVE`; only active postings may appear in public listings, homepage recommendations, job details, or application forms. Inactive and nonexistent job detail/application URLs return 404.
- “Recent” means newest `created_at` first. The homepage shows exactly the four newest active jobs, or fewer when fewer than four exist.
- Search uses a GET query parameter named `q` on `/jobs/` and matches job title or location case-insensitively. Department filtering uses a GET query parameter named `department` containing the department primary key. Search and department selection can be combined; filtering and pagination must retain relevant query parameters.
- Department filter tabs represent departments with active jobs, plus an “All jobs” option.
- The application form collects `Candidate.full_name`, `Candidate.email`, optional `Candidate.phone`, `Candidate.resume`, optional `Candidate.portfolio_url`, and optional `Application.cover_letter`. Resume remains optional to match `Candidate.resume.blank=True`; when provided, it must pass the existing extension, size, and content validation.
- A successful public submission creates a new Candidate and a linked Application with its model-default `Applied` status. Do not add candidate deduplication or an authentication requirement.
- Use Post/Redirect/Get after a valid submission and show a success message on the active job detail page. Do not create another success route or a new template solely for confirmation.
- Preserve the existing root URL and `/tracker/` mount behavior and namespaces. The tracker URLconf is mounted at both prefixes, so its patterns remain reachable under both mounts; ensure navbar links and root-facing redirects use the root `tracker` namespace.
- Reuse the current Tailwind CDN and visual conventions in `tracker/base.html`; do not add a dependency or asset pipeline.

## Files likely to change

- `tracker/views.py` — implement `HomeView`, `JobListView`, `JobDetailView`, and `ApplicationCreateView`.
- `tracker/urls.py` — add named job list, detail, and application routes while preserving the home route.
- `tracker/forms.py` — add `ApplicationForm` with explicit `Meta.fields` and resume validation.
- `tracker/templates/tracker/home.html` — hero, search, recent job cards, and browse-all action.
- `tracker/templates/tracker/job_list.html` — search, department filters, job-card grid, pagination, and empty states.
- `tracker/templates/tracker/job_detail.html` — active job description and specifications with an application action.
- `tracker/templates/tracker/apply.html` — accessible multipart application form and validation errors.
- `tracker/templates/tracker/partials/navbar.html` — link the brand to `/` and “Job Board” to `/jobs/`.
- `tracker/tests.py` or a focused module under `tracker/tests/` — cover routes, filtering, active-only visibility, uploads, submissions, and templates using existing test conventions.
- `README.md` — after implementation, report the delivered public job board and candidate submission flow accurately, distinguish remaining planned work, and update the project structure.
- `AGENTS.md` — after implementation, update only the factual project-status statements that say the job board and candidate application flow are still unimplemented.

## Implementation requirements

1. **Home page**
   - Replace the temporary home response with a `HomeView` served at `/`; preserve GET-only behavior.
   - Query active jobs ordered by newest creation time, limited to four, and use `select_related('department')`.
   - Render a responsive hero with a GET search form targeting the namespaced job list route and a prominent “Browse All Jobs” link.
   - Follow the hero with a “Featured / Recent Jobs” card grid. Each card should show job title, department, location, and salary when provided, and link to that active job’s detail page.
   - Handle zero active jobs gracefully without implying that jobs are available.

2. **Public job board and details**
   - Add `JobListView` at `/jobs/`. Show active postings only, ordered newest first, with `select_related('department')`.
   - Support `q` title/location search and a `department` filter. Validate filter values through ORM lookups; invalid or unknown departments should yield a safe empty result or be ignored consistently, not raise an uncaught error.
   - Provide department tabs for departments with active jobs and an “All jobs” tab. Preserve active search/filter selections in links and pagination.
   - Paginate the job listing (12 jobs per page) and render a useful empty state for no matching jobs.
   - Add `JobDetailView` at `/jobs/<int:pk>/`. Its queryset must contain active postings only and `select_related('department')`. Show description, requirements, department, location, optional salary range, and an “Apply Now” link to the corresponding application route.
   - Add `ApplicationCreateView` at `/jobs/<int:pk>/apply/`. It must be public, accept only an active posting, render `apply.html`, and bind submitted files via `request.FILES`.
   - On valid submission, save the Candidate and its Application association as one atomic operation. Set the job posting explicitly, leave status at the existing `Applied` default, provide a success message, and redirect to the active job detail page. Invalid input must re-render the bound form and all validation errors.

3. **Application form and resume security**
   - Create `ApplicationForm` as a `forms.ModelForm` for `Application`, with an explicit `Meta.fields` allowlist containing only the candidate-input fields listed above and `cover_letter`. Do not expose `candidate`, `job_posting`, `status`, or timestamps as editable form fields.
   - Declare candidate fields not native to `Application` on the form and implement a clear save path that creates the Candidate and linked Application without an orphaned candidate if application saving fails.
   - Reuse `validate_resume_file` from `tracker.models` for uploaded files. Do not duplicate or weaken the model's `.pdf`/`.docx`, 5 MiB, and document-content checks. Display resume errors beside the resume control.
   - Keep `resume` optional to match the model; validate it whenever a file is provided.
   - Use Django's normal CSRF middleware and include `{% csrf_token %}` in every POST form. The application form must use `enctype="multipart/form-data"`.

4. **Templates, navigation, and accessibility**
   - Keep templates in `tracker/templates/tracker/` and extend `tracker/base.html`.
   - Use semantic headings, labels, buttons, and links; ensure keyboard access, visible focus states, and responsive layouts at narrow and wide widths.
   - Follow the existing slate/white/indigo design, consistent typography, clean spacing, and card styling. Do not introduce status color semantics that are unrelated to the public hiring pages.
   - Show every form field's label, help text where appropriate, field errors, and `form.non_field_errors`; ensure errors are associated with their controls and visible after invalid submission.
   - Render user- and database-provided content using normal Django autoescaping. Do not mark descriptions, requirements, or form values safe.
   - Make “Job Board” resolve to the root job-list route and make the RecruiterHub brand/logo resolve to the root home route. Do not add login, account, logout, recruiter, or policy links.
   - Do not expose candidate records, resumes, resume URLs, or application data through public views or templates.

5. **Tests and project documentation**
   - Add focused tests for root and namespaced URL behavior; homepage recent-job ordering/limit and exclusion of inactive jobs; job list search, department filters, pagination, and empty state; active-only detail/application access; and links/forms rendering without `NoReverseMatch`.
   - Test successful anonymous application submission, linked Candidate/Application fields and default status, and invalid form re-rendering without creating records.
   - Test resume validation for valid PDF/DOCX inputs, invalid extensions/content, and files over 5 MiB. Reuse existing upload test helpers where practical.
   - Verify CSRF token presence in the rendered application form. Do not disable CSRF middleware or weaken upload validation to simplify tests.
   - Update README and the factual project status in AGENTS only after the feature is implemented. Do not describe recruiter dashboards, authentication roles, analytics, or other planned functionality as delivered.
   - Do not add models, migrations, dependencies, settings changes, static assets, or media-serving/download routes for this feature.

## Security requirements

- Keep all public listing/detail/application querysets restricted to active jobs; do not expose inactive postings.
- Keep candidate and application data private. Never render, link, or provide a download route for an uploaded resume.
- Keep the candidate/job/status/timestamp associations out of user-editable fields; explicitly set relationships and use the model's default application status.
- Preserve the existing resume extension, size, and content validation exactly; do not trust a browser-provided MIME type as a substitute.
- Use a database transaction for linked Candidate/Application creation and report validation/save errors normally; do not silently discard failures.
- Keep Django CSRF protection enabled for the application POST and use escaped Django template output.
- Do not use raw SQL, add credentials, introduce authentication routes, or add unrelated security infrastructure.

## Acceptance criteria

- `/` renders a responsive public landing page with a working title/location search form, no more than four newest active jobs, and a working “Browse All Jobs” action.
- `/jobs/` lists only active jobs, supports combined search and department filters, retains filter state through pagination, and handles no-result states.
- `/jobs/<int:pk>/` shows full public specifications for an active job and returns 404 for inactive or nonexistent jobs.
- `/jobs/<int:pk>/apply/` accepts anonymous applications only for active jobs and creates one linked Candidate/Application pair on valid submission.
- The form has explicit allowed fields, visible validation errors, CSRF protection, multipart encoding, and reuse of the existing resume validation for PDF/DOCX up to 5 MiB.
- Existing root and `/tracker/` routes, namespaces, admin behavior, shared template shell, and prior tests remain intact.
- Navigation links point to real root-facing routes. No public page exposes candidate/application data or resume content.
- README and AGENTS accurately distinguish implemented behavior from still-planned product features.
- No migration or dependency change is introduced; all required checks pass.

## Checks to run

Run from the repository root with `uv run` and the local `DJANGO_SECRET_KEY` configured in `.env` or the process environment. Never print or commit secret values.

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`

Report the exact results. No migration should be needed.

## Exact manual test steps

1. Create a few departments and active job postings with different titles, locations, salary ranges, and creation times in Django admin. Also create an inactive posting.
2. Run the three checks above and confirm they pass with no pending model migrations.
3. Start the server with `uv run python manage.py runserver`.
4. Open `http://127.0.0.1:8000/`. Confirm the hero and recent-job cards render, only the four newest active postings are shown, and “Browse All Jobs” opens `/jobs/`.
5. Submit the homepage search for a known title or location; confirm the job board shows matching active postings.
6. On `/jobs/`, select a department and combine it with a search term. Confirm only matching active jobs appear and the selected filters remain selected when moving between pages.
7. Open an active job detail page and confirm the department, location, requirements, description, salary when present, and “Apply Now” action. Request the inactive job URL and confirm it returns 404.
8. Open the application page as an anonymous visitor. Confirm labels, CSRF token, multipart form encoding, file input, and field-level errors are present and accessible.
9. Submit a valid application with no resume, then submit another with a valid PDF or DOCX under 5 MiB. Confirm each success message, redirect, and linked Candidate/Application records with status Applied.
10. Submit invalid files (wrong extension, malformed PDF/DOCX, and a file larger than 5 MiB) and invalid required candidate data. Confirm errors are shown and no Candidate/Application is created for invalid submissions.
11. Confirm candidate details and uploaded resume URLs are not shown on public pages, the brand links to `/`, and “Job Board” links to `/jobs/`.
12. Check the home, listing, detail, and application pages at narrow and wide viewport widths and navigate interactive controls with the keyboard, verifying visible focus.
13. Confirm `/tracker/`, its existing namespace reversal, and `/admin/` remain available. Stop the development server after verification.

Do not implement this prompt until the user explicitly approves it.
