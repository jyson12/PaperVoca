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

원본 논문 PDF 폴더: **`D:\논리전개연습`** (2026-10-20부터, 이전 `D:\논문`).
영문 저널 6종 + 한국 학술지 4종(★ 폴더)이 있지만, **한국 학술지(최상위 ★ 폴더)는 단어장 대상에서 제외**한다
(`pdf_extractor.py`의 `collect_pdfs()` — 대상 872개).

저장소 구성: `scripts/`·`.claude/`·`.mcp.json`·`data/`(중간 산출물·검수표)는 git으로 백업한다.
`raw_text/`(논문 본문, 저작권·용량)와 `web/`(빌드 산출물)는 `.gitignore`로 로컬 전용.

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
- **검증 방법**: 하이픈·소프트하이픈 분절을 먼저 합친 뒤, 문장 토큰 중 표제어의
  **굴절형만**(s/es/d/ed/ing/er/est, e탈락·y→i·자음중복) 허용한다.
  ly/en/ation/ment 같은 **파생 접미사는 다른 단어**로 본다
  (`like`→"likely", `deep`→"deepen", `cognitive`→"cognitively", `analytic`→"analytics").
  → `scripts/reextract_examples.py`의 `forms()`/`is_bad_example()`을 그대로 쓸 것.
- 저자명·고유명사 매칭도 배제(`hint`→"Hinton", `tal`→"Talebinamvar", `left`→"Leftwich",
  `driver`→"Walshe & Driver", `law`→"Law & Chen").
- **보일러플레이트·깨진 문장 금지**: 라이선스(Creative Commons/Open Access), `Keywords:`,
  저자 기여·윤리 승인·소속 기관, 참고문헌 제목, 절 제목이 붙은 문장("Conclusion This study…"),
  합자 누락("arti cial"), front matter(`raw_text/0_*`)는 예문으로 쓰지 않는다 (`good_sentence()`).
- **의미·품사가 맞는 용례를 고를 것**: 표제어가 들어 있어도 다른 의미면 안 된다
  (`face`←"face-to-face", `live`←"daily lives", `fit`←"one-size-fits-all", `art`←"state-of-the-art").
  재추출 시 `pick(..., must=정규식)`으로 원하는 용례를 지정한다 (`data/review3_fixes.tsv`의 `#REEX` 참고).
- **재추출 결과는 직접 읽고 확인**한다 (`data/reextract_report.json`). 규칙을 통과해도 깨진 문장
  (절 제목 병합, 띄어쓰기 누락 "documentsa", 논문 제목, 비문)이나 다른 의미 용례가 뽑힐 수 있다.
  → `data/bad_examples.tsv`에 `word⇥문장 앞부분` 등록(불합격·후보 제외) 또는
  `#REEX⇥word⇥정규식`으로 용례 지정 후 재실행 (예: `coordinate`→좌표 명사 제외, `overall`→문두 부사 제외).

### 2. 뜻 검증 — meaning_ko가 예문에서 쓰인 의미와 일치하는가
- 예문을 읽고 그 문맥에서 단어가 실제 뜻하는 바를 파악한 뒤, meaning_ko 첫 단어가 그와 맞는지 본다.
- **첫 단어만 보지 말 것**: `—` 뒤 한국어 설명과 `en_def`(카드에 표시됨)도 같은 의미·품사여야 한다.
  3차 검토(2026-10)에서 1,393개를 교정했는데 상당수가 표제만 맞고 설명/영어 정의가 엉뚱했다.
  예) `educational` en_def="여행사 팸투어", `lead`=금속 납, `key`=자물쇠 열쇠, `prior`=수도원장,
  `rather` 설명="선호하다", `session` en_def=재즈 즉흥 연주 모임, `math` en_def=풀베기.
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

### (보조) 발음 검증 — IPA가 영국식(RP)이고 품사에 맞는가
- 품사에 따라 발음이 갈리는 단어 주의: `lead` 동사 /liːd/(≠납 /lɛd/), `live` 형용사 /laɪv/, `close` 형용사 /kləʊs/,
  `conduct`·`convert` 동사는 2음절 강세, `conflict`·`discourse` 명사는 1음절 강세,
  `-ate` 동사 /-eɪt/ ↔ 형용사 /-ət/ (`moderate`, `associate`, `articulate`), `document` 동사 /-mɛnt/.
- 미국식(ɚ ɝ oʊ, 짧은 ɑ) · 방언식(ʌɪ ʌʊ ɒʊ ɛː) · 협의(ɾ ɫ) 표기는 RP로 바꾼다. 표기 관례: `ɹ`, `ɛ`, 어말 `ə`.
- `python scripts/check_ipa.py`로 점검(CMU 사전 대조 + 표기 스캔) → 고칠 값은 `data/ipa_fixes.json`에 넣고
  `python scripts/apply_ipa_fixes.py`로 적용. CMU 불일치는 영·미 차이일 수 있으니 사람이 판단한다.

### 검수 후 마무리
```bash
python scripts/build_dashboard.py
cp web/index.html index.html
git add data/vocabulary.json index.html   # 스크립트·검수표를 고쳤다면 scripts/ data/ 도 함께
git commit -m "..."   # 커밋 메시지 끝에 Co-Authored-By: Claude ...
git push origin main
```

### 참고 스크립트
- `find_extra_words.py` — 2001위↓ 후보 추출
- `add_words.py` — 새 단어 일괄 추가(API+번역+예문)
- `full_review_fix.py` / `full_review_fix2.py` — 검수 결과 일괄 적용 예시(노이즈 삭제·뜻 교정·예문 재추출·보충)
- `reextract_examples.py` — 전 단어 예문 엄격 검증 + 불합격 예문만 재추출 (QA 1단계 자동화)
  + `data/bad_examples.tsv` (수작업 불합격 예문·`#REEX` 용례 지정). 코퍼스 빈도 캐시는 `raw_text/token_counts.json`
- `check_ipa.py` (IPA 점검, 읽기 전용) / `apply_ipa_fixes.py` (`data/ipa_fixes.json` 적용, 재실행 안전)
- `full_review_fix3.py` + `data/review3_fixes.tsv` — 3차 전수 검토 적용
  (TSV: `word⇥pos⇥meaning_ko⇥en_def`, `=`는 유지 / `#REEX⇥word[⇥정규식]` 예문 교체 / `#RENAME` 표제어 교정)
  + `data/ipa_fixes.json` (IPA 교정 원장: 3차 Wiktionary 기반 보완 + 4차 CMU 사전 대조 교정, 영국식(RP) 기준)
- ⛔ `review_vocabulary.py` — 접두 오매칭 결함. 재실행 금지(참고용으로만 보존).
