import type { SearchHit } from "./types";

const SEARCH_QUERY = `
query SearchAds($input: Ads_SearchInput!) {
  searchAds(input: $input) {
    count
    ads {
      id
      title
      posted
      state
      subCategory { id title { translated } url }
    }
  }
}`;

function ageFromPosted(posted: unknown): { refreshedAt: string | null; ageDays: number | null } {
  if (posted == null) return { refreshedAt: null, ageDays: null };
  // 999.md often returns unix seconds
  const n = typeof posted === "number" ? posted : Number(posted);
  let d: Date;
  if (Number.isFinite(n) && n > 1e9) {
    d = new Date(n > 1e12 ? n : n * 1000);
  } else {
    d = new Date(String(posted));
  }
  if (Number.isNaN(d.getTime())) return { refreshedAt: null, ageDays: null };
  const ageDays = Math.floor((Date.now() - d.getTime()) / (24 * 3600 * 1000));
  return { refreshedAt: d.toISOString(), ageDays };
}

export async function searchNine99(query: string, limit = 8): Promise<SearchHit[]> {
  const res = await fetch("https://999.md/graphql", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "https://999.md",
      Referer: "https://999.md/",
      "User-Agent": "AutoPartsCore/0.3 (+public GraphQL catalog)",
    },
    body: JSON.stringify({
      query: SEARCH_QUERY,
      variables: {
        input: {
          query,
          pagination: { skip: 0, limit: Math.min(limit, 24) },
          categoryId: 5001,
          subCategoryId: 674,
        },
      },
    }),
    next: { revalidate: 0 },
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const payload = await res.json();
  if (payload?.errors?.length && !payload?.data?.searchAds) {
    throw new Error(payload.errors[0]?.message || "999.md GraphQL error");
  }
  const ads = payload?.data?.searchAds?.ads || [];

  return ads.slice(0, limit).map((ad: Record<string, unknown>) => {
    const id = String(ad.id);
    const sub = (ad.subCategory || {}) as { url?: string };
    const subUrl = sub.url || "transport/spare-parts-for-cars";
    const age = ageFromPosted(ad.posted);
    return {
      sourceId: "nine99_md",
      sourceName: "999.md",
      title: String(ad.title || "999.md"),
      url: `https://999.md/ro/${subUrl}/${id}`,
      price: null,
      currency: "EUR",
      country: "MD",
      imageUrl: null,
      brand: null,
      refreshedAt: age.refreshedAt,
      ageDays: age.ageDays,
    } satisfies SearchHit;
  });
}
