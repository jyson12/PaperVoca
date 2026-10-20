"""
fix_new_words.py
새로 추가한 24개 단어 중 품사·뜻 오류 수정 + 잘못 추출된 예문 재추출.
"""
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VOCAB_FILE = Path("data/vocabulary.json")
RAW_DIR    = Path("raw_text")

POS_KO = {
    "noun": "명사", "verb": "동사", "adjective": "형용사",
    "adverb": "부사", "preposition": "전치사", "conjunction": "접속사",
}

# word → (pos, meaning_ko, en_def)
FIXES = {
    "relational": ("adjective",
        "관계적인 — 사람·사물·개념 사이의 관계나 상호작용에 관련된.",
        "Relating to the connections or relationships between people or things."),
    "thesis": ("noun",
        "학위논문 — 학위 취득을 위해 제출하는 연구 논문; 학술적 주장.",
        "A long research document submitted for an academic degree."),
    "postgraduate": ("noun",
        "대학원생 — 학사 학위 취득 후 석·박사 과정에서 공부하는 학생; (수식어로) 대학원의.",
        "A student who continues studying after completing an undergraduate degree."),
    "overly": ("adverb",
        "지나치게 — 필요 이상으로; 과도하게.",
        "To an excessive degree; too much."),
    "mediator": ("noun",
        "매개자 — 둘 사이에서 정보·상호작용을 전달하거나 연결하는 사람 또는 요소.",
        "A person or thing that connects or transmits between two parties."),
    "exclusively": ("adverb",
        "오로지 — 다른 것을 제외하고 전적으로; 한 가지에만 한정하여.",
        "Solely or entirely; to the exclusion of anything else."),
    "dedicate": ("verb",
        "전념하다 — 시간·노력·자원을 특정 목적에 온전히 바치거나 할애하다.",
        "To devote time, effort, or resources entirely to a particular purpose."),
    "profound": ("adjective",
        "심오한 — (영향·변화·통찰 등이) 매우 깊고 강한; 근본적인.",
        "Very great or intense; having deep insight or significance."),
    "craft": ("verb",
        "만들다 — 정교하게 또는 공들여 만들어내다; 세심하게 구성하다.",
        "To make or construct something with skill and careful effort."),
    "incomplete": ("adjective",
        "불완전한 — 완전하지 않은; 빠지거나 끝나지 않은 부분이 있는.",
        "Not complete; lacking some part or not finished."),
    "deployment": ("noun",
        "배포·도입 — 시스템·도구·기술을 실제 환경에 배치하여 사용하는 것.",
        "The act of putting a system, tool, or resource into practical use."),
    "stance": ("noun",
        "입장 — 어떤 사안에 대한 태도나 관점; 견지.",
        "An attitude or position taken toward an issue."),
    "aforementioned": ("adjective",
        "앞서 언급한 — 앞에서 이미 말하거나 거론한.",
        "Mentioned or referred to previously."),
    "deem": ("verb",
        "여기다 — ~라고 판단하거나 간주하다; ~로 보다.",
        "To regard or consider something in a specified way."),
    "award": ("verb",
        "수여하다 — 상·보조금·학위 등을 공식적으로 주다; (명사) 상·수상.",
        "To give or grant something officially, such as a prize or funding."),
}

# 재추출이 필요한 예문 (단어 미포함 / 오매칭)
BAD_EXAMPLES = {
    "benchmark": [1],  # index(0-base) 1 = 예문2 재추출
    "stance":    [1],  # "in- stance" (instance 오매칭) 재추출
}

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


def find_clean_examples(word, txt_files, metadata, exclude_sents, n=1):
    """word를 정확한 단어 경계로 포함하고, 하이픈 분절 아티팩트가 아닌 예문 추출."""
    import random
    # 단어 경계 + 앞이 하이픈 분절('- ')이 아닌 경우만
    pattern = re.compile(r'(?<![-\w])' + re.escape(word) + r'\w*\b', re.IGNORECASE)
    hyphen_split = re.compile(r'-\s+' + re.escape(word), re.IGNORECASE)  # "in- stance" 류 차단
    sent_pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')

    random.seed((hash(word) + 999) % (2**32))
    sampled = random.sample(txt_files, min(len(txt_files), 400))
    found = []
    for txt_path in sampled:
        if len(found) >= n:
            break
        try:
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for sent in sent_pattern.split(text):
            sent = re.sub(r"\s+", " ", sent.strip().replace("\n", " "))
            wc = len(sent.split())
            if wc < 12 or wc > 55:
                continue
            if not pattern.search(sent):
                continue
            if hyphen_split.search(sent):
                continue
            if not is_good_sentence(sent):
                continue
            if sent in exclude_sents:
                continue
            slug = txt_path.stem
            source_file = metadata.get(slug, {}).get("filename", slug + ".pdf")
            found.append({"sentence": sent[:400], "source": source_file, "type": "from_paper"})
            if len(found) >= n:
                break
    return found


def main():
    data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    wd = {w["word"]: w for w in data["words"]}

    meta_path = RAW_DIR / "metadata.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    txt_files = [f for f in RAW_DIR.glob("*.txt") if f.name != "metadata.json"]

    pos_fixed = meaning_fixed = ex_fixed = 0

    # 1. 품사·뜻 수정
    for word, (pos, meaning, en_def) in FIXES.items():
        w = wd[word]
        if w["pos"] != pos:
            w["pos"] = pos
            w["pos_ko"] = POS_KO.get(pos, pos)
            pos_fixed += 1
        w["meaning_ko"] = meaning
        w["en_def"] = en_def
        meaning_fixed += 1

    # 2. 잘못된 예문 재추출
    for word, idxs in BAD_EXAMPLES.items():
        w = wd[word]
        existing = {e["sentence"] for e in w["examples"]}
        for idx in idxs:
            new_ex = find_clean_examples(word, txt_files, metadata, existing, n=1)
            if new_ex:
                w["examples"][idx] = new_ex[0]
                existing.add(new_ex[0]["sentence"])
                ex_fixed += 1
                print(f"  [{word}] 예문{idx+1} 재추출: {new_ex[0]['sentence'][:70]}...")
            else:
                print(f"  [{word}] 예문{idx+1} 대체 문장 못 찾음 → 기존 예문 제거")
                w["examples"].pop(idx)

    VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n품사 수정: {pos_fixed}개")
    print(f"뜻 수정:   {meaning_fixed}개")
    print(f"예문 재추출: {ex_fixed}개")
    print("vocabulary.json 저장 완료")


if __name__ == "__main__":
    main()
