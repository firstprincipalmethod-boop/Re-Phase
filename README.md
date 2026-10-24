# Re-Phase

**Re-Phase** (*Relative Phase Reconstruction*) is a relation-first diagnostic framework for reconstructing compatible worlds under partial observation.

It turns fibers, projections, path lifts, bridge obstructions, recoverability guards, forgetting maps, and selector constraints into finite objects that can be inspected, tested, and reproduced.

## Current Focus

- DOI series index and conceptual reading guide
- Vol.5.3 corrected edition 2026-10-21 (`noheader_r1`) — published on Zenodo: [10.5281/zenodo.23499738](https://doi.org/10.5281/zenodo.23499738)
- Vol.5.4 corrected edition 2026-10-21 — published on Zenodo: [10.5281/zenodo.23499819](https://doi.org/10.5281/zenodo.23499819)
- Vol.6.1 v0.4.2 — historical archived release
- Vol.6.1 corrected 2026-10-23 implementation — present in this tree; paired Zenodo publication pending

See the [2026-10-24 publication/integration checkpoint](docs/publication-status-2026-10-24.md) for current correction boundaries and the [2026-10-22 record](docs/publication-status-2026-10-22.md) for frozen Vol.5.3/Vol.5.4 publication evidence. The [pre-publication checkpoint](docs/prepublication-status-2026-10-21.md) is retained as history, not current publication status.

## Archive

Zenodo fixed records are authoritative for published releases. GitHub is the public navigation, living documentation, and development repository; it does not claim to contain byte-identical publication PDF/ZIP copies unless explicitly stated.

See [docs/series.md](docs/series.md) for the complete publication chronology and DOI registry.

## Documentation

- **[docs/series.md](docs/series.md)** — Publication chronology and Zenodo DOI registry
- **[docs/reading-guide.md](docs/reading-guide.md)** — Conceptual reading paths (not publication order)
- **[living-index.md](living-index.md)** — Cross-volume index and references
- **[docs/publication-status-2026-10-22.md](docs/publication-status-2026-10-22.md)** — Vol.5.3/Vol.5.4 published artifacts, evidence scope, and retained history
- **[ROADMAP.md](ROADMAP.md)** — Future directions
- **[CHANGELOG.md](CHANGELOG.md)** — Change history

## Repository Structure

- **docs/** — Labels, milestones, reading guides, series index, publication status, and historical checkpoints
- **witnesses/** — corrected Vol.6.1 harness, repository replay, and explicitly separated historical documentation
- **.github/ISSUE_TEMPLATE/** — Issue templates for structured collaboration
- **.github/PULL_REQUEST_TEMPLATE.md** — PR review template

## GitHub Workflow

- **Issues**: Track definitions, notation changes, proofs, examples, cross-volume consistency, and release preparation. See [docs/labels.md](docs/labels.md) for label taxonomy.
- **Pull Requests**: Submit changes for review. Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
- **Milestones**: Organize issues into major development phases. See [docs/milestones.md](docs/milestones.md).
- **Discussions**: [Coming soon]

## License

Except for the explicitly listed MIT software/data materials below, non-code materials (text, figures, notation, documentation, examples) are licensed under [CC BY-NC 4.0](LICENSE.md).

All code, scripts, and executable implementations, including the Vol.6.1 witness harness, are licensed under the [MIT License](LICENSE-CODE.md). Imported Vol.6.1 machine-readable specifications, golden snapshots, results and explicitly listed operational support also retain MIT; see [LICENSE-SOFTWARE.md](witnesses/vol6_1/LICENSE-SOFTWARE.md). See [LICENSE.md](LICENSE.md) for the policy and this scoped exception.
