# Data contracts

`manifest-v1.schema.json` describes the existing repository manifest using
JSON Schema Draft 2020-12. The schema version describes the data shape, not the
skill release number. It permits existing additional metadata and preserves the
ordered native roots. Existing manifests need no new fields or migration.

Production validation remains the dependency-free Python reader in
`scripts/validation/manifest.py`. Contract parity tests cover roots, required
fields, name constraints and representative valid/invalid mutations; they are
not a general JSON Schema validator or proof of every possible input. Consumers
using a JSON Schema engine should select Draft 2020-12 explicitly.

Runner state and runtime evidence retain their current formats. They do not
yet have published schemas; adding those requires characterizing error-path
and historical records before freezing a compatibility contract.
