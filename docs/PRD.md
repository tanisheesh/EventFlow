# EventFlow — Product Requirements Document

**Status:** Final (v1 live)
**Owner:** Tanish Poddar
**One-liner:** Event management in Flask: organizers run events, venues, speakers and ticket types; attendees book and cancel tickets. Monitored live by Reqly.

---

## 1. Problem

Small event organizers juggle events, venues, speakers and ticket stock across spreadsheets, and attendees
have no single place to see what's on and what they've booked. EventFlow puts both sides in one web app
with role-based access. It also serves a second purpose: a real, multi-route application with logins and
writes that [Reqly](https://github.com/tanisheesh/reqly) can monitor in public, so Reqly's dashboard shows
real traffic instead of synthetic data.

---

## 2. Goals (v1)

1. Email and password signup and login, with passwords stored as bcrypt hashes.
2. Three roles with enforced access: attendee, organizer and administrator.
3. Organizers can create, edit and delete events, venues, speakers and ticket types from one dashboard.
4. Attendees can book one or more tickets of a type, see them under "My tickets" and cancel them.
5. Ticket stock never goes below zero, and cancellations return stock.
6. Deployed with a live demo URL and ready-made demo accounts for every role.
7. Every route monitored by Reqly, with a public metrics dashboard linked from the app.

---

## 3. Non-Goals

- **Real payments** — bookings create orders without charging anyone. The `Payment` table exists in the schema but nothing writes to it yet.
- **Email notifications** — no booking confirmations or reminders.
- **Seat maps** — tickets have an optional `seat_number`, but there is no seat picker.
- **Per-organizer ownership** — events record who created them, but every organizer can manage every event.

---

## 4. Users

**Primary:** Event organizers who need to publish events and track ticket sales, and the attendees who book them.

**Secondary:** Developers evaluating Reqly, who use EventFlow as the live app behind Reqly's demo dashboard.

---

## 5. User Stories

1. *As an attendee,* I browse upcoming events and open one to see its venue, speakers and ticket types, so that I can decide what to attend.
2. *As an attendee,* I book several tickets of one type in one go, so that my group is covered by one order.
3. *As an attendee,* I cancel a ticket from "My tickets", so that its seat goes back on sale and my order total is updated.
4. *As an organizer,* I create an event with a venue, speakers and priced ticket types, so that attendees can book it.
5. *As an organizer,* I see all events, venues, speakers, tickets and orders on one dashboard, so that I know where sales stand.
6. *As an administrator,* I list and remove organizer accounts, so that only trusted people run events.
7. *As a Reqly evaluator,* I open the metrics dashboard from the app, so that I can see latency and errors for the requests I just made.

---

## 6. Functional Requirements

### 6.1 Auth

- Signup always creates an attendee; organizer and administrator accounts are seeded, not self-served.
- Login stores the user id, name and role in a signed session cookie; logout clears it.
- Protected routes redirect to login when signed out, and to the home page when the role is wrong. Administrators pass every role check.

### 6.2 Events, venues and speakers

- Organizers can create, edit and delete each. An event belongs to one venue and has any number of speakers.

### 6.3 Tickets and orders

- Booking checks that the ticket type exists and that the requested quantity is between 1 and the remaining stock.
- A booking creates one order and one ticket row per seat, and decrements stock, in one transaction.
- Cancelling a ticket deletes it, returns one unit of stock, and updates the order total, or deletes the order if it was the last ticket. Only the ticket's owner can cancel it.

### 6.4 Monitoring

- Every request is reported to the Reqly collector with its route template, status, latency, release and hashed user id.
- Monitoring must never break the app: with no collector configured or reachable, EventFlow works the same.

---

## 7. Non-Functional Requirements

- **Security:** passwords hashed with bcrypt; secrets only in environment variables; user ids hashed with a secret salt before they reach Reqly.
- **Cost:** runs on Render's free web service plan with SQLite, with no paid services.
- **Reliability:** Reqly sends from a background thread with a bounded queue, so a slow collector never delays a request.

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Live demo | Every demo account can log in and complete its role's main flow on the live URL |
| Reqly demo | Requests made in EventFlow appear on the Reqly dashboard within a minute |

---

## 9. Risks & Open Questions

- **Ephemeral data** — SQLite on Render's free plan lives on the service's local disk, so data is reset on every deploy or restart (demo accounts are re-created on start).
- **Cold starts** — the free plan sleeps when idle, so the first request takes about 30 seconds.
- **No CSRF tokens** — forms rely on the session cookie alone.

---

## 10. v2 Candidates

- Real payments (Stripe test mode) writing to the existing `Payment` table — the biggest missing piece of the booking flow.
- Event ownership per organizer, so organizers only manage their own events.
- Postgres instead of SQLite, so data survives deploys.
- Booking confirmation emails.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
