# Security and compliance notes

- External content is untrusted.
- `validate_public_url` blocks localhost, private/link-local/reserved IPs, metadata endpoints, and non-http(s) schemes.
- Export cells are sanitized against spreadsheet formula injection.
- Secrets belong in environment variables (see `.env.example`); never commit keys.
- Do not bypass CAPTCHA, auth, paywalls, or rate limits.
- Store only public business contacts relevant to sourcing.
- VIN retention should be minimized; VIN is not included in default exports.
- Demo mode must remain clearly labelled.
