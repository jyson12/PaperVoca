"""
full_review_fix3.py
전체 재검토 3차: 2000개 전 단어의 뜻(meaning_ko 표제+설명)·영어 정의(en_def)·품사를
예문 기준으로 교정하고, 의미/품사가 어긋난 예문을 재추출하고, IPA를 보완한다.

입력
- data/review3_fixes.tsv : 수기 검토 결과
    word<TAB>pos<TAB>meaning_ko<TAB>en_def   ('=' 는 기존 값 유지)
    #REEX<TAB>word[<TAB>regex]               예문 2개 재추출 (regex: 원하는 의미·품사 용례, 대소문자 구분)
    #RENAME<TAB>old<TAB>new<TAB>pos<TAB>meaning_ko<TAB>en_def   표제어 교정 (표제어화 오류)
- data/ipa_fixes.json : {word: ipa} — Wiktionary 기반 IPA 보완/교체

사용: python scripts/full_review_fix3.py [--dry-run]
"""
import json, sys
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from reextract_examples import forms, load_sentences, pick, is_bad_example  # noqa: E402

VOCAB_FILE = Path("data/vocabulary.json")
FIX_FILE   = Path("data/review3_fixes.tsv")
IPA_FILE   = Path("data/ipa_fixes.json")
POS_KO = {"noun": "명사", "verb": "동사", "adjective": "형용사", "adverb": "부사",
          "preposition": "전치사", "conjunction": "접속사", "pronoun": "대명사",
          "determiner": "한정사"}


def parse_fixes():
    fixes, reex, renames = {}, {}, []
    for line in FIX_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("# "):
            continue
        p = line.split("\t")
        if p[0] == "#REEX":
            reex[p[1]] = p[2] if len(p) > 2 else None
        elif p[0] == "#RENAME":
            renames.append(p[1:])
        else:
            assert len(p) == 4, line
            fixes[p[0]] = p[1:]
    return fixes, reex, renames


def main(dry_run=False):
    data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    words = data["words"]
    fixes, reex, renames = parse_fixes()
    wd = {w["word"]: w for w in words}

    # 1. 표제어 교정
    for old, new, pos, mean, en in renames:
        assert old in wd and new not in wd, (old, new)
        w = wd.pop(old)
        w.update(word=new, lemma=new, pos=pos, pos_ko=POS_KO[pos], meaning_ko=mean, en_def=en)
        wd[new] = w

    # 2. 뜻·품사·영어 정의 교정
    missing = [k for k in fixes if k not in wd]
    assert not missing, missing
    for word, (pos, mean, en) in fixes.items():
        w = wd[word]
        if pos != "=":
            w["pos"], w["pos_ko"] = pos, POS_KO[pos]
        if mean != "=":
            w["meaning_ko"] = mean
        if en != "=":
            w["en_def"] = en

    # 3. IPA 보완/교체
    ipa_fixes = json.loads(IPA_FILE.read_text(encoding="utf-8")) if IPA_FILE.exists() else {}
    for word, ipa in ipa_fixes.items():
        if word in wd:
            wd[word]["ipa"] = ipa

    # 4. 예문 재추출 (지정 단어는 2개 모두 교체)
    missing = [k for k in reex if k not in wd]
    assert not missing, missing
    needed = set().union(*(forms(t) for t in reex)) if reex else set()
    print(f"예문 재추출 대상: {len(reex)}개 — 원문 색인 중…", flush=True)
    sents, index = load_sentences(needed)
    report, partial = [], []
    for word, must in reex.items():
        w = wd[word]
        old = {e["sentence"] for e in w["examples"]}
        new = pick(word, sents, index, old, set(), 2, must=must)
        if len(new) < 2:   # 지정 용례가 부족하면 일반 용례로 보충
            partial.append(word)
            new += pick(word, sents, index, old | {e["sentence"] for e in new},
                        {e["source"] for e in new}, 2 - len(new))
        if len(new) < 2:   # 그래도 부족하면 기존 예문 중 유효한 것 유지
            new += [e for e in w["examples"] if not is_bad_example(word, e["sentence"])][:2 - len(new)]
        report.append({"word": word, "must": must, "old": sorted(old),
                       "new": [e["sentence"] for e in new]})
        w["examples"] = new

    print(f"표제어 교정: {len(renames)}개 / 뜻·품사 교정: {len(fixes)}개 / IPA: {len(ipa_fixes)}개")
    print(f"예문 재추출: {len(report)}개 (지정 용례 부족→일반 보충 {len(partial)}개: {partial})")
    Path("data/review3_reex_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if not dry_run:
        data["meta"]["generated_at"] = str(date.today())
        data["meta"]["word_count"] = len(words)
        VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
