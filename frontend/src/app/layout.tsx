import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Project Adjudicator (SEBI) — Agentic RAG",
  description: "A regulatory-intelligence prototype over the public SEBI corpus. Not legal advice.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="flex min-h-screen">
          <aside className="w-64 shrink-0 border-r border-slate-800 bg-slate-900/40 p-5">
            <div className="mb-8">
              <div className="text-lg font-semibold text-slate-100">Adjudicator</div>
              <div className="text-xs text-slate-500">SEBI · Agentic RAG prototype</div>
            </div>
            <nav className="space-y-1 text-sm">
              <Link href="/analyze" className="block rounded px-3 py-2 text-slate-300 hover:bg-slate-800">
                Scenario runner
              </Link>
              <Link href="/obligations" className="block rounded px-3 py-2 text-slate-300 hover:bg-slate-800">
                Obligation browser
              </Link>
            </nav>
            <div className="mt-10 rounded border border-amber-900/50 bg-amber-950/30 p-3 text-[11px] leading-relaxed text-amber-300/80">
              Prototype — <strong>not legal advice</strong>. Identifies potential gaps for expert review;
              every finding cites a source circular.
            </div>
          </aside>
          <main className="flex-1 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
