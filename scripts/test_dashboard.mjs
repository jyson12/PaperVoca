// 대시보드 UI 시험: headless Chrome(없으면 Edge) + CDP — Node 22+ 내장 WebSocket 사용, 추가 패키지 없음.
// 사용법: node scripts/test_dashboard.mjs [web/index.html]
// 즐겨찾기·외움 표시, 학습 기록 필터, 저장·새로고침 유지, CSV(BOM·원본 왕복 비교),
// 학습 기록 백업·불러오기(합치기·잘못된 파일 거부), 학습 모드(뜻 보기·알아요/모르겠어요·키보드), 저장소 차단 환경을 시험한다.
// 시험용 브라우저 프로필은 임시 폴더에 만들고 끝나면 지운다 (사용자 브라우저 기록과 무관).
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const CHROME = ["C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find((p) => existsSync(p));
const PAGE = pathToFileURL(resolve(process.argv[2] || "web/index.html")).href;
const PORT = 9337;
const prof = mkdtempSync(join(tmpdir(), "pv-uitest-"));

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${prof}`,
  "--no-first-run", "--no-default-browser-check", "--disable-gpu", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let ws, id = 0;
const pending = new Map();
const events = [];
function send(method, params = {}) {
  return new Promise((res, rej) => {
    const i = ++id; pending.set(i, { res, rej });
    ws.send(JSON.stringify({ id: i, method, params }));
  });
}
async function ev(expr) {
  const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error("evaluate 실패: " + JSON.stringify(r.exceptionDetails).slice(0, 400));
  return r.result.value;
}
async function waitFor(expr, ms = 5000) {   // 조건이 참이 될 때까지 대기 (headless 타이머 지연 대비)
  for (let t = 0; t < ms; t += 100) { if (await ev(`!!(${expr})`)) return true; await sleep(100); }
  return false;
}
async function nav(url) {   // 이전 문서에 표식을 두고, 표식이 사라진 새 문서에 카드가 그려질 때까지 대기
  try { await ev("window.__oldDoc=1"); } catch {}
  await send("Page.navigate", { url });
  await waitFor("!window.__oldDoc && document.readyState==='complete' && document.querySelector('#grid .card')", 10000);
}

const results = [];
function check(name, ok, detail = "") { results.push({ name, ok, detail }); console.log((ok ? "PASS " : "FAIL ") + name + (detail ? "  — " + detail : "")); }

try {
  let targets;
  for (let i = 0; i < 50; i++) {
    try { targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); if (targets.find(t => t.type === "page")) break; } catch {}
    await sleep(200);
  }
  const page = targets.find((t) => t.type === "page");
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (m) => {
    const d = JSON.parse(m.data);
    if (d.id && pending.has(d.id)) { const p = pending.get(d.id); pending.delete(d.id); d.error ? p.rej(new Error(d.error.message)) : p.res(d.result); }
    else if (d.method) events.push(d);
  };
  await send("Page.enable"); await send("Runtime.enable");

  // 1) 첫 로드
  await nav(PAGE);
  const errs = () => events.filter((e) => e.method === "Runtime.exceptionThrown" || (e.method === "Runtime.consoleAPICalled" && e.params.type === "error"));
  check("스크립트 오류 없음", errs().length === 0, errs().map(e => JSON.stringify(e.params).slice(0, 200)).join(" | "));
  check("카드 20개 표시", await ev("document.querySelectorAll('#grid .card').length") === 20);
  check("진행 현황 초기값", await ev("document.getElementById('pr').textContent") === "✅ 외움 0 / 2000 · ⭐ 0",
    await ev("document.getElementById('pr').textContent"));
  check("카드마다 ☆·외움 버튼", await ev("document.querySelectorAll('#grid .btn-star').length===20 && document.querySelectorAll('#grid .btn-m[data-mark=l]').length===20"));

  // 2) 즐겨찾기·외움 클릭
  const w1 = await ev("document.querySelector('#grid .card .btn-star').getAttribute('data-word')");
  const w2 = await ev("document.querySelectorAll('#grid .card')[1].querySelector('.btn-star').getAttribute('data-word')");
  await ev("document.querySelector('#grid .card .btn-star').click()");
  await ev("document.querySelectorAll('#grid .card')[1].querySelector('.btn-m[data-mark=l]').click()");
  check("☆ → ★ 표시 전환", await ev("document.querySelector('#grid .card .btn-star').textContent") === "★");
  check("외움 카드 흐림 표시", await ev("document.querySelectorAll('#grid .card')[1].classList.contains('learned')"));
  check("진행 현황 갱신", await ev("document.getElementById('pr').textContent") === "✅ 외움 1 / 2000 · ⭐ 1");
  const stored = await ev("localStorage.getItem('pv-marks')");
  check("브라우저 저장소에 표제어 기준 저장", stored === JSON.stringify({ [w1]: { s: 1 }, [w2]: { l: 1 } }), stored);
  check("TTS 버튼과 충돌 없음(외움 클릭이 음성 재생 안 함)", await ev("document.querySelectorAll('.btn-t.pl').length") === 0);

  // 3) 필터
  await ev("var s=document.getElementById('mf');s.value='s';s.dispatchEvent(new Event('change'))");
  check("⭐ 즐겨찾기 필터 = 1개", await ev("document.getElementById('sc').textContent") === "1 / 2000개");
  await ev("var s=document.getElementById('mf');s.value='l';s.dispatchEvent(new Event('change'))");
  check("✅ 외운 단어 필터 = 1개", await ev("document.getElementById('sc').textContent") === "1 / 2000개");
  await ev("var s=document.getElementById('mf');s.value='u';s.dispatchEvent(new Event('change'))");
  check("📖 안 외운 단어 필터 = 1999개", await ev("document.getElementById('sc').textContent") === "1999 / 2000개");

  // 4) CSV (현재 필터: 안 외운 단어 1999개)
  await ev("window.__blob=null;URL.createObjectURL=function(b){window.__blob=b;return 'about:blank';};HTMLAnchorElement.prototype.click=function(){window.__dl=this.download;};");
  await ev("document.getElementById('csvBtn').click()");
  const csv = await ev("window.__blob.text()");
  const lines = csv.split("\r\n");
  const head = await ev("window.__blob.slice(0,3).arrayBuffer().then(b=>Array.from(new Uint8Array(b)))");
  check("CSV: UTF-8 BOM (EF BB BF)", head.join(",") === "239,187,191", head.join(","));
  check("CSV: 머리글 + 1999행", lines.length === 2000, String(lines.length));
  check("CSV: 파일 이름", /^PaperVoca_\d{4}-\d{2}-\d{2}\.csv$/.test(await ev("window.__dl")), await ev("window.__dl"));
  check("CSV: 머리글", lines[0].replace("\ufeff", "") === '"단어","품사","발음","뜻","영어 정의","빈도","논문 수","예문 1","출처 1","예문 2","출처 2","즐겨찾기","외움"');
  check("CSV: 첫 행 즐겨찾기 O", lines[1].startsWith(`"${w1}",`) && lines[1].endsWith('"O",""'), lines[1].slice(0, 60) + " … " + lines[1].slice(-12));
  // 왕복 검사: CSV를 표준 규칙으로 다시 읽어 원본 데이터와 칸마다 비교 (큰따옴표·쉼표·줄바꿈 포함)
  function parseCsv(t) {
    const rows = []; let row = [], cell = "", q = false;
    for (let i = 0; i < t.length; i++) {
      const c = t[i];
      if (q) { if (c === '"') { if (t[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
      else if (c === '"') q = true;
      else if (c === ",") { row.push(cell); cell = ""; }
      else if (c === "\r" && t[i + 1] === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; i++; }
      else cell += c;
    }
    row.push(cell); rows.push(row); return rows;
  }
  const parsed = parseCsv(csv);
  const expect = await ev(`VOCAB.words.filter(w=>w.word!==${JSON.stringify(w2)}).sort((a,b)=>b.frequency-a.frequency).map(w=>{const e=w.examples||[];
    return [w.word,w.pos_ko||w.pos,w.ipa,w.meaning_ko,w.en_def,w.frequency,w.doc_spread,e[0]&&e[0].sentence,e[0]&&e[0].source,e[1]&&e[1].sentence,e[1]&&e[1].source]
      .map(v=>{let s=String(v==null?'':v);return /^[=+\\-@\\t\\r]/.test(s)?"'"+s:s;});})`);
  let mism = 0, firstBad = "";
  expect.forEach((r, i) => { const got = parsed[i + 1].slice(0, 11); if (JSON.stringify(got) !== JSON.stringify(r)) { mism++; if (!firstBad) firstBad = r[0]; } });
  const quoteCells = expect.flat().filter((s) => s.includes('"')).length;
  check("CSV: 다시 읽은 값이 원본과 칸마다 일치 (1999행×11칸)", parsed.length === 2000 && mism === 0,
    `불일치 ${mism}행${firstBad ? " (예: " + firstBad + ")" : ""}, 큰따옴표 든 칸 ${quoteCells}개`);

  // 5) 새로고침 후 유지 + 검색·즐겨찾기 조합
  await nav(PAGE);
  check("새로고침 후 진행 현황 유지", await ev("document.getElementById('pr').textContent") === "✅ 외움 1 / 2000 · ⭐ 1");
  check("새로고침 후 ★ 유지", await ev("document.querySelector('#grid .card .btn-star').textContent") === "★");
  await ev("var s=document.getElementById('mf');s.value='s';s.dispatchEvent(new Event('change'))");
  await ev(`var i=document.getElementById('si');i.value='zzzz';i.dispatchEvent(new Event('input'))`);
  check("검색 결과 없음 안내", await waitFor("document.querySelector('.empty h3')") &&
    (await ev("document.querySelector('.empty h3').textContent")) === "검색 결과 없음");
  await ev(`var i=document.getElementById('si');i.value='';i.dispatchEvent(new Event('input'))`);
  await waitFor("document.getElementById('sc').textContent==='1 / 2000개'");
  await ev("var s=document.getElementById('mf');s.value='l';s.dispatchEvent(new Event('change'))");
  await ev("document.querySelector('#grid .btn-m[data-mark=l]').click()");
  await ev("var s=document.getElementById('mf');s.value='l';s.dispatchEvent(new Event('change'))");
  check("외움 해제 → 외운 단어 0개 안내", (await ev("document.querySelector('.empty h3').textContent")) === "해당하는 단어가 없습니다");
  check("외움 해제 후 저장소", await ev("localStorage.getItem('pv-marks')") === JSON.stringify({ [w1]: { s: 1 } }));

  // 5b) 학습 기록 백업·불러오기 (현재 기록: w1 즐겨찾기)
  await nav(PAGE);
  await ev("URL.createObjectURL=function(b){window.__blob=b;return 'about:blank';};HTMLAnchorElement.prototype.click=function(){window.__dl=this.download;};");
  check("학습 기록 패널: 처음엔 닫힘", await ev("document.getElementById('mkPanel').hidden && document.getElementById('mkMenu').getAttribute('aria-expanded')==='false'"));
  await ev("document.getElementById('mkMenu').click()");
  check("학습 기록 패널: 버튼으로 열림", await ev("!document.getElementById('mkPanel').hidden && document.getElementById('mkPanel').offsetHeight>0 && document.getElementById('mkMenu').getAttribute('aria-expanded')==='true'"));
  await ev("document.getElementById('mkExp').click()");
  check("학습 기록 패널: 백업 후 닫힘", await ev("document.getElementById('mkPanel').hidden"));
  const bak = JSON.parse(await ev("window.__blob.text()"));
  const bakName = await ev("window.__dl");
  check("기록 백업: 파일 형식·내용", bak.app === "PaperVoca" && bak.type === "study-marks" && bak.version === 1 &&
    JSON.stringify(bak.marks) === JSON.stringify({ [w1]: { s: 1 } }) && /^PaperVoca_study_\d{4}-\d{2}-\d{2}\.json$/.test(bakName),
    bakName + " " + JSON.stringify(bak.marks));
  check("기록 백업 알림", await waitFor("document.getElementById('toast').classList.contains('show')") &&
    (await ev("document.getElementById('toast').textContent")) === "학습 기록(1개 단어)을 파일로 저장했습니다.");

  // 다른 기기에서 만든 백업을 불러온다고 가정: w1 외움 추가, w3 즐겨찾기+외움, 단어장에 없는 단어, 형식이 틀린 항목
  const w3 = await ev("document.querySelectorAll('#grid .card')[2].querySelector('.btn-star').getAttribute('data-word')");
  async function importFile(name, content) {
    const path = join(prof, name);
    writeFileSync(path, content);
    await ev("document.getElementById('toast').textContent='';document.getElementById('mkFile').value=''");
    const doc = await send("DOM.getDocument", { depth: 0 });
    const q = await send("DOM.querySelector", { nodeId: doc.root.nodeId, selector: "#mkFile" });
    await send("DOM.setFileInputFiles", { nodeId: q.nodeId, files: [path] });
    await waitFor("document.getElementById('toast').textContent");
    return ev("document.getElementById('toast').textContent");
  }
  const imp = JSON.stringify({ app: "PaperVoca", type: "study-marks", version: 1,
    marks: { [w1]: { l: 1 }, [w3]: { s: 1, l: 1 }, notaword_xyz: { s: 1 }, broken: "x" } });
  let msg = await importFile("import.json", imp);
  check("불러오기 알림", msg === "학습 기록을 합쳤습니다 — 3개 단어에 표시가 더해졌습니다.", msg);
  check("불러오기: 기존 기록을 지우지 않고 합침",
    await ev("localStorage.getItem('pv-marks')") === JSON.stringify({ [w1]: { s: 1, l: 1 }, [w3]: { s: 1, l: 1 }, notaword_xyz: { s: 1 } }),
    await ev("localStorage.getItem('pv-marks')"));
  check("불러오기 후 진행 현황(단어장 밖 단어 제외)", await ev("document.getElementById('pr').textContent") === "✅ 외움 2 / 2000 · ⭐ 2",
    await ev("document.getElementById('pr').textContent"));
  check("불러오기 후 카드 표시 갱신", await ev("document.querySelectorAll('#grid .card')[2].classList.contains('learned') && document.querySelectorAll('#grid .card')[2].querySelector('.btn-star').textContent==='★'"));
  msg = await importFile("import2.json", imp);
  check("같은 파일 다시 불러오기 → 더할 것 없음 안내", msg === "새로 더할 기록이 없습니다 (이미 같은 기록이 있습니다).", msg);
  const before = await ev("localStorage.getItem('pv-marks')");
  const m1 = await importFile("bad.json", "{ not json");
  const m2 = await importFile("other.json", JSON.stringify({ app: "Other", marks: { x: { s: 1 } } }));
  check("잘못된 파일 거부(깨진 JSON·다른 앱 파일)", m1 === "PaperVoca 학습 기록 파일이 아닙니다." && m2 === m1 &&
    await ev("localStorage.getItem('pv-marks')") === before, m1 + " / " + m2);

  // 5c) 학습 모드 (현재 기록: w1·w3 즐겨찾기+외움) — 즐겨찾기 필터로 2개만, 순서 섞기 끄고 시험
  const key = (k) => send("Input.dispatchKeyEvent", { type: "keyDown", key: k, code: k === " " ? "Space" : k.length === 1 ? "Digit" + k : k,
    text: k.length === 1 ? k : undefined, windowsVirtualKeyCode: k === " " ? 32 : k === "Escape" ? 27 : k === "ArrowLeft" ? 37 : k.charCodeAt(0) })
    .then(() => send("Input.dispatchKeyEvent", { type: "keyUp", key: k, windowsVirtualKeyCode: k === " " ? 32 : k === "Escape" ? 27 : k === "ArrowLeft" ? 37 : k.charCodeAt(0) }));
  const sdWord = () => ev("(document.querySelector('#sdBody .fc-word')||{}).textContent||''");
  const meaningOf = (w) => ev(`VOCAB.words.find(x=>x.word===${JSON.stringify(w)}).meaning_ko`);
  await ev(`var i=document.getElementById('si');i.value='zzzz';i.dispatchEvent(new Event('input'))`);
  await waitFor("document.querySelector('.empty')");
  await ev("document.getElementById('toast').textContent='';document.getElementById('studyBtn').click()");
  check("학습 모드: 목록이 비면 열지 않고 안내", await ev("document.getElementById('study').hidden") &&
    (await ev("document.getElementById('toast').textContent")).startsWith("학습할 단어가 없습니다"));
  await ev(`var i=document.getElementById('si');i.value='';i.dispatchEvent(new Event('input'))`);
  await waitFor("document.getElementById('sc').textContent==='2000 / 2000개'");
  await ev("var s=document.getElementById('mf');s.value='s';s.dispatchEvent(new Event('change'))");
  await ev("document.getElementById('studyBtn').click()");
  check("학습 모드: 시작 화면에 대상 개수", await ev("!document.getElementById('study').hidden") &&
    (await ev("document.querySelector('#sdBody .sd-big').textContent")) === "지금 목록의 단어 2개로 학습합니다.");
  check("학습 모드: 뒤 화면 조작 막힘(inert)·스크롤 잠금", await ev("document.getElementById('main').inert && document.getElementById('ctl').inert && document.body.style.overflow==='hidden'"));
  await ev("document.getElementById('sdShuffle').checked=false;document.querySelector('#sdBody [data-act=start]').click()");
  check("학습 모드: 첫 카드 = 목록 첫 단어, 뜻은 가려짐", (await sdWord()) === w1 && await ev("!document.querySelector('#sdBody .fc-back')") &&
    (await ev("document.getElementById('sdProg').textContent")) === "1 / 2", await sdWord());
  await ev("document.activeElement.blur()");
  await key(" ");
  check("학습 모드: Space로 뜻 보기", await waitFor("document.querySelector('#sdBody .fc-back')") &&
    (await ev("document.querySelector('#sdBody .fc-back .mk').textContent")) === await meaningOf(w1));
  await key("2");
  await waitFor(`document.querySelector('#sdBody .fc-word') && document.querySelector('#sdBody .fc-word').textContent===${JSON.stringify(w3)}`);
  check("학습 모드: 2(모르겠어요) → 외움 해제·다음 카드", JSON.parse(await ev("localStorage.getItem('pv-marks')"))[w1].l === undefined &&
    (await sdWord()) === w3 && (await ev("document.getElementById('sdProg').textContent")) === "2 / 2");
  await ev("document.querySelector('#sdBody [data-act=prev]').click()");
  check("학습 모드: ‹ 이전으로 돌아가면 다시 앞면", (await sdWord()) === w1 && await ev("!document.querySelector('#sdBody .fc-back')"));
  await ev("document.querySelector('#sdBody [data-act=reveal]').click()");
  await ev("document.querySelector('#sdBody [data-act=dont]').click()");
  await ev("document.querySelector('#sdBody [data-act=reveal]').click()");
  await ev("document.querySelector('#sdBody [data-act=know]').click()");
  check("학습 모드: 끝 화면 집계", (await ev("document.querySelector('#sdBody .sd-end p:nth-child(2)').textContent")) === "✅ 알아요 1 · 🔁 모르겠어요 1" &&
    JSON.parse(await ev("localStorage.getItem('pv-marks')"))[w3].l === 1);
  await ev("document.querySelector('#sdBody [data-act=retry]').click()");
  check("학습 모드: 모르겠어요 단어만 다시", (await sdWord()) === w1 && (await ev("document.getElementById('sdProg').textContent")) === "1 / 1");
  await ev("document.querySelector('#sdBody [data-act=reveal]').click()");
  await key("1");
  await waitFor("document.querySelector('#sdBody .sd-end')");
  check("학습 모드: 1(알아요) → 외움 표시", JSON.parse(await ev("localStorage.getItem('pv-marks')"))[w1].l === 1 &&
    (await ev("document.querySelector('#sdBody .sd-end p:nth-child(2)').textContent")) === "✅ 알아요 1 · 🔁 모르겠어요 0");
  await key("Escape");
  check("학습 모드: Esc로 닫으면 목록·진행 현황 갱신, 조작 복구", await waitFor("document.getElementById('study').hidden") &&
    (await ev("document.getElementById('pr').textContent")) === "✅ 외움 2 / 2000 · ⭐ 2" &&
    await ev("!document.getElementById('main').inert && document.body.style.overflow===''") &&
    await ev("document.activeElement===document.getElementById('studyBtn')"));
  check("학습 모드: 스크립트 오류 없음", errs().length === 0, errs().map(e => JSON.stringify(e.params).slice(0, 200)).join(" | "));

  // 6) 저장소가 막힌 환경(사생활 보호 모드 등)에서도 동작
  await send("Page.addScriptToEvaluateOnNewDocument", { source: "Storage.prototype.getItem=function(){throw new Error('blocked')};Storage.prototype.setItem=function(){throw new Error('blocked')};" });
  events.length = 0;
  await nav(PAGE);
  check("저장소 차단 시 오류 없이 표시", errs().length === 0 && await ev("document.querySelectorAll('#grid .card').length") === 20);
  await ev("document.querySelector('#grid .card .btn-star').click()");
  check("저장소 차단 시 클릭 동작(저장만 안 됨)", await ev("document.querySelector('#grid .card .btn-star').textContent") === "★");
} catch (e) {
  check("시험 실행", false, e.stack || String(e));
} finally {
  try { ws && ws.close(); } catch {}
  // 브라우저가 완전히 끝난 뒤 지운다 (Windows는 종료 직후에도 프로필 파일을 잠시 붙잡고 있음)
  const exited = chrome.exitCode !== null ? Promise.resolve() : new Promise((r) => chrome.once("exit", r));
  chrome.kill();
  await Promise.race([exited, sleep(5000)]);
  try { rmSync(prof, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 }); }
  catch (e) { console.log("임시 프로필 삭제 실패 (직접 지워도 됨): " + prof); }
  const fail = results.filter((r) => !r.ok).length;
  console.log(`\n결과: ${results.length - fail} 통과 / ${fail} 실패`);
  process.exit(fail ? 1 : 0);
}
