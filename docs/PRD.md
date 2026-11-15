# EventFlow — Product Requirements Document

| Field | Value |
|---|---|
| **Status** | v1.0 Live |
| **Owner** | Tanish Poddar |
| **Live URL** | [https://eventflow-g2h5.onrender.com](https://eventflow-g2h5.onrender.com) |
| **One-liner** | Event management in Flask: organizers run events, venues, speakers and ticket types; attendees book and cancel tickets. Monitored live by Reqly. |

---

## 1. Problem & Quantified Impact

Small event organizers commonly coordinate events, venues, speakers, and ticket availability across disconnected spreadsheets and manual registration forms, causing oversold venues, stale ticket counts, and zero self-service order tracking for attendees. At the same time, [Reqly](https://github.com/tanisheesh/reqly) needed a multi-role production web application generating real authenticated read/write traffic rather than synthetic ping loops so evaluators can inspect live latency percentiles, release tags, and per-user telemetry. EventFlow unifies organizer operations, attendee booking/cancellation, admin governance, and fail-open Reqly observability in a single Flask service running on Render's free tier.

| Dimension | Before (Manual / Baseline) | After (v1 Target) |
|---|---|---|
| Ticket inventory reconciliation | Manual spreadsheet tally across tiers and cancellations | Transactional `Order` + `Ticket` + `TicketType.quantity` sync in one SQLAlchemy commit |
| Venue capacity enforcement | Error-prone manual arithmetic across ticket tiers | Server-side guard ensuring `sum(existing.quantity) + new <= venue.capacity` |
| Attendee self-service & cancellation | Email/DM requests to organizer to drop seats | Self-service `/my-tickets` view with one-click cancellation and stock restoration |
| API observability demo traffic | Synthetic mock data in Reqly dashboard | Live `reqly>=0.7.1` telemetry across 25 Flask routes on Render (`$0/mo` cost) |

---

## 2. Goals (v1 / MVP)

1. Email/password registration and login with bcrypt password hashing (`bcrypt.gensalt()`) and signed Flask session cookies.
2. Three enforced RBAC roles (`attendee`, `organizer`, `administrator`) where public `/signup` always provisions `attendee` regardless of submitted form fields.
3. Organizers manage events, venues, speakers, and priced ticket tiers from `/dashboard` with linked-venue deletion protection and venue-capacity enforcement.
4. Attendees browse upcoming events (`/`, `/events`, `/events/<event_id>`), book multi-ticket orders in one transaction, view `/my-tickets`, and cancel individual owned tickets with automatic stock return and order cleanup.
5. Administrators inspect organizer event counts and cascade-delete organizer accounts via `/admin/organizers`.
6. Deployed live on Render (`render.yaml`) with three idempotently seeded demo accounts (`create_admin_users.py`), covered by 5 end-to-end `pytest` smoke tests (`tests/test_smoke.py`), and monitored live by Reqly (`https://reqly-eventflow-dashboard.onrender.com`).

---

## 3. Non-Goals (Explicit Scope Cuts)

- **Real payment processing** — Bookings generate `Order` and `Ticket` rows without charging a card. The `Payment` table exists in `app.py` and `schema_sqlite.sql`, deferred until Stripe test-mode integration is prioritized.
- **Transactional emails** — No booking confirmations or event reminders; trigger to add is real attendee registration outside demo usage.
- **Interactive seat selection** — `Ticket.seat_number` exists in the schema as an optional nullable integer, deferred unless assigned-seating venues are required.
- **Per-organizer event ownership isolation** — `Event.organizer_id` is recorded on creation and used on `/admin/organizers`, while `/dashboard` currently lets any organizer manage all events; trigger to add is multi-tenant external organizer onboarding.

---

## 4. Users & Personas

**Primary:** Small event organizers managing schedules, venues, speakers, and ticket tiers on one dashboard, alongside attendees discovering events and managing booked tickets.

**Secondary:** Developers and recruiters evaluating [Reqly](https://github.com/tanisheesh/reqly) who exercise real authenticated flows on EventFlow and watch route telemetry update on the public Reqly dashboard.

---

## 5. User Stories & Acceptance Criteria

### Story 1 — Onboarding, Authentication & Role Enforcement
*As a visitor or demo evaluator, I want to sign up or sign in with role-appropriate credentials so that I access only the capabilities permitted for my role.*
- **Given** an anonymous user submits `POST /signup` even with a tampered `user_type=administrator` form field, **When** `signup()` persists the `User`, **Then** `user_type` is forced to `attendee` and duplicate emails roll back cleanly with an error flash.
- **Given** an unauthenticated visitor or `attendee` requests `GET /dashboard` or `GET /my-tickets` (when signed out), **When** `@login_required` evaluates the session, **Then** the app fails closed with a `302` redirect to `/login` or `/` and flashes a warning/danger alert.

### Story 2 — Organizer Event, Venue, Speaker & Ticket Tier Management
*As an organizer, I want to create venues, events, speakers, and ticket tiers within venue capacity so that attendees can book valid tickets.*
- **Given** a venue has `capacity = 100` and existing ticket tiers totaling `80`, **When** an organizer submits `POST /events/<id>/tickets/manage` with `quantity = 30`, **Then** the write is rejected before commit with a flash error explaining `110 > 100`.
- **Given** a venue is referenced by at least one `Event`, **When** an organizer attempts `POST /venues/<id>/delete`, **Then** deletion is blocked (`Cannot delete venue. It is linked to existing events.`).

### Story 3 — Attendee Ticket Booking & Ownership-Safe Cancellation
*As an attendee, I want to book multiple tickets in one order and cancel individual seats from `/my-tickets` so that my order total and available event stock stay accurate.*
- **Given** `TicketType` has `quantity = 10`, **When** an attendee posts `quantity = 2` to `/book_ticket/<event_id>`, **Then** in a single transaction one `Order` and two `Ticket` rows are inserted and `TicketType.quantity` becomes `8`.
- **Given** Attendee A owns `ticket_id`, **When** Attendee A posts `/tickets/<ticket_id>/cancel`, **Then** `TicketType.quantity` increments by `1`, the ticket is deleted, and `Order.total_price` is recalculated (or the `Order` is deleted if 0 tickets remain); if Attendee B attempts the same `POST`, ownership verification rejects the request with a flash error and zero DB changes.

### Story 4 — Administrator Organizer Governance & Live Reqly Metrics
*As an administrator, I want to view organizer event counts, remove organizer accounts safely, and jump straight to live Reqly API metrics.*
- **Given** an administrator visits `/admin/organizers`, **When** `manage_organizers()` queries organizers and `GROUP BY Event.organizer_id`, **Then** each organizer row displays their exact event count and `POST /admin/organizers/<user_id>/delete` cascades deletion of their tickets, ticket types, speakers, and events inside one transaction.

---

## 6. Functional Requirements

### 6.1 Auth & RBAC
- Passwords hashed via `bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())` and verified via `bcrypt.checkpw(...)`.
- Session stores `user_id`, `user_name`, and `user_role`; `GET /logout` clears the session.
- `@login_required(role=...)` queries `User` from `session['user_id']`; `administrator` passes every check, `organizer` passes `organizer` and `attendee` checks, and `attendee` passes `attendee` checks only (`book_ticket` specifically restricts to `session.get('user_role') == 'attendee'`).

### 6.2 Events, Venues, Speakers & Capacity Rules
- Organizers create, edit, and delete events (`name`, `description`, `date`, `time`, `location_id`, `organizer_id`, linked `speakers`), venues (`name`, `address`, `capacity`, `city`, `state`, `zip_code`), and speakers (`name`, `bio`, `event_id`).
- `manage_event_tickets` enforces `sum(existing_ticket_types.quantity) + new_quantity <= event.venue.capacity`.

### 6.3 Tickets, Orders & Transactions
- `book_ticket` validates `ticket_type` exists for `event_id` and `1 <= quantity <= ticket_type.quantity`, then atomically creates `Order`, N `Ticket` records, and decrements `TicketType.quantity`.
- `cancel_ticket` verifies `order.user_id == session['user_id']`, increments `TicketType.quantity` via `db.session.begin_nested()`, removes the `Ticket`, and either recalculates `order.total_price` or removes the empty `Order`.

### 6.4 Observability & Failure Isolation
- `reqly.instrument(app, service_name="eventflow", consumer=reqly_consumer)` captures route template, status code, latency, `RENDER_GIT_COMMIT`, `REQLY_ENVIRONMENT`, and HMAC-salted `user_id` (`REQLY_CONSUMER_SALT`).
- Telemetry executes asynchronously on a background thread and disables itself on internal failure so collector outages never interrupt EventFlow responses.

---

## 7. Edge-Case & Failure Behavior Matrix

| Scenario | Expected System Behavior | User Feedback / Status |
|---|---|---|
| Empty event, venue, speaker, or ticket list | Render template empty-state message with link/CTA to browse or create | `200` with empty-state prompt |
| Ticket quantity `< 1` or `> ticket_type.quantity` | Booking rejected before any DB insert/update | `302` redirect + danger flash alert |
| Ticket tier total exceeds `venue.capacity` | Reject tier creation before DB insert | `302` redirect + danger flash alert |
| Duplicate email on `/signup` | SQLAlchemy `IntegrityError` caught and rolled back | `200` re-render + `"Email address already exists."` |
| Unauthenticated / unauthorized role access | `@login_required` or `book_ticket` guard blocks execution | `302` redirect to `/login` or `/` + flash alert |
| Cross-user ticket cancel attempt (IDOR) | `order.user_id != session['user_id']` stops before `begin_nested()` | `302` redirect to `/my-tickets` + danger flash |
| Reqly collector unreachable or `REQLY_API_KEY` missing | Background worker retries/drops batch; Flask app unaffected | Zero visible error to end user |
| Non-existent entity ID (`/events/99999`) | Flask-SQLAlchemy `.get_or_404()` aborts cleanly | `404 Not Found` |

---

## 8. Non-Functional Requirements & Budgets

- **Latency:** Server-rendered SQLite queries respond in sub-50ms warm locally; Render free tier cold starts sleep after 15m inactivity and wake in ~30s.
- **Security:** `bcrypt` per-user salted password hashes; forced `attendee` role on `/signup`; ownership guard on `/tickets/<id>/cancel`; server-only secrets via `.env` / Render env vars; salted Reqly consumer hashing. *(Known v1 gaps tracked for v2: no CSRF token middleware on forms; `SECRET_KEY` has a dev fallback in `app.py` if unset.)*
- **Cost & Spend Ceiling:** `$0/mo` running entirely within Render free web-service and local SQLite file storage.
- **Reliability:** Multi-row writes use SQLAlchemy transaction rollback on exception; Reqly telemetry is fail-open and bounded by a background thread queue.
- **Accessibility & UI:** Semantic `<header>`, `<nav>`, `<main>`, `<footer>`, form `<label>` associations, responsive CSS grids, and consistent `#008080` teal theme.

---

## 9. Unit Economics & Quota Budget

| Resource | Free-Tier / Plan Limit | Estimated Usage per 1,000 Actions | Headroom / Scaling Note |
|---|---|---|---|
| Compute (Render Web Service) | 750 free instance hrs/mo · 512 MB RAM | < 1 instance-hr active compute | Sleeps after 15m idle (~30s wake); single process |
| Database (SQLite on Render disk) | Ephemeral container disk | < 1 MB for demo records | Reset on deploy/restart; migrate to Postgres for durability |
| Observability (Reqly Collector & Dashboard) | Self-hosted Render free tier | ~1,000 telemetry events (~200 KB) | Configurable via `REQLY_SAMPLE_RATE` (`0` in tests) |

---

## 10. Success Metrics & Instrumentation

| Metric | Target | How Measured |
|---|---|---|
| Live demo availability | All 3 seeded roles log in and complete primary CRUD/booking flows | Manual post-deploy smoke verification on `eventflow-g2h5.onrender.com` |
| Regression safety | 100% pass rate on `tests/test_smoke.py` (5 E2E role tests) & `compileall` | GitHub Actions `CI` workflow on every push & PR to `master` |
| Security scanning | 0 high/critical CodeQL or Gitleaks findings | GitHub Actions `CodeQL`, `Secret Scan`, and `Dependency Review` |
| Reqly telemetry delivery | Live route p50/p95/p99 and release tracking visible within ~60s | Public Reqly dashboard (`reqly-eventflow-dashboard.onrender.com`) |

---

## 11. Risks, Assumptions & Open Questions

| Item | Impact | Mitigation / Status |
|---|---|---|
| **Ephemeral SQLite disk on Render free tier** | High (data resets on deploy/sleep cycle) | `start.py` re-initializes schema + demo accounts automatically on boot |
| **No CSRF tokens on HTML forms** | Medium | Tracked as top v2 hardening item (`Flask-WTF` / `CSRFProtect`) |
| **Concurrent last-seat booking race** | Medium | Single-writer SQLite limits concurrency today; replace read-then-decrement with atomic `UPDATE ... WHERE quantity >= :qty` in v2 |
| **Single `app.py` module (787 lines) & Flask dev server in `start.py`** | Low–Medium | `gunicorn>=26.2.0` is already in `requirements.txt`; split into Blueprints + WSGI startup in v2 |

---

## 12. v2 Candidates

- **CSRF & boundary validation hardening** — Add `Flask-WTF` CSRF tokens across all forms and Pydantic/WTForms schema validation before route writes.
- **Gunicorn WSGI production startup** — Update `start.py` / `render.yaml` to run `gunicorn` after DB bootstrap.
- **PostgreSQL + Alembic migrations** — Persist production events and bookings across deploys and support forward-only schema migrations.
- **Stripe test-mode checkout** — Populate the existing `Payment` table (`payment_method`, `transaction_id`) during booking.
- **Per-organizer event ownership & `/events` filter wiring** — Restrict organizer edit/delete to `event.organizer_id == session['user_id']` and connect `events.html`'s `search` / `date` query inputs to `list_events()`.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
