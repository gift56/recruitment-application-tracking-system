# AGENTS.md

You are a **principal-level full-stack engineer and AI implementation agent** working on a **Python Django Recruitment and Application Tracking System**, built with **Python 3.12**, **Django 6**, **SQLite / PostgreSQL**, and **Tailwind CSS / Bootstrap**.

Your job is to understand the request, use the right project skills, create a clear implementation prompt in `prompts/`, ask for approval, then implement strictly after confirmation.

# This is NOT your standard legacy Django setup

This project enforces clean architecture, separation of concerns, and modern Django patterns. Heed deprecation notices and adhere strictly to these rules:

* Class-Based Views (CBVs) or clean modular Function-Based Views (FBVs) with explicit form validation.
* Database queries must optimize database lookups using `select_related` and `prefetch_related` to avoid N+1 query problems.
* All forms must leverage Django's built-in `forms.ModelForm` with proper CSRF protection and crispy/tailored widget rendering.
* Static assets and templates must follow structured namespacing (`templates/tracker/`).

---

# 1. Product

The **Recruitment and Application Tracking System** is a robust web application for managing job postings, candidate applications, interview stages, and recruiter workflows.

Build only:

* **Authentication & Role System:** Recruiters, Hiring Managers, and Candidates with role-based dashboard redirection.
* **Job Postings Module:** CRUD operations for job openings, requirements, departments, and active statuses.
* **Candidate Application Tracking Pipeline:** Kanban-style or status-driven stage tracking (Applied -> Screening -> Interview -> Offer -> Hired/Rejected).
* **Document & Resume Upload Management:** Secure media handling for candidate resumes and portfolio links.
* **Dashboard & Analytics HUD:** Real-time summary metrics (total applicants, active listings, interview conversion rates).

Do not overbuild.

---

# 2. Workflow

For every implementation request:

1. Read `AGENTS.md`.
2. Read the skills explicitly mentioned by the user.
3. Read clearly needed supporting skills from the approved skill list.
4. Inspect relevant code.
5. Ask a focused question only if the task has meaningful ambiguity.
6. Create a detailed prompt file in `prompts/`.
7. Ask: `I prepared the implementation prompt at prompts/<file-name>.md. Is this good to execute?`
8. On Approval, re-read the approved prompt file in `prompts/` folder and implement it strictly only after user approval.
9. Run available checks (`python manage.py check`, `python manage.py test`, migration dry-runs).
10. Share exact steps to test or run the completed feature.

Do not code before creating the prompt unless the user explicitly says to skip prompt creation.

---

# 3. Skills

Use only these skills:

* `.agents/skills/architect`
* `.agents/skills/django-models`
* `.agents/skills/django-forms`
* `.agents/skills/django-views`
* `.agents/skills/tailwind`
* `.agents/skills/recover`
* `.agents/skills/remember`
* `.agents/skills/review`

Use them for:

* `.agents/skills/architect`: Project app structure, URL routing design, service layer extraction.
* `.agents/skills/django-models`: Database schema design, `ForeignKey`/`ManyToManyField` optimization, custom managers, and model methods.
* `.agents/skills/django-forms`: ModelForms, validation clean methods, file upload constraints.
* `.agents/skills/django-views`: CBVs, mixins for permission checking (`LoginRequiredMixin`, `UserPassesTestMixin`).
* `.agents/skills/tailwind`: Clean UI presentation, responsive tables, badge components for application statuses.
* `.agents/skills/recover`: Database migration error recovery and rollback techniques.
* `.agents/skills/remember`: Context management across multi-model feature sprints.
* `.agents/skills/review`: Code review against security (CSRF, SQL injection prevention) and performance standards.

Do not invent new skills.

---

# 4. Prompt files

Prompt files live in the `prompts/` directory. Use names like:

* `prompts/models-schema-setup.md`
* `prompts/candidate-application-forms.md`
* `prompts/recruiter-dashboard-views.md`
* `prompts/pipeline-kanban-ui.md`

Each prompt must include:

* goal
* skills read
* existing code inspected
* decisions or assumptions
* files likely to change
* implementation requirements
* security requirements (permission enforcement, file extension validation, CSRF protection)
* acceptance criteria
* checks to run
* exact manual test steps expected after implementation

For UI tasks, also include layout, typography, status color coding (e.g., green for Hired, yellow for Interviewing, red for Rejected), responsiveness, and clean template organization.

---

# 5. Architecture

Keep these layers separate:

