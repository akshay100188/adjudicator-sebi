import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { Umami } from "@/components/analytics/Umami";
import { ThemeToggle } from "@/components/ThemeToggle";

export const metadata: Metadata = {
  title: "Project Adjudicator (SEBI) — Agentic RAG",
  description: "A regulatory-intelligence prototype over the public SEBI corpus. Not legal advice.",
};

// Applied before paint so the chosen theme doesn't flash. Light is the default:
// the `dark` class is only added when the user explicitly opted into dark mode.
const themeInit = `try{if(localStorage.theme==='dark')document.documentElement.classList.add('dark')}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body className="min-h-screen">
        <div className="flex min-h-screen">
          <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900/40">
            <div className="mb-8">
              <div className="text-lg font-semibold text-slate-900 dark:text-slate-100">Adjudicator</div>
              <div className="text-xs text-slate-500">SEBI · Agentic RAG prototype</div>
            </div>
            <nav className="space-y-1 text-sm">
              <Link href="/analyze" className="block rounded px-3 py-2 text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
                Scenario runner
              </Link>
              <Link href="/obligations" className="block rounded px-3 py-2 text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
                Obligation browser
              </Link>
              <Link href="/code" className="block rounded px-3 py-2 text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
                Code analysis
              </Link>
            </nav>
            <div className="mt-10 rounded border border-amber-300 bg-amber-50 p-3 text-[11px] leading-relaxed text-amber-800 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-300/80">
              Prototype — <strong>not legal advice</strong>. Identifies potential gaps for expert review;
              every finding cites a source circular.
            </div>
            <div className="mt-auto pt-6">
              <ThemeToggle />
            </div>
          </aside>
          <main className="flex-1 p-8">{children}</main>
        </div>
        <Umami />
      </body>
    </html>
  );
}
