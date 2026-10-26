import type { SearchHit } from "./types";

type Product = {
  "@type"?: string | string[];
  name?: string;
  url?: string;
  image?: string | string[] | { url?: string }[];
  brand?: string | { name?: string };
  sku?: string;
  offers?:
    | {
        price?: string | number;
        priceCurrency?: string;
        url?: string;
        seller?: { name?: string };
      }
    | Array<Record<string, unknown>>;
  "@graph"?: unknown[];
  itemListElement?: Array<{ item?: Product } | Product>;
};

const LD_RE = /<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;

function isProduct(t: unknown): boolean {
  return t === "Product" || (Array.isArray(t) && t.includes("Product"));
}

function collect(node: unknown, out: Product[]) {
  if (Array.isArray(node)) {
    node.forEach((n) => collect(n, out));
    return;
  }
  if (!node || typeof node !== "object") return;
  const obj = node as Product;
  if (isProduct(obj["@type"])) out.push(obj);
  for (const g of obj["@graph"] || []) collect(g, out);
  if (obj["@type"] === "ItemList") {
    for (const el of obj.itemListElement || []) {
      collect((el as { item?: Product }).item || el, out);
    }
  }
}

function extractProducts(html: string): Product[] {
  const out: Product[] = [];
  for (const m of html.matchAll(LD_RE)) {
    try {
      collect(JSON.parse(m[1]), out);
    } catch {
      /* skip bad blocks */
    }
  }
  return out;
}

function offerOf(p: Product) {
  const o = p.offers;
  if (Array.isArray(o)) return (o[0] || {}) as NonNullable<Exclude<Product["offers"], unknown[]>>;
  return (o || {}) as NonNullable<Exclude<Product["offers"], unknown[]>>;
}

function imageOf(p: Product): string | null {
  const img = p.image;
  if (typeof img === "string") return img.startsWith("//") ? `https:${img}` : img;
  if (Array.isArray(img) && img.length) {
    const first = img[0];
    if (typeof first === "string") return first.startsWith("//") ? `https:${first}` : first;
    if (first && typeof first === "object" && first.url) {
      return first.url.startsWith("//") ? `https:${first.url}` : first.url;
    }
  }
  return null;
}

function brandOf(p: Product): string | null {
  if (typeof p.brand === "string") return p.brand;
  if (p.brand && typeof p.brand === "object") return p.brand.name || null;
  return null;
}

const MARKETS: Record<
  string,
  { origin: string; searchUrl: (q: string) => string; country: string; currency: string; name: string }
> = {
  prom_ua: {
    origin: "https://prom.ua",
    searchUrl: (q) => `https://prom.ua/ua/search?search_term=${encodeURIComponent(q)}`,
    country: "UA",
    currency: "UAH",
    name: "Prom.ua",
  },
  flagma_ua: {
    origin: "https://flagma.ua",
    searchUrl: (q) => `https://flagma.ua/uk/search/?q=${encodeURIComponent(q)}`,
    country: "UA",
    currency: "UAH",
    name: "Flagma.ua",
  },
  prom_md: {
    origin: "https://prom.md",
    searchUrl: (q) => `https://prom.md/search?search_term=${encodeURIComponent(q)}`,
    country: "MD",
    currency: "MDL",
    name: "Prom.md",
  },
};

export async function searchJsonLd(
  sourceId: keyof typeof MARKETS,
  query: string,
  limit = 8,
): Promise<SearchHit[]> {
  const cfg = MARKETS[sourceId];
  if (!cfg) return [];

  const res = await fetch(cfg.searchUrl(query), {
    headers: {
      "User-Agent": "AutoPartsCore/0.3 (+public JSON-LD catalog)",
      Accept: "text/html",
      "Accept-Language": "uk-UA,uk;q=0.9,bg;q=0.8,en;q=0.7",
      Referer: `${cfg.origin}/`,
    },
    next: { revalidate: 0 },
  });

  const html = await res.text();
  const head = html.slice(0, 300).toLowerCase();
  if (head.includes("just a moment") || (res.status === 403 && head.includes("captcha"))) {
    throw new Error("Access challenge — refusing to bypass");
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const products = extractProducts(html).slice(0, limit);
  return products
    .map((p) => {
      const offer = offerOf(p);
      let url = String(p.url || offer.url || "");
      if (url.startsWith("//")) url = `https:${url}`;
      const rawPrice = offer.price;
      const price =
        rawPrice === undefined || rawPrice === null ? null : Number(rawPrice);
      return {
        sourceId,
        sourceName: cfg.name,
        title: String(p.name || "Listing"),
        url,
        price: Number.isFinite(price) ? price : null,
        currency: (offer.priceCurrency || cfg.currency).toUpperCase(),
        country: cfg.country,
        imageUrl: imageOf(p),
        brand: brandOf(p),
        // Catalog products are treated as currently offered (no ad age).
        refreshedAt: new Date().toISOString(),
        ageDays: 0,
      } satisfies SearchHit;
    })
    .filter((h) => h.url);
}
