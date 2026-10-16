# Engineering Decisions — EventFlow

---

## Decision 1 — SQLite created and seeded at start-up

**Context:** The live demo runs on Render's free web service plan, which has no managed database and no persistent disk.

**Decision:** SQLite through Flask-SQLAlchemy. `start.py` runs `db.create_all()` and seeds the three demo accounts on every start.

**Reason:** No database service to provision or pay for, and the demo is always in a known state with working logins, even after the disk is wiped by a redeploy.

**Tradeoff:** Data created on the live demo is lost on every deploy or restart, and SQLite allows one writer at a time. There are no migrations, so schema changes on existing data are manual.

---

## Decision 2 — Roles in one decorator, administrator passes every check

**Context:** Three roles share most pages: attendees book, organizers manage, administrators do both and manage organizers.

**Decision:** One `login_required(role)` decorator that loads the user from the session and compares `user_type`. Administrators always pass, and organizers may use attendee views.

**Reason:** Access rules live in one place, and every protected route states its role in its decorator, so a route's access level is visible at a glance.

**Tradeoff:** The role check is a flat comparison, not a permission model, so finer rules (an organizer managing only their own events) would need a different design.

---

## Decision 3 — Ticket stock as a counter, changed in the same transaction as the order

**Context:** Booking and cancelling must keep `TicketType.quantity` consistent with the tickets that exist.

**Decision:** Booking creates the order and tickets and decrements the counter in one transaction; cancelling deletes the ticket, increments the counter and updates or deletes the order in one transaction. Any exception rolls back.

**Reason:** A failure in the middle never leaves stock out of step with tickets, and remaining stock is one column read instead of a count over all tickets.

**Tradeoff:** The stock check and the decrement aren't atomic across concurrent requests, so two simultaneous bookings for the last seat could both pass the check.

---

## Decision 4 — Monitoring with Reqly, fail-open and privacy-preserving

**Context:** EventFlow is the live demo for Reqly, so it needs real monitoring, but monitoring must never take the app down.

**Decision:** One `reqly.instrument()` call with the logged-in user as the consumer, the user id hashed with a secret salt in the SDK, and the release read from `RENDER_GIT_COMMIT`.

**Reason:** The SDK sends from a background thread and turns itself off on internal errors, so a collector outage costs data, not uptime. Hashing in the app means the collector never stores real user ids, yet "which users did this incident hit" still works.

**Tradeoff:** Hashed ids can't be mapped back to accounts from the Reqly dashboard alone.

---

## What I'd do differently in v2

- **CSRF tokens on every form** — forms currently rely on the session cookie alone.
- **Gunicorn in production** — `gunicorn` is already a dependency, but `start.py` serves with Flask's built-in server.
- **Postgres with migrations** — so data survives deploys and the schema can change safely.
- **Ownership checks** — events now record their organizer; organizers should only be able to edit and delete their own.

---

## Explicit non-decisions (deferred to v2)

| Feature | Why deferred |
|---|---|
| Real payments | Booking flow first; the `Payment` table is ready for a Stripe test-mode integration |
| Email confirmations | Needs a mail provider and background sending; not needed for the demo |

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hey%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
