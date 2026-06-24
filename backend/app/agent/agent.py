"""Hand-rolled ReAct agent (ADR-002) — the v2 heart.

The controller (Sonnet) decides, per step, which Phase-3 tool to call: routes simple vs multi-hop,
decomposes, traces supersession, corrects on weak retrieval, and self-checks grounding before
answering. We own the loop: bounded agency + a trajectory log on every tool call + a grounding gate.

Not legal advice. Output is for expert review only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date

import anthropic

from ..config import settings
from .tools_schema import TOOL_SCHEMAS, dispatch

MODEL = "claude-sonnet-4-6"
MAX_STEPS = 8  # bounded agency (ADR 4.2) — caps tool-call rounds

DISCLAIMER = ("This output does not constitute legal advice or a compliance determination. "
              "All findings require review by a qualified compliance professional. "
              "Always verify against the cited source circular.")

SYSTEM = f"""You are a retrieval agent for SEBI stock-broker (Trading Member) compliance. Today is \
{{today}}. Given a question or a product-change scenario, gather the set of CURRENTLY-VALID SEBI \
obligations that apply, using the tools — then stop and report.

Your job is retrieval + applicability, NOT writing the final compliance findings (that is a later step).

How to work (ReAct):
1. ROUTE first. Decide: is this a simple obligation lookup, or a multi-hop question (supersession,
   'what changed', 'consolidated position as of today')? State your route in your reasoning.
2. RETRIEVE with hybrid_search. If the user used lay phrasing, also reformulate into canonical SEBI
   terminology (e.g. "client money" -> "running account settlement of client funds" / "upstreaming of
   client funds") and search again. If the top results look weak or off-topic, CORRECT: reformulate and
   re-retrieve (do not just accept the first hit).
3. For multi-hop: expand_to_parent to get an obligation's source circular reference, then graph_lookup
   on that reference to trace amends/supersedes/consolidated_by, and use temporal_filter to confirm
   what is valid as of today.
4. rerank your candidate set for precision before finalising.
5. GROUNDING SELF-CHECK before answering: every obligation_id you report MUST have been returned by a
   tool in this session. Do not invent obligation IDs.

Budget: at most {MAX_STEPS} tool-call rounds. Be efficient — simple questions need 1-2 tools.

When done, STOP calling tools and output ONLY a JSON object (no prose around it):
{{{{"route": "simple|multi-hop", "relevant_obligations": ["SB-..."],
  "reasoning": "<1-3 sentences on why these apply / what the supersession trace showed>",
  "correction_fired": true|false}}}}"""


@dataclass
class Step:
    thought: str
    tool: str
    args: dict
    observation: dict


@dataclass
class AgentResult:
    query: str
    route: str
    relevant_obligations: list[str]
    reasoning: str
    correction_fired: bool
    trajectory: list[Step] = field(default_factory=list)
    grounding_dropped: list[str] = field(default_factory=list)
    steps_used: int = 0
    disclaimer: str = DISCLAIMER

    def tool_sequence(self) -> list[str]:
        return [s.tool for s in self.trajectory]


def _summarize(obs: dict) -> dict:
    """Trim observations for the trajectory log."""
    s = dict(obs)
    if "valid_obligation_ids" in s:
        s["valid_obligation_ids"] = f"[{s['valid_count']} ids]"
    return s


def run_agent(query: str, as_of: date | None = None, verbose: bool = False) -> AgentResult:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    system = SYSTEM.format(today=(as_of or date.today()).isoformat())
    messages: list[dict] = [{"role": "user", "content": query}]
    trajectory: list[Step] = []
    surfaced: set[str] = set()  # obligation ids returned by any tool (grounding universe)

    for step in range(MAX_STEPS):
        resp = client.messages.create(
            model=MODEL, max_tokens=1500, system=system, tools=TOOL_SCHEMAS, messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})

        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        thought = " ".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()

        if not tool_uses:  # agent finished — parse final JSON
            final = _parse_final(thought)
            relevant = final.get("relevant_obligations", [])
            grounded = [o for o in relevant if o in surfaced]
            dropped = [o for o in relevant if o not in surfaced]  # grounding gate
            if verbose:
                print(f"[final] route={final.get('route')} obligations={grounded} dropped={dropped}")
            return AgentResult(
                query=query, route=final.get("route", "unknown"), relevant_obligations=grounded,
                reasoning=final.get("reasoning", ""), correction_fired=bool(final.get("correction_fired")),
                trajectory=trajectory, grounding_dropped=dropped, steps_used=step,
            )

        tool_results = []
        for tu in tool_uses:
            obs, ids = dispatch(tu.name, tu.input or {})
            surfaced.update(ids)
            trajectory.append(Step(thought=thought, tool=tu.name, args=tu.input or {}, observation=_summarize(obs)))
            if verbose:
                print(f"[step {step}] {tu.name}({json.dumps(tu.input)[:80]}) -> {str(_summarize(obs))[:120]}")
            tool_results.append({"type": "tool_result", "tool_use_id": tu.id,
                                 "content": json.dumps(obs)[:6000]})
        messages.append({"role": "user", "content": tool_results})

    # ran out of budget
    return AgentResult(query=query, route="unknown", relevant_obligations=[], reasoning="step budget exhausted",
                       correction_fired=False, trajectory=trajectory, steps_used=MAX_STEPS)


def _parse_final(text: str) -> dict:
    t = text.strip()
    if "```" in t:
        t = t.split("```")[1].lstrip("json").strip()
    start, end = t.find("{"), t.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(t[start:end + 1])
        except json.JSONDecodeError:
            pass
    return {"route": "unknown", "relevant_obligations": [], "reasoning": t[:200], "correction_fired": False}