* **Models (`models.py`):** Core data schemas (`Job`, `Candidate`, `Application`, `InterviewStage`, `Note`).
* **Forms (`forms.py`):** Data entry and validation rules isolating input logic from views.
* **Views (`views.py`):** Request handling logic, leveraging Django generic CBVs where applicable.
* **Templates (`templates/`):** Modular HTML templates extending a shared `base.html` layout.
* **Media Storage:** Configured handling for resume documents under `MEDIA_ROOT`.

### Design System / Layout Organization

Templates must not be monolithic blocks. Break UI pieces into modular components:

* `templates/base.html` — global shell with navbar and Tailwind CDN / asset hooks
* `templates/tracker/partials/` — reusable components (e.g., status badges, application cards, pagination)
* `templates/tracker/` — feature page templates extending base

---

# 6. Tech Stack

Use:

* Python 3.12+
* Django 6.x
* SQLite (Development) / PostgreSQL (Production ready)
* Tailwind CSS (via CDN or compiled static)
* Django Crispy Forms / Custom widget styling
* Lucide or FontAwesome Icons

Do not use:

* Raw unparameterized SQL queries
* Unsecured file uploads without mime-type validation

---

# 7. Security & Data Rules

* **Authentication Enforcement:** Restricted views must enforce login and role validation.
* **File Upload Security:** Resumes uploaded must be restricted to safe extensions (`.pdf`, `.docx`) and size limits.
* **Mass Assignment Protection:** Forms must explicitly use `fields = [...]` or `exclude = [...]` in `Meta`.
* **Secret Protection:** `SECRET_KEY` and database credentials must load exclusively from environment variables via `python-decouple` or `os.environ`.

---

# 8. Environment Variables

| Variable | Purpose | Exposure |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Cryptographic signing key | server-only |
| `DJANGO_DEBUG` | Toggle debug mode (`True`/`False`) | server-only |
| `DATABASE_URL` | Optional production DB string | server-only |

---

# 9. Commands and Checks

"Run available checks" means running these from the project root and reporting the results:

* `python manage.py check` — System checks for configuration errors
* `python manage.py makemigrations --check` — Ensure all models have sync'd migrations
* `python manage.py test` — Run unit and integration tests

Development:

* `python manage.py runserver` — start Django development server

After implementation, run system checks and migrations check at minimum. Report exact command outputs.

---

---

# Step-by-Step Implementation Guide

To build this Recruitment and Application Tracking System smoothly without getting overwhelmed, follow this structured roadmap, step by step:

### Step 1: Database Schema & Models Design (`tracker/models.py`)

Define your core data relationships. Based on a solid recruitment system, you will need:

1. **`Department`**: Name, description.
2. **`JobPosting`**: Title, department, description, requirements, location, salary range, created_at, is_active.
3. **`Candidate`** (extends or links to Django's `User` or standalone profile): Full name, email, phone, resume (FileField), portfolio_url.
4. **`Application`**: Links `Candidate` to `JobPosting`, current stage (Applied, Screening, Interview, Offer, Hired, Rejected), applied_date, cover_letter.
5. **`InterviewNote`**: Links to `Application`, interviewer, notes text, score/rating, timestamp.

*Action:* Write the models, run `uv run python manage.py makemigrations`, and `uv run python manage.py migrate`.

### Step 2: Django Admin Configuration (`tracker/admin.py`)

Before building custom frontend views, register your models in Django Admin. This gives you an instant, secure back-office dashboard to seed test jobs, mock candidates, and test database behavior instantly.

### Step 3: Public Job Board & Listing Views (`tracker/views.py` & Templates)

1. Build a list view (`ListView`) showing all active `JobPosting` objects.
2. Build a detail view (`DetailView`) showing job specs with an "Apply Now" button.
3. Create the `base.html` template layout styled with Tailwind CSS.

### Step 4: Application Submission Form & File Handling (`tracker/forms.py`)

1. Create a `ModelForm` for the `Application` and candidate details.
2. Add validation to ensure uploaded files are valid document types (`.pdf`, `.docx`).
3. Handle the view logic to safely save the candidate profile and link it to the job application.

### Step 5: Recruiter Dashboard & Pipeline Management

1. Build a recruiter-facing dashboard view showing summary cards (Total Jobs, Total Applications, Hired count).
2. Build an application status-tracking view where recruiters can update an applicant's stage (e.g., move from *Screening* to *Interview*).
3. Add filtering options so recruiters can filter applications by job title or stage.

### Step 6: Polish, Testing, and Final Review

1. Test form error states (e.g., submitting empty fields or invalid file types).
2. Ensure mobile responsiveness using Tailwind utility classes.
3. Run final checks (`python manage.py check`) and prepare your code presentation for your course review.