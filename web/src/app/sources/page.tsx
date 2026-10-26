import { AppShell } from "@/components/AppShell";
import { LIVE_SOURCES } from "@/lib/catalog/types";

const DEFERRED = [
  { id: "rozetka", why: "Search API IDs only; hydrate behind Cloudflare" },
  { id: "allegro / ebay", why: "OAuth / credentials" },
  { id: "autodoc / dok / exist", why: "Cloudflare / 403" },
  { id: "auto.ria", why: "API key + rate limits; cars/donors focus" },
];

export default function SourcesPage() {
  return (
    <AppShell title="Source Connectors" subtitle="Live catalogs vs deferred sources">
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="panel overflow-hidden">
          <div className="border-b border-[var(--line)] px-4 py-3 font-bold">Operational</div>
          <ul className="divide-y divide-[var(--line)]">
            {LIVE_SOURCES.map((s) => (
              <li key={s.id} className="flex items-center justify-between px-4 py-3 text-sm">
                <div>
                  <p className="font-semibold">{s.name}</p>
                  <p className="text-xs text-[var(--muted)]">{s.id}</p>
                </div>
                <span className="badge badge-ok">{s.country}</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="panel overflow-hidden">
          <div className="border-b border-[var(--line)] px-4 py-3 font-bold">Deferred</div>
          <ul className="divide-y divide-[var(--line)]">
            {DEFERRED.map((d) => (
              <li key={d.id} className="px-4 py-3 text-sm">
                <p className="font-semibold">{d.id}</p>
                <p className="text-xs text-[var(--muted)]">{d.why}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </AppShell>
  );
}
