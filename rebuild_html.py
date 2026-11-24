"""Generate a standalone HTML app with the current question bank."""
import json
from pathlib import Path

base = Path(__file__).resolve().parent
data = json.loads((base / 'questions.json').read_text(encoding='utf-8'))
questions = data['questions']
assert len({q['id'] for q in questions}) == len(questions)
assert all(0 <= q['answer'] < len(q['choices']) for q in questions)
html = (base / 'app_template.html').read_text(encoding='utf-8')
assert html.count('__DATA__') == 1
packed = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
(base / 'index.html').write_text(html.replace('__DATA__', packed), encoding='utf-8')
print(f'Wrote index.html ({len(questions)} questions)')
