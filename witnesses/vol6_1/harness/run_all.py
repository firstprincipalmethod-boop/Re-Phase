#!/usr/bin/env python3
"""Vol.6.1 verification harness orchestrator (EMPTY until canonical specs + compute are added).
Pipeline (D11/D13):  specs -> compute -> golden compare -> write generated output (final status) -> report.

Modes:
  scaffold (default): pending is allowed; exit 0 unless a hard error.
  --strict / --release: certified release gate. ANY of
      invalid spec, compute error, no-compute-registered, no-golden, fail, pending
  causes a non-zero exit.
Runs cleanly with zero specs (in scaffold mode)."""
import sys, os, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from spec_loader import load_specs
from compute import compute, REGISTRY
from output_writer import write_output
from golden import load_golden, compare
from report import build_tables
from schema import ALLOWED_VERIFICATION_STATUS, bucket, REQUIRED_WITNESS_IDS, required_id_check

# Populate the compute REGISTRY by importing the per-volume witness modules for their
# @witness registration side-effect (D15). If this import is removed, the witnesses are
# never registered -> every witness reports 'no-compute-registered' -> the release gate
# fails. Registration must happen here (or in compute.py), not only in the module files.
import compute_v53, compute_v54  # noqa: F401  (imported for side-effect only)

SPECS = os.path.join(HERE, "specs")
GEN   = os.path.join(HERE, "generated")
GOLD  = os.path.join(HERE, "golden")

# verification states that are NOT acceptable in a certified release
RELEASE_BLOCKING = {"fail", "pending", "no-golden", "no-compute-registered", "error", "invalid"}
# every non-"invalid" blocking/terminal status run_all can assign must be a schema-allowed output status
# (explicit raise, not assert: must hold under python -O as well)
if not (RELEASE_BLOCKING - {"invalid"}) <= ALLOWED_VERIFICATION_STATUS:
    raise RuntimeError("run_all status set drifted from schema.ALLOWED_VERIFICATION_STATUS")

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", "--release", dest="strict", action="store_true",
                    help="certified-release gate: invalid/fail/pending/no-compute/no-golden -> non-zero exit")
    args = ap.parse_args(argv)

    specs, problems = load_specs(SPECS)
    print("= Vol.6.1 witness harness =  (mode: %s)" % ("release/strict" if args.strict else "scaffold"))
    print(f"specs loaded: {len(specs)} | invalid: {len(problems)} | compute fns registered: {len(REGISTRY)}")
    for path, errs in problems:
        print(f"  [INVALID] {os.path.basename(path)}")
        for e in errs: print(f"            - {e}")

    records = []
    counts = {"pass":0,"fail":0,"pending":0,"no-golden":0,"no-compute-registered":0,"error":0}
    for spec in specs:
        b = bucket(spec)                                           # 0) certification bucket (D15)
        gen_dir, gold_dir = os.path.join(GEN, b), os.path.join(GOLD, b)
        computed, cstatus = compute(spec)                          # 1) compute
        if cstatus == "ok":
            gstatus, diffs = compare(computed, load_golden(gold_dir, spec["id"]))  # 2) verify vs golden/<b>
        else:
            gstatus, diffs = cstatus, []                           # no-compute-registered / error
        final = {"pass":"pass","fail":"fail","no-golden":"no-golden",
                 "no-compute-registered":"no-compute-registered","error":"error"}.get(gstatus,"pending")
        rec = write_output(spec, computed, cstatus, gen_dir, verification_status=final)  # 3) write into generated/<b>
        records.append(rec)
        counts[final if final in counts else "pending"] = counts.get(final,0) + 1
        print(f"  [{final.upper():22s}] {spec['id']:40s} compute={cstatus}")
        for k, g, c in diffs: print(f"          diff {k}: golden={g!r} != computed={c!r}")

    if specs:
        tables = build_tables(records, GEN)
        for kind, (p, n) in tables.items(): print(f"table[{kind}]: {n} rows -> {p}")

    print("summary: " + " ".join(f"{k}={v}" for k,v in counts.items()) + f" | invalid_specs={len(problems)}")

    if args.strict:
        # Release manifest check (minimal D14): the certified suite is exactly the
        # REQUIRED_WITNESS_IDS set. A deleted spec (or an empty spec directory) must
        # fail the gate, not silently shrink the suite; an unexpected id must not
        # silently grow it.
        missing, unexpected = required_id_check(s["id"] for s in specs)
        for wid in missing:    print(f"  [MISSING REQUIRED] {wid}")
        for wid in unexpected: print(f"  [UNEXPECTED SPEC ] {wid}")
        blocking = len(problems) + sum(counts.get(s,0) for s in RELEASE_BLOCKING)
        if blocking or missing or unexpected:
            print(f"RELEASE GATE: FAIL ({blocking} blocking, {len(missing)} missing required, "
                  f"{len(unexpected)} unexpected)")
            return 2
        print(f"RELEASE GATE: PASS (all {len(REQUIRED_WITNESS_IDS)} required witnesses present, "
              "generated, golden-verified)")
        return 0
    # scaffold mode: only hard errors fail the run
    return 1 if (counts["error"] or len(problems)) else 0

if __name__ == "__main__":
    raise SystemExit(main())
