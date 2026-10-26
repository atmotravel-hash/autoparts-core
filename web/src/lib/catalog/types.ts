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
};

export type SearchResponse = {
  query: string;
  results: SearchHit[];
  errors: { sourceId: string; message: string }[];
  tookMs: number;
};

export const LIVE_SOURCES = [
  { id: "olx_ua", name: "OLX Ukraine", country: "UA" },
  { id: "prom_ua", name: "Prom.ua", country: "UA" },
  { id: "flagma_ua", name: "Flagma.ua", country: "UA" },
  { id: "olx_pl", name: "OLX Poland", country: "PL" },
  { id: "olx_ro", name: "OLX Romania", country: "RO" },
  { id: "olx_bg", name: "OLX Bulgaria", country: "BG" },
  { id: "bazar_bg", name: "Bazar.bg", country: "BG" },
  { id: "olx_pt", name: "OLX Portugal", country: "PT" },
  { id: "nine99_md", name: "999.md", country: "MD" },
] as const;

export type SourceId = (typeof LIVE_SOURCES)[number]["id"];
