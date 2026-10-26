import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[var(--paper)]">
      <section className="relative min-h-[100svh] overflow-hidden text-[var(--paper)]">
        <div className="absolute inset-0">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?auto=format&fit=crop&w=2400&q=80"
            alt=""
            className="hero-media h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[rgba(18,20,26,0.92)] via-[rgba(18,20,26,0.72)] to-[rgba(18,20,26,0.35)]" />
          <div className="absolute inset-0 bg-gradient-to-t from-[rgba(18,20,26,0.85)] via-transparent to-[rgba(18,20,26,0.25)]" />
          <div className="grain absolute inset-0" />
        </div>

        <div className="relative flex min-h-[100svh] flex-col">
          <SiteHeader tone="on-dark" />
          <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col justify-end px-5 pb-16 pt-24 md:px-10 md:pb-24">
            <p className="animate-rise font-[family-name:var(--font-display)] text-5xl font-extrabold leading-[0.92] tracking-tight md:text-7xl lg:text-8xl">
              AutoParts
              <span className="block text-[var(--signal)]">Core</span>
            </p>
            <div className="signal-line mt-6 h-[3px] w-40 bg-[var(--signal)]" />
            <h1 className="animate-rise-delay mt-7 max-w-xl font-[family-name:var(--font-display)] text-2xl font-semibold leading-tight tracking-tight text-white/95 md:text-3xl">
              Запчасти по живым каталогам Европы, Молдовы и Украины
            </h1>
            <p className="animate-rise-delay-2 mt-4 max-w-lg text-base text-white/70 md:text-lg">
              Один поиск по OLX, Prom, Flagma, 999.md и Bazar.bg — публичные данные, без ключей.
            </p>
            <div className="animate-rise-delay-2 mt-8 flex flex-wrap gap-3">
              <Link
                href="/search?q=фара+Passat+B8"
                className="bg-[var(--signal)] px-6 py-3 text-sm font-bold text-[var(--ink)] transition hover:bg-[#f0b52f]"
              >
                Искать фару Passat B8
              </Link>
              <Link
                href="/sources"
                className="border border-white/35 bg-white/5 px-6 py-3 text-sm font-semibold text-white backdrop-blur-sm transition hover:bg-white/12"
              >
                Какие источники работают
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-20 md:px-10 md:py-28">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--steel)]">
          Как это устроено
        </p>
        <h2 className="mt-3 max-w-2xl font-[family-name:var(--font-display)] text-3xl font-bold tracking-tight md:text-4xl">
          Тот же метод, что и в ядре: GraphQL и Product JSON-LD
        </h2>
        <p className="mt-4 max-w-2xl text-[var(--ink-soft)]">
          Берём только то, что сайты уже отдают своей витрине. Cloudflare и CAPTCHA не обходим —
          такие источники просто отложены.
        </p>
        <div className="mt-12 grid gap-10 md:grid-cols-3">
          {[
            {
              t: "Публичный каталог",
              d: "OLX GraphQL, 999.md GraphQL, Prom/Flagma/Bazar JSON-LD — проверено live.",
            },
            {
              t: "Рынки в фокусе",
              d: "UA, MD, PL, RO, BG, PT. Казахстан и Беларусь сознательно не тянем.",
            },
            {
              t: "Честные ярлыки",
              d: "Нет цены — так и пишем. Demo/fixture не маскируем под live.",
            },
          ].map((item) => (
            <div key={item.t} className="border-t border-black/15 pt-5">
              <h3 className="font-[family-name:var(--font-display)] text-xl font-bold">{item.t}</h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--ink-soft)]">{item.d}</p>
            </div>
          ))}
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
