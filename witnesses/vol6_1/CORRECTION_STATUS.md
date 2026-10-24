# Vol.6.1 correction / integration status — 2026-10-24

The current cross-volume reference is the
[2026-10-24 publication and integration checkpoint](../../docs/publication-status-2026-10-24.md).
The [2026-10-22 record](../../docs/publication-status-2026-10-22.md) remains the
frozen Vol.5.3/Vol.5.4 publication evidence; the
[2026-10-21 pre-publication page](../../docs/prepublication-status-2026-10-21.md)
is historical, not the current overall status (C2).

## Current source tree

Phase 2 imported the fixed 2026-10-23 software at commit `8411834aa7ddf82ae0792740bdc7e98d4d73008a`.
Phase 3 synchronizes documentation and supplies a repository-layout replay.
The 59 harness files, Toy D helper and original SYNC_CONTRACT remain unchanged
from phase 2. Runtime success must be supported by the phase-3 report and
corresponding action/job outcome, not inferred from this status page.
PR review and main merge are phase 4; this checkpoint does not claim either.

| Paired artifact | DOI | License | Zenodo checkpoint |
|---|---|---|---|
| Manuscript | 10.5281/zenodo.23499925 | CC BY-NC 4.0 | publication pending |
| Software | 10.5281/zenodo.23499964 | MIT | publication pending |

The supplied Keywords receipt observed both drafts unpublished on
2026-10-24 at 00:58:16 JST. This integration does not re-read or mutate Zenodo,
and does not infer publication from its date field. Vol.5.3 and Vol.5.4 retain
their already-recorded published status and frozen files.

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
creation-time claims; a new repository replay does not retroactively change
external-review or platform statuses. No golden refresh, original artifact
rebuild, license redefinition, Zenodo Publish, tag or Release is performed.
Temporary transfer branches are outside this implementation tree; cleanup is
a separate owner decision, not part of this PR's verification.
