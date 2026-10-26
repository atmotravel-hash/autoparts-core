import { AppShell } from "@/components/AppShell";
import Link from "next/link";

export default function OemPage() {
  return (
    <AppShell title="OEM Search" subtitle="Search by manufacturer / OEM numbers">
      <div className="panel p-6">
        <p className="text-sm text-[var(--muted)]">
          Use Vehicle Search and put the OEM into the OEM field — live catalogs are queried with that token.
        </p>
        <Link href="/search" className="btn-primary mt-4 inline-block">
          Open Vehicle Search
        </Link>
      </div>
    </AppShell>
  );
}
