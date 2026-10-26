import { AppShell } from "@/components/AppShell";
import { LIVE_SOURCES, MARKET_GROUPS, MAX_LISTING_AGE_DAYS } from "@/lib/catalog/types";

const DEFERRED = [
  { id: "olx_pl / olx_bg / olx_pt", blocker: "Outside product markets", path: "Deferred — UA/MD/RO only" },
  { id: "bazar_bg", blocker: "Outside product markets", path: "Deferred — UA/MD/RO only" },
  { id: "rozetka", blocker: "CF on detail hydrate", path: "Merchant / partner API" },
  { id: "allegro", blocker: "OAuth + CAPTCHA on public GQL", path: "developer.allegro.pl OAuth app" },
  { id: "ebay", blocker: "App credentials", path: "eBay Browse / Buy API" },
  { id: "autodoc", blocker: "Cloudflare", path: "Affiliate / B2B feed" },
  { id: "dok_ua", blocker: "Cloudflare", path: "Partner feed" },
  { id: "exist_ua", blocker: "403 / auth wall", path: "B2B account" },
  { id: "auto_ria", blocker: "API key + rate limits", path: "developers.ria.com free key (opt-in)" },
  { id: "otomoto", blocker: "cars-first Otodom", path: "OLX Group Partner API" },
  { id: "hotline", blocker: "No Product JSON-LD SSR", path: "No zero-key catalog path" },
  { id: "bigl", blocker: "No Product JSON-LD on search", path: "No zero-key catalog path" },
  { id: "publi24", blocker: "No usable Product LD", path: "No zero-key catalog path" },
];

const METHOD: Record<string, string> = {
  olx_ua: "GraphQL ListingSearchQuery",
  olx_ro: "GraphQL ListingSearchQuery",
  nine99_md: "GraphQL searchAds",
  prom_ua: "Product JSON-LD",
  flagma_ua: "Product JSON-LD",
  prom_md: "Product JSON-LD",
};

export default function SourcesPage() {
  const markets = MARKET_GROUPS.map((g) => g.country).join(" · ");

  return (
    <AppShell
      title="Source Connectors"
      subtitle={`Live catalogs · fresh ≤ ${MAX_LISTING_AGE_DAYS} days · no CAPTCHA bypass`}
    >
      <div className="mb-4 flex flex-wrap gap-2 text-xs font-semibold">
        <span className="rounded-full bg-blue-600 px-3 py-1 text-white">Markets: {markets}</span>
        <span className="rounded-full bg-slate-200 px-3 py-1 text-slate-700">
          {LIVE_SOURCES.length} live · deferred paths documented
        </span>
      </div>

      <section className="panel mb-4 overflow-hidden">
        <div className="border-b border-[var(--line)] px-4 py-3 font-bold">
          Operational (UA · MD · RO)
        </div>
        <ul className="divide-y divide-[var(--line)]">
          {LIVE_SOURCES.map((s) => (
            <li key={s.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
              <div>
                <p className="font-semibold">{s.name}</p>
                <p className="text-xs text-[var(--muted)]">
                  {s.id} · {METHOD[s.id] || "public catalog"}
                </p>
              </div>
              <span className="badge badge-ok">{s.country}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel overflow-hidden">
        <div className="border-b border-[var(--line)] px-4 py-3 font-bold">
          Not in product / not allowed publicly — collection path
        </div>
        <ul className="divide-y divide-[var(--line)]">
          {DEFERRED.map((s) => (
            <li
              key={s.id}
              className="grid gap-1 px-4 py-3 text-sm md:grid-cols-[160px_minmax(0,1fr)_minmax(0,1.2fr)]"
            >
              <p className="font-semibold">{s.id}</p>
              <p className="text-xs text-[var(--muted)]">{s.blocker}</p>
              <p className="text-xs font-medium text-[var(--ink)]">Path: {s.path}</p>
            </li>
          ))}
        </ul>
        <p className="border-t border-[var(--line)] px-4 py-3 text-xs text-[var(--muted)]">
          Full map: <code className="font-mono">docs/ACCESS_PATHS.md</code>
        </p>
      </section>
    </AppShell>
  );
}
