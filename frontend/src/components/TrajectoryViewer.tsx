import type { TrajectoryStep } from "@/lib/api";

const TOOL_COLOR: Record<string, string> = {
  temporal_filter: "bg-sky-900/50 text-sky-300 border-sky-800",
  hybrid_search: "bg-violet-900/50 text-violet-300 border-violet-800",
  rerank: "bg-fuchsia-900/50 text-fuchsia-300 border-fuchsia-800",
  expand_to_parent: "bg-emerald-900/50 text-emerald-300 border-emerald-800",
  graph_lookup: "bg-amber-900/50 text-amber-300 border-amber-800",
};

export function TrajectoryViewer({
  steps,
  route,
  reasoning,
}: {
  steps: TrajectoryStep[];
  route: string;
  reasoning: string;
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-5">
      <div className="mb-3 flex items-center gap-3">
        <h3 className="text-sm font-semibold text-slate-200">Agent trajectory</h3>
        <span className="rounded-full border border-slate-700 bg-slate-800 px-2 py-0.5 text-[11px] text-slate-300">
          route: {route}
        </span>
        <span className="text-[11px] text-slate-500">{steps.length} tool calls</span>
      </div>
      <ol className="space-y-2">
        {steps.map((s) => (
          <li key={s.step} className="flex gap-3 text-xs">
            <span className="mt-0.5 w-5 shrink-0 text-right text-slate-600">{s.step}</span>
            <span
              className={`h-fit shrink-0 rounded border px-2 py-0.5 font-mono ${
                TOOL_COLOR[s.tool] || "bg-slate-800 text-slate-300 border-slate-700"
              }`}
            >
              {s.tool}
            </span>
            <div className="min-w-0 flex-1">
              <div className="truncate font-mono text-slate-500">{JSON.stringify(s.args)}</div>
              <div className="truncate text-slate-400">{JSON.stringify(s.observation)}</div>
            </div>
          </li>
        ))}
      </ol>
      {reasoning && (
        <div className="mt-4 border-t border-slate-800 pt-3 text-xs text-slate-400">
          <span className="font-semibold text-slate-300">Reasoning: </span>
          {reasoning}
        </div>
      )}
    </div>
  );
}
