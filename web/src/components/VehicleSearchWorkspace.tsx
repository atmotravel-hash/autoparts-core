"use client";

import { FormEvent, useMemo, useState, useTransition } from "react";
import type { SearchHit, SearchResponse, SourceId } from "@/lib/catalog/types";
import { LIVE_SOURCES } from "@/lib/catalog/types";
import { estimateFitment, formatMoney } from "@/lib/fitment";

const MAKES = ["Volkswagen", "BMW", "Audi", "Skoda", "Toyota"];
const MODELS = ["Passat", "Golf", "3 Series", "A4", "Octavia"];
const GENS = ["B8 (2014–2023)", "B7", "Mk7", "F30", "B9"];
const PARTS = ["Headlight", "Front fender", "Bumper", "Side mirror"];
const YEARS = Array.from({ length: 16 }, (_, i) => 2024 - i);

function buildQuery(make: string, model: string, gen: string, part: string, oem: string) {
  const g = gen.split(/\s+/)[0];
  const partMap: Record<string, string> = {
    Headlight: "фара",
    "Front fender": "крыло",
    Bumper: "бампер",
    "Side mirror": "зеркало",
  };
  const partQ = partMap[part] || part;
  return [partQ, model, g, oem].filter(Boolean).join(" ").trim();
}

