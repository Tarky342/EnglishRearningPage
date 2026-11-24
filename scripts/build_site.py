import json
import shutil
from pathlib import Path

root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'questions.json').read_text(encoding='utf-8'))
assert len(bank['questions'])==365
assert len(bank['categories'])==16

template=(root/'app_template.html').read_text(encoding='utf-8')
assert template.count('__DATA__')==1
html=template.replace('__DATA__',json.dumps(bank,ensure_ascii=False,separators=(',', ':')))

site=root/'site'
(site/'assets').mkdir(parents=True,exist_ok=True)
(site/'index.html').write_text(html,encoding='utf-8')
shutil.copy2(root/'assets/tutor-ui.css',site/'assets/tutor-ui.css')
shutil.copy2(root/'assets/tutor-ui.js',site/'assets/tutor-ui.js')
lib=root/'functions/_lib/bank.js'
lib.write_text('export const BANK = '+json.dumps({q['id']:q for q in bank['questions']},ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('built:',site/'index.html','questions:',len(bank['questions']))
