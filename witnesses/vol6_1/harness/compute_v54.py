"""Vol.5.4 (selector) witness compute functions.

EMPTY ON PURPOSE (D13 sequencing): canonical specs land in specs/v54/ FIRST, then the
compute functions below are filled in. Each @witness registers into the shared REGISTRY
in compute.py; run_all.py imports this module for that side-effect.

Convention (D12): family-level. Counted objects are Y_adm, lift fibers, information cells,
projected choice sets V_k(y), and per-class selector verdicts — do NOT force |Pt|/|Lift|.

CERTIFICATION HOLD (D15): golden freeze for Vol.5.4 witnesses is HELD until the open
must-fix items are resolved:
  - M1: retained-coordinate selectors do not fit the q_k^C : Y_adm -> I_k^C factorization
        (blocks the retention-vs-memory witness, Toy D).
  - M2: selector inconsistency must be existential, not tied to one specific offline selector.
  - M3: CPre inclusion direction depends on an unspecified must/may abstraction.
Additional caveats to carry on the sheets (not blockers, but flagged):
  - Toy C: pure "non-blocking-only" reading of the local-choice / no-continuation gap.
  - Toy E: CPre direction misread in the target-sound-but-not-selector-preserving case.

    from compute import witness

    @witness("v54_toy_A_memoryless_fail")
    def _(spec):
        # enumerate Y_adm, lift fibers, information cells, projected choice sets;
        # decide per-class selector existence (memoryless / lookback_1 / causal / offline /
        # quotient). Return a flat dict; GENERATED here, never in the spec.
        return {"offline": ..., "causal": ..., "lookback_1": ..., "memoryless": ...,
                "quotient_selector": ..., "verdict": ...}
"""
from compute import witness  # noqa: F401  (imported for @witness availability)

# --- Vol.5.4 witnesses register below (none yet; golden held per D15 until M1-M3 close) ---
