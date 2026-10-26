import { AppShell } from "@/components/AppShell";
import { LIVE_SOURCES, MAX_LISTING_AGE_DAYS } from "@/lib/catalog/types";

export default function SourcesPage() {
  return (
    <AppShell title="Source Connectors" subtitle={`Live catalogs · fresh ≤ ${MAX_LISTING_AGE_DAYS} days`}>
      <section className="panel overflow-hidden">
        <div className="border-b border-[var(--line)] px-4 py-3 font-bold">Operational (UA · MD · RO)</div>
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
    </AppShell>
  );
}
