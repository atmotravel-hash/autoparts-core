"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useMemo, useState, useTransition } from "react";
import type { SearchHit, SearchResponse } from "@/lib/catalog/types";
import { LIVE_SOURCES } from "@/lib/catalog/types";

function money(hit: SearchHit) {
  if (hit.price == null) return "Цена не указана";
  return `${hit.price.toLocaleString("ru-RU")} ${hit.currency || ""}`.trim();
}

export function SearchPanel({
  initialQuery,
  initialData,
}: {
  initialQuery: string;
  initialData: SearchResponse | null;
}) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [selected, setSelected] = useState<string[]>(LIVE_SOURCES.map((s) => s.id));
  const [data, setData] = useState<SearchResponse | null>(initialData);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const grouped = useMemo(() => {
    const map = new Map<string, number>();
    for (const r of data?.results || []) map.set(r.sourceId, (map.get(r.sourceId) || 0) + 1);
    return map;
  }, [data]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setError(null);
    startTransition(async () => {
      router.replace(`/search?q=${encodeURIComponent(q)}`);
      try {
        const params = new URLSearchParams({
          q,
          sources: selected.join(","),
          limit: "6",
        });
        const res = await fetch(`/api/search?${params.toString()}`);
        const json = (await res.json()) as SearchResponse;
        setData(json);
      } catch (err) {
        setError(String(err));
      }
    });
  }

  function toggleSource(id: string) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 md:px-10 md:py-14">
      <form onSubmit={onSubmit} className="space-y-5">
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--steel)]">
            Запрос
          </span>
          <div className="mt-2 flex flex-col gap-3 sm:flex-row">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="например: фара Passat B8"
              className="w-full border border-black/15 bg-white px-4 py-3 text-base outline-none ring-[var(--signal)] transition focus:ring-2"
            />
            <button
              type="submit"
              disabled={pending || !query.trim()}
              className="bg-[var(--ink)] px-6 py-3 text-sm font-bold text-[var(--paper)] transition hover:bg-[var(--ink-soft)] disabled:opacity-50"
            >
              {pending ? "Ищем…" : "Найти"}
            </button>
          </div>
        </label>

        <fieldset>
          <legend className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--steel)]">
            Источники
          </legend>
          <div className="mt-3 flex flex-wrap gap-2">
            {LIVE_SOURCES.map((s) => {
              const on = selected.includes(s.id);
              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => toggleSource(s.id)}
                  className={`border px-3 py-1.5 text-xs font-semibold transition ${
                    on
                      ? "border-[var(--ink)] bg-[var(--ink)] text-[var(--paper)]"
                      : "border-black/20 bg-transparent text-[var(--ink-soft)]"
                  }`}
                >
                  {s.name}
                </button>
              );
            })}
          </div>
        </fieldset>
      </form>

      {error && <p className="mt-6 text-sm text-red-700">{error}</p>}

      {data && (
        <div className="mt-10">
          <div className="flex flex-wrap items-end justify-between gap-3 border-b border-black/10 pb-4">
            <div>
              <h2 className="font-[family-name:var(--font-display)] text-2xl font-bold tracking-tight">
                {data.results.length} предложений
              </h2>
              <p className="mt-1 text-sm text-[var(--steel)]">
                «{data.query}» · {data.tookMs} ms
                {grouped.size ? ` · ${[...grouped.entries()].map(([k, v]) => `${k}:${v}`).join(" · ")}` : ""}
              </p>
            </div>
          </div>

          {data.errors.length > 0 && (
            <details className="mt-4 text-sm text-[var(--steel)]">
              <summary className="cursor-pointer">Ошибки источников ({data.errors.length})</summary>
              <ul className="mt-2 space-y-1">
                {data.errors.map((e) => (
                  <li key={`${e.sourceId}-${e.message}`}>
                    <span className="font-semibold text-[var(--ink)]">{e.sourceId}</span>: {e.message}
                  </li>
                ))}
              </ul>
            </details>
          )}

          <ul className="mt-6 divide-y divide-black/10">
            {data.results.map((hit) => (
              <li key={`${hit.sourceId}-${hit.url}`} className="grid gap-4 py-5 md:grid-cols-[120px_1fr_auto]">
                <div className="h-[88px] w-full overflow-hidden bg-[var(--paper-deep)] md:w-[120px]">
                  {hit.imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={hit.imageUrl} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <div className="flex h-full items-center justify-center text-[10px] uppercase tracking-wider text-[var(--steel)]">
                      no photo
                    </div>
                  )}
                </div>
                <div>
                  <a
                    href={hit.url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-semibold leading-snug text-[var(--ink)] underline-offset-2 hover:underline"
                  >
                    {hit.title}
                  </a>
                  <p className="mt-1 text-sm text-[var(--steel)]">
                    {hit.sourceName} · {hit.country}
                    {hit.brand ? ` · ${hit.brand}` : ""}
                  </p>
                </div>
                <div className="md:text-right">
                  <p className="font-[family-name:var(--font-display)] text-lg font-bold">{money(hit)}</p>
                  <a
                    href={hit.url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 inline-block text-xs font-semibold uppercase tracking-wider text-[var(--signal-deep)]"
                  >
                    Открыть →
                  </a>
                </div>
              </li>
            ))}
          </ul>

          {!data.results.length && (
            <p className="mt-8 text-[var(--ink-soft)]">Ничего не нашли по этому запросу.</p>
          )}
        </div>
      )}
    </div>
  );
}
