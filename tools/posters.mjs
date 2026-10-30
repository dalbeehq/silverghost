// poster.jpg가 없는 본판과 버린 판을 헤드리스로 열어 4.5초 뒤 화면을 찍는다. 콘솔 오류가 있으면 실패로 끝난다.
import {createRequire} from 'module';
import {existsSync, readdirSync, readFileSync} from 'fs';
import {execFileSync} from 'child_process';
import {fileURLToPath} from 'url';
const require=createRequire(process.env.PUPPETEER_FROM||`${process.env.HOME}/ws/tools/hyperframes-0.8.174/`);
const puppeteer=require('puppeteer-core');
const exe=process.env.CHROME||`${process.env.HOME}/ws/tools/cache/pw-browsers/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell`;
const ITEMS=fileURLToPath(new URL('../items',import.meta.url));
const jobs=[];
for(const name of readdirSync(ITEMS)){
  const item=JSON.parse(readFileSync(`${ITEMS}/${name}/item.json`,'utf8'));
  jobs.push([`${ITEMS}/${name}/${name}.html`,`${ITEMS}/${name}/poster.jpg`]);
  for(const r of item.rejected) jobs.push([`${ITEMS}/${name}/${r.file}`,`${ITEMS}/${name}/${r.poster}`]);
}
const todo=jobs.filter(([,out])=>!existsSync(out));
const b=await puppeteer.launch({executablePath:exe,headless:true,args:['--use-angle=metal','--enable-gpu','--ignore-gpu-blocklist','--mute-audio','--no-sandbox']});
let bad=0;
for(const [html,out] of todo){
  const p=await b.newPage();await p.setViewport({width:1280,height:720});
  const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('file://'+html);await new Promise(r=>setTimeout(r,4500));
  const png=out.replace(/\.jpg$/,'.png');await p.screenshot({path:png});await p.close();
  execFileSync('/opt/homebrew/bin/magick',[png,'-resize','760x','-quality','70',out]);execFileSync('rm',[png]);
  if(errs.length){bad++;console.log('ERR',html,errs)}else console.log('ok',out.replace(ITEMS+'/',''));
}
await b.close();
if(bad)process.exit(1);
