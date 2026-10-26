import { AppShell } from "@/components/AppShell";
import { LIVE_SOURCES, MARKET_GROUPS, MAX_LISTING_AGE_DAYS } from "@/lib/catalog/types";

export default function SettingsPage() {
  const markets = MARKET_GROUPS.map((g) => `${g.country} (${g.label})`).join(", ");

  return (
    <AppShell title="Settings" subtitle="Workspace preferences">
      <div className="panel space-y-3 p-6 text-sm text-[var(--muted)]">
        <p>
          Product markets: <span className="font-semibold text-[var(--ink)]">{markets}</span>
        </p>
        <p>
          Live sources:{" "}
          <span className="font-semibold text-[var(--ink)]">{LIVE_SOURCES.length}</span> zero-key
          catalogs (GraphQL / JSON-LD).
        </p>
        <p>
          Listings older than {MAX_LISTING_AGE_DAYS} days are dropped when age is known. Unknown age
          is hidden in strict freshness mode.
        </p>
        <p>No CAPTCHA / Cloudflare bypass. Blocked sources stay deferred with a documented access path.</p>
      </div>
    </AppShell>
  );
}
