# PaperVoca 프로젝트 작업 로그

> 마지막 업데이트: 2026-10-24
> 작업 디렉토리: `d:\test\논문단어집\`
> 현재 배포 상태: **2000개 단어, 3차 전수 검토 + 4차 품질 점검(IPA 사전 대조·잔여 깨진 예문) 반영, 소스 백업·보안 정리 완료** (최신 커밋은 `git log -1`)
> ▶ **새 창·새 세션에서는 바로 아래 "인수인계" 섹션부터 읽을 것.**

---

## ▶ 새 세션 인수인계 (2026-10-24 기준)

### 한눈에 보는 현재 상태
- **단어장**: 2000개 (표제어·id 중복 0), 3차 전수 검토 + 4차 품질 점검 완료.
  예문 2개씩 — `is_bad_example()` 불합격 0개(10-21 규칙 강화 후), IPA·en_def 2000/2000.
  IPA는 영국식(RP) 기준으로 CMU 사전 대조·표기 스캔 통과 (`scripts/check_ipa.py` 표기 문제 0개).
- **배포**: https://jyson12.github.io/PaperVoca (원격 `origin/main`과 동기화 상태로 마무리).
  10-24 마지막 반영 확인: 폴더 이름 변경 커밋 `6fda2a3` 푸시 후 사이트 HTTP 200·새 경로(`D:/논문집`) 반영·옛 경로 0 확인.
  (그 뒤 커밋 `2ff8c73`은 log.md만 바꿈 — 사이트 내용 변화 없음.)
- **결정 대기**: 없음. 남은 것은 선택 기능 작업뿐 (아래 "이어서 할 수 있는 작업").
- **원본 PDF**: `D:\논문집`(10-21 폴더 이름 변경, 이전 `D:\논리전개연습`) — 영문 저널 6종 872편만 대상, 최상위 ★ 폴더(한국 학술지 4종 1,213편)는 제외.
  `raw_text/`에는 기존에 추출한 734편이 그대로 있음 (재추출하지 않음).
- **저장소 백업**: `scripts/`·`.claude/`·`.mcp.json`·`data/`·기획서까지 git 추적.
  `raw_text/`(저작권·용량)·`web/`(빌드 산출물)는 `.gitignore`로 로컬 전용. **저장소는 공개(public)**.
- **GitHub 저장소·보안**: 2026-10-20 저장소를 **삭제 후 같은 이름으로 재생성**해 옛 이력을 제거했다.
  모든 커밋 작성자는 GitHub noreply 주소, 개인 이메일·계정 관련 서술은 원격·로컬 모두 0건.
  GitHub 계정의 이메일 비공개·노출 푸시 차단 설정 켜짐. MCP 서버는 1.0.0으로 고정. Pages(main / root) 정상.
  이 PC의 git 작성자도 전역(`--global`)·저장소(`--local`) 모두 noreply (10-24) — 사용자는 GitHub에 메일 주소 공개를 원하지 않음.

### 2026-10-20 하루 동안 한 일 (순서대로 — 자세한 내용은 아래 각 작업 내역)
1. 3차 전수 검토: 예문 엄격 검증·재추출, 뜻·정의·품사 1,393개 교정, IPA 373개 보완, 중복 id 31개 정리.
2. 원본 폴더 경로 변경: `D:\논문` → `D:\논리전개연습`.
3. 한국 학술지(★) 추출 제외, `D:\논문` 삭제 영향 검토(지장 없음), 소스 백업(.gitignore + scripts·.claude·data 추적).
4. 인수인계 섹션 신설, 개인정보·보안 점검.
5. 보안 정리: log.md의 계정 관련 서술 삭제, MCP 버전 고정, 커밋 작성자 noreply 전환.
6. 이력 재작성(작성자 이메일·옛 log.md 정리) → 저장소 삭제·재생성 → Pages 재설정 → 로컬 옛 객체·백업 정리.

### 2026-10-21에 한 일 (자세한 내용은 아래 "4차 품질 점검")
0. 세션 시작 점검: 원격과 동기화·작성자 noreply·사이트 정상·예문 검증 0개 확인.
   CLAUDE.md가 "수정됨"으로 보이던 것은 줄바꿈(CRLF) 차이뿐이라 `git checkout -- CLAUDE.md`로 정리.
1. IPA 사전 대조: CMU 발음사전 + 표기 스캔으로 2000개 전수 점검 → **199개 교정** (오기·품사별 발음·강세·미국식/방언 표기).
2. 잔여 깨진 예문: 규칙 보강(절 제목 병합·병합어·글머리표 등) + 수작업 불합격 목록 → **79개 단어 예문 교체**.
3. CLAUDE.md(QA 절차에 재추출 결과 확인·불합격 목록·IPA 검증 추가)·log.md 갱신 →
   빌드 → 커밋 `7b3cf9e` → 푸시 → 배포 사이트 반영 확인.
4. **원본 폴더 이름 변경 `D:\논리전개연습` → `D:\논문집`**(사용자 요청, 영어논문작성 프로젝트 세션에서 두 프로젝트를 함께 처리 — 아래 "2026-10-21 작업 내역 — 원본 폴더 이름 변경").
   경로 문자열만 바꿈(코드 로직·단어장 내용 무변경). 이 세션에서는 커밋하지 않았고, 10-24에 검증 후 커밋·푸시했다(아래).

### 2026-10-24에 한 일
1. 세션 시작 점검: 원격과 동기화·작성자 noreply 확인. 작업 트리에 10-21 폴더 이름 변경분(10개 파일)이 미커밋으로 남아 있었음.
2. 폴더 이름 변경분 검증 → 커밋·푸시:
   - 변경이 경로 문자열 치환뿐인지 diff로 확인 (log.md 외 21줄 ↔ 21줄, 경로 외 내용 변경 없음).
   - `D:\논문집` 있음 · `D:\논리전개연습` 없음 · `pdf_extractor.collect_pdfs()` **872개**(★ 0) ·
     `raw_text/metadata.json` original_path **734/734 실재** · `vocabulary.json` meta.source_dir `D:/논문집`, 단어 2000 ·
     `.mcp.json` JSON 정상 · `web/index.html`과 `index.html` 동일 · 옛 이름은 CLAUDE.md·log.md의 이력 기록에만 남음.
   - 예문 검증 `--dry-run` 재추출 대상 0개, `check_ipa.py` 표기 문제 0개, 개인정보·인증 정보 스캔 0건.
   - 커밋 `6fda2a3` → 푸시 → 배포 사이트 HTTP 200·새 경로 반영 확인.
3. **`D:\논문` 폴더가 삭제된 것을 확인** (사용자가 직접 삭제) → "결정 대기" 1번 해소.
4. **이 PC의 전역 git 작성자를 GitHub noreply로 변경** (사용자 결정: "GitHub에 메일 주소가 공개되지 않기를 원함")
   → "결정 대기" 2번 해소. 전역·이 저장소·새 저장소 모두 `269617839+jyson12@users.noreply.github.com`(이름 `jyson12`) 확인.
   이 설정은 커밋 작성자 정보에만 쓰이며 GitHub 로그인·알림 메일과는 무관. log.md 정리 후 커밋 `2ff8c73` 푸시.
   (Claude의 다른 프로젝트 세션에서도 지키도록 "GitHub 메일 비공개" 선호를 Claude 메모리에 저장함.)
5. 이 인수인계 섹션 갱신 (창을 바꿔도 이어갈 수 있게).

### 새 세션 시작 시 점검 순서 (권장)
```bash
cd d:\test\논문단어집
git status -sb && git log -1 --oneline          # 원격과 동기화·작업 트리 깨끗한지
git config user.email                           # …@users.noreply.github.com 이어야 함
python scripts/reextract_examples.py --dry-run  # "재추출 대상 단어: 0개"여야 정상 (약 1~2분)
python scripts/check_ipa.py                     # "표기 문제 0" 이어야 정상 (CMU 불일치 81은 영·미 차이로 정상)
```
- **환경 준비 (다른 PC·새 환경일 때만)**: `check_ipa.py`는 NLTK CMU 발음사전이 필요하다 →
  `python -c "import nltk; nltk.download('cmudict')"` (이 PC에는 10-21에 설치함).
  `reextract_examples.py`는 NLTK 불용어(stopwords)를 쓰고, 첫 실행 때 `raw_text/token_counts.json`(코퍼스 빈도 캐시)을
  만든다 — `raw_text/`가 없는 새 클론에서는 코퍼스 기반 규칙이 꺼진 채로 동작한다(오류는 아님).

### 작업 규칙 (사용자 선호 포함)
- **진행 메모·보고는 모두 한국어로** 쓴다 (사용자 요청).
- 단어를 추가·수정할 때는 **CLAUDE.md의 QA 3단계**를 따르고, 끝나면 예문을 검증한다:
  `python scripts/reextract_examples.py --dry-run` → 대상 0개여야 정상 (불합격 예문만 교체하는 스크립트라 재실행해도 안전).
  교체된 예문은 `data/reextract_report.json`에서 **뜻·품사에 맞는 용례인지 직접 읽고** 확인한다.
  깨졌거나 뜻이 다른 문장은 `data/bad_examples.tsv`에 등록(또는 `#REEX` 용례 정규식 지정) 후 다시 실행.
