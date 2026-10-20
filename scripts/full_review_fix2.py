"""
full_review_fix2.py
전체 재검토 2차: 잔여 노이즈 표제어 삭제 + 문자그대로 뜻 교정 + 접두 오매칭 예문 재추출.
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

# 1. 잔여 노이즈 삭제 (단어 조각·약어)
NOISE_DELETE = {"tal", "tor", "pant", "min"}

# 2. 보충 신규 단어
NEW_WORDS = [("prioritise","verb"),("redesign","verb"),("zone","noun"),("withdraw","verb")]
NEW_MEAN = {
    "prioritise":"우선시하다 — 여러 일 중 더 중요한 것을 먼저 처리하도록 순위를 정하다.",
    "redesign":"재설계하다 — 기존의 구조나 방식을 새롭게 다시 설계하다.",
    "zone":"영역 — 특정 목적이나 특성으로 구분되는 구역이나 범위.",
    "withdraw":"철회하다 — 참여·진술·동의 등을 거두어들이거나 중단하다.",
}

# 3. 문자그대로/오역 뜻 → 학술 의미 교정
MEANING_FIXES = {
    "side":("noun","측면 — 어떤 사물이나 문제의 한 부분이나 관점.",
            "An aspect or part of something."),
    "tie":("noun","유대 — 사람·집단·개념 사이의 관계나 연결.",
           "A connection or relationship between people or things."),
    "facet":("noun","측면 — 어떤 대상이 지닌 여러 양상 중 하나.",
             "One of the various aspects or features of something."),
    "era":("noun","시대 — 특정 특징으로 구분되는 역사적·사회적 시기.",
           "A distinct period of time marked by particular characteristics."),
    "live":("adjective","실시간의 — 녹화가 아닌 실시간으로 이루어지는.",
            "Happening in real time rather than recorded."),
    "standing":("noun","지위 — 어떤 집단이나 분야에서 차지하는 위치나 평판.",
                "A person's status, position, or reputation."),
    "lab":("noun","실험실 — 실험과 연구를 수행하는 공간.",
           "A room or facility for scientific experiments and research."),
    "holder":("noun","보유자 — 어떤 지위·자격·자원을 가지고 있는 사람.",
              "A person who holds a position, qualification, or resource."),
    "day":("noun","날 — 하루; 특정한 날짜나 시점.",
           "A period of 24 hours; a particular date or time."),
    "phone":("noun","전화 — 음성 통신 장치; (구어) 스마트폰.",
             "A device for voice communication; a smartphone."),
}

# 4. 접두/부분 오매칭으로 예문이 다른 단어를 가리키는 단어 → 예문 전면 재추출
RE_EXTRACT_ALL = [
    "age","via","add","per","art","bot","fun","exam","rich","span","hint","left",
    "ever","never","though","reform","spread","pilot","press","pass","verb","harm",
    "fact","side","tie","facet","live","head","day","phone","holder","standing",
    "era","lab","back","care","block","solid","home",
]

BAD_SENT = re.compile(r"@|\bEmail\b|\bFunding\b|\bDOI\b|\bORCID\b|©|\bCopyright\b|"
    r"https?://|www\.|\.com\b|\.org\b|\.edu\b|^\s*\d+\s*$|^Table\s+\d|^Figure\s+\d|"
    r"\bISSN\b|\bISBN\b", re.IGNORECASE)
SUF = {'','s','es','ed','ing','d','ly','r','rs','n','ment','ments','ive','ation',
       'al','ally','able','ity','ness','er','ers','ence','ant','ion','ions','en'}

def good(s):
    if BAD_SENT.search(s): return False
    a=sum(1 for c in s if c.isalpha())
    if len(s) and a/len(s)<0.6: return False
    ws=s.split()
    if sum(1 for w in ws if w.isupper() and len(w)>2)>len(ws)*0.3: return False
    return True

def standalone(word, sent):
    """단어가 (굴절 포함) 독립 토큰으로 존재하고, 다른 긴 단어의 접두가 아님."""
    j = re.sub(r'(\w)-\s+(\w)', r'\1\2', sent).lower()
    w = word.lower()
    for m in re.finditer(r'(?<![a-z])'+re.escape(w)+r'([a-z]*)', j):
        if m.group(1) in SUF:
            return True
    return False

def fetch_ipa(word):
    try:
        req=urllib.request.Request(DICT_API.format(word=word.lower()),
                                   headers={"User-Agent":"PaperVoca/1.0"})
        with urllib.request.urlopen(req,timeout=8) as r:
            d=json.loads(r.read().decode("utf-8"))
        e=d[0] if d else {}
        ph=e.get("phonetic","")
        if not ph:
            for p in e.get("phonetics",[]):
                if p.get("text"): ph=p["text"];break
        return ph
    except Exception: return ""

def find_ex(word, txt_files, meta, exclude, n=2):
    import random
    split=re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    random.seed((hash(word)+555)%(2**32))
    out=[]
    for tp in random.sample(txt_files, min(len(txt_files),400)):
        if len(out)>=n: break
        try: text=tp.read_text(encoding="utf-8",errors="ignore")
        except Exception: continue
        for sent in split.split(text):
            sent=re.sub(r"\s+"," ",sent.strip().replace("\n"," "))
            wc=len(sent.split())
            if wc<12 or wc>50: continue
            if not standalone(word,sent): continue
            if not good(sent) or sent in exclude: continue
            out.append({"sentence":sent[:400],
                        "source":meta.get(tp.stem,{}).get("filename",tp.stem+".pdf"),
                        "type":"from_paper"})
            exclude.add(sent)
            if len(out)>=n: break
    return out

def main():
    data=json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    meta=json.loads((RAW_DIR/"metadata.json").read_text(encoding="utf-8"))
    txt_files=[f for f in RAW_DIR.glob("*.txt") if f.name!="metadata.json"]

    # 1. 노이즈 삭제
    removed=[w["word"] for w in data["words"] if w["word"] in NOISE_DELETE]
    data["words"]=[w for w in data["words"] if w["word"] not in NOISE_DELETE]
    wd={w["word"]:w for w in data["words"]}

    # 2. 뜻 교정
    mfix=0
    for word,(pos,mean,en) in MEANING_FIXES.items():
        if word in wd:
            w=wd[word]; w["pos"]=pos; w["pos_ko"]=POS_KO.get(pos,pos)
            w["meaning_ko"]=mean; w["en_def"]=en; mfix+=1

    # 3. 예문 재추출
    exfix=0; dropped=0
    for word in RE_EXTRACT_ALL:
        if word not in wd: continue
        w=wd[word]
        new=find_ex(word, txt_files, meta, set(), n=2)
        if new:
            w["examples"]=new; exfix+=1
        else:
            dropped+=1  # 못 찾으면 기존 유지

    # 4. 보충 신규
    start=len(data["words"])+1; added=[]
    for i,(word,pos) in enumerate(NEW_WORDS):
        if word in wd: continue
        ipa=fetch_ipa(word); time.sleep(0.3)
        exs=find_ex(word, txt_files, meta, set(), n=2)
        data["words"].append({"id":f"w{start+i:04d}","word":word,"lemma":word,
            "pos":pos,"pos_ko":POS_KO.get(pos,pos),"ipa":ipa,
            "meaning_ko":NEW_MEAN[word],"en_def":"","frequency":0,"doc_spread":0,
            "score":0.0,"difficulty":"academic","examples":exs,
            "audio":{"mode":"web_speech","file":None}})
        added.append(word)

    data["meta"]["word_count"]=len(data["words"])
    data["meta"]["generated_at"]=str(date.today())
    VOCAB_FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"노이즈 삭제: {len(removed)}개 ({', '.join(removed)})")
    print(f"뜻 교정: {mfix}개")
    print(f"예문 재추출: {exfix}개 (대체문장 못찾음 {dropped}개)")
    print(f"보충 신규: {len(added)}개 ({', '.join(added)})")
    print(f"최종 단어 수: {len(data['words'])}개")

if __name__=="__main__":
    main()
