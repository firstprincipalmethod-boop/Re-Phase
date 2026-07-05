"""Compute layer — the ONLY place where a spec's inputs are turned into outputs.
EMPTY ON PURPOSE: no witness compute function is registered yet. Canonical specs are
fixed from the source volumes first (D13 sequencing); compute functions are added then,
so source-reading mistakes are never frozen into code ahead of the specs.

To add a witness later:

    from compute import witness

    @witness("v53_missing_cell")
    def _(spec):
        # read spec['spec'] inputs; enumerate Pt, Lift, feature image, target; return a flat dict.
        return {"pt_size": ..., "lift_size": ..., "feature_image_pt": [...], "feature_image_lift": [...],
                "recoverable": ...}
"""
REGISTRY = {}

def witness(witness_id):
    def deco(fn):
        REGISTRY[witness_id] = fn
        return fn
    return deco

def compute(spec):
    """Return (computed_dict, status). status in {'ok','no-compute-registered','error'}."""
    fn = REGISTRY.get(spec.get("id"))
    if fn is None:
        return {}, "no-compute-registered"
    try:
        return fn(spec), "ok"
    except Exception as e:
        return {"error": repr(e)}, "error"
