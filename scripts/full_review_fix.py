"""
full_review_fix.py
전체 단어장 재검토 결과 일괄 수정:
1. 노이즈 표제어 삭제 (단어 조각)
2. 비학술/오역 뜻 교정 (예문 기준)
3. 잘못 추출된 예문 재추출 (하이픈 분절·부분일치 아티팩트 제거)
4. 삭제분만큼 새 학술 단어 보충 (2000개 유지)
"""
import json, re, time, urllib.request, sys
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

try:
    from deep_translator import GoogleTranslator
    TR = True
except ImportError:
    TR = False

VOCAB_FILE = Path("data/vocabulary.json")
RAW_DIR    = Path("raw_text")
DICT_API   = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

POS_KO = {"noun":"명사","verb":"동사","adjective":"형용사","adverb":"부사",
          "preposition":"전치사","conjunction":"접속사","pronoun":"대명사"}

# ── 1. 삭제할 노이즈 표제어 ────────────────────────────────────────
NOISE_DELETE = {"ate", "tial", "tively", "ent"}

# ── 2. 뜻/품사 교정 (word → pos, meaning_ko, en_def) ──────────────
MEANING_FIXES = {
    "face": ("verb",
        "직면하다 — 문제·상황·도전 등에 부딪히거나 마주하다.",
        "To confront or deal with a problem or situation."),
    "save": ("verb",
        "저장하다 — 데이터나 자료를 보관하다; (시간·자원을) 절약하다.",
        "To store data; to avoid spending time or resources."),
    "corpus": ("noun",
        "말뭉치 — 언어 분석을 위해 모아 둔 대규모 텍스트 자료.",
        "A large collection of texts used for linguistic analysis."),
    "justify": ("verb",
        "정당화하다 — 어떤 행동·주장·결정이 타당함을 근거를 들어 설명하다.",
        "To show or prove to be reasonable or valid with evidence."),
    "none": ("pronoun",
        "아무것도 — 하나도 없음; 어느 것도 ~아니다.",
        "Not any; not one; no part."),
    "pool": ("noun",
        "풀 — 어떤 목적을 위해 모아 둔 자원·인력·데이터의 집합.",
        "A combined collection of resources, people, or data."),
    "animation": ("noun",
        "애니메이션 — 이미지를 연속적으로 보여 움직임을 구현한 영상.",
        "A sequence of images displayed to create the illusion of movement."),
    "release": ("verb",
        "공개하다 — 자료·제품·정보를 외부에 내놓거나 배포하다.",
        "To make data, a product, or information available to the public."),
    "convert": ("verb",
        "전환하다 — 한 형태·상태·값을 다른 것으로 바꾸다; 변환하다.",
        "To change something into a different form, state, or value."),
    "median": ("noun",
        "중앙값 — 데이터를 크기순으로 늘어놓았을 때 한가운데에 위치하는 값.",
        "The middle value in a data set ordered from smallest to largest."),
    "trust": ("noun",
        "신뢰 — 어떤 사람이나 대상의 능력·진실성에 대한 믿음이나 의존.",
        "Firm belief in or reliance on the ability or truth of someone or something."),
    "sign": ("noun",
        "신호 — 어떤 것을 나타내거나 알리는 표시·징후.",
        "An indication or signal that shows the presence of something."),
    "targeted": ("adjective",
        "표적화된 — 특정 대상이나 목표에 맞추어진; 대상으로 삼은.",
        "Aimed at or directed toward a particular group or objective."),
    "undermine": ("verb",
        "훼손하다 — 어떤 것의 기반이나 효력을 서서히 약화시키다.",
        "To gradually weaken the basis or effectiveness of something."),
    "physical": ("adjective",
        "물리적인 — 물질이나 신체에 관련된; 실재하는.",
        "Relating to material things or the body; tangible."),
    "read": ("verb",
        "읽다 — 글을 보고 그 의미를 이해하다.",
        "To look at and understand the meaning of written text."),
    "deep": ("adjective",
        "깊은 — 정도가 깊거나 심층적인 (예: 심층 학습, 깊은 이해).",
        "Extending far down or in; profound or thorough."),
    "root": ("noun",
        "뿌리 — 근원이나 기반; 어떤 것이 비롯되는 근본.",
        "The basic cause, source, or origin of something."),
    "shape": ("verb",
        "형성하다 — 어떤 것의 형태·성격·방향을 결정하거나 만들어가다.",
        "To determine or influence the form, nature, or direction of something."),
}

# ── 3. 재추출할 예문 (단어 미포함·하이픈 분절·부분일치 아티팩트) ──
RE_EXTRACT = {
    "search": [0], "face": [0, 1], "introduction": [1], "script": [0],
    "thing": [0], "room": [0, 1], "equation": [0], "edge": [0],
    "prove": [1], "file": [1], "graphical": [0], "formation": [1],
    "contextually": [1], "sign": [0, 1], "none": [0, 1], "save": [0, 1],
    "median": [0],
}

# ── 4. 노이즈 삭제분 보충용 신규 단어 (word, fallback_pos) ─────────
NEW_WORDS = [
    ("underpin",       "verb"),
    ("stimulus",       "noun"),
    ("generalization", "noun"),
    ("realm",          "noun"),
]
NEW_FALLBACK_MEANING = {
    "underpin":       "뒷받침하다 — 어떤 이론·주장·구조의 근거나 기반이 되다.",
    "stimulus":       "자극 — 반응이나 활동을 유발하는 요인이나 사건.",
    "generalization": "일반화 — 특정 사례에서 도출한 결론을 더 넓은 범위로 확장하는 것.",
    "realm":          "영역 — 특정 분야나 활동의 범위.",
}

