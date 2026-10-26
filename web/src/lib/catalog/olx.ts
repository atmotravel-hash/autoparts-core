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
        created_time
        last_refresh_time
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
  olx_ro: { host: "www.olx.ro", country: "RO", currency: "RON", name: "OLX Romania" },
};

function photoUrl(link?: string | null): string | null {
  if (!link) return null;
  return link.replace("{width}", "640").replace("{height}", "480");
}

function ageFrom(ts: unknown): { refreshedAt: string | null; ageDays: number | null } {
  if (!ts) return { refreshedAt: null, ageDays: null };
  const d = new Date(String(ts));
  if (Number.isNaN(d.getTime())) return { refreshedAt: null, ageDays: null };
  const ageDays = Math.floor((Date.now() - d.getTime()) / (24 * 3600 * 1000));
  return { refreshedAt: d.toISOString(), ageDays };
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
    { key: "limit", value: String(Math.min(limit, 24)) },
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
    const age = ageFrom(row.last_refresh_time || row.created_time);
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
      refreshedAt: age.refreshedAt,
      ageDays: age.ageDays,
    } satisfies SearchHit;
  });
}
