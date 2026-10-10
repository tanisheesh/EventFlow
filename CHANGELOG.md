# Changelog

All notable changes to **EventFlow** are documented here.

---

## [1.0.0] — 2026-10-11

First tagged release, covering everything built since April 2025.

### ✨ Added
- Signup and login with three roles: attendee, organizer and administrator
- Organizer dashboard to create, edit and delete events, venues, speakers and ticket types
- Ticket booking with priced ticket types and live stock, "My tickets" and cancellation that returns stock
- Administrator page to manage organizers
- Demo accounts for every role, with "Use these" buttons on the login page
- Render deployment from `render.yaml`
- API monitoring with Reqly: latency, errors and status codes per route, a **Metrics** link for administrators and a public dashboard
- Reqly now tags each request with the logged-in user (hashed with `REQLY_CONSUMER_SALT`), the environment and the deployed commit

### 🔒 Security
- Signup always creates an attendee; the role sent by the form is ignored
- `.env` is no longer tracked in git

### 👆 Dependencies
- `reqly` pinned to `>=0.5.4`

---

[1.0.0]: https://github.com/tanisheesh/EventFlow/releases/tag/v1.0.0

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hey@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hey%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
