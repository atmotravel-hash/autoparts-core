"""Landed cost calculation with explicit unknowns."""

from __future__ import annotations

from decimal import Decimal

from autoparts_core.core.enums import DeliveryEligibility
from autoparts_core.core.models import Money, PriceBreakdown
from autoparts_core.pricing.fx import convert


def build_price_breakdown(
    *,
    item_amount: float | Decimal | None,
    item_currency: str | None,
    shipping_amount: float | Decimal | None = None,
    shipping_currency: str | None = None,
    target_currency: str = "EUR",
    delivery_eligibility: str | DeliveryEligibility = DeliveryEligibility.UNKNOWN,
    known_taxes: float | Decimal | None = None,
    tax_currency: str | None = None,
    allow_fixture_fx: bool = True,
) -> PriceBreakdown:
    warnings: list[str] = []
    assumptions: list[str] = []
    unknowns: list[str] = []

    item_converted, fx_quote, w1 = convert(
        Decimal(str(item_amount)) if item_amount is not None else None,
        item_currency,
        target_currency,
        allow_fixture=allow_fixture_fx,
    )
    warnings.extend(w1)

    ship_converted = None
    if shipping_amount is None:
        unknowns.append("shipping")
        warnings.append("Shipping cost unknown — not treated as zero")
    else:
        ship_cur = shipping_currency or item_currency
        ship_converted, _, w2 = convert(
            Decimal(str(shipping_amount)),
            ship_cur,
            target_currency,
            allow_fixture=allow_fixture_fx,
        )
        warnings.extend(w2)

    tax_converted = None
    if known_taxes is None:
        unknowns.append("taxes_duties_fees")
        warnings.append("Taxes/duties/fees unknown — not treated as zero")
    else:
        tax_converted, _, w3 = convert(
            Decimal(str(known_taxes)),
            tax_currency or item_currency,
            target_currency,
            allow_fixture=allow_fixture_fx,
        )
        warnings.extend(w3)
        assumptions.append("Known tax/fee amount supplied by caller")

    estimated = None
    if item_converted is not None:
        estimated = item_converted
        if ship_converted is not None:
            estimated += ship_converted
        else:
            assumptions.append("Estimated landed excludes unknown shipping")
        if tax_converted is not None:
            estimated += tax_converted
        else:
            assumptions.append("Estimated landed excludes unknown taxes/duties")

    eligibility = (
        delivery_eligibility
        if isinstance(delivery_eligibility, DeliveryEligibility)
        else DeliveryEligibility(delivery_eligibility)
    )

    return PriceBreakdown(
        item_original=Money(
            amount=Decimal(str(item_amount)) if item_amount is not None else None,
            currency=item_currency,
        ),
        item_converted=Money(amount=item_converted, currency=target_currency)
        if item_converted is not None
        else None,
        shipping_original=Money(
            amount=Decimal(str(shipping_amount)) if shipping_amount is not None else None,
            currency=shipping_currency or item_currency,
        )
        if shipping_amount is not None
        else None,
        shipping_converted=Money(amount=ship_converted, currency=target_currency)
        if ship_converted is not None
        else None,
        known_taxes_fees=Money(amount=tax_converted, currency=target_currency)
        if tax_converted is not None
        else None,
        estimated_landed=Money(amount=estimated, currency=target_currency) if estimated is not None else None,
        unknown_cost_components=unknowns,
        fx_rate=fx_quote.rate if fx_quote else None,
        fx_provider=fx_quote.provider if fx_quote else None,
        fx_timestamp=fx_quote.as_of if fx_quote else None,
        delivery_eligibility=eligibility,
        assumptions=assumptions,
        warnings=warnings,
    )
