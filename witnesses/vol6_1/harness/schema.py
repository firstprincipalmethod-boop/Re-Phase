"""Vol.6.1 witness schemas + minimal stdlib validator (no external deps).
Enforces D13: a SPEC carries inputs only and MUST NOT contain expected numbers.
Expected numbers live only in GENERATED output / GOLDEN snapshots."""

# Keys that, if present in a spec, indicate handwritten expected output (forbidden by D13).
# feature_image_pt/feature_image_lift are the locked 2026-07-04 names (h_pt/h_lift deprecated,
# kept here too so old-style handwritten specs are still caught).
FORBIDDEN_IN_SPEC = {
    "expected", "output", "computed", "results",
    "pt_size", "lift_size", "h_pt", "h_lift",
    "feature_image_pt", "feature_image_lift",
    "lift_status", "target_check", "tau_pre", "verdict",
    "recoverable", "selector_verdict", "verdicts",
}

REQUIRED_SPEC_KEYS = ["id", "source_volume", "kind", "role", "status", "count_objects", "spec"]
ALLOWED_KINDS = {"pathwise", "selector"}
ALLOWED_STATUS = {"core", "core with caveat", "optional", "to-verify"}

# --- Convention lock 2026-07-04 (feature_image naming + verdict vocabulary) ---
# See Obsidian 03_Working_Memos/Vol6_1/ClaudeCode_opinion_for_ChatGPT_mainline_2026-07-04.md
# and vscode_claude_response_vol6_1_convention_lock.md for the decision trail.
#
# lift_status describes the state of Lift(y) itself; verdict describes which Re-Phase
# distinction the witness demonstrates. The two are deliberately kept separate (A4).
ALLOWED_LIFT_STATUS = {"infeasible", "unique", "ambiguous"}

# target_check (v0.1 feedback, replaces boolean target_included): an empty Lift makes
# "is feature_image_lift subset of target" vacuously true, which reads as a false positive
# next to recoverable=false. vacuous_empty_lift names that case explicitly instead of
# collapsing it into the same value as a genuine within_target result.
ALLOWED_TARGET_CHECK = {"vacuous_empty_lift", "within_target", "outside_target"}

# id -> locked verdict string. v53 entries are certified; v54 entries are locked vocabulary
# but golden is still on hold pending M1-M3 upstream selector issues (Vol.5.4 content summary §8).
VERDICT_BY_WITNESS = {
    # v53 (Vol.5.3 pathwise)
    "v53_collapse": "collapse",
    "v53_gap_collapse": "gap_collapse",
    "v53_unique_lift": "unique_lift",
    "v53_feature_ambiguous_recoverable": "feature_sufficient_ambiguity",
    "v53_missing_cell": "feature_effective_unresolved",
    "v53_same_slices_different_edges": "same_slices_different_edges",
    "v53_constant_velocity": "observation_thinning",
    # v54 (Vol.5.4 selector) -- vocabulary locked, golden on hold
    "v54_toy_A_memoryless_fail": "memoryless_selector_failure",
    "v54_toy_B_bridge_conflict": "bridge_cell_conflict",
    "v54_toy_C_nonblocking": "nonblocking_failure",
    "v54_toy_D_traceable_silent": "retention_memory_separation",
    "v54_toy_E_target_sound_not_selector": "target_sound_not_selector_preserving",
    "v54_toy_F_safe_nonexact": "safe_nonexact_forgetting",
}

# D15: Vol.6.1 certifies exactly two witness groups. source_volume picks the certification
# bucket (specs/<b>, generated/<b>, golden/<b>). The volume<->kind coupling is definitional
# here (D12): Vol.5.3 = pathwise, Vol.5.4 = selector. A mismatch means a misfiled witness.
ALLOWED_SOURCE_VOLUME = {"Vol.5.3", "Vol.5.4"}
VOLUME_BUCKET = {"Vol.5.3": "v53", "Vol.5.4": "v54"}
VOLUME_KIND   = {"Vol.5.3": "pathwise", "Vol.5.4": "selector"}

def bucket(spec):
    """Certification bucket ('v53'/'v54') for a spec, from source_volume (D15).
    Expects a spec that passed validate_spec; raises so a misroute is loud, never silent."""
    sv = spec.get("source_volume")
    if sv not in VOLUME_BUCKET:
        raise ValueError(f"cannot bucket {spec.get('id')!r}: source_volume={sv!r} "
                         f"not in {sorted(VOLUME_BUCKET)}")
    return VOLUME_BUCKET[sv]

