"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getObligations,
  getObligation,
  type Obligation,
  type ObligationDetail,
} from "@/lib/api";

export default function ObligationsPage() {
  const [items, setItems] = useState<Obligation[]>([]);
  const [chapter, setChapter] = useState("all");
  const [openId, setOpenId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ObligationDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getObligations().then(setItems).catch((e) => setError(String(e)));
  }, []);

  const chapters = useMemo(
    () => ["all", ...Array.from(new Set(items.map((o) => o.chapter).filter(Boolean) as string[]))],
    [items]
  );
  const shown = items.filter((o) => chapter === "all" || o.chapter === chapter);

  async function toggle(id: string) {
    if (openId === id) {
      setOpenId(null);
      setDetail(null);
      return;
    }
    setOpenId(id);
    setDetail(null);
    setDetail(await getObligation(id));
  }

  if (error) return <p className="text-sm text-rose-600 dark:text-rose-400">Error: {error}</p>;

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Obligation browser</h1>
      <p className="mt-1 text-sm text-slate-500">
        {items.length} SEBI stock-broker obligations · click one to see its text, expected controls,
        and citation graph.
      </p>

      <select
        value={chapter}
        onChange={(e) => setChapter(e.target.value)}
        className="mt-4 rounded border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 dark:border-slate-800 dark:bg-slate-900/60 dark:text-slate-300"
      >
        {chapters.map((c) => (
          <option key={c} value={c}>
            {c === "all" ? "All chapters" : c}
          </option>
        ))}
      </select>

      <ul className="mt-4 space-y-2">
        {shown.map((o) => (
          <li key={o.obligation_id} className="rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900/40">
            <button onClick={() => toggle(o.obligation_id)} className="flex w-full items-center gap-3 p-3 text-left">
              <span className="font-mono text-xs text-slate-500">{o.obligation_id}</span>
              <span className="flex-1 text-sm text-slate-800 dark:text-slate-200">{o.title}</span>
              {o.valid_today && (
                <span className="rounded-full border border-emerald-300 bg-emerald-50 px-2 py-0.5 text-[10px] text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
                  valid today
                </span>
              )}
            </button>
            {openId === o.obligation_id && (
              <div className="border-t border-slate-200 p-4 text-xs dark:border-slate-800">
                {!detail ? (
                  <p className="text-slate-500">loading…</p>
                ) : (
                  <div className="space-y-3">
                    <p className="text-slate-700 dark:text-slate-300">{detail.obligation_text}</p>
                    {detail.expected_controls && detail.expected_controls.length > 0 && (
                      <div>
                        <div className="text-slate-500">Expected controls</div>
                        <ul className="ml-4 list-disc text-slate-700 dark:text-slate-300">
                          {detail.expected_controls.map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div>
                      <div className="text-slate-500">
                        Source: <span className="font-mono text-emerald-600 dark:text-emerald-400">{detail.source_circular_ref}</span> ·
                        clauses {(detail.clause_refs || []).join(", ")}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-500">Citation graph (supersession / consolidation)</div>
                      <ul className="ml-4 mt-1 space-y-0.5 font-mono text-slate-600 dark:text-slate-400">
                        {detail.citation_graph.map((e, i) => (
                          <li key={i}>
                            {e.relation_type} → {e.to_ref} <span className="text-slate-400 dark:text-slate-600">(depth {e.depth})</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    {detail.related_obligations.length > 0 && (
                      <div>
                        <div className="text-slate-500">Related obligations (cross-references)</div>
                        <ul className="ml-4 mt-1 space-y-0.5 text-slate-600 dark:text-slate-400">
                          {detail.related_obligations.map((r, i) => (
                            <li key={i}>
                              <span className="text-slate-400 dark:text-slate-600">{r.direction}</span>{" "}
                              <span className="font-mono text-sky-600 dark:text-sky-400">{r.obligation_id}</span> — {r.title}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
