# Implementation Prompt: Salary Ranges, Departments, and Job Management

## Status

Implemented and validated. Do not expand scope beyond this prompt.

## Goal

Make compensation information consistently visible on public job listings, let staff recruiters add departments from the portal, and provide a complete recruiter workflow to list, edit, and delete job postings. Preserve existing job/application records, public browsing behavior, staff authorization, and the model's protection against deleting jobs referenced by applications.

## Skills read

- `.agents/skills/architect` — resolve product language and decisions before implementation.
- `.agents/skills/django-forms` — use model-backed forms, explicit field allowlists, and field-level validation.
- `.agents/skills/django-views` — use generic create/update/list/delete patterns and route authorization.
- `.agents/skills/imprint` — preserve and update the established UI registry after adding recruiter UI.

## Existing code inspected

- `AGENTS.md` — project workflow, approval requirements, staff access, templates, validation, and verification commands.
- `README.md` — current public job-board and recruiter capabilities.
- `prompts/08-recruiter-dashboard-and-pipeline.md` — approved recruiter implementation and existing authorization/design decisions.
- `tracker/models.py` — `Department.name` and optional description; `JobPosting.salary_range` is a `CharField(blank=True)`; `Application.job_posting` uses `on_delete=PROTECT`.
- `tracker/forms.py` — `JobPostingForm` explicitly allows title, department, location, salary range, description, requirements, and status; shared control styling helper is available.
- `tracker/views.py` and `tracker/urls.py` — public job board/detail/home routes, recruiter job creation, staff-only access mixin, and root URL namespace.
- `tracker/templates/tracker/job_list.html` — public cards show salary only if `salary_range` is nonempty.
- `tracker/templates/tracker/job_detail.html` — job detail also conditionally shows salary only when present.
- `tracker/templates/tracker/home.html` — featured cards conditionally show salary when present.
- `tracker/management/commands/seed_data.py` — three sample jobs are created with `get_or_create`; currently they do not set salary ranges, and reruns do not update existing rows.
- `tracker/tests.py` — public job-board and recruiter tests, including job creation and seed-command coverage.
- `ui-registry.md` — established slate/white/indigo recruiter UI patterns.

## Language and decisions

- **Price range:** the existing `JobPosting.salary_range` field; present it as a clearly labeled salary range on the public homepage cards, job-board cards, and job detail page.
- **Salary requirement:** recruiter create and edit forms require a salary range so newly managed postings include compensation. No database schema change is requested; existing records with empty values remain valid and public pages must communicate missing values rather than silently omit the field.
- **Add departments:** an authenticated staff recruiter can create a persistent `Department` with a name and optional description in the recruiter portal, then select it when creating or editing a posting. The add-department action is a separate accessible page linked from the job form; after saving, return to job creation, where the new department is available.
- **Edit jobs:** staff can update all existing job-posting fields (title, department, location, salary range, description, requirements, and status).
- **Delete jobs:** staff can permanently delete a posting only when it has no applications. The confirmation flow must explain the action. If applications reference it, block deletion and explain that the recruiter can mark the job Inactive instead. Preserve the existing `PROTECT` behavior and linked application history.
- **Department names:** trim whitespace and reject case-insensitive duplicate department names through form validation. Do not add a database migration solely for department uniqueness.
- **Existing seeded postings:** seed jobs receive sample salary ranges. On reruns, fill a salary range only when a known sample job's existing range is blank; preserve any salary value a recruiter has already set.
- **No incidental scope:** do not add a department edit/delete workflow, new roles, APIs, routes unrelated to these features, dependencies, or schema changes.

## Files likely to change

