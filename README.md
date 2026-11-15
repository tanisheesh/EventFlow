<p align="center">
  <img src="docs/assets/logo.svg" width="64" height="64" alt="EventFlow">
</p>

<h1 align="center">EventFlow</h1>

<p align="center">
  <strong>Event management in Flask: organizers run events, venues, speakers and ticket types; attendees book and cancel tickets. Monitored live by Reqly.</strong>
</p>

<p align="center">
  <a href="https://eventflow-g2h5.onrender.com">
    <img src="https://img.shields.io/badge/live_demo-visit-008080?style=flat-square" alt="Live Demo">
  </a>
  <a href="https://github.com/tanisheesh/EventFlow/actions/workflows/ci.yml">
    <img src="https://github.com/tanisheesh/EventFlow/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/tanisheesh/EventFlow/actions/workflows/codeql.yml">
    <img src="https://github.com/tanisheesh/EventFlow/actions/workflows/codeql.yml/badge.svg" alt="CodeQL">
  </a>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Reqly-06B6D4?style=flat-square" alt="Reqly">
  <img src="https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black" alt="Render">
  <img src="https://img.shields.io/badge/license-GPL--3.0-008080?style=flat-square" alt="License">
</p>

---

## What is EventFlow?

EventFlow replaces fragmented event spreadsheets with a single server-rendered Flask web app where organizers manage venues, speakers, and priced ticket tiers while attendees browse events and book or cancel seats with transactional inventory updates. It also serves as the live production demo for [Reqly](https://github.com/tanisheesh/reqly), streaming real route latency, error rates, release tags, and salted user telemetry to a public observability dashboard without ever blocking requests.

> **Live demo →** [https://eventflow-g2h5.onrender.com](https://eventflow-g2h5.onrender.com) (Render free tier; first cold start takes ~30s)
> Public Reqly dashboard: [reqly-eventflow-dashboard.onrender.com](https://reqly-eventflow-dashboard.onrender.com) · Collector API: [reqly-eventflow-collector.onrender.com/docs](https://reqly-eventflow-collector.onrender.com/docs)

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@eventhub.com` | `Admin@123` |
| Organizer | `organizer@eventhub.com` | `Organizer@123` |
| Attendee | `buyer@eventhub.com` | `Buyer@123` |

The `/login` page includes one-click **"Use These"** buttons for each seeded demo account.

---

## What you get

- **Three enforced roles** — attendees book and cancel tickets, organizers manage events/venues/speakers/ticket tiers on `/dashboard`, and administrators oversee organizers on `/admin/organizers`
- **Events, venues, and speakers** — full create, edit, and delete flows with venue-capacity checks (`total_tickets <= event.venue.capacity`) and linked-venue deletion protection
- **Transactional ticket stock** — booking creates one `Order` plus per-seat `Ticket` rows and decrements `TicketType.quantity` atomically; cancelling returns stock and removes empty orders
- **Hardened role boundaries** — public `/signup` ignores client-supplied `user_type` values and always provisions `attendee`, while cancellation enforces ticket ownership (`order.user_id == session['user_id']`)
- **Live Reqly observability** — instrumented via `reqly.instrument(app, service_name="eventflow", consumer=reqly_consumer)` with `REQLY_CONSUMER_SALT` HMAC hashing and fail-open background batching

---

## By the numbers

| Metric | Value | Source |
|---|---|---|
| HTTP route handlers | 25 `@app.route` endpoints across 13 Jinja2 templates | `app.py`, `templates/` |
| Relational data model | 8 SQLAlchemy tables (`User`, `Venue`, `Event`, `TicketType`, `Order`, `Ticket`, `Speaker`, `Payment`) | `app.py`, `schema_sqlite.sql` |
| Role-based access & demo accounts | 3 RBAC roles (`attendee`, `organizer`, `administrator`), bcrypt-hashed passwords | `app.py`, `create_admin_users.py` |
| Automated smoke test suite | 5 end-to-end `pytest` tests covering auth, CRUD, booking/cancel & role redirects | `tests/test_smoke.py` |
| Telemetry fail-open guarantee | Background thread batching (`REQLY_SAMPLE_RATE` configurable; collector optional) | `app.py`, `render.yaml` |

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Jinja2 3.1 · Server-rendered HTML · Plain CSS (`#008080` teal theme) · Vanilla JS |
| Backend | Python 3.12 · Flask `>=3.1.3` · Werkzeug `>=3.1.9` · Gunicorn `>=26.2.0` |
| Database | SQLite · Flask-SQLAlchemy `3.1.1` · SQLAlchemy `2.1.8` |
| Auth | Signed Flask session cookies · bcrypt `>=5.0.0` per-password salts · Role decorators |
| Observability | Reqly Python SDK (`reqly>=0.7.1`) · `REQLY_CONSUMER_SALT` user hashing · `RENDER_GIT_COMMIT` releases |
| Infra | Render free web service (`render.yaml`, Oregon) |

---

## Engineering Decisions

**Why SQLite seeded at startup over managed PostgreSQL?**
Render's free web plan has no managed database or persistent disk, so `start.py` runs `db.create_all()` and idempotently seeds the three demo accounts on every boot at `$0/mo` with zero external connection overhead. When persistent user data or concurrent multi-worker writes are required, switching `DATABASE_URL` to PostgreSQL + Alembic migrations requires no ORM rewrite.

**Why store remaining `TicketType.quantity` as a transactional counter instead of counting `Ticket` rows?**
Keeping `quantity` directly on `TicketType` turns availability checks into a single indexed column read and updates stock in the same SQLAlchemy transaction as `Order` and `Ticket` creation (or cancellation rollback). Under high-concurrency flash sales, the next step is replacing the read-then-decrement check with an atomic `UPDATE tickettype SET quantity = quantity - :qty WHERE ... AND quantity >= :qty`.

**Why fail-open Reqly background instrumentation with salted consumer IDs?**
Because EventFlow showcases Reqly in public, telemetry must never degrade user checkout latency or leak account IDs. The SDK hashes `session['user_id']` locally using `REQLY_CONSUMER_SALT`, dispatches batches on a background thread, and disables itself cleanly if the collector is unreachable.

**What would you do differently in v2?**
Add `Flask-WTF` CSRF protection on all `POST` forms, serve via `gunicorn` (already in `requirements.txt`) instead of `start.py`'s Flask server, split the 787-line `app.py` into Blueprints and validated service modules, enforce per-organizer `organizer_id` ownership checks, and move to PostgreSQL with Alembic migrations.

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements — quantified impact, acceptance criteria, edge cases, unit economics |
| [Architecture](docs/ARCHITECTURE.md) | System topology (Mermaid), route contracts, SQLite schema/indexes, scale ceilings |
| [Decisions](docs/DECISIONS.md) | Technical ADRs — comparison matrices, tradeoffs, and reversal triggers |
| [Setup](docs/SETUP.md) | Local dev onboarding, env var matrix, seed data, and troubleshooting |
| [Deploy](docs/DEPLOY.md) | Production Render & Docker topology, smoke checks, and incident runbooks |
| [Contributing](CONTRIBUTING.md) | Branching from `master`, emoji commit style, and PR checklist |
| [Changelog](CHANGELOG.md) | Release history mapped to commit history |
| [Security](SECURITY.md) | Vulnerability reporting policy and security scope |

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
