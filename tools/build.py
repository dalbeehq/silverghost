# items/<이름>/ 폴더들로 배포 폴더(dist/)를 만든다.
#   dist/registry.json      shadcn registry 목록
#   dist/r/<이름>.json       shadcn registry-item, 파일 내용 포함. `npx silverghost add`와 `npx shadcn add`가 받는다
#   dist/items/<이름>/...    사이트 카드가 쓰는 본판, 버린 판, 포스터
#   dist/index.json         사이트 카드 목록
# 사람이 tools/curate.py에서 남김으로 고른 항목(item.json curated.keep)만 내보낸다.
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS, DIST = ROOT / 'items', ROOT / 'dist'
HOME = 'https://thedalbee.com/silverghost'
REQUIRED = ['name', 'title', 'description', 'kind', 'credit', 'license', 'made', 'rejected']

# <silverghost-이름> 태그. 단독 페이지를 그림자 DOM 속 iframe에 넣어서 페이지 CSS와 서로 섞이지 않는다.
ELEMENT = """// Silver Ghost: __NAME__. Usage: import './__NAME__.js' then <silverghost-__NAME__></silverghost-__NAME__>
const HTML = __HTML__;
class SilverGhostItem extends HTMLElement {
  connectedCallback() {
    if (this.shadowRoot) return;
    const root = this.attachShadow({ mode: 'open' });
    root.innerHTML = '<style>:host{display:block;position:relative;aspect-ratio:16/9}iframe{position:absolute;inset:0;width:100%;height:100%;border:0;display:block}</style>';
    const frame = document.createElement('iframe');
    frame.title = this.getAttribute('label') || '__NAME__';
    frame.srcdoc = HTML;
    root.append(frame);
  }
}
if (!customElements.get('silverghost-__NAME__')) customElements.define('silverghost-__NAME__', SilverGhostItem);
"""

def load(d):
    item = json.loads((d / 'item.json').read_text())
    missing = [k for k in REQUIRED if k not in item]
    if missing or item['name'] != d.name:
        sys.exit(f'{d.name}: item.json 칸 누락 {missing} 또는 이름 불일치')
    for f in [f'{d.name}.html', 'poster.jpg'] + [x for r in item['rejected'] for x in (r['file'], r['poster'])]:
        if not (d / f).exists():
            sys.exit(f'{d.name}: 파일 없음 {f}')
    if not item['rejected']:
        sys.exit(f'{d.name}: 버린 판이 없다. 공개 카드는 버린 판이 1개 이상이어야 한다')
    return item

if DIST.exists():
    shutil.rmtree(DIST)
(DIST / 'r').mkdir(parents=True)
cards, reg = [], []
skipped = []
for d in sorted(p for p in ITEMS.iterdir() if p.is_dir()):
    item = load(d)
    if not item.get('curated', {}).get('keep'):
        skipped.append(d.name)
        continue
    n = item['name']
    html = (d / f'{n}.html').read_text()
    # 받는 파일은 둘이다. <이름>.html은 그대로 여는 단독 페이지, <이름>.js는 어느 페이지에나 끼우는 태그 <silverghost-이름>이다.
    files = {f'silverghost/{n}.html': html, f'silverghost/{n}.js': ELEMENT.replace('__NAME__', n).replace('__HTML__', json.dumps(html, ensure_ascii=False))}
    entry = {'name': n, 'type': 'registry:file', 'title': item['title'], 'description': item['description'],
             'files': [{'path': t, 'type': 'registry:file', 'target': t} for t in files]}
    reg.append(entry)
    full = dict(entry, **{'$schema': 'https://ui.shadcn.com/schema/registry-item.json'})
    full['files'] = [dict(f, content=files[f['path']]) for f in entry['files']]
    (DIST / 'r' / f'{n}.json').write_text(json.dumps(full, ensure_ascii=False))
    shutil.copytree(d, DIST / 'items' / n, ignore=shutil.ignore_patterns('item.json'))
    # 사이트에 올리는 사본만 검색에서 뺀다. add로 받는 사본(r/<이름>.json)은 원본 그대로다.
    for page in (DIST / 'items' / n).rglob('*.html'):
        html = page.read_text()
        page.write_text(html.replace('<head>', '<head>\n<meta name="robots" content="noindex">', 1))
    cards.append({k: item[k] for k in ['name', 'title', 'description', 'kind', 'credit', 'license', 'made', 'rejected']}
                 | {'title_ko': item.get('title_ko', ''), 'deps': item.get('deps', []), 'html': f'items/{n}/{n}.html', 'poster': f'items/{n}/poster.jpg',
                    'add': f'npx silverghost add {n}'})
(DIST / 'registry.json').write_text(json.dumps({'$schema': 'https://ui.shadcn.com/schema/registry.json',
    'name': 'silverghost', 'homepage': HOME, 'items': reg}, ensure_ascii=False, indent=2))
(DIST / 'index.json').write_text(json.dumps(cards, ensure_ascii=False, indent=2))
# 사이트 첫 화면 스크롤 장면의 재료: 점묘 점 두 벌과 고르기 숫자
(DIST / 'story').mkdir()
for story, src in [('car', 'silver-ghost-1907'), ('whale', 'humpback-side'), ('plane', 'plane-side'), ('f1', 'f1-side')]:
    shutil.copy(ROOT / f'cases/stipple/{src}.points.json', DIST / f'story/{story}.json')
(DIST / 'story/stats.json').write_text(json.dumps({'made': len(cards) + len(skipped), 'kept': len(cards), 'dropped': len(skipped),
    'rejected': sum(len(c['rejected']) for c in cards)}))
print(f'{len(cards)} items -> {DIST}. 사람이 남김으로 고르지 않아 뺀 것 {len(skipped)}개: {" ".join(skipped)}')
if not cards:
    sys.exit('남김으로 고른 항목이 0개다. tools/curate.py로 먼저 고른다')
