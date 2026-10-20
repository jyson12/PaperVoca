"""
build_dashboard.py (v2)
vocabulary.json + CSS + JS를 모두 index.html 단일 파일에 인라인 삽입
→ 외부 파일 없이 더블클릭만으로 실행 가능
"""
import json
from pathlib import Path

DATA_FILE = Path("data/vocabulary.json")
WEB_DIR   = Path("web")
WEB_DIR.mkdir(exist_ok=True)
OUT_FILE  = WEB_DIR / "index.html"

data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
vocab_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

meta = data.get("meta", {})
word_count = meta.get("word_count", len(data["words"]))
paper_count = meta.get("paper_count", "?")
generated_at = meta.get("generated_at", "2026-06-03")

# 품사 목록
pos_set = sorted(set(w.get("pos", "") for w in data["words"]) - {""})
POS_KO_MAP = {
    "noun": "명사", "verb": "동사", "adjective": "형용사",
    "adverb": "부사", "preposition": "전치사", "pronoun": "대명사",
    "conjunction": "접속사", "determiner": "한정사",
}
pos_options = "\n".join(
    f'<option value="{p}">{POS_KO_MAP.get(p, p)}</option>'
    for p in pos_set
)

css = r"""
:root{--bg:#f0f4f8;--surface:#fff;--surface2:#f8fafc;--border:#e2e8f0;--primary:#6366f1;--primary-light:#eef2ff;--primary-dark:#4f46e5;--text:#1e293b;--muted:#64748b;--light:#94a3b8;--shadow:0 1px 3px rgba(0,0,0,.08);--shadow-lg:0 4px 16px rgba(0,0,0,.1);--r:12px;--rs:8px}
[data-theme=dark]{--bg:#0f172a;--surface:#1e293b;--surface2:#0f172a;--border:#334155;--primary:#818cf8;--primary-light:#1e1b4b;--primary-dark:#a5b4fc;--text:#f1f5f9;--muted:#94a3b8;--light:#64748b;--shadow:0 1px 3px rgba(0,0,0,.3);--shadow-lg:0 4px 16px rgba(0,0,0,.4)}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
header{background:var(--primary);color:#fff;padding:18px 24px;display:flex;align-items:center;justify-content:space-between;gap:12px;position:sticky;top:0;z-index:100;box-shadow:var(--shadow-lg)}
.hl h1{font-size:1.35rem;font-weight:700}
.hl p{font-size:.8rem;opacity:.8;margin-top:2px}
#themeBtn{background:rgba(255,255,255,.2);border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:1.1rem;color:#fff;display:flex;align-items:center;justify-content:center}
#themeBtn:hover{background:rgba(255,255,255,.35)}
.controls{background:var(--surface);border-bottom:1px solid var(--border);padding:14px 24px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;position:sticky;top:64px;z-index:90;box-shadow:var(--shadow)}
.sw{position:relative;flex:1;min-width:180px}
.sw input{width:100%;padding:8px 12px 8px 34px;border:1px solid var(--border);border-radius:var(--rs);background:var(--surface2);color:var(--text);font-size:.9rem;outline:none}
.sw input:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(99,102,241,.15)}
.si{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--muted);pointer-events:none}
select,.bv{padding:7px 11px;border:1px solid var(--border);border-radius:var(--rs);background:var(--surface2);color:var(--text);font-size:.85rem;cursor:pointer;outline:none}
select:focus{border-color:var(--primary)}
.vt{display:flex;gap:4px}
.bv{padding:7px 10px}
.bv.on{background:var(--primary);color:#fff;border-color:var(--primary)}
.sc{font-size:.8rem;color:var(--muted);white-space:nowrap}
main{padding:20px 24px;max-width:1400px;margin:0 auto}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
#grid.lv{grid-template-columns:1fr}
.card{background:var(--surface);border-radius:var(--r);border:1px solid var(--border);padding:18px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:10px;transition:transform .15s,box-shadow .15s}
.card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg)}
.lv .card{flex-direction:row;align-items:flex-start;gap:18px;padding:14px 18px}
.ch{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.wm{display:flex;flex-direction:column;gap:2px}
.wt{font-size:1.3rem;font-weight:700;color:var(--text)}
.wi{font-size:.78rem;color:var(--muted);font-style:italic}
.lv .wm{min-width:155px}
.badges{display:flex;gap:5px;flex-wrap:wrap}
.b{display:inline-block;padding:2px 8px;border-radius:99px;font-size:.7rem;font-weight:600}
.bp{background:var(--primary-light);color:var(--primary)}
.bf{background:#ecfdf5;color:#059669}
[data-theme=dark] .bp{background:#1e1b4b;color:#a5b4fc}
[data-theme=dark] .bf{background:#022c22;color:#34d399}
.mk{font-size:.93rem;color:var(--text);line-height:1.5;font-weight:500}
.me{font-size:.78rem;color:var(--muted);margin-top:3px;line-height:1.4}
.ex{background:var(--surface2);border-left:3px solid var(--primary);border-radius:0 var(--rs) var(--rs) 0;padding:9px 11px}
.es{font-size:.84rem;color:var(--text);line-height:1.6;font-style:italic}
.es mark{background:var(--primary-light);color:var(--primary);border-radius:3px;padding:0 2px;font-style:normal;font-weight:600}
[data-theme=dark] .es mark{background:#1e1b4b;color:#a5b4fc}
.esr{font-size:.7rem;color:var(--light);margin-top:4px}
.cf{display:flex;justify-content:space-between;align-items:center;padding-top:4px;border-top:1px solid var(--border)}
.fi{font-size:.73rem;color:var(--muted)}
.tb{display:flex;gap:5px}
.btn-t{display:flex;align-items:center;gap:3px;padding:5px 9px;border:1px solid var(--border);border-radius:var(--rs);background:var(--surface2);color:var(--muted);font-size:.76rem;cursor:pointer;transition:all .15s}
.btn-t:hover{background:var(--primary-light);border-color:var(--primary);color:var(--primary)}
.btn-t:active{transform:scale(.95)}
.btn-t.pl{background:var(--primary);border-color:var(--primary);color:#fff}
.empty{grid-column:1/-1;text-align:center;padding:60px 20px;color:var(--muted)}
.empty h3{font-size:1.1rem;margin-bottom:8px}
#st{position:fixed;bottom:24px;right:24px;width:44px;height:44px;border-radius:50%;background:var(--primary);color:#fff;border:none;cursor:pointer;font-size:1rem;box-shadow:var(--shadow-lg);display:none;align-items:center;justify-content:center;z-index:200}
#st.show{display:flex}
#pag{display:flex;justify-content:center;align-items:center;gap:6px;padding:24px 0;flex-wrap:wrap}
.pg-btn{padding:7px 13px;border:1px solid var(--border);border-radius:var(--rs);background:var(--surface2);color:var(--text);font-size:.85rem;cursor:pointer;transition:all .15s;min-width:36px;line-height:1}
.pg-btn:hover:not(:disabled){background:var(--primary-light);border-color:var(--primary);color:var(--primary)}
.pg-btn.on{background:var(--primary);border-color:var(--primary);color:#fff;font-weight:700}
.pg-btn:disabled{opacity:.4;cursor:default}
.pg-ellipsis{padding:7px 6px;color:var(--muted);font-size:.85rem}
.pg-info{font-size:.8rem;color:var(--muted);padding:0 8px}
@media(max-width:640px){header{padding:12px 16px}.controls{padding:10px 16px;top:58px}main{padding:14px 16px}#grid{grid-template-columns:1fr}.lv .card{flex-direction:column}.pg-btn{padding:6px 10px;font-size:.8rem}}
"""

