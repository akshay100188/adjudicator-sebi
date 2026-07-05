"use client";

import { useRef, useState } from "react";
import {
  analyze,
  analyzeDocument,
  type AnalyzeResult,
  type DocumentAnalyzeResult,
} from "@/lib/api";
import { FindingCard } from "@/components/FindingCard";
import { TrajectoryViewer } from "@/components/TrajectoryViewer";

const SAMPLES = [
  "We settle client running accounts once a year. After settlement we notify clients by email only. When our operations team is busy we retain client funds to ease processing.",
  "Our authorised persons collect funds and securities directly from clients to speed onboarding, and they run their own proprietary trades using the pooled client money.",
  "Is our running-account settlement policy compliant as of today, and has anything changed in the underlying rules?",
];

type Mode = "scenario" | "document";

export default function AnalyzePage() {
  const [mode, setMode] = useState<Mode>("scenario");
  const [scenario, setScenario] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | DocumentAnalyzeResult | null>(null);
  const [error, setError] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  const docResult = result && "assertions" in result ? (result as DocumentAnalyzeResult) : null;

  async function run() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      if (mode === "scenario") setResult(await analyze(scenario));
      else if (file) setResult(await analyzeDocument(file));
    } catch (e) {
      setError(e instanceof Error ? e.message : "error");
    } finally {
      setLoading(false);
    }
  }

  const canRun = mode === "scenario" ? scenario.trim().length > 0 : file !== null;

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Scenario runner</h1>
      <p className="mt-1 text-sm text-slate-500">
        Describe a product change or policy, or upload a policy document. The agent retrieves the
        currently-valid SEBI obligations that apply, traces supersession, and surfaces gaps — each cited
        to a source circular.
      </p>

      <div className="mt-4 inline-flex rounded-lg border border-slate-300 p-0.5 text-xs dark:border-slate-800">
        {(["scenario", "document"] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => {
              setMode(m);
              setResult(null);
              setError("");
            }}
            className={`rounded-md px-3 py-1.5 font-medium transition ${
              mode === m
                ? "bg-emerald-700 text-white"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            }`}
          >
            {m === "scenario" ? "Scenario" : "Document upload"}
          </button>
        ))}
      </div>

      {mode === "scenario" ? (
        <>
          <textarea
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            rows={5}
            placeholder="Describe your stock-broker product change or policy…"
            className="mt-4 w-full rounded-lg border border-slate-300 bg-white p-3 text-sm text-slate-800 outline-none focus:border-slate-400 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-200 dark:focus:border-slate-600"
          />
          <div className="mt-2 flex flex-wrap gap-2">
            {SAMPLES.map((s, i) => (
              <button
                key={i}
                onClick={() => setScenario(s)}
                className="rounded border border-slate-300 bg-white px-2 py-1 text-[11px] text-slate-600 hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-400 dark:hover:bg-slate-800"
              >
                sample {i + 1}
              </button>
            ))}
          </div>
        </>
      ) : (
        <div className="mt-4">
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.txt,.md,text/plain,application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-emerald-700 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-emerald-600 dark:text-slate-400"
          />
          <p className="mt-2 text-[11px] text-slate-400 dark:text-slate-600">
            PDF, .txt or .md, up to 5 MB. The upload is processed in memory and{" "}
            <span className="font-medium">never stored</span> — only the extracted practice assertions
            are analysed. Uploaded text is treated as data, never as instructions.
          </p>
        </div>
      )}

      <button
        onClick={run}
        disabled={loading || !canRun}
        className="mt-3 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600 disabled:opacity-40"
      >
        {loading
          ? "Analysing… (agent is running, ~30–60s)"
          : mode === "scenario"
          ? "Analyse"
          : "Analyse document"}
      </button>

      {error && <p className="mt-4 text-sm text-rose-600 dark:text-rose-400">Error: {error}</p>}

      {result && (
        <div className="mt-8 space-y-6">
          {docResult && (
            <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/40">
              <div className="mb-2 flex items-center gap-3">
                <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                  Practice assertions extracted ({docResult.assertions.length})
                </h2>
                {docResult.raw_document_persisted === false && (
                  <span className="rounded-full border border-emerald-300 bg-emerald-50 px-2 py-0.5 text-[11px] text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/30 dark:text-emerald-400">
                    raw upload not stored
                  </span>
                )}
              </div>
              <ul className="list-disc space-y-1 pl-5 text-xs text-slate-600 dark:text-slate-400">
                {docResult.assertions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </section>
          )}

          <section>
            <div className="mb-3 flex items-center gap-3">
              <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Findings ({result.findings.length})
              </h2>
              {result.findings.length === 0 && (
                <span className="text-xs text-emerald-600 dark:text-emerald-400">
                  No gaps identified against the considered obligations.
                </span>
              )}
            </div>
            <div className="space-y-3">
              {result.findings.map((f) => (
                <FindingCard key={f.obligation_id} f={f} />
              ))}
            </div>
            <p className="mt-2 text-[11px] text-slate-400 dark:text-slate-600">
              {result.obligations_considered.length} obligations considered ·{" "}
              {result.findings.length} flagged
            </p>
          </section>

          <TrajectoryViewer
            steps={result.trajectory}
            route={result.route}
            reasoning={result.reasoning}
          />

          <p className="rounded border border-amber-300 bg-amber-50 p-3 text-[11px] text-amber-800 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-300/80">
            {result.disclaimer}
          </p>
        </div>
      )}
    </div>
  );
}
