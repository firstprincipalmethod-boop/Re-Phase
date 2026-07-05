"""Vol.5.3 (pathwise) witness compute functions.

EMPTY ON PURPOSE (D13 sequencing): canonical specs land in specs/v53/ FIRST, then the
compute functions below are filled in — never the reverse. Each @witness registers into
the shared REGISTRY in compute.py; run_all.py imports this module for that side-effect.

Convention (D12): Pt(y) = product_k F_k(y_k) (full pointwise relaxation); Lift(y) its
transition-compatible subset. Return a flat dict of generated numbers only.

    from compute import witness

    @witness("v53_collapse")
    def _(spec):
        # read spec['spec'] inputs; enumerate Pt, Lift, feature image, target, tau_pre.
        # tau_pre(y) = online prefix-failure index (Vol.5.3 §7.2): the first prefix length k at
        #   which the online prefix lift Liftpre_{0:k}(y) is empty, equivalently R_k(y) = empty.
        #   Represent it STRUCTURALLY (no numeric sentinel):
        #       finite failure : {"status": "finite",     "k": 2}
        #       never empty    : {"status": "no_failure", "k": null}
        #   GENERATED here, never written into the spec (D13).
        #
        # feature_image_pt / feature_image_lift naming locked 2026-07-04 (convention lock):
        # H_Pt / H_Lift are deprecated (misread as entropy). See
        # Obsidian 03_Working_Memos/Vol6_1/ClaudeCode_opinion_for_ChatGPT_mainline_2026-07-04.md
        # and vscode_claude_response_vol6_1_convention_lock.md for the decision trail.
        #
        # verdict is looked up from schema.VERDICT_BY_WITNESS (locked 2026-07-04), not free text.
        # certified v53 column set (report.py PATHWISE_COLS): id, pt_size, lift_size, lift_status,
        # feature_image_pt, feature_image_lift, target, target_check, tau_pre_status, tau_pre_k,
        # recoverable, verdict. (target_check replaces boolean target_included -- v0.1 feedback
        # 2026-07-05: an empty Lift made "subset of target" vacuously true, which read as a false
        # positive next to recoverable=false. See schema.ALLOWED_TARGET_CHECK.)
        return {"pt_size": ..., "lift_size": ..., "lift_status": ...,
                "feature_image_pt": [...], "feature_image_lift": [...],
                "target": [...], "target_check": ...,
                "tau_pre": {"status": ..., "k": ...},
                "recoverable": ..., "verdict": ...}
"""
from compute import witness  # noqa: F401  (imported for @witness availability)

# --- Vol.5.3 witnesses register below (none yet; canonical specs land first, D13) ---
