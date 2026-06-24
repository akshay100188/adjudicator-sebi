# ADR-012: RRF fusion constant k = 60

Status: accepted
Date: 2026-06-24
Plan ref: ADR 3.1 · Evidence: EXP-002

## Context
Reciprocal Rank Fusion scores documents by Σ 1/(k + rank). The constant k controls how sharply top
ranks dominate.

## Options considered
- k ∈ {10, 30, 60, 100}, measured in EXP-002.

## Decision
**k = 60** (the literature-standard default).

## Why
EXP-002 was completely flat across all four values — with two ranked lists over a small pool, k does
not change the relative order enough to move any document across the @1/3/5 boundaries. With no
empirical reason to deviate, we keep the well-understood default.

## Consequences / what we'll measure
Revisit only if a larger corpus shows k-sensitivity. Logged as a no-op tuning result.
