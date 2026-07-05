"""Self-test of the harness machinery using SYNTHETIC fixtures only.
No canonical witness content here — these are throwaway objects that exercise
schema validation (incl. D13), compute registry, golden compare, and table build."""
import sys, os, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import validate_spec, validate_output, bucket
from compute import witness, compute, REGISTRY
from golden import compare, freeze_golden, load_golden
from report import build_tables, SELECTOR_COLS
from spec_loader import load_specs

def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}"); return cond

ok = True
# 1. clean input-only spec validates
clean = {"id":"_fixture","source_volume":"Vol.5.3","kind":"pathwise","role":"r",
         "status":"core","count_objects":{"pt_object":"Pt=prod F_k"},"spec":{"states":{}}}
v,_ = validate_spec(clean); ok &= check("clean input-only spec passes", v)

# 2. D13: spec containing expected numbers is REJECTED
dirty = dict(clean); dirty["expected"]={"pt_size":27}
v,errs = validate_spec(dirty); ok &= check("D13: spec with 'expected' is rejected", (not v) and any("D13" in e for e in errs))

# 3. nested expected number also caught
dirty2 = {"id":"x","source_volume":"Vol.5.3","kind":"pathwise","role":"r","status":"core",
          "count_objects":{"a":"b"},"spec":{"foo":{"lift_size":2}}}
v,errs = validate_spec(dirty2); ok &= check("D13: nested expected number is rejected", (not v) and any("D13" in e for e in errs))

# 4. missing count_objects rejected (D12)
nc = dict(clean); nc.pop("count_objects")
v,_ = validate_spec(nc); ok &= check("missing count_objects rejected", not v)

# 5. compute with empty registry -> no-compute-registered
REGISTRY.clear()
c,st = compute(clean); ok &= check("empty registry -> no-compute-registered", st=="no-compute-registered" and c=={})

# 6. register a dummy compute -> ok
@witness("_fixture")
def _(spec): return {"pt_size":6,"lift_size":1,"recoverable":True,"verdict":"demo"}
c,st = compute(clean); ok &= check("registered compute returns computed dict", st=="ok" and c["pt_size"]==6)

# 7. golden compare: freeze then match -> pass; tamper -> fail
with tempfile.TemporaryDirectory() as d:
    freeze_golden(d, "_fixture", c)
    g = load_golden(d, "_fixture")
    s,diffs = compare(c, g); ok &= check("golden compare pass on identical", s=="pass" and not diffs)
    s,diffs = compare({**c,"pt_size":99}, g); ok &= check("golden compare fail on drift", s=="fail" and bool(diffs))

# 8. output schema validates a generated record, and accepts EVERY status run_all may write
from schema import ALLOWED_VERIFICATION_STATUS, ALLOWED_COMPUTE_STATUS
rec = {"id":"_fixture","generated_by":"compute.py","compute_status":"ok","computed":c,
       "verification":{"status":"pass"}}
v,_ = validate_output(rec); ok &= check("generated output record validates", v)
# run_all writes these verification statuses; schema must accept all of them
for st in ["pass","fail","pending","no-golden","no-compute-registered","error"]:
    r = {"id":"x","generated_by":"c","compute_status":"ok","computed":{},"verification":{"status":st}}
    vv,_ = validate_output(r); ok &= check(f"output status '{st}' accepted", vv)
# and a bogus status is rejected
rbad = {"id":"x","generated_by":"c","compute_status":"ok","computed":{},"verification":{"status":"weird"}}
vv,_ = validate_output(rbad); ok &= check("bogus verification status rejected", not vv)
# bogus compute_status rejected
rbad2 = {"id":"x","generated_by":"c","compute_status":"nonsense","computed":{},"verification":{"status":"pass"}}
vv,_ = validate_output(rbad2); ok &= check("bogus compute_status rejected", not vv)
# run_all's blocking set (minus 'invalid') is a subset of schema-allowed statuses
import run_all as _ra
ok &= check("run_all status set subset of schema-allowed",
            (_ra.RELEASE_BLOCKING - {"invalid"}) <= ALLOWED_VERIFICATION_STATUS)

# 9. report builds a table from records (pathwise)
with tempfile.TemporaryDirectory() as d:
    paths = build_tables([{"id":"_fixture","kind":"pathwise","computed":c}], d)
    ok &= check("report builds pathwise table", paths["pathwise"][1]==1 and os.path.exists(paths["pathwise"][0]))

