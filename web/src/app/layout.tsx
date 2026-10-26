import type { Metadata } from "next";
import { Manrope } from "next/font/google";
import "./globals.css";

const body = Manrope({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "AutoParts Intelligence",
  description: "Find. Compare. Buy. — vehicle parts search across EU · MD · UA catalogs",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${body.variable} antialiased`}>{children}</body>
    </html>
  );
}
