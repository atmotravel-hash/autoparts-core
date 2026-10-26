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
  refreshedAt: string | null;
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

export const LIVE_SOURCES = [
  { id: "olx_ua", name: "OLX Ukraine", country: "UA" },
  { id: "prom_ua", name: "Prom.ua", country: "UA" },
  { id: "flagma_ua", name: "Flagma.ua", country: "UA" },
  { id: "nine99_md", name: "999.md", country: "MD" },
  { id: "prom_md", name: "Prom.md", country: "MD" },
  { id: "olx_ro", name: "OLX Romania", country: "RO" },
  { id: "olx_pl", name: "OLX Poland", country: "PL" },
  { id: "olx_bg", name: "OLX Bulgaria", country: "BG" },
  { id: "bazar_bg", name: "Bazar.bg", country: "BG" },
  { id: "olx_pt", name: "OLX Portugal", country: "PT" },
] as const;

export type SourceId = (typeof LIVE_SOURCES)[number]["id"];

export const MAX_LISTING_AGE_DAYS = 30;

export const MARKET_GROUPS: { country: string; label: string; sourceIds: SourceId[] }[] = [
  { country: "UA", label: "Ukraine", sourceIds: ["olx_ua", "prom_ua", "flagma_ua"] },
  { country: "MD", label: "Moldova", sourceIds: ["nine99_md", "prom_md"] },
  { country: "RO", label: "Romania", sourceIds: ["olx_ro"] },
  { country: "PL", label: "Poland", sourceIds: ["olx_pl"] },
  { country: "BG", label: "Bulgaria", sourceIds: ["olx_bg", "bazar_bg"] },
  { country: "PT", label: "Portugal", sourceIds: ["olx_pt"] },
];
