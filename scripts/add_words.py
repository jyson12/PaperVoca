"""
add_words.py
새 단어 목록을 받아 vocabulary.json에 추가.
vocabulary_builder.py의 핵심 로직 재사용.
"""
import json, re, time, urllib.request, urllib.error, sys
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

RAW_DIR    = Path("raw_text")
VOCAB_FILE = Path("data/vocabulary.json")
DICT_API   = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

POS_KO = {
    "noun": "명사", "verb": "동사", "adjective": "형용사",
    "adverb": "부사", "preposition": "전치사", "conjunction": "접속사",
}

# 추가할 24개 단어 (word, pos)
NEW_WORDS = [
    ("contextually",      "adverb"),
    ("relational",        "adjective"),
    ("thesis",            "noun"),
    ("praise",            "noun"),
    ("standardize",       "verb"),
    ("postgraduate",      "noun"),
    ("corroborate",       "verb"),
    ("overly",            "adverb"),
    ("mediator",          "noun"),
    ("exclusively",       "adverb"),
    ("inclusivity",       "noun"),
    ("dedicate",          "verb"),
    ("conceptualisation", "noun"),
    ("satisfactory",      "adjective"),
    ("profound",          "adjective"),
    ("benchmark",         "noun"),
    ("craft",             "verb"),
    ("incomplete",        "adjective"),
    ("deployment",        "noun"),
    ("stance",            "noun"),
    ("conducive",         "adjective"),
    ("aforementioned",    "adjective"),
    ("deem",              "verb"),
    ("award",             "verb"),
]

BAD_SENT_PATTERNS = re.compile(
    r"@|\bEmail\b|\bFunding\b|\bDOI\b|\bORCID\b|©|\bCopyright\b|"
    r"https?://|www\.|\.com\b|\.org\b|\.edu\b|"
    r"^\s*\d+\s*$|^Table\s+\d|^Figure\s+\d|^Fig\.\s*\d|"
    r"\bISSN\b|\bISBN\b|\bVol\.\b|\bpp\.\b",
    re.IGNORECASE
)

def is_good_sentence(sent):
    if BAD_SENT_PATTERNS.search(sent):
        return False
    alpha = sum(1 for c in sent if c.isalpha())
    if len(sent) > 0 and alpha / len(sent) < 0.6:
        return False
    words = sent.split()
    upper = sum(1 for w in words if w.isupper() and len(w) > 2)
    if upper > len(words) * 0.3:
        return False
    return True


def fetch_dict_api(word):
    url = DICT_API.format(word=word.lower())
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PaperVoca/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        entry = data[0] if data else {}
        phonetic = entry.get("phonetic", "")
        if not phonetic:
            for ph in entry.get("phonetics", []):
                if ph.get("text"):
                    phonetic = ph["text"]
                    break
        pos, en_def = "", ""
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


def translate_to_ko(text):
    if not TRANSLATOR_AVAILABLE or not text:
        return text
    try:
        return GoogleTranslator(source="en", target="ko").translate(text[:400]) or text
    except Exception:
        return text


def find_examples(word, txt_files, max_examples=2):
    import random
    pattern = re.compile(r'\b' + re.escape(word) + r'\w*\b', re.IGNORECASE)
    sent_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    examples = []
    random.seed(hash(word) % (2**32))
    sampled = random.sample(txt_files, min(len(txt_files), 300))

    meta_path = RAW_DIR / "metadata.json"
    metadata = {}
    if meta_path.exists():
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))

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


def main():
    data     = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    existing = {w["word"] for w in data["words"]}
    txt_files = [f for f in RAW_DIR.glob("*.txt") if f.name != "metadata.json"]
    start_id  = len(data["words"]) + 1

    added = []
    for idx, (word, fallback_pos) in enumerate(NEW_WORDS):
        if word in existing:
            print(f"  {word}: 이미 존재 — 건너뜀")
            continue

        api   = fetch_dict_api(word)
        time.sleep(0.3)

        ipa     = api.get("ipa", "")
        pos_api = api.get("pos_api", "")
        en_def  = api.get("en_def", "")
        final_pos = pos_api if pos_api else fallback_pos

        word_ko = translate_to_ko(word)
        time.sleep(0.15)

        if en_def and len(en_def) <= 200:
            def_ko = translate_to_ko(en_def)
            time.sleep(0.15)
            meaning_ko = f"{word_ko} — {def_ko}" if def_ko != word_ko else word_ko
        else:
            meaning_ko = word_ko

        examples = find_examples(word, txt_files)

        entry = {
            "id":         f"w{start_id + idx:04d}",
            "word":       word,
            "lemma":      word,
            "pos":        final_pos,
            "pos_ko":     POS_KO.get(final_pos, final_pos),
            "ipa":        ipa,
            "meaning_ko": meaning_ko,
            "en_def":     en_def,
            "frequency":  0,
            "doc_spread": 0,
            "score":      0.0,
            "difficulty": "academic",
            "examples":   examples,
            "audio":      {"mode": "web_speech", "file": None},
        }
        data["words"].append(entry)
        added.append(word)

        print(f"  [{idx+1:2d}/{len(NEW_WORDS)}] {word:25s}  IPA:{bool(ipa)}  예문:{len(examples)}개")

    data["meta"]["word_count"] = len(data["words"])
    data["meta"]["generated_at"] = str(date.today())
    VOCAB_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n추가 완료: {len(added)}개")
    print(f"최종 단어 수: {len(data['words'])}개")
    print("vocabulary.json 저장 완료")


if __name__ == "__main__":
    main()