export function VehicleSearchWorkspace({
  initialData = null,
}: {
  initialData?: SearchResponse | null;
}) {
  const [make, setMake] = useState("Volkswagen");
  const [model, setModel] = useState("Passat");
  const [generation, setGeneration] = useState("B8 (2014–2023)");
  const [year, setYear] = useState(2017);
  const [part, setPart] = useState("Headlight");
  const [oem, setOem] = useState("3G1941007A");
  const [condition, setCondition] = useState("Any");
  const [currency, setCurrency] = useState("EUR");
  const [destination, setDestination] = useState("UA");
  const [sources, setSources] = useState<SourceId[]>(LIVE_SOURCES.map((s) => s.id));
  const [data, setData] = useState<SearchResponse | null>(initialData);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();
  const [hideWeak, setHideWeak] = useState(false);
  const [maxPrice, setMaxPrice] = useState(2000);

  const query = useMemo(
    () => buildQuery(make, model, generation, part, oem),
    [make, model, generation, part, oem],
  );

  const rows = useMemo(() => {
    let list = data?.results || [];
    if (hideWeak) {
      list = list.filter((h) => estimateFitment(h, query).tone !== "muted");
    }
    list = list.filter((h) => h.price == null || h.price <= maxPrice);
    return list;
  }, [data, hideWeak, maxPrice, query]);

  function toggleSource(id: SourceId) {
    setSources((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  async function onSearch(e: FormEvent) {
    e.preventDefault();
    setError(null);
    startTransition(async () => {
      try {
        const params = new URLSearchParams({
          q: query,
          sources: sources.join(","),
          limit: "8",
        });
        const res = await fetch(`/api/search?${params}`);
        const json = (await res.json()) as SearchResponse;
        setData(json);
      } catch (err) {
        setError(String(err));
      }
    });
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_300px]">
      <div className="min-w-0 space-y-4">
        <form onSubmit={onSearch} className="panel p-4 md:p-5">
          <div className="mb-4 flex flex-wrap gap-2 border-b border-[var(--line)] pb-3 text-sm font-semibold">
            <span className="rounded-md bg-blue-50 px-3 py-1.5 text-[var(--blue)]">Vehicle + Part</span>
            <span className="rounded-md px-3 py-1.5 text-[var(--muted)]">OEM Number</span>
            <span className="rounded-md px-3 py-1.5 text-[var(--muted)]">Part Name</span>
            <span className="rounded-md px-3 py-1.5 text-[var(--muted)]">VIN (optional)</span>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            <div className="field">
              <label>Make</label>
              <select value={make} onChange={(e) => setMake(e.target.value)}>
                {MAKES.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Model</label>
              <select value={model} onChange={(e) => setModel(e.target.value)}>
                {MODELS.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Generation</label>
              <select value={generation} onChange={(e) => setGeneration(e.target.value)}>
                {GENS.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Year</label>
              <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
                {YEARS.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Part</label>
              <select value={part} onChange={(e) => setPart(e.target.value)}>
                {PARTS.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className="field">
              <label>OEM number</label>
              <input value={oem} onChange={(e) => setOem(e.target.value)} placeholder="3G1941007A" />
            </div>
            <div className="field">
              <label>Condition</label>
              <select value={condition} onChange={(e) => setCondition(e.target.value)}>
                {["Any", "NEW", "USED", "REFURBISHED", "DAMAGED"].map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Destination</label>
              <select value={destination} onChange={(e) => setDestination(e.target.value)}>
                {["UA", "MD", "PL", "RO", "BG", "DE"].map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Currency</label>
              <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                {["EUR", "USD", "UAH", "MDL", "PLN"].map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <p className="mb-2 text-xs font-semibold text-[var(--muted)]">Sources</p>
            <div className="flex flex-wrap gap-2">
              {LIVE_SOURCES.map((s) => {
                const on = sources.includes(s.id);
                return (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => toggleSource(s.id)}
                    className={`rounded-md border px-2.5 py-1 text-xs font-semibold ${
                      on ? "border-blue-600 bg-blue-600 text-white" : "border-[var(--line)] text-[var(--muted)]"
                    }`}
                  >
                    {s.name}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-[var(--muted)]">
              Query: <span className="font-semibold text-[var(--ink)]">{query}</span>
            </p>
            <button type="submit" className="btn-primary" disabled={pending || !sources.length}>
              {pending ? "Searching…" : "Search"}
            </button>
          </div>
        </form>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <section className="panel overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--line)] px-4 py-3">
            <h2 className="text-base font-bold">Results ({rows.length} listings)</h2>
            <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
              <span>Cheapest first</span>
              {data ? <span>· {data.tookMs} ms</span> : null}
            </div>
          </div>

          {!data && (
            <p className="px-4 py-10 text-sm text-[var(--muted)]">
              Submit a search to load ranked offers from live catalogs.
            </p>
          )}

          <ul className="divide-y divide-[var(--line)]">
            {rows.map((hit) => (
              <ResultRow key={`${hit.sourceId}-${hit.url}`} hit={hit} query={query} destination={destination} />
            ))}
          </ul>

          {data && !rows.length && (
            <p className="px-4 py-8 text-sm text-[var(--muted)]">No listings match current filters.</p>
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
              <dt className="text-[var(--muted)]">Found</dt>
              <dd className="font-semibold">{data?.results.length ?? "—"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-[var(--muted)]">Shown</dt>
              <dd className="font-semibold">{rows.length || "—"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-[var(--muted)]">Destination</dt>
              <dd className="font-semibold">{destination}</dd>
            </div>
          </dl>
        </div>

        <div className="panel p-4">
          <h3 className="text-sm font-bold">Quick filters</h3>
          <label className="mt-3 flex items-center gap-2 text-sm">
            <input type="checkbox" checked={hideWeak} onChange={(e) => setHideWeak(e.target.checked)} />
            Hide weak title matches
          </label>
          <div className="mt-4">
            <label className="text-xs font-semibold text-[var(--muted)]">
              Max price ({currency}): {maxPrice}
            </label>
            <input
              className="mt-2 w-full"
              type="range"
              min={50}
              max={5000}
              step={50}
              value={maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value))}
            />
          </div>
          <div className="mt-4 flex gap-2">
            <button type="button" className="btn-primary flex-1 text-center text-xs" onClick={() => setHideWeak(false)}>
              Apply filters
            </button>
            <button
              type="button"
              className="btn-ghost flex-1 text-xs"
              onClick={() => {
                setHideWeak(false);
                setMaxPrice(2000);
              }}
            >
              Reset
            </button>
          </div>
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
    <li className="grid gap-3 px-4 py-3 md:grid-cols-[72px_minmax(0,1.4fr)_minmax(0,1fr)_140px_120px] md:items-center">
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
        </p>
      </div>
      <div className="text-sm">
        <p className="font-bold">{formatMoney(hit.price, hit.currency)}</p>
        <p className="text-xs text-[var(--muted)]">Delivery to {destination}: Unknown</p>
      </div>
      <div>
        <span className={`badge ${tone}`}>
          {fit.label} · {Math.round(fit.confidence * 100)}%
        </span>
        <p className="mt-1 text-[10px] text-[var(--muted)]">title heuristic — not verified OEM proof</p>
      </div>
      <div className="md:text-right">
        <a href={hit.url} target="_blank" rel="noreferrer" className="btn-primary inline-block px-3 py-1.5 text-xs">
          View
        </a>
      </div>
    </li>
  );
}