# 10. report builds the SELECTOR table: selector columns are used (kind routing),
#     and a pathwise record in the same batch does NOT leak into the selector table (D12).
with tempfile.TemporaryDirectory() as d:
    sel = {"id":"_sel_fixture","offline":True,"causal":False,"lookback_1":True,
           "memoryless":False,"quotient_selector":True,"verdict":"demo-selector"}
    paths = build_tables([{"id":"_sel_fixture","kind":"selector","computed":sel},
                          {"id":"_fixture","kind":"pathwise","computed":c}], d)
    sp, sn = paths["selector"]
    header = open(sp).readline().strip().split(",")
    ok &= check("report builds selector table",
                sn==1 and paths["pathwise"][1]==1 and header==SELECTOR_COLS and os.path.exists(sp))

# 11. D15 volume routing: source_volume -> v53/v54 bucket; volume<->kind misfile and
#     unknown volume are rejected by validate_spec (so a misroute is loud, never silent no-golden).
pw  = {"id":"v53_x","source_volume":"Vol.5.3","kind":"pathwise","role":"r","status":"core",
       "count_objects":{"pt_object":"Pt"},"spec":{}}
sel = {"id":"v54_x","source_volume":"Vol.5.4","kind":"selector","role":"r","status":"core",
       "count_objects":{"family_object":"Y_adm"},"spec":{}}
mis = dict(pw); mis["kind"] = "selector"          # 5.3 spec mislabelled as selector
unk = dict(pw); unk["source_volume"] = "Vol.9.9"  # volume outside the certified set
ok &= check("D15 volume bucket routing + misfile/unknown rejected",
            bucket(pw)=="v53" and bucket(sel)=="v54"
            and validate_spec(pw)[0] and validate_spec(sel)[0]
            and (not validate_spec(mis)[0]) and (not validate_spec(unk)[0]))

# 12. D15 placement enforcement: a valid spec dropped in the WRONG bucket folder is rejected by
#     spec_loader (path bucket must match source_volume bucket), not silently routed elsewhere.
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "v53")); os.makedirs(os.path.join(d, "v54"))
    good = {"id":"v53_ok","source_volume":"Vol.5.3","kind":"pathwise","role":"r","status":"core",
            "count_objects":{"pt_object":"Pt"},"spec":{}}
    bad  = dict(good, id="v53_misplaced")             # same 5.3 spec, physically dropped in v54/
    json.dump(good, open(os.path.join(d, "v53", "v53_ok.json"), "w"))
    json.dump(bad,  open(os.path.join(d, "v54", "v53_misplaced.json"), "w"))
    loaded, probs = load_specs(d)
    loaded_ids = {s["id"] for s in loaded}
    placement_flagged = any("D15 placement" in e for _, es in probs for e in es)
    ok &= check("D15 placement mismatch rejected by spec_loader",
                loaded_ids == {"v53_ok"} and placement_flagged)

# 13. D-v54-08: Toy B/C declare a redundant restatement of derivable data
#     (left_support/right_support alongside bridge_edges; required_prefix_choice
#     alongside transitions). The real compute functions must reject a spec where
#     the declared value diverges from what's actually derivable -- same
#     discipline as D13's "expected value rejected" tests, but for a
#     cross-consistency invariant rather than a forbidden key. Field SHAPES here
#     mirror the real Toy B/C specs; the values are deliberately wrong synthetic
#     fixtures, not canonical witness content.
import compute_v54  # noqa: F401  (import registers the real Toy A-F functions)
from compute import REGISTRY as _v54_registry

def _raises_assertion(fn, spec):
    try:
        fn(spec); return False
    except AssertionError:
        return True

toy_b_tampered = {"id": "v54_toy_B_bridge_conflict", "spec": {
    "choice_kind": "bridge_edge",
    "information_cell": {"I_bridge": ["u", "v"]},
    "bridge_edges": {"u": [["A", "B"], ["C", "D"]], "v": [["A", "D"], ["C", "B"]]},
    "left_support": ["A", "Z"],   # WRONG: derived common_left_support is ["A","C"]
    "right_support": ["B", "D"],
}}
ok &= check("D-v54-08: Toy B mismatched declared left_support is rejected",
            _raises_assertion(_v54_registry["v54_toy_B_bridge_conflict"], toy_b_tampered))

toy_c_tampered = {"id": "v54_toy_C_nonblocking", "spec": {
    "choice_kind": "nonblocking_prefix",
    "shared_prefix": "s", "local_choices": ["m", "n"],
    "futures": {
        "alpha": {"terminal": "a", "required_prefix_choice": "n"},  # WRONG: derived is "m"
        "beta": {"terminal": "b", "required_prefix_choice": "n"},
    },
    "transitions": {"T0": [["s", "m"], ["s", "n"]], "T1": [["m", "a"], ["n", "b"]]},
}}
ok &= check("D-v54-08: Toy C mismatched declared required_prefix_choice is rejected",
            _raises_assertion(_v54_registry["v54_toy_C_nonblocking"], toy_c_tampered))

REGISTRY.clear()
print("ALL PASS" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
