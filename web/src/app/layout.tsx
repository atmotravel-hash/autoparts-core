import type { Metadata } from "next";
import { Manrope, Syne } from "next/font/google";
import "./globals.css";

const display = Syne({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["600", "700", "800"],
});

const body = Manrope({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "AutoParts Core — поиск запчастей EU · MD · UA",
  description:
    "Живой поиск автозапчастей по публичным каталогам OLX, Prom.ua, Flagma, 999.md и Bazar.bg — без ключей и без обхода CAPTCHA.",
  metadataBase: new URL("https://autoparts-core.vercel.app"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className={`${display.variable} ${body.variable} antialiased`}>{children}</body>
    </html>
  );
}
