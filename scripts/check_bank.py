import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'questions.json').read_text(encoding='utf-8'))
seen=set()
for q in bank['questions']:
    assert q['id'] not in seen
    seen.add(q['id'])
    assert len(q['choices'])==4 and 0<=q['answer']<4
    assert q['stem'] and q['explanation']
assert len(seen)==365
assert len(bank['categories'])==16
print('OK',len(seen),'questions',len(bank['categories']),'categories')
