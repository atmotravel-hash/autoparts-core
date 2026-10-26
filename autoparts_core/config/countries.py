"""Configurable country registry — not hardcoded throughout the app."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Country:
    iso_code: str
    display_name: str
    default_currency: str
    languages: tuple[str, ...]
    enabled_sources: tuple[str, ...] = ()
    delivery_region: str = "EU"
    eu_member: bool = False
    tax_import_notes: str = ""
    enabled: bool = True


# Priority markets from Spec §4
COUNTRY_REGISTRY: dict[str, Country] = {
    c.iso_code: c
    for c in [
        Country("DE", "Germany", "EUR", ("de", "en"), eu_member=True, delivery_region="EU"),
        Country("PL", "Poland", "PLN", ("pl", "en"), eu_member=True, delivery_region="EU"),
        Country("LT", "Lithuania", "EUR", ("lt", "en", "ru"), eu_member=True, delivery_region="EU"),
        Country("LV", "Latvia", "EUR", ("lv", "en", "ru"), eu_member=True, delivery_region="EU"),
        Country("EE", "Estonia", "EUR", ("et", "en", "ru"), eu_member=True, delivery_region="EU"),
        Country("CZ", "Czechia", "CZK", ("cs", "en"), eu_member=True, delivery_region="EU"),
        Country("SK", "Slovakia", "EUR", ("sk", "en"), eu_member=True, delivery_region="EU"),
        Country("RO", "Romania", "RON", ("ro", "en"), eu_member=True, delivery_region="EU"),
        Country("BG", "Bulgaria", "BGN", ("bg", "en"), eu_member=True, delivery_region="EU"),
        Country("HU", "Hungary", "HUF", ("hu", "en"), eu_member=True, delivery_region="EU"),
        Country("AT", "Austria", "EUR", ("de", "en"), eu_member=True, delivery_region="EU"),
        Country("FR", "France", "EUR", ("fr", "en"), eu_member=True, delivery_region="EU"),
        Country("IT", "Italy", "EUR", ("it", "en"), eu_member=True, delivery_region="EU"),
        Country("ES", "Spain", "EUR", ("es", "en"), eu_member=True, delivery_region="EU"),
        Country("NL", "Netherlands", "EUR", ("nl", "en"), eu_member=True, delivery_region="EU"),
        Country("BE", "Belgium", "EUR", ("nl", "fr", "de", "en"), eu_member=True, delivery_region="EU"),
        Country("SE", "Sweden", "SEK", ("sv", "en"), eu_member=True, delivery_region="EU"),
        Country("FI", "Finland", "EUR", ("fi", "en"), eu_member=True, delivery_region="EU"),
        Country("DK", "Denmark", "DKK", ("da", "en"), eu_member=True, delivery_region="EU"),
        Country("IE", "Ireland", "EUR", ("en"), eu_member=True, delivery_region="EU"),
        Country("PT", "Portugal", "EUR", ("pt", "en"), eu_member=True, delivery_region="EU"),
        Country("HR", "Croatia", "EUR", ("hr", "en"), eu_member=True, delivery_region="EU"),
        Country("SI", "Slovenia", "EUR", ("sl", "en"), eu_member=True, delivery_region="EU"),
        Country("GR", "Greece", "EUR", ("el", "en"), eu_member=True, delivery_region="EU"),
        Country("LU", "Luxembourg", "EUR", ("fr", "de", "en"), eu_member=True, delivery_region="EU"),
        Country("CY", "Cyprus", "EUR", ("el", "en"), eu_member=True, delivery_region="EU"),
        Country("MT", "Malta", "EUR", ("en", "mt"), eu_member=True, delivery_region="EU"),
        Country(
            "MD",
            "Moldova",
            "MDL",
            ("ro", "ru", "en"),
            delivery_region="MD",
            eu_member=False,
            tax_import_notes="Non-EU; import duties may apply — mark as estimate until rules verified",
        ),
        Country(
            "UA",
            "Ukraine",
            "UAH",
            ("uk", "ru", "en"),
            delivery_region="UA",
            eu_member=False,
            tax_import_notes="Non-EU; customs/VAT estimates required — never treat as zero",
        ),
        Country("GB", "United Kingdom", "GBP", ("en"), delivery_region="UK", eu_member=False),
        Country("CH", "Switzerland", "CHF", ("de", "fr", "it", "en"), delivery_region="CH", eu_member=False),
        Country("NO", "Norway", "NOK", ("no", "en"), delivery_region="NO", eu_member=False),
    ]
}

QUERY_LANGUAGES = (
    "en",
    "de",
    "pl",
    "ro",
    "uk",
    "ru",
    "fr",
    "it",
    "es",
    "cs",
    "sk",
    "lt",
    "lv",
    "et",
    "nl",
)


def enabled_countries() -> list[Country]:
    return [c for c in COUNTRY_REGISTRY.values() if c.enabled]


def get_country(iso: str) -> Country | None:
    return COUNTRY_REGISTRY.get(iso.upper())
