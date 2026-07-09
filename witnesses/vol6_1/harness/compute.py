"""Compute layer — the ONLY place where a spec's inputs are turned into outputs.
This module holds only the registry; the witness compute functions live in
compute_v53.py and compute_v54.py and register themselves here on import (D15).
Historical note (D13 sequencing): canonical specs were fixed from the source volumes
first, and compute functions were added after, so source-reading mistakes were never
frozen into code ahead of the specs. As of v0.4.2 all 13 witnesses are registered.

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
