import { copyFileSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const output = path.resolve('dist/client');
const repositoryBase = '/EVOLVE-Frame';
const textExtensions = new Set(['.css', '.html', '.js', '.json']);

function rewrite(directory) {
  for (const entry of readdirSync(directory)) {
    const file = path.join(directory, entry);
    if (statSync(file).isDirectory()) {
      rewrite(file);
      continue;
    }
    if (!textExtensions.has(path.extname(file))) continue;
    const source = readFileSync(file, 'utf8');
    const updated = source.replaceAll('/_next/', `${repositoryBase}/_next/`);
    if (updated !== source) writeFileSync(file, updated);
  }
}

rewrite(output);
copyFileSync(path.join(output, 'index.html'), path.join(output, '404.html'));
writeFileSync(path.join(output, '.nojekyll'), '');
