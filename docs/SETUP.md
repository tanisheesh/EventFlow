# Local Setup — EventFlow

> **Just want to try it?** Use the live deployment at [https://eventflow-g2h5.onrender.com](https://eventflow-g2h5.onrender.com) — zero setup needed.
> This guide covers running **EventFlow** locally, initializing SQLite + demo accounts, running CI verification checks, and troubleshooting common issues.

---

## Prerequisites & Versions

- Python `3.12` recommended (`3.9+` compatible; matches `.github/workflows/ci.yml`)
- `pip` + `git`
- Optional: Docker & Docker Compose (only if running a local [Reqly](https://github.com/tanisheesh/reqly) collector + dashboard)

---

## 1. Clone & Install

```bash
git clone https://github.com/tanisheesh/EventFlow
cd EventFlow
python -m venv venv
source venv/bin/activate        # Windows PowerShell: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2. Environment Variables

Copy `.env.example` to `.env` and populate values as needed:

```bash
cp .env.example .env
```

| Variable | Type / Format | Required | Scope | Local Default / Source |
|---|---|---|---|---|
| `SECRET_KEY` | Random hex/string | ✅ *(recommended)* | Server-only | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | `development` \| `testing` \| `production` | ❌ | Server-only | `development` |
| `FLASK_APP` | Module filename | ❌ | Server-only | `app.py` |
| `DATABASE_URL` | SQLAlchemy URI | ❌ | Server-only | `sqlite:///eventhub.db` (stored in `instance/eventhub.db`) |
| `TEST_DATABASE_URL` | SQLAlchemy URI | ❌ | Test-only | `sqlite:///:memory:` (used by `TestingConfig` in `config.py`) |
| `PORT` | Integer port | ❌ | Server-only | `5000` |
| `REQLY_COLLECTOR_URL` | HTTP(S) URL | ❌ | Server-only | `http://localhost:8000` (local Reqly Docker Compose) |
| `REQLY_API_KEY` | Ingest secret string | ❌ | Server-only | Collector's `REQLY_INGEST_KEY` (`demo-key` for local compose) |
| `REQLY_ENVIRONMENT` | Environment tag | ❌ | Server-only | `development` |
| `REQLY_CONSUMER_SALT` | Random hex/string | ❌ | Server-only | Hashes `session['user_id']` before Reqly telemetry leaves the app |
| `REQLY_DASHBOARD_URL` | HTTP(S) URL | ❌ | Template link | `http://localhost:5173` (linked for admins + footer) |
| `REQLY_SAMPLE_RATE` | Float (`0`–`1`) | ❌ | Server/Test | Set `0` in tests (`tests/test_smoke.py`) to suppress emission |

> Never commit `.env` or `.env.local`. All `REQLY_*` variables are optional; without a collector, EventFlow remains completely functional and fail-open.

---

## 3. Database Initialization & Seed Data

`start.py` automatically creates missing tables via `db.create_all()`, ensures the `event.organizer_id` column exists, and runs `create_admin_users()` idempotently on every launch.

To initialize or seed manually instead:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python create_admin_users.py
```

Default seeded demo credentials:

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@eventhub.com` | `Admin@123` |
| Organizer | `organizer@eventhub.com` | `Organizer@123` |
| Attendee | `buyer@eventhub.com` | `Buyer@123` |

---

## 4. Run Locally

```bash
python start.py
```

EventFlow listens on `http://localhost:5000` (or `$PORT`).

### Optional: Run With a Local Reqly Collector

```bash
git clone https://github.com/tanisheesh/reqly
cd reqly
docker compose up -d
```

Set `REQLY_COLLECTOR_URL=http://localhost:8000`, `REQLY_API_KEY=demo-key`, `REQLY_CONSUMER_SALT=<random>`, and `REQLY_DASHBOARD_URL=http://localhost:5173` in EventFlow's `.env`, then restart `python start.py`. See the [Reqly quickstart](https://reqly.tanisheesh.in/docs/quickstart/).

---

## 5. Run Verification & Full Test Suite

Run the exact same checks `.github/workflows/ci.yml` enforces before committing:

```bash
python -m compileall -q -x '(\.venv|venv|node_modules|\.git)/' .
python -m pytest -q
# If ruff is configured in ruff.toml / .ruff.toml / pyproject.toml:
ruff check .
```

*(If `coderabbit` CLI is installed locally: `coderabbit review --agent --uncommitted` or `coderabbit review --agent --base master`)*

---

## 6. Known Local-Only Limitations

- **`app.py` vs `config.py`:** `app.py` loads `SECRET_KEY` and `DATABASE_URL` directly via `python-dotenv` (`load_dotenv()`) rather than calling `get_config()` from `config.py`.
- **SQLite file location:** Relative URIs like `sqlite:///eventhub.db` are resolved by Flask-SQLAlchemy into `instance/eventhub.db` rather than the repo root.
- **Built-in server in `start.py`:** `start.py` starts Flask's development WSGI server (`app.run(..., debug=False)`) unless launched directly via `gunicorn app:app`.

---

## 7. Troubleshooting

| Symptom / Exact Error | Root Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Running global `python` instead of virtual environment | Activate `venv` (`source venv/bin/activate` / `.\venv\Scripts\Activate.ps1`) and run `pip install -r requirements.txt` |
| `sqlite3.OperationalError: no such column: event.organizer_id` | Older pre-existing `eventhub.db` created before `organizer_id` was added | Run `python start.py` once (runs `ALTER TABLE` check) or delete `instance/eventhub.db` to recreate cleanly |
| `Address already in use` on port `5000` | Another process (or AirPlay Receiver on macOS) holds port `5000` | Set `PORT=5050` in `.env` and restart `python start.py` |
| Reqly metrics missing locally | `REQLY_COLLECTOR_URL` / `REQLY_API_KEY` unset or collector down | Verify `REQLY_SAMPLE_RATE` isn't `0` and collector is reachable on `http://localhost:8000` |
| `LegacyAPIWarning: The Query.get() method is considered legacy` | SQLAlchemy `2.1.8` warning on existing `Model.query.get()` calls | Non-fatal warning; tests pass normally (tracked for v2 `db.session.get()` migration) |

---

## 8. Deploy to Production

See [DEPLOY.md](DEPLOY.md) for Render Blueprint deployment, Docker self-hosting, post-deploy verification, and rollback procedures.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
