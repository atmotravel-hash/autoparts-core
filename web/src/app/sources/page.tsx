import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { LIVE_SOURCES } from "@/lib/catalog/types";

const DEFERRED = [
  { id: "rozetka", why: "Search API только ID, hydrate за Cloudflare" },
  { id: "allegro / ebay", why: "OAuth / ключи" },
  { id: "autodoc / dok / exist", why: "Cloudflare / 403" },
  { id: "auto.ria", why: "Ключ + лимиты, в основном авто/доноры" },
  { id: "satu.kz / deal.by", why: "Вне фокуса EU/MD/UA" },
];

export default function SourcesPage() {
  return (
    <main className="min-h-screen bg-[var(--paper)]">
      <div className="border-b border-black/10 bg-[linear-gradient(160deg,#1c212b_0%,#2a3140_55%,#3a3324_100%)] text-[var(--paper)]">
        <SiteHeader tone="on-dark" />
        <div className="mx-auto max-w-6xl px-5 pb-12 pt-6 md:px-10">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--signal)]">
            Источники
          </p>
          <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-extrabold tracking-tight md:text-5xl">
            Что реально работает
          </h1>
          <p className="mt-3 max-w-2xl text-white/70">
            Метод один: публичный GraphQL или Product JSON-LD. Без обхода защит.
          </p>
        </div>
      </div>

      <section className="mx-auto max-w-6xl px-5 py-14 md:px-10">
        <h2 className="font-[family-name:var(--font-display)] text-2xl font-bold">В поиске</h2>
        <ul className="mt-6 divide-y divide-black/10 border-y border-black/10">
          {LIVE_SOURCES.map((s) => (
            <li key={s.id} className="flex flex-wrap items-baseline justify-between gap-3 py-4">
              <div>
                <p className="font-semibold">{s.name}</p>
                <p className="text-sm text-[var(--steel)]">{s.id}</p>
              </div>
              <p className="text-sm font-medium text-[var(--ink-soft)]">{s.country}</p>
            </li>
          ))}
        </ul>

        <h2 className="mt-14 font-[family-name:var(--font-display)] text-2xl font-bold">Отложено</h2>
        <ul className="mt-6 space-y-4">
          {DEFERRED.map((d) => (
            <li key={d.id} className="border-l-2 border-[var(--signal)] pl-4">
              <p className="font-semibold">{d.id}</p>
              <p className="text-sm text-[var(--steel)]">{d.why}</p>
            </li>
          ))}
        </ul>
      </section>
      <SiteFooter />
    </main>
  );
}
