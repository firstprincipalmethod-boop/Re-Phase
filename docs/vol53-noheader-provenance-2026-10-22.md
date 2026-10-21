# Vol.5.3 noheader-r1: prepared-artifact provenance

Record date: 2026-10-22. Manuscript edition date: 2026-10-21.
DOI retained: `10.5281/zenodo.23499738`.

This note connects the previous headered **prepared files** with the current `noheader_r1` prepared pair. It is not a claim that either pair was newly published, uploaded, or verified on Zenodo by this documentation change. The historical published source edition, DOI `10.5281/zenodo.20956126`, is a separate object and is not altered.

## 1. Before and after

### Previous prepared pair: headered, retained as historical input

| File | Bytes | SHA-256 | MD5 |
|---|---:|---|---|
| `Re_Phase_Vol_5_3_Corrected_2026-10-21.pdf` | 6,359,551 | `d91c8eb5139bb4c65f4cddb7db282ce25518214f6f740dfd0b2525c8dc0286a5` | `67bbed8a324538896858bc8dec3feb3a` |
| `Re_Phase_Vol_5_3_Source_2026-10-21.zip` | 6,008,616 | `c75e9b39f5eaa35f2280683647149c3c6594541ff2784f1b8bf3bce5a37634fb` | `26619d06a230404cc6c30fbfd290aab1` |

### Current prepared pair: noheader-r1

| File | Bytes | SHA-256 | MD5 |
|---|---:|---|---|
| `Re_Phase_Vol_5_3_Corrected_2026-10-21_noheader_r1.pdf` | 6,356,099 | `4a2dd6ed2fa2f93a07d195220f203359b5989137fc8d758022e3a02551d2f6f3` | `b8b7cd1c7ec15e85eb3eb6ce72568af5` |
| `Re_Phase_Vol_5_3_Source_2026-10-21_noheader_r1.zip` | 6,037,993 | `b544ffd7a31f5a0213b7b1306251f24b4cb73ee8016674a5df98ae08fbcf81ec` | `1b29cc9bb18c8ad9d6c8ce3eabac01ab` |

The old and new files are **not byte-identical**. Their filenames and both checksums must not be interchanged. The prepared-file registry was updated in PR #26, merged as `5e60e8ec1194469deb0311cfeb7bbe584eb5db4d`. See [the prepared-file registry](prepublication-status-2026-10-21.md).

## 2. Change scope and evidence

The noheader generation report records removal of the left and right running headers and the upper rule on pages 2-37. It records an unchanged cover, 37-page pagination, body text and positions, figures, footer, links, outline, DOI, edition date, and PDF metadata. The source ZIP also updates its build-helper/output naming, companion-PDF identity, manifest, checksums, and documentation, and preserves earlier verification files under `provenance/headered_edition_verification/`. Therefore the entire source archive is not described as a two-line-only change.

Local confirmation performed for this provenance note:

- The previous and current Vol.5.3 pairs, and the unchanged Vol.5.4 pair below, were rehashed from their supplied bytes; all six identities matched the supplied receipts.
- Both Vol.5.3 ZIPs passed CRC checks. All 71 entries in the new source archive's `SHA256SUMS.txt` matched.
- TeX bytes after `\begin{document}` were identical between the two Vol.5.3 sources; all 20 existing paths under `figures/` and `checks/` were byte-identical.
- The supplied replacement Zenodo Description differed only by the two distribution filenames.

This confirmation did **not** rerun the mathematical checks, rebuild the PDF, repeat full-page rendering, or issue a new external review. The prior header-removal report records those earlier rendering/build checks and their limits. Existing external review approvals remain approvals of the headered binaries; content-preservation evidence is not a new independent approval of the replacement binaries.

Evidence retained outside this repository (filenames identify records, not repository download links):

