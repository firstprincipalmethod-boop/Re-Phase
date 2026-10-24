# Changelog

All notable changes to Re-Phase will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 2026-10-24 — Vol.6.1 corrected implementation integration (phases 2–3)

- Stage the fixed 2026-10-23 schema-2 harness: 59 files plus unchanged Toy D helper and package synchronization contract. All remain byte-identical to the fixed source package.
- Clarify G1: the 13 current golden paths now contain corrected snapshots; old v0.4.2 goldens remain at commit `cb592ad34ed6aa8db24fea02595793289919b6cf` and the immutable software DOI `21220093` archive. No old commit or archive is rewritten.
- Synchronize current README/correction/schema/publication navigation, address C2 and unavailable-tag recovery, and explicitly preserve the MIT software/data exception.
- Add a non-mutating repository-layout replay with both Python modes, 17 generated-file comparisons and eight fixed manuscript table/metadata comparisons. Runtime outcomes belong to its execution report, not the historical package receipts.
- Keep both Vol.6.1 successor records publication pending. PR/main merge is separate; no Zenodo edit/Publish, tag/Release, publication-artifact rebuild, or Core/Atlas/Decisions_Log update.

### 2026-10-22 — Vol.5.3/Vol.5.4 post-publication documentation sync

- Updated current navigation to the published corrected Vol.5.3 DOI `10.5281/zenodo.23499738` (`noheader_r1`) and Vol.5.4 DOI `10.5281/zenodo.23499819` (unchanged 2026-10-21 PDF/source pair).
- Added the [publication status and artifact registry](docs/publication-status-2026-10-22.md), based on owner confirmation, supplied post-publication screenshots, and separately identified pre-publication verification records. This sync does not claim a new direct Zenodo readback or remote SHA-256 measurement.
- Preserved historical DOI records and the original pre-publication/provenance checkpoint bodies; added notices linking those checkpoints to the later publication record. Earlier pending statements below describe their own checkpoints, not the current Vol.5.3/Vol.5.4 state.
- Retained the accepted Vol.5.4 reference [6] edition-note variant and the old Vol.5.3 hashes inside the unchanged Vol.5.4 validation archive.
- Vol.6.1 corrective revision and successor publication remain pending. No research code, witness specs, golden snapshots, generated outputs, schemas, publication binaries, Zenodo records, Git tags, or GitHub Releases were changed by this sync.

### 2026-10-22 — Vol.5.3 prepared artifact identity update

- Updated the prepared Vol.5.3 PDF/Source ZIP identities after layout-only removal of running headers and header rules from pages 2–37. Mathematical content, DOI, and publication status are unchanged; Zenodo publication remains pending (not yet published).
- Added the [headered-to-noheader provenance record](docs/vol53-noheader-provenance-2026-10-22.md), retaining both file identities and the historical Vol.5.3 validation inputs inside the unchanged Vol.5.4 archive. This documentation record does not certify a Zenodo draft replacement; remote execution requires a separate before/after receipt. No publication artifacts, Vol.6.1 code/spec/golden files, Zenodo records, tags, or GitHub Releases were changed by this addition.

### 2026-10-21 — Pre-publication documentation sync

- Recorded prepared corrected editions for Vol.5.3 and Vol.5.4, including owner-supplied frozen PDF/ZIP identities; Zenodo publication is pending.
- Preserved historical Zenodo DOI records pending publication of the corrected editions.
- Clarified Vol.6.1 v0.4.2 as a historical archived harness under corrective revision, with owner-designated successor records pending publication.
- Added a current correction-status document while preserving the historical v0.4.2 Zenodo description.
- Synchronized repository navigation and README license wording with the existing license policy.
- No research code, witness specs, golden snapshots, generated outputs, schemas, publication binaries, Zenodo records, Git tags, or GitHub Releases were changed.

### Earlier repository setup

- Repository initialization
- Core framework structure established
