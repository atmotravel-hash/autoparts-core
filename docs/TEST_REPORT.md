# Test report

**Run:** 26 Oct 2026, Europe/Chisinau (EET)

## Default suite
```
pytest -q
```
**32 passed**, 2 skipped (live markers).

## Live GraphQL
```
RUN_LIVE_GRAPHQL=1 pytest -m live -q
```
**2 passed** (OLX UA search + 999.md health).

## E2E smoke
Passat B8 headlight → 51 live listings ingested from olx_ua/olx_pl/nine99_md (0 connector crashes).
