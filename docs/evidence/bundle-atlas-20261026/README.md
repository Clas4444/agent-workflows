# Bundle atlas rendering evidence — 2026-10-26

The atlas explains existing bundle workflows. It does not add skills, change
membership, execute a model or prove that the illustrated behavior occurs in
every host. Sources: `skill-bundles.json`, canonical skill instructions, and
`docs/assets/bundles/workflows.json` for the reviewed explanations.

[render-check.json](render-check.json) records a local headless Chrome render of
all fourteen actual SVG files, their SHA256 identities, text-node counts and
geometry checks. The checks reject text outside the canvas, outside step or
recommendation cards, and overlapping text boxes. PNG previews and a contact
sheet were inspected locally; private paths and disposable rendering files stay
under ignored `.loop/`. This is not a live GitHub renderer check.

The [published index](published-hashes.json) checks these reviewed record bytes,
not authorship or execution attestation. The
[session report](../../testing/BUNDLE-ATLAS-2026-10-26.md) distinguishes rendering,
deterministic generation/tests, release CI and unexecuted behavioral coverage.
