"""
reextract_examples.py
전체 2000개 예문을 엄격 기준으로 검증하고, 불합격 예문만 논문 원문에서 재추출한다.

검증 기준 (CLAUDE.md QA 1단계 강화판)
- 하이픈/소프트하이픈 분절을 합친 뒤, 표제어의 **굴절형만** 허용
  (s/es/d/ed/ing/er/est, e탈락, y→i, 자음중복). 파생 접미사(ly/en/ation…)는
  다른 단어로 본다 (like→likely, deep→deepen, cognitive→cognitively 방지).
- 하이픈 복합어 안의 매칭(face-to-face, long-term)·문장 중간 대문자(고유명사)는 후순위.
- 라이선스·키워드·저자기여·윤리승인 등 보일러플레이트 문장 불합격.

사용: python scripts/reextract_examples.py [--dry-run]
"""
import json, re, sys, hashlib
from pathlib import Path
from collections import defaultdict
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

VOCAB_FILE = Path("data/vocabulary.json")
RAW_DIR    = Path("raw_text")
REPORT     = Path("data/reextract_report.json")

BOILER = re.compile(
    r"Creative Commons|licen[cs]ed under|Open Access|All rights reserved|text and data mining|"
    r"How to cite|Author contributions|Conflicts? of interest|Competing (financial )?interest|Ethics approval|"
    r"Data availability|Corresponding author|Published online|Received:|Accepted:|Keywords?:|"
    r"\bpp\.\s*\d|\bVol\.\s*\d|\bdoi\b|https?://|www\.|@|©|\bISSN\b|\bISBN\b|\bORCID\b|"
    r"\bFunding\s*(?::|information|statement|This|The)|\bEmail\b",
    re.I)
HEADING = re.compile(r"\b(INTRODUCTION|METHODS?|RESULTS|DISCUSSION|CONCLUSIONS?|ABSTRACT|"
                     r"REFERENCES|ACKNOWLEDGE?MENTS?|STATEMENT|BACKGROUND|LIMITATIONS)\b")
# fi/fl 합자 누락으로 생긴 조각 토큰 (arti cial, signi cant, in uence …)
FRAG = {"cant", "cantly", "cally", "cation", "cations", "cient", "ciently", "cult", "culty",
        "culties", "cial", "ned", "nition", "nitions", "nd", "nds", "ndings", "nding", "rst",
        "eld", "elds", "nal", "nally", "gure", "gures", "ect", "ects", "ected", "ection",
        "ections", "uence", "uenced", "uences", "dence", "ict", "icts", "exible", "exibility",
        "xed", "nancial", "nance", "nish", "nished", "rm", "rms", "ts", "tting"}
