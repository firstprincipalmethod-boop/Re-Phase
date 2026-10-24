# Vol.6.1 — A Finite Witness Harness

**Corrected edition: 2026-10-23; schema 2.** This source tree contains the
corrected implementation, not the historical v0.4.2 implementation. Its 59
harness files are unchanged copies of the fixed MIT Software ZIP (SHA-256
`48abc2ae97e1cf0ea5089f7e9610dfef0d4b6c14194f41e85a8660c4086c181e`).

This is the phase-3 integration checkpoint, not a publication announcement.
The manuscript DOI `10.5281/zenodo.23499925` (CC BY-NC 4.0) and software DOI
`10.5281/zenodo.23499964` (MIT) remain **publication pending** at the supplied
2026-10-24 Zenodo checkpoint. PR/merge is a separate step. See
[publication status](../../docs/publication-status-2026-10-24.md) and
[CORRECTION_STATUS.md](CORRECTION_STATUS.md).

## Reproduce from a repository checkout

Use Python 3.10 or later; no third-party Python package is required. From the
repository root, run:

```sh
python -I -B witnesses/vol6_1/recheck_integration.py --report ../vol61-repository-replay.json
```

The wrapper validates the copied bytes, executes the fixed-suite gate,
primary selftest, checker selftest, independent complete-record checker,
bounded comparisons and Toy D correspondence in both normal and `-O` modes.
It writes only to temporary directories and the explicitly chosen external
report, not to tracked `generated/`, `golden/`, specs or package archives.
It compares each fresh set of 17 result files to both the repository snapshot
and the fixed manuscript result hashes, and regenerates the eight manuscript
table/metadata files using the unchanged MIT table generator in a temporary
source-layout directory. The generator uses preserved package verification
records to reproduce the fixed manuscript's tables; those records are not
relabelled as new runs. Fresh execution records live only in the new report.

To inspect Toy D directly from the repository root, the relocated helper
requires its source root explicitly:

```sh
python -I -B witnesses/vol6_1/checks/toy_d_information_correspondence.py --software-root .
python -I -B -O witnesses/vol6_1/checks/toy_d_information_correspondence.py --software-root .
```

`--release` on `harness/run_all.py` is a compatibility name for the strict local
gate; it does not publish, upload, tag or approve a release. Direct gate calls
without `--out-dir` write the tracked generated directory, so the wrapper above
is the preferred non-mutating integration check. `freeze_candidate.py` is not
used by this process and is never used to make a failed comparison pass.

## Contents and correspondence

| Location | Meaning |
|---|---|
| `harness/specs/v53`, `harness/specs/v54` | 7 pathwise and 6 selection inputs |
| `harness/contract.py`, `suite_manifest.json` | schema 2, complete IDs and pinned spec/golden bytes |
| `harness/golden/` | 13 corrected complete-result envelopes |
| `harness/generated/` | 13 result JSON, 3 CSV and one summary |
| `checks/toy_d_information_correspondence.py` | finite C1 qualification, not general equivalence |
| `SYNC_CONTRACT.json` | unchanged standalone package contract, not a repository manifest |
| `integration/phase2-source-map.json` | phase-2 import mapping |
| `integration/phase3-manifest.json` | source hashes and fixed manuscript result/table expectations |
| `integration/table-inputs/` | unchanged table generator, source map and past verification records |

See [schema/migration](SCHEMA_AND_MIGRATION.md), [correction map](CORRECTION_MAP.md)
and [checker coverage](INDEPENDENT_COVERAGE.md). The source correspondence is
in `integration/table-inputs/provenance/source_map.json`; the fixed upstream
records are Vol.5.3 `23499738` (2026-10-21 noheader-r1) and Vol.5.4 `23499819`
(2026-10-21). Their files are not changed by this integration.

The copied schema/correction/coverage notes retain original package-relative paths;
`verification/` in those notes maps to `integration/table-inputs/verification/`
here. Other archived provenance remains in the fixed source ZIP.

The contract's relative paths are interpreted in the original package layout.
This repository does not contain the entire software or manuscript archive.
The archived `verify_package.py` checks the original archive, not this selective
repository import. The repository wrapper checks the explicitly mapped subset.
It does not rebuild the PDF or replay archived patch applications.

## Typed obligations and evidence limits

Toy A checks every time of the supplied unique paths. Toy B is abstract,
member-dependent edge choice. Toy C's positive local choice does not establish
a full-path selector. D/E/F distinguish display/path sections from terminal
common-action policies. Both E/F have quotient sections; their post-policy
counts differ. Stable legacy IDs, including `not_selector`, are not current
semantic claims. `role_label` is metadata; the 50 `claim_checks` are computed.

Target counts are 13 cases, 50 finite predicates, 97 primary selftests, 116
checker selftests, 20,740 bounded path models (373,320 fields) and 2,696
one-decision policy models per mode. The two modes repeat the same models;
they are not additional distinct models. A valid replay report must actually
record success. Source fidelity, regression equality and numerical checking
are distinct evidence. Shared validation and same-author checker code do not
constitute external review, a general proof, controller synthesis, CPre
certification, minimum-memory result, stability theorem or performance advantage.

## Current golden paths and historical recovery (G1)

`harness/golden/` contains the **2026-10-23 corrected snapshots**. Phase 2
replaced all 13 golden files at the same repository paths; it did not merely
add an alternative directory. Old Git commits and original Zenodo archives
were not modified. The manuscript's statement that old golden snapshots are
not overwritten in place refers to the preserved **v0.4.2 archives**, not to
an immutable path on a moving Git branch.

Recover the previous repository golden files at commit
`cb592ad34ed6aa8db24fea02595793289919b6cf`:

```sh
git show cb592ad34ed6aa8db24fea02595793289919b6cf:witnesses/vol6_1/harness/golden/v54/v54_toy_E_target_sound_not_selector.golden.json
```

The historical MIT software archive is DOI
[10.5281/zenodo.21220093](https://doi.org/10.5281/zenodo.21220093), filename
`Re_Phase_Vol_6_1_software_v0_4_2.zip`, SHA-256
`82164beff12de69e1493ba558b30d2a840dd3cd01d2877346a6bbd27dc1cd8c4`.
The historical manuscript source archive (DOI `10.5281/zenodo.21220080`) has
SHA-256 `3905df1ba66069ab195accc72c5977f53f00cbc57ae90237aacbf73dcf6e958a`.
The old `vol6.1-v0.4.2` tag was unavailable in earlier checks; it is not recreated
and is not the recovery procedure. Historical 13/13 PASS is not a new
certification against corrected Vol.5.3/Vol.5.4.

## History and licenses

The previous README and correction-status text are preserved byte-for-byte in
[historical/](historical/). [ZENODO_DESCRIPTION.md](ZENODO_DESCRIPTION.md) is
explicitly the historical v0.4.2 description; the corrected package description
is [software-notes/ZENODO_DESCRIPTION_2026-10-23.txt](software-notes/ZENODO_DESCRIPTION_2026-10-23.txt).
Past reviews, platform observations and packaged contract fields retain their
original targets. New repository runs do not rewrite them.

Imported code, machine-readable fixtures/results/contracts and explicitly
identified operational support retain MIT; see [LICENSE-SOFTWARE.md](LICENSE-SOFTWARE.md).
Manuscript text, figures, tables and PDF remain separately CC BY-NC 4.0 and are
not included here. The table generator is a declared MIT exception in the
manuscript source; copying it does not relicense the manuscript.
