# EventFlow — Architecture

---

## 1. Stack

| Layer | Tech |
|---|---|
| Framework | Flask 3 (server-rendered Jinja2 templates) |
| Auth | Flask signed-cookie sessions, bcrypt password hashes |
| Database | SQLite |
| ORM | Flask-SQLAlchemy 3.0 on SQLAlchemy 1.4 |
| Styling | Plain CSS (`static/css/style.css`), teal `#008080` theme |
| Client JS | Vanilla JS (`static/js/`) for form validation |
| Observability | Reqly Python SDK (`reqly>=0.5.4`) |
| Hosting | Render free web service, defined in `render.yaml` |

---

## 2. Components

```
app.py                  Flask app: config, models, decorators, all routes, Reqly setup
start.py                Production entry point: create tables, seed demo users, serve
create_admin_users.py   Seeds the three demo accounts (idempotent)
config.py               Config classes per environment (development / testing / production)
schema_sqlite.sql       Reference SQL for the same schema
templates/              Jinja2 pages, all extending layout.html
static/                 CSS, JS, favicon
```

### Models (`app.py`)

`User`, `Venue`, `Event`, `Speaker`, `TicketType`, `Order`, `Ticket` and `Payment` as Flask-SQLAlchemy
models. Tables are created by `db.create_all()` at start-up; there is no migration tool.

### Access control (`login_required`, `organizer_required`)

A decorator loads the user from `session['user_id']` on every protected request. Signed-out users go to
`/login`; users with the wrong role go to `/`. Administrators pass every check, and organizers may also use
attendee views. Booking checks `session['user_role'] == 'attendee'` directly.

### Reqly instrumentation

`reqly.instrument(app, service_name="eventflow", consumer=reqly_consumer)` hooks Flask's request lifecycle.
`reqly_consumer` returns the logged-in user id from the session; the SDK hashes it with
`REQLY_CONSUMER_SALT` (HMAC-SHA256) before it is queued. Collector URL, ingest key and environment come from
`REQLY_*` environment variables, and the release from `RENDER_GIT_COMMIT`. Events are batched and sent by a
background thread, so requests never wait on the collector.

---

## 3. Data Flow

```
[Browser] --form POST--> [Flask route]
     |                        |-- decorator: session -> User -> role check
     |                        |-- SQLAlchemy: read / write SQLite (one transaction)
     |<--302 / HTML-----------|-- flash() message + redirect, or render_template
                              |
                              '-- teardown: Reqly records route, status, latency,
                                  hashed user id -> queue -> background thread
                                  -> POST batch to the Reqly collector
```

Booking a ticket, end to end:

1. An attendee submits the ticket type and quantity on `/events/<id>` to `POST /book_ticket/<id>`.
2. The route checks the session role, the ticket type and `1 <= quantity <= stock`.
3. In one transaction it creates an `Order`, one `Ticket` per seat, and decrements `TicketType.quantity`.
4. On any error the transaction is rolled back and the error is logged.
5. The user is redirected back to the event page with a flash message; the booking shows in `/my-tickets`.

---

## 4. Database Schema

- `user` — `user_id`, `name`, unique `email`, bcrypt `password`, `user_type` (`attendee` / `organizer` / `administrator`)
- `venue` — `venue_id`, `name`, `address`, `capacity`, `city`, `state`, `zip_code`
- `event` — `event_id`, `name`, `description`, `date`, `time`, `location_id` → venue, `organizer_id` → user (who created it)
- `speaker` — `speaker_id`, `name`, `bio`, `event_id` → event
- `tickettype` — `ticket_type_id`, `event_id` → event, `type`, `price`, `quantity` (remaining stock)
- `order` — `order_id`, `user_id` → user, `date`, `total_price`, `payment_id` → payment
- `ticket` — `ticket_id`, `event_id` → event, `order_id` → order, `price`, `type`, `seat_number`
- `payment` — `payment_id`, unique `order_id`, `payment_method`, `transaction_id` (defined, not written yet)

No indexes beyond primary keys and the unique `email` / `order_id` constraints.

---

## 5. Routes

| Method | Route | Access | Description |
|---|---|---|---|
| `GET` | `/`, `/events`, `/events/<id>` | public | Home, event list, event details with ticket types |
| `GET POST` | `/login`, `/signup` | public | Sign in; sign up as an attendee |
| `GET` | `/logout` | any | Clear the session |
| `GET` | `/dashboard` | organizer | Events, venues, speakers, tickets and orders |
| `GET POST` | `/events/create`, `/events/<id>/edit` | organizer | Event form |
| `POST` | `/events/<id>/delete` | organizer | Delete an event |
| `GET POST` | `/venues/create`, `/venues/<id>/edit`, `/speakers/...` | organizer | Venue and speaker CRUD |
| `GET POST` | `/events/<id>/tickets/manage` | organizer | Ticket types and stock |
| `GET` | `/events/<id>/tickets` | organizer | Tickets sold for an event |
| `POST` | `/book_ticket/<id>` | attendee | Book tickets |
| `GET` | `/my-tickets` | attendee | The user's orders and tickets |
| `POST` | `/tickets/<id>/cancel` | attendee (owner) | Cancel a ticket, return stock |
| `GET` | `/admin/organizers` | administrator | List organizers |
| `POST` | `/admin/organizers/<id>/delete` | administrator | Remove an organizer |

---

## 6. Security

- **Secrets:** `SECRET_KEY`, `REQLY_API_KEY` and `REQLY_CONSUMER_SALT` come from the environment only. `.env` is gitignored; on Render, `SECRET_KEY` and `REQLY_CONSUMER_SALT` are generated by the Blueprint and `REQLY_API_KEY` is set in the dashboard.
- **Passwords:** bcrypt with a per-password salt (`bcrypt.gensalt()`).
- **Roles:** checked server-side on every protected route; signup always creates an attendee, whatever the form sends.
- **Ownership:** cancelling a ticket checks that its order belongs to the session user.
- **Monitoring privacy:** Reqly records route templates (`/events/<int:event_id>`), never raw paths, query strings or bodies, and only a salted hash of the user id.
- **Not yet:** no CSRF tokens on forms.

---

## 7. Error Handling & Reliability

| Failure | Behaviour |
|---|---|
| DB error while booking or cancelling | Transaction rolled back, flash message, redirect; nothing half-written |
| Duplicate email on signup | `IntegrityError` caught, "Email address already exists" |
| Reqly collector down or slow | Requests unaffected; the SDK retries a batch, then drops it and logs a warning |
| Error inside the Reqly SDK | Logged once, instrumentation switches itself off; the app keeps serving |

---

## 8. Deployment

1. Render web service from `render.yaml`: `pip install -r requirements.txt`, then `python start.py`.
2. `start.py` creates the tables and the demo accounts on every start, then serves on `$PORT`.
3. Pushes to `master` redeploy automatically. Details in [DEPLOY.md](DEPLOY.md).

---

## 9. Explicit Scope Cuts

- **Payments** — the `Payment` model is in place, but bookings don't charge.
- **Migrations** — `db.create_all()` only creates missing tables; `start.py` adds the one later column (`event.organizer_id`) by hand. Further schema changes need the same.
- **Event ownership** — events record their organizer (used by the admin page), but every organizer can still manage every event.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hey%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
