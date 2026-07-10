# Vol.6.1 Witness Verification Harness

Purpose: enforce D11/D12/D13 — every certified number in Vol.6.1 is **generated from a finite
witness spec and verified**, never handwritten. Content is split per source volume (**D15**);
the verification machinery is shared.

## Status
**Repository-complete for both lanes.** Vol.5.3 (v53, pathwise) has all 7 witnesses live,
golden-frozen, and release-gate certified. Vol.5.4 (v54, selector) has all 6 Toy A–F witnesses
live, golden-frozen, and release-gate certified, including a golden **content audit** pass
(D-v54-07~09) that verified the golden output is faithful to the M1–M3/D-v54 definitions, not
just internally self-consistent with its own compute. `run_all.py --release` reports
**13/13 PASS** (7 v53 + 6 v54).

## Archive
- Manuscript: https://doi.org/10.5281/zenodo.21220080 (v0.4.2)
- Witness harness (this directory): https://doi.org/10.5281/zenodo.21220093
- git tag: `vol6.1-v0.4.2`

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
      -> golden/<bucket>/*.golden.json (frozen snapshot; run_all diffs against it)
        -> generated/table_v53.csv, table_v54.csv
          -> Appendix witness sheets -> prose   (sheet generator: TODO)
```
Before a golden snapshot is frozen, the generated output is reviewed by hand against the
canonical spec and the source-volume definitions — `run_all.py --release` passing only proves
generated==golden, not that golden is *correct*; that review step matters (see the v54 content
audit, D-v54-07~09, below).

## Files
- `schema.py`        — spec/output schemas + validator. Enforces **D13** (no expected numbers in a
                       spec), **D12** (count_objects required), and **D15** (source_volume bucket +
                       volume/kind coupling). `bucket(spec)` maps source_volume -> v53/v54.
                       `FORBIDDEN_IN_SPEC` covers both v53-era fields (`lift_status`, `tau_pre`, ...)
                       and v54 generated fields (`cell_conflict`, `square_commutes`, `exact`, ...).
- `spec_loader.py`   — loads + validates specs from `specs/` (recursive). Enforces **D15 placement**:
                       folder bucket must equal source_volume bucket. Only `*.json` is loaded —
                       `*.json.example` files are ignored, so draft/example specs never affect the
                       release gate.
- `compute.py`       — registry core: `@witness`, `compute`, `REGISTRY`.
- `compute_v53.py`   — Vol.5.3 (pathwise) witness fns. All 7 v53 witnesses registered.
- `compute_v54.py`   — Vol.5.4 (selector) witness fns. All 6 Toy A–F witnesses registered.
- `output_writer.py` — writes `generated/<bucket>/<id>.out.json`.
- `golden.py`        — freeze / compare golden snapshots (drift detection); per-bucket dir.
- `report.py`        — builds `table_v53.csv` (pathwise) and `table_v54.csv` (selector) at
                       `generated/` root. Selector witnesses are **not** forced onto |Pt|/|Lift| (D12);
                       `SELECTOR_COLS` is a summary row (`id`/`choice_kind`/`verdict`/
                       `verification_status`) — variant-level detail lives only in the JSON.
- `run_all.py`       — orchestrator. Imports `compute_v53`/`compute_v54` for @witness registration,
                       routes generated/golden per bucket. In `--release` mode the loaded id set
                       must equal `schema.REQUIRED_WITNESS_IDS` exactly: missing or unexpected
                       ids fail the gate, and zero specs fail as 13 missing ids.
- `selftest.py`      — exercises the machinery with synthetic fixtures (no canonical content);
                       28 checks, including negative cases for the D-v54-08 cross-check discipline
                       and for the release manifest (missing / empty / unexpected id sets).
- `specs/v53/_TEMPLATE_pathwise.json.example`, `specs/v54/_TEMPLATE_selector.json.example`
                     — input-only spec shapes for adding a new witness.

## Registration side-effect (do not remove)
`@witness` registers only when its module is imported. `run_all.py` imports `compute_v53` and
`compute_v54` for that reason. **Drop those imports and every witness reports
`no-compute-registered`, so the release gate fails.** (Design log D15.)

## Use
```
python3 run_all.py            # load specs -> compute -> verify -> report -> pass/fail summary
python3 run_all.py --release   # certified-release gate (non-zero exit on any blocking item)
python3 selftest.py            # verify the harness machinery itself (28 checks)
python3 -O selftest.py         # rejection guarantees must also hold under optimized mode
python3 -O run_all.py --release
```

**Required-id manifest (implemented):** `schema.REQUIRED_WITNESS_IDS` (derived from the
registered verdict vocabulary, so there is no second list to drift) is enforced by the
`--release` gate: a required witness missing from `specs/`, an unexpected id, or an empty spec
directory all fail the gate with a non-zero exit. Exercised by selftest negative cases; holds
under `python -O`. Remaining deferred hardening: a hash-pinned golden manifest.

## Conventions

### Vol.5.3 (`kind: pathwise`, `specs/v53/`)
`Pt(y) = product_k F_k(y_k)` (full pointwise relaxation), `Lift(y)` its transition-compatible
subset. Each sheet declares this in `count_objects` (D12). `tau_pre` (online prefix-failure
index, §7.2) is generated as a **structured** value — `{"status":"finite","k":2}` or
`{"status":"no_failure","k":null}` — never a numeric sentinel. Two witnesses
(`v53_same_slices_different_edges`, `v53_constant_velocity`) compare two variants and return
nested `variant_a`/`variant_b` (or `full_context`/`thinned_context`) blocks — `report.py`'s flat
CSV table leaves some columns blank for these rows; the nested detail is only in the JSON.

### Vol.5.4 (`kind: selector`, `specs/v54/`)
Family-level; counted objects are the admissible base-path family, per-selector-class
information cells, and member-relative projected choice sets `V^Q(y)` for a fixed `choice_kind`
— no forced `|Pt|`/`|Lift|`. Every witness carries a top-level `verdict`
(`schema.VERDICT_BY_WITNESS`, a controlled vocabulary — see `Decisions_Log.md` D-v54-02).

**cell_conflict certificate** (M2 lock): for an information cell with member -> choice-set data,
the common choice set is the intersection across members; `cell_conflict` is true iff that
intersection is empty. For `choice_kind` in `{state, bridge_edge, action}` a nonempty common
choice set is itself a constructive existence witness. `choice_kind=nonblocking_prefix`
(Toy C) is nonexistence-only — existence would additionally need cross-time consistency, not
yet certified.

**Variant-bearing witnesses** (D-v54-03: Toy A, Toy D): a single witness id carries multiple
named `variants` in its generated output rather than being split into separate files, because
the comparison across variants *is* the witness's claim. The top-level `verdict` names the
primary claim (D-v54-06); full per-variant detail (including, for Toy D, a per-`memory_class`
breakdown — D-v54-07) lives only in `variants`, never flattened into a CSV column. An existence
claim (`selector_exists=true`) is only made alongside an explicit `selector_table` witness
(D-v54-04), never bare.

**Quotient witnesses** (M3 lock: Toy E, Toy F): `exact`/`target_sound`/`square_commutes` are
derived generically from the spec's own `quotient_map`/`target_verdict`/`display_images` (never
hardcoded); `square_commutes` is grounded via the identity display-quotient assumption when
`display_quotient="identity"`. `cpre_claim_status` is always `"not_certified"` — CPre inclusion
is out of scope unless a must/may abstraction mode is fixed.

**Redundant declared inputs are cross-checked, not just ignored** (D-v54-08): Toy B's
`left_support`/`right_support` and Toy C's `required_prefix_choice` restate values that are
independently derivable from `bridge_edges`/`transitions`. Compute derives its own values and
checks them against the declaration; a mismatch raises an explicit `ValueError` (effective
under `python -O` as well), surfacing as a compute error, not a silent divergence.

**`lookback_r` window convention** (D-v54-09): `lookback_r` means the current observation plus
the `r` preceding observations (window `r+1`); `memoryless` is `lookback_0` (window 1). This
matches Vol.5.4's `q_lookback(k,r,y) = y[max(0,k-r):k+1]`.

### Both volumes
A witness spec NEVER stores expected numbers; those exist only in `generated/` and `golden/`
(D13). Promoting a witness from draft to certified follows: `*.json.example` (Obsidian-reviewed
draft) -> `*.json` (live spec, input-only) -> `compute_<bucket>.py` function registered ->
`generated/<bucket>/<id>.out.json` reviewed by hand -> `golden/<bucket>/<id>.golden.json` frozen
-> `run_all.py --release` re-verified.
