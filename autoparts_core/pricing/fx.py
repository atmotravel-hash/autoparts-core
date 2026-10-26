"""Currency conversion with explicit FX provenance.

Never silently replace an unavailable rate with a guess.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Clearly labelled fixture rates for offline/demo mode — NOT live market data
FIXTURE_RATES_EUR: dict[str, Decimal] = {
    "EUR": Decimal("1"),
    "USD": Decimal("1.08"),
    "GBP": Decimal("0.86"),
    "PLN": Decimal("4.30"),
    "CZK": Decimal("25.20"),
    "HUF": Decimal("395.0"),
    "RON": Decimal("4.97"),
    "BGN": Decimal("1.96"),
    "SEK": Decimal("11.50"),
    "DKK": Decimal("7.46"),
    "UAH": Decimal("43.00"),
    "MDL": Decimal("19.20"),
    "CHF": Decimal("0.94"),
    "NOK": Decimal("11.60"),
}


@dataclass
class FxQuote:
    base: str
    quote: str
    rate: Decimal
    provider: str
    as_of: datetime
    is_fixture: bool


def get_rate(
    base: str,
    quote: str,
    *,
    allow_fixture: bool = True,
    live_provider_rate: FxQuote | None = None,
) -> FxQuote | None:
    base, quote = base.upper(), quote.upper()
    if live_provider_rate is not None:
        return live_provider_rate
    if not allow_fixture:
        return None
    if base == quote:
        return FxQuote(base, quote, Decimal("1"), "identity", datetime.utcnow(), is_fixture=False)
    # Convert via EUR pivot using fixture table
    if base not in FIXTURE_RATES_EUR or quote not in FIXTURE_RATES_EUR:
        return None
    # rate such that 1 base = rate quote
    # amount_eur = amount_base / FIXTURE_RATES_EUR[base]  (since table is units per EUR)
    # wait: FIXTURE_RATES_EUR["PLN"]=4.30 means 1 EUR = 4.30 PLN
    # so 1 PLN = 1/4.30 EUR; 1 PLN in USD = (1/4.30)*1.08
    eur_per_base = Decimal("1") / FIXTURE_RATES_EUR[base]
    quote_per_eur = FIXTURE_RATES_EUR[quote]
    rate = eur_per_base * quote_per_eur
    return FxQuote(
        base=base,
        quote=quote,
        rate=rate,
        provider="fixture_rates_v1",
        as_of=datetime.utcnow(),
        is_fixture=True,
    )


def convert(
    amount: Decimal | float | None,
    from_currency: str | None,
    to_currency: str,
    *,
    allow_fixture: bool = True,
) -> tuple[Decimal | None, FxQuote | None, list[str]]:
    warnings: list[str] = []
    if amount is None or from_currency is None:
        warnings.append("Missing amount or currency — conversion skipped")
        return None, None, warnings
    quote = get_rate(from_currency, to_currency, allow_fixture=allow_fixture)
    if quote is None:
        warnings.append(
            f"No exchange rate available for {from_currency}->{to_currency}; "
            "converted price left unknown (not guessed)"
        )
        return None, None, warnings
    converted = Decimal(str(amount)) * quote.rate
    if quote.is_fixture:
        warnings.append(
            f"FX rate from fixture provider '{quote.provider}' as of {quote.as_of.isoformat()}Z — not live market data"
        )
    return converted, quote, warnings
