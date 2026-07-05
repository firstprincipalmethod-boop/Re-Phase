"""Optional golden-snapshot comparator. A golden file freezes a previously-approved 'computed'.
run_all compares freshly recomputed output against golden; mismatch => fail (catches drift)."""
import json, os

def load_golden(golden_dir, wid):
    p = os.path.join(golden_dir, f"{wid}.golden.json")
    return json.load(open(p)) if os.path.exists(p) else None

def freeze_golden(golden_dir, wid, computed):
    os.makedirs(golden_dir, exist_ok=True)
    p = os.path.join(golden_dir, f"{wid}.golden.json")
    json.dump({"id": wid, "computed": computed}, open(p, "w"), indent=2, sort_keys=True, ensure_ascii=False)
    return p

def compare(computed, golden):
    """Return (status, diffs). status in {'pass','fail','no-golden'}."""
    if golden is None:
        return "no-golden", []
    g = golden.get("computed", {})
    diffs = []
    for k in sorted(set(g) | set(computed)):
        if g.get(k) != computed.get(k):
            diffs.append((k, g.get(k), computed.get(k)))
    return ("pass" if not diffs else "fail"), diffs