- IPA를 고칠 때: `python scripts/check_ipa.py`로 점검 → 고칠 값은 `data/ipa_fixes.json`에 넣고
  `python scripts/apply_ipa_fixes.py`로 적용 (재실행 안전). 품사별 발음(lead·live·close, -ate 동사/형용사 등) 주의.
- 빌드·배포: `python scripts/build_dashboard.py` → `cp web/index.html index.html` → 변경 파일 add → commit → `git push origin main`.
- ⛔ 재실행 금지: `full_review_fix3.py`(1회용 — 다시 돌리면 지정 용례 예문이 또 교체됨), `review_vocabulary.py`(접두 오매칭 결함).
- 공개 저장소이므로 새 파일을 올리기 전에 개인정보·인증 정보(이메일·전화번호·API 키·토큰 등)를 검사한다.
  계정 보안 관련 경위(인증·로그인 문제 등)는 log.md 같은 추적 파일에 쓰지 않는다.
- 커밋 작성자는 이 저장소의 git 설정(`git config --local`)과 이 PC의 전역 설정(`--global`, 10-24) 모두
  GitHub noreply 주소로 지정되어 있다 (개인 이메일 사용 금지 — 사용자는 GitHub에 메일 주소가 공개되지 않기를 원함).
  커밋 전에 `git config user.email`이 `…@users.noreply.github.com`인지 확인할 것.
- 다른 PC에 이 저장소의 **재생성 이전 복사본**이 있으면 거기서 푸시하지 않는다 (지우고 새로 받을 것).
- `.mcp.json`의 MCP 서버 버전을 올릴 때는 GitHub 보안 권고와 출시 시점(최소 2주 경과)을 먼저 확인한다.

### 결정 대기 중 (사용자 응답 필요)
- 없음 (10-24 기준).
1. ~~`D:\논문` 폴더 삭제~~ → 사용자가 삭제함 (10-24 확인, 프로젝트 영향 없음은 10-20에 검토 완료).
2. ~~이 PC의 전역 git 작성자 이메일 변경 여부~~ → 사용자 결정으로 noreply로 변경 (10-24).

### 10-20에 끝난 보안 관련 결정 (참고)
- GitHub 계정 이메일 비공개·노출 푸시 차단 설정 → 사용자가 켬.
- 과거 커밋 이력 정리 → 이력 재작성 후 저장소 재생성으로 옛 커밋까지 제거 (GitHub Support 요청 불필요).
- 재작성 전 로컬 백업 → 사이트 정상 확인 후 삭제.

### 이어서 할 수 있는 작업 (선택)
- 음성 파일 사전 생성(edge-tts), 엑셀/CSV 내보내기, 즐겨찾기·학습 완료 체크 기능.
- ~~잔여 깨진 예문 수작업 점검~~, ~~수기 IPA 사전 대조~~ → 10-21 완료 (아래 "4차 품질 점검").
- 참고 — 다시 점검할 필요 없는 항목: 넓은 감사(문장 중간 대문자·병합어 휴리스틱)에서 남는 약 98건은
  고유명사구("Large Language Models")·정상 복합어("interlanguage", "datatype")로 판정한 **오탐**이고,
  `check_ipa.py`의 CMU 불일치 81건은 영·미 발음 차이로 판정한 **정상**이다.

---

## 2026-10-21 작업 내역 — 4차 품질 점검 (IPA 사전 대조 + 잔여 깨진 예문)

### 1. IPA 사전 대조 → 199개 교정
- **방법**: NLTK CMU 발음사전(미국식)과 대조. 모음 체계가 달라 **자음 골격 + 1차 강세 위치**만 비교하고,
  RP 비R음화·요드 차이는 정규화했다. 여기에 미국식·방언·협의 표기 스캔과 음절 수 비교를 더했다.
  → `scripts/check_ipa.py` (읽기 전용, 결과 `data/ipa_check_report.json`).
- **수기 IPA(157개)** 중 실제 오류는 소수였고, 오히려 **Wiktionary 자동 채택분**에서 문제가 많이 나왔다:
  - 오기·음절 누락: `act` /æk/, `translate` /ˈtɹɛnzlæet/, `limit` /ˈlɪmt/, `wide` /wɑed/, `trust` /trʊst/, `pursue` /pəˈʃu/ 등
  - 품사에 안 맞는 발음: `lead`(동사인데 금속 '납' /lɛd/), `live`(형용사인데 /lɪv/), `close`(형용사인데 /kləʊz/),
    `conduct`·`convert`(동사인데 명사 강세), `conflict`·`discourse`(명사인데 동사 강세),
    `document`·`complement`·`supplement`·`associate`·`articulate`(동사인데 명사·형용사 발음), `moderate`(형용사인데 /-eɪt/)
  - 방언(호주·뉴질랜드·Lindsey식) 표기: `without` /wɪθˈʌʊt/, `old` /ˈɒʊld/, `light` /lʌɪt/, `primary` /ˈpɹɒeməɹi/ 등
  - 미국식 표기 혼입(ɚ ɝ oʊ, 짧은 ɑ, 모음 뒤 ɹ): `offer`, `world`, `leader`, `exposure` 등 약 90개 → RP로 통일
  - 강세 오류: `evolution`, `automatically`, `motivational`, `illustrate`, `innovative` 등