| Evidence | SHA-256 |
|---|---|
| `Re_Phase_Vol_5_3_Noheader_Report_2026-10-21_r1.md` | `32f7f94baedea0695f59735cd27d34502922d09830c6c99adb66b792293968f7` |
| `Re_Phase_Vol_5_3_Noheader_Receipt_2026-10-21_r1.json` | `5f5a9d545a0aae8fd1989ab40eb93949192ed2157cb117c6b185ae73413b3921` |
| `Re_Phase_Vol53_Noheader_CrossVolume_Impact_2026-10-22_r1.md` | `539ccfcf765be7325720880f00376167cacd96a41af957d98a819f0354bf2c28` |

The current source archive itself contains `HEADER_REMOVAL.md`, `provenance/remove_running_header.patch`, and the preserved historical verification records.

## 3. Vol.5.4: preserve the actual validation inputs

Vol.5.4 was checked against the headered Vol.5.3. Its source archive retains those old identities in `provenance/input_identity.json`, `verification/cross_volume_consistency.json`, `verification/input_immutability.json`, and the corresponding metadata-check/history files. They record the inputs actually used and must **not** be rewritten to suggest that the earlier checks used `noheader_r1`.

The provenance chain is:

1. Vol.5.4 was checked against the headered Vol.5.3.
2. The headered and noheader Vol.5.3 bodies, figures, computation scripts and pagination were checked for the stated preservation properties.
3. The publication candidates are now the noheader Vol.5.3 and the unchanged Vol.5.4.

This is a scoped correspondence, not binary identity or an assertion that arbitrary errors cannot exist. The Vol.5.4 metadata checker validates its bundled historical input registry; it does not fetch or authenticate the current Zenodo contents.

The unchanged Vol.5.4 pair is:

| File | Bytes | SHA-256 | MD5 |
|---|---:|---|---|
| `Re_Phase_Vol_5_4_Corrected_2026-10-21.pdf` | 535,386 | `f692f7dc4b129a3647562bdeab020db1aa6c82b894f88fcf4e0fea2c22a0aa01` | `1bb3b3d3e1cedb5b9c54150406d2c800` |
| `Re_Phase_Vol_5_4_Source_2026-10-21.zip` | 168,433 | `a0947e0d7d05206666a2f6470b7aa3a1c6e65e96f7e02adca19910c61ca80ef2` | `900113afab17a0624f9c22e4b985875a` |

No Vol.5.4 artifact or past receipt is regenerated for this change.

## 4. Vol.6.1 and the frozen baseline

The later Vol.6.1 corrective work should identify its actual inputs as Vol.5.3 `noheader_r1` and Vol.5.4 `2026-10-21`. Existing v0.4.2 manuscript/software, specs, golden snapshots, generated outputs, and historical reviews remain unchanged. The header removal neither resolves the previously identified Vol.6.1 corrections nor creates a new mathematical revision of those claims.

The earlier `Frozen_Baseline_2026-10-21_r1` remains a creation-time snapshot. This note and the noheader receipt are successor provenance; they do not silently overwrite that snapshot.

## 5. Separate the candidate change from the Zenodo execution receipt

As of this documentation checkpoint, publication remains pending and the current Zenodo draft contents have not been read back in this operation. A browser connection could not be established. No Zenodo file deletion, upload, metadata save, or Publish was performed by this operation.

The separately authorized draft replacement is limited to DOI `10.5281/zenodo.23499738`: retain a record of the old file identities, place the verified noheader PDF/ZIP, remove only the identified prior prepared pair after the new uploads are verified, and change only the two distribution filenames in the live Description. Keep the DOI, edition date, version and unrelated metadata unchanged. Do not modify Vol.5.4 or either Vol.6.1 record, and do not Publish.

Completion requires a **separate execution receipt** with actual before/after filenames and server-displayed MD5s, any downloaded SHA-256/byte results, saved Description comparison, continued draft status, and the actual time and actions. The old headered-pair MD5 PASS cannot be reused for the new pair. This provenance note alone does not certify remote replacement completion.
