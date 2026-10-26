"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Dashboard", icon: "▦" },
  { href: "/search", label: "Vehicle Search", icon: "⌕" },
  { href: "/oem", label: "OEM Search", icon: "#" },
  { href: "/part-name", label: "Part Name Search", icon: "≡" },
  { href: "/listings", label: "Listings", icon: "☰" },
  { href: "/sources", label: "Source Connectors", icon: "⧉" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <aside className="sidebar hidden min-h-screen flex-col px-4 py-5 md:flex">
        <div className="mb-6 px-2">
          <p className="text-[15px] font-extrabold tracking-tight text-white">AutoParts Intelligence</p>
          <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-400">UA · MD · RO</p>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map((item) => {
            const active =
              item.href === "/search"
                ? pathname === "/search" || pathname === "/"
                : item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
            // Home redirects to search UX — highlight Vehicle Search on /
            const isActive =
              item.href === "/search"
                ? pathname === "/" || pathname.startsWith("/search")
                : item.href === "/"
                  ? false
                  : active;
            return (
              <Link key={item.href} href={item.href === "/" ? "/search" : item.href} className={`nav-item ${isActive ? "active" : ""}`}>
                <span className="w-4 text-center text-xs opacity-80">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="mt-4 border-t border-white/10 px-2 pt-4">
          <p className="text-sm font-semibold text-white">John Doe</p>
          <p className="text-xs text-slate-400">Pro Plan</p>
        </div>
      </aside>

      <div className="min-w-0">
        <header className="border-b border-[var(--line)] bg-white px-4 py-4 md:px-6">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h1 className="text-xl font-bold tracking-tight md:text-2xl">{title}</h1>
              {subtitle ? <p className="mt-0.5 text-sm text-[var(--muted)]">{subtitle}</p> : null}
            </div>
            <Link href="/search" className="btn-primary md:hidden">
              Search
            </Link>
          </div>
          <nav className="mt-3 flex gap-2 overflow-x-auto pb-1 md:hidden">
            {NAV.filter((n) => n.href !== "/").map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="whitespace-nowrap rounded-full border border-[var(--line)] bg-white px-3 py-1 text-xs font-semibold text-[var(--muted)]"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <div className="px-3 py-4 md:px-6 md:py-5">{children}</div>
      </div>
    </div>
  );
}