- 교정값은 `data/ipa_fixes.json`(IPA 교정 원장, 373 → 563개)에 병합하고 `scripts/apply_ipa_fixes.py`로 적용.
- 남은 CMU 불일치 81개는 영·미 차이(RP의 `schedule` /ˈʃɛdjuːl/, `laboratory` /ləˈbɒɹətɹi/ 등)나 CMU 자체 편차로 확인 → 정상.

### 2. 잔여 깨진 예문 → 79개 단어 예문 교체
- 넓은 감사(코퍼스 빈도 기반)로 4000개 예문을 훑어 실제 불량 약 60개를 확인. 유형:
  절 제목 병합("Feature selection Feature selection leads…", "Literature review Strategies for…"),
  띄어쓰기 누락("documentsa", "theresearch", "Expandingthe"), 표 캡션("TA B L E 1"), 글머리표(•) 목록,
  "(cf." 등 약어에서 잘린 문장, 폭 없는 공백(U+200B)으로 붙은 두 문장, 출판사 안내문("Author Services…").
- `reextract_examples.py` 규칙 보강: 자간 분리 3글자↑, 글머리표, Keywords 줄, 절 제목+대문자, 대문자 일반어 연속,
  제목 반복, 띄어쓰기 누락 병합어·문장 중간 일반어 대문자(코퍼스 빈도 — 캐시 `raw_text/token_counts.json`),
  약어 잘림, 문장 병합, U+2011 하이픈 분절·폭 없는 문자 정리. 각 규칙은 현재 예문에 시험해 오탐을 줄였다.
- 규칙으로 일반화하기 어려운 문장은 **`data/bad_examples.tsv`**(수작업 불합격 목록, 17건)에 등록.
  같은 파일의 `#REEX` 줄로 용례를 지정(6건): `divide`(동사), `coordinate`(조율하다 — 좌표 명사 제외),
  `overall`(형용사 — 문두 부사 제외), `feeling`(명사), `processing`(명사), `adolescent`(명사).
- 교체된 예문은 모두 직접 읽고 뜻·품사를 확인했다. 최종 `--dry-run` 재추출 대상 0개.

## 2026-10-20 작업 내역 — 개인정보·보안 점검 (공개 저장소)

### 점검 범위와 방법
- 현재 추적 파일 전체, 단어장 데이터(`vocabulary.json`·`index.html`), **전체 커밋 이력(삭제된 내용 포함)**,
  커밋 작성자 정보, 저장소 공개 여부(GitHub API), 웹 단어장 코드(`build_dashboard.py`)를 검사.
- 패턴: 개인키, GitHub·Anthropic/OpenAI·Google·AWS·Slack·Notion 토큰, `key/secret/token/password = "..."` 형태,
  이메일, 휴대전화, 주민등록번호, IP 주소, PC 사용자 경로(`C:\Users\…`).

### 결과 — 직접적인 유출 없음
- 인증 정보(키·토큰·비밀번호·개인키): 현재 파일 0건, 커밋 이력 0건.
- 주민번호·휴대전화·IP·PC 사용자 경로: 0건. 논문 원문(`raw_text/`)·`web/`은 이력상 한 번도 커밋된 적 없음.
- 웹 단어장: 외부 스크립트·CDN 없음, 카드에 넣는 모든 값을 `esc()`/`hi()`/`hiEx()`로 이스케이프,
  데이터에 `<script`·`javascript:`·`onerror=` 같은 조각 없음, 로그인·입력 저장 기능 없음(localStorage에는 테마만).
- 스크립트의 외부 통신: 사전 API·구글 번역에 영어 단어·정의만 전송.

### 조치 (사용자 요청: 위험 요소 삭제·비공개 전환)
- 계정 보안 관련 서술을 log.md에서 삭제.
- `.mcp.json`의 MCP 서버를 `@modelcontextprotocol/server-filesystem@1.0.0`으로 고정
  (알려진 취약점 CVE-2025-53109/53110은 2025.7.1에서 수정되어 해당 없음. 날짜형 2026.8.31은 지원 중단,
  2.0.0은 출시 직후라 제외). 초기화·허용 폴더 응답으로 정상 동작 확인. 버전을 올릴 때는 보안 권고를 확인할 것.
- 이후 커밋은 GitHub noreply 주소로 작성 (저장소 로컬 git 설정).

### 이력 재작성 (사용자 결정)
- `git filter-branch`로 커밋 20개 전체의 작성자·커미터를 GitHub noreply 주소로 통일하고,
  옛 버전 `log.md` 4개에서 계정 관련 서술을 제거한 뒤 `main`을 강제 푸시.
- 검증: 새 이력 전체에서 개인 이메일·계정 관련 표현 0건, 파일 내용이 바뀐 커밋은 의도한 4개(log.md)뿐,
  최종 파일 상태는 재작성 전과 동일.
- **커밋 번호가 모두 바뀜.** 이 파일의 커밋 번호는 새 번호로 고쳤음. 대응표: `.git/commit-map.txt` (옛 번호 → 새 번호, 로컬 전용).
- 그러나 강제 푸시 후에도 옛 커밋 번호로 직접 접근하면 옛 내용이 보였음 (GitHub이 연결 끊긴 커밋을 보관하며,
  저장소 주인이 직접 지울 방법은 없음 — GitHub Support 요청 또는 저장소 재생성만 가능).

### 저장소 재생성 (사용자 결정 — 옛 커밋 완전 제거)
- 사용자가 GitHub에서 저장소를 삭제하고 같은 이름 `PaperVoca`(공개, 빈 저장소)로 다시 만듦 → 정리된 `main`만 푸시.
- 확인: 재생성 직후 원격 커밋 22개 모두 noreply 작성자, **옛 커밋 번호 20개 전부 조회 불가**(API 422, 웹 404).
- 잃은 것 없음 (재생성 전 별·포크·이슈·릴리스 모두 0). 웹 단어장 주소는 그대로.
- 사용자가 Pages를 다시 켬(main / root) → 사이트 HTTP 200, 단어 2000개, 배포본과 로컬 `index.html` 해시 일치 확인.
- 한계: 삭제된 저장소는 GitHub 내부에 90일간 복구용으로 보관(비공개). 외부 아카이브·이미 받아 간 사본은 통제 불가.
- 다른 PC에 이 저장소 사본이 있다면 지우고 새로 받을 것 (옛 사본에서 푸시하면 옛 이력이 되살아남).

### 로컬 정리 (마지막 단계)
- 사용자가 GitHub 이메일 비공개·노출 푸시 차단 설정을 켬.
- 재작성 전 원본 이력 백업(번들)과 임시 커밋 목록을 사용자 요청으로 삭제. reflog 만료 + `git gc --prune=now`로
  로컬 저장소 안의 옛 객체도 정리 → 옛 이메일·계정 관련 서술 포함 객체 0건, `git fsck` 문제 0건.
