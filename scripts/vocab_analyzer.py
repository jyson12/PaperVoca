"""
vocab-analyzer v2: raw_text/ → data/selected_words.json
개선:
  - NLTK pos_tag_sents로 문맥 기반 정확한 POS 분류
  - -ing 명사(NN/NNS) 보존: training, learning, scaffolding 등
  - 고유명사(NNP/NNPS) 자동 제거: Wang, Chen, Liu 등
  - 접미사 아티팩트 필터 강화: tive, ence, ance 등
파라미터: min_freq=3, top_n=2000
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import nltk

for _res, _pkg in [
    ("tokenizers/punkt_tab",                    "punkt_tab"),
    ("corpora/stopwords",                        "stopwords"),
    ("corpora/wordnet",                          "wordnet"),
    ("taggers/averaged_perceptron_tagger_eng",   "averaged_perceptron_tagger_eng"),
]:
    try:
        nltk.data.find(_res)
    except LookupError:
        nltk.download(_pkg, quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag_sents

RAW_DIR    = Path("raw_text")
DATA_DIR   = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = DATA_DIR / "selected_words.json"

MIN_FREQ = 3
TOP_N    = 2000

STOP_WORDS = set(stopwords.words("english"))

# Penn Treebank → 우리 POS
PENN_TO_POS = {
    "NN": "noun",  "NNS": "noun",
    "VB": "verb",  "VBD": "verb", "VBG": "verb",
    "VBN": "verb", "VBP": "verb", "VBZ": "verb",
    "JJ": "adjective", "JJR": "adjective", "JJS": "adjective",
    "RB": "adverb",    "RBR": "adverb",    "RBS": "adverb",
}

# Penn Treebank → WordNetLemmatizer pos
PENN_TO_LEMMA_POS = {
    "NN": "n",  "NNS": "n",
    "VB": "v",  "VBD": "v", "VBG": "v",
    "VBN": "v", "VBP": "v", "VBZ": "v",
    "JJ": "a",  "JJR": "a", "JJS": "a",
    "RB": "r",  "RBR": "r", "RBS": "r",
}

NOISE_PATTERNS = re.compile(
    r"^(https?|www|doi|isbn|issn|vol|pp|fig|eq|sec|ref|ibid|op|cit|"
    r"chatgpt|gpt|llm|llms|genai|ai|ml|nlp|api|url|pdf|html|xml|csv|"
    r"edu|org|com|gov|net|et|al|ie|eg|etc|vs|cf|nb|"
    r"ing|cod|tion|sion)$",
    re.IGNORECASE
)

# 하이픈 분리 아티팩트 및 접미사 단독 토큰
SUFFIX_ONLY = re.compile(
    r"^(ing|ed|er|est|tion|sion|ment|ness|ity|ize|ise|"
    r"tive|ence|ance|ive|ory|ary|ous|ful|less|able|ible)$",
    re.IGNORECASE
)

BASIC_WORDS = {
    "a","an","the","in","on","at","to","of","for","with","by","from","as","is",
    "are","was","were","be","been","being","have","has","had","do","does","did",
    "will","would","could","should","may","might","shall","can","need","dare",
    "ought","used","that","this","these","those","it","its","he","she","they",
    "we","you","i","me","him","her","us","them","my","your","his","their","our",
    "what","which","who","whom","whose","when","where","why","how","all","both",
    "each","every","either","neither","no","nor","not","only","own","same","so",
    "than","too","very","just","but","if","or","and","because","while","since",
    "study","studies","result","results","show","shows","shown","find","found",
    "use","used","uses","using","provide","provides","provided","based","base",
    "include","includes","including","also","well","however","although","thus",
    "therefore","furthermore","moreover","nevertheless","conclude","conclusion",
    "paper","research","data","model","method","approach","system","analysis",
    "work","works","table","figure","section","example","case","note","due",
    "large","small","high","low","new","good","different","important","possible",
    "first","second","third","last","next","previous","following","general",
    "specific","main","major","other","several","many","few","much","more","most",
    "less","least","such","same","similar","different","various","certain",
    "number","numbers","set","sets","type","types","form","forms","part","parts",
    "point","points","way","ways","time","times","level","levels","group","groups",
    "process","processes","effect","effects","factor","factors","value","values",
    "task","tasks","given","take","taken","make","made","makes","making","two",
    "three","four","five","one","zero","get","gets","got","come","comes","came",
    "go","goes","went","see","seen","know","known","think","thought","say","said",
    "mean","means","call","called","describe","described","present","presented",
    "test","tested","measure","measured","compare","compared","apply","applied",
    "propose","proposed","develop","developed","design","designed","implement",
    "introduce","consider","considered","evaluate","evaluated","examine","investigated",
    "perform","performed","achieve","achieved","obtain","obtained","require","required",
    "suggest","suggested","indicate","indicated","demonstrate","demonstrated",
    "observe","observed","represent","represented","define","defined","discuss",
    "discussed","report","reported","review","reviewed","relate","related","identify",
    "identified","improve","improved","increase","increased","decrease","decreased",
    "become","becomes","became","allow","allows","allowed","involve","involves",
    "affect","affects","affected","influence","influences","influenced","support",
    "supported","contribute","contributes","contributed","address","addressed",
    "focus","focuses","focused","aim","aims","aimed","tend","tends","tended",
    "exist","exists","existed","occur","occurs","occurred","vary","varies","varied",
    "depend","depends","depended","assume","assumes","assumed","expect","expected",
    "approach","question","issue","problem","challenge","aspect","feature","element",
    "component","factor","condition","context","environment","situation","scenario",
    "content","information","knowledge","understanding","ability","capacity",
    "potential","opportunity","benefit","advantage","disadvantage","limitation",
    "sample","participant","student","teacher","user","learner","person","people",
    "group","team","class","school","university","course","program","curriculum",
    "tool","technology","platform","device","application","software","system",
    "online","digital","computer","internet","web","social","media","network",
    "activity","experience","interaction","practice","strategy","technique",
    "objective","goal","criterion","measure","scale","instrument","survey","questionnaire",
    "interview","observation","experiment","simulation","scenario","condition",
    "variable","construct","concept","theory","framework","model","paradigm",
    "approach","perspective","view","opinion","attitude","belief","perception",
    "motivation","engagement","performance","achievement","outcome","result",
    "effect","impact","influence","change","difference","relationship","correlation",
    "association","pattern","trend","characteristic","property","attribute",
    "quality","quantity","degree","extent","level","dimension","aspect","component",
    "phase","stage","step","process","procedure","mechanism","structure","function",
    "role","purpose","function","nature","scope","range","scale","domain",
}

LEMMATIZER = WordNetLemmatizer()


def smart_lemmatize(token: str, penn_pos: str) -> str:
    """Penn Treebank POS 기반 lemmatize.
    -ing으로 끝나고 NN/NNS로 태깅된 경우 명사 gerund → 원형 유지."""
    if token.endswith("ing") and len(token) > 5 and penn_pos in ("NN", "NNS"):
        return token  # training, learning, scaffolding 등 보존
    lem_pos = PENN_TO_LEMMA_POS.get(penn_pos, "n")
    return LEMMATIZER.lemmatize(token, pos=lem_pos)


def is_valid_token(token: str, lemma: str) -> bool:
    if len(token) < 3:
        return False
    if not re.match(r"^[a-zA-Z]+$", token):
        return False
    if token in STOP_WORDS or lemma in STOP_WORDS:
        return False
    if lemma in BASIC_WORDS or token in BASIC_WORDS:
        return False
    if NOISE_PATTERNS.match(token) or NOISE_PATTERNS.match(lemma):
        return False
    if SUFFIX_ONLY.match(token) or SUFFIX_ONLY.match(lemma):
        return False
    if token[0].isdigit():
        return False
    return True


def analyze(txt_files: list, min_freq: int, top_n: int) -> list:
    word_freq:      Counter             = Counter()
    word_docs:      defaultdict         = defaultdict(set)
    word_pos_votes: defaultdict         = defaultdict(Counter)

    SENT_BATCH = 500  # 한 번에 pos_tag_sents에 넘길 문장 수

    print(f"분석 중... {len(txt_files)}개 파일", flush=True)
    for idx, txt_path in enumerate(txt_files, 1):
        try:
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        sentences   = sent_tokenize(text)
        seen_in_doc: set = set()

        for b in range(0, len(sentences), SENT_BATCH):
            batch     = sentences[b : b + SENT_BATCH]
            tokenized = [word_tokenize(s) for s in batch]   # 대소문자 유지 (POS 정확도)
            try:
                tagged_batch = pos_tag_sents(tokenized)
            except Exception:
                continue

            for tagged_sent in tagged_batch:
                for orig_token, penn_pos in tagged_sent:
                    # 고유명사(인명·지명 등) 제거
                    if penn_pos in ("NNP", "NNPS"):
                        continue

                    token = orig_token.lower()
                    if not re.match(r"^[a-zA-Z]+$", token):
                        continue

                    lemma = smart_lemmatize(token, penn_pos)

                    if not is_valid_token(token, lemma):
                        continue

                    key = lemma
                    word_freq[key] += 1
                    word_pos_votes[key][PENN_TO_POS.get(penn_pos, "noun")] += 1
                    seen_in_doc.add(key)

        for w in seen_in_doc:
            word_docs[w].add(txt_path.stem)

        if idx % 100 == 0 or idx == len(txt_files):
            print(f"  [{idx}/{len(txt_files)}] 처리 완료", flush=True)

    candidates = {w: f for w, f in word_freq.items() if f >= min_freq}
    print(f"min_freq={min_freq} 이상 단어: {len(candidates)}개", flush=True)

    scored = []
    for word, freq in candidates.items():
        doc_spread = len(word_docs[word])
        score      = freq * math.log(doc_spread + 1)
        pos        = word_pos_votes[word].most_common(1)[0][0] if word_pos_votes[word] else "noun"
        scored.append({
            "word":       word,
            "lemma":      word,
            "pos":        pos,
            "frequency":  freq,
            "doc_spread": doc_spread,
            "score":      round(score, 2),
            "difficulty": "academic",
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    selected = scored[:top_n]
    print(f"상위 {top_n}개 선별 완료", flush=True)
    return selected


def main():
    txt_files = [f for f in RAW_DIR.glob("*.txt") if f.name != "metadata.json"]
    if not txt_files:
        print("오류: raw_text/ 에 txt 파일이 없습니다.")
        sys.exit(1)

    words = analyze(txt_files, MIN_FREQ, TOP_N)

    output = {
        "meta": {
            "source_dir":    str(RAW_DIR),
            "txt_file_count": len(txt_files),
            "min_freq":      MIN_FREQ,
            "top_n":         TOP_N,
            "word_count":    len(words),
        },
        "words": words,
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장 완료: {OUTPUT_FILE}")
    print("상위 10개 단어 미리보기:")
    for w in words[:10]:
        print(f"  {w['word']:22s}  pos={w['pos']:10s}  빈도={w['frequency']:5d}  논문수={w['doc_spread']:3d}")


if __name__ == "__main__":
    main()
