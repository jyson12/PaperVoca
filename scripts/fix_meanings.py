"""
fix_meanings.py
API가 잘못 가져온 정의/번역을 올바른 학술 의미로 교체.
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VOCAB_FILE = Path("data/vocabulary.json")

# (word) → {pos, pos_ko, meaning_ko, en_def}
FIXES = {
    # API가 완전히 다른 단어를 정의한 경우
    "cognitive": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "인지의 — 지각·기억·판단·추론 등 정신적 과정에 관련된.",
        "en_def": "Of or relating to mental processes such as perception, memory, and reasoning."
    },
    "enhance": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "향상시키다 — 품질·가치·능력 등을 더 나아지게 하다.",
        "en_def": "To improve or increase the quality, value, or extent of."
    },
    "effective": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "효과적인 — 원하는 결과를 실제로 달성하는; 효력이 있는.",
        "en_def": "Producing the intended result; having an intended or expected effect."
    },
    "peer": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "동료 — 지위·능력·나이가 같은 사람; 학습 맥락에서 같은 수준의 학습자.",
        "en_def": "A person of the same age, status, or ability as another."
    },
    "foster": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "육성하다 — 발전하거나 성장하도록 장려하고 지원하다.",
        "en_def": "To encourage or promote the development or growth of."
    },
    "qualitative": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "질적인 — 수치가 아닌 성질·특성으로 측정하거나 평가하는.",
        "en_def": "Relating to, measuring, or measured by the quality rather than quantity."
    },
    "comprehensive": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "포괄적인 — 모든 측면이나 요소를 포함하는; 광범위하고 완전한.",
        "en_def": "Including or dealing with all or nearly all elements or aspects."
    },
    "combine": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "결합하다 — 둘 이상의 것을 합치거나 통합하여 하나로 만들다.",
        "en_def": "To merge or unite two or more things into one whole."
    },
    "real": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "실제의 — 실재하거나 사실인; 상상이나 가상이 아닌 실제로 존재하는.",
        "en_def": "Actually existing or occurring in fact; not imagined or supposed."
    },
    "formal": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "공식적인 — 정해진 규칙이나 절차를 따르는; 격식을 갖춘.",
        "en_def": "Following established rules or conventions; official or structured."
    },
    "proficiency": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "숙달 — 특정 분야에서 높은 수준의 기술이나 능력을 갖춘 상태.",
        "en_def": "A high degree of skill or competence in a particular domain."
    },
    "competency": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "역량 — 특정 과제를 성공적으로 수행하는 데 필요한 지식·기술·능력.",
        "en_def": "The ability to do something successfully or efficiently."
    },
    "adoption": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "채택 — 새로운 방법·기술·아이디어를 받아들여 사용하기 시작하는 것.",
        "en_def": "The action of taking up or starting to use something new."
    },
    "addition": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "추가 — 기존의 것에 더하거나 보충하는 것; 첨가.",
        "en_def": "The action or process of adding something to something else."
    },
    "assign": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "배정하다 — 과제·역할·임무를 특정 사람이나 그룹에 할당하다.",
        "en_def": "To allocate a task, role, or responsibility to a specific person or group."
    },
    "display": {
        "pos": "verb", "pos_ko": "동사",
        "meaning_ko": "표시하다 — 정보나 내용을 시각적으로 보여주다; 나타내다.",
        "en_def": "To show or present information in a visible or visual form."
    },
    "global": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "전 세계적인 — 전체 세계에 걸쳐 있거나 영향을 미치는; 포괄적인.",
        "en_def": "Relating to or encompassing the whole world; comprehensive."
    },
    "construction": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "구성 — 지식이나 개념을 만들어 가는 과정; 무언가를 조직하거나 형성하는 행위.",
        "en_def": "The process of building or forming; the way something is organized."
    },
    "right": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "올바른 — 사실에 부합하거나 적절한; 정확하고 적합한.",
        "en_def": "Morally good, justified, or acceptable; factually correct."
    },
    "stress": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "강조 — 특별한 중요성을 두거나 강하게 표현하는 것; (심리) 심리적 압박.",
        "en_def": "Emphasis or importance placed on something; also psychological pressure."
    },
    "body": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "본문 — 글의 주요 내용 부분; 집단·조직의 본체.",
        "en_def": "The main part of a text or document; a group of people or things."
    },
    "short": {
        "pos": "adjective", "pos_ko": "형용사",
        "meaning_ko": "짧은 — 시간이나 길이가 제한된; 간결한.",
        "en_def": "Measuring a small amount in length or duration; brief."
    },
    "confidence": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "자신감 — 자신의 능력이나 판단에 대한 확신; 신뢰.",
        "en_def": "A feeling of trust in one's abilities or knowledge; self-assurance."
    },
    "regard": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "관점 — 어떤 것에 대한 고려나 주의; ~에 관하여.",
        "en_def": "Consideration or concern for; attention or thought given to something."
    },
    # 추가로 발견된 오류들
    "training": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "훈련 — 특정 기술이나 능력을 개발하기 위한 체계적인 연습이나 교육.",
        "en_def": "Systematic practice or education to develop skill or knowledge."
    },
    "prompt": {
        "pos": "noun", "pos_ko": "명사",
        "meaning_ko": "프롬프트 — 행동이나 응답을 유도하는 신호, 지시문, 또는 단서.",
        "en_def": "A cue or instruction that elicits a response or action."
    },
}


def main():
    data   = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    fixed  = 0
    for w in data["words"]:
        word = w["word"]
        if word in FIXES:
            f = FIXES[word]
            w["pos"]        = f["pos"]
            w["pos_ko"]     = f["pos_ko"]
            w["meaning_ko"] = f["meaning_ko"]
            if "en_def" in f:
                w["en_def"] = f["en_def"]
            fixed += 1

    VOCAB_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"뜻/품사 수정 완료: {fixed}개")
    print("vocabulary.json 저장 완료")


if __name__ == "__main__":
    main()
