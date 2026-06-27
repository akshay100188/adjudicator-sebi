import type { TrajectoryStep } from "@/lib/api";

const TOOL_COLOR: Record<string, string> = {
  temporal_filter: "bg-sky-50 text-sky-700 border-sky-300 dark:bg-sky-900/50 dark:text-sky-300 dark:border-sky-800",
  hybrid_search: "bg-violet-50 text-violet-700 border-violet-300 dark:bg-violet-900/50 dark:text-violet-300 dark:border-violet-800",
  rerank: "bg-fuchsia-50 text-fuchsia-700 border-fuchsia-300 dark:bg-fuchsia-900/50 dark:text-fuchsia-300 dark:border-fuchsia-800",
  expand_to_parent: "bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-900/50 dark:text-emerald-300 dark:border-emerald-800",
  graph_lookup: "bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-900/50 dark:text-amber-300 dark:border-amber-800",
};

const TOOL_FALLBACK =
  "bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700";

export function TrajectoryViewer({
  steps,
  route,
  reasoning,
}: {
  steps?: TrajectoryStep[] | null;
  route: string;
  reasoning: string;
}) {
  const items = steps ?? [];
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900/40">
      <div className="mb-3 flex items-center gap-3">
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Agent trajectory</h3>
        <span className="rounded-full border border-slate-300 bg-slate-100 px-2 py-0.5 text-[11px] text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
          route: {route}
        </span>
        <span className="text-[11px] text-slate-500">{items.length} tool calls</span>
      </div>
      <ol className="space-y-2">
        {items.map((s) => (
          <li key={s.step} className="flex gap-3 text-xs">
            <span className="mt-0.5 w-5 shrink-0 text-right text-slate-400 dark:text-slate-600">{s.step}</span>
            <span
              className={`h-fit shrink-0 rounded border px-2 py-0.5 font-mono ${
                TOOL_COLOR[s.tool] || TOOL_FALLBACK
              }`}
            >
              {s.tool}
            </span>
            <div className="min-w-0 flex-1">
              <div className="truncate font-mono text-slate-500">{JSON.stringify(s.args)}</div>
              <div className="truncate text-slate-600 dark:text-slate-400">{JSON.stringify(s.observation)}</div>
            </div>
          </li>
        ))}
      </ol>
      {reasoning && (
        <div className="mt-4 border-t border-slate-200 pt-3 text-xs text-slate-600 dark:border-slate-800 dark:text-slate-400">
          <span className="font-semibold text-slate-700 dark:text-slate-300">Reasoning: </span>
          {reasoning}
        </div>
      )}
    </div>
  );
}