- 이 PC의 **전역** git 작성자 이메일은 그대로 둠 (다른 프로젝트에도 영향 — 인수인계 "결정 대기" 2번 참고).

---

## 2026-10-21 작업 내역 — 원본 폴더 이름 변경 (`D:\논리전개연습` → `D:\논문집`)

- 사용자 요청으로 폴더 이름만 변경(내용 그대로) — 변경 전후 파일 2,089개 · PDF 2,087개 · 2,998,753,607바이트 동일.
  같은 폴더를 원본으로 쓰는 `d:\test\영어논문작성` 프로젝트와 함께 처리했다.
- 바꾼 곳(경로 문자열만, 757곳): `scripts/pdf_extractor.py`(SOURCE_DIR·설명) · `scripts/vocabulary_builder.py`(meta.source_dir) ·
  `data/vocabulary.json`(meta.source_dir) · `raw_text/metadata.json`(original_path 734) · `.mcp.json`(Filesystem MCP 루트) ·
  `index.html`·`web/index.html`(내장 데이터의 source_dir) · `.gitignore` 주석 · `CLAUDE.md` · `.claude/agents/pdf-extractor.md` · 기획서(11).
  파일마다 인코딩·줄바꿈(CRLF/LF)을 그대로 두고 바이트 단위로 치환.
- 검증: `pdf_extractor.collect_pdfs()` → **872개**(★ 0) · `metadata.json` original_path **734/734 실재** · `vocabulary.json` source_dir `D:/논문집` ·
  Filesystem MCP(1.0.0)가 새 루트로 기동되는지 확인 · `D:\논리전개연습` 문자열은 이 log.md의 지난 기록에만 남음(그때의 사실).
- 이 세션에서는 커밋·푸시하지 않았다 — 작업 트리 변경 10개 파일(이 log.md 포함, `raw_text/`·`web/`은 추적 제외).
  → **10-24에 재검증 후 커밋·푸시** (맨 위 "2026-10-24에 한 일").

---

## 2026-10-20 작업 내역 — 한국 학술지 제외 · `D:\논문` 삭제 영향 검토 · 소스 백업

### 1. 한국 학술지 제외 (사용자 결정)
- `scripts/pdf_extractor.py`에 `collect_pdfs()` 추가: 최상위 폴더명이 `★`로 시작하면 제외.
  확인 결과 수집 대상 **872개 = 기존 `D:\논문`과 동일한 영문 저널 6종** (★ 포함 0개).
- `.claude/agents/pdf-extractor.md`, `CLAUDE.md`에도 제외 규칙 명시. 현재 단어장은 재추출하지 않음(변화 없음).

### 2. `D:\논문` 삭제 시 프로젝트 영향 검토 → **지장 없음**
- 원본 PDF를 직접 읽는 코드는 `pdf_extractor.py` 하나뿐이며 이미 `D:\논리전개연습`을 가리킴.
- 공통 PDF 872개 **전체 MD5 일치** (불일치 0) — `D:\논리전개연습`이 완전한 사본.
- 나머지 스크립트는 프로젝트 안의 `raw_text/`(이미 추출된 텍스트)와 `metadata.json`의 **파일명**만 사용.
  `metadata.json`의 원본 경로 734개는 새 폴더로 갱신했고 실재 734/734 확인.
- 대시보드·`vocabulary.json`은 파일명 문자열만 담고 원본 파일을 열지 않음.
- `.mcp.json`은 새 폴더를 가리키고, 사용자 Claude 설정(`~/.claude/settings.json`, `~/.claude.json`)에는 `D:\논문` 참조 없음.
- `D:\논문` 문자열이 남은 곳은 `CLAUDE.md`·`log.md`의 "이전 경로" 기록뿐.
- 검토 범위 밖: 이 프로젝트 외의 프로그램(참고문헌 관리 도구 등)이 `D:\논문`을 쓰는지는 확인하지 않음.

### 3. 소스 백업 (07-03부터의 미결 사항 → 권장안 ① 적용)
- `.gitignore` 신설: `raw_text/`(논문 본문, 저작권·용량), `web/`(빌드 산출물), `__pycache__/`,
  `data/vocabulary_checkpoint.json`, `.claude/settings.local.json` 제외.
- 저장소에 추가: `scripts/` 17개, `.claude/`(에이전트 6·스킬 1), `.mcp.json`, 기획서,
  `data/` 중간 산출물·검수 파일(`selected_words.json`, `extra_candidates.json`, `review_batches/`,
  `review_results/`, `review_report.txt`, `review3_fixes.tsv`, `ipa_fixes.json`, 재추출 보고서 2개).
- 올리기 전 비밀정보(API 키·토큰·비밀번호·이메일) 패턴 검사: 해당 없음.

---

## 2026-10-20 작업 내역 — 원본 논문 폴더 경로 변경 (`D:\논문` → `D:\논리전개연습`)

- `D:\논리전개연습`은 이미 존재하던 폴더로, `D:\논문`의 PDF 872개를 같은 상대 경로로 모두 포함
  (크기 872/872 일치, 표본 31개 MD5 일치) + 한국 학술지 4종 PDF 1,213개 추가
  (★교육공학연구 345, ★교육정보미디어연구 513, ★직업능력개발연구 150, ★진로교육연구 205).
- 변경한 곳: `scripts/pdf_extractor.py`(SOURCE_DIR), `scripts/vocabulary_builder.py`(meta.source_dir),
  `.mcp.json`(Filesystem MCP 허용 폴더 — Claude Code 재시작 후 적용), `.claude/agents/pdf-extractor.md`,
  `data/vocabulary.json`(meta.source_dir), `raw_text/metadata.json`(original_path 734개 — 새 경로 실재 734/734 확인),
  `논문단어집_대시보드_기획서.md`.
- `D:\논문` 폴더 자체는 손대지 않음(삭제 여부는 사용자 결정).
- ~~⚠️ 주의~~ → 같은 날 **한국 학술지 제외로 결정·반영** (위 항목 1). 당시 메모: `pdf_extractor.py`를 다시 돌리면 한국 학술지 1,213편도 추출 대상에 포함된다
  (대부분 국문 본문 + 영문 초록). 포함할지/★ 폴더를 제외할지 재추출 전에 결정 필요.

---

## 2026-10-20 작업 내역 — 3차 전수 검토 (예문 엄격 검증 + 뜻/정의/품사 + IPA)

### 배경
log의 "추가 품질 점검(선택)" 항목을 진행하다가, 2차 검토 이후에도 남은 문제가 훨씬 넓다는 것을 확인.
- 예문 검증이 일부 단어에만 적용됐고, 접미사 화이트리스트에 파생 접미사(ly/en/ation)가 있어
  `like`←"likely", `deep`←"deepen", `cognitive`←"cognitively" 같은 다른 단어 예문이 통과.
- 이전 검토는 meaning_ko **첫 단어**만 봤기 때문에 `—` 뒤 설명과 en_def(카드에 표시)가
  엉뚱한 sense로 남아 있었음 (`educational`="여행사 팸투어", `lead`=납, `key`=열쇠, `math`=풀베기 등).
