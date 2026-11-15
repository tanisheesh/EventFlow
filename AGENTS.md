# EventFlow — Agent Development Guidelines

Follow these rules strictly on every file you create or modify in **EventFlow**.

---

## 1. File Organization & Architecture

- **File naming:**
  - Python: ALWAYS use `snake_case` for modules, functions, and variables (`create_admin_users.py`, `cancel_ticket`) and `PascalCase` for SQLAlchemy models and config classes (`TicketType`, `ProductionConfig`).
  - Frontend assets: Use `kebab-case` for JS modules (`event-validation.js`) and `snake_case` for Jinja2 templates (`event_details.html`, `my_tickets.html`).
- **File size limit:** Keep files focused and **under 300 lines**. `app.py` is currently 787 lines; extract new route groups into Flask Blueprints (`routes/`) and domain/DB helpers into focused modules (`services/` or `models.py`) instead of growing `app.py` further.
- **Layered separation:**
  - `templates/` — Jinja2 views extending `templates/layout.html` (`layout.html` owns navbar, flash alerts, footer, and global Reqly links). Keep business/DB logic out of templates.
  - `static/css/style.css` — shared design tokens and layout styles; `static/js/` — progressive enhancement and form validation.
  - `config.py` — environment configuration classes (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`).
  - Route handlers stay thin: verify session/role -> validate form/query inputs -> run transactional DB helper -> flash message and `redirect()` or `render_template()`.
- **Reusability (Rule of Two):** Extract any repeated route guard, query pattern, or Jinja2 template block used 2+ times into a shared decorator, helper function, or Jinja2 partial/macro.

---

## 2. Code Style & Strictness

- **PEP 8 formatting:** 4-space indentation, max line length 100 chars (matching `.editorconfig`).
- **No dead code or debug clutter:** Never leave unused imports, commented-out code blocks, stray `print()` calls, or `console.log()` debug statements. Use `app.logger` for server errors.
- **Control flow & early returns:** Check auth, role, and input validity at the top of each route with early returns/redirects before starting DB mutations.
- **SQLAlchemy 2.x conventions:** Use `db.session.get(Model, pk)` and `db.session.execute(db.select(...))` rather than legacy `Model.query.get()` when adding or updating queries.
- **Error handling:** Wrap multi-step DB writes (e.g., creating an `Order` + `Ticket` rows + updating `TicketType.quantity`) in `try / except` blocks that call `db.session.rollback()` on failure and log via `app.logger.error(...)`. NEVER use bare `except:` or silent `except Exception: pass`.

---

## 3. UI Craft & Anti-AI-Slop Rules

- **Banned clichés:**
  - No generic purple/indigo/pink linear gradients, neon box-shadow glows, or rainbow badge spam.
  - No cookie-cutter 3-column icon-in-circle marketing grids inside dashboards or utility pages.
  - No emoji-prefixed app UI headings, hype copy (*"Supercharge..."*), or hardcoded fake telemetry/metrics.
  - No dead `href="#"` links, no-op buttons, or `window.alert()` / blocking `window.confirm()` on new UI.
- **Design discipline:** Stick to the existing CSS variables in `static/css/style.css` (`--primary-color: #008080`, `--accent-color: #FFA500`, `--secondary-color: #F0F0F0`, `1px` borders), consistent currency formatting (`₹`), and `tabular-nums` for prices, counts, and timestamps.
- **Mandatory UI states:** Every list, table, and dashboard view must handle **Empty** (clear message + next action), **Error** (flash alert banner), and **Populated** states cleanly.
- **Accessibility & responsiveness:** Semantic HTML (`<button>`, `<label for>`, `<main>`, `<nav>`), visible focus rings, WCAG AA contrast, and zero horizontal overflow at `375px` and `1280px`.

---

## 4. Security Rules

- **Boundary validation:** Explicitly validate, strip, and coerce every form field and query parameter before touching the database; handle missing keys and `ValueError` cleanly with flash errors and safe redirects (no mass assignment).
- **Auth + IDOR protection:** Protect every non-public route with `@login_required(role=...)` or `@organizer_required` AND verify resource ownership (`order.user_id == session['user_id']`, `event.organizer_id == session['user_id']` for organizer isolation), failing closed (`302` redirect to `/login` or `/`, or `403`/`404`). Never accept a role from public signup forms.
- **Password & session safety:** Hash passwords exclusively with `bcrypt.hashpw(..., bcrypt.gensalt())`. In production (`FLASK_ENV=production`), `SECRET_KEY` must come from environment variables rather than a hardcoded fallback. Never log passwords, session cookies, or `REQLY_API_KEY`.
- **XSS & CSRF hygiene:** Rely on Jinja2 HTML auto-escaping for template expressions; never mark user-supplied strings `| safe`. Add CSRF protection (`Flask-WTF` / `CSRFProtect`) on all `POST` forms when hardening/extending routes.
- **Secrets isolation & telemetry privacy:** Never commit `.env*` files; document every new env var in `.env.example` with an empty value. Keep Reqly instrumentation fail-open and hash user IDs via `REQLY_CONSUMER_SALT`.

---

## 5. Testing & Verification

- **No work is complete without tests:**
  - New helpers/validators -> unit tests in `tests/` (happy path + empty/null/boundary cases).
  - New routes or permission checks -> Flask `test_client()` tests verifying `200`/`302` redirects, auth/role/ownership enforcement, and DB rollback/stock integrity.
  - Bugfixes -> regression test reproducing the bug before fixing.
  - Template/UI changes -> verify mobile (`375px`) and desktop (`1280px`) layouts and zero console errors.
- **Test isolation:** Set `REQLY_SAMPLE_RATE="0"` and use a temporary SQLite database (matching `tests/test_smoke.py`) so tests never touch local dev data or emit telemetry.
- **Never bypass checks:** Never delete tests, mark failing tests as skipped, or disable CI steps.

### Verification Commands (Run Before Finishing)

```bash
python -m compileall -q -x '(\.venv|venv|node_modules|\.git)/' .
python -m pytest -q
# If ruff.toml / .ruff.toml / [tool.ruff] is configured:
ruff check .
```

If `coderabbit` CLI is installed locally, optionally run a pre-PR review on your changes:

```bash
coderabbit review --agent --uncommitted   # or --base master --gate major
```

---

## 6. Git & Commit Rules

- **Atomic commits:** `<emoji> [#issue] [scope:] <present tense lowercase message>` (see `CONTRIBUTING.md`).
- **PRs:** Use plain-English **past-tense** PR titles against `master`, fill `.github/PULL_REQUEST_TEMPLATE.md`, and include docs / `.env.example` / tests in the same PR.
- **Safety:** Never force-push or run `git reset --hard` on `master`. Record any Render rollback deploy ID/SHA and reason in a commit or PR.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
