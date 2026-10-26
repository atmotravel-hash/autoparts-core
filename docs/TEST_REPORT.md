# Test report

**Run:** 26 Oct 2026, ~06:00 Europe/Chisinau (EET)  
**Command:** `pytest -q`  
**Environment:** Python 3.12.3, local SQLite, no live API credentials  

## Result

**26 passed**, 0 failed.

## Coverage exercised

- OEM normalization / similarity
- Multilingual taxonomy + side detection
- Fitment evidence (exact / title-only / incompatible)
- FX fixture provenance + unknown shipping
- SSRF URL blocking + export formula sanitization
- Duplicate scoring (exact URL; OEM-alone insufficient)
- CSV/XLSX import-export reconcile
- Fixture connector search + persistence
- Condition / completeness maps
- Discovery query generation

## Live integrations

None. Live-source tests are intentionally absent (opt-in only when credentials exist).