- `tracker/forms.py` — add `DepartmentForm`, make salary range required on `JobPostingForm`, and validate duplicate department names.
- `tracker/views.py` — add staff-only department creation, recruiter job listing, job editing, and safe delete-confirmation views.
- `tracker/urls.py` — add named department-create, recruiter job-list, job-edit, and job-delete routes.
- `tracker/management/commands/seed_data.py` — add compensation ranges to samples and conditionally fill blank ranges on existing seeded records.
- `tracker/templates/tracker/job_list.html`, `home.html`, and `job_detail.html` — label salary ranges consistently and handle legacy blank values explicitly.
- `tracker/templates/tracker/job_form.html` — expose a valid route to add a department and explain required salary range.
- `tracker/templates/tracker/recruiter_dashboard.html` — expose the job-management page.
- New namespaced templates under `tracker/templates/tracker/` for recruiter job list, department creation, and delete confirmation.
- `tracker/tests.py` or a focused test module — cover required salaries, public display, department creation/duplicate validation, edit, delete, protected deletion, and seed backfill behavior.
- `README.md` and `AGENTS.md` — update only factual capability statements after the implementation.
- `ui-registry.md` — record added recruiter component patterns without unrelated restyling.

## Implementation requirements

### 1. Public salary-range display

1. On the public home page, job-board cards, and job detail page, show a labeled “Salary range” value whenever one exists.
2. Do not hide the salary row/label for existing postings whose value is blank; render a clear neutral “Not provided” value for legacy records instead of implying a numeric amount.
3. Keep the same visual hierarchy as location and department metadata, with responsive wrapping and existing slate/indigo design tokens.
4. Preserve public visibility rules: only active job postings appear in public listings and details.

### 2. Required recruiter salary entry

1. Keep `salary_range` in `JobPostingForm.Meta.fields` and enforce required input in the recruiter form.
2. If the underlying `ModelForm` field remains optional due to `JobPosting.salary_range.blank=True`, set the form field's `required` property explicitly and provide a clear field error for blank input.
3. Do not alter model schema or create migrations.
4. Retain the entered salary on edit and display it in recruiter job-management rows as useful context.

### 3. Department creation

1. Add `DepartmentForm` as a `ModelForm` with explicit fields `name` and `description`.
2. Trim surrounding whitespace from the name and reject an empty or case-insensitive duplicate name with a field-level validation error. Do not alter existing department names or create a migration.
3. Add a staff-only department-create page and route, for example `/recruiter/departments/create/`.
4. Add a visible “Add department” link from the recruiter job form to this page. On successful creation, show a success message and return to `/recruiter/jobs/create/`; the created department must appear in the selection immediately.
5. On invalid input, retain submitted data and render accessible field/non-field errors. Include CSRF protection.

### 4. Recruiter job listing and editing

1. Add a staff-only recruiter job-management list, for example `/recruiter/jobs/`, containing active and inactive postings with title, department, location, salary range, status, and edit/delete actions.
2. Make management discoverable from the recruiter dashboard and job-creation form without adding dead links.
3. Add a staff-only edit route such as `/recruiter/jobs/<int:pk>/edit/`, reusing `JobPostingForm` and its explicit allowlist. Successful edits show a message and return to the management list; invalid forms preserve their values and errors.
4. A staff recruiter may edit active/inactive status. The public board must continue to expose active postings only.
5. Optimize related department lookups with `select_related('department')` where appropriate.

### 5. Safe job deletion

1. Add a staff-only confirmation page and POST-only deletion action at a named recruiter job-delete route.
2. Explain the permanent action and identify the posting on the confirmation page. Use CSRF protection and do not delete on GET.
3. Show whether applications reference the posting. If there are existing applications, do not offer a working delete submission; explain that the job must be marked Inactive to retain its history.
4. Enforce the application check on POST as well, and handle a concurrent reference safely by catching Django's `ProtectedError`. On a blocked delete, show a clear message without losing the job or applications and return to the job-management list.
5. When no applications reference the job, delete it after confirmation and show a success message.
6. Preserve `on_delete=PROTECT` in the model and do not cascade/delete application, candidate, or interview-note records.

### 6. Seed data

1. Give each of the three known sample jobs a realistic, clearly formatted salary range.
2. Preserve `seed_data` idempotency and its DEBUG guard.
3. On rerun, if a known sample job exists with a blank salary, fill only that blank salary range. Do not overwrite any nonblank value or unrelated job.
4. Add tests proving new seed jobs have salary ranges and existing nonblank salary customizations survive reruns.

