import Link from "next/link";

export function SiteHeader({ tone = "light" }: { tone?: "light" | "on-dark" }) {
  const onDark = tone === "on-dark";
  return (
    <header
      className={`relative z-20 flex items-center justify-between gap-6 px-5 py-5 md:px-10 ${
        onDark ? "text-[var(--paper)]" : "text-[var(--ink)]"
      }`}
    >
      <Link href="/" className="group flex items-baseline gap-2">
        <span
          className="font-[family-name:var(--font-display)] text-2xl font-extrabold tracking-tight md:text-[1.75rem]"
          style={{ letterSpacing: "-0.03em" }}
        >
          AutoParts
        </span>
        <span
          className={`text-xs font-semibold uppercase tracking-[0.22em] ${
            onDark ? "text-[var(--signal)]" : "text-[var(--signal-deep)]"
          }`}
        >
          Core
        </span>
      </Link>
      <nav className="flex items-center gap-5 text-sm font-medium md:gap-8">
        <Link href="/search" className="opacity-90 transition hover:opacity-100">
          Поиск
        </Link>
        <Link href="/sources" className="opacity-90 transition hover:opacity-100">
          Источники
        </Link>
        <Link
          href="/search?q=фара+Passat+B8"
          className={`rounded-sm px-3.5 py-2 text-sm font-semibold transition ${
            onDark
              ? "bg-[var(--signal)] text-[var(--ink)] hover:bg-[#f0b52f]"
              : "bg-[var(--ink)] text-[var(--paper)] hover:bg-[var(--ink-soft)]"
          }`}
        >
          Найти запчасть
        </Link>
      </nav>
    </header>
  );
}
