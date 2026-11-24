/* DCR result()の誤答カード内のみで動く、API非依存のUIアダプター。 */
(() => {
  const endpoint='/api/tutor';
  const labels={explain:'間違えた理由',simplify:'やさしく説明',practice:'類題を解く'};
  function node(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=String(text);if(cls)e.className=cls;return e;}
  function renderAnswer(target,data){
    target.replaceChildren();
    const t=data.tutor;
    target.append(node('h3',t.title),node('p',t.explanation),node('p','ポイント：'+t.keyPoint),node('p','ヒント：'+t.hint,'ai-hint'));
    if(!t.check||!Array.isArray(t.check.choices)||t.check.choices.length!==2||![0,1].includes(t.check.answerIndex))return;
    const quiz=node('div',undefined,'ai-check');
    quiz.append(node('strong','理解確認（学習成績には反映されません）'),node('p',t.check.stem));
    const buttons=t.check.choices.map((label,i)=>{
      const b=node('button',label);b.type='button';
      b.addEventListener('click',()=>{
        buttons.forEach(x=>x.disabled=true);
        b.classList.add(i===t.check.answerIndex?'ai-right':'ai-wrong');
        buttons[t.check.answerIndex].classList.add('ai-right');
        quiz.append(node('p',`${i===t.check.answerIndex?'正解':'不正解'}：${t.check.reasoning}`));
      });
      return b;
    });
    buttons.forEach(b=>quiz.append(b));
    target.append(quiz,node('p','AI生成内容は誤りを含む場合があります。正式な採点には使用しません。','ai-note'));
  }
  async function requestTutor(button){
    const card=button.closest('.ai-tutor');
    const output=card?.querySelector('.ai-tutor-response');
    if(!output)return;
    const actions=Array.from(card.querySelectorAll('[data-ai-action]'));
    actions.forEach(b=>b.disabled=true);
    output.replaceChildren(node('p',`${labels[button.dataset.aiAction]}を生成中…`));
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),15000);
    try{
      const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({questionId:card.dataset.questionId,selectedIndex:Number(card.dataset.selected),action:button.dataset.aiAction})});
      let data;
      try{data=await response.json();}catch{throw new Error('サーバーから有効なJSONを受信できませんでした。');}
      if(!response.ok){
        const status=data?.error||'UNKNOWN';
        if(status==='RATE_LIMITED')throw new Error('利用回数の上限に達しました。しばらくしてから再試行してください。');
        if(status==='API_NOT_CONFIGURED'||status==='RATE_LIMIT_NOT_CONFIGURED')throw new Error('管理者によるAI接続の設定が必要です。');
        throw new Error('AIを一時的に利用できません。既存の解説で学習を続けられます。');
      }
      renderAnswer(output,data);
    }catch(e){output.replaceChildren(node('p',e.name==='AbortError'?'応答が時間切れになりました。再試行してください。':e.message));}
    finally{clearTimeout(timer);actions.forEach(b=>b.disabled=false);}
  }
  document.addEventListener('click',e=>{
    const button=e.target.closest('button[data-ai-action]');
    if(button){e.preventDefault();requestTutor(button);}
  });
})();
