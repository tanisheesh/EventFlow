# Local Setup — EventFlow

> **Just want to try it?** Use the live demo at [eventflow-g2h5.onrender.com](https://eventflow-g2h5.onrender.com) — no setup needed.
> This guide is for running EventFlow locally or self-hosting it.

---

## Prerequisites

- Python 3.9+
- Git
- Optional: Docker, to run a local Reqly collector and dashboard

---

## 1. Clone and install

```bash
git clone https://github.com/tanisheesh/EventFlow
cd EventFlow
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable | Where to get it |
|---|---|
| `SECRET_KEY` | Any long random string: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | Default `sqlite:///eventhub.db` (created under `instance/`) |
| `PORT` | Port for `start.py`, default `5000` |
| `REQLY_COLLECTOR_URL` | Your Reqly collector, e.g. `http://localhost:8000`. Optional |
| `REQLY_API_KEY` | The collector's `REQLY_INGEST_KEY`. Optional |
| `REQLY_ENVIRONMENT` | Label for this deployment, e.g. `development` |
| `REQLY_CONSUMER_SALT` | Any random string; user ids are hashed with it before they're sent |
| `REQLY_DASHBOARD_URL` | Reqly dashboard URL, linked from the nav for administrators |

All `REQLY_*` variables are optional: without a collector, EventFlow runs normally.

---

## 3. Database setup

Nothing to run: `start.py` creates the tables and the demo accounts. To do it by hand:

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python create_admin_users.py
```

---

## 4. Run locally

```bash
python start.py
```

EventFlow will be running at `http://localhost:5000`. Log in with the demo accounts in the
[README](../README.md#what-is-eventflow).

### With a local Reqly collector

```bash
git clone https://github.com/tanisheesh/reqly && cd reqly && docker compose up -d
```

Then set `REQLY_COLLECTOR_URL=http://localhost:8000`, `REQLY_API_KEY=demo-key` (the compose default) and
`REQLY_DASHBOARD_URL=http://localhost:5173`, and restart EventFlow. See the
[Reqly quickstart](https://reqly.tanisheesh.in/docs/quickstart/).

---

## 5. Deploy to production

See [DEPLOY.md](DEPLOY.md) for production deployment and rollback steps.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hey@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hey%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
