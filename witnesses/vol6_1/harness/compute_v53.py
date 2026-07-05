"""Vol.5.3 (pathwise) witness compute functions.

Canonical specs land in specs/v53/ FIRST, then the compute function for that witness is
filled in — never the reverse (D13 sequencing). Each @witness registers into the shared
REGISTRY in compute.py; run_all.py imports this module for that side-effect.

Convention (D12): Pt(y) = product_k F_k(y_k) (full pointwise relaxation); Lift(y) its
transition-compatible subset. Return a flat dict of generated numbers only.

tau_pre(y) = online prefix-failure index (Vol.5.3 §7.2): the first prefix length k at which
the online prefix lift Liftpre_{0:k}(y) is empty, equivalently R_k(y) = empty. Represented
STRUCTURALLY (no numeric sentinel): finite failure -> {"status": "finite", "k": 2}; never
empty -> {"status": "no_failure", "k": None}. GENERATED here, never written into the spec.

feature_image_pt / feature_image_lift naming locked 2026-07-04 (convention lock): H_Pt /
H_Lift are deprecated (misread as entropy). verdict is looked up from
schema.VERDICT_BY_WITNESS (locked 2026-07-04), not free text.

certified v53 column set (report.py PATHWISE_COLS): id, pt_size, lift_size, lift_status,
feature_image_pt, feature_image_lift, target, target_check, tau_pre_status, tau_pre_k,
recoverable, verdict. (target_check replaces boolean target_included -- v0.1 feedback
2026-07-05: an empty Lift made "subset of target" vacuously true, which read as a false
positive next to recoverable=false. See schema.ALLOWED_TARGET_CHECK.)

Only v53_collapse is registered here so far. The remaining v53 witnesses
(v53_gap_collapse, v53_unique_lift, v53_feature_ambiguous_recoverable, v53_missing_cell,
v53_same_slices_different_edges, v53_constant_velocity) land in a follow-up PR.
"""
import itertools
from compute import witness
from schema import VERDICT_BY_WITNESS


def _stage_keys(d):
    """Sort 'X0','X1',...,'X10' by numeric suffix, not lexically."""
    return sorted(d.keys(), key=lambda k: int(k[1:]))


def _feature_of(path, feature):
    if feature == "terminal_state":
        return path[-1]
    raise ValueError(f"unknown feature kind {feature!r}")


def _compute_variant(state_sets, transitions, feature, target):
    """Core Pt/Lift/tau_pre/feature-image computation for one (state_sets, transitions)
    variant. Returns everything EXCEPT 'verdict' -- verdict is witness-specific (looked up
    from schema.VERDICT_BY_WITNESS by the caller), not a property of the variant itself.
    state_sets: {Xk: [...]}. transitions: {Tk: [[a,b],...]}."""
    stage_keys = _stage_keys(state_sets)
    F = [set(state_sets[k]) for k in stage_keys]
    trans_keys = _stage_keys(transitions)
    T = [set(tuple(e) for e in transitions[k]) for k in trans_keys]
    n = len(F) - 1
    target_set = set(target)

    Pt = list(itertools.product(*F))

    paths = [(x,) for x in F[0]]
    for k in range(n):
        paths = [path + (b,) for path in paths for b in F[k + 1] if (path[-1], b) in T[k]]
    Lift = paths

    # forward reachable-compatible sets R_k (Vol.5.1 §2.2 / Vol.5.3 §4.6): tau_pre is the
    # first k at which R_k is empty, i.e. the online prefix lift first collapses.
    R = [set(F[0])]
    for k in range(n):
        R.append(F[k + 1] & {b for (a, b) in T[k] if a in R[k]})
    tau_pre_k = next((k for k, Rk in enumerate(R) if not Rk), None)
    tau_pre = {"status": "finite", "k": tau_pre_k} if tau_pre_k is not None else {"status": "no_failure", "k": None}

    feature_image_pt = sorted({_feature_of(p, feature) for p in Pt})
    feature_image_lift = sorted({_feature_of(p, feature) for p in Lift})
    lift_status = "infeasible" if not Lift else ("unique" if len(Lift) == 1 else "ambiguous")
    if not Lift:
        target_check = "vacuous_empty_lift"
    elif set(feature_image_lift) <= target_set:
        target_check = "within_target"
    else:
        target_check = "outside_target"
    recoverable = bool(Lift) and target_check == "within_target"

    return {
        "pt_size": len(Pt),
        "lift_size": len(Lift),
        "lift_status": lift_status,
        "feature_image_pt": feature_image_pt,
        "feature_image_lift": feature_image_lift,
        "target": sorted(target_set),
        "target_check": target_check,
        "tau_pre": tau_pre,
        "recoverable": recoverable,
    }


def _pathwise_witness(spec):
    """Single-variant Vol.5.3 pathwise witnesses (D12): spec['spec'] = {state_sets, transitions,
    feature, target}."""
    s = spec["spec"]
    result = _compute_variant(s["state_sets"], s["transitions"],
                               s.get("feature", "terminal_state"), s.get("target", []))
    result["verdict"] = VERDICT_BY_WITNESS[spec["id"]]
    return result


# --- Vol.5.3 witnesses ---

@witness("v53_collapse")
def _(spec):
    return _pathwise_witness(spec)
