# ADR-002: Agent orchestration framework

Status: accepted
Date: 2026-06-23
Decision ref: §10 Decision C / plan ADR 4.1

## Context
The v2 heart is an LLM controller that plans and executes retrieval over the Phase-3 tools (ReAct:
Thought → Action → Observation). The framework choice shapes all of Phase 4 and how defensible the
"I built the agent" claim is in interviews.

## Options considered
- **Hand-rolled Anthropic SDK tool-loop** — raw tool-use loop we own line by line. Pro: maximum
  understanding and control; you can explain the agent end-to-end; no framework lock-in; cleanest
  learning + interview defense. Con: more plumbing (loop governance, trajectory logging, retries
  written by hand).
- **LangGraph** — explicit, inspectable state machine. Pro: great for visualising the trajectory and
  enforcing gates; structured. Con: framework lock-in; abstracts away the loop mechanics you most
  want to learn; the "I built it" signal is weaker.
- **LlamaIndex agents** — fastest RAG primitives. Pro: quickest to a working agent. Con: most
  magic/abstraction; hides exactly the mechanics this project exists to teach.

## Decision
**Hand-rolled Anthropic SDK tool-loop** for v1.

## Why the others were rejected
This is a learning project whose defensibility comes from being able to explain every line of the
control loop — bounded agency, corrective-retrieval triggers, the grounding gate. A framework that
owns the loop (LangGraph) or hides it (LlamaIndex) trades away the single most valuable thing here.
LangGraph is noted as the **natural refactor** once the hand-rolled loop is understood and we want
a nicer trajectory visualiser.

## Consequences / what we'll measure
- We own: tool schemas, system prompt, loop governance (max steps, max re-retrievals), and the
  trajectory log written on every tool call.
- Phase 4 metric gate: trajectory correctness on the golden set (right tools, right order,
  correction fires when it should) **and** end-answer recall ≥ target (§7).
- Bounded agency (ADR TBD Phase 4): cap steps/re-retrievals so the agent can't loop or over-spend.
