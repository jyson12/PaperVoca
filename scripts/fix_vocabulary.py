"""
fix_vocabulary.py
두 가지 작업:
1. review_vocabulary.py가 잘못 변경한 POS → selected_words.json에서 복원
2. 학술 문맥에 맞지 않는 뜻 22개 → 올바른 한국어 뜻으로 교체
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VOCAB_FILE    = Path("data/vocabulary.json")
SELECTED_FILE = Path("data/selected_words.json")

POS_KO = {
    "noun": "명사", "verb": "동사", "adjective": "형용사", "adverb": "부사"
}

# ── 올바른 뜻으로 교정할 단어 (학술 맥락 기준) ─────────────────────────────
MEANING_FIXES = {
    "follow": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "따르다 — 다른 사람이나 사물의 뒤를 가거나, 어떤 지침·원칙에 순종하다.",
        "en_def": "To go after or behind; to comply with or act according to."
    },
    "express": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "표현하다 — 생각이나 감정을 말·글·행동으로 나타내다.",
        "en_def": "To convey thoughts, feelings, or ideas through words or actions."
    },
    "adaptive": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "적응적인 — 변화하는 조건이나 상황에 맞게 조정하거나 변형할 수 있는.",
        "en_def": "Characterized by or showing an ability to adapt to different conditions."
    },
    "continue": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "계속하다 — 중단 없이 지속적으로 진행하거나 유지하다.",
        "en_def": "To carry on or keep doing something without stopping."
    },
    "train": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "훈련하다 — 특정 기술이나 능력을 개발하기 위해 가르치거나 지도하다.",
        "en_def": "To teach or develop skills through practice or instruction."
    },
    "distance": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "거리 — 두 지점 사이의 공간적 간격; 원격 교육에서 물리적·심리적 격리.",
        "en_def": "The amount of space between two points; separation in space or time."
    },
    "move": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "이동하다 — 한 위치에서 다른 위치로 바꾸다; 발전하거나 진전시키다.",
        "en_def": "To change position or location; to progress or advance."
    },
    "exhibit": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "나타내다 — 어떤 특성이나 행동을 명확하게 보여주거나 드러내다.",
        "en_def": "To display or show (a quality, feeling, or behaviour) clearly."
    },
    "designer": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "설계자 — 교육 자료나 시스템을 계획하고 구성하는 사람.",
        "en_def": "A person who plans and creates the structure or appearance of something."
    },
    "english": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "영어 — 영국·미국 등 영어권 국가에서 사용되는 언어; 제2외국어 학습 맥락에서 목표 언어.",
        "en_def": "The language originally from England, widely used as a global language."
    },
    "advanced": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "고급의 — 기초 수준을 넘어 발전되거나 복잡한; 높은 수준의.",
        "en_def": "At a higher level of development; beyond the basic stage."
    },
    "embed": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "포함시키다 — 어떤 요소를 더 큰 전체 안에 통합하거나 단단히 끼워 넣다.",
        "en_def": "To incorporate or fix (an element) firmly within a larger whole."
    },
    "navigate": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "탐색하다 — 복잡한 상황이나 디지털 환경을 효과적으로 이해하고 다루다.",
        "en_def": "To plan and follow a route through a complex environment or system."
    },
    "speak": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "말하다 — 언어를 사용하여 생각이나 의견을 구두로 표현하다.",
        "en_def": "To talk or use language to express thoughts and ideas verbally."
    },
    "match": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "일치하다 — 두 사물이 서로 같거나 대응하다; 적절히 연결되거나 조합되다.",
        "en_def": "To correspond or be equal to; to pair things that go together well."
    },
    "dashboard": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "대시보드 — 주요 정보나 데이터를 한눈에 볼 수 있도록 시각화한 인터페이스.",
        "en_def": "A visual display showing key data or metrics in an organized interface."
    },
    "send": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "보내다 — 정보·데이터·메시지를 전달하거나 전송하다.",
        "en_def": "To cause to go or be taken to a destination; to transmit a message."
    },
    "journey": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "여정 — (비유적으로) 학습이나 성장의 과정; 경험의 흐름.",
        "en_def": "A process of development or progress, especially in learning."
    },
    "navigation": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "탐색 — 디지털 환경이나 정보 시스템에서 원하는 것을 찾아가는 행위.",
        "en_def": "The process of finding one's way through a digital or information space."
    },
    "tone": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "어조 — 말투나 글에서 나타나는 태도나 분위기; 커뮤니케이션의 전반적인 특성.",
        "en_def": "The general character or attitude expressed in speech or writing."
    },
}

# 유지할 수동 수정 항목 (이전 세션에서 검토 완료)
PRESERVED_MEANINGS = {
    "academic":    {"pos": "adjective", "pos_ko": "형용사",
                    "meaning_ko": "학문적인 — 학교나 대학 등 교육 기관에 관련된; 이론적·학술적인."},
    "integration": {"pos": "noun",      "pos_ko": "명사",
                    "meaning_ko": "통합 — 부분들을 하나의 전체로 결합하거나 융합하는 행위 또는 과정."},
    "complete":    {"pos": "adjective", "pos_ko": "형용사",
                    "meaning_ko": "완전한 — 아무것도 빠진 것 없이 전부 갖추어진; 완벽한."},
    "promote":     {"pos": "verb",      "pos_ko": "동사",
                    "meaning_ko": "촉진하다 — 어떤 것이 발전하거나 성장하도록 장려하거나 지원하다."},
}

# 제거할 노이즈 단어 (접미사 조각, 의미 없는 토큰)
NOISE_WORDS = {"ences", "ings"}

# ──────────────────────────────────────────────────────────────────────────────

def main():
    # 1. 로드
    vocab_data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    selected   = json.loads(SELECTED_FILE.read_text(encoding="utf-8"))

    # selected_words.json → 단어별 POS 딕셔너리
    sel_pos = {w["word"]: w["pos"] for w in selected["words"]}

    pos_restored  = 0
    meaning_fixed = 0
    preserved     = 0
    removed       = []
    kept_words    = []

    for w in vocab_data["words"]:
        word = w["word"]

        # 노이즈 단어 제거
        if word in NOISE_WORDS:
            removed.append(word)
            continue

        # 이전 세션 수동 수정 보존
        if word in PRESERVED_MEANINGS:
            fix = PRESERVED_MEANINGS[word]
            w["pos"]        = fix["pos"]
            w["pos_ko"]     = fix["pos_ko"]
            w["meaning_ko"] = fix["meaning_ko"]
            preserved += 1
            kept_words.append(w)
            continue

        # POS 복원 (selected_words.json 기준)
        correct_pos = sel_pos.get(word)
        if correct_pos and correct_pos != w.get("pos"):
            w["pos"]    = correct_pos
            w["pos_ko"] = POS_KO.get(correct_pos, correct_pos)
            pos_restored += 1

        # 뜻 교정
        if word in MEANING_FIXES:
            fix = MEANING_FIXES[word]
            w["pos"]        = fix["pos"]
            w["pos_ko"]     = fix["pos_ko"]
            w["meaning_ko"] = fix["meaning_ko"]
            if "en_def" in fix:
                w["en_def"] = fix["en_def"]
            meaning_fixed += 1

        kept_words.append(w)

    vocab_data["words"] = kept_words
    vocab_data["meta"]["word_count"] = len(kept_words)
    VOCAB_FILE.write_text(
        json.dumps(vocab_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"POS 복원:      {pos_restored}개")
    print(f"뜻 교정:       {meaning_fixed}개")
    print(f"수동 수정 보존: {preserved}개")
    print(f"노이즈 제거:   {len(removed)}개  ({', '.join(removed)})")
    print(f"최종 단어 수:  {len(kept_words)}개")
    print("vocabulary.json 저장 완료")


if __name__ == "__main__":
    main()
