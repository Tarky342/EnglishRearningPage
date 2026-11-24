import { BANK } from '../_lib/bank.js';
import { TUTOR_SYSTEM, ACTION_GUIDES } from '../_lib/prompts.js';
import { TUTOR_SCHEMA, validateTutorOutput } from '../_lib/schema.js';
import { mockTutor } from '../_lib/mock.js';

const ACTIONS=new Set(['explain','simplify','practice']);
const noStore={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
function reply(status,value){return new Response(JSON.stringify(value),{status,headers:noStore});}

export async function onRequestPost({request,env}){
  const origin=request.headers.get('Origin');
  if(origin&&origin!==new URL(request.url).origin)return reply(403,{error:'ORIGIN_DENIED'});
  if((request.headers.get('Sec-Fetch-Site')||'')==='cross-site')return reply(403,{error:'CROSS_SITE_DENIED'});
  if(!(request.headers.get('Content-Type')||'').toLowerCase().startsWith('application/json'))return reply(415,{error:'JSON_REQUIRED'});
  if(Number(request.headers.get('Content-Length')||0)>2048)return reply(413,{error:'TOO_LARGE'});
  let payload;
  try{
    const raw=await request.text();
    if(raw.length>2048)return reply(413,{error:'TOO_LARGE'});
    payload=JSON.parse(raw);
  }catch{return reply(400,{error:'INVALID_JSON'});}
  if(!payload||typeof payload!=='object')return reply(400,{error:'INVALID_BODY'});
  const {questionId,action,selectedIndex}=payload;
  if(typeof questionId!=='string'||!/^q\d{4}$/.test(questionId)||!ACTIONS.has(action)||!Number.isInteger(selectedIndex))return reply(400,{error:'INVALID_INPUT'});
  const q=BANK[questionId];
  if(!q||selectedIndex<-1||selectedIndex>=q.choices.length)return reply(400,{error:'UNKNOWN_QUESTION'});

  const localMock=env.APP_ENV==='local'&&env.AI_MOCK_MODE==='1';
  if(localMock)return reply(200,{tutor:mockTutor(q,action),mode:'mock'});

  if(!env.AI_RATE_LIMITER?.limit)return reply(503,{error:'RATE_LIMIT_NOT_CONFIGURED'});
  const ip=request.headers.get('CF-Connecting-IP')||'unknown';
  let rate;
  try{rate=await env.AI_RATE_LIMITER.limit({key:ip});}catch{return reply(503,{error:'RATE_LIMIT_UNAVAILABLE'});}
  if(!rate.success)return reply(429,{error:'RATE_LIMITED'});
  if(!env.OPENAI_API_KEY)return reply(503,{error:'API_NOT_CONFIGURED'});

  const input=JSON.stringify({
    action,
    actionGuidance:ACTION_GUIDES[action],
    question:{id:q.id,category:q.cat,stem:q.stem,passage:q.passage||null,choices:q.choices},
    learner:{selectedIndex,selectedText:selectedIndex===-1?'未回答':q.choices[selectedIndex]},
    authoritativeAnswer:{correctIndex:q.answer,correctText:q.choices[q.answer],explanation:q.explanation}
  });
  const controller=new AbortController();
  const timeout=setTimeout(()=>controller.abort(),12000);
  try{
    const upstream=await fetch('https://api.openai.com/v1/responses',{
      method:'POST',signal:controller.signal,
      headers:{'Content-Type':'application/json',Authorization:`Bearer ${env.OPENAI_API_KEY}`},
      body:JSON.stringify({
        model:env.OPENAI_MODEL||'gpt-6-luna',
        instructions:TUTOR_SYSTEM,
        input,
        text:{format:{type:'json_schema',name:'dcr_tutor',strict:true,schema:TUTOR_SCHEMA}},
        max_output_tokens:1200,
        store:false
      })
    });
    if(!upstream.ok){console.error('OPENAI_HTTP',upstream.status);return reply(502,{error:'AI_UNAVAILABLE'});}
    const result=await upstream.json();
    if(result.status&&result.status!=='completed')return reply(502,{error:'AI_INCOMPLETE'});
    const pieces=(result.output||[]).flatMap(item=>item.type==='message'?(item.content||[]):[]);
    if(pieces.some(part=>part.type==='refusal'))return reply(502,{error:'AI_REFUSED'});
    const outputText=pieces.filter(part=>part.type==='output_text').map(part=>part.text).join('');
    let tutor;
    try{tutor=JSON.parse(outputText);}catch{return reply(502,{error:'AI_INVALID_JSON'});}
    if(!validateTutorOutput(tutor,q.stem))return reply(502,{error:'AI_INVALID_OUTPUT'});
    if(result.usage)console.info('AI_USAGE',JSON.stringify({model:env.OPENAI_MODEL||'gpt-6-luna',in:result.usage.input_tokens,out:result.usage.output_tokens}));
    return reply(200,{tutor,mode:'live'});
  }catch(e){
    console.error('AI_REQUEST_FAILED',e?.name==='AbortError'?'timeout':'network');
    return reply(502,{error:'AI_UNAVAILABLE'});
  }finally{clearTimeout(timeout);}
}
