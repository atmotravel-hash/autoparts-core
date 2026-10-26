import { NextRequest, NextResponse } from "next/server";
import { runCatalogSearch } from "@/lib/catalog/search";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q") || "";
  const sources = req.nextUrl.searchParams.get("sources");
  const limit = Number(req.nextUrl.searchParams.get("limit") || "6");

  try {
    const data = await runCatalogSearch({
      query: q,
      sources: sources ? sources.split(",").map((s) => s.trim()).filter(Boolean) : undefined,
      limitPerSource: Number.isFinite(limit) ? limit : 6,
    });
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json(
      { query: q, results: [], errors: [{ sourceId: "server", message: String(err) }], tookMs: 0 },
      { status: 500 },
    );
  }
}
