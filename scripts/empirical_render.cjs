// Render generated SVGs with the standard sharp package; no network or model calls.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
async function main() {
  if (process.argv.length !== 3) throw new Error('Usage: node empirical_render.cjs FIGURE_DIRECTORY');
  const folder = path.resolve(process.argv[2]);
  for (const name of ['acceptance', 'per-run', 'cost-quality', 'coverage']) {
    await sharp(path.join(folder, name + '.svg')).png().toFile(path.join(folder, name + '.png'));
  }
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