- IPA 없는 단어 282개 + 기존 IPA 중 조각 표기(`/-ʃnəl/`)·지역 방언(`/ˌɘndɘˈvɘd͡ʒɘl/` NZ)·
  협의 표기(`[ʔæʔp̚]`) 등 90개.

### 수행 (모두 스크립트로 재현 가능)
1. **예문 엄격 검증·재추출** — `scripts/reextract_examples.py`
   - 굴절형만 허용 + 보일러플레이트/절 제목 병합/합자 누락/front matter 문장 필터.
   - 불합격 예문 보유 단어 299개 → 불합격 예문만 교체. 재검증 결과 표제어 미포함 예문 **0개**.
2. **2000개 전수 수기 검토** — `data/review3_fixes.tsv` → `scripts/full_review_fix3.py`
   - 뜻·설명·영어 정의·품사 교정 **1,393개**, 의미/품사가 맞는 용례로 예문 교체 **219개**
     (정규식으로 용례 지정: `face`→"face challenges", `fit`→"model fit", `live`→"live sessions" 등).
   - 표제어 교정 1개: `physic`(약) → **`physics`**(물리학) — 표제어화 오류.
   - 품사 교정 예: `among`·`like`·`behind`·`outside` → 전치사, `must` → 동사(조동사),
     `though`·`unless` → 접속사, `another` → 한정사, `total`·`patient`·`alternative` → 명사.
3. **IPA 보완·교체 373개** — Wiktionary API 원문 파싱(영국식 RP 우선, 품사별 발음 구분:
   permit/extract/update 등) → `data/ipa_fixes.json`. Wiktionary에 발음이 없는 파생어·복수형 등
   ~120개는 수기 작성(ɹ·ɛ 표기 관례 통일). 결과: **IPA 없는 단어 282개 → 0개**, 조각·방언·협의 표기 90개 교체.
4. **깨진 예문 추가 정리** — `is_broken()` 필터(절 제목·소제목 병합, 참고문헌 제목, 쪽 머리말 `14 / 18`,
   자간 분리 `K E Y W O R D S`, 표 캡션, 합자 누락, 한중일 문자 혼입 등)를 예문 검증에 포함.
   하이픈 분절(`pedagog- ical`) 정규화 916개, 깨진 예문 교체 3회 반복(309→123→16개 단어).
   재추출 시 `#REEX` 정규식(지정 용례)을 계속 적용.
5. **중복 id 31개 정리** — 단어 추가 스크립트가 '개수+1'부터 id를 매겨 생긴 충돌.
   빈 번호를 재배정해 id 2000개 모두 고유 (`scripts/fix_duplicate_ids.py`). 대시보드는 id 미사용이라 화면 영향 없음.
6. 대시보드 품사 필터에 `접속사`·`한정사` 라벨 추가 (기존엔 `conjunction`이 영어로 노출).
7. CLAUDE.md QA 규칙 강화 (굴절형만 허용, 설명·en_def까지 검증, 보일러플레이트·깨진 문장 금지, 용례 지정 재추출).

### 최종 검증
- 단어 2000개·표제어 중복 0·id 중복 0, 예문 2개씩, **표제어 미포함/보일러플레이트/깨진 예문 0개**
  (`is_bad_example()` 기준), IPA·en_def 누락 0개, 대시보드 카드 2000개, JS 문법 검사(node --check) 통과.
- 한계: 문장 중간이 PDF에서 섞인 경우("…documentsa difference…")처럼 규칙으로 못 잡는 잔여 오류가
  소수 남아 있을 수 있음.

### ~~미결~~ → 해결
- `scripts/`·`.claude/` 저장소 백업 — 같은 날 백업 완료 (맨 위 항목 3).

---

## 프로젝트 개요

D:\논문집 폴더(2026-10-21 이름 변경 — 이전 `D:\논리전개연습`, 10-20 이전 `D:\논문`)의 PDF 논문(770개)에서 학습 가치 높은 영어 단어 **2000개**를 자동 추출하고,
한국어 뜻·IPA 발음기호·예문·음성 재생이 포함된 웹 단어장 대시보드를 생성하는 프로젝트.
페이지네이션 적용: 한 페이지에 20개 단어 표시.

---

## 2026-07-03 작업 내역 — 상태 점검 및 깃/배포 검증

### 상태 검증 (log.md 기록과 일치 확인)
- Git: 로컬 = 원격 동기화됨 (`9157989`), fetch/push 정상 동작.
- 단어 **2000개**, 예문 0개인 단어 없음, 중복 표제어 없음.
- GitHub Pages 라이브(HTTP 200), 배포본에 최신 수정(직면하다·말뭉치·experimentation)·
  삭제 단어(tal·statutory) 모두 반영 확인. 카드 2000개 확인.
- IPA 발음기호 없는 단어 **282개** (Free Dictionary API 미등록 — 알려진 이슈, 보완은 선택 사항).

### ⚠️ 발견: 저장소에 소스가 백업돼 있지 않음
- `git ls-files` 결과 **추적 파일은 4개뿐**: `CLAUDE.md`, `data/vocabulary.json`,
  `index.html`, `log.md`.
- **추적 안 됨(로컬 전용)**: `scripts/`(파이프라인·검수 스크립트 전체), `.claude/`(에이전트·스킬),
  `raw_text/`(734개 논문 텍스트, ~41MB), `data/selected_words.json`·`extra_candidates.json`·
  `review_batches/`·`review_results/`, `.mcp.json`.
- 즉, 완성물만 배포되고 **그걸 만드는 스크립트/원문은 백업 안 됨** → 로컬 유실 시 재현 어려움.
- 대응(→ 2026-10-20 ① 적용 완료): ① `scripts/`·`.claude/`를 저장소에 추가(권장, `raw_text/`는
  용량·저작권상 `.gitignore` 제외) ② `.gitignore`만 정리 ③ 그대로 두기.

---

## 2026-06-25 작업 내역 — 전체 단어장 2차 검토 + QA 프로세스 문서화

### 배경
24개 신규 단어 검토에 이어, 사용자 요청으로 **2000개 전체**를 예문 기준 재검토.
"예문 추출 정확성 + 뜻 일치 + 품사 일치" 3가지를 전수 점검.

### 발견·수정 (커밋 `8787ea0`)
- **노이즈 표제어 8개 삭제**: ate, tial, tively, ent, tal, tor, pant, min
  (각각 gener-ate, poten-tial, effec-tively, differ-ent, Talebinamvar, educa-tor,
   partici-pant, mini-mal 의 조각)
- **`statutory` 교체** → `experimentation`: 734개 논문 전체에서 Creative Commons
  라이선스 보일러플레이트로만 등장 → 실제 학술 어휘 아님
- **뜻 오류 ~30개 교정**: face(얼굴→직면하다), save(스포츠→저장하다), corpus(신체→말뭉치),
  justify(신이옳다고→정당화하다), pool(수영장→풀), animation(생기→애니메이션),
  release(인질석방→공개하다), convert(개종→전환하다), median(정맥→중앙값), none(종교→아무것도),
  sign(징후→신호), trust(신뢰하다→신뢰), corpus, side, tie, facet, era, live, standing 등
