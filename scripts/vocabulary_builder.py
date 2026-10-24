"""
vocabulary_builder.py
dictionary-agent + example-curator 통합 스크립트
selected_words.json → vocabulary.json

단계:
1. Free Dictionary API로 IPA/품사/영어 정의 수집
2. deep_translator로 한국어 뜻 생성
3. raw_text/ 에서 예문 추출
4. vocabulary.json 저장
"""
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from collections import defaultdict

# deep_translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("[경고] deep_translator 미설치 → 영어 정의를 한국어 뜻으로 사용")

RAW_DIR = Path("raw_text")
DATA_DIR = Path("data")
INPUT_FILE = DATA_DIR / "selected_words.json"
OUTPUT_FILE = DATA_DIR / "vocabulary.json"
CHECKPOINT_FILE = DATA_DIR / "vocabulary_checkpoint.json"
CHECKPOINT_EVERY = 50  # N개마다 중간 저장

DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

# 품사 한국어 매핑
POS_KO = {
    "noun": "명사", "verb": "동사", "adjective": "형용사",
    "adverb": "부사", "preposition": "전치사", "conjunction": "접속사",
    "pronoun": "대명사", "interjection": "감탄사", "article": "관사",
}

def fetch_dict_api(word: str) -> dict:
    """Free Dictionary API 호출. 실패하면 빈 dict 반환."""
    url = DICT_API.format(word=word.lower())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PaperVoca/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        entry = data[0] if data else {}
        meaning = {}

        # IPA 발음기호
        phonetic = entry.get("phonetic", "")
        if not phonetic:
            for ph in entry.get("phonetics", []):
                if ph.get("text"):
                    phonetic = ph["text"]
                    break

        # 품사 + 첫 번째 영어 정의
        pos = ""
        en_def = ""
        for m in entry.get("meanings", []):
            if not pos:
                pos = m.get("partOfSpeech", "")
            if not en_def and m.get("definitions"):
                en_def = m["definitions"][0].get("definition", "")
            if pos and en_def:
                break

        return {"ipa": phonetic, "pos_api": pos, "en_def": en_def}
    except Exception:
        return {}


def translate_to_ko(text: str) -> str:
    """영어 텍스트를 한국어로 번역. 실패하면 원문 반환."""
    if not TRANSLATOR_AVAILABLE or not text:
        return text
    try:
        translated = GoogleTranslator(source="en", target="ko").translate(text[:400])
        return translated or text
    except Exception:
        return text


# 예문 품질 필터: 이메일/URL/헤더 패턴 감지
BAD_SENT_PATTERNS = re.compile(
    r"@|\bEmail\b|\bFunding\b|\bDOI\b|\bORCID\b|©|\bCopyright\b|"
    r"https?://|www\.|\.com\b|\.org\b|\.edu\b|"
    r"^\s*\d+\s*$|^Table\s+\d|^Figure\s+\d|^Fig\.\s*\d|"
    r"\bISSN\b|\bISBN\b|\bVol\.\b|\bpp\.\b",
    re.IGNORECASE
)

def is_good_sentence(sent: str) -> bool:
    """예문으로 적합한 문장인지 확인."""
    if BAD_SENT_PATTERNS.search(sent):
        return False
    # 특수문자 비율이 너무 높으면 제외
    alpha_count = sum(1 for c in sent if c.isalpha())
    if len(sent) > 0 and alpha_count / len(sent) < 0.6:
        return False
    # 대문자 단어가 너무 많으면 제외 (약어 나열)
    words = sent.split()
    upper_words = sum(1 for w in words if w.isupper() and len(w) > 2)
    if upper_words > len(words) * 0.3:
        return False
    return True


def find_examples(word: str, lemma: str, txt_files: list, metadata: dict, max_examples: int = 2) -> list:
    """raw_text/ 에서 단어가 포함된 예문 추출 (15~60단어 길이)."""
    pattern = re.compile(r'\b' + re.escape(lemma) + r'\w*\b', re.IGNORECASE)
    # 문장 분리 패턴 (마침표/!/?  뒤 대문자 기준)
    sent_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')

    examples = []
    import random
    random.seed(hash(word) % (2**32))  # 단어별 다른 시드로 다양한 출처
    sampled = random.sample(txt_files, min(len(txt_files), 300))

    for txt_path in sampled:
        if len(examples) >= max_examples:
            break
        try:
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
            sentences = sent_pattern.split(text)
            for sent in sentences:
                sent = sent.strip().replace("\n", " ")
                sent = re.sub(r"\s+", " ", sent)
                words_in_sent = sent.split()
                if len(words_in_sent) < 12 or len(words_in_sent) > 55:
                    continue
                if not pattern.search(sent):
                    continue
                if not is_good_sentence(sent):
                    continue

                slug = txt_path.stem
                source_file = metadata.get(slug, {}).get("filename", slug + ".pdf")
                examples.append({
                    "sentence": sent[:400],
                    "source": source_file,
                    "type": "from_paper"
                })
                if len(examples) >= max_examples:
                    break
        except Exception:
            continue

    return examples


BAD_DEF_KEYWORDS = re.compile(
    r"\btravel\b|\bagency\b|\bairline\b|\blegal\b|\blaw\b|\bcourt\b|"
    r"\bfamiliariz\b|\bfam trip\b|\binsurance\b",
    re.IGNORECASE
)


