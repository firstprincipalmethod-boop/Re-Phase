# Fixed table-reproduction inputs (not new executions)

The Python generator and all JSON files here are exact copies identified in
`../phase3-manifest.json`. The source package's MIT exception applies to these
scripts and machine-readable software data. No manuscript text, figures, PDF
or authored table files are included.

`verification/` contains **past package observations** bound by the unchanged
SYNC_CONTRACT. Do not read them as phase-3 results or update their status fields.
The repository wrapper assembles a temporary standalone-style table directory,
copies fresh repository-generated outputs there, runs build_tables.py, and
compares all eight generated-file hashes with the fixed manuscript source.
The generated macros intentionally reproduce the original package's evidence
counts and contract digest. New runtime observations are stored separately in
the caller's external replay report.
