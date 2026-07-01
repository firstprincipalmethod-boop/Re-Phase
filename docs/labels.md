# Labels Specification

This document defines the label taxonomy for Re-Phase GitHub Issues.

## Label Categories

### Type Labels (Issue Content Type)

| Label | Description | Use Case |
|-------|-------------|----------|
| `type:definition` | New definition or definition modification | Propose or modify core concepts |
| `type:notation` | Notation introduction or standardization | Propose notation changes, flag collisions |
| `type:example` | Concrete example or toy model | Illustrate concepts with examples |
| `type:proof` | Theorem, lemma, or claim verification | Propose or verify proofs |
| `type:structure` | Volume structure, architecture, or integration | Cross-volume alignment and design |
| `type:release` | Pre-publication checklist and release logistics | Publication workflow and archival |

### Risk Labels (Potential Issues)

| Label | Description | Use Case |
|-------|-------------|----------|
| `risk:concept-drift` | Concept definition diverges from prior volumes | Flag where older vs. newer terminology conflict |
| `risk:notational-conflict` | Symbol or notation collides with prior usage | Flag notation ambiguity or collision |

### Volume Labels

| Label | Description | Scope |
|-------|-------------|-------|
| `vol:1` | Vol.1 Foundations | Foundational definitions and order-theoretic arena |
| `vol:2` | Vol.2 Hidden State | Fiber structures and partial observation |
| `vol:3` | Vol.3 Dual Inner Product | Pathwise compatibility and duality |
| `vol:4` | Vol.4 Posterior Compatibility | Bayesian update and temporal dynamics |
| `vol:5` | Vol.5 Continuation | Fiberwise liftability and selector existence |
| `vol:6` | Vol.6 Recoverability | Bridge obstruction and recoverability guards |
| `vol:6.1` | Vol.6.1 (Current) | Windowed path fibers and minimal sufficient context |

### State Labels (Development Status)

| Label | Description | Meaning |
|-------|-------------|----------|
| `state:draft` | Draft or proposal stage | Idea being formulated, not finalized |
| `state:ready` | Ready for integration | Proposal vetted and ready to merge into main text |
| `state:published` | Published in Zenodo or arXiv | Finalized and archived |

## Label Assignment Rules

- **Every issue should have at least one `type:*` label** to categorize its content.
- **Cross-volume issues should have multiple `vol:*` labels** for all affected volumes.
- **Risk labels are optional** but should be applied when conflicts or drifts are suspected.
- **State labels track workflow**: `draft` → `ready` → `published`.

## Total: 18 Labels

- Type: 6 labels
- Risk: 2 labels
- Volume: 7 labels
- State: 3 labels
