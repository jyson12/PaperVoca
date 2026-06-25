# PaperVoca 프로젝트 작업 로그

> 마지막 업데이트: 2026-06-24
> 작업 디렉토리: `d:\test\논문단어집\`

---

## 프로젝트 개요

D:\논문 폴더의 PDF 논문(770개)에서 학습 가치 높은 영어 단어 **2000개**를 자동 추출하고,
한국어 뜻·IPA 발음기호·예문·음성 재생이 포함된 웹 단어장 대시보드를 생성하는 프로젝트.
페이지네이션 적용: 한 페이지에 20개 단어 표시.

---

## 2026-06-25 작업 내역 — 전체 단어장 2차 검토 + QA 프로세스 문서화

### 배경
24개 신규 단어 검토에 이어, 사용자 요청으로 **2000개 전체**를 예문 기준 재검토.
"예문 추출 정확성 + 뜻 일치 + 품사 일치" 3가지를 전수 점검.

### 발견·수정 (커밋 `7a78506`)
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

### 최종 결과 (2026-06-24 커밋: `0846429`)
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
- Filesystem MCP 등록: `.mcp.json` (D:\논문 접근용)

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
| PDF 추출 | 완료 (734/770) |
| 단어 선별 | **완료 (2000개 선별, 현재 1976개 유효)** |
| 뜻·IPA·예문 수집 | **완료** |
| 전체 단어 카드 검토 및 수정 | **완료** — 419개 뜻 수정, 43개 POS 수정, 22개 노이즈 삭제 |
| 웹 대시보드 HTML 생성 | **완료** (`web/index.html`, 2195 KB) |
| 페이지네이션 (20개/페이지) | **완료** — 이전/다음/번호 버튼 |
| GitHub Pages 배포 | **완료** — https://jyson12.github.io/PaperVoca |
| 단어 수 2000개 복구 | **미완료** — 노이즈 삭제로 24개 부족, 새 단어 추가 필요 |
| 음성 파일 사전 생성(edge-tts) | 미완료 (선택 사항) |

---

## 파일 구조

```
d:\test\논문단어집\
├── log.md                          ← 이 파일
├── .mcp.json                       ← Filesystem MCP 설정
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
├── scripts/
│   ├── pdf_extractor.py            ← PDF → raw_text/*.txt
│   ├── vocab_analyzer.py           ← raw_text/ → data/selected_words.json
│   ├── vocabulary_builder.py       ← selected_words.json → data/vocabulary.json
│   ├── build_dashboard.py          ← vocabulary.json → web/index.html
│   ├── review_vocabulary.py        ← (참고용) NLTK POS 검토 — prefix-match 오류 있어 재실행 금지
│   ├── fix_vocabulary.py           ← POS 복원 + 뜻 교정 + 노이즈 제거
│   ├── fix_meanings.py             ← API 도메인 오류 뜻 교체
│   ├── apply_all_fixes.py          ← 에이전트 검토 결과 419개 뜻·43개 POS 일괄 적용
│   └── find_extra_words.py         ← ★ 미실행 — 2001위↓ 후보 단어 추출 (24개 보충용)
├── raw_text/
│   ├── metadata.json               ← 추출된 논문 메타데이터
│   └── *.txt                       ← 734개 논문 텍스트
├── data/
│   ├── selected_words.json         ← 2000개 선별 단어 (빈도/분산 점수 포함)
│   ├── vocabulary.json             ← 1976개 완성 단어집 (현재 배포 중)
│   ├── review_batches/             ← batch_01~10.json (에이전트 검토용 분할 파일)
│   ├── review_results/             ← 에이전트 검토 결과 저장
│   └── extra_candidates.json       ← find_extra_words.py 실행 후 생성 예정
└── web/
    ├── index.html                  ← 완성된 단어장 대시보드 (단일 파일, 2195 KB)
    └── audio/                      ← edge-tts mp3 저장 위치 (비어있음)
```

---

## 재실행 명령어

```bash
# ★ 24개 단어 보충 (다음에 이어서 할 작업)
cd d:\test\논문단어집
python scripts/find_extra_words.py    # 약 5~15분 — 2001위↓ 후보 출력 + extra_candidates.json 저장
# 콘솔 출력 보고 24개 선별 후 vocabulary_builder.py 로 추가

# 대시보드 재빌드 및 배포
python scripts/build_dashboard.py
cp web/index.html index.html
git add data/vocabulary.json index.html
git commit -m "메시지"
git push origin main

# 전체 파이프라인 (처음부터)
python scripts/pdf_extractor.py       # PDF → raw_text/
python scripts/vocab_analyzer.py      # raw_text/ → selected_words.json (TOP_N=2000)
python scripts/vocabulary_builder.py  # selected_words.json → vocabulary.json
python scripts/build_dashboard.py     # vocabulary.json → web/index.html
cp web/index.html index.html
git add index.html && git push origin main
```

---

## 남은 작업

### ★ 최우선: 단어 수 2000개 복구 (24개 부족)

`scripts/find_extra_words.py`를 실행하면 현재 vocabulary.json에 없는 후보 단어를 순위순으로 뽑아준다.

```bash
cd d:\test\논문단어집
python scripts/find_extra_words.py   # 약 5~15분 소요, 734개 파일 재분석
# → data/extra_candidates.json 에 후보 저장, 콘솔에 상위 50개 출력
```

출력 확인 후 24개를 선별해 vocabulary_builder.py로 뜻·IPA·예문을 채우고 추가:

```bash
# extra_candidates.json에서 원하는 단어를 selected_words.json에 추가한 뒤
python scripts/vocabulary_builder.py  # 캐시 히트로 기존 단어 재처리 없이 신규만 API 호출
python scripts/build_dashboard.py
cp web/index.html index.html
git add data/vocabulary.json index.html
git commit -m "Add 24 replacement words to restore 2000-word count"
git push origin main
```

### 선택 사항
- **음성 파일 사전 생성** — `audio-generator` 에이전트, edge-tts 설치 필요 (`pip install edge-tts`)
- **엑셀/CSV 내보내기** — `data/vocabulary.json` → xlsx 변환
- **검색·필터 기능 강화** — 즐겨찾기, 학습 완료 체크

---

## 알려진 이슈

| 이슈 | 원인 | 해결책 |
|------|------|--------|
| 36개 PDF 추출 실패 | 폴더명에 한국어 포함 (`5.ETR&D` 하위) | 경로를 영문으로 변경 후 재실행 |
| IPA 없는 단어 일부 | Free Dictionary API 미등록 단어 | 수동 보완 또는 다른 API 사용 |
| vocabulary_builder 장시간 실행 | API 호출 포함 2000개 처리 시 ~2시간 소요 | 체크포인트 기능 추가, PC 재시작 후 이어서 실행 |
| 단어 수 1976개 (24개 부족) | selected_words.json 상위 2000개 중 22개가 노이즈 토큰이었음 | `find_extra_words.py` 실행 후 후보 선별·추가 |

---

## 주요 설계 결정

- **단어 점수**: `frequency × log(doc_spread + 1)` — 단일 논문에 집중된 단어보다 여러 논문에 분산된 단어 우선
- **기초어 제외**: NLTK 빈출어 + 직접 정의한 2,000개 기초 단어 제외 → 학술 어휘 집중
- **단일 HTML 파일**: 외부 CSS/JS 로드 실패 문제 방지, 어디서든 파일 하나로 실행
- **TTS**: edge-tts mp3 대신 브라우저 내장 Web Speech API 사용 (의존성 없음)
- **페이지네이션**: 2000개 단어를 20개씩 나눠 표시 (100페이지), 스마트 페이지 번호 (생략 부호 포함)
- **체크포인트**: vocabulary_builder.py가 50개마다 중간 저장 → 중단 후 이어서 실행 가능
