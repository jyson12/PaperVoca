"""
fix_duplicate_ids.py
단어 추가 스크립트가 '현재 개수+1'부터 id를 매기면서 생긴 중복 id를 정리한다.
첫 번째 항목은 그대로 두고, 이후 중복 항목에 w0001~w{N} 중 비어 있는 번호를 차례로 배정한다.

사용: python scripts/fix_duplicate_ids.py
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VOCAB_FILE = Path("data/vocabulary.json")

data = json.loads(VOCAB_FILE.read_text(encoding="utf-8"))
words = data["words"]
used, dups = set(), []
for w in words:
    if w["id"] in used:
        dups.append(w)
    used.add(w["id"])
free = [f"w{i:04d}" for i in range(1, len(words) + 1) if f"w{i:04d}" not in used]
assert len(free) >= len(dups), (len(free), len(dups))
for w, new_id in zip(dups, free):
    print(f"  {w['word']:20s} {w['id']} → {new_id}")
    w["id"] = new_id
assert len({w["id"] for w in words}) == len(words)
VOCAB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"중복 id 재배정: {len(dups)}개")