PROPER_OK = {"british", "chinese", "european", "american", "japanese"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z’']*")


def _common_words():
    """문장 중간에 대문자로 나오면 안 되는 일반어 (불용어 + 단어장 표제어)."""
    words = set()
    try:
        from nltk.corpus import stopwords
        words |= set(stopwords.words("english"))
    except Exception:  # noqa: BLE001 — nltk 데이터가 없으면 단어장만 사용
        pass
    if VOCAB_FILE.exists():
        words |= {w["word"] for w in json.loads(VOCAB_FILE.read_text(encoding="utf-8"))["words"]}
    return words - PROPER_OK - {"english"}


COMMON = _common_words()
MIDCAP_RE = re.compile(r"(?<=[a-z,] )([A-Z][a-z]+) (?=[a-z])")   # '… education Recent developments'
ACRO_HEAD_RE = re.compile(r"\b[A-Z]{2,} (The|This|These|In|We|Our|It) ")  # '… in VR The VRSCT …'


def forms(w):
    """표제어의 굴절형 집합."""
    w = w.lower()
    f = {w, w+"s", w+"es", w+"d", w+"ed", w+"ing", w+"er", w+"est", w+"'s", w+"’s"}
    if w.endswith("e"):
        f |= {w[:-1]+s for s in ("ing", "ed", "er", "est")}
    if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
        f |= {w[:-1]+s for s in ("ies", "ied", "ier", "iest")}
    if len(w) >= 3 and w[-1] not in "aeiouwxy" and w[-2] in "aeiou" and w[-3] not in "aeiou":
        f |= {w+w[-1]+s for s in ("ed", "ing", "er", "est")}
    if w.endswith("ic"):
        f |= {w+"k"+s for s in ("ed", "ing")}
    return f


def clean(s):
    s = re.sub(r"­\s*", "", s)                                   # 소프트 하이픈
    s = re.sub(r"([a-z])- (?!(?:and|or|to|and/or)\b)([a-z])", r"\1\2", s)  # in- stance → instance
    return re.sub(r"\s+", " ", s).strip()


def contains(word, sent):
    fs = forms(word)
    return any(t.lower() in fs for t in WORD_RE.findall(clean(sent)))


def is_bad_example(word, sent):
    return (not contains(word, sent)) or bool(BOILER.search(sent)) or is_broken(clean(sent))


def good_sentence(s):
    wc = len(s.split())
    if wc < 12 or wc > 40: return False
    if BOILER.search(s): return False
    if sum(c.isalpha() or c == " " for c in s) / len(s) < 0.85: return False
    if sum(c.isdigit() for c in s) / len(s) > 0.06: return False
    return not is_broken(s)


def is_broken(s):
    """PDF 추출 과정에서 깨진 문장 (잘림·병합·제목·머리말·합자 누락 등)."""
    if not re.match(r"^[A-Z“\"‘']", s): return True
    if not re.search(r"[.!?][”\"’')]?$", s): return True
    if re.search(r"[.!?]\s+[a-z]", s): return True             # 문장 병합 흔적
    if re.search(r"[.!?][”\"’]\s+[A-Z]", s): return True       # 인용 뒤 다음 문장 병합
    if re.search(r"[a-z]{3,}[.!?]\s+\d", s): return True        # '… progress. 3.5.' 절 번호 꼬리
    if re.search(r"\b[A-Z]\.$", s): return True                  # 'J.' 등 머리말 꼬리
    if re.search(r"[a-z]{2,}\d", s): return True                # 'Fryer1,4' 저자 각주 번호
    if re.search(r"\d+ / \d+", s): return True                  # '14 / 18' 쪽 번호 머리말
    if re.search(r"[-]", s): return True            # 설문 체크박스 등 사설 영역 글리프
    if re.search(r"\b[A-Z] [A-Z] [A-Z] [A-Z]\b", s): return True  # 'K E Y W O R D S' 자간 분리 제목
    if re.match(r"(Introduction|Conclusions?|Discussion|Results?|Methods?|Background|Abstract|"
                r"Summary)\s+[A-Z]", s): return True              # 절 제목 + 본문 병합
    if re.search(r"[A-Za-z,] (The|A|An|This|These|Those|Our|We|It|In|To|For) [a-z]", s):
        return True                                              # 소제목 + 본문 병합
    if re.search(r": [A-Z]", s) and not re.search(
            r"\b(is|are|was|were|has|have|had|can|could|will|would|may|might|should|did|does|do)\b", s):
        return True                                              # 참고문헌 제목
    if re.search(r"\?: [A-Z]|: (A|An|The) [\w-]+ (study|review|analysis|approach|framework|"
                 r"investigation|perspective|meta-analysis|case|exploration|examination)\b", s):
        return True                                              # 참고문헌 제목 (부제)
    if re.match(r"(Table|Figure|Fig\.)\s*\d", s): return True   # 표·그림 캡션
    if re.search(r"\s\d+(\.\d+)+\.?$", s): return True          # 'status 2.2.' 절 번호 꼬리
    if re.search(r"[a-z]\.[A-Z][a-z]", s): return True          # 마침표 뒤 공백 없는 병합
    if re.search(r"\(\d\.\d{4,}\)", s): return True             # 설문 문항 부하량 표
    if re.search(r"[A-Z][a-z]+ / [A-Z]", s): return True        # 표 셀 병합
    if re.search(r"[぀-鿿가-힯]", s): return True  # 한중일 문자 혼입
    if any(t.lower() in COMMON for t in MIDCAP_RE.findall(s)): return True  # 소제목·표 셀 병합
    if ACRO_HEAD_RE.search(s): return True
    if re.search(r"\b(Table|Figure|Fig\.) \d+\.?$", s): return True   # 캡션 꼬리
    if re.search(r"\b([A-Z][a-z]+) \1\b", s): return True             # 'Hallucination Hallucination' 제목 반복
    if HEADING.search(s): return True
    if any(t.lower() in FRAG for t in WORD_RE.findall(s)): return True
    return False


def load_sentences(needed_forms):
    """needed_forms에 속한 토큰을 포함하는 양질의 문장만 색인."""
    meta = json.loads((RAW_DIR/"metadata.json").read_text(encoding="utf-8"))
    split = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")
    sents, index = [], defaultdict(list)
    for tp in sorted(RAW_DIR.glob("*.txt")):
        if tp.name.startswith("0_"):   # 저널 front matter 제외
            continue
        text = tp.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"(\w)-\s*\n\s*([a-z])", r"\1\2", text)
        src = meta.get(tp.stem, {}).get("filename", tp.stem + ".pdf")
        for raw in split.split(text):
            s = clean(raw.replace("\n", " "))
            if not good_sentence(s):
                continue
            toks = {t.lower() for t in WORD_RE.findall(s)} & needed_forms
            if not toks:
                continue
            sid = len(sents)
            sents.append((s, src))
            for t in toks:
                index[t].append(sid)
    return sents, index


