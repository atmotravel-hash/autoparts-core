import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-black/10 bg-[var(--asphalt)] px-5 py-10 text-[var(--paper)] md:px-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="font-[family-name:var(--font-display)] text-xl font-bold tracking-tight">
            AutoParts Core
          </p>
          <p className="mt-2 max-w-md text-sm text-white/65">
            Публичные каталоги EU · MD · UA. Без ключей, без обхода CAPTCHA. Demo-данные
            помечаются отдельно.
          </p>
        </div>
        <div className="flex gap-6 text-sm text-white/75">
          <Link href="/search" className="hover:text-white">
            Поиск
          </Link>
          <Link href="/sources" className="hover:text-white">
            Источники
          </Link>
        </div>
      </div>
    </footer>
  );
}
