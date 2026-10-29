# Implementation Prompt: Root Route and Temporary Home

## Goal

Wire the tracker app into the site root so `http://127.0.0.1:8000/` no longer returns a 404. Add a minimal temporary home view in `tracker/urls.py` and an app template that uses the shared RecruiterHub layout. The public job board is not implemented, so this feature must not redirect to or pretend to provide a job-board endpoint.

## Skills read

- `.agents/skills/django-views` — function-based views and URL configuration.
- `.agents/skills/architect` — align routing behavior with the current app structure and avoid coupling the landing page to future features.

## Existing code inspected

- `AGENTS.md` — current project status, template conventions, approval workflow, and security requirements.
- `README.md` — confirms the public job board is planned and not yet implemented.
- `core/urls.py` — currently mounts the admin and tracker URLconf at `/tracker/`.
- `tracker/urls.py` — declares `app_name = 'tracker'` but currently has no URL patterns.
- `tracker/templates/tracker/base.html` and partials — existing shared page layout, navigation behavior, alerts, and footer.
- `tracker/models.py` — job postings exist as models but no public listing view or job-board endpoint exists.
- `tracker/tests.py` — existing test classes and conventions; add focused URL/view coverage here unless a more appropriate test module is established.
- `core/settings.py` — `APP_DIRS=True` and request context processor are enabled for app templates.

## Decisions and assumptions

- Implement only the root route and a temporary, public, read-only landing page. Do not add models, migrations, forms, auth flows, a job board, or recruiter functionality.
- Add the requested `path('', include('tracker.urls'))` to `core/urls.py`, preserving the existing admin and `/tracker/` inclusion unless tests or Django's URL namespace behavior require a narrowly scoped adjustment.
- Use a simple function-based view because the home page is a one-off static response.
- Render a small template under `tracker/templates/tracker/` that extends `tracker/base.html`, with a clear statement that the recruitment workspace is under development. Do not query or expose candidate, application, or resume data.
- Give the root route a stable name within the `tracker` app namespace. Verify reverse resolution returns `/` and that the existing `/tracker/` namespace remains valid.
- Do not add a redirect to `/jobs/` or another route that does not currently exist. The job board remains a future feature.
- Preserve the shared layout's existing behavior; do not make current navbar links or account controls point to nonexistent features.

## Files likely to change

- `core/urls.py` — include `tracker.urls` at the site root.
- `tracker/urls.py` — add a named root pattern and import the home view.
- `tracker/views.py` — add the minimal home function-based view.
- `tracker/templates/tracker/home.html` — render the temporary landing content using the shared base template.
- `tracker/tests.py` or a focused tracker URL/view test module — cover URL resolution, response, and template rendering.
- `README.md` — after implementation, update current capabilities and project structure to mention the temporary root landing page while keeping the job board labeled planned.

## Implementation requirements

1. Mount the tracker URLconf at the empty path in `core/urls.py` using Django's `include`.
2. Keep the existing `/admin/` route and `/tracker/` URLconf mount working; avoid introducing ambiguous named route behavior. If multiple inclusions of the same app namespace create reverse ambiguity, resolve it with the smallest clear URL configuration adjustment and document the impact in tests.
3. Implement a GET-only, public home view that renders the app-namespaced temporary landing template. Do not add database queries or accept state-changing requests.
4. Extend `tracker/base.html` in the landing template and present concise, honest copy that the job board is not available yet. Do not invent page content beyond the temporary site entry point.
5. Add a focused test that uses Django's test client to GET `/`, asserts a successful response and the intended template, and verifies the page does not raise template or reverse-resolution errors.
6. Add URL-resolution tests confirming the named root URL reverses to `/` and admin URLs remain resolvable. Check that the existing `/tracker/` URL configuration behaves as intentionally retained after the root include.
7. Keep this feature unauthenticated and read-only; do not expose stored candidate or application data.
8. Update `README.md` after implementation to describe the temporary landing page as implemented and the public job board as planned. Do not treat this implementation prompt as evidence that the route already exists.

## Security requirements

- The home page must not display candidate records, applications, resumes, or other sensitive data.
- Do not introduce forms, mutations, file handling, raw SQL, new credentials, or authentication configuration.
- Use Django template autoescaping and existing template loader conventions.
- Do not add links to non-existent job-board, account, logout, recruiter, or policy endpoints.

## Acceptance criteria

- A GET request to `/` returns HTTP 200 and renders the temporary home template using the shared base layout.
- Root URL reversal returns `/` through the intended tracker namespace without disrupting admin URL resolution.
- The existing `/tracker/` URL configuration remains available or any necessary adjustment is explicitly covered by tests.
- No redirect points to an unimplemented job board, and no candidate/application data is displayed.
- Focused tracker tests and the required Django checks pass; no migration is created.
- `README.md` accurately distinguishes the implemented temporary root page from the planned job board.

## Checks to run

Run from the repository root with `uv run` and the local `DJANGO_SECRET_KEY` configured in `.env` or the process environment. Never print or commit the secret.

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`

Report exact results. No migration should be needed for URL/view/template changes.

## Exact manual test steps

1. Run the checks above and confirm they pass.
2. Start the server with `uv run python manage.py runserver`.
3. Open `http://127.0.0.1:8000/` and confirm the temporary landing page renders instead of a 404.
4. Confirm the page uses the shared layout and says the job board is not yet available; verify it does not advertise nonexistent routes.
5. Open `http://127.0.0.1:8000/admin/` and confirm the admin route remains reachable.
6. Check the existing `/tracker/` mount behaves as intended after adding the root include.
7. Stop the development server and confirm no migrations were created.

Do not implement this prompt until the user explicitly approves it.
