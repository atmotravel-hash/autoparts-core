import { AppShell } from "@/components/AppShell";

export default function SettingsPage() {
  return (
    <AppShell title="Settings" subtitle="Workspace preferences">
      <div className="panel p-6 text-sm text-[var(--muted)]">
        <p>Product markets: UA · MD · RO only.</p>
        <p className="mt-2">Listings older than 30 days are dropped when age is known.</p>
        <p className="mt-2">No CAPTCHA bypass. Credential sources stay deferred.</p>
      </div>
    </AppShell>
  );
}