# ──────────────────────────────────────────────────────────────────
BAD_SENT = re.compile(
    r"@|\bEmail\b|\bFunding\b|\bDOI\b|\bORCID\b|©|\bCopyright\b|"
    r"https?://|www\.|\.com\b|\.org\b|\.edu\b|^\s*\d+\s*$|"
    r"^Table\s+\d|^Figure\s+\d|^Fig\.\s*\d|\bISSN\b|\bISBN\b|\bVol\.\b|\bpp\.\b",
    re.IGNORECASE)

def is_good_sentence(s):
    if BAD_SENT.search(s): return False
    a = sum(1 for c in s if c.isalpha())
    if len(s) and a/len(s) < 0.6: return False
    ws = s.split()
    if sum(1 for w in ws if w.isupper() and len(w)>2) > len(ws)*0.3: return False
    return True

def has_word(word, sent):
    """하이픈 분절을 합친 뒤 단어가 독립 토큰으로 존재하는지(부분일치 배제)."""
    joined = re.sub(r'(\w)-\s+(\w)', r'\1\2', sent)
    pat = re.compile(r'(?<![A-Za-z])' + re.escape(word) + r'(?:s|es|ed|ing|d|ly|er|ers)?\b',
                     re.IGNORECASE)
    return pat.search(joined) is not None

def fetch_api(word):
    try:
        req = urllib.request.Request(DICT_API.format(word=word.lower()),
                                     headers={"User-Agent":"PaperVoca/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
        e = data[0] if data else {}
        ph = e.get("phonetic","")
        if not ph:
            for p in e.get("phonetics",[]):
                if p.get("text"): ph = p["text"]; break
        return {"ipa": ph}
    except Exception:
        return {}

def translate(t):
    if not TR or not t: return t
    try: return GoogleTranslator(source="en",target="ko").translate(t[:400]) or t
    except Exception: return t

def find_examples(word, txt_files, metadata, exclude, n=1):
    import random
    sent_split = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    random.seed((hash(word)+12345) % (2**32))
    sampled = random.sample(txt_files, min(len(txt_files), 400))
    out = []
    for tp in sampled:
        if len(out) >= n: break
        try: text = tp.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        for sent in sent_split.split(text):
            sent = re.sub(r"\s+"," ", sent.strip().replace("\n"," "))
            wc = len(sent.split())
            if wc < 12 or wc > 55: continue
            if not has_word(word, sent): continue
            if not is_good_sentence(sent): continue
            if sent in exclude: continue
            slug = tp.stem
            src = metadata.get(slug,{}).get("filename", slug+".pdf")
            out.append({"sentence": sent[:400], "source": src, "type":"from_paper"})
            if len(out) >= n: break
    return out


def main():
    data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    meta_path = RAW_DIR / "metadata.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    txt_files = [f for f in RAW_DIR.glob("*.txt") if f.name != "metadata.json"]

    # 1. 노이즈 삭제
    kept = [w for w in data["words"] if w["word"] not in NOISE_DELETE]
    removed = [w["word"] for w in data["words"] if w["word"] in NOISE_DELETE]
    data["words"] = kept
    wd = {w["word"]: w for w in data["words"]}

    # 2. 뜻/품사 교정
    mfix = 0
    for word,(pos,mean,en) in MEANING_FIXES.items():
        if word in wd:
            w = wd[word]
            w["pos"]=pos; w["pos_ko"]=POS_KO.get(pos,pos)
            w["meaning_ko"]=mean; w["en_def"]=en
            mfix += 1

    # 3. 예문 재추출
    exfix = 0
    for word, idxs in RE_EXTRACT.items():
        if word not in wd: continue
        w = wd[word]
        existing = {e["sentence"] for e in w["examples"]}
        for idx in sorted(idxs):
            if idx >= len(w["examples"]): continue
            new = find_examples(word, txt_files, metadata, existing, n=1)
            if new:
                w["examples"][idx] = new[0]
                existing.add(new[0]["sentence"]); exfix += 1
            else:
                w["examples"][idx] = None
        w["examples"] = [e for e in w["examples"] if e]

    # 4. 신규 단어 보충
    start_id = len(data["words"]) + 1
    added = []
    for i,(word,fb_pos) in enumerate(NEW_WORDS):
        if word in wd:
            print(f"  {word}: 이미 존재 — 건너뜀"); continue
        api = fetch_api(word); time.sleep(0.3)
        exs = find_examples(word, txt_files, metadata, set(), n=2)
        data["words"].append({
            "id": f"w{start_id+i:04d}", "word": word, "lemma": word,
            "pos": fb_pos, "pos_ko": POS_KO.get(fb_pos,fb_pos),
            "ipa": api.get("ipa",""),
            "meaning_ko": NEW_FALLBACK_MEANING[word], "en_def":"",
            "frequency":0,"doc_spread":0,"score":0.0,"difficulty":"academic",
            "examples": exs, "audio":{"mode":"web_speech","file":None},
        })
        added.append(word)

    data["meta"]["word_count"] = len(data["words"])
    data["meta"]["generated_at"] = str(date.today())
    VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"노이즈 삭제: {len(removed)}개 ({', '.join(removed)})")
    print(f"뜻/품사 교정: {mfix}개")
    print(f"예문 재추출: {exfix}개")
    print(f"신규 보충: {len(added)}개 ({', '.join(added)})")
    print(f"최종 단어 수: {len(data['words'])}개")


if __name__ == "__main__":
    main()