def occurrence_quality(word, sent):
    """0=최상(표제어 원형, 소문자, 복합어 아님) … 클수록 후순위. None=매칭 없음."""
    fs, w = forms(word), word.lower()
    best = None
    for m in WORD_RE.finditer(sent):
        t = m.group(0)
        if t.lower() not in fs:
            continue
        q = 0
        if t.lower() != w: q += 1
        before, after = sent[max(0, m.start()-1):m.start()], sent[m.end():m.end()+1]
        if before == "-" or after == "-": q += 4
        if t[0].isupper() and m.start() > 0 and w not in PROPER_OK: q += 6
        if t.isupper() and len(t) > 1: q += 6
        best = q if best is None else min(best, q)
    return best


def pick(word, sents, index, exclude_sents, exclude_srcs, n, must=None):
    """must: 문장이 반드시 매칭해야 하는 정규식(대소문자 구분) — 특정 의미·품사 용례 지정용."""
    cand = set()
    for f in forms(word):
        cand.update(index.get(f, []))
    scored = []
    for sid in cand:
        s, src = sents[sid]
        if s in exclude_sents:
            continue
        if must and not re.search(must, s):
            continue
        q = occurrence_quality(word, s)
        if q is None:
            continue
        wc = len(s.split())
        lenpen = 0 if 15 <= wc <= 32 else 1
        h = hashlib.md5((word + s).encode("utf-8")).hexdigest()
        scored.append((q, lenpen, h, s, src))
    scored.sort()
    out, used_src = [], set(exclude_srcs)
    for q, _, _, s, src in scored:        # 1차: 출처 중복 회피
        if len(out) >= n: break
        if src in used_src: continue
        out.append({"sentence": s, "source": src, "type": "from_paper"}); used_src.add(src)
    for q, _, _, s, src in scored:        # 2차: 부족하면 출처 중복 허용
        if len(out) >= n: break
        if any(o["sentence"] == s for o in out): continue
        out.append({"sentence": s, "source": src, "type": "from_paper"})
    return out


def load_musts():
    """data/review3_fixes.tsv 의 '#REEX⇥word⇥정규식' — 단어별로 지정된 의미·품사 용례."""
    path = Path("data/review3_fixes.tsv")
    musts = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            p = line.split("\t")
            if p[0] == "#REEX" and len(p) > 2:
                musts[p[1]] = p[2]
    return musts


def main(dry_run=False):
    data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    words = data["words"]
    cleaned = 0
    for w in words:                       # 하이픈 분절·소프트하이픈 정리 (표제어가 유지될 때만)
        for e in w["examples"]:
            c = clean(e["sentence"])
            if c != e["sentence"] and contains(w["word"], c):
                e["sentence"] = c; cleaned += 1
    print(f"분절 정리된 예문: {cleaned}개")
    targets = {w["word"] for w in words
               if len(w["examples"]) < 2 or any(is_bad_example(w["word"], e["sentence"]) for e in w["examples"])}
    if not targets:                       # 불합격 예문 없음 → 보고서·단어장을 건드리지 않고 종료
        print("재추출 대상 단어: 0개 — 모든 예문이 검증을 통과했습니다.")
        if cleaned and not dry_run:
            VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    needed = set().union(*(forms(t) for t in targets))
    print(f"재추출 대상 단어: {len(targets)}개 — 원문 색인 중…", flush=True)
    sents, index = load_sentences(needed)
    print(f"색인 문장: {len(sents)}개", flush=True)

    musts = load_musts()
    report, failed = [], []
    for w in words:
        if w["word"] not in targets:
            continue
        keep = [e for e in w["examples"] if not is_bad_example(w["word"], e["sentence"])]
        must = musts.get(w["word"])
        new = pick(w["word"], sents, index, {e["sentence"] for e in keep},
                   {e["source"] for e in keep}, 2 - len(keep), must=must)
        if must and len(keep) + len(new) < 2:   # 지정 용례가 부족하면 일반 용례로 보충
            new += pick(w["word"], sents, index, {e["sentence"] for e in keep + new},
                        {e["source"] for e in keep + new}, 2 - len(keep) - len(new))
        if not new:
            failed.append(w["word"]); continue
        report.append({"word": w["word"],
                       "old": [e["sentence"] for e in w["examples"] if e not in keep],
                       "new": [e["sentence"] for e in new]})
        w["examples"] = keep + new

    print(f"재추출 완료: {len(report)}개 / 대체 문장 없음: {len(failed)}개 {failed}")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if not dry_run:
        data["meta"]["generated_at"] = str(date.today())
        VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
