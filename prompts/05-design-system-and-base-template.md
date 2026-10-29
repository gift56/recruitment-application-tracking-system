# Implementation Prompt: Design System and Base Template

## Goal

Create the first reusable visual shell for the recruitment-tracking application: a responsive, accessible base template and modular navbar, Django message alerts, application-status badge, and footer partials. This is a presentation-only foundation; do not build product views or imply that planned routes, authentication flows, or policy pages already exist.

## Skills read

- No Tailwind-specific skill is available in the current workspace. Follow the project guidance in `AGENTS.md` and the requirements in this prompt.

## Existing code inspected

- `AGENTS.md` — project conventions, verified environment, template organization, and checks.
- `README.md` — current implementation status, roadmap, setup, and security limitations.
- `core/settings.py` — `APP_DIRS=True`, request/auth/messages context processors, static URL, and current settings.
- `core/urls.py` and `tracker/urls.py` — admin is mounted; the tracker namespace currently has no endpoints.
- `tracker/models.py` — application stage values and display labels.
- `tracker/tests.py` — current Django test conventions.
- The project has no existing templates, Tailwind build pipeline, or icon dependency.

## Decisions and assumptions

- Implement only templates and focused template tests. Do not add views, URL patterns, authentication behavior, models, settings, dependencies, or a frontend build pipeline.
- Store the shared shell at `tracker/templates/tracker/base.html` and partials under `tracker/templates/tracker/partials/` so every template name remains app-namespaced and avoids collisions.
- Use the Tailwind CDN for this initial local-development scaffold, with a clear note in the template that it is not the production asset strategy. Do not add dependencies. Use inline SVG for simple icons rather than adding an icon package.
- Use the actual `Application.Status` values (`applied`, `screening`, `interview`, `offer`, `hired`, `rejected`) and their Django display labels.
- The requested job-board, pipeline, dashboard, job-create, account, logout, and policy destinations do not currently exist. Render navigation/actions only when a corresponding route exists; do not add fake links, unresolved `{% url %}` calls, or unrelated endpoints. Show account controls only for an authenticated user, and include a logout action only if an actual logout route is configured.
- Read Django messages from the existing messages context processor. Support success, error, warning, and info message levels.
- Keep candidate records, resumes, and other private data out of the shared layout.

## Files likely to change

- `tracker/templates/tracker/base.html` — document shell, Tailwind CDN hook, content/title blocks, shared partial includes, and page landmarks.
- `tracker/templates/tracker/partials/navbar.html` — responsive brand/navigation and only currently routable actions.
- `tracker/templates/tracker/partials/alerts.html` — accessible, dismissible Django messages.
- `tracker/templates/tracker/partials/status_badge.html` — escaped badge for each application stage plus a neutral fallback.
- `tracker/templates/tracker/partials/footer.html` — compact footer; include policy links only if matching routes exist.
- `tracker/tests.py` or a focused `tracker/tests/` module — template loading/rendering and badge/message coverage.

## Implementation requirements

1. Build a semantic page shell with `header`, `nav`, `main`, and `footer` landmarks; provide overridable title/content blocks and include the shared partials without duplicating markup.
2. Use a restrained light SaaS visual system: slate-neutral page background, white bordered surfaces, indigo primary accents, charcoal primary text, muted secondary text, and a system sans-serif stack. Keep typography scannable and spacing consistent.
3. Make the layout responsive and usable by keyboard. Provide visible focus styles, accessible names for icon-only controls, and appropriate message roles (`role="alert"` for errors and `role="status"` for routine updates).
4. Render Django messages with distinct success, error, warning, and info treatments. Provide a real dismiss action; any JavaScript must be small, scoped to the alert control, and must not interpolate message content.
5. Render a status badge for all six `Application.Status` values using the requested stage colors (blue, purple, amber, indigo, emerald, and rose). Include a neutral fallback for unexpected values. Rely on Django template autoescaping; do not mark status or other dynamic content safe.
6. Use `request.user` only for conditional account presentation. Do not expose a nonfunctional logout/account action or link to a route that is not configured.
7. Keep page-specific content in child templates and reusable UI in the partials directory. Do not add a page, route, or endpoint solely to preview the shell.
8. Add focused tests that load and render the base template and badge for every known stage, exercise the unknown-stage fallback and message variants, and confirm rendering does not require the not-yet-implemented feature routes.
9. Keep the template useful without client-side interaction where possible, and ensure the alert dismiss control is only included when its behavior is implemented.

## Security requirements

- Preserve Django autoescaping; do not use `safe`, `mark_safe`, or raw interpolation for message text, usernames, status labels, or other dynamic values.
- Do not display candidate/application details or resume links in global navigation, alerts, or the footer.
- Do not add state-changing forms. If a form becomes necessary within this approved scope, include `{% csrf_token %}` and do not invent an endpoint.
- Do not add external scripts beyond the explicitly approved Tailwind CDN. Keep all status colors and icon markup fixed in the templates.

## Acceptance criteria

- The base template and four requested partials exist at the namespaced paths described above and can be loaded by Django's app template loader.
- The shared layout is responsive, semantically structured, and keyboard-accessible, with consistent typography, surface, and color treatments.
- All six application statuses render with the specified colors; unknown values render safely with a neutral style.
- Django messages render for success, error, warning, and info, and the dismiss control works without injecting dynamic content into JavaScript.
- The templates do not raise `NoReverseMatch`, present dead links, create fake auth controls, or claim unimplemented routes are available.
- Focused template tests and required Django checks pass. No database migration is needed.

## Checks to run

Run from the repository root with `uv run` and the local `DJANGO_SECRET_KEY` configured in `.env` or the process environment. Never print or commit the secret.

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`

Report the exact results. No migration should be created for this template-only feature.

## Exact manual test steps

1. Run the checks above and confirm they pass.
2. Start the server with `uv run python manage.py runserver`; confirm there are no template syntax errors during startup or rendering.
3. Load the base template from a Django test or shell and confirm the page shell and partials render without unresolved URL errors.
4. Render each application status and an unexpected status; confirm the correct badge treatment and escaped text.
5. Render success, error, warning, and info messages; confirm each has the expected styling and accessible role, and dismiss each alert using its control.
6. Check the layout at narrow and wide viewport widths and navigate interactive controls with the keyboard, verifying visible focus.
7. Confirm no links point to unimplemented job, pipeline, dashboard, account, logout, or policy routes.
8. Stop the development server after verification.

Do not implement this prompt until the user explicitly approves it.
