# Known limitations

- **No live marketplace connector has been tested.** eBay, Allegro, AUTODOC, Ovoko stubs are non-operational.
- **Brave Search** not configured — Discovery page generates queries only.
- **FX rates** in demo mode come from `fixture_rates_v1`, not a live provider.
- **VIN decode** not integrated; VIN field is accepted but unused for fitment.
- **Manual URL import** stores metadata only — does not scrape protected pages.
- **Job workers** persist queue rows but do not yet run a background scheduler loop.
- **PostgreSQL** path is schema-compatible via SQLAlchemy URL but not production-hardened here.
- **Image hashes / perceptual duplicate** not computed (no image download by default).
- Fixture listings are **demo data** and must not be presented as current availability.
