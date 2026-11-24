import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const bank=JSON.parse(fs.readFileSync(path.join(root,'questions.json'),'utf8'));
if(bank.questions.length!==365)throw new Error('問題数が365ではありません');
if(bank.categories.length!==16)throw new Error('カテゴリ数が16ではありません');

const template=fs.readFileSync(path.join(root,'app_template.html'),'utf8');
if(template.split('__DATA__').length!==2)throw new Error('テンプレートの埋込み場所が不正です');
const html=template.replace('__DATA__',JSON.stringify(bank).replaceAll('</','<\\/'));

fs.writeFileSync(path.join(root,'index.html'),html,'utf8');
const site=path.join(root,'site');
fs.mkdirSync(path.join(site,'assets'),{recursive:true});
fs.writeFileSync(path.join(site,'index.html'),html,'utf8');
fs.copyFileSync(path.join(root,'assets','tutor-ui.css'),path.join(site,'assets','tutor-ui.css'));
fs.copyFileSync(path.join(root,'assets','tutor-ui.js'),path.join(site,'assets','tutor-ui.js'));

const byId=Object.fromEntries(bank.questions.map(q=>[q.id,q]));
fs.mkdirSync(path.join(root,'functions','_lib'),{recursive:true});
fs.writeFileSync(path.join(root,'functions','_lib','bank.js'),`export const BANK = ${JSON.stringify(byId)};\n`,'utf8');
console.log(`built: ${site}${path.sep}index.html (${bank.questions.length} questions)`);