- **품사 오류 교정**: API 고어 sense로 인한 오분류
- **예문 ~70개 재추출**: 접두 오매칭(age→agent, add→address, sign→significant, fun→fund),
  하이픈 분절(in- stance=instance, re- search=research, inter- face)
- **보충 신규 8개**: underpin, stimulus, generalization, realm, prioritise, redesign,
  zone, withdraw (삭제분 보충, 2000개 유지)

### 핵심 교훈 (CLAUDE.md에 명문화)
- `\bword\w*` 예문 추출 패턴은 **다른 단어의 접두**를 잡는다(짧은 단어일수록 위험).
  → 하이픈 합친 뒤 `(?<![A-Za-z])word(접미사)?\b` + 접미사 화이트리스트로 검증.
- Free Dictionary API는 학술과 다른 sense(고어·종교·군사·스포츠·해부학)를 1번 정의로 자주 반환.
- **CLAUDE.md에 단어 추가/수정 시 필수 3단계 QA 프로세스 추가** → 앞으로 자동 적용.

### 검수 스크립트 추가
- `full_review_fix.py`, `full_review_fix2.py` — 노이즈 삭제·뜻 교정·예문 재추출·보충 일괄 적용
- `add_words.py` — 신규 단어 추가(API+번역+예문)

### 마무리 작업 (커밋 `efe903c`)
- `funding`·`statutory` 예문 0개 → 재추출. `statutory`는 라이선스 문구로만 등장해
  `experimentation`(실험)으로 교체.
- `bot` 예문이 의료 처방("1 bot"=병 약어)이라 chatbot 맥락으로 재추출.
- `fun` 예문이 "Fund/funded"에 오매칭 → "Fund"류 제외하고 재추출, 뜻도 명사 "재미"로 수정.
- **웹 대시보드 반영 검증 완료**: `index.html`에 단어 카드 2000개, 수정된 뜻/삭제 단어 모두 확인,
  로컬 HEAD = origin/main 일치 확인.
- CLAUDE.md 신규 작성 → 단어 추가/수정 시 3단계 QA(예문 추출·뜻·품사) 자동 적용.

### 최종 상태
- **2000개 단어** 전부 예문 2개 보유(0개 없음), 중복 표제어 없음.
- 모든 변경 커밋·푸시 완료, GitHub Pages 배포 반영됨.

---

## 2026-06-24 작업 내역 — 전체 단어 카드 검토 및 수정

### 배경
- `offer`(권하다→제공하다), `resource`(의지→자료) 등 예문과 뜻이 불일치하는 카드를 사용자가 발견
- 전체 1998개 단어 카드를 예문 기반으로 재검토 요청

### 문제 파악: review_vocabulary.py의 prefix-match 오류
- `review_vocabulary.py`가 NLTK pos_tag + `re.compile(r"^" + re.escape(word))`로 예문에서 POS를 추출
- `learn` 검색 시 `learning`, `learner`, `learners` 등 파생형이 모두 매칭 → 모두 NN으로 태깅 → verb `learn`을 noun으로 잘못 분류
- 이 방식으로 344개 POS가 잘못 변경됨

### 수정 작업 (스크립트)
| 스크립트 | 역할 | 결과 |
|----------|------|------|
| `scripts/fix_vocabulary.py` | selected_words.json 기준 POS 복원 + 20개 뜻 교정 + 노이즈 단어(`ences`, `ings`) 제거 | POS 323개 복원, 뜻 20개 교정 |
| `scripts/fix_meanings.py` | API가 잘못 가져온 도메인 오류 뜻 26개 교체 | 26개 수정 (cognitive, effective, foster 등) |
| `scripts/apply_all_fixes.py` | 5개 에이전트가 전체 10 배치(200개씩)를 병렬 검토한 결과 일괄 적용 | 뜻 419개 수정, POS 43개 수정, 노이즈 22개 삭제 |

### 에이전트 병렬 검토 방식
- vocabulary.json을 200개씩 10개 배치(`data/review_batches/batch_01.json`~`batch_10.json`)로 분할
- 5개 에이전트가 각 2배치씩 병렬 검토 (예문을 기준으로 뜻·품사 적합성 판단)
- 결과: 노이즈 토큰 22개 삭제 목록 + ~350개 수정 목록 도출

### 최종 결과 (2026-06-24 커밋: `e641be7`)
- **삭제된 노이즈 단어 22개**: ogy, red, der, ple, gy, mance, cess, mation, ture, cally, demic, tional, van, dent, tions, ments, cal, rat, cation, nology, ten, port
- **뜻 수정**: 419개
- **POS 수정**: 43개
- **현재 단어 수**: 1,976개 (목표 2,000개 대비 24개 부족)
- **배포**: https://jyson12.github.io/PaperVoca (git push 완료)

### 다음 단계: 24개 보충
`scripts/find_extra_words.py` 작성 완료 (아직 미실행).  
실행하면 raw_text/를 재분석해 현재 vocabulary에 없는 후보를 순위순으로 출력하고 `data/extra_candidates.json`에 저장함.

---

## 완료된 작업

### Step 1 — 환경 설정
- Python 패키지 설치: `pymupdf`, `nltk`, `deep-translator`, `requests`
- 프로젝트 디렉토리 생성: `raw_text/`, `data/`, `web/audio/`, `scripts/`, `.claude/agents/`
- Filesystem MCP 등록: `.mcp.json` (원본 논문 폴더 접근용 — 현재 `D:\논문집`)

### Step 2 — Sub-agents 생성
`.claude/agents/` 에 6개 에이전트 파일 생성:
- `pdf-extractor.md`
- `vocab-analyzer.md`
- `dictionary-agent.md`
- `example-curator.md`
- `dashboard-builder.md`
- `audio-generator.md` (선택 사항)

커스텀 스킬: `.claude/skills/vocab-extraction/SKILL.md`

### Step 3 — PDF 추출
- 스크립트: `scripts/pdf_extractor.py`
- 결과: 770개 중 **734개 추출 성공**, 36개 실패 (한국어 폴더명 경로 인코딩 문제)
- 출력: `raw_text/*.txt` + `raw_text/metadata.json`
- 주요 수정: `safe_print()` (Windows CP949 콘솔 오류 방지), `page_count`를 `doc.close()` 전에 저장

### Step 4 — 단어 선별
- 스크립트: `scripts/vocab_analyzer.py`
- 결과: 22,990+ 후보 → **2000개 최종 선별** (TOP_N=2000으로 변경)
- 출력: `data/selected_words.json`
- 점수 공식: `score = frequency × log(doc_spread + 1)`
- 기초 빈출어 2,000개 제외, 노이즈 패턴 필터(NOISE_PATTERNS), 접미사 단독 토큰 필터(SUFFIX_ONLY)

