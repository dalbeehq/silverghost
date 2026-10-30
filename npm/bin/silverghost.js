#!/usr/bin/env node
// npx silverghost add <이름...> | list
// 레지스트리는 기본 https://thedalbee.com/silverghost, --registry <주소나 폴더>로 바꾼다.
import {mkdir, readFile, writeFile, access} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';

const HELP = `Silver Ghost: motion components made by AI, curated by a human.

  npx silverghost list
  npx silverghost add <name...> [--dir <folder>] [--force]

Options
  --registry <url|folder>  default https://thedalbee.com/silverghost
  --dir <folder>           where files go, default: current folder
  --force                  overwrite existing files`;

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const flag = k => { const i = args.indexOf(k); if (i < 0) return false; args.splice(i, 1); return true; };
const registry = (opt('--registry', process.env.SILVERGHOST_REGISTRY || 'https://thedalbee.com/silverghost')).replace(/\/$/, '');
const dir = resolve(opt('--dir', '.'));
const force = flag('--force');
const [cmd, ...names] = args;

async function get(path) {
  if (/^https?:/.test(registry)) {
    const res = await fetch(`${registry}/${path}`);
    if (!res.ok) throw new Error(`${res.status} ${registry}/${path}`);
    return res.json();
  }
  return JSON.parse(await readFile(`${registry}/${path}`, 'utf8'));
}
const exists = p => access(p).then(() => true, () => false);

async function add(name) {
  const item = await get(`r/${encodeURIComponent(name)}.json`).catch(() => { throw new Error(`unknown item "${name}". See: npx silverghost list`); });
  for (const f of item.files) {
    const out = resolve(dir, f.target || f.path);
    if (!out.startsWith(dir)) throw new Error(`refusing path outside --dir: ${f.target}`);
    if (!force && await exists(out)) { console.log(`skip ${out} (exists, use --force)`); continue; }
    await mkdir(dirname(out), {recursive: true});
    await writeFile(out, f.content);
    console.log(`added ${out}`);
  }
}

try {
  if (cmd === 'list') {
    const reg = await get('registry.json');
    for (const it of reg.items) console.log(`${it.name.padEnd(24)} ${it.title}`);
  } else if (cmd === 'add' && names.length) {
    for (const n of names) await add(n);
  } else {
    console.log(HELP);
  }
} catch (e) {
  console.error(`silverghost: ${e.message}`);
  process.exit(1);
}
