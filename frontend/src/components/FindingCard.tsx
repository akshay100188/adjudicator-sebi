import type { Finding } from "@/lib/api";

const CONF: Record<string, string> = {
  high: "bg-rose-900/50 text-rose-300 border-rose-800",
  medium: "bg-amber-900/50 text-amber-300 border-amber-800",
  low: "bg-slate-800 text-slate-300 border-slate-700",
};

export function FindingCard({ f }: { f: Finding }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="font-mono text-xs text-slate-400">{f.obligation_id}</span>
        <span className={`rounded border px-2 py-0.5 text-[11px] ${CONF[f.confidence] || CONF.low}`}>
          {f.confidence} confidence
        </span>
      </div>
      <p className="text-sm font-medium text-slate-100">{f.gap_summary}</p>
      <dl className="mt-3 space-y-2 text-xs">
        <div>
          <dt className="text-slate-500">Evidence (from scenario)</dt>
          <dd className="text-slate-300">{f.evidence}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Recommended action</dt>
          <dd className="text-slate-300">{f.recommended_action}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Source</dt>
          <dd className="font-mono text-emerald-400">{f.citation}</dd>
        </div>
      </dl>
    </div>
  );
}