js = r"""
(function(){
'use strict';
var words = VOCAB.words;
var PAGE_SIZE = 20;
var state = {q:'',pos:'all',sort:'freq',view:'grid',theme:localStorage.getItem('pv-theme')||'light',page:0};

// DOM
var grid = document.getElementById('grid');
var inp  = document.getElementById('si');
var psel = document.getElementById('pf');
var ssel = document.getElementById('sf');
var stat = document.getElementById('sc');
var bg   = document.getElementById('bg');
var bl   = document.getElementById('bl');
var tb   = document.getElementById('themeBtn');
var sbt  = document.getElementById('st');

// 테마
function applyTheme(t){
  document.documentElement.setAttribute('data-theme',t);
  tb.textContent = t==='dark'?'☀️':'🌙';
  localStorage.setItem('pv-theme',t);
}
applyTheme(state.theme);
tb.onclick = function(){state.theme=state.theme==='dark'?'light':'dark';applyTheme(state.theme);};

// 이스케이프
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

// 단어 강조
function hi(text,q){
  var e=esc(text||'');
  if(!q)return e;
  var r=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi');
  return e.replace(r,'<mark>$1</mark>');
}

// 예문 강조
function hiEx(sent,word,q){
  if(!sent)return '';
  var e=esc(sent);
  var r=new RegExp('\\b('+word.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'\\w*)\\b','gi');
  e=e.replace(r,'<mark>$1</mark>');
  if(q&&q.length>2){
    var r2=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi');
    e=e.replace(r2,'<mark>$1</mark>');
  }
  return e;
}

// 빈도 라벨
function fl(f){if(f>=10000)return '🔥 '+f.toLocaleString();if(f>=3000)return '⭐ '+f.toLocaleString();return f.toLocaleString();}

// 카드 생성
function mkCard(w){
  var ex=w.examples&&w.examples[0];
  var div=document.createElement('div');
  div.className='card';

  var hdr='<div class="ch"><div class="wm"><span class="wt">'+hi(w.word,state.q)+'</span>'+(w.ipa?'<span class="wi">'+esc(w.ipa)+'</span>':'')+'</div>'
    +'<div class="badges"><span class="b bp">'+esc(w.pos_ko||w.pos)+'</span><span class="b bf">'+fl(w.frequency)+'회</span></div></div>';

  var meaning='<div><div class="mk">'+hi(w.meaning_ko,state.q)+'</div>'+(w.en_def?'<div class="me">'+esc((w.en_def||'').slice(0,100))+'</div>':'')+'</div>';

  var example='';
  if(ex){
    example='<div class="ex"><div class="es">'+hiEx(ex.sentence,w.word,state.q)+'</div><div class="esr">📄 '+esc(ex.source||'')+'</div></div>';
  }

  var footer='<div class="cf"><span class="fi">📊 '+w.frequency.toLocaleString()+'회 · '+w.doc_spread+'편</span>'
    +'<div class="tb">'
    +'<button class="btn-t" data-word="'+esc(w.word)+'" data-type="word">🔊 단어</button>'
    +(ex?'<button class="btn-t" data-sentence="'+esc(ex.sentence)+'" data-type="example">🔊 예문</button>':'')
    +'</div></div>';

  div.innerHTML = hdr+meaning+example+footer;
  return div;
}

// 필터/정렬
function fs(){
  var r=words.slice();
  if(state.q){var q=state.q.toLowerCase();r=r.filter(function(w){return w.word.toLowerCase().indexOf(q)>=0||w.meaning_ko.toLowerCase().indexOf(q)>=0||((w.en_def||'').toLowerCase().indexOf(q)>=0);});}
  if(state.pos!=='all'){r=r.filter(function(w){return w.pos===state.pos;});}
  if(state.sort==='freq'){r.sort(function(a,b){return b.frequency-a.frequency;});}
  else if(state.sort==='alpha'){r.sort(function(a,b){return a.word.localeCompare(b.word);});}
  else if(state.sort==='spread'){r.sort(function(a,b){return b.doc_spread-a.doc_spread;});}
  return r;
}

// 페이지 범위 계산
function getPageRange(cur, total){
  if(total<=7)return Array.from({length:total},function(_,i){return i;});
  if(cur<4)return [0,1,2,3,4,'…',total-1];
  if(cur>total-5)return [0,'…',total-5,total-4,total-3,total-2,total-1];
  return [0,'…',cur-1,cur,cur+1,'…',total-1];
}

// 페이지네이션 렌더
function renderPag(total, totalPages){
  var pag=document.getElementById('pag');
  if(!pag)return;
  pag.innerHTML='';
  if(totalPages<=1){pag.style.display='none';return;}
  pag.style.display='flex';

  function mkBtn(label, onclick, disabled, on){
    var b=document.createElement('button');
    b.className='pg-btn'+(on?' on':'');
    b.textContent=label;
    b.disabled=!!disabled;
    if(!disabled)b.onclick=onclick;
    return b;
  }

  pag.appendChild(mkBtn('‹ 이전',function(){state.page--;render();window.scrollTo(0,0);},state.page===0,false));

  getPageRange(state.page,totalPages).forEach(function(p){
    if(p==='…'){
      var s=document.createElement('span');s.className='pg-ellipsis';s.textContent='…';pag.appendChild(s);
    } else {
      pag.appendChild(mkBtn(p+1,(function(pp){return function(){state.page=pp;render();window.scrollTo(0,0);};})(p),false,p===state.page));
    }
  });

  pag.appendChild(mkBtn('다음 ›',function(){state.page++;render();window.scrollTo(0,0);},state.page===totalPages-1,false));

  var info=document.createElement('span');info.className='pg-info';
  info.textContent=(state.page+1)+' / '+totalPages+' 페이지 (전체 '+total+'개)';
  pag.appendChild(info);
}

// 렌더
function render(){
  var filtered=fs();
  var totalPages=Math.ceil(filtered.length/PAGE_SIZE)||1;
  if(state.page>=totalPages)state.page=Math.max(0,totalPages-1);
  var start=state.page*PAGE_SIZE;
  var pageWords=filtered.slice(start,start+PAGE_SIZE);

  stat.textContent=filtered.length+' / '+words.length+'개';
  grid.innerHTML='';
  if(filtered.length===0){
    var em=document.createElement('div');
    em.className='empty';
    em.innerHTML='<h3>검색 결과 없음</h3><p>"'+esc(state.q)+'"에 해당하는 단어가 없습니다.</p>';
    grid.appendChild(em);
    renderPag(0,0);
    return;
  }
  var frag=document.createDocumentFragment();
  pageWords.forEach(function(w){frag.appendChild(mkCard(w));});
  grid.appendChild(frag);
  renderPag(filtered.length,totalPages);
}

// TTS
var curUtter=null;
grid.addEventListener('click',function(e){
  var btn=e.target.closest('.btn-t');
  if(!btn)return;
  if(!window.speechSynthesis){alert('이 브라우저는 음성 합성을 지원하지 않습니다.');return;}
  var type=btn.getAttribute('data-type');
  var text=type==='word'?btn.getAttribute('data-word'):btn.getAttribute('data-sentence');
  var rate=type==='word'?0.85:0.8;
  if(curUtter){window.speechSynthesis.cancel();document.querySelectorAll('.btn-t.pl').forEach(function(b){b.classList.remove('pl');});if(curUtter._btn===btn){curUtter=null;return;}}
  var u=new SpeechSynthesisUtterance(text);
  u.lang='en-US';u.rate=rate;u.pitch=1;u._btn=btn;
  var vs=window.speechSynthesis.getVoices();
  var v=vs.find(function(x){return x.lang.startsWith('en')&&x.localService;})||vs.find(function(x){return x.lang.startsWith('en');});
  if(v)u.voice=v;
  u.onstart=function(){btn.classList.add('pl');curUtter=u;};
  u.onend=u.onerror=function(){btn.classList.remove('pl');curUtter=null;};
  window.speechSynthesis.speak(u);
});

// 이벤트
var t;
inp.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){state.q=inp.value.trim();state.page=0;render();},200);});
psel.addEventListener('change',function(){state.pos=psel.value;state.page=0;render();});
ssel.addEventListener('change',function(){state.sort=ssel.value;state.page=0;render();});
bg.addEventListener('click',function(){state.view='grid';grid.classList.remove('lv');bg.classList.add('on');bl.classList.remove('on');});
bl.addEventListener('click',function(){state.view='list';grid.classList.add('lv');bl.classList.add('on');bg.classList.remove('on');});
window.addEventListener('scroll',function(){sbt.classList.toggle('show',window.scrollY>300);});
sbt.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});

if(window.speechSynthesis){window.speechSynthesis.getVoices();}

render();
})();
"""

