import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const bank=JSON.parse(fs.readFileSync(path.join(root,'questions.json'),'utf8'));
const seen=new Set();
for(const q of bank.questions){
  if(seen.has(q.id))throw new Error(`重複ID: ${q.id}`);
  seen.add(q.id);
  if(q.choices.length!==4||q.answer<0||q.answer>=4)throw new Error(`選択肢が不正: ${q.id}`);
  if(!q.stem||!q.explanation)throw new Error(`本文または解説が不足: ${q.id}`);
}
if(seen.size!==365)throw new Error(`問題数が${seen.size}です`);
if(bank.categories.length!==16)throw new Error(`カテゴリ数が${bank.categories.length}です`);
console.log(`OK ${seen.size} questions ${bank.categories.length} categories`);