### Step 5 — 단어장 완성 (뜻·IPA·예문)
- 스크립트: `scripts/vocabulary_builder.py`
- 결과: **2000개 단어** × (IPA + 한국어 뜻 + 예문 2개)
- 출력: `data/vocabulary.json`
- Free Dictionary API로 IPA/품사/영어 정의 수집
- deep-translator(GoogleTranslator)로 한국어 번역
- 비학술 정의 필터(`BAD_DEF_KEYWORDS`), 이메일·DOI 포함 예문 제거(`BAD_SENT_PATTERNS`)
- 체크포인트 기능: 50개마다 `data/vocabulary_checkpoint.json` 저장 → 중단 후 재시작 시 이어서 진행

### Step 7 — GitHub Pages 배포
- 레포: `https://github.com/jyson12/PaperVoca`
- 배포 URL: `https://jyson12.github.io/PaperVoca`
- 방식: `main` 브랜치 root → GitHub Pages 활성화
- 파일: `web/index.html` 단일 파일 (2207 KB)

### Step 6 — 웹 대시보드 생성
- 스크립트: `scripts/build_dashboard.py`
- 결과: `web/index.html` (단일 파일)
- CSS + JS + 데이터 모두 인라인 (외부 파일 의존성 없음)
- `document.createElement` + `data-*` 속성으로 카드 생성
- Web Speech API (speechSynthesis)로 TTS 발음 재생
- 이벤트 위임 방식 TTS
- **페이지네이션 추가**: 20개/페이지, 이전/다음 버튼, 페이지 번호 표시 (현재 페이지 강조)
- 필터/정렬 변경 시 자동으로 1페이지로 초기화

---

## 현재 상태

| 항목 | 상태 |
|------|------|
| PDF 추출 | 완료 (734/770) — 이후 원본 폴더 `D:\논문집`(10-20 이전, 10-21 이름 변경)으로 변경(★ 제외 872편 대상), 재추출은 안 함 |
| 단어 선별 | **완료 (2000개)** |
| 뜻·IPA·예문 수집 | **완료** |
| 전체 단어 카드 1차 검토 (06-24) | **완료** — 419개 뜻, 43개 POS, 22개 노이즈 삭제 |
| 24개 신규 단어 추가 + 검토 (06-25) | **완료** — 7 POS·15 뜻 수정, 2 예문 재추출 |
| 전체 단어장 2차 검토 (06-25) | **완료** — 노이즈 8개 삭제, ~30개 뜻, ~70개 예문 재추출 |
| 단어 수 2000개 유지 | **완료** — 삭제분만큼 보충, 예문 0개 단어 없음 |
| QA 프로세스 문서화 (CLAUDE.md) | **완료** — 단어 추가/수정 시 자동 적용 (10-20 강화) |
| 전체 단어장 3차 검토 (10-20) | **완료** — 뜻·정의·품사 1,393개, 예문 엄격 검증·재추출, IPA 373개, 중복 id 31개 |
| IPA 발음기호 | **완료** — 2000/2000 (Wiktionary RP 기준, 10-21 CMU 사전 대조로 199개 교정) |
| 잔여 깨진 예문 점검 (10-21) | **완료** — 규칙 보강 + 수작업 불합격 목록, 79개 단어 예문 교체 |
| 웹 대시보드 HTML 생성 + 반영 검증 | **완료** (`index.html`, 2112 KB, 2000 카드 확인) |
| GitHub Pages 배포 | **완료** — https://jyson12.github.io/PaperVoca (10-21 4차 품질 점검 `7b3cf9e`까지 반영 확인) |
| 원본 폴더 경로 변경 (10-20) | **완료** — `D:\논문` → `D:\논리전개연습`, 한국 학술지(★) 제외 |
| 원본 폴더 이름 변경 (10-21) | **완료** — `D:\논리전개연습` → `D:\논문집`, 경로 문자열 757곳, 수집 872·원본 경로 734/734 실재 (10-24 커밋·푸시) |
| 소스 백업 (10-20) | **완료** — scripts/·.claude/·data 추적, raw_text/·web/ 로컬 전용 |
| 개인정보·보안 점검 (10-20) | **완료** — 직접 유출 없음 확인 |
| 보안 정리 (10-20) | **완료** — 계정 관련 서술 삭제, MCP 1.0.0 고정, 작성자 noreply, 이력 재작성 + 저장소 재생성, 로컬 옛 객체 정리 |
| 음성 파일 사전 생성(edge-tts) | 미완료 (선택 사항) |

---

## 파일 구조

```
d:\test\논문단어집\
├── log.md                          ← 이 파일
├── .gitignore                      ← (10-20) raw_text/·web/·캐시·개인 설정 제외
├── .mcp.json                       ← Filesystem MCP 설정 (D:\논문집 + 프로젝트 폴더)
├── 논문단어집_대시보드_기획서.md
├── .claude/
│   ├── agents/
│   │   ├── pdf-extractor.md
│   │   ├── vocab-analyzer.md
│   │   ├── dictionary-agent.md
│   │   ├── example-curator.md
│   │   ├── dashboard-builder.md
│   │   └── audio-generator.md
│   └── skills/
│       └── vocab-extraction/
│           └── SKILL.md
├── CLAUDE.md                       ← ★ 단어 추가/수정 시 필수 3단계 QA 프로세스 (자동 적용)
├── scripts/
│   ├── pdf_extractor.py            ← PDF → raw_text/*.txt
│   ├── vocab_analyzer.py           ← raw_text/ → data/selected_words.json
│   ├── vocabulary_builder.py       ← selected_words.json → data/vocabulary.json
│   ├── build_dashboard.py          ← vocabulary.json → web/index.html
│   ├── review_vocabulary.py        ← ⛔ (참고용) NLTK POS 검토 — prefix-match 오류, 재실행 금지
│   ├── fix_vocabulary.py           ← (06-24) POS 복원 + 뜻 교정 + 노이즈 제거
│   ├── fix_meanings.py             ← (06-24) API 도메인 오류 뜻 교체
│   ├── apply_all_fixes.py          ← (06-24) 에이전트 검토 결과 419개 뜻·43개 POS 일괄 적용
│   ├── find_extra_words.py         ← 2001위↓ 후보 단어 추출 → data/extra_candidates.json
│   ├── add_words.py                ← (06-25) 신규 단어 추가 (API+번역+예문)
│   ├── fix_new_words.py            ← (06-25) 신규 24단어 POS·뜻·예문 교정
│   ├── full_review_fix.py          ← (06-25) 2차 검토 1탄: 노이즈 삭제·뜻·예문·보충
│   ├── full_review_fix2.py         ← (06-25) 2차 검토 2탄: 잔여 노이즈·접두오매칭 예문 재추출
│   ├── reextract_examples.py       ← (10-20) ★ 예문 엄격 검증(굴절형·보일러플레이트·깨진 문장) + 불합격 예문만 재추출
│   ├── full_review_fix3.py         ← (10-20) 3차 검토 적용: review3_fixes.tsv + ipa_fixes.json (1회만 실행 — 재실행 시 예문이 또 바뀜)
│   ├── fix_duplicate_ids.py        ← (10-20) 중복 id 재배정
│   ├── check_ipa.py                ← (10-21) IPA 점검: CMU 사전 대조 + 표기 스캔 (읽기 전용)
│   └── apply_ipa_fixes.py          ← (10-21) data/ipa_fixes.json → vocabulary.json 적용 (재실행 안전)
├── raw_text/                       ← 로컬 전용 (.gitignore)
│   ├── metadata.json               ← 추출된 논문 메타데이터 (original_path는 D:\논문집 기준 — 10-21 갱신)
│   ├── token_counts.json           ← (10-21) reextract_examples.py 코퍼스 빈도 캐시 (원문이 바뀌면 자동 재생성)
│   └── *.txt                       ← 734개 논문 텍스트
├── index.html                     ← ★ git 추적 대상 = 실제 배포 파일 (web/index.html 복사본)
├── data/
│   ├── selected_words.json         ← 2000개 선별 단어 (빈도/분산 점수 포함)
│   ├── vocabulary.json             ← 2000개 완성 단어집 (현재 배포 중)
│   ├── review_batches/             ← batch_01~10.json (에이전트 검토용 분할 파일)
│   ├── review_results/             ← 에이전트 검토 결과 저장
│   ├── extra_candidates.json       ← find_extra_words.py 결과 (2001위↓ 후보 124개)
│   ├── review3_fixes.tsv           ← (10-20) 3차 수기 검토표 (뜻·정의·품사 1,393 / #REEX 용례 지정 219 / #RENAME 1)
│   ├── ipa_fixes.json              ← IPA 교정 원장 563개 (10-20 Wiktionary 373 + 10-21 사전 대조 교정)
│   ├── ipa_check_report.json       ← (10-21) check_ipa.py 결과
│   ├── bad_examples.tsv            ← (10-21) 수작업 불합격 예문 + #REEX 용례 지정
│   └── reextract_report.json 등    ← 재추출 전후 예문 기록
└── web/                            ← 로컬 전용 (.gitignore)
    ├── index.html                  ← build_dashboard.py 생성물 (→ root로 복사해 배포)
    └── audio/                      ← edge-tts mp3 저장 위치 (비어있음)
```