def save_output(result_words: list, txt_files: list, path: Path):
    """result_words를 JSON 파일로 저장."""
    import sys
    from datetime import date
    output = {
        "meta": {
            "generated_at": str(date.today()),
            "source_dir": "D:/논문집",
            "paper_count": len(txt_files),
            "word_count": len(result_words)
        },
        "words": result_words
    }
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.flush()


def main():
    import sys
    # 기존 vocabulary.json 캐시 로드 (변경 없는 단어는 API 재호출 생략)
    cache: dict = {}
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            for w in existing.get("words", []):
                cache[w["word"]] = w
            print(f"캐시 로드: {len(cache)}개 단어", flush=True)
        except Exception:
            pass

    # 입력 로드
    raw = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    words = raw["words"]
    new_words_count = sum(1 for w in words if w["word"] not in cache)
    print(f"처리할 단어: {len(words)}개  (캐시 재사용: {len(words)-new_words_count}개 / 신규 API: {new_words_count}개)", flush=True)

    # 체크포인트 로드 (이어서 실행 지원)
    start_idx = 0
    result_words = []
    if CHECKPOINT_FILE.exists():
        try:
            ckpt = json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
            result_words = ckpt.get("words", [])
            start_idx = len(result_words)
            if start_idx > 0:
                print(f"체크포인트 발견: {start_idx}개 이어서 처리", flush=True)
        except Exception:
            result_words = []
            start_idx = 0

    # 메타데이터 로드
    meta_path = RAW_DIR / "metadata.json"
    metadata = {}
    if meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))

    txt_files = [f for f in RAW_DIR.glob("*.txt") if f.name != "metadata.json"]
    print(f"논문 텍스트: {len(txt_files)}개", flush=True)

    for i, w in enumerate(words[start_idx:], start_idx + 1):
        word  = w["word"]
        lemma = w.get("lemma", word)

        # ── 캐시 히트: 기존 데이터 재사용, 빈도·점수·POS만 최신화 ──
        if word in cache:
            entry = dict(cache[word])
            entry["id"]         = f"w{i:04d}"
            entry["frequency"]  = w["frequency"]
            entry["doc_spread"] = w["doc_spread"]
            entry["score"]      = w["score"]
            # vocab_analyzer v2가 pos_tag 기반 POS를 새로 계산했으면 반영
            new_pos = w.get("pos", "")
            if new_pos and new_pos != entry.get("pos", ""):
                entry["pos"]    = new_pos
                entry["pos_ko"] = POS_KO.get(new_pos, new_pos)
            result_words.append(entry)
            if i % 100 == 0 or i == len(words):
                print(f"  [{i:4d}/{len(words)}] {word:22s}  [캐시]", flush=True)
            # 체크포인트 저장 (캐시 단어도 카운트)
            if i % CHECKPOINT_EVERY == 0:
                save_output(result_words, txt_files, CHECKPOINT_FILE)
            continue

        # ── 캐시 미스: API 호출 ──
        api_data = fetch_dict_api(word)
        time.sleep(0.2)

        ipa     = api_data.get("ipa", "")
        pos_api = api_data.get("pos_api", w.get("pos", "noun"))
        en_def  = api_data.get("en_def", "")

        # pos 결정: -ing 명사 gerund는 pos_tag 결과 우선 (API는 기본 동사로 분류하는 경향)
        analyzer_pos = w.get("pos", "noun")
        if word.endswith("ing") and analyzer_pos == "noun":
            final_pos = "noun"
        else:
            final_pos = pos_api if pos_api else analyzer_pos

        word_ko = translate_to_ko(word)
        time.sleep(0.1)
        if en_def and not BAD_DEF_KEYWORDS.search(en_def) and len(en_def) <= 200:
            def_ko = translate_to_ko(en_def)
            time.sleep(0.1)
            meaning_ko = f"{word_ko} — {def_ko}" if def_ko != word_ko else word_ko
        else:
            meaning_ko = word_ko

        examples = find_examples(word, lemma, txt_files, metadata)

        entry = {
            "id":         f"w{i:04d}",
            "word":       word,
            "lemma":      lemma,
            "pos":        final_pos,
            "pos_ko":     POS_KO.get(final_pos, final_pos),
            "ipa":        ipa,
            "meaning_ko": meaning_ko,
            "en_def":     en_def,
            "frequency":  w["frequency"],
            "doc_spread": w["doc_spread"],
            "score":      w["score"],
            "difficulty": w.get("difficulty", "academic"),
            "examples":   examples,
            "audio":      {"mode": "web_speech", "file": None},
        }
        result_words.append(entry)

        status    = "API+번역" if en_def else "번역only"
        ex_count  = len(examples)
        if i % 20 == 0 or i == len(words):
            print(f"  [{i:4d}/{len(words)}] {word:22s}  IPA:{bool(ipa)}  예문:{ex_count}개  ({status})", flush=True)

        if i % CHECKPOINT_EVERY == 0:
            save_output(result_words, txt_files, CHECKPOINT_FILE)
            print(f"  [체크포인트 저장: {i}개]", flush=True)

    # 최종 저장
    save_output(result_words, txt_files, OUTPUT_FILE)
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
    print(f"\n저장 완료: {OUTPUT_FILE}  ({len(result_words)}개 단어)", flush=True)


if __name__ == "__main__":
    main()
