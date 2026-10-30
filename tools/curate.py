# 달비가 항목마다 남김과 뺌을 고르는 화면. 고른 값은 items/<이름>/item.json의 curated 칸에 바로 적힌다.
# build.py는 curated.keep이 true인 항목만 내보낸다.
# 사용: python3 tools/curate.py [포트=4331] 뒤 http://localhost:4331 을 연다.
import json, sys, datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / 'items'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4331

PAGE = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Silver Ghost 고르기</title><style>
:root{--bg:#0f1316;--fg:#e8edf0;--mut:#8a969e;--line:#26313a;--keep:#62c1db;--drop:#d0675b}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,"Apple SD Gothic Neo",sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
header b{font-size:17px}#sum{color:var(--mut)}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);gap:16px;padding:16px}
@media(max-width:800px){main{grid-template-columns:1fr}}
#list{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;align-content:start}
.c{border:2px solid var(--line);background:#141a1e;cursor:pointer;text-align:left;color:inherit;padding:0;font:inherit}
.c[aria-current=true]{border-color:var(--fg)}.c.keep{border-color:var(--keep)}.c.drop{border-color:var(--drop)}
.c img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}.c div{padding:6px 8px}.c small{color:var(--mut)}
.c .st{float:right;font-weight:600}.c.keep .st{color:var(--keep)}.c.drop .st{color:var(--drop)}
#view{position:sticky;top:64px;align-self:start}
#view iframe{width:100%;aspect-ratio:16/9;border:1px solid var(--line);background:#000;display:block}
.tabs{display:flex;gap:6px;margin:8px 0}.tabs button,.act button{font:inherit;padding:8px 14px;border:1px solid var(--line);background:#141a1e;color:var(--fg);cursor:pointer}
.tabs button[aria-pressed=true]{border-color:var(--fg)}
.act{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px}
.act .k{border-color:var(--keep);color:var(--keep)}.act .d{border-color:var(--drop);color:var(--drop)}
#note{flex:1;min-width:200px;padding:8px;background:#141a1e;border:1px solid var(--line);color:var(--fg);font:inherit}
#why{color:var(--mut);margin:4px 0}
</style></head><body>
<header><b>Silver Ghost 고르기</b><span id="sum"></span><span style="color:var(--mut)">키보드: K 남김, D 뺌, 화살표 이동</span></header>
<main><div id="list"></div><section id="view"><h2 id="t" style="margin:0 0 4px;font-size:18px"></h2><p id="desc" style="margin:0;color:var(--mut)"></p>
<div class="tabs"><button id="tk" aria-pressed="true">남긴 판</button><button id="tr" aria-pressed="false">버린 판</button></div>
<iframe id="f" title="미리보기"></iframe><p id="why"></p>
<div class="act"><button class="k" id="bk">남김 (K)</button><button class="d" id="bd">뺌 (D)</button><input id="note" placeholder="한 줄 메모 (선택)"></div></section></main>
<script>
let items=[],i=0;
const $=s=>document.querySelector(s);
async function load(){items=await (await fetch('/api/items')).json();draw();show(0)}
function st(o){return o.curated?(o.curated.keep?'keep':'drop'):''}
function draw(){
  $('#list').innerHTML=items.map((o,k)=>`<button class="c ${st(o)}" data-k="${k}" aria-current="${k===i}"><img src="/items/${o.name}/poster.jpg" alt=""><div><span class="st">${o.curated?(o.curated.keep?'남김':'뺌'):''}</span>${o.title}<br><small>${o.name}</small></div></button>`).join('');
  const n=items.filter(o=>o.curated&&o.curated.keep).length,d=items.filter(o=>o.curated&&!o.curated.keep).length;
  $('#sum').textContent=`남김 ${n}, 뺌 ${d}, 안 고름 ${items.length-n-d}`;
}
function show(k,rej){i=(k+items.length)%items.length;const o=items[i];
  $('#t').textContent=o.title;$('#desc').textContent=o.description;
  $('#f').src=rej?`/items/${o.name}/${o.rejected[0].file}`:`/items/${o.name}/${o.name}.html`;
  $('#why').textContent=rej?'버린 이유: '+o.rejected[0].why:'';
  $('#tk').setAttribute('aria-pressed',!rej);$('#tr').setAttribute('aria-pressed',!!rej);
  $('#note').value=o.curated&&o.curated.note||'';
  document.querySelectorAll('.c').forEach(b=>b.setAttribute('aria-current',+b.dataset.k===i));}
async function pick(keep){const o=items[i];
  const r=await fetch('/api/pick',{method:'POST',body:JSON.stringify({name:o.name,keep,note:$('#note').value})});
  o.curated=await r.json();draw();show(i+1)}
$('#list').onclick=e=>{const b=e.target.closest('.c');if(b)show(+b.dataset.k)};
$('#tk').onclick=()=>show(i,false);$('#tr').onclick=()=>show(i,true);
$('#bk').onclick=()=>pick(true);$('#bd').onclick=()=>pick(false);
addEventListener('keydown',e=>{if(e.target.id==='note')return;
  if(e.key==='k'||e.key==='K')pick(true);else if(e.key==='d'||e.key==='D')pick(false);
  else if(e.key==='ArrowRight'||e.key==='ArrowDown')show(i+1);else if(e.key==='ArrowLeft'||e.key==='ArrowUp')show(i-1)});
load();
</script></body></html>'''


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass

    def send_json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            body = PAGE.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/api/items':
            self.send_json([json.loads((d / 'item.json').read_text()) for d in sorted(ITEMS.iterdir()) if (d / 'item.json').exists()])
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != '/api/pick':
            self.send_error(404)
            return
        req = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        path = ITEMS / req['name'] / 'item.json'
        if path.parent.parent != ITEMS or not path.exists():
            self.send_error(400)
            return
        item = json.loads(path.read_text())
        item['curated'] = {'keep': bool(req['keep']), 'by': 'dalbee', 'at': datetime.date.today().isoformat(), 'note': req.get('note', '').strip()}
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n')
        self.send_json(item['curated'])


print(f'http://localhost:{PORT}')
ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