---

## 재실행 명령어

```bash
# ★ 단어를 추가/수정할 때 — 먼저 CLAUDE.md의 3단계 QA 프로세스를 반드시 따른다.

# 단어 검토·수정 후 재빌드 및 배포 (표준 절차)
cd d:\test\논문단어집
python scripts/reextract_examples.py --dry-run   # 예문 검증 — "재추출 대상 0개"면 정상 (아니면 --dry-run 빼고 실행)
python scripts/check_ipa.py           # IPA 점검 (표기 문제 0개 유지) — 교정은 ipa_fixes.json + apply_ipa_fixes.py
python scripts/build_dashboard.py     # vocabulary.json → web/index.html
cp web/index.html index.html          # ★ git이 추적하는 root index.html로 복사 (필수)
git add data/vocabulary.json index.html   # 스크립트·검수표를 고쳤다면 scripts/ data/ 도
git commit -m "메시지"                 # 끝에 Co-Authored-By: Claude ...
git push origin main

# 새 단어 후보 뽑기 (2001위↓)
python scripts/find_extra_words.py    # 약 5~15분 → data/extra_candidates.json

# 전체 파이프라인 (처음부터)
python scripts/pdf_extractor.py       # D:\논문집 PDF(★ 한국 학술지 제외 872편) → raw_text/
python scripts/vocab_analyzer.py      # raw_text/ → selected_words.json (TOP_N=2000)
python scripts/vocabulary_builder.py  # selected_words.json → vocabulary.json
python scripts/build_dashboard.py     # vocabulary.json → web/index.html
cp web/index.html index.html
git add index.html && git push origin main
```

---

## 남은 작업

> 핵심 작업(추출·선별·뜻/품사 검토·2000개 유지·배포·QA 문서화)은 **모두 완료**.
> 아래는 선택 사항이며, 단어를 더 손볼 경우 **반드시 [CLAUDE.md](CLAUDE.md)의 3단계 QA를 먼저 따른다.**

### 결정 대기 (사용자 응답 필요)
- 없음. (`D:\논문` 삭제·전역 git 작성자 noreply 변경은 10-24 완료, 과거 커밋 이력 정리·이메일 비공개 설정은 10-20 완료)

### 선택 사항
- **음성 파일 사전 생성** — `audio-generator` 에이전트, edge-tts 설치 필요 (`pip install edge-tts`)
- **엑셀/CSV 내보내기** — `data/vocabulary.json` → xlsx 변환
- **검색·필터 기능 강화** — 즐겨찾기, 학습 완료 체크
- ~~추가 품질 점검~~ → 2026-10-20 3차 전수 검토로 완료.
- ~~소스 백업 결정~~ → 2026-10-20 백업 완료.

---

## 알려진 이슈

| 이슈 | 원인 | 해결책 |
|------|------|--------|
| 36개 PDF 추출 실패 | 폴더명에 한국어 포함 (`5.ETR&D` 하위) | 경로를 영문으로 변경 후 재실행 |
| ~~IPA 없는 단어 282개~~ (해결됨) | Free Dictionary API 미등록 단어 | Wiktionary 원문 + 수기 보완 → 0개 (10-20) |
| ~~meaning_ko 설명·en_def 오역~~ (해결됨) | 이전 검토가 표제(첫 단어)만 확인 | 3차 전수 검토로 1,393개 교정 (10-20) |
| vocabulary_builder 장시간 실행 | API 호출 포함 2000개 처리 시 ~2시간 소요 | 체크포인트 기능 추가, PC 재시작 후 이어서 실행 |
| ~~단어 수 부족~~ (해결됨) | selected_words 상위 2000개에 노이즈 토큰 다수 포함 | 노이즈 삭제분만큼 학술 단어 보충 → **2000개 유지 완료** |
| 예문 추출 시 접두/하이픈 오매칭 | `\bword\w*` 패턴이 다른 단어의 접두·하이픈 분절을 잡음 | 하이픈 합친 뒤 독립 토큰+접미사 화이트리스트로 검증 (CLAUDE.md 참조) |
| Free Dictionary API 오역 sense | 학술과 다른 1번 정의(고어·종교·군사 등) 반환 | 예문 기준 뜻 검증 후 수동 교정 (CLAUDE.md 참조) |
| ~~소스 미백업~~ (해결됨) | 저장소가 완성물 4개 파일만 추적 | 10-20: scripts/·.claude/·data 백업, raw_text/·web/는 .gitignore |

---

## 주요 설계 결정

- **단어 점수**: `frequency × log(doc_spread + 1)` — 단일 논문에 집중된 단어보다 여러 논문에 분산된 단어 우선
- **기초어 제외**: NLTK 빈출어 + 직접 정의한 2,000개 기초 단어 제외 → 학술 어휘 집중
- **단일 HTML 파일**: 외부 CSS/JS 로드 실패 문제 방지, 어디서든 파일 하나로 실행
- **TTS**: edge-tts mp3 대신 브라우저 내장 Web Speech API 사용 (의존성 없음)
- **페이지네이션**: 2000개 단어를 20개씩 나눠 표시 (100페이지), 스마트 페이지 번호 (생략 부호 포함)
- **체크포인트**: vocabulary_builder.py가 50개마다 중간 저장 → 중단 후 이어서 실행 가능
