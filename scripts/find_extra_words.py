"""
find_extra_words.py
vocab_analyzer와 동일한 로직으로 top 2100을 분석,
현재 vocabulary.json에 없는 후보 단어를 순위순으로 출력.
"""
import json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import nltk
for _res, _pkg in [
    ("tokenizers/punkt_tab",                  "punkt_tab"),
    ("corpora/stopwords",                      "stopwords"),
    ("corpora/wordnet",                        "wordnet"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
]:
    try:
        nltk.data.find(_res)
    except LookupError:
        nltk.download(_pkg, quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag_sents

RAW_DIR   = Path("raw_text")
VOCAB_FILE = Path("data/vocabulary.json")
OUT_FILE   = Path("data/extra_candidates.json")

TOP_N    = 2100   # 기존 2000 + 여유 100
MIN_FREQ = 3

STOP_WORDS = set(stopwords.words("english"))

PENN_TO_POS = {
    "NN":"noun","NNS":"noun",
    "VB":"verb","VBD":"verb","VBG":"verb","VBN":"verb","VBP":"verb","VBZ":"verb",
    "JJ":"adjective","JJR":"adjective","JJS":"adjective",
    "RB":"adverb","RBR":"adverb","RBS":"adverb",
}
PENN_TO_LEMMA_POS = {
    "NN":"n","NNS":"n",
    "VB":"v","VBD":"v","VBG":"v","VBN":"v","VBP":"v","VBZ":"v",
    "JJ":"a","JJR":"a","JJS":"a",
    "RB":"r","RBR":"r","RBS":"r",
}

NOISE_PATTERNS = re.compile(
    r"^(https?|www|doi|isbn|issn|vol|pp|fig|eq|sec|ref|ibid|op|cit|"
    r"chatgpt|gpt|llm|llms|genai|ai|ml|nlp|api|url|pdf|html|xml|csv|"
    r"edu|org|com|gov|net|et|al|ie|eg|etc|vs|cf|nb|"
    r"ing|cod|tion|sion)$",
    re.IGNORECASE
)
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


def smart_lemmatize(token, penn_pos):
    if token.endswith("ing") and len(token) > 5 and penn_pos in ("NN","NNS"):
        return token
    lem_pos = PENN_TO_LEMMA_POS.get(penn_pos, "n")
    return LEMMATIZER.lemmatize(token, pos=lem_pos)


def is_valid_token(token, lemma):
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


def main():
    txt_files = [f for f in RAW_DIR.glob("*.txt") if f.name != "metadata.json"]
    print(f"파일: {len(txt_files)}개 분석 시작...", flush=True)

    word_freq      = Counter()
    word_docs      = defaultdict(set)
    word_pos_votes = defaultdict(Counter)
    SENT_BATCH     = 500

    for idx, txt_path in enumerate(txt_files, 1):
        try:
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        sentences   = sent_tokenize(text)
        seen_in_doc = set()

        for b in range(0, len(sentences), SENT_BATCH):
            batch     = sentences[b:b+SENT_BATCH]
            tokenized = [word_tokenize(s) for s in batch]
            try:
                tagged_batch = pos_tag_sents(tokenized)
            except Exception:
                continue
            for tagged_sent in tagged_batch:
                for orig_token, penn_pos in tagged_sent:
                    if penn_pos in ("NNP", "NNPS"):
                        continue
                    token = orig_token.lower()
                    if not re.match(r"^[a-zA-Z]+$", token):
                        continue
                    lemma = smart_lemmatize(token, penn_pos)
                    if not is_valid_token(token, lemma):
                        continue
                    word_freq[lemma] += 1
                    word_pos_votes[lemma][PENN_TO_POS.get(penn_pos,"noun")] += 1
                    seen_in_doc.add(lemma)

        for w in seen_in_doc:
            word_docs[w].add(txt_path.stem)

        if idx % 100 == 0 or idx == len(txt_files):
            print(f"  [{idx}/{len(txt_files)}] 처리 완료", flush=True)

    candidates = {w: f for w, f in word_freq.items() if f >= MIN_FREQ}
    scored = []
    for word, freq in candidates.items():
        doc_spread = len(word_docs[word])
        score      = freq * math.log(doc_spread + 1)
        pos        = word_pos_votes[word].most_common(1)[0][0] if word_pos_votes[word] else "noun"
        scored.append({"word":word,"lemma":word,"pos":pos,
                        "frequency":freq,"doc_spread":doc_spread,
                        "score":round(score,2),"difficulty":"academic"})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:TOP_N]

    # 현재 vocabulary에 없는 단어만 추출
    voc  = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
    voc_set = {w["word"] for w in voc["words"]}
    extras = [w for w in top if w["word"] not in voc_set]

    OUT_FILE.write_text(json.dumps({"words": extras}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {OUT_FILE}  ({len(extras)}개)")

    # 순위 조회용 인덱스
    scored_index = {w["word"]: i + 1 for i, w in enumerate(scored)}

    print(f"\n=== 추가 후보 ({len(extras)}개, 상위 50개 표시) ===")
    for w in extras[:50]:
        rank = scored_index.get(w["word"], "?")
        print(f"  rank={str(rank):>4s}  {w['word']:25s}  pos={w['pos']:10s}  "
              f"freq={w['frequency']:5d}  spread={w['doc_spread']:3d}  score={w['score']:.1f}")


if __name__ == "__main__":
    main()
