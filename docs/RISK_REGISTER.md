# Risk register

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | No live authorized source access | High | Fixture + manual import; never claim live |
| R2 | Scope creep | High | Milestone gating |
| R3 | Fitment false positives | Critical | Evidence-gated statuses |
| R4 | ToS / unauthorized scraping | Critical | API-first; no CAPTCHA bypass |
| R5 | Unknown costs treated as zero | High | Explicit unknowns + warnings |
| R7 | SSRF via URL import | High | Scheme/IP allowlisting |
| R8 | Destructive merges | High | Review UI; reversible merge history |
