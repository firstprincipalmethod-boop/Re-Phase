# Vol.6.1 Witness Verification Harness (empty scaffold)

Purpose: enforce D11/D12/D13 — every certified number in Vol.6.1 is **generated from a finite
witness spec and verified**, never handwritten. Content is split per source volume (**D15**);
the verification machinery is shared.

## Status
EMPTY ON PURPOSE. No canonical witness specs and no compute functions are included yet.
Canonical specs are fixed from the source volumes (Vol.5.3 / 5.4) FIRST, dropped into
`specs/v53/` or `specs/v54/`, then compute functions are added in `compute_v53.py` /
`compute_v54.py`. This ordering prevents source-reading mistakes from being frozen into code
ahead of the specs. Certification order: **Vol.5.3 first**; Vol.5.4 golden freeze is **held**
pending must-fix items M1–M3 (see design log D15).

## Layout (per-volume split, D15)
```
specs/v53/       specs/v54/          canonical specs, input-only (NO numbers, D13)
compute_v53.py   compute_v54.py      @witness compute fns (register into compute.REGISTRY)
generated/v53/   generated/v54/      per-witness generated output  <id>.out.json
generated/table_v53.csv, table_v54.csv                aggregate registry tables (root)
golden/v53/      golden/v54/         frozen snapshots  <id>.golden.json
```
`source_volume` selects the bucket (`Vol.5.3 -> v53`, `Vol.5.4 -> v54`). The volume<->kind
coupling is definitional (D12): 5.3 = pathwise, 5.4 = selector. `spec_loader` **enforces** that a
spec's physical folder matches its `source_volume` bucket, and `schema.validate_spec` rejects an
unknown volume or a volume/kind mismatch — a misfiled witness fails loudly, never silently routing
to the wrong bucket.

## Pipeline (D13)
```
specs/<bucket>/*.json (inputs only, NO numbers)
  -> compute_v53.py / compute_v54.py   recompute Pt/Lift/feature/selector verdicts, tau_pre
    -> generated/<bucket>/*.out.json   (computed numbers + provenance)
      -> golden/<bucket>/*.golden.json (optional frozen snapshot; run_all diffs against it)
        -> generated/table_v53.csv, table_v54.csv
          -> Appendix witness sheets -> prose   (sheet generator: TODO)
```

## Files
- `schema.py`        — spec/output schemas + validator. Enforces **D13** (no expected numbers in a
                       spec), **D12** (count_objects required), and **D15** (source_volume bucket +
                       volume/kind coupling). `bucket(spec)` maps source_volume -> v53/v54.
- `spec_loader.py`   — loads + validates specs from `specs/` (recursive). Enforces **D15 placement**:
                       folder bucket must equal source_volume bucket.
- `compute.py`       — registry core: `@witness`, `compute`, `REGISTRY`.
- `compute_v53.py`   — Vol.5.3 (pathwise) witness fns. EMPTY; add with `@witness("v53_...")`.
- `compute_v54.py`   — Vol.5.4 (selector) witness fns. EMPTY; golden HELD per D15 (M1–M3).
- `output_writer.py` — writes `generated/<bucket>/<id>.out.json`.
- `golden.py`        — freeze / compare golden snapshots (drift detection); per-bucket dir.
- `report.py`        — builds `table_v53.csv` (pathwise) and `table_v54.csv` (selector) at
                       `generated/` root. Selector witnesses are **not** forced onto |Pt|/|Lift| (D12).
- `run_all.py`       — orchestrator. Imports `compute_v53`/`compute_v54` for @witness registration,
                       routes generated/golden per bucket. Runs cleanly with zero specs.
- `selftest.py`      — exercises the machinery with synthetic fixtures (no canonical content).
- `specs/v53/_TEMPLATE_pathwise.json.example`, `specs/v54/_TEMPLATE_selector.json.example`
                     — input-only spec shapes to fill from the source volumes.

## Registration side-effect (do not remove)
`@witness` registers only when its module is imported. `run_all.py` imports `compute_v53` and
`compute_v54` for that reason. **Drop those imports and every witness reports
`no-compute-registered`, so the release gate fails.** (Design log D15.)

## Use
```
python3 run_all.py     # load specs -> compute -> verify -> report -> pass/fail summary
python3 run_all.py --release   # certified-release gate (non-zero exit on any blocking item)
python3 selftest.py    # verify the harness machinery itself (22 checks)
```

**Release-gate caveat at scaffold stage:** with zero specs present, `run_all.py --release`
exits 0 ("PASS") vacuously — there is nothing to fail. This is *not* a certified-witness
claim; it only means the machinery itself is sound. A real certification claim requires a
`core_manifest.json` of required witness ids (planned, not yet added) so the gate fails
when a required witness is missing, not just when a present one fails.

## Conventions
- Vol.5.3 (`kind: pathwise`, `specs/v53/`): `Pt(y) = product_k F_k(y_k)` (full pointwise
  relaxation), `Lift(y)` its transition-compatible subset. Each sheet declares this in
  `count_objects` (D12). `tau_pre` (online prefix-failure index, §7.2) is generated as a
  **structured** value — `{"status":"finite","k":2}` or `{"status":"no_failure","k":null}` —
  never a numeric sentinel.
- Vol.5.4 (`kind: selector`, `specs/v54/`): family-level; counted objects are Y_adm, lift fibers,
  information cells, projected choice sets, and per-class selector verdicts — no forced |Pt|/|Lift|.
- A witness spec NEVER stores expected numbers; those exist only in `generated/` and `golden/` (D13).
