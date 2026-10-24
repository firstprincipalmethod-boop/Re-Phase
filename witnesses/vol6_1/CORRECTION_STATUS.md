# Vol.6.1 publication / integration status — 2026-10-24

The current cross-volume reference is the
[Vol.6.1 post-publication record](../../docs/vol61-publication-sync-2026-10-24.md).
The [earlier integration checkpoint](../../docs/publication-status-2026-10-24.md),
[2026-10-22 record](../../docs/publication-status-2026-10-22.md), and
[2026-10-21 pre-publication page](../../docs/prepublication-status-2026-10-21.md)
retain their original checkpoint bodies and evidence scope.

## Current source tree and published pair

The corrected 2026-10-23 implementation was merged through
[PR #29](https://github.com/firstprincipalmethod-boop/Re-Phase/pull/29) on
2026-10-24 at 12:57:57 JST, commit `854c3dda22830c7cde3ab51efc9a5a8440b1cc33`.
Phase-2 import commit `8411834aa7ddf82ae0792740bdc7e98d4d73008a` and the
phase-3 repository replay remain separately identified historical work.
The 59 harness files, Toy D helper and original SYNC_CONTRACT are unchanged
by this documentation sync. No new runtime validation is claimed.

| Paired artifact | Published version DOI | License | Edition / Version |
|---|---|---|---|
| Manuscript | [10.5281/zenodo.23499925](https://doi.org/10.5281/zenodo.23499925) | CC BY-NC 4.0 | 2026-10-23 |
| Software | [10.5281/zenodo.23499964](https://doi.org/10.5281/zenodo.23499964) | MIT | 2026-10-23 |

The owner confirmed software publication followed by manuscript publication.
Fresh public DataCite metadata confirms both DOIs as active/findable, with
matching versions, licenses and reciprocal supplement relations. Direct
Zenodo retrieval was unavailable; remote PDF/ZIP bytes and SHA-256 were not
remeasured. See the linked publication record for the exact evidence boundary.
The earlier unpublished-draft receipts remain historical; Vol.5.3 and Vol.5.4
retain their already-recorded published status and frozen files.

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

## Remaining boundaries

C2 is addressed by the current navigation above. R4-03 is addressed by recovery
through a fixed commit/DOI/hash rather than an unavailable historical tag.
G1 is addressed explicitly above and in README. Old README/status bytes are
preserved in `historical/`; the old Zenodo description remains unchanged.

The original package contract and historical verification records retain their
creation-time claims; publication does not retroactively change external-review
or platform statuses. This documentation sync performs no harness replay,
golden refresh, original artifact rebuild, license redefinition, Zenodo edit
or Publish, tag or Release operation.
Temporary transfer branches are outside this implementation tree; cleanup is
a separate owner decision, not part of this PR's verification.