html = (
    "<!DOCTYPE html>\n"
    "<html lang='ko'>\n"
    "<head>\n"
    "<meta charset='UTF-8'>\n"
    "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    "<title>PaperVoca — 논문 기반 영어 단어집</title>\n"
    "<style>" + css + "</style>\n"
    "</head>\n"
    "<body>\n"
    "<header>\n"
    "  <div class='hl'><h1>📚 PaperVoca</h1>"
    f"<p>논문 {paper_count}편 · 학습 어휘 {word_count}개 · {generated_at}</p></div>\n"
    "  <button id='themeBtn' title='다크/라이트 전환'>🌙</button>\n"
    "</header>\n"
    "<div class='controls'>\n"
    "  <div class='sw'><span class='si'>🔍</span><input id='si' type='search' placeholder='단어, 뜻으로 검색...' autocomplete='off'></div>\n"
    "  <select id='pf'><option value='all'>모든 품사</option>" + pos_options + "</select>\n"
    "  <select id='sf'><option value='freq'>빈도 높은 순</option><option value='alpha'>알파벳 순</option><option value='spread'>논문 분산도 순</option></select>\n"
    "  <div class='vt'><button id='bg' class='bv on' title='카드뷰'>⊞</button><button id='bl' class='bv' title='리스트뷰'>☰</button></div>\n"
    f"  <span class='sc' id='sc'>{word_count}개</span>\n"
    "</div>\n"
    "<main><div id='grid'></div><div id='pag'></div></main>\n"
    "<button id='st' title='맨 위로'>▲</button>\n"
    "<script>var VOCAB=" + vocab_json + ";</script>\n"
    "<script>" + js + "</script>\n"
    "</body>\n"
    "</html>"
)

OUT_FILE.write_text(html, encoding="utf-8")
size_kb = OUT_FILE.stat().st_size // 1024
print(f"생성 완료: {OUT_FILE}  ({size_kb} KB)")
