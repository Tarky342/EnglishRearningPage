import test from 'node:test';
import assert from 'node:assert/strict';
import { onRequestPost } from '../functions/api/tutor.js';
import { validateTutorOutput } from '../functions/_lib/schema.js';

const URL='https://example.pages.dev/api/tutor';
function request(body,origin='https://example.pages.dev'){
  return new Request(URL,{method:'POST',headers:{'Content-Type':'application/json',Origin:origin,'CF-Connecting-IP':'203.0.113.1'},body:JSON.stringify(body)});
}
const base={questionId:'q0001',action:'explain',selectedIndex:2};
const allowed={limit:async()=>({success:true})};
const sample={title:'三人称単数',explanation:'The officeは単数なのでopensを使います。',keyPoint:'三人称単数',hint:'主語に注目',check:{stem:'The offices ___ early every day.',choices:['open','opens'],answerIndex:0,reasoning:'主語が複数なのでopen。'}};

test('365問はサーバー側mockで動作する',async()=>{
  const r=await onRequestPost({request:request(base),env:{APP_ENV:'local',AI_MOCK_MODE:'1'}});
  assert.equal(r.status,200);
  const j=await r.json();
  assert.equal(j.mode,'mock');
  assert.match(j.tutor.explanation,/opens/);
});
test('不正originを拒否',async()=>{
  const r=await onRequestPost({request:request(base,'https://evil.example'),env:{APP_ENV:'local',AI_MOCK_MODE:'1'}});
  assert.equal(r.status,403);
});
test('存在しない問題IDを拒否',async()=>{
  const r=await onRequestPost({request:request({...base,questionId:'q9999'}),env:{APP_ENV:'local',AI_MOCK_MODE:'1'}});
  assert.equal(r.status,400);
});
test('不正な選択肢を拒否',async()=>{
  const r=await onRequestPost({request:request({...base,selectedIndex:22}),env:{APP_ENV:'local',AI_MOCK_MODE:'1'}});
  assert.equal(r.status,400);
});
test('本番設定不足はfail closed',async()=>{
  const r=await onRequestPost({request:request(base),env:{OPENAI_API_KEY:'redacted'}});
  assert.equal(r.status,503);
});
test('レート超過を拒否',async()=>{
  const r=await onRequestPost({request:request(base),env:{OPENAI_API_KEY:'redacted',AI_RATE_LIMITER:{limit:async()=>({success:false})}}});
  assert.equal(r.status,429);
});
test('スキーマ検証',()=>{
  assert.ok(validateTutorOutput(sample,'The office ___ at nine every weekday.'));
  assert.equal(validateTutorOutput({...sample,check:{...sample.check,answerIndex:5}},'Original'),false);
});
test('store=falseとJSON schemaを送信',async()=>{
  const old=globalThis.fetch;
  let sent;
  globalThis.fetch=async(_url,opts)=>{sent=JSON.parse(opts.body);return new Response(JSON.stringify({status:'completed',output:[{type:'message',content:[{type:'output_text',text:JSON.stringify(sample)}]}],usage:{input_tokens:321,output_tokens:42}}),{status:200,headers:{'Content-Type':'application/json'}})};
  try{
    const r=await onRequestPost({request:request(base),env:{OPENAI_API_KEY:'redacted',AI_RATE_LIMITER:allowed}});
    assert.equal(r.status,200);
    assert.equal(sent.store,false);
    assert.equal(sent.model,'gpt-6-luna');
    assert.equal(sent.text.format.type,'json_schema');
    const inp=JSON.parse(sent.input);
    assert.equal(inp.authoritativeAnswer.correctText,'opens');
  }finally{globalThis.fetch=old;}
});
