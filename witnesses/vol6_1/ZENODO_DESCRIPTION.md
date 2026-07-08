# Re-Phase Vol.6.1 Witness Harness

Version: v0.4.2
Date: 2026-07-06
Author: Takashi Ito, Independent Researcher
Software DOI: 10.5281/zenodo.21220093
Associated manuscript DOI: 10.5281/zenodo.21220080
License: MIT License
Archived source state: git tag `vol6.1-v0.4.2` (main, v53+v54 repository-complete, 13/13 release-gate PASS)

## Description

This archive contains the executable witness harness for Re-Phase Vol.6.1.

The harness implements the finite certification layer for selected distinctions from:

- Re-Phase Vol.5.3 pathwise compatibility lifting
- Re-Phase Vol.5.4 information-adapted selector preservation

The certified suite contains 13 finite witnesses:

```text
v53 pathwise witnesses: 7 / 7
v54 selector witnesses: 6 / 6
total certified witnesses: 13 / 13
```

Each certified witness has:

- an input-only canonical specification
- a registered compute function
- a generated output
- a reviewed golden snapshot
- release-gate verification

The release command is:

```text
python run_all.py --release
```

Expected release status: 13 specs loaded, 13 PASS, `RELEASE GATE: PASS`.

The v54 lane also has a completed golden content audit against the locked M1–M3 definitions
and D-v54 decisions (D-v54-07~09) — this verifies the golden output is faithful to those
definitions, not just internally self-consistent with its own compute.

## Scope

This software archive contains the Vol.6.1 witness harness, canonical specs, generated outputs,
golden snapshots, report tables, and selftests. It does **not** contain the manuscript as the
primary archived work. The associated manuscript is archived separately as:

> Re-Phase Vol.6.1: A Certified Finite Witness Suite for Vol.5.3 and Vol.5.4
> DOI: 10.5281/zenodo.21220080

## Repository

https://github.com/firstprincipalmethod-boop/Re-Phase

## License

The code, scripts, and Vol.6.1 witness harness are licensed under the MIT License
(see `LICENSE-CODE.md` at the repository root).

Non-code manuscript materials are archived separately under CC BY-NC 4.0
(DOI 10.5281/zenodo.21220080).
