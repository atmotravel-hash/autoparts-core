import { searchJsonLd } from "./jsonld";
import { searchNine99 } from "./nine99";
import { searchOlx } from "./olx";
import type { SearchHit, SearchResponse, SourceId } from "./types";
import { LIVE_SOURCES, MAX_LISTING_AGE_DAYS } from "./types";

const DEFAULT_SOURCES: SourceId[] = LIVE_SOURCES.map((s) => s.id);

async function runSource(id: SourceId, query: string, limit: number): Promise<SearchHit[]> {
  if (id === "olx_ua" || id === "olx_ro") return searchOlx(id, query, limit);
  if (id === "prom_ua" || id === "flagma_ua") return searchJsonLd(id, query, limit);
  if (id === "nine99_md") return searchNine99(query, limit);
  return [];
}

function isFresh(hit: SearchHit): boolean {
  // Strict: unknown age from classifieds is dropped; catalog JSON-LD has ageDays=0.
  if (hit.ageDays == null) return false;
  return hit.ageDays <= MAX_LISTING_AGE_DAYS;
}

export async function runCatalogSearch(opts: {
  query: string;
  sources?: string[];
  limitPerSource?: number;
}): Promise<SearchResponse> {
  const started = Date.now();
  const query = opts.query.trim();
  if (!query) {
    return {
      query,
      results: [],
      droppedStale: 0,
      errors: [{ sourceId: "input", message: "Empty query" }],
      tookMs: 0,
      markets: ["UA", "MD", "RO"],
    };
  }

  const wanted = (opts.sources?.length ? opts.sources : DEFAULT_SOURCES).filter((s) =>
    LIVE_SOURCES.some((x) => x.id === s),
  ) as SourceId[];

  const limit = Math.min(opts.limitPerSource ?? 10, 20);
  const settled = await Promise.allSettled(wanted.map((id) => runSource(id, query, limit)));

  const raw: SearchHit[] = [];
  const errors: SearchResponse["errors"] = [];

  settled.forEach((item, i) => {
    const sourceId = wanted[i];
    if (item.status === "fulfilled") raw.push(...item.value);
    else errors.push({ sourceId, message: item.reason?.message || String(item.reason) });
  });

  const results = raw.filter(isFresh);
  const droppedStale = raw.length - results.length;

  results.sort((a, b) => {
    if (a.price == null && b.price == null) return (a.ageDays ?? 99) - (b.ageDays ?? 99);
    if (a.price == null) return 1;
    if (b.price == null) return -1;
    return a.price - b.price;
  });

  return {
    query,
    results,
    droppedStale,
    errors,
    tookMs: Date.now() - started,
    markets: ["UA", "MD", "RO"],
  };
}
