# Correction disposition — corrected edition 23 October 2026

This table maps the supplied 20 October review to implemented local changes.
`Implemented and tested` refers to the tests shipped here, not an external
acceptance or a public release. Upstream Vol.5.3/5.4 are not rewritten.

| Review issue | Change | Evidence / boundary |
|---|---|---|
| M61-01 gap | Singleton fibers, both adjacent relations empty | lift 0, Pt 1, first failure 1, no live-cone obstruction; exact enumeration |
| M61-01 same slices | Parallel/full edges; actual surviving projections; path-dependent all-branch-equality feature | 2 versus 8 lifts, equal slices, histogram 2/0 versus 2/6; §12.6 source mapping |
| M61-01 velocity | Integer position/velocity states, q'=q+v and v'=v, H=v0, eight observation schedules | 33/3/1 counts; stages retained; closed-form second enumeration |
| Additional source-fidelity alignment | Unique-lift and feature-ambiguity fixtures reproduce the published source sizes rather than legacy smaller analogues | Pt 8 / lift 1; Pt 27 / lift 2; explicitly changed fixture data |
| M61-02 / SW-02 | Typed section, full-path, local edge and common-action outputs | A checked at every time; D sections coexist with policy failure; E quotient section true/post-policy false |
| M61-03 | Fixed role label separated from data-derived checks | 50 predicates; action/transition mutations change computed claims without changing role metadata |
| M61-04 | Original 0–18 organization retained, status/counts centralized, tables generated from results | manuscript source build and shared synchronization contract |
| Comparator / ID deficiencies | Strict type/key equality, outer-ID and exact filename/bucket/ID-set checks | bool/int, missing/null, wrong ID, duplicate/missing spec and golden tests |
| SW-04 Toy C | Produce local table/count on success, full-path existence null; conflict gives false | positive-local mutation tested; no general success-side synthesis claimed |
| SW-05 quotient exactness | Map domains exactly equal declared members; injectivity checked on that domain | extra/missing map-entry tests in E/F |
| SW-06 unused structure | Contiguous stage/transition keys, endpoint checks, partitions are disjoint covers; all B cells computed | extra stage/transition/cell and stale A information tests |
| SW-07 thinning | Require strict observation reduction and successful recoverability on both sides | empty target produces false/false and thinning false |
| SW-08 pre-write behavior | Validate complete suite and paths before computing/output; all comparisons before writing | invalid ID/path, duplicate, malformed and mismatch gate tests write no new output |
| Golden / source correspondence | Explicit candidate freeze with separately implemented enumeration, then strict normal/-O gate | snapshots remain locally reviewed candidates; external review pending |
| M3 / CPre | Preserve not-certified boundary | no CPre or controller synthesis claim added |

Original review evidence and v0.4.2 originals remain outside this public-candidate
software archive. Personal filesystem paths and raw private review logs are not
included. Both original archive SHA-256 values are retained in the input registry.

## r1 -> r2 review findings

The historical `provenance/historical_responses/R2_REVIEW_RESPONSE.md` records the R1-R4 implementation checkpoint.
See `provenance/historical_responses/R3_REVIEW_RESPONSE.md` for the later r2 acceptance/Windows evidence and the historical r3 delta.
R1/R2 are auxiliary-checker corrections, not a claim that the primary r1 gate was bypassed.
Review finding R3 was subsequently confirmed repaired on native Windows for r2.
That supplied execution is retained as r2 evidence, not relabeled as a fresh r3 run.
R4 patches are regenerated and tested on exact old bytes; their scope is explicit.

## Publication-preparation disposition

| Finding | Current disposition |
|---|---|
| R4-01 | PDF and current READMEs separate r3/r4 preparation checkpoints, subsequent reviewer Windows execution, and the new cleaned-edition run. |
| R4-04 | Appendix C says one physical line per command. ASCII `--` typography is retained. |
| R4-02 | GitHub historical code is not current-edition evidence. Integration is NOT_EXECUTED. |
| C2 / R4-03 | Packaged integration notes use the 10/22 publication-status target and fixed commit/archive paths; remote navigation correction is NOT_EXECUTED. |
| Public filenames | Three distribution filenames and root directory names omit `_r4`; prior target identifiers remain historical. |
| Private paths | Separate sanitized review-evidence derivative; original reviews and hashes retained unchanged, new derivative hashes recorded. |

See `PUBLICATION_PREPARATION.md`. Prior r4 review is not automatically transferred
to this new set of bytes. No mathematical fixture or computation was modified.