def validate_spec(obj, where="<spec>"):
    """Return (ok, errors). Structural + D13 check only; does NOT inspect spec contents' correctness."""
    errs = []
    if not isinstance(obj, dict):
        return False, [f"{where}: spec must be a JSON object"]
    for k in REQUIRED_SPEC_KEYS:
        if k not in obj:
            errs.append(f"{where}: missing required key '{k}'")
    if obj.get("kind") not in ALLOWED_KINDS:
        errs.append(f"{where}: kind must be one of {sorted(ALLOWED_KINDS)} (got {obj.get('kind')!r})")
    if obj.get("status") not in ALLOWED_STATUS:
        errs.append(f"{where}: status must be one of {sorted(ALLOWED_STATUS)}")
    # D15: source_volume must be a certified bucket, and match its kind (misfile guard)
    sv = obj.get("source_volume")
    if sv not in ALLOWED_SOURCE_VOLUME:
        errs.append(f"{where}: source_volume must be one of {sorted(ALLOWED_SOURCE_VOLUME)} (got {sv!r})")
    elif VOLUME_KIND[sv] != obj.get("kind"):
        errs.append(f"{where}: source_volume {sv} requires kind '{VOLUME_KIND[sv]}' "
                    f"(got {obj.get('kind')!r}) — misfiled witness? (D15)")
    # D13: no expected numbers anywhere in the spec
    def scan(node, path):
        if isinstance(node, dict):
            for key, val in node.items():
                if key.lower() in FORBIDDEN_IN_SPEC:
                    errs.append(f"{where}: forbidden key '{path}{key}' — expected outputs must NOT be in a spec (D13)")
                scan(val, f"{path}{key}.")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                scan(v, f"{path}{i}.")
    scan(obj, "")
    # count_objects must declare what is counted
    co = obj.get("count_objects")
    if not isinstance(co, dict) or not co:
        errs.append(f"{where}: count_objects must be a non-empty object declaring counted objects (D12)")
    return (len(errs) == 0), errs

REQUIRED_OUTPUT_KEYS = ["id", "generated_by", "computed", "verification"]

# verification statuses run_all.py may write into a generated output record.
# Must stay in sync with run_all.py (pass/fail/pending plus the non-verifiable states).
ALLOWED_VERIFICATION_STATUS = {
    "pass", "fail", "pending",
    "no-golden", "no-compute-registered", "error",
}

# compute_status values written by compute()/run_all (provenance, not a verdict)
ALLOWED_COMPUTE_STATUS = {"ok", "no-compute-registered", "error"}

def validate_output(obj, where="<output>"):
    errs = []
    if not isinstance(obj, dict):
        return False, [f"{where}: output must be a JSON object"]
    for k in REQUIRED_OUTPUT_KEYS:
        if k not in obj:
            errs.append(f"{where}: missing required key '{k}'")
    if "compute_status" in obj and obj["compute_status"] not in ALLOWED_COMPUTE_STATUS:
        errs.append(f"{where}: compute_status must be one of {sorted(ALLOWED_COMPUTE_STATUS)}")
    v = obj.get("verification", {})
    if isinstance(v, dict):
        st = v.get("status")
        if st not in ALLOWED_VERIFICATION_STATUS and st is not None:
            errs.append(f"{where}: verification.status must be one of {sorted(ALLOWED_VERIFICATION_STATUS)}")
    # convention lock 2026-07-04: lift_status vocabulary + locked id->verdict mapping
    computed = obj.get("computed", {})
    if isinstance(computed, dict):
        ls = computed.get("lift_status")
        if ls is not None and ls not in ALLOWED_LIFT_STATUS:
            errs.append(f"{where}: computed.lift_status must be one of {sorted(ALLOWED_LIFT_STATUS)} (got {ls!r})")
        tc = computed.get("target_check")
        if tc is not None and tc not in ALLOWED_TARGET_CHECK:
            errs.append(f"{where}: computed.target_check must be one of {sorted(ALLOWED_TARGET_CHECK)} (got {tc!r})")
        wid = obj.get("id")
        expected_verdict = VERDICT_BY_WITNESS.get(wid)
        verdict = computed.get("verdict")
        if expected_verdict is not None and verdict is not None and verdict != expected_verdict:
            errs.append(f"{where}: computed.verdict for {wid!r} must be {expected_verdict!r} (got {verdict!r})")
    return (len(errs) == 0), errs
