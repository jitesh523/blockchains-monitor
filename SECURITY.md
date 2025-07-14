# SECURITY.md

## Input Validation and Secret Handling Guidance

- **Secrets** should be managed only through environment variables or an external secret manager. Never check `.env` (containing secrets) into your repo.
- **Input Event Validation** is performed in `validation.py` — extend it to cover any event/feed payload your system receives.

See code comments for rate limiting/429-retry best practices, and review your deployment for DDOS protection solutions (e.g., Cloudflare, AWS Shield).

