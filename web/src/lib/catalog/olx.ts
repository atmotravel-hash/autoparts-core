import type { SearchHit } from "./types";

const LISTING_SEARCH_QUERY = `
query ListingSearchQuery($searchParameters: [SearchParameter!]!) {
  clientCompatibleListings(searchParameters: $searchParameters) {
    __typename
    ... on ListingSuccess {
      data {
        id
        title
        url
        params {
          key
          type
          value {
            __typename
            ... on PriceParam { value currency }
          }
        }
        photos { link }
      }
    }
  }
}`;

const MARKETS: Record<
  string,
  { host: string; country: string; currency: string; name: string; partsCategory?: string }
> = {
  olx_ua: { host: "www.olx.ua", country: "UA", currency: "UAH", name: "OLX Ukraine", partsCategory: "2550" },
  olx_pl: { host: "www.olx.pl", country: "PL", currency: "PLN", name: "OLX Poland" },
  olx_ro: { host: "www.olx.ro", country: "RO", currency: "RON", name: "OLX Romania" },
  olx_bg: { host: "www.olx.bg", country: "BG", currency: "BGN", name: "OLX Bulgaria" },
  olx_pt: { host: "www.olx.pt", country: "PT", currency: "EUR", name: "OLX Portugal" },
};

function photoUrl(link?: string | null): string | null {
  if (!link) return null;
  return link.replace("{width}", "640").replace("{height}", "480");
}

export async function searchOlx(
  sourceId: keyof typeof MARKETS,
  query: string,
  limit = 8,
): Promise<SearchHit[]> {
  const cfg = MARKETS[sourceId];
  if (!cfg) return [];

  const params: { key: string; value: string }[] = [
    { key: "query", value: query },
    { key: "offset", value: "0" },
    { key: "limit", value: String(Math.min(limit, 20)) },
  ];
  if (cfg.partsCategory) params.push({ key: "category_id", value: cfg.partsCategory });

  const res = await fetch(`https://${cfg.host}/apigateway/graphql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: `https://${cfg.host}`,
      Referer: `https://${cfg.host}/`,
      "User-Agent": "AutoPartsCore/0.3 (+public GraphQL catalog)",
    },
    body: JSON.stringify({
      operationName: "ListingSearchQuery",
      query: LISTING_SEARCH_QUERY,
      variables: { searchParameters: params },
    }),
    next: { revalidate: 0 },
  });

  const textHead = (await res.clone().text()).slice(0, 200).toLowerCase();
  if (textHead.includes("just a moment") || textHead.includes("captcha")) {
    throw new Error("Access challenge — refusing to bypass");
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const payload = await res.json();
  const rows = payload?.data?.clientCompatibleListings?.data || [];

  return rows.map((row: Record<string, unknown>) => {
    let price: number | null = null;
    let currency: string | null = cfg.currency;
    for (const p of (row.params as Record<string, unknown>[]) || []) {
      const val = (p.value || {}) as Record<string, unknown>;
      if (p.key === "price" || p.type === "price") {
        price = typeof val.value === "number" ? val.value : Number(val.value) || null;
        currency = (val.currency as string) || currency;
      }
    }
    const photos = (row.photos as { link?: string }[]) || [];
    return {
      sourceId,
      sourceName: cfg.name,
      title: String(row.title || "OLX listing"),
      url: String(row.url || ""),
      price,
      currency,
      country: cfg.country,
      imageUrl: photoUrl(photos[0]?.link),
      brand: null,
    } satisfies SearchHit;
  });
}
