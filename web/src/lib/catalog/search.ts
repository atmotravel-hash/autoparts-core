import { searchJsonLd } from "./jsonld";
import { searchNine99 } from "./nine99";
import { searchOlx } from "./olx";
import type { SearchHit, SearchResponse, SourceId } from "./types";
import { LIVE_SOURCES } from "./types";

const DEFAULT_SOURCES: SourceId[] = [
  "olx_ua",
  "prom_ua",
  "flagma_ua",
  "olx_pl",
  "olx_ro",
  "olx_bg",
  "bazar_bg",
  "nine99_md",
];

async function runSource(id: SourceId, query: string, limit: number): Promise<SearchHit[]> {
  if (id.startsWith("olx_")) return searchOlx(id as "olx_ua", query, limit);
  if (id === "prom_ua" || id === "flagma_ua" || id === "bazar_bg") {
    return searchJsonLd(id, query, limit);
  }
  if (id === "nine99_md") return searchNine99(query, limit);
  return [];
}

export async function runCatalogSearch(opts: {
  query: string;
  sources?: string[];
  limitPerSource?: number;
}): Promise<SearchResponse> {
  const started = Date.now();
  const query = opts.query.trim();
  if (!query) {
    return { query, results: [], errors: [{ sourceId: "input", message: "Empty query" }], tookMs: 0 };
  }

  const wanted = (opts.sources?.length ? opts.sources : DEFAULT_SOURCES).filter((s) =>
    LIVE_SOURCES.some((x) => x.id === s),
  ) as SourceId[];

  const limit = Math.min(opts.limitPerSource ?? 6, 12);
  const settled = await Promise.allSettled(wanted.map((id) => runSource(id, query, limit)));

  const results: SearchHit[] = [];
  const errors: SearchResponse["errors"] = [];

  settled.forEach((item, i) => {
    const sourceId = wanted[i];
    if (item.status === "fulfilled") results.push(...item.value);
    else errors.push({ sourceId, message: item.reason?.message || String(item.reason) });
  });

  results.sort((a, b) => {
    if (a.price == null && b.price == null) return 0;
    if (a.price == null) return 1;
    if (b.price == null) return -1;
    return a.price - b.price;
  });

  return { query, results, errors, tookMs: Date.now() - started };
}
