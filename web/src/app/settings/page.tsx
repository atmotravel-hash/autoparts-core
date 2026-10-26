import { AppShell } from "@/components/AppShell";

export default function SettingsPage() {
  return (
    <AppShell title="Settings" subtitle="Workspace preferences">
      <div className="panel p-6 text-sm text-[var(--muted)]">
        <p>Default markets: UA · MD · PL · RO · BG · PT</p>
        <p className="mt-2">No CAPTCHA bypass. Credential sources stay deferred.</p>
      </div>
    </AppShell>
  );
}
