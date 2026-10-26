"use client";

import { FormEvent, useEffect, useMemo, useState, useTransition } from "react";
import type { SearchHit, SearchResponse, SourceId } from "@/lib/catalog/types";
import { LIVE_SOURCES, MARKET_GROUPS, MAX_LISTING_AGE_DAYS } from "@/lib/catalog/types";
import { estimateFitment, formatMoney } from "@/lib/fitment";

const MARKET_LABEL = MARKET_GROUPS.map((g) => g.country).join(" · ");

const MAKES = ["Volkswagen", "BMW", "Audi", "Skoda", "Toyota", "Mercedes-Benz", "Renault", "Ford"];
const MODELS = ["Passat", "Golf", "3 Series", "A4", "Octavia", "C-Class", "Focus", "Megane"];
const GENS = ["B8 (2014–2023)", "B7", "Mk7", "F30", "B9", "W205"];
const PARTS = ["Headlight", "Front fender", "Bumper", "Side mirror", "Radiator", "Door"];
const YEARS = Array.from({ length: 16 }, (_, i) => 2024 - i);

function buildQuery(make: string, model: string, gen: string, part: string, oem: string) {
  const g = gen.split(/\s+/)[0];
  const partMap: Record<string, string> = {
    Headlight: "фара",
    "Front fender": "крыло",
    Bumper: "бампер",
    "Side mirror": "зеркало",
    Radiator: "радиатор",
    Door: "дверь",
  };
  const partQ = partMap[part] || part;
  return [partQ, model, g, oem].filter(Boolean).join(" ").trim();
}

