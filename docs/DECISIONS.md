# Engineering Decisions — EventFlow

---

## ADR-01 — SQLite Created and Seeded at Startup Over Managed PostgreSQL

**Context:** EventFlow's live deployment runs on Render's free web service tier, which provides no managed database or persistent volume.

### Options Considered

| Option | Query Latency | Monthly Cost | Ops Complexity | Verdict |
|---|---|---|---|---|
| **SQLite + `start.py` idempotent seed** | < 2ms local disk | $0 | Low (single file) | ✅ **Chosen** |
| Managed PostgreSQL (Render / Neon) | 10–30ms network | $0–$7+ (Render free DB expires) | Medium (migrations + URL rotation) | ❌ Rejected for v1 |
| In-memory SQLite (`:memory:`) | < 1ms | $0 | Low, but wiped across Gunicorn workers | ❌ Rejected |

**Decision & Reason:** Use SQLite via Flask-SQLAlchemy and run `db.create_all()` + `create_admin_users()` inside `start.py` on every boot. There are zero external DB credentials to rotate, zero network round-trips, and every Render redeploy or cold-start wakes in a known clean state with all three demo accounts ready.

**Tradeoff Accepted:** Live demo records created by visitors reset on every deploy or container recycle, SQLite permits only one writer at a time, and schema changes require explicit `ALTER TABLE` startup checks (as done for `event.organizer_id` in `start.py`).

**Reversal Trigger:** Revisit when persistent user bookings are required across deploys or concurrent write volume exceeds ~5–10 writes/sec — point `DATABASE_URL` to managed PostgreSQL and add Alembic migrations.

---

## ADR-02 — Flat Role Decorator Hierarchy Over Per-Resource ACL Matrix

**Context:** EventFlow has three user types (`attendee`, `organizer`, `administrator`) sharing read views while gating organizer management and admin actions.

### Options Considered

| Option | Check Overhead | Monthly Cost | Ops Complexity | Verdict |
|---|---|---|---|---|
| **Single `login_required(role)` decorator** | 1 PK query (`User.query.get`) | $0 | Low | ✅ **Chosen** |
| Flask-Security / RBAC policy table | Multiple joins / policy eval | $0 | High | ❌ Rejected |
| Ad-hoc `session` checks in every route | Minimal | $0 | High drift risk | ❌ Rejected |

**Decision & Reason:** Centralize role checking in `login_required(role="attendee")` and `@organizer_required` in `app.py`. Unauthenticated users redirect to `/login`, wrong roles redirect to `/`, `administrator` passes every decorator check, and `organizer` passes `organizer` and `attendee` checks. Route permissions are readable in one line above each handler.

**Tradeoff Accepted:** Role equality does not enforce per-organizer event ownership (`event.organizer_id` is stored for admin cleanup, not filtered in `edit_event` / `delete_event`). Also, `book_ticket` checks `session.get('user_role') == 'attendee'` directly, so organizers/admins cannot book tickets without an attendee account.

**Reversal Trigger:** Revisit when multiple independent organizers publish competing events on the same instance — enforce `event.organizer_id == session['user_id']` (or admin override) on every mutation route.

---

## ADR-03 — Transactional `TicketType.quantity` Counter Over Aggregate `COUNT(Ticket)`

**Context:** Booking and cancellation must keep remaining seat counts consistent with issued `Ticket` rows while enforcing venue capacity.

### Options Considered

| Option | Read Cost | Monthly Cost | Concurrency Safety | Verdict |
|---|---|---|---|---|
| **Mutable `TicketType.quantity` column in transaction** | O(1) single-row read | $0 | Safe under single-process; TOCTOU under multi-worker | ✅ **Chosen** |
| Aggregate `initial_cap - COUNT(Ticket)` per request | O(N) join/count scan | $0 | Safe if serialized, slower at scale | ❌ Rejected |
| Redis distributed inventory lock | 5–15ms network | $0–$10 | High | ❌ Overkill for v1 |

**Decision & Reason:** Store remaining inventory directly on `TicketType.quantity`. `book_ticket` inserts `Order` + N `Ticket` rows and decrements `TicketType.quantity` in one commit; `cancel_ticket` uses `db.session.begin_nested()` to increment `quantity`, remove the `Ticket`, and update or delete the `Order`.

**Tradeoff Accepted:** Reading `ticket_type.quantity` in Python before updating allows a narrow TOCTOU window if two concurrent requests book the final ticket simultaneously under multi-worker WSGI.

