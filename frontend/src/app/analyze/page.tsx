"use client";

import { useState } from "react";
import { analyze, type AnalyzeResult } from "@/lib/api";
import { FindingCard } from "@/components/FindingCard";
import { TrajectoryViewer } from "@/components/TrajectoryViewer";

const SAMPLES = [
  "We settle client running accounts once a year. After settlement we notify clients by email only. When our operations team is busy we retain client funds to ease processing.",
  "Our authorised persons collect funds and securities directly from clients to speed onboarding, and they run their own proprietary trades using the pooled client money.",
  "Is our running-account settlement policy compliant as of today, and has anything changed in the underlying rules?",
];

export default function AnalyzePage() {
  const [scenario, setScenario] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState("");

  async function run() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await analyze(scenario));
    } catch (e) {
      setError(e instanceof Error ? e.message : "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-xl font-semibold text-slate-100">Scenario runner</h1>
      <p className="mt-1 text-sm text-slate-500">
        Describe a product change or policy. The agent retrieves the currently-valid SEBI obligations
        that apply, traces supersession, and surfaces gaps — each cited to a source circular.
      </p>

      <textarea
        value={scenario}
        onChange={(e) => setScenario(e.target.value)}
        rows={5}
        placeholder="Describe your stock-broker product change or policy…"
        className="mt-4 w-full rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-200 outline-none focus:border-slate-600"
      />
      <div className="mt-2 flex flex-wrap gap-2">
        {SAMPLES.map((s, i) => (
          <button
            key={i}
            onClick={() => setScenario(s)}
            className="rounded border border-slate-800 bg-slate-900/60 px-2 py-1 text-[11px] text-slate-400 hover:bg-slate-800"
          >
            sample {i + 1}
          </button>
        ))}
      </div>
      <button
        onClick={run}
        disabled={loading || !scenario.trim()}
        className="mt-3 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-40"
      >
        {loading ? "Analysing… (agent is running, ~30–60s)" : "Analyse"}
      </button>

      {error && <p className="mt-4 text-sm text-rose-400">Error: {error}</p>}

      {result && (
        <div className="mt-8 space-y-6">
          <section>
            <div className="mb-3 flex items-center gap-3">
              <h2 className="text-sm font-semibold text-slate-200">
                Findings ({result.findings.length})
              </h2>
              {result.findings.length === 0 && (
                <span className="text-xs text-emerald-400">
                  No gaps identified against the considered obligations.
                </span>
              )}
            </div>
            <div className="space-y-3">
              {result.findings.map((f) => (
                <FindingCard key={f.obligation_id} f={f} />
              ))}
            </div>
            <p className="mt-2 text-[11px] text-slate-600">
              {result.obligations_considered.length} obligations considered ·{" "}
              {result.findings.length} flagged
            </p>
          </section>

          <TrajectoryViewer
            steps={result.trajectory}
            route={result.route}
            reasoning={result.reasoning}
          />

          <p className="rounded border border-amber-900/50 bg-amber-950/30 p-3 text-[11px] text-amber-300/80">
            {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
