<p align="center">
  <img src="docs/assets/logo.svg" width="64" height="64" alt="EventFlow">
</p>

<h1 align="center">EventFlow</h1>

<p align="center">
  <strong>Event management in Flask: organizers run events, venues, speakers and ticket types; attendees book and cancel tickets. Monitored live by Reqly.</strong>
</p>

<p align="center">
  <a href="https://eventflow-g2h5.onrender.com"><img src="https://img.shields.io/badge/live_demo-008080?style=flat-square" alt="Live Demo"></a>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black" alt="Render">
  <img src="https://img.shields.io/badge/license-GPL--3.0-008080?style=flat-square" alt="License">
</p>

---

## What is EventFlow?

EventFlow is a small, complete event-ticketing app: organizers publish events with venues, speakers and
priced ticket types, and attendees browse, book and cancel tickets, with stock kept in sync on every
booking and cancellation. It is also the live demo for [Reqly](https://github.com/tanisheesh/reqly), the
self-hosted API observability tool, so every request it serves shows up on a public metrics dashboard.

> **Live demo →** [eventflow-g2h5.onrender.com](https://eventflow-g2h5.onrender.com) (free tier, the first load can take ~30s)

| Role | Email | Password |
|---|---|---|
| 👑 Administrator | `admin@eventhub.com` | `Admin@123` |
| 🎯 Organizer | `organizer@eventhub.com` | `Organizer@123` |
| 🛒 Attendee | `buyer@eventhub.com` | `Buyer@123` |

The login page has "Use these" buttons for each account.

---

## What you get

- **Three roles** — attendees book tickets, organizers manage everything on a dashboard, administrators also manage organizers
- **Events, venues and speakers** — create, edit and delete each from the organizer dashboard
- **Ticket types with stock** — priced tiers with a quantity that goes down on booking and back up on cancellation
- **Orders** — booking several tickets creates one order; cancelling the last ticket removes it
- **Live API monitoring** — latency, errors, releases and per-user traffic in [Reqly](#monitored-by-reqly)

---

## Monitored by Reqly

EventFlow is instrumented with the [`reqly`](https://pypi.org/project/reqly/) Python SDK in one call:

```python
reqly.instrument(app, service_name="eventflow", consumer=reqly_consumer)
```

| | |
|---|---|
| **Metrics dashboard** | [reqly-eventflow-dashboard.onrender.com](https://reqly-eventflow-dashboard.onrender.com) (public, read-only) |
| **Collector API** | [reqly-eventflow-collector.onrender.com/docs](https://reqly-eventflow-collector.onrender.com/docs) |
| **Reqly docs** | [reqly.tanisheesh.in/docs](https://reqly.tanisheesh.in/docs/) |

Every route reports p50/p95/p99 latency, error rate and status codes, tagged with the deployed commit
(`RENDER_GIT_COMMIT`) and the logged-in user, hashed with `REQLY_CONSUMER_SALT` before it leaves the app.
If the collector is down, EventFlow keeps working: the SDK is fail-open. In the app, log in as the
administrator and click **Metrics** in the nav bar, or follow "Monitored by Reqly" in the footer.

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | Jinja2 templates · CSS · vanilla JS |
| Backend | Python · Flask 3 · Flask-SQLAlchemy |
| Database | SQLite |
| Auth | Flask sessions · bcrypt password hashes · role decorators |
| Observability | Reqly Python SDK |
| Infra | Render (Blueprint in `render.yaml`) |

---

## Run it locally

```bash
git clone https://github.com/tanisheesh/EventFlow && cd EventFlow
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                              # set SECRET_KEY
python start.py                                   # creates tables + demo accounts, serves :5000
```

Full guide, including running a local Reqly collector: [docs/SETUP.md](docs/SETUP.md).

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements — goals, user stories, non-goals |
| [Architecture](docs/ARCHITECTURE.md) | System design, data flow, component breakdown |
| [Decisions](docs/DECISIONS.md) | Every major technical decision and why |
| [Setup](docs/SETUP.md) | Local dev setup and env vars |
| [Deploy](docs/DEPLOY.md) | Production deployment on Render, rollback |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Security](SECURITY.md) | How to report a vulnerability |

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
