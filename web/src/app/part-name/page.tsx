import { AppShell } from "@/components/AppShell";
import Link from "next/link";

export default function PartNamePage() {
  return (
    <AppShell title="Part Name Search" subtitle="Free-text part queries">
      <div className="panel p-6">
        <p className="text-sm text-[var(--muted)]">
          Part name search is available on Vehicle Search (Part dropdown + query composition).
        </p>
        <Link href="/search" className="btn-primary mt-4 inline-block">
          Open Vehicle Search
        </Link>
      </div>
    </AppShell>
  );
}
