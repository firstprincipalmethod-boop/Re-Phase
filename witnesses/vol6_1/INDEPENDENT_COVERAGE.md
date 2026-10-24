# Independent checker coverage — retained corrected implementation

`derive_expected_record(spec)` constructs every expected result field from a
validated input before `compare_complete` sees the actual record. No actual
result field chooses a class or narrows the expected field set.

| Class | Implementation boundary |
|---|---|
| INDEPENDENT_DERIVATION | Numerical/set-valued evidence, all variants/policies, selected paths/tables, counts, feature images, dynamic policy preservation and claim predicates, re-enumerated from input |
| CONTRACT_VALIDATION | Full key sets/JSON types, registered ID/role/source/version/digest, obligation strings, fixed no-certification/no-control assertions and generated-wrapper labels |
| INDEPENDENT_DERIVATION_WITH_CONTRACT_BOUNDARY | Toy C's status is derived from its prefix conflict; local success is restricted to `not_checked`, not global success |
| PRIMARY_GOLDEN_REGRESSION_AND_REGENERATION | Strict primary snapshots and regenerated JSON/CSV/run-summary byte consistency; no claim that auxiliary inspection replays the primary golden gate |

`verification/independent_coverage.json` lists all paths of each expected record,
including containers and null/empty values. Classification is derived from the
expected record, not the inspected output. Containers are structurally validated;
their dynamic leaves are separately derived. No computed field is omitted merely
because it is a string. Unrecognized/missing/extra fields fail strict comparison.

The generated `verification` wrapper is checked against its declared labels.
A label such as `strict_golden: pass` is NOT independent proof that a past run
occurred. `run_all.py --release` separately replays the primary gate.

The same-session implementation is not an independent reviewer. The supplied
Historical r1-r4 reviews and a review of these new edition bytes are separate evidence.
