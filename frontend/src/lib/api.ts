const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

export interface Obligation {
  obligation_id: string;
  title: string;
  category: string | null;
  intermediary_type: string | null;
  source_circular_ref: string;
  clause_refs: string[] | null;
  chapter: string | null;
  valid_today: boolean;
}

export interface CitationEdge {
  from_ref: string;
  to_ref: string;
  relation_type: string;
  depth: number;
}

export interface RelatedObligation {
  obligation_id: string;
  title: string;
  direction: "refers_to" | "referenced_by";
  source_note: string | null;
}

export interface ObligationDetail extends Obligation {
  obligation_text: string;
  expected_controls: string[] | null;
  parent_text: string | null;
  citation_graph: CitationEdge[];
  related_obligations: RelatedObligation[];
}

export interface Finding {
  obligation_id: string;
  gap_summary: string;
  evidence: string;
  recommended_action: string;
  confidence: string;
  citation: string;
}

export interface TrajectoryStep {
  step: number;
  tool: string;
  args: Record<string, unknown>;
  observation: Record<string, unknown>;
}

export interface AnalyzeResult {
  route: string;
  reasoning: string;
  obligations_considered: { obligation_id: string; title: string }[];
  findings: Finding[];
  trajectory: TrajectoryStep[];
  trajectory_tools: string[];
  grounding_dropped: string[];
  steps_used: number;
  disclaimer: string;
}

export async function getObligations(): Promise<Obligation[]> {
  const r = await fetch(`${API}/obligations`, { cache: "no-store" });
  if (!r.ok) throw new Error("failed to load obligations");
  return r.json();
}

export async function getObligation(id: string): Promise<ObligationDetail> {
  const r = await fetch(`${API}/obligations/${id}`, { cache: "no-store" });
  if (!r.ok) throw new Error("failed to load obligation");
  return r.json();
}

export interface CodeSignal {
  file: string;
  line: number;
  category: string;
  description: string;
}

export interface CodeResult extends AnalyzeResult {
  files_scanned: number;
  languages: string[];
  signals: CodeSignal[];
  derived_description: string;
}

export async function codeAnalyse(repo_path: string): Promise<CodeResult> {
  const r = await fetch(`${API}/code-analysis/analyse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_path }),
  });
  if (!r.ok) throw new Error("code analysis failed");
  return r.json();
}

export async function analyze(scenario: string): Promise<AnalyzeResult> {
  const r = await fetch(`${API}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario }),
  });
  if (!r.ok) throw new Error("analysis failed");
  return r.json();
}
