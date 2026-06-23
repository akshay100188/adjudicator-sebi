# ADR-005: Code-analysis module is out of v1

Status: accepted
Date: 2026-06-23
Decision ref: §10 Decision E / plan Phase 8

## Context
A code-analysis module (map a GitHub repo's code to SEBI obligations via Semgrep + AST + agent) is
the rarest differentiator to show — and the deepest hole to fall into. It risks eating the RAG/agent
learning that is the actual point of the project.

## Options considered
- **Out of v1; Phase 8 stretch only** — Pro: protects the core learning budget (agent + eval);
  delivers a measurable engine first. Con: the flashiest feature lands last (or not at all).
- **In v1 core** — Pro: differentiator early. Con: large surface (Semgrep rule authoring, AST,
  tree-sitter) that competes for time with the agent + eval harness, which are non-negotiable.

## Decision
**Out of v1.** Revisit as a Phase 8 stretch only after the agent + eval harness are solid.

## Why the other was rejected
The project's defensible signal is the agent and how it's *evaluated* (§7), not a code scanner. The
plan is explicit: code-analysis "must not eat the core learning." It is sequenced dead last.

## Consequences / what we'll measure
- If built (Phase 8): privacy-by-design — shallow clone → scan → delete; persist only finding
  metadata (file path, line, obligation code), never the code. Reuses the §3 PII posture.
