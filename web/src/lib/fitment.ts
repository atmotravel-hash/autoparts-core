import type { SearchHit } from "./catalog/types";

export type FitmentBadge = {
  label: string;
  tone: "ok" | "warn" | "bad" | "muted";
  confidence: number;
};

/** Heuristic UI badge from title/query — not a verified fitment engine claim. */
export function estimateFitment(hit: SearchHit, query: string): FitmentBadge {
  const t = `${hit.title} ${hit.brand || ""}`.toLowerCase();
  const q = query.toLowerCase();
  const tokens = q.split(/[\s+/,_-]+/).filter((x) => x.length > 1);
  const hits = tokens.filter((tok) => t.includes(tok)).length;
  const ratio = tokens.length ? hits / tokens.length : 0;

  if (ratio >= 0.75) return { label: "Likely Compatible", tone: "warn", confidence: 0.68 + ratio * 0.2 };
  if (ratio >= 0.4) return { label: "Unconfirmed", tone: "bad", confidence: 0.4 + ratio * 0.2 };
  return { label: "Unconfirmed", tone: "muted", confidence: 0.35 };
}

export function formatMoney(amount: number | null, currency: string | null) {
  if (amount == null) return "—";
  const cur = (currency || "EUR").toUpperCase();
  try {
    return new Intl.NumberFormat("en-EU", {
      style: "currency",
      currency: cur,
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `${amount} ${cur}`;
  }
}
