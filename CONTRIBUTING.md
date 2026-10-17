# Contributing to Lumen AI

Thanks for helping. Lumen is a privacy-first project, so a few rules go beyond the usual.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q
```

## Principles
- **No new personal data without justification.** If a change collects, stores or transmits new data, update `docs/fr/aipd-dpia.md` and the privacy notice in the same pull request.
- **Never commit real data**: no real names, e-mails, prompts, databases, logs or keys, in code, tests, screenshots or issues.
- **Security fixes need a test.** Behavioural changes to rights, retention, audit or compliance rules need tests too.
- Keep dependencies few and open source.
- Code and UI are in English; documents in `docs/fr/` are in French.

## Pull request checklist
- [ ] `pytest -q` passes
- [ ] No secrets or personal data in the diff
- [ ] Docs and privacy notice updated if data handling changed
- [ ] `CHANGELOG.md` updated