**Reversal Trigger:** Revisit before switching to multi-worker Gunicorn or running high-concurrency drops — replace read-then-write with atomic conditional `UPDATE tickettype SET quantity = quantity - :qty WHERE ticket_type_id = :id AND quantity >= :qty`.

---

## ADR-04 — Fail-Open Background Reqly Instrumentation With Salted Consumer IDs

**Context:** EventFlow acts as the live public showcase for Reqly, so every route needs real latency, error, and user metrics without risking checkout reliability or leaking user IDs.

### Options Considered

| Option | Request Overhead | Monthly Cost | Failure Blast Radius | Verdict |
|---|---|---|---|---|
| **Reqly SDK background thread + `REQLY_CONSUMER_SALT`** | ~0ms synchronous | $0 | Zero (fail-open) | ✅ **Chosen** |
| Synchronous HTTP POST per request | +30–200ms p95 | $0 | Collector outage breaks EventFlow | ❌ Rejected |
| Log scraping / Prometheus sidecar | Minimal | Paid infra | Complex on Render free tier | ❌ Rejected |

**Decision & Reason:** Call `reqly.instrument(app, service_name="eventflow", consumer=reqly_consumer)` once in `app.py`. The SDK hashes `session['user_id']` locally with `REQLY_CONSUMER_SALT`, tags `RENDER_GIT_COMMIT` and `REQLY_ENVIRONMENT`, and dispatches batches asynchronously while silently disabling itself on SDK/network failure.

**Tradeoff Accepted:** Telemetry events can be dropped during prolonged collector outages, and hashed consumer IDs cannot be reversed back to raw `User` emails from the Reqly dashboard alone.

**Reversal Trigger:** Revisit if strict lossless billing/audit trails are required — add a durable local outbox or message broker instead of in-memory SDK batching.

---

## ADR-05 — Server-Rendered Flask + Jinja2 Over Separate Next.js Frontend

**Context:** Early commits (`b537024`, `8597fa7`) scaffolded a Next.js frontend before commit `06f2b25` rebuilt EventFlow as a unified Flask + Jinja2 app.

### Options Considered

| Option | Cold Build / Runtime | Monthly Cost | Codebase Complexity | Verdict |
|---|---|---|---|---|
| **Flask + Jinja2 monolith** | Single Python process | $0 | Low (1 service, 0 CORS) | ✅ **Chosen** |
| Next.js SPA + Flask JSON API | 2 builds + 2 hosted services | $0–$14 | High (CORS, token sync, 2 deploys) | ❌ Replaced |

**Decision & Reason:** Consolidate HTML rendering, cookie sessions, ORM transactions, and Reqly route instrumentation into one Flask service deployed via a single Render Blueprint (`render.yaml`).

**Tradeoff Accepted:** Full page reloads on form submits, inline confirmation prompts, and less reactive filtering compared to a client-side SPA.

**Reversal Trigger:** Revisit if interactive real-time seat maps or live inventory WebSockets become core requirements — introduce JSON endpoints or HTMX partials incrementally.

---

## What I'd Do Differently in v2

- **Add CSRF protection (`Flask-WTF`)** — All `POST` forms currently rely on session cookies without CSRF tokens.
- **Serve production via `gunicorn`** — `gunicorn>=26.2.0` is already in `requirements.txt`, yet `start.py` currently invokes Flask's built-in development server (`app.run(...)`).
- **Split the 787-line `app.py` into Blueprints + validated schemas** — Separate `auth`, `events`, `bookings`, and `admin` Blueprints and add strict Pydantic/WTForms input parsing.
- **Fix UI & filter mismatches** — Wire `events.html`'s `search`/`date` inputs in `list_events()`, unify currency symbols (`₹` vs `$` in `manage_tickets.html`), replace `href="#"` placeholders in `dashboard.html`, and update legacy `Model.query.get()` calls for SQLAlchemy 2.1.

---

## Explicit Non-Decisions (Deferred to v2)

| Feature | Why Deferred | Trigger to Build |
|---|---|---|
| **Stripe test-mode payments** | Core booking/cancellation inventory flow shipped first; `Payment` table is already modeled | Real paid ticket flows required beyond demo |
| **Transactional booking emails** | Requires SMTP/provider credentials and async worker queue | Real external attendee signups outside demo |
| **Interactive venue seat picker** | `Ticket.seat_number` exists as nullable metadata; general admission tiers cover v1 | Reserved-seating event requirement |
| **Server-side `/events` search/date filtering** | Small seeded demo catalog fits on one page | > 20 concurrent events listed |

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
