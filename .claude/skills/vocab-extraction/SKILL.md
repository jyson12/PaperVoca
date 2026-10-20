# vocab-extraction

학술 논문 텍스트에서 학습 가치가 높은 영어 단어를 일관된 방법론으로 추출한다.

## 방법론 (고정 파이프라인)

### 1. 토큰화 & 표제어 추출
- `nltk.word_tokenize` + `WordNetLemmatizer`
- 소문자화 후 처리

### 2. 불용어 제거 기준
- NLTK 영어 stopwords
- 1~2글자 토큰
- 숫자/기호 포함 토큰
- URL/약어 패턴: `https?|www|doi|vol|pp|fig|genai|gpt|llm|ai|ml|nlp|pdf|html|et|al|ie|eg`
- 접미사만 남은 토큰: `ing|ed|er|tion|sion`

### 3. 기초 빈출어 제외 (학습 가치 필터)
- GSL(General Service List) 기반 2,000개 기초어휘 제외
- 논문 메타어 제외: `study|result|model|method|approach|system|analysis|paper|research|data`

### 4. 점수 공식
```
score = frequency × log(doc_spread + 1)
```
- `frequency`: 전체 코퍼스 내 등장 횟수
- `doc_spread`: 해당 단어가 등장한 논문 수 (분산도)

### 5. 출력 스키마 (`selected_words.json`)
```json
{
  "meta": { "min_freq": 3, "top_n": 200, "word_count": 200 },
  "words": [
    {
      "word": "cognitive",
      "lemma": "cognitive",
      "pos": "adjective",
      "frequency": 8333,
      "doc_spread": 561,
      "score": 52760.4,
      "difficulty": "academic"
    }
  ]
}
```

### 6. 기본 파라미터
| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `min_freq` | 3 | 최소 등장 횟수 |
| `top_n` | 200 | 추출 단어 수 |
| `difficulty` | "academic" | 난이도 태그 |

## 사용법
```
이 스킬을 사용해 raw_text/ 폴더의 논문 텍스트에서 단어를 추출해줘.
파라미터: min_freq=3, top_n=200
```

## 실행 스크립트
`scripts/vocab_analyzer.py` 참조 (파이프라인 구현체)
