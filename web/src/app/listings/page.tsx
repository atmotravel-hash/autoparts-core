import { AppShell } from "@/components/AppShell";
import Link from "next/link";

export default function ListingsPage() {
  return (
    <AppShell title="Listings" subtitle="Browse offers from the last search">
      <div className="panel p-6">
        <p className="text-sm text-[var(--muted)]">Run a Vehicle Search to populate live listings.</p>
        <Link href="/search" className="btn-primary mt-4 inline-block">
          Go to Vehicle Search
        </Link>
      </div>
    </AppShell>
  );
}
