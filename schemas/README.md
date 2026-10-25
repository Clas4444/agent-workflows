# Data contracts

Need-based installation has a version-1 registry in `skill-bundles.json`, enforced
by `scripts/skill_bundles.py` without third-party dependencies. Each named bundle
has a purpose and unique manifest skill names. Bundles may overlap; they are not
the disjoint functional group partition or a runtime dispatcher. Explicit bundle
unions resolve to manifest order before the sync engine runs. No JSON Schema
compliance beyond the documented reader is claimed for this registry.

The opt-in acceptance CLI has a separately documented version-1 contract in
[ACCEPTANCE-GATE.md](../docs/ACCEPTANCE-GATE.md), enforced by its dependency-free
Python reader. It does not change the repository manifest or runner state and
does not yet have a published JSON Schema.

`manifest-v1.schema.json` describes the existing repository manifest using
JSON Schema Draft 2020-12. The schema version describes the data shape, not the
skill release number. It permits existing additional metadata and preserves the
ordered native roots. Existing manifests need no new fields or migration.

Production validation remains the dependency-free Python reader in
`scripts/validation/manifest.py`. Contract parity tests cover roots, required
fields, name constraints and representative valid/invalid mutations; they are
not a general JSON Schema validator or proof of every possible input. Consumers
using a JSON Schema engine should select Draft 2020-12 explicitly.

Version strings now enforce SemVer core/prerelease/build syntax rather than
merely three digit groups. Version and skill-name patterns use explicit
end-of-input checks to avoid regex-engine differences around a final newline.
The 2026-10-25 campaign compared Python and Node regex behavior; a complete
third-party JSON Schema engine was NOT_RUN. See the
[hardening evidence](../docs/UPDATE-30M-2026-10-25.md).

Runner state and runtime evidence retain their current formats. They do not
yet have published schemas; adding those requires characterizing error-path
and historical records before freezing a compatibility contract.

## Managed resources (1.9)

The optional manifest field `resource_manifest` names `skill-resources.json`. Version 1 maps skill names to safe relative supporting-file paths; SKILL.md and the two existing runners remain implicit. Unregistered source resources, missing declared registries and divergent native copies fail validation. Legacy minimal sources without extra resources remain supported. Individual selection reads only the skill inventory when no bundle is requested.