export function VehicleSearchWorkspace() {
  const [make, setMake] = useState("Volkswagen");
  const [model, setModel] = useState("Passat");
  const [generation, setGeneration] = useState("B8 (2014–2023)");
  const [year, setYear] = useState(2017);
  const [part, setPart] = useState("Headlight");
  const [oem, setOem] = useState("");
  const [condition, setCondition] = useState("Any");
  const [currency, setCurrency] = useState("EUR");
  const [destination, setDestination] = useState("UA");
  const [sources, setSources] = useState<SourceId[]>(LIVE_SOURCES.map((s) => s.id));
  const [data, setData] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();
  const [maxPrice, setMaxPrice] = useState(3000);
  const [booted, setBooted] = useState(false);

  const query = useMemo(
    () => buildQuery(make, model, generation, part, oem),
    [make, model, generation, part, oem],
  );

  const rows = useMemo(() => {
    return (data?.results || []).filter((h) => h.price == null || h.price <= maxPrice);
  }, [data, maxPrice]);

  const byCountry = useMemo(() => {
    const map = new Map<string, number>();
    for (const r of rows) {
      if (r.price == null) continue;
      const prev = map.get(r.country);
      if (prev == null || r.price < prev) map.set(r.country, r.price);
    }
    return [...map.entries()].sort((a, b) => a[1] - b[1]);
  }, [rows]);

  function toggleSource(id: SourceId) {
    setSources((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  function runSearch(q: string, src: SourceId[]) {
    setError(null);
    startTransition(async () => {
      try {
        const params = new URLSearchParams({
          q,
          sources: src.join(","),
          limit: "10",
        });
        const res = await fetch(`/api/search?${params}`);
        const json = (await res.json()) as SearchResponse;
        setData(json);
      } catch (err) {
        setError(String(err));
      }
    });
  }

  useEffect(() => {
    if (booted) return;
    setBooted(true);
    runSearch(query, sources);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [booted]);

  function onSearch(e: FormEvent) {
    e.preventDefault();
    runSearch(query, sources);
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 text-xs font-semibold">
        <span className="rounded-full bg-blue-600 px-3 py-1 text-white">Markets: {MARKET_LABEL}</span>
        <span className="rounded-full bg-slate-200 px-3 py-1 text-slate-700">
          Fresh ≤ {MAX_LISTING_AGE_DAYS}d · stale ads dropped
        </span>
        <span className="rounded-full bg-slate-200 px-3 py-1 text-slate-700">
          {LIVE_SOURCES.length} zero-key sources
        </span>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0 space-y-4">
          <form onSubmit={onSearch} className="panel p-4 md:p-5">
            <div className="mb-4 flex flex-wrap gap-2 border-b border-[var(--line)] pb-3 text-sm font-semibold">
              <span className="rounded-md bg-blue-50 px-3 py-1.5 text-[var(--blue)]">Vehicle + Part</span>
              <span className="rounded-md px-3 py-1.5 text-[var(--muted)]">OEM</span>
              <span className="rounded-md px-3 py-1.5 text-[var(--muted)]">Part name</span>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              <Field label="Make">
                <select value={make} onChange={(e) => setMake(e.target.value)}>
                  {MAKES.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </select>
              </Field>
              <Field label="Model">
                <select value={model} onChange={(e) => setModel(e.target.value)}>
                  {MODELS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </select>
              </Field>
              <Field label="Generation">
                <select value={generation} onChange={(e) => setGeneration(e.target.value)}>
                  {GENS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </select>
              </Field>
              <Field label="Year">
                <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
                  {YEARS.map((y) => (
                    <option key={y} value={y}>
                      {y}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Part">
                <select value={part} onChange={(e) => setPart(e.target.value)}>
                  {PARTS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </select>
              </Field>
            </div>

            <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Field label="OEM number (optional)">
                <input value={oem} onChange={(e) => setOem(e.target.value)} placeholder="e.g. 3G1941007A" />
              </Field>
              <Field label="Condition">
                <select value={condition} onChange={(e) => setCondition(e.target.value)}>
                  {["Any", "NEW", "USED", "REFURBISHED", "DAMAGED"].map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              </Field>
              <Field label="Ship to">
                <select value={destination} onChange={(e) => setDestination(e.target.value)}>
                  {MARKET_GROUPS.map((g) => (
                    <option key={g.country} value={g.country}>
                      {g.country}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Display currency">
                <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                  {["EUR", "UAH", "MDL", "RON", "PLN", "BGN", "USD"].map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              </Field>
            </div>

            <div className="mt-4 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs font-semibold text-[var(--muted)]">Sources by market</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="btn-ghost px-2 py-1 text-[11px]"
                    onClick={() => setSources(LIVE_SOURCES.map((s) => s.id))}
                  >
                    All
                  </button>
                  <button type="button" className="btn-ghost px-2 py-1 text-[11px]" onClick={() => setSources([])}>
                    None
                  </button>
                </div>
              </div>
              {MARKET_GROUPS.map((group) => (
                <div key={group.country}>
                  <p className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-[var(--muted)]">
                    {group.label}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {LIVE_SOURCES.filter((s) => group.sourceIds.includes(s.id)).map((s) => {
                      const on = sources.includes(s.id);
                      return (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => toggleSource(s.id)}
                          className={`rounded-md border px-2.5 py-1 text-xs font-semibold ${
                            on
                              ? "border-blue-600 bg-blue-600 text-white"
                              : "border-[var(--line)] text-[var(--muted)]"
                          }`}
                        >
                          {s.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
              <p className="text-xs text-[var(--muted)]">
                Live query: <span className="font-semibold text-[var(--ink)]">{query}</span>
              </p>
              <button type="submit" className="btn-primary" disabled={pending || !sources.length}>
                {pending ? "Searching…" : "Search"}
              </button>
            </div>
          </form>

          {error && <p className="text-sm text-red-600">{error}</p>}

          {byCountry.length > 0 && (
            <div className="panel flex flex-wrap gap-3 px-4 py-3">
              <span className="text-xs font-bold uppercase tracking-wide text-[var(--muted)]">Lowest by market</span>
              {byCountry.map(([c, p], i) => (
                <span key={c} className={`text-sm font-semibold ${i === 0 ? "text-green-700" : ""}`}>
                  {c}: {formatMoney(p, rows.find((r) => r.country === c && r.price === p)?.currency || currency)}
                  {i === 0 ? " · best" : ""}
                </span>
              ))}
            </div>
          )}

          <section className="panel overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--line)] px-4 py-3">
              <h2 className="text-base font-bold">
                Results ({rows.length} offers
                {data?.droppedStale ? ` · ${data.droppedStale} stale hidden` : ""})
              </h2>
              <div className="text-xs text-[var(--muted)]">
                Cheapest first{data ? ` · ${data.tookMs} ms` : ""}
                {pending ? " · updating…" : ""}
              </div>
            </div>

            {!data && pending && <p className="px-4 py-10 text-sm text-[var(--muted)]">Loading live catalogs…</p>}
            {!data && !pending && (
              <p className="px-4 py-10 text-sm text-[var(--muted)]">Run Search to load offers.</p>
            )}

            <ul className="divide-y divide-[var(--line)]">
              {rows.map((hit) => (
                <ResultRow key={`${hit.sourceId}-${hit.url}`} hit={hit} query={query} destination={destination} />
              ))}
            </ul>

            {data && !rows.length && (
              <p className="px-4 py-8 text-sm text-[var(--muted)]">
                No fresh offers for this query. Try another part/OEM or enable more sources.
              </p>
            )}

            {data?.errors?.length ? (
              <details className="border-t border-[var(--line)] px-4 py-3 text-xs text-[var(--muted)]">
                <summary>Source errors ({data.errors.length})</summary>
                <ul className="mt-2 space-y-1">
                  {data.errors.map((e) => (
                    <li key={`${e.sourceId}-${e.message}`}>
                      <b>{e.sourceId}</b>: {e.message}
                    </li>
                  ))}
                </ul>
              </details>
            ) : null}
          </section>
        </div>

        <aside className="space-y-4">
          <div className="panel p-4">
            <h3 className="text-sm font-bold">Search summary</h3>
            <p className="mt-2 text-sm font-semibold">
              {make} {model} {generation.split(/\s+/)[0]} · {year}
            </p>
            <p className="text-xs text-[var(--muted)]">
              {part}
              {oem ? ` · OEM ${oem}` : ""}
            </p>
            <dl className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-[var(--muted)]">Fresh offers</dt>
                <dd className="font-semibold">{data?.results.length ?? "—"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[var(--muted)]">Shown</dt>
                <dd className="font-semibold">{rows.length || "—"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[var(--muted)]">Stale dropped</dt>
                <dd className="font-semibold">{data?.droppedStale ?? "—"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[var(--muted)]">Ship to</dt>
                <dd className="font-semibold">{destination}</dd>
              </div>
            </dl>
          </div>

          <div className="panel p-4">
            <h3 className="text-sm font-bold">Quick filters</h3>
            <div className="mt-3">
              <label className="text-xs font-semibold text-[var(--muted)]">
                Max price ({currency}): {maxPrice}
              </label>
              <input
                className="mt-2 w-full"
                type="range"
                min={50}
                max={8000}
                step={50}
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
              />
            </div>
            <button type="button" className="btn-ghost mt-4 w-full text-xs" onClick={() => setMaxPrice(3000)}>
              Reset price
            </button>
          </div>

          <div className="panel p-4">
            <h3 className="text-sm font-bold">By source</h3>
            <ul className="mt-3 space-y-2 text-sm">
              {LIVE_SOURCES.map((s) => {
                const n = (data?.results || []).filter((r) => r.sourceId === s.id).length;
                return (
                  <li key={s.id} className="flex justify-between">
                    <span className="text-[var(--muted)]">{s.name}</span>
                    <span className="font-semibold">{n || "—"}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <label>{label}</label>
      {children}
    </div>
  );
}

function ResultRow({
  hit,
  query,
  destination,
}: {
  hit: SearchHit;
  query: string;
  destination: string;
}) {
  const fit = estimateFitment(hit, query);
  const tone =
    fit.tone === "ok"
      ? "badge-ok"
      : fit.tone === "warn"
        ? "badge-warn"
        : fit.tone === "bad"
          ? "badge-bad"
          : "badge-muted";

  return (
    <li className="grid gap-3 px-4 py-3 md:grid-cols-[72px_minmax(0,1.5fr)_minmax(0,0.9fr)_150px_110px] md:items-center">
      <div className="h-[56px] w-[72px] overflow-hidden rounded-md bg-slate-100">
        {hit.imageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={hit.imageUrl} alt="" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-[10px] text-slate-400">N/A</div>
        )}
      </div>
      <div className="min-w-0">
        <a href={hit.url} target="_blank" rel="noreferrer" className="font-semibold leading-snug hover:underline">
          {hit.title}
        </a>
        <p className="mt-1 text-xs text-[var(--muted)]">
          {hit.brand ? `${hit.brand} · ` : ""}
          {hit.sourceName} · {hit.country}
          {hit.ageDays != null ? ` · ${hit.ageDays}d` : ""}
        </p>
      </div>
      <div className="text-sm">
        <p className="font-bold">{formatMoney(hit.price, hit.currency)}</p>
        <p className="text-xs text-[var(--muted)]">To {destination}: shipping unknown</p>
      </div>
      <div>
        <span className={`badge ${tone}`}>
          {fit.label} · {Math.round(fit.confidence * 100)}%
        </span>
        <p className="mt-1 text-[10px] text-[var(--muted)]">title match only</p>
      </div>
      <div className="md:text-right">
        <a href={hit.url} target="_blank" rel="noreferrer" className="btn-primary inline-block px-3 py-1.5 text-xs">
          View
        </a>
      </div>
    </li>
  );
}
