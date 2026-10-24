# Vol.6.1 — Post-publication documentation checkpoint, 2026-10-24

## Published pair and repository integration

The corrected Vol.6.1 manuscript and software are published on Zenodo.
The owner confirmed software publication followed by manuscript publication.
The edition, Zenodo Publication date and Version remain **2026-10-23**;
this documentation checkpoint is **2026-10-24**. Neither date field is an
independently captured Publish-click timestamp.

| Object | Published version DOI | License | State |
|---|---|---|---|
| Manuscript | [10.5281/zenodo.23499925](https://doi.org/10.5281/zenodo.23499925) | CC BY-NC 4.0 | Published corrected edition 2026-10-23 |
| Software / witness harness | [10.5281/zenodo.23499964](https://doi.org/10.5281/zenodo.23499964) | MIT | Published corrected edition 2026-10-23 |

The corrected implementation was merged into main via
[PR #29](https://github.com/firstprincipalmethod-boop/Re-Phase/pull/29) on
**2026-10-24 12:57:57 JST** (03:57:57 UTC). Fresh GitHub reads confirmed:

- Main / PR #29 merge commit: `854c3dda22830c7cde3ab51efc9a5a8440b1cc33`.
- Root tree: `e514da572656f2ed49f5ae55515983e73d567095`.
- Unchanged harness tree: `d090e14611146294f941439ee8e8af49a28701e0`.

This documentation change starts from that main commit and is submitted on
`docs/vol61-postpublication-2026-10-24` through a separate PR. It does not itself
merge or push to main; PR #29 integration and this documentation PR are distinct.

## Publication evidence and limits

Owner confirmation in the publication handoff is supported by fresh, public
DataCite DOI metadata retrieved on 2026-10-24:

| Public metadata source | State / active | Version / Issued | License ID | Reciprocal relation |
|---|---|---|---|---|
| [Manuscript DataCite record](https://api.datacite.org/dois/10.5281/zenodo.23499925) | `findable` / `true` | 2026-10-23 / 2026-10-23 | `cc-by-nc-4.0` | `IsSupplementedBy` software DOI 23499964 |
| [Software DataCite record](https://api.datacite.org/dois/10.5281/zenodo.23499964) | `findable` / `true` | 2026-10-23 / 2026-10-23 | `mit` | `IsSupplementTo` manuscript DOI 23499925 |

DataCite records the software DOI registration at `2026-10-24T05:16:54.000Z`
and manuscript registration at `2026-10-24T05:22:00.000Z`. These are DOI
registration timestamps, not measured Publish-click times or file creation
timestamps. The manuscript title is *Re-Phase Vol.6.1: A Finite Witness Harness
for Vol.5.3 and Vol.5.4*; the software title uses an em dash after Vol.6.1.

Direct Zenodo page/API retrieval was unavailable (HTTP 403 on direct requests).
This sync therefore claims fresh **DOI metadata verification**, supported by
owner publication confirmation, not fresh Zenodo file-byte verification.
No PDF/ZIP was downloaded, rebuilt or recompressed. Remote exact bytes and
SHA-256 are **NOT_MEASURED** in this operation; DataCite metadata does not
establish artifact-byte identity. The earlier final gate explicitly recorded
both records as unpublished, and is retained as pre-publication evidence.

## Retained fixed artifact identities

The following table is preserved from the PR #29 checkpoint. Byte counts and
SHA-256 identify the previously fixed local artifacts; MD5 values are from
the earlier Zenodo UI receipt. They are not relabelled as fresh remote
measurements. Same-named earlier candidates can have different bytes.

| Artifact | bytes | SHA-256 | displayed MD5 |
|---|---:|---|---|
| `Re_Phase_Vol_6_1_Manuscript_2026-10-23.pdf` | 505665 | `37aee8f308b5c57c8843f0482f079bbaaf44f5b3c4b47d4bb825587fbcd8e820` | `1d627781b2312b8fb029924e6bdc8db5` |
| `Re_Phase_Vol_6_1_Manuscript_Source_2026-10-23.zip` | 491252 | `a98cf7b51d5908632c65b14006211c3a404d409a57961f3e8a802b34c7a56130` | `4cc9004ca6bba4504849586265656076` |
| `Re_Phase_Vol_6_1_Software_2026-10-23.zip` | 523545 | `48abc2ae97e1cf0ea5089f7e9610dfef0d4b6c14194f41e85a8660c4086c181e` | `3fc8f4f2aa5db343efb588a20507cb81` |

## Retained history, sources and licenses

- Historical v0.4.2 manuscript DOI [21220080](https://doi.org/10.5281/zenodo.21220080) and software DOI [21220093](https://doi.org/10.5281/zenodo.21220093) remain archived history; no historical title or record is rewritten.
- DataCite identifies the manuscript all-versions DOI as `10.5281/zenodo.21220079` and software all-versions DOI as `10.5281/zenodo.21220092`. The version-specific corrected DOIs above remain the current reading/download targets.
- Fixed source editions remain Vol.5.3 corrected 2026-10-21 noheader-r1, DOI [23499738](https://doi.org/10.5281/zenodo.23499738), and Vol.5.4 corrected 2026-10-21, DOI [23499819](https://doi.org/10.5281/zenodo.23499819). Their [publication evidence and files](publication-status-2026-10-22.md) are unchanged.
- Manuscript text, figures and PDF retain CC BY-NC 4.0. Software and declared build-code/machine-readable-data exceptions retain MIT; repository license files are unchanged.
- Current golden paths already contain the 2026-10-23 snapshots imported by PR #29. Historical recovery remains at commit `cb592ad34ed6aa8db24fea02595793289919b6cf` or the v0.4.2 Zenodo archives; see [G1](../witnesses/vol6_1/CORRECTION_STATUS.md#current-golden-paths-and-historical-recovery-g1).
- The complete [2026-10-21](prepublication-status-2026-10-21.md), [2026-10-22](publication-status-2026-10-22.md), and [earlier 2026-10-24](publication-status-2026-10-24.md) checkpoint bodies remain intact beneath later-status notices. Their pending statements describe those earlier observations.

## Verification scope for this documentation change

Review is limited to publication/navigation consistency, DOI/license/version
agreement, historical preservation, relative links and the exact Markdown
allowlist. Git blob/tree comparison protects every path outside that allowlist,
including Toy code, harness, specs, goldens, generated results, schema, contracts,
source maps, stored verification evidence, distribution files and licenses.

No harness execution, new Windows/Linux replay, PDF build, mathematical proof
audit or external scientific review is performed. Earlier finite-suite results
retain their original targets and environments; publication does not transfer
old approval to new bytes, establish arbitrary-domain proof, provide institutional
certification, synthesize general controllers or demonstrate a performance advantage.
Zenodo records, Git tags and GitHub Releases are not changed by this sync.
