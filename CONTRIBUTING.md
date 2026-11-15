# Contributing to EventFlow

Thanks for taking the time to contribute! Bug reports, fixes, docs improvements and feature ideas are all welcome.

---

## Before you start

- **Found a bug?** Open a [bug report](../../issues/new?template=bug_report.yml). Search existing issues first.
- **Have an idea?** Open a [feature request](../../issues/new?template=feature_request.yml) before writing code, so we can agree on the approach.
- **Found a security issue?** Don't open a public issue. Follow [SECURITY.md](SECURITY.md).
- Small fixes (typos, docs, obvious bugs) can go straight to a pull request.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Local setup

Full instructions are in [docs/SETUP.md](docs/SETUP.md). Short version:

```bash
git clone https://github.com/<your-username>/EventFlow   # your fork
cd EventFlow
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python start.py
```

---

## Workflow

1. **Fork** the repo and create a branch from `master`:

   | Branch prefix | Use for |
   |---|---|
   | `feat/` | new feature, e.g. `feat/event-search-filter` |
   | `fix/` | bug fix, e.g. `fix/ticket-stock-race` |
   | `docs/` | documentation only |
   | `chore/` | tooling, config, dependencies |
   | `refactor/` | code change with no behaviour change |

2. **Make your change.** Keep it focused, one feature or fix per PR, following [AGENTS.md](AGENTS.md).
3. **Check it locally** before pushing:

   ```bash
   python -m compileall -q -x '(\.venv|venv|node_modules|\.git)/' . && python -m pytest -q
   ```

4. **Open a pull request** against `master`. Use a clean **past-tense** PR title (e.g. `Added server-side search filter for events`). The PR template will guide you.

---

## Commit messages

Commits follow an emoji-prefixed format:

```
<emoji> [#issue] [scope:] <message in present tense, lowercase>
```

| Emoji | Type | Example |
|---|---|---|
| ✨ | New feature | `✨ #12 add csv attendee export` |
| 🐛 | Bug fix | `🐛 auth: fix redirect loop on logout` |
| 🎊 | Improvement | `🎊 speed up dashboard load` |
| ♻️ | Refactor | `♻️ extract booking service from app.py` |
| 📚 | Docs | `📚 add deploy guide` |
| 🧪 | Tests | `🧪 cover cross-user ticket cancellation guard` |
| 🔨 | Chore / config | `🔨 add coderabbit review rules` |
| 👆 | Dependency update | `👆 upgrade flask to 3.1.3` |
| 🔒 | Security | `🔒 add csrf protection to booking form` |
| 💀 | Code deletion | `💀 remove unused template partial` |

Breaking changes add a line `🚨 BREAKING CHANGE: <what breaks>` in the commit body.

---

## Code style

- Run the compile check and `pytest` before committing. CI runs the same checks.
- Follow [AGENTS.md](AGENTS.md) and existing project structure.
- Python: PEP 8 (`snake_case` for modules/functions, `PascalCase` for models). Templates extend `templates/layout.html`; shared styles go in `static/css/style.css`.
- No secrets in code. Use env vars and add new ones to `.env.example` with empty values.
- Update docs and tests when behaviour, setup, or env vars change.

---

## Pull request checklist

- [ ] Branch is up to date with `master`
- [ ] Compile check and `pytest` pass locally, and the app runs (`python start.py`)
- [ ] Commits follow the format above and PR title is plain-English past tense
- [ ] Docs / `.env.example` / `CHANGELOG.md` updated if needed
- [ ] PR description explains **what** and **why**

PRs are reviewed as soon as possible. Feedback is about the code, never the person.

---

<div align="center">

<h3>Tanish Poddar</h3>

<a href="https://tanisheesh.in"><img src="https://img.shields.io/badge/Website-tanisheesh.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/tanisheesh"><img src="https://img.shields.io/badge/LinkedIn-tanisheesh-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/tanisheesh"><img src="https://img.shields.io/badge/GitHub-tanisheesh-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:hi@tanisheesh.in"><img src="https://img.shields.io/badge/Email-hi%40tanisheesh.in-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
