# Implementation Prompt: Local Environment Configuration

## Goal

Fix local Django startup so `uv run python manage.py runserver` can read `DJANGO_SECRET_KEY` from a project-root `.env` file when no process environment value is set. Keep secrets out of source control, preserve explicit failure when no key is configured, and document that Django commands must run from the project root.

## Skills read

- None. This is a focused settings and local environment configuration fix; no available skill adds needed project-specific guidance.

## Existing code inspected

- `AGENTS.md` — requires secrets to load exclusively from environment variables via `python-decouple` or `os.environ`.
- `core/settings.py` — currently reads `DJANGO_SECRET_KEY` directly from `os.environ` and raises `ImproperlyConfigured` if missing.
- `manage.py` — exists at the project root and sets `DJANGO_SETTINGS_MODULE` to `core.settings`.
- `core/urls.py` — project URL configuration.
- Workspace root — no `pyproject.toml`, requirements file, existing `.env`, or `.gitignore` is present.
- Current `uv` virtual environment — neither `python-dotenv` nor `python-decouple` is installed.

## Decisions and assumptions

- Add `.env` loading without adding a third-party dependency or creating an unrelated package manifest.
- Read only simple `KEY=VALUE` lines from the project-root `.env`; support blank lines and comments, trim surrounding whitespace, and strip matching single or double quotes. Do not execute or evaluate file contents.
- Existing process environment variables take precedence over `.env` values.
- Require a non-empty `DJANGO_SECRET_KEY`; continue to raise `ImproperlyConfigured` with a clear message if it is absent from both sources.
- Add `.env` to `.gitignore` and add a committed `.env.example` with a clearly non-secret placeholder and setup instructions.
- Do not add a real or reusable secret to the repository.
- Explain the second reported error by documenting that `manage.py` must be invoked from the project root, not from inside `tracker`.

## Files likely to change

- `core/settings.py`
- `.gitignore`
- `.env.example`

## Implementation requirements

1. Load `.env` from the directory containing `manage.py`, without relying on the caller's current directory.
2. Do not overwrite any variable already set in the process environment.
3. Ensure the loader handles missing `.env` without error, while malformed non-empty lines fail clearly rather than being silently interpreted.
4. Read `DJANGO_SECRET_KEY` only after loading `.env`; retain explicit missing/empty-key failure.
5. Add `.env` to `.gitignore`; do not ignore `.env.example`.
6. Add `.env.example` containing `DJANGO_SECRET_KEY=replace-with-a-generated-secret` and concise instructions to copy it to `.env` and replace the placeholder with a generated local key.
7. Keep settings unrelated to this issue unchanged.
8. Do not create a `.env` file or place any actual secret in workspace files.

## Security requirements

- Never add or print a real secret.
- Never evaluate `.env` as Python, shell, or PowerShell code.
- The `.env` file must be ignored by git; only the placeholder example may be tracked.
- Process environment values must override `.env`.
- Missing secrets must fail clearly; do not fall back to a hard-coded or development secret.

## Acceptance criteria

- With a valid `DJANGO_SECRET_KEY` in project-root `.env` and the process variable unset, `uv run python manage.py check` succeeds from the project root.
- With a process `DJANGO_SECRET_KEY` set and a different `.env` value, the process value is used.
- With no key in either source, settings raise `ImproperlyConfigured`.
- Missing `.env` is tolerated if a process environment key is present.
- `.env` is ignored by git and `.env.example` remains available.
- Running the command from inside `tracker` is not presented as supported; the correct root-level invocation is documented.

## Checks to run

Run from the project root with `uv run`:

1. `uv run python manage.py check`
2. `uv run python manage.py makemigrations --check`
3. `uv run python manage.py test tracker`
4. Smoke-test settings loading in separate processes for `.env` fallback, environment precedence, and missing-key behavior without revealing any key values.
5. Start `uv run python manage.py runserver 127.0.0.1:8000 --noreload`, verify the server responds, and stop it after the smoke test.

Report exact command results. Remove only any temporary test `.env` created for validation.

## Exact manual test steps

1. From the project root, copy `.env.example` to `.env`.
2. Replace the placeholder with a locally generated secret; do not commit `.env`.
3. Run `uv run python manage.py check`, then `uv run python manage.py runserver`.
4. Confirm the startup error about missing `DJANGO_SECRET_KEY` no longer occurs.
5. Stop the server and run `git check-ignore .env`; confirm it reports the file as ignored.
6. To verify the working-directory issue, return to the project root before running Django commands; `manage.py` is not inside the `tracker` directory.
