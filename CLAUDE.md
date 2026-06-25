# PaperVoca — 프로젝트 가이드

논문 PDF에서 추출한 학술 영어 단어 **2000개**의 웹 단어장.
배포: https://jyson12.github.io/PaperVoca · 레포: https://github.com/jyson12/PaperVoca

## 핵심 파이프라인
```
raw_text/*.txt → vocab_analyzer.py → selected_words.json
              → vocabulary_builder.py → vocabulary.json
              → build_dashboard.py → web/index.html → (cp) index.html
```
빌드 후 항상 `cp web/index.html index.html` (git이 추적하는 건 root의 index.html).

## 단어장 불변 규칙
- 단어장은 **항상 정확히 2000개**를 유지한다. 노이즈를 삭제하면 같은 수만큼 학술 단어를 보충한다.
- 추가 후보는 `find_extra_words.py`로 2001위 이하에서 뽑는다(`data/extra_candidates.json`).

---

## ★ 단어 추가/수정 시 필수 검수 프로세스 (QA)

새 단어를 추가하거나 기존 단어를 손볼 때는 **반드시 아래 3가지를 예문 기준으로 검증**한다.
이 검수를 건너뛰면 안 된다. (Free Dictionary API는 학술 맥락과 다른 뜻을 자주 반환함 —
고어·종교·군사·스포츠·해부학·항해 등 엉뚱한 sense를 1번 정의로 주는 경우가 많다.)

### 1. 예문 추출 검증 — 예문에 표제어가 "독립 단어"로 실제 존재하는가
- **부분/접두 오매칭 금지**: `\bword\w*` 패턴은 다른 단어의 접두를 잡는다.
  예) `age`→"agent", `add`→"address", `fun`→"fund", `art`→"artificial", `sign`→"significant",
  `none`→"nonetheless", `bot`→"both", `per`→"performance".
- **하이픈 분절 아티팩트 금지**: PDF 줄바꿈으로 쪼개진 단어를 잡는다.
  예) `stance`←"in- stance"(=instance), `search`←"re- search"(=research), `face`←"inter- face".
- **검증 방법**: 하이픈 분절을 먼저 합친 뒤(`(\w)-\s+(\w)` → `\1\2`),
  `(?<![A-Za-z])word(굴절접미사)?\b` 가 매칭되고, 매칭 토큰의 나머지가 정규 접미사
  화이트리스트(s/es/ed/ing/ly/ment/ation/al/...)에 있는지 확인한다. 아니면 다른 단어임.
- 저자명·고유명사 매칭도 배제(`hint`→"Hinton", `tal`→"Talebinamvar", `left`→"Leftwich").

### 2. 뜻 검증 — meaning_ko가 예문에서 쓰인 의미와 일치하는가
- 예문을 읽고 그 문맥에서 단어가 실제 뜻하는 바를 파악한 뒤, meaning_ko 첫 단어가 그와 맞는지 본다.
- 흔한 오류 예: `offer` 권하다→**제공하다**, `resource` 의지→**자료**, `thesis` 명제→**학위논문**,
  `craft` 선박→**만들다**, `save` 스포츠 방어→**저장하다**, `corpus` 신체→**말뭉치**,
  `deploy(ment)` 전개→**배포**, `stance` 자세→**입장**, `mediator` 중재인→**매개자**.
- 비학술 도메인 신호(바다/종교/군사/스포츠/해부학/식물/그리스신화 등)가 보이면 거의 오역이다.

### 3. 품사 검증 — pos가 예문의 실제 용법과 일치하는가
- 예문에서 그 단어가 동사로 쓰였는지 명사/형용사/부사로 쓰였는지 보고 pos를 맞춘다.
- API가 고어 명사 sense를 줘서 동사/형용사가 명사로 잘못 분류되는 일이 잦다.
  예) `overly` 형용사→**부사**, `profound` 명사→**형용사**, `deem` 명사→**동사**,
  `incomplete` 명사→**형용사**, `aforementioned` 명사→**형용사**.
- ⚠️ NLTK `pos_tag` + `^word` 접두 정규식으로 예문 POS를 추정하는 방식은 쓰지 말 것
  (`learn`이 "learning/learner"를 잡아 동사를 명사로 오분류 — `review_vocabulary.py`의 실패 원인).
  코퍼스 다수결 POS(`selected_words.json`)가 per-sentence 추정보다 신뢰도가 높다.

### 검수 후 마무리
```bash
python scripts/build_dashboard.py
cp web/index.html index.html
git add data/vocabulary.json index.html
git commit -m "..."   # 커밋 메시지 끝에 Co-Authored-By: Claude ...
git push origin main
```

### 참고 스크립트
- `find_extra_words.py` — 2001위↓ 후보 추출
- `add_words.py` — 새 단어 일괄 추가(API+번역+예문)
- `full_review_fix.py` / `full_review_fix2.py` — 검수 결과 일괄 적용 예시(노이즈 삭제·뜻 교정·예문 재추출·보충)
- ⛔ `review_vocabulary.py` — 접두 오매칭 결함. 재실행 금지(참고용으로만 보존).
