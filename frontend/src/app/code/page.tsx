"use client";

import { useState } from "react";
import { codeAnalyse, type CodeResult } from "@/lib/api";
import { FindingCard } from "@/components/FindingCard";
import { TrajectoryViewer } from "@/components/TrajectoryViewer";

export default function CodePage() {
  const [path, setPath] = useState("data/code_samples/broking_app");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CodeResult | null>(null);
  const [error, setError] = useState("");

  async function run() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await codeAnalyse(path));
    } catch (e) {
      setError(e instanceof Error ? e.message : "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Code analysis</h1>
      <p className="mt-1 text-sm text-slate-500">
        Scans a repository for compliance-relevant <em>signals</em> (never the code itself) and maps
        them to SEBI obligations via the same agent. Privacy-by-design: code is never stored or sent to
        the LLM — only file/line/category metadata flows downstream.
      </p>

      <div className="mt-4 flex gap-2">
        <input
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="server-side repo path"
          className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-slate-400 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-200 dark:focus:border-slate-600"
        />
        <button
          onClick={run}
          disabled={loading || !path.trim()}
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-40"
        >
          {loading ? "Scanning… (~30–60s)" : "Scan"}
        </button>
      </div>

      {error && <p className="mt-4 text-sm text-rose-600 dark:text-rose-400">Error: {error}</p>}

      {result && (
        <div className="mt-8 space-y-6">
          {result.signals.length === 0 && (
            <p className="rounded border border-slate-200 bg-white p-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-slate-900/40 dark:text-slate-400">
              No compliance-relevant code signals detected in {result.files_scanned} scanned file(s).
            </p>
          )}

          {result.signals.length > 0 && (
          <section>
            <h2 className="mb-2 text-sm font-semibold text-slate-800 dark:text-slate-200">
              Signals ({result.signals.length}) · {result.files_scanned} files ·{" "}
              {result.languages.join(", ")}
            </h2>
            <ul className="space-y-1 text-xs">
              {result.signals.map((s, i) => (
                <li key={i} className="flex gap-3">
                  <span className="font-mono text-slate-500">
                    {s.file}:{s.line}
                  </span>
                  <span className="rounded border border-slate-300 bg-slate-100 px-1.5 text-[10px] text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                    {s.category}
                  </span>
                  <span className="text-slate-600 dark:text-slate-400">{s.description}</span>
                </li>
              ))}
            </ul>
          </section>
          )}

          {result.route && (
            <>
              <section>
                <h2 className="mb-3 text-sm font-semibold text-slate-800 dark:text-slate-200">
                  Mapped obligation findings ({result.findings.length})
                </h2>
                <div className="space-y-3">
                  {result.findings.map((f) => (
                    <FindingCard key={f.obligation_id} f={f} />
                  ))}
                </div>
              </section>

              <TrajectoryViewer steps={result.trajectory} route={result.route} reasoning={result.reasoning} />
            </>
          )}

          <p className="rounded border border-amber-300 bg-amber-50 p-3 text-[11px] text-amber-800 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-300/80">
            {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
