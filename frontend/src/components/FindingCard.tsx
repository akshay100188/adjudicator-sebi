import type { Finding } from "@/lib/api";

const CONF: Record<string, string> = {
  high: "bg-rose-50 text-rose-700 border-rose-300 dark:bg-rose-900/50 dark:text-rose-300 dark:border-rose-800",
  medium: "bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-900/50 dark:text-amber-300 dark:border-amber-800",
  low: "bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700",
};

export function FindingCard({ f }: { f: Finding }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900/40">
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="font-mono text-xs text-slate-600 dark:text-slate-400">{f.obligation_id}</span>
        <span className={`rounded border px-2 py-0.5 text-[11px] ${CONF[f.confidence] || CONF.low}`}>
          {f.confidence} confidence
        </span>
      </div>
      <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{f.gap_summary}</p>
      <dl className="mt-3 space-y-2 text-xs">
        <div>
          <dt className="text-slate-500">Evidence (from scenario)</dt>
          <dd className="text-slate-700 dark:text-slate-300">{f.evidence}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Recommended action</dt>
          <dd className="text-slate-700 dark:text-slate-300">{f.recommended_action}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Source</dt>
          <dd className="font-mono text-emerald-600 dark:text-emerald-400">{f.citation}</dd>
        </div>
      </dl>
    </div>
  );
}