### 7. UI, accessibility, and documentation

1. Reuse the current `tracker/base.html`, Tailwind CDN, namespaced templates, slate-neutral background, white rounded-2xl surfaces, indigo actions/focus, typography, and existing focus patterns.
2. Use semantic forms and headings, visible labels, accessible field errors, keyboard-operable controls, responsive management lists, and clear delete warnings.
3. Preserve template autoescaping for department names, job text, and salary values.
4. Do not add fake account or logout links. Keep candidate and resume privacy unchanged.
5. Update `ui-registry.md` for the department form, job-management list, edit form, and delete confirmation. Avoid unrelated design changes.
6. Update `README.md` and `AGENTS.md` after implementation so current capabilities accurately include department creation and job-posting management; note that salary range is required by recruiter create/edit forms while legacy records can remain blank.

## Security and data-integrity requirements

- Every new recruiter page and state-changing action must use the existing staff authorization pattern.
- Use CSRF protection on create, edit, and delete forms. Never permit job deletion by GET.
- Validate department duplicates server-side; never trust a form's department IDs without Django's model-choice validation.
- Preserve `Application.job_posting`'s `PROTECT` semantics; deletion must not erase applicant history.
- Validate job form fields using Django forms and keep a strict `Meta.fields` allowlist.
- Keep job text and salary output autoescaped.
- Do not add schema changes, external dependencies, or production infrastructure.

## Acceptance criteria

- Public home, listing, and detail pages present the salary range with a clear label when populated and an explicit “Not provided” state for legacy blanks.
- New and edited recruiter-managed jobs cannot be saved with an empty salary range.
- Seeded jobs each have a visible sample salary range; rerunning the seed command fills prior blank sample ranges but preserves nonblank recruiter-customized ranges.
- Staff can add a department with optional description and use it immediately in job creation/editing. Duplicate names differing only in case or surrounding whitespace are rejected clearly.
- The recruiter dashboard links to a list containing both active and inactive jobs.
- Staff can edit every allowed job field and receives accessible validation errors for invalid data.
- Staff can delete a job only after confirmation and only when it has no applications. Jobs with applications remain intact and show an actionable explanation to mark inactive.
- Anonymous and non-staff users cannot reach any new recruiter view/action. GET requests never delete.
- Existing public active-only behavior, pipeline history, routes, and resume privacy are preserved.
- No migration or dependency change is introduced.

## Checks to run

From the repository root, with the local `DJANGO_SECRET_KEY` configured:

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`

Report exact results. No migration should be needed; do not run migrations for this feature.

## Exact manual test steps

1. Run the three checks and confirm no pending migrations.
2. As staff, open recruiter job creation. Add a new department and confirm it returns to the job form with the new department selectable.
3. Try creating a department with a duplicate name using different casing and surrounding spaces; confirm an accessible validation error and no duplicate row.
4. Try creating a job without a salary range; confirm the job is rejected with a clear field error. Create one with a salary range.
5. Visit `/`, `/jobs/`, and the new job detail page. Confirm each public location shows a labeled salary range and active-only filtering remains intact.
6. Run `uv run python manage.py seed_data` twice. Confirm all seeded sample jobs have salary ranges and a manually changed nonblank sample salary is preserved.
7. Open the recruiter job list and edit a posting's title, department, salary, description, and status. Confirm successful values persist and errors remain visible for invalid submissions.
8. Open delete confirmation for a job with no applications, verify GET does not delete it, then confirm by POST and verify it is removed.
9. Open delete confirmation for a job with applications. Confirm the page explains why it cannot be deleted; attempt a forged POST and verify the job and all application records remain intact.
10. Repeat access attempts as anonymous and authenticated non-staff users for every new route; confirm redirects/403 behavior.
11. Check the new forms and job-management list at narrow and wide viewport widths, using keyboard navigation and visible focus.
12. Confirm existing public application and recruiter pipeline flows remain usable.

Do not implement this prompt until the user explicitly approves it.
