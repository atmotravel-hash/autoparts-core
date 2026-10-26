export type SearchHit = {
  sourceId: string;
  sourceName: string;
  title: string;
  url: string;
  price: number | null;
  currency: string | null;
  country: string;
  imageUrl: string | null;
  brand: string | null;
  /** ISO timestamp when known */
  refreshedAt: string | null;
  /** days since refresh; null if unknown */
  ageDays: number | null;
};

export type SearchResponse = {
  query: string;
  results: SearchHit[];
  droppedStale: number;
  errors: { sourceId: string; message: string }[];
  tookMs: number;
  markets: string[];
};

/** Product scope: Ukraine · Moldova · Romania only */
export const LIVE_SOURCES = [
  { id: "olx_ua", name: "OLX Ukraine", country: "UA" },
  { id: "prom_ua", name: "Prom.ua", country: "UA" },
  { id: "flagma_ua", name: "Flagma.ua", country: "UA" },
  { id: "nine99_md", name: "999.md", country: "MD" },
  { id: "olx_ro", name: "OLX Romania", country: "RO" },
] as const;

export type SourceId = (typeof LIVE_SOURCES)[number]["id"];

export const MAX_LISTING_AGE_DAYS = 30;
