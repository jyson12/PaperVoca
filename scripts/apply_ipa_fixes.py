"""data/ipa_fixes.json 의 IPA 교정을 vocabulary.json 에 적용한다 (재실행 안전).

ipa_fixes.json 은 {word: ipa} 형식의 IPA 교정 원장이다.
- 3차 검토: Wiktionary 기반 보완 (full_review_fix3.py 가 최초 적용)
- 4차 검토: CMUdict 대조(scripts/check_ipa.py) 후 RP 기준 수기 교정

사용법:
    python scripts/apply_ipa_fixes.py            # 적용
    python scripts/apply_ipa_fixes.py --dry-run  # 바뀔 항목만 출력
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

VOCAB_FILE = Path("data/vocabulary.json")
IPA_FILE = Path("data/ipa_fixes.json")


def main(dry_run: bool) -> None:
    vocab = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    words = vocab["words"] if isinstance(vocab, dict) else vocab
    fixes = json.loads(IPA_FILE.read_text(encoding="utf-8"))
    wd = {w["word"]: w for w in words}

    missing = [k for k in fixes if k not in wd]
    changed = []
    for word, ipa in fixes.items():
        w = wd.get(word)
        if w is not None and w.get("ipa") != ipa:
            changed.append((word, w.get("ipa"), ipa))
            w["ipa"] = ipa

    for word, old, new in changed:
        print(f"  {word}: {old} → {new}")
    print(f"IPA 교정 원장 {len(fixes)}개 / 변경 {len(changed)}개 / 단어장에 없는 항목 {len(missing)}개")
    if missing:
        print("  없는 항목:", ", ".join(missing))
    if changed and not dry_run:
        VOCAB_FILE.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"저장: {VOCAB_FILE}")


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
