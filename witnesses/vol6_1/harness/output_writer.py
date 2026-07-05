"""Write generated output JSON (computed numbers + provenance). Never edited by hand.
The verification status is passed in AFTER golden comparison, so the file on disk
always reflects the final verdict (not a stale 'pending')."""
import json, os

def write_output(spec, computed, compute_status, out_dir, verification_status="pending"):
    os.makedirs(out_dir, exist_ok=True)
    rec = {
        "id": spec.get("id"),
        "source_volume": spec.get("source_volume"),
        "kind": spec.get("kind"),
        "generated_by": "witnesses/vol6_1/harness/compute.py",
        "compute_status": compute_status,
        "computed": computed,
        "verification": {"checked_by": "run_all.py", "status": verification_status},
    }
    path = os.path.join(out_dir, f"{spec.get('id')}.out.json")
    json.dump(rec, open(path, "w"), indent=2, sort_keys=True, ensure_ascii=False)
    return rec
