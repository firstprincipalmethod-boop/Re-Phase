"""Report / table generator interface. Builds summary table from GENERATED outputs only."""
import csv, os

# columns differ by witness kind (D12: don't force |Pt|/|Lift| on selector witnesses)
# certified v53 column set locked 2026-07-04, updated 2026-07-05 (v0.1 feedback, see
# Obsidian "claudeへの指示6.1v0.1に向けて"): target_included (boolean) replaced by
# target_check (controlled vocabulary, schema.ALLOWED_TARGET_CHECK); tau_pre stays
# structured in the generated JSON but is flattened to tau_pre_status/tau_pre_k here so
# the registry table has no embedded objects. feature_image_pt/lift replace the
# deprecated H_Pt/H_Lift (misread as entropy).
PATHWISE_COLS = ["id", "pt_size", "lift_size", "lift_status", "feature_image_pt", "feature_image_lift",
                 "target", "target_check", "tau_pre_status", "tau_pre_k", "recoverable", "verdict"]
SELECTOR_COLS = ["id", "offline", "causal", "lookback_1", "memoryless", "quotient_selector", "verdict"]

def _row(rec, cols):
    c = rec.get("computed", {})
    tau_pre = c.get("tau_pre") or {}
    flat = dict(c, tau_pre_status=tau_pre.get("status", ""), tau_pre_k=tau_pre.get("k", ""))
    return {col: (rec["id"] if col == "id" else flat.get(col, "")) for col in cols}

def build_tables(records, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for kind, cols, fname in [("pathwise", PATHWISE_COLS, "table_v53.csv"),
                              ("selector", SELECTOR_COLS, "table_v54.csv")]:
        rows = [_row(r, cols) for r in records if r.get("kind") == kind]
        p = os.path.join(out_dir, fname)
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for r in rows: w.writerow(r)
        paths[kind] = (p, len(rows))
    return paths
