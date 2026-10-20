"""vocabulary.json 의 IPA 점검 (QA 보조, 읽기 전용).

1) CMUdict(미국식) 대조 — 모음 체계가 달라 자음 골격 + 1차 강세 음절 위치만 비교한다.
   RP 비R음화(모음 뒤 r 탈락)와 요드(tj/dj/nj…) 차이는 정규화한다.
2) 표기 스캔 — 미국식(ɚ ɝ oʊ, 짧은 ɑ, 모음 뒤 ɹ), 협의 표기(ɾ ɫ), ASCII r/g, 강세 표시 누락,
   방언식 이중모음(ʌɪ ʌʊ ɒʊ …).
3) 품사별 발음이 갈리는 단어(record, conduct, -ate 동사/형용사 등) 목록.

불일치가 곧 오류는 아니다 — RP 고유 발음(laboratory, schedule 등)도 걸리므로 사람이 판단하고,
고칠 항목은 data/ipa_fixes.json 에 넣은 뒤 scripts/apply_ipa_fixes.py 로 적용한다.

준비: python -c "import nltk; nltk.download('cmudict')"
사용법: python scripts/check_ipa.py   → data/ipa_check_report.json
"""
import json
import re
import sys
from pathlib import Path

from nltk.corpus import cmudict

sys.stdout.reconfigure(encoding="utf-8")

VOCAB_FILE = Path("data/vocabulary.json")
REPORT = Path("data/ipa_check_report.json")

ARPA_C = {"P": "p", "B": "b", "T": "t", "D": "d", "K": "k", "G": "ɡ", "CH": "C", "JH": "J",
          "F": "f", "V": "v", "TH": "θ", "DH": "ð", "S": "s", "Z": "z", "SH": "ʃ", "ZH": "ʒ",
          "HH": "h", "M": "m", "N": "n", "NG": "ŋ", "L": "l", "R": "ɹ", "W": "w", "Y": "j"}
IPA_VOWELS = "aeiouæɑɒɔəɛɜɪʊʌɐ"
YOD_RE = re.compile(r"(?<=[tdnszlθ])j")

STYLE_PATTERNS = {
    "미국식 ɚ/ɝ": r"[ɚɝ]",
    "미국식 oʊ": r"oʊ",
    "미국식 짧은 ɑ": r"ɑ(?!ː)",
    "모음 뒤 ɹ": rf"[{IPA_VOWELS}ː]ɹ(?![{IPA_VOWELS}ˈˌ.)])",
    "협의 표기 ɾ/ɫ": r"[ɾɫ]",
    "ASCII r/g": r"[rg]",
    "방언식 이중모음": r"ʌɪ|ʌʊ|ɒʊ|ɑe|æe|ɒe|ɛː|eː",
    "hw": r"hw",
}


def cmu_parse(phones):
    """CMU 음소열 → (자음 골격, 1차 강세 모음 index)."""
    out, vowels, stress = [], 0, None
    for i, ph in enumerate(phones):
        base = re.sub(r"\d", "", ph)
        nxt_is_vowel = i + 1 < len(phones) and phones[i + 1][-1].isdigit()
        if base in ARPA_C:
            if base == "R" and not nxt_is_vowel:  # 모음 앞이 아니면 RP에서 탈락
                continue
            out.append(ARPA_C[base])
        else:
            if ph.endswith("1") and stress is None:
                stress = vowels
            if base == "ER" and nxt_is_vowel:  # 모음 앞 ER은 r 연결
                out.append("ɹ")
            vowels += 1
    return YOD_RE.sub("", "".join(out)), stress


def ipa_parse(ipa):
    """IPA → (자음 골격, 1차 강세 음절 index, 음절(모음군) 수)."""
    s = ipa.strip().strip("/[]").split(",")[0].strip()
    s = s.replace("͡", "").replace("(ɹ)", "").replace("(r)", "")
    s = s.replace("tʃ", "C").replace("dʒ", "J")
    s = s.replace("g", "ɡ").replace("r", "ɹ").replace("ɾ", "t").replace("ɫ", "l")
    s = s.replace("ɚ", "ə").replace("ɝ", "ɜ")
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(rf"ɹ(?![{IPA_VOWELS}ˈˌ.])", "", s)
    s = re.sub(r"[ː.ˑ̩̯‿ʔ ]", "", s)
    skel, vowels, stress, prev_v = [], 0, None, False
    for ch in s:
        if ch in "ˈˌ":
            if ch == "ˈ" and stress is None:
                stress = vowels
            prev_v = False
        elif ch in IPA_VOWELS:
            vowels += 0 if prev_v else 1
            prev_v = True
        else:
            prev_v = False
            skel.append(ch)
    if stress is None and vowels == 1:
        stress = 0
    return YOD_RE.sub("", "".join(skel)), stress, vowels


def main():
    vocab = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    words = vocab["words"] if isinstance(vocab, dict) else vocab
    cmu = cmudict.dict()

    mismatch, missing, hetero, style = [], [], [], []
    for w in words:
        word, ipa, pos = w["word"], w.get("ipa") or "", w.get("pos")
        skel, st, nv = ipa_parse(ipa)

        body = ipa.strip("/")
        hits = [k for k, p in STYLE_PATTERNS.items() if re.search(p, body)]
        if nv >= 2 and "ˈ" not in body:
            hits.append("강세 표시 없음")
        if hits:
            style.append({"word": word, "pos": pos, "ipa": ipa, "issues": hits})

        prons = cmu.get(word.lower())
        if not prons:
            missing.append({"word": word, "pos": pos, "ipa": ipa})
            continue
        cands = [cmu_parse(p) for p in prons]
        if len({c[1] for c in cands}) > 1:
            hetero.append({"word": word, "pos": pos, "ipa": ipa, "cmu": [" ".join(p) for p in prons]})
        skel_ok = any(c[0] == skel for c in cands)
        stress_ok = any(c[1] == st for c in cands) or (st is None and nv <= 1)
        if not (skel_ok and stress_ok):
            mismatch.append({
                "word": word, "pos": pos, "ipa": ipa,
                "issue": ("자음" if not skel_ok else "") + ("강세" if not stress_ok else ""),
                "cmu": [" ".join(p) for p in prons],
            })

    report = {"cmu_mismatch": mismatch, "style": style, "pos_dependent": hetero,
              "not_in_cmu": missing}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"CMU 불일치 {len(mismatch)} / 표기 문제 {len(style)} / 품사별 발음 {len(hetero)} "
          f"/ CMU 미등재 {len(missing)} → {REPORT}")


if __name__ == "__main__":
    main()
