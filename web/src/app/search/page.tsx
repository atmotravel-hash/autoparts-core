import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SearchPanel } from "@/components/SearchPanel";
import { runCatalogSearch } from "@/lib/catalog/search";
import type { SearchResponse } from "@/lib/catalog/types";

export const dynamic = "force-dynamic";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const sp = await searchParams;
  const q = (sp.q || "").trim();
  let initial: SearchResponse | null = null;
  if (q) {
    initial = await runCatalogSearch({ query: q, limitPerSource: 6 });
  }

  return (
    <main className="min-h-screen bg-[var(--paper)]">
      <div className="border-b border-black/10 bg-[linear-gradient(135deg,#f3f0ea_0%,#e8e2d6_45%,#d9d3c6_100%)]">
        <SiteHeader />
        <div className="mx-auto max-w-6xl px-5 pb-10 pt-4 md:px-10">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--steel)]">Поиск</p>
          <h1 className="mt-2 font-[family-name:var(--font-display)] text-4xl font-extrabold tracking-tight md:text-5xl">
            Живые предложения
          </h1>
          <p className="mt-3 max-w-2xl text-[var(--ink-soft)]">
            Запрос уходит в публичные каталоги. Цены и ссылки — как на витрине источника.
          </p>
        </div>
      </div>
      <SearchPanel initialQuery={q || "фара Passat B8"} initialData={initial} />
      <SiteFooter />
    </main>
  );
}
