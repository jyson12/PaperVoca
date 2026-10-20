"""
review_vocabulary.py
vocabulary.json 전체를 검토하여 예문 기반 품사 불일치 및 이상 뜻을 수정한다.

검토 항목:
1. 예문에서 단어의 실제 POS를 pos_tag로 추출 → 저장된 POS와 비교
2. 학술 문맥에 맞지 않는 뜻 패턴 감지
3. 확정 케이스 자동 수정, 애매한 케이스 보고서 출력
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import nltk
for _res, _pkg in [
    ("tokenizers/punkt_tab",                  "punkt_tab"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
]:
    try:
        nltk.data.find(_res)
    except LookupError:
        nltk.download(_pkg, quiet=True)

from nltk.tokenize import word_tokenize
from nltk import pos_tag

DATA_FILE   = Path("data/vocabulary.json")
REPORT_FILE = Path("data/review_report.txt")

PENN_TO_POS = {
    "NN": "noun",  "NNS": "noun",
    "VB": "verb",  "VBD": "verb", "VBG": "verb",
    "VBN": "verb", "VBP": "verb", "VBZ": "verb",
    "JJ": "adjective", "JJR": "adjective", "JJS": "adjective",
    "RB": "adverb",    "RBR": "adverb",    "RBS": "adverb",
}
POS_KO = {
    "noun": "명사", "verb": "동사", "adjective": "형용사", "adverb": "부사"
}

# 학술 문맥에서 의심스러운 뜻 패턴
BAD_MEANING_PATTERNS = re.compile(
    r"설문조사|플라톤|기차|홍보|여행|보험|법원|파충류|당구|항공|"
    r"스코틀랜드|권투|야구|크리켓|럭비|미식축구|레슬링|체스|"
    r"낚시|사냥|골프|배구|배드민턴|탁구|"
    r"주류 밀매|급증|피치|파도|"
    r"A follower of Plato|A completed survey|"
    r"completed survey|strikes a ball"
)


def get_example_pos(word: str, sentence: str) -> str | None:
    """예문에서 해당 단어의 실제 POS를 추출."""
    try:
        tokens = word_tokenize(sentence)
        tagged = pos_tag(tokens)
        pattern = re.compile(r"^" + re.escape(word), re.IGNORECASE)
        votes = []
        for token, penn in tagged:
            if pattern.match(token):
                pos = PENN_TO_POS.get(penn, None)
                if pos:
                    votes.append(pos)
        if votes:
            return Counter(votes).most_common(1)[0][0]
    except Exception:
        pass
    return None


def review(data: dict) -> tuple[list, list, list]:
    """
    Returns:
        auto_fixed  : 자동 수정된 항목 [(word, field, old, new)]
        flagged     : 검토 필요 항목 [(word, reason)]
        ok          : 이상 없는 항목 수
    """
    words       = data["words"]
    auto_fixed  = []
    flagged     = []
    ok_count    = 0

    for idx, w in enumerate(words):
        word     = w["word"]
        cur_pos  = w.get("pos", "")
        meaning  = w.get("meaning_ko", "")
        examples = w.get("examples", [])
        issues   = []

        # ── 1. 예문 기반 POS 추출 ──────────────────────────────
        ex_pos_votes = []
        for ex in examples:
            sent = ex.get("sentence", "")
            p = get_example_pos(word, sent)
            if p:
                ex_pos_votes.append(p)

        if ex_pos_votes:
            example_pos = Counter(ex_pos_votes).most_common(1)[0][0]
            confidence  = ex_pos_votes.count(example_pos) / len(ex_pos_votes)

            if example_pos != cur_pos and confidence >= 0.5:
                # -ing 명사는 예문에서 verb(VBG)로 나타나도 noun 유지
                is_ing_noun = word.endswith("ing") and cur_pos == "noun"
                if not is_ing_noun:
                    old_pos = cur_pos
                    w["pos"]    = example_pos
                    w["pos_ko"] = POS_KO.get(example_pos, example_pos)
                    auto_fixed.append((word, "pos", old_pos, example_pos))
                    issues.append(f"POS {old_pos}→{example_pos} (예문 근거)")

        # ── 2. 뜻 품질 검사 ───────────────────────────────────
        if BAD_MEANING_PATTERNS.search(meaning):
            flagged.append((word, f"의심스러운 뜻: {meaning[:60]}"))
            issues.append("뜻 수동 검토 필요")

        # ── 3. 뜻이 단순 로마자/영어 그대로인 경우 ──────────
        korean_chars = sum(1 for c in meaning if "가" <= c <= "힣")
        if len(meaning) > 0 and korean_chars < len(meaning) * 0.2:
            flagged.append((word, f"한국어 번역 없음: {meaning[:60]}"))
            issues.append("번역 없음")

        if not issues:
            ok_count += 1

        if idx % 200 == 0:
            print(f"  [{idx+1}/2000] 검토 중...", flush=True)

    return auto_fixed, flagged, ok_count


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("vocabulary.json 전체 검토 시작...", flush=True)

    data  = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    total = len(data["words"])
    print(f"총 {total}개 단어 검토", flush=True)

    auto_fixed, flagged, ok_count = review(data)

    # 수정본 저장
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 보고서 작성
    lines = []
    lines.append(f"=== vocabulary.json 검토 보고서 ===\n")
    lines.append(f"총 단어: {total}개")
    lines.append(f"자동 수정: {len(auto_fixed)}개")
    lines.append(f"수동 검토 필요: {len(flagged)}개")
    lines.append(f"이상 없음: {ok_count}개\n")

    lines.append(f"\n── 자동 수정 ({len(auto_fixed)}개) ──")
    for word, field, old, new in auto_fixed:
        lines.append(f"  {word:22s}  {field}: {old} → {new}")

    lines.append(f"\n── 수동 검토 필요 ({len(flagged)}개) ──")
    for word, reason in flagged:
        lines.append(f"  {word:22s}  {reason}")

    report = "\n".join(lines)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(report, flush=True)
    print(f"\n보고서 저장: {REPORT_FILE}", flush=True)


if __name__ == "__main__":
    main()
